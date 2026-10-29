#!/usr/bin/env python3
"""render-book.py — Chapter audio rendered clone-locked to frozen golden voices.

WHY THIS EXISTS
  A narration script is only text until a voice speaks it, and the voice is where an
  audiobook silently changes book. This renderer exists to make a drifting voice
  impossible by construction rather than visible after the fact:

    1. CLONE, NEVER DESIGN. Every chapter render is one pass per scene, conditioned
       on each character's frozen golden reference (`clone_lock.py`). There is no
       design call on this path and no seed to vary: the renderer's only chapter
       entry point is `synthesize_scene_to_wav`, which requires a frozen reference
       per character in the scene. Per-segment draw selection — the mechanism that
       picked a different acoustic identity per line — is gone.

    2. NO GOLDEN REFERENCE, NO RENDER. A chapter that references a character with
       no frozen reference HARD-STOPS with an error naming that character. It never
       designs a voice on the fly to fill the gap and never substitutes another
       character's voice.

    3. ONE PASS PER SCENE. A scene (the script's own unit, split at explicit `pause`
       segments) is handed to the engine whole, with `speaker_N:` tags and the
       ordered frozen references. Characters are never rendered separately and
       stitched: each separate render can warp independently, which is the same
       drift bug in a different shape.

    4. VOICE CONFIG GATE. `casting.validate_voices_config` must hold — every voice
       is a natural-language VOICE_DESIGN with no real-person reference audio, and
       every speaker in every script maps to a declared voice or alias.

    5. FROZEN REFERENCES ARE IMMUTABLE. Before rendering, the reference checksums
       are snapshotted; after each chapter they are re-checked. A render that
       modified a frozen reference raises instead of shipping.

    6. DRIFT INSTRUMENTATION. After each chapter, speaker-embedding cosine between
       the rendered audio and each character's golden reference is measured per
       character and appended to `audiobook/audio/drift-log.json` (and printed as
       a table). A character below the floor FAILS the chapter and is flagged for
       re-render — never silently accepted. The floor is a parameter
       (`--drift-floor`) so it can be calibrated per verifier; the measured values
       are what the log records.

  Audio layout (under <book>/audiobook/audio/):
    chapter-NN.wav                              assembled chapter (16-bit mono)
    segments/chapter-NN/scene-NN.wav            one file per single engine pass
    segments/chapter-NN/scene-NN.wav.meta.json  who spoke, under which reference
    drift-log.json                              per-chapter, per-character similarity
    render-manifest.json                        render ledger with hashes and records

  What this file does not own: the directing layer (`build-script.py`), the engine
  contract (`renderer.py`), and any humanistic voice guidelines.

USAGE
  python tools/audio/render-book.py <book-root> [--chapter <num-or-file>]
      [--backend <name>] [--out-dir <dir>] [--script-dir <dir>]
      [--drift-floor <float>] [--verifier auto|ecapa|campplus]

EXIT CODES
  0  RENDERED — all requested chapters rendered, drift-checked, and logged
  1  REFUSED / FAIL — voice config refused, unfrozen/drifted character, stale
     script, or a character below the drift floor
  2  NOT RUN — missing book directory, missing config, or no scripts
  3  ERROR — malformed config/registry, or a synthesis engine that is unavailable
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
ROOT_DIR = os.path.dirname(TOOLS_DIR)

SCRIPT_NAME_RE = re.compile(r"^chapter-(\d+)\.json$", re.I)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sanitize_filename(name):
    return re.sub(r"[^A-Za-z0-9_-]+", "-", str(name)).strip("-") or "speaker"


def read_wav_frames(wav_path):
    """Read a 16-bit mono WAV. Returns (frames_bytes, sample_rate)."""
    import wave

    with wave.open(wav_path, "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            raise ValueError(
                f"{wav_path}: expected 16-bit mono WAV, got "
                f"{wf.getsampwidth() * 8}-bit {wf.getnchannels()}ch")
        return wf.readframes(wf.getnframes()), wf.getframerate()


# ---------------------------------------------------------------------------
# Script loading & gates
# ---------------------------------------------------------------------------

def load_scripts(script_dir, chapter_filter):
    """Load narration scripts. Returns (scripts_list, error_or_None) where each
    entry is (ch_num, script_path, script_dict)."""
    if not os.path.isdir(script_dir):
        return [], f"no narration script directory at {script_dir} — run build-script.py first"
    out = []
    for name in sorted(os.listdir(script_dir)):
        m = SCRIPT_NAME_RE.match(name)
        if not m:
            continue
        ch_num = int(m.group(1))
        if chapter_filter is not None:
            if str(chapter_filter).isdigit():
                if ch_num != int(chapter_filter):
                    continue
            elif os.path.basename(str(chapter_filter)) != name:
                continue
        path = os.path.join(script_dir, name)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError) as exc:
            return [], f"cannot parse script {path}: {exc}"
        out.append((ch_num, path, data))
    return out, None


def check_script_freshness(book_root, ch_num, script_path, script):
    """Stale-script refusal: the script's recorded source_sha256 must match the
    manuscript file it was built from. Returns (ok, reason)."""
    source_rel = script.get("source_file", "")
    want_sha = script.get("source_sha256", "")
    if not source_rel or not want_sha:
        return False, (
            f"{script_path}: no source_file/source_sha256 recorded — script predates the "
            f"stale-script contract; rebuild with build-script.py"
        )
    source_path = os.path.join(book_root, source_rel)
    if not os.path.isfile(source_path):
        return False, f"{script_path}: source manuscript file missing at {source_path}"
    with open(source_path, "r", encoding="utf-8", errors="ignore") as fh:
        got_sha = hashlib.sha256(fh.read().encode("utf-8")).hexdigest()
    if got_sha != want_sha:
        return False, (
            f"{script_path}: STALE — {source_rel} changed since the script was built "
            f"(script {want_sha[:16]}, manuscript {got_sha[:16]}); rebuild with build-script.py"
        )
    return True, ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", newline="\n")

    ap = argparse.ArgumentParser(
        description="Render narration scripts clone-locked to frozen golden voices.")
    ap.add_argument("book", help="Path to the book root directory")
    ap.add_argument("--chapter", default=None,
                    help="Optional single chapter number or script filename")
    ap.add_argument("--backend", default=None,
                    help="Synthesis backend (default: audiobook config 'backend', else ming)")
    ap.add_argument("--out-dir", default=None,
                    help="Audio output directory (default: <book>/audiobook/audio)")
    ap.add_argument("--script-dir", default=None,
                    help="Narration script directory (default: <book>/audiobook/scripts)")
    ap.add_argument("--drift-floor", type=float, default=None,
                    help="Speaker-similarity floor per character (default: clone_lock's "
                         "calibrated default, 0.70)")
    ap.add_argument("--verifier", default="auto", choices=("auto", "ecapa", "campplus"),
                    help="Speaker-verification instrument for the drift log: ecapa "
                         "(speechbrain, CPU), campplus (the engine's own encoder), or auto")
    args = ap.parse_args(argv)

    book_root = os.path.abspath(args.book)
    if not os.path.isdir(book_root):
        print(f"render-book: no such book directory: {book_root}", file=sys.stderr)
        return 2

    casting = load_module("audio_casting", os.path.join(HERE, "casting.py"))
    clone_lock = load_module("audio_clone_lock", os.path.join(HERE, "clone_lock.py"))
    renderer_mod = load_module("audio_renderer", os.path.join(HERE, "renderer.py"))
    verifier_mod = load_module("audio_verifier", os.path.join(HERE, "verifier.py"))

    script_dir = os.path.abspath(args.script_dir) if args.script_dir else \
        os.path.join(book_root, "audiobook", "scripts")
    scripts, err = load_scripts(script_dir, args.chapter)
    if err:
        print(f"render-book: NOT RUN — {err}", file=sys.stderr)
        return 2
    if not scripts:
        print(f"render-book: NOT RUN — no chapter scripts under {script_dir} "
              f"(nothing to render, never a pass)", file=sys.stderr)
        return 2

    # GATE 4 — voice config (VOICE_DESIGN only, no real-person clones)
    ab_cfg, cfg_path, cfg_err = casting.load_audiobook_config(book_root)
    if cfg_err:
        print(f"render-book: NOT RUN — {cfg_err}", file=sys.stderr)
        return 2
    ok, voices, problems = casting.validate_voices_config(ab_cfg, book_root)
    if not ok:
        print(f"render-book: REFUSED — voice config gate failed ({cfg_path}):",
              file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    # GATE 5 — frozen references: every declared character has one, and it is
    # byte-identical to its record.
    try:
        registry, _voices, lookup = clone_lock.sync_registry_with_cast(book_root)
    except clone_lock.CloneLockError as exc:
        print(f"render-book: REFUSED — {exc}", file=sys.stderr)
        return 1
    ref_problems, registry = clone_lock.verify_registry(book_root, registry)
    if ref_problems:
        print("render-book: REFUSED — clone-lock reference check failed:",
              file=sys.stderr)
        for p in ref_problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    # Every character the scripts actually use must be frozen. This is the hard
    # stop that names characters — it runs before the engine is even loaded so a
    # refused render costs nothing and cannot half-produce audio.
    needed = set()
    for _ch, _path, script in scripts:
        for seg in script.get("segments", []):
            if str(seg.get("kind")) == "pause":
                continue
            character = lookup.get(str(seg.get("speaker", "")).lower())
            if character:
                needed.add(character)
    unresolved = sorted({
        str(seg.get("speaker"))
        for _ch, _path, script in scripts
        for seg in script.get("segments", [])
        if str(seg.get("kind")) != "pause"
        and lookup.get(str(seg.get("speaker", "")).lower()) is None
    })
    if unresolved:
        print(f"render-book: REFUSED — speaker(s) with no declared voice: "
              f"{unresolved}", file=sys.stderr)
        return 1
    try:
        clone_lock.require_frozen(book_root, needed, registry=registry)
    except clone_lock.CloneLockError as exc:
        print(f"render-book: REFUSED — {exc}", file=sys.stderr)
        return 1

    backend_name = args.backend or ab_cfg.get("backend") or "ming"
    try:
        renderer = renderer_mod.create_renderer(backend_name)
    except (ValueError, RuntimeError) as exc:
        print(f"render-book: ERROR — {exc}", file=sys.stderr)
        return 3

    try:
        verifier, verifier_note = verifier_mod.make_verifier(args.verifier, renderer)
    except (ValueError, RuntimeError) as exc:
        print(f"render-book: ERROR — {exc}", file=sys.stderr)
        return 3

    drift_floor = (float(args.drift_floor) if args.drift_floor is not None
                   else float(clone_lock.DEFAULT_DRIFT_FLOOR))
    if not 0.0 < drift_floor <= 1.0:
        print(f"render-book: ERROR — --drift-floor must be in (0, 1]; got {drift_floor}",
              file=sys.stderr)
        return 3

    stale_reasons = []
    for ch_num, script_path, script in scripts:
        fresh, why = check_script_freshness(book_root, ch_num, script_path, script)
        if not fresh:
            stale_reasons.append(why)
    if stale_reasons:
        print("render-book: REFUSED — stale narration script(s):", file=sys.stderr)
        for r in stale_reasons:
            print(f"  - {r}", file=sys.stderr)
        return 1

    out_dir = os.path.abspath(args.out_dir) if args.out_dir else \
        os.path.join(book_root, "audiobook", "audio")
    os.makedirs(out_dir, exist_ok=True)

    manifest_path = os.path.join(out_dir, "render-manifest.json")
    render_manifest = {
        "schema": "incunabula.audiobook.render.v2",
        "book": book_root,
        "backend": renderer.backend,
        "render_mode": "CLONE_LOCK_SINGLE_PASS",
        "verifier": getattr(verifier, "kind", "unknown"),
        "verifier_note": verifier_note,
        "drift_floor": drift_floor,
        "rendered_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "chapters": {},
    }
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as fh:
                prev = json.load(fh)
            if isinstance(prev.get("chapters"), dict):
                render_manifest["chapters"].update(prev["chapters"])
        except (OSError, ValueError):
            pass

    all_fails = []
    built = []
    for ch_num, script_path, script in scripts:
        try:
            record, fails = clone_lock.render_chapter(
                renderer=renderer,
                book_root=book_root,
                script=script,
                script_path=script_path,
                out_dir=out_dir,
                drift_floor=drift_floor,
                verifier=verifier,
                registry=registry,
            )
        except clone_lock.CloneLockError as exc:
            print(f"render-book: REFUSED — {exc}", file=sys.stderr)
            return 1
        except (ValueError, RuntimeError) as exc:
            print(f"render-book: ERROR — {exc}", file=sys.stderr)
            return 3
        clone_lock.append_drift_log(book_root, record)
        render_manifest["chapters"][f"{ch_num:02d}"] = record
        if fails:
            all_fails.extend(fails)
            continue
        built.append((ch_num, record))

    with open(manifest_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(render_manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    log = clone_lock.load_drift_log(book_root)
    print("=" * 67)
    print(f"## render-book   {book_root}")
    print("=" * 67)
    print(f"   backend:      {renderer.backend} (render_mode={render_manifest['render_mode']})")
    print(f"   verifier:     {verifier_note}")
    print(f"   drift floor:  {drift_floor:.2f}")
    print(f"   chapters:     {len(built)} rendered, {len(all_fails)} failing check(s)")
    for ch_num, rec in built:
        chars = ", ".join(
            f"{c}={d.get('cosine') if d.get('cosine') is not None else 'skip'}"
            for c, d in sorted(rec["drift"].items()))
        print(f"   - ch-{ch_num:02d} -> {rec['chapter_wav']} "
              f"({rec['duration_sec']:.1f}s, {len(rec['scenes'])} scene pass(es), "
              f"characters={rec['characters']})")
        print(f"       similarity: {chars or '(not measured)'}")
    print()
    print("   drift across the book:")
    print(clone_lock.format_drift_table(log))
    print()
    print(f"   drift log: {os.path.relpath(os.path.join(book_root, clone_lock.DRIFT_LOG_REL.replace('/', os.sep)), book_root).replace(chr(92), '/')}")
    print(f"   manifest:  {os.path.relpath(manifest_path, book_root).replace(chr(92), '/')}")
    print()
    if all_fails:
        print("render-book: FAIL — audio refused as a release artifact:", file=sys.stderr)
        for r in all_fails:
            print(f"  - {r}", file=sys.stderr)
        return 1
    print("BOOK RENDERED — every scene a single clone-locked pass, "
          "every character within the drift floor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
