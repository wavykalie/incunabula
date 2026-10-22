#!/usr/bin/env python3
"""render-book.py — Chapter audio rendering locked to frozen golden voices (Cluster C).

WHY THIS EXISTS
  A narration script is only text until a voice speaks it, and the voice is where an
  audiobook silently changes book. Rendering must therefore be impossible with any
  voice other than the one a human approved and `casting.py freeze` froze: an
  unfrozen voice, a voice whose `voice_design` changed after approval, a drifted
  synthesis engine, or a script that no longer matches the frozen manuscript would
  each put a different book in the listener's ears than the one that was reviewed.

  This renderer enforces four boundaries before and after producing audio:
    1. REFUSAL TEST #2 — VOICE CONFIG: `casting.validate_voices_config` must hold.
       Every voice is a natural-language VOICE_DESIGN (zero real-person clone or
       reference-audio inputs), `NARRATOR` is defined, and every speaker appearing
       in the narration scripts maps to a declared voice or alias. Exit 1 on failure.
    2. REFUSAL TEST #4 — FROZEN GOLDEN REFERENCES: `casting.verify_frozen_voices`
       must hold. Every voice has an approved golden reference (180–300s), its
       `voice_design_sha256` and `golden_wav_sha256` match disk, and its speaker
       embedding exists. Exit 1 on failure. Rendering is locked to
       `VOICE_CLONE_FROM_GOLDEN`.
    3. STALE SCRIPT REFUSAL: every `audiobook/scripts/chapter-NN.json` must carry a
       `source_sha256` matching the current `manuscript/chapters/` file it was built
       from. A script built from a different manuscript state is refused, not rendered.
    4. SPEAKER DRIFT GATE: after rendering, each speaker's assembled audio is embedded
       and compared (cosine) against that voice's frozen golden embedding. Below the
       drift floor (default 0.90; same voice measures > 0.96, different voices < 0.75)
       the render FAILS — the audio exists but is refused as a release artifact.

  Audio layout (under <book>/audiobook/audio/, or --out-dir):
    chapter-NN.wav                          assembled chapter (16-bit mono)
    segments/chapter-NN/<segment_id>.wav    per-segment audio for ASR/QC alignment
    render-manifest.json                    render ledger: hashes, durations, drift
  Paralinguistic tags in spoken_text (`[sigh]`, `[breath]`, `[laughter]`) are
  performance cues, not words: they are stripped before synthesis and preserved in
  the manifest. `pause_after_ms` silences (including explicit `pause` segments for
  scene breaks) are honored exactly.

USAGE
  python tools/audio/render-book.py <book-root> [--chapter <num-or-file>]
      [--backend <name>] [--out-dir <dir>] [--script-dir <dir>]
      [--drift-min-cosine <float>]

EXIT CODES
  0  RENDERED — all requested chapters rendered, drift-checked, and assembled
  1  REFUSED / FAIL — voice config refused, unfrozen/drifted voice, stale script,
     speaker below the drift floor, or unknown speaker in a script
  2  NOT RUN — missing book directory, missing audiobook/config.yaml, or no scripts
  3  ERROR — malformed config, script JSON, or WAV of unexpected format
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
ROOT_DIR = os.path.dirname(TOOLS_DIR)

SCRIPT_NAME_RE = re.compile(r"^chapter-(\d+)\.json$", re.I)
PARALINGUISTIC_TAG_RE = re.compile(r"\[[a-zA-Z][a-zA-Z ]*\]")
SCRIPT_SCHEMA = "incunabula.audiobook.script.v1"

DEFAULT_SAMPLE_RATE = 24000
DEFAULT_DRIFT_MIN_COSINE = 0.90
MIN_DRIFT_AUDIO_SEC = 3.0


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sanitize_filename(name):
    return re.sub(r"[^A-Za-z0-9_-]+", "-", str(name)).strip("-") or "speaker"


def silence_bytes(n_samples):
    return b"\x00\x00" * max(0, int(n_samples))


def read_wav_frames(wav_path):
    """Read a 16-bit mono WAV. Returns (frames_bytes, sample_rate). Raises ValueError
    on any format this assembler cannot concatenate losslessly."""
    with wave.open(wav_path, "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            raise ValueError(
                f"{wav_path}: expected 16-bit mono WAV, got "
                f"{wf.getsampwidth() * 8}-bit {wf.getnchannels()}ch"
            )
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


def build_speaker_lookup(voices):
    """Map lowercase speaker name/alias -> voice_id from validated voice config."""
    lookup = {}
    for vid, vinfo in voices.items():
        lookup[vid.lower()] = vid
        for alias in vinfo.get("aliases", []):
            lookup[str(alias).lower()] = vid
    return lookup


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_chapter(
    renderer,
    ch_num,
    script_path,
    script,
    voices,
    speaker_lookup,
    out_dir,
    drift_min_cosine,
    frozen_embeddings,
):
    """Render one narration script to per-segment WAVs + an assembled chapter WAV,
    then run the speaker-drift gate. Returns (chapter_record, fail_reasons)."""
    fails = []
    segments = script.get("segments", [])
    if not segments:
        return None, [f"{script_path}: script contains no segments"]

    seg_out_dir = os.path.join(out_dir, "segments", f"chapter-{ch_num:02d}")
    os.makedirs(seg_out_dir, exist_ok=True)

    sample_rate = DEFAULT_SAMPLE_RATE
    chapter_frames = bytearray()
    speaker_frames = {}  # voice_id -> bytearray of that speaker's rendered audio
    seg_records = []
    rendered_count = 0
    paralinguistic_used = {}

    for seg in segments:
        seg_id = str(seg.get("segment_id", f"seg{len(seg_records) + 1:04d}"))
        kind = str(seg.get("kind", "narration"))
        speaker = str(seg.get("speaker", "NARRATOR"))
        pause_ms = int(seg.get("pause_after_ms", 0) or 0)

        tags = [t for t in (seg.get("paralinguistic_tags") or []) if isinstance(t, str)]
        for t in tags:
            paralinguistic_used.setdefault(speaker, []).append(t)

        spoken = str(seg.get("spoken_text", "") or "")
        spoken_clean = PARALINGUISTIC_TAG_RE.sub(" ", spoken)
        spoken_clean = re.sub(r"\s+", " ", spoken_clean).strip()

        if kind == "pause" or not spoken_clean:
            silence = silence_bytes(int(sample_rate * pause_ms / 1000.0))
            chapter_frames.extend(silence)
            seg_records.append({
                "segment_id": seg_id,
                "kind": kind,
                "speaker": speaker,
                "wav": None,
                "duration_sec": round(len(silence) / 2 / sample_rate, 3),
                "pause_after_ms": pause_ms,
                "paralinguistic_tags": tags,
            })
            continue

        voice_id = speaker_lookup.get(speaker.lower())
        if voice_id is None:
            fails.append(
                f"{script_path}: segment {seg_id} speaker {speaker!r} has no matching voice "
                f"in audiobook.voices (Refusal Test #2)"
            )
            continue

        vinfo = voices[voice_id]
        seg_wav = os.path.join(seg_out_dir, f"{seg_id}.wav")
        res = renderer.synthesize_to_wav(
            text=spoken_clean,
            out_wav_path=seg_wav,
            voice_id=voice_id,
            voice_design=vinfo["voice_design"],
            style=seg.get("style") or {},
            sample_rate=sample_rate,
        )
        if not res or not os.path.isfile(seg_wav):
            fails.append(f"{script_path}: segment {seg_id} synthesis produced no WAV")
            continue

        frames, seg_rate = read_wav_frames(seg_wav)
        if seg_rate != sample_rate:
            raise ValueError(
                f"{seg_wav}: sample rate {seg_rate} does not match chapter rate {sample_rate}"
            )
        pause = silence_bytes(int(sample_rate * pause_ms / 1000.0))
        chapter_frames.extend(frames)
        chapter_frames.extend(pause)
        speaker_frames.setdefault(voice_id, bytearray()).extend(frames)

        rendered_count += 1
        seg_records.append({
            "segment_id": seg_id,
            "kind": kind,
            "speaker": speaker,
            "voice_id": voice_id,
            "wav": os.path.relpath(seg_wav, out_dir).replace("\\", "/"),
            "duration_sec": res["duration_sec"],
            "pause_after_ms": pause_ms,
            "paralinguistic_tags": tags,
        })

    if fails:
        return None, fails

    # Assemble the chapter WAV
    chapter_wav = os.path.join(out_dir, f"chapter-{ch_num:02d}.wav")
    with wave.open(chapter_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(chapter_frames))
    with open(chapter_wav, "rb") as fh:
        chapter_sha = hashlib.sha256(fh.read()).hexdigest()

    # Speaker drift gate: each speaker's rendered audio against the frozen golden embedding
    drift = {}
    for voice_id, frames in sorted(speaker_frames.items()):
        audio_sec = len(frames) / 2 / sample_rate
        frozen = frozen_embeddings.get(voice_id)
        if frozen is None:
            drift[voice_id] = {"cosine": None, "audio_sec": round(audio_sec, 2),
                               "status": "SKIPPED (no frozen embedding)"}
            continue
        if audio_sec < MIN_DRIFT_AUDIO_SEC:
            drift[voice_id] = {"cosine": None, "audio_sec": round(audio_sec, 2),
                               "status": f"SKIPPED (under {MIN_DRIFT_AUDIO_SEC:.0f}s)"}
            continue
        tmp_wav = os.path.join(seg_out_dir, f".drift-{sanitize_filename(voice_id)}.wav")
        with wave.open(tmp_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(bytes(frames))
        emb = _CASTING.extract_speaker_embedding_from_wav(tmp_wav)
        try:
            os.remove(tmp_wav)
        except OSError:
            pass
        cos = _CASTING.cosine_similarity(emb, frozen)
        status = "OK" if cos >= drift_min_cosine else "FAIL"
        if status == "FAIL":
            fails.append(
                f"chapter-{ch_num:02d}: speaker drift for {voice_id!r} — rendered audio "
                f"cosine {cos:.4f} vs frozen golden embedding is below the drift floor "
                f"{drift_min_cosine:.2f} (Refusal Test #4 extension)"
            )
        drift[voice_id] = {"cosine": round(cos, 6), "audio_sec": round(audio_sec, 2),
                           "status": status}

    duration_sec = len(chapter_frames) / 2 / sample_rate
    with open(script_path, "rb") as fh:
        script_sha = hashlib.sha256(fh.read()).hexdigest()
    record = {
        "chapter": ch_num,
        "script_file": os.path.relpath(script_path, _BOOK_ROOT).replace("\\", "/"),
        "script_sha256": script_sha,
        "source_file": script.get("source_file", ""),
        "source_sha256": script.get("source_sha256", ""),
        "chapter_wav": os.path.relpath(chapter_wav, _BOOK_ROOT).replace("\\", "/"),
        "chapter_wav_sha256": chapter_sha,
        "total_segments": len(segments),
        "rendered_segments": rendered_count,
        "duration_sec": round(duration_sec, 3),
        "speakers": sorted({s["speaker"] for s in seg_records}),
        "paralinguistic_tags": paralinguistic_used,
        "drift": drift,
        "status": "RENDERED" if not fails else "FAIL",
        "segments": seg_records,
    }
    return record, fails


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

_BOOK_ROOT = None
_CASTING = None


def main(argv=None):
    global _BOOK_ROOT, _CASTING
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", newline="\n")

    ap = argparse.ArgumentParser(
        description="Render narration scripts to chapter audio locked to frozen golden voices."
    )
    ap.add_argument("book", help="Path to the book root directory")
    ap.add_argument("--chapter", default=None,
                    help="Optional single chapter number or script filename")
    ap.add_argument("--backend", default="ming", help="Synthesis backend (default: ming)")
    ap.add_argument("--out-dir", default=None,
                    help="Audio output directory (default: <book>/audiobook/audio)")
    ap.add_argument("--script-dir", default=None,
                    help="Narration script directory (default: <book>/audiobook/scripts)")
    ap.add_argument("--drift-min-cosine", type=float, default=DEFAULT_DRIFT_MIN_COSINE,
                    help=f"Speaker-drift cosine floor (default: {DEFAULT_DRIFT_MIN_COSINE})")
    args = ap.parse_args(argv)

    book_root = os.path.abspath(args.book)
    _BOOK_ROOT = book_root
    if not os.path.isdir(book_root):
        print(f"render-book: no such book directory: {book_root}", file=sys.stderr)
        return 2

    _CASTING = load_module("audio_casting", os.path.join(HERE, "casting.py"))
    renderer_mod = load_module("audio_renderer", os.path.join(HERE, "renderer.py"))

    # Narration scripts must exist before anything else is worth checking
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

    # REFUSAL TEST #2 — voice config (VOICE_DESIGN only, no real-person clones,
    # every script speaker covered by a declared voice or alias)
    ab_cfg, cfg_path, cfg_err = _CASTING.load_audiobook_config(book_root)
    if cfg_err:
        print(f"render-book: NOT RUN — {cfg_err}", file=sys.stderr)
        return 2
    ok, voices, problems = _CASTING.validate_voices_config(ab_cfg, book_root)
    if not ok:
        print(f"render-book: REFUSED — voice config gate failed ({cfg_path}):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    # REFUSAL TEST #4 — every voice frozen to an approved, uncorrupted golden reference
    ok, manifest, reasons = _CASTING.verify_frozen_voices(book_root)
    if not ok:
        print("render-book: REFUSED — voice freeze gate failed (Refusal Test #4):",
              file=sys.stderr)
        for r in reasons:
            print(f"  - {r}", file=sys.stderr)
        return 1

    try:
        renderer = renderer_mod.create_renderer(args.backend)
    except ValueError as exc:
        print(f"render-book: ERROR — {exc}", file=sys.stderr)
        return 3

    speaker_lookup = build_speaker_lookup(voices)

    # Frozen golden embeddings for the drift gate
    frozen_embeddings = {}
    for vid, frec in manifest.get("voices", {}).items():
        emb_rel = frec.get("speaker_embedding_file", "")
        emb_path = os.path.join(book_root, emb_rel)
        if emb_rel and os.path.isfile(emb_path):
            try:
                with open(emb_path, "r", encoding="utf-8") as fh:
                    frozen_embeddings[vid] = json.load(fh).get("embedding") or []
            except (OSError, ValueError):
                pass

    # Stale-script refusal for every script about to be rendered
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
        "schema": "incunabula.audiobook.render.v1",
        "book": book_root,
        "backend": renderer.backend,
        "render_mode": "VOICE_CLONE_FROM_GOLDEN",
        "drift_min_cosine": args.drift_min_cosine,
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
            record, fails = render_chapter(
                renderer=renderer,
                ch_num=ch_num,
                script_path=script_path,
                script=script,
                voices=voices,
                speaker_lookup=speaker_lookup,
                out_dir=out_dir,
                drift_min_cosine=args.drift_min_cosine,
                frozen_embeddings=frozen_embeddings,
            )
        except ValueError as exc:
            print(f"render-book: ERROR — {exc}", file=sys.stderr)
            return 3
        if fails:
            all_fails.extend(fails)
            if record:
                render_manifest["chapters"][f"{ch_num:02d}"] = record
            continue
        render_manifest["chapters"][f"{ch_num:02d}"] = record
        built.append((ch_num, record))

    with open(manifest_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(render_manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print("=" * 67)
    print(f"## render-book   {book_root}")
    print("=" * 67)
    print(f"   backend:      {renderer.backend} (render_mode={render_manifest['render_mode']})")
    print(f"   chapters:     {len(built)} rendered, {len(all_fails)} failing check(s)")
    for ch_num, rec in built:
        rel_wav = rec["chapter_wav"]
        drift_str = ", ".join(
            f"{vid}={d['cosine'] if d['cosine'] is not None else 'skip'}"
            for vid, d in sorted(rec["drift"].items())
        )
        print(f"   - ch-{ch_num:02d} -> {rel_wav} ({rec['duration_sec']:.1f}s, "
              f"{rec['rendered_segments']} segs, speakers={rec['speakers']})")
        print(f"       drift: {drift_str}")
    print(f"   manifest: {os.path.relpath(manifest_path, book_root).replace(chr(92), '/')}")
    print()
    if all_fails:
        print("render-book: FAIL — rendered audio refused as release artifacts:", file=sys.stderr)
        for r in all_fails:
            print(f"  - {r}", file=sys.stderr)
        return 1
    print("BOOK RENDERED — all chapters assembled from frozen golden voices, drift within floor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
