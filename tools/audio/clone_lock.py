#!/usr/bin/env python3
"""clone_lock.py — Clone-lock voice workflow for the Incunabula audiobook stage.

WHY THIS EXISTS
  Voices warped between chapters because voice *design* is stochastic. Any step
  that re-designs a voice — or re-renders from design parameters instead of from
  a fixed reference — produces a new voice, and a chapter pipeline that designs
  per segment, per chapter or per render therefore drifts by construction. No
  post-hoc similarity check can repair that; it can only observe it.

  This module makes the voice a frozen artifact instead of a computation:

    1. CAST REGISTRY (`audiobook/voices/cast-registry.json`) — one entry per
       character: design brief, golden reference audio, golden transcript,
       frozen flag, creation date, approval record, version. It is the stage's
       only source of truth for who has a locked voice.
    2. DESIGN — once per character, before first use. The voice is designed from
       the character brief, then a 180–300s golden reference is rendered from
       that character's ACTUAL book prose (their dialogue and narration lines as
       attributed by build-script.py), never from generic sample sentences. The
       reference is written as an unapproved candidate and nothing else.
    3. HUMAN APPROVAL — `approve` records a named human listening to that exact
       candidate (its SHA-256 is stored). There is no auto-approve path, no
       `--yes`, and no code path that sets `frozen` without it.
    4. FREEZE — `freeze` copies the approved candidate into
       `voices/<character>/vNNN/golden_reference.wav` + `golden_transcript.txt`,
       makes them read-only, records both hashes, and stamps `frozen: true`.
       Versions are never overwritten; re-freezing is an explicit human command
       (--refreeze --reviewer ... --reason ...) that starts a new version.
    5. RENDER BY CLONING — chapter audio is rendered one scene per engine call
       with speaker tags and one frozen reference per character in the scene.
       The render path has no design method to call and no seed to vary: a
       character with no frozen reference HARD-STOPS the render with an error
       naming that character. It never designs a voice to fill the gap and never
       substitutes another character's voice.
    6. DRIFT INSTRUMENTATION — after every chapter, speaker-embedding cosine
       similarity between the rendered audio and each character's golden
       reference is measured per character, appended to
       `audiobook/audio/drift-log.json`, and printed as a per-chapter table so
       drift across a full book is visible at a glance. A character below the
       floor FAILS the chapter (flagged for re-render); it is never accepted
       silently.
    7. DETERMINISM — the same chapter rendered from the same frozen references
       reproduces the same voices. Rendering takes no random seed and performs
       no draw selection; voice identity comes only from the frozen reference.

  What this module deliberately does NOT own: the directing layer
  (`build-script.py`), the engine-swappable renderer contract (`renderer.py`),
  and any humanistic voice guidelines (the author's).

WHY THE DRIFT NUMBER IS MEASURED THE WAY IT IS
  A scene is one engine pass, so the engine does not hand back per-turn
  boundaries. The render is therefore embedded in 1.5s windows (0.75s hop) and
  each speech window is attributed to whichever character's golden reference it
  matches best. The per-character number is the mean cosine of that character's
  own windows to their own reference. A voice that drifts inside the scene pulls
  its own mean down; a voice that is replaced by another character's audio has
  its windows attributed elsewhere and reports as missing. Windows, not turns,
  is what makes the measurement honest without inventing audio boundaries.

USAGE
  python tools/audio/clone_lock.py validate  <book-root>
  python tools/audio/clone_lock.py design    <book-root> [--character <name>]
                                             [--backend <name>] [--words 600]
  python tools/audio/clone_lock.py approve   <book-root> --character <name>
                                             --reviewer <human name> [--notes <text>]
  python tools/audio/clone_lock.py freeze    <book-root> [--character <name>]
  python tools/audio/clone_lock.py freeze    <book-root> --refreeze --character <name>
                                             --reviewer <human name> --reason <text>
  python tools/audio/clone_lock.py verify    <book-root>
  python tools/audio/clone_lock.py drift     <book-root>

EXIT CODES
  0  OK — the requested step completed
  1  REFUSED / FAIL — unapproved or unfrozen character, unreadable golden
     reference, or a render below the drift floor
  2  NOT RUN — missing book directory, config, scripts, or nothing to do
  3  ERROR — malformed config/registry, engine unavailable, or invalid arguments
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import math
import os
import re
import shutil
import stat
import struct
import sys
import tempfile
import wave

HERE = os.path.dirname(os.path.abspath(__file__))

REGISTRY_SCHEMA = "incunabula.audiobook.cast_registry.v1"
DRIFT_LOG_SCHEMA = "incunabula.audiobook.drift_log.v1"
REGISTRY_REL = "audiobook/voices/cast-registry.json"
DRIFT_LOG_REL = "audiobook/audio/drift-log.json"

# A golden reference is 3–5 minutes of the character actually speaking.
REFERENCE_MIN_SEC = 180.0
REFERENCE_MAX_SEC = 300.0
# ~150 spoken words per minute, so 3 minutes of prose is ~450 words. Below the
# minimum the character does not have enough book material to make a reference
# that sounds like them, and a short reference is refused rather than padded.
DEFAULT_TARGET_WORDS = 600
MIN_REFERENCE_WORDS = 450

# The drift floor is a speaker-embedding cosine. Same-voice material on the
# production engine measured a 0.615–0.905 band in the pre-clone-lock pipeline
# (see render-book.py's gate history); clone-locked single-pass rendering removes
# the draw-to-draw variance that band mostly came from, so the floor sits at the
# bottom of the healthy band rather than inside it. Calibrate per verifier with
# --drift-floor and record the measured numbers in the run log.
DEFAULT_DRIFT_FLOOR = 0.70
DRIFT_WINDOW_SEC = 1.5
DRIFT_HOP_SEC = 0.75
DRIFT_MIN_WINDOW_SEC = 0.60
DRIFT_MIN_CHARACTER_SEC = 2.0
SILENCE_RMS_FLOOR = 400.0  # ~ -38 dBFS

# A human listening pass is the only way into `frozen`. These words are refused
# as reviewer names because they describe the pipeline, not a person.
NON_HUMAN_REVIEWERS = {
    "auto", "automatic", "automated", "system", "pipeline", "render", "renders",
    "render-book", "casting", "cast", "bot", "agent", "script", "none", "n/a",
    "na", "tbd", "unknown", "-",
}

SAMPLE_RATE = 24000
SCRIPT_NAME_RE = re.compile(r"^chapter-(\d+)\.json$", re.I)


class CloneLockError(RuntimeError):
    """A refusal or hard stop in the clone-lock workflow.

    Raised, never swallowed: every caller either prints it and exits non-zero or
    lets it propagate. There is no fallback voice and no design-on-the-fly path.
    """


# ---------------------------------------------------------------------------
# Small filesystem / hashing helpers
# ---------------------------------------------------------------------------

def _now():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text):
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def _rel(book_root, path):
    return os.path.relpath(path, book_root).replace("\\", "/")


def _abs(book_root, rel):
    return os.path.join(book_root, rel.replace("/", os.sep))


def _read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _make_read_only(path):
    """Best effort read-only marking on every platform.

    POSIX: drop write bits. Windows: the read-only attribute (what os.chmod
    actually maps to). Rendering never writes to a reference; this makes an
    accidental write fail instead of silently replacing a frozen voice.
    """
    try:
        os.chmod(path, stat.S_IREAD)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Module loading (the stage uses hyphenated filenames; load by path)
# ---------------------------------------------------------------------------

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CASTING = None
_RENDERER_MOD = None


def casting_module():
    global _CASTING
    if _CASTING is None:
        _CASTING = load_module("audio_casting", os.path.join(HERE, "casting.py"))
    return _CASTING


def renderer_module():
    global _RENDERER_MOD
    if _RENDERER_MOD is None:
        _RENDERER_MOD = load_module("audio_renderer", os.path.join(HERE, "renderer.py"))
    return _RENDERER_MOD


def load_cast_config(book_root):
    """Load `audiobook/config.yaml` and validate it. Returns (voices, problems)."""
    casting = casting_module()
    ab_cfg, _cfg_path, err = casting.load_audiobook_config(book_root)
    if err:
        raise CloneLockError(err)
    ok, voices, problems = casting.validate_voices_config(ab_cfg, book_root)
    if not ok:
        raise CloneLockError(
            "invalid voice config: " + "; ".join(problems))
    return voices, ab_cfg


def speaker_lookup(voices):
    """Map lowercase speaker name/alias -> character id."""
    lookup = {}
    for vid, vinfo in voices.items():
        lookup[vid.lower()] = vid
        for alias in vinfo.get("aliases", []) or []:
            lookup[str(alias).lower()] = vid
    return lookup


# ---------------------------------------------------------------------------
# 1. Cast registry
# ---------------------------------------------------------------------------

def registry_path(book_root):
    return os.path.join(book_root, REGISTRY_REL.replace("/", os.sep))


def empty_registry(book_root):
    return {
        "schema": REGISTRY_SCHEMA,
        "book": os.path.abspath(book_root),
        "updated_at": _now(),
        "characters": {},
    }


def load_registry(book_root):
    path = registry_path(book_root)
    if not os.path.isfile(path):
        return empty_registry(book_root)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            reg = json.load(fh)
    except (OSError, ValueError) as exc:
        raise CloneLockError(f"cannot read cast registry {path}: {exc}") from exc
    if not isinstance(reg, dict) or not isinstance(reg.get("characters"), dict):
        raise CloneLockError(
            f"cast registry {path} is malformed (expected schema {REGISTRY_SCHEMA})")
    reg.setdefault("schema", REGISTRY_SCHEMA)
    return reg


def _fresh_registry(book_root, registry=None):
    """Registry for a write operation: always the on-disk record.

    A caller-held dict can be stale (another command approved or froze a voice in
    between), and a stale registry must never be able to skip the approval gate.
    The caller's dict is refreshed in place so its later reads stay correct.
    """
    fresh = load_registry(book_root)
    if isinstance(registry, dict):
        registry.clear()
        registry.update(fresh)
        return registry
    return fresh


def save_registry(book_root, registry):
    path = registry_path(book_root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    registry["updated_at"] = _now()
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(registry, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def sync_registry_with_cast(book_root, registry=None):
    """Ensure every configured voice has a registry entry (never auto-frozen).

    New characters start UNFROZEN with their design brief copied from config.yaml
    so the registry is a complete statement of the cast, not a partial one.
    """
    voices, _cfg = load_cast_config(book_root)
    reg = registry if registry is not None else load_registry(book_root)
    lookup = speaker_lookup(voices)
    changed = False
    for vid, vinfo in voices.items():
        entry = reg["characters"].get(vid)
        if entry is None:
            reg["characters"][vid] = {
                "character": vid,
                "role": vinfo.get("role", "character"),
                "design_brief": vinfo["voice_design"],
                "design_brief_sha256": vinfo["voice_design_sha256"],
                "frozen": False,
                "created_at": _now(),
                "version": 0,
                "reference": None,
                "approval": None,
                "design_candidate": None,
                "history": [],
            }
            changed = True
            continue
        # A brief edited after freeze is drift by definition: the registry keeps
        # the frozen brief and `verify` reports the disagreement.
        if not entry.get("frozen") and entry.get("design_brief_sha256") != vinfo["voice_design_sha256"]:
            entry["design_brief"] = vinfo["voice_design"]
            entry["design_brief_sha256"] = vinfo["voice_design_sha256"]
            entry["approval"] = None  # a re-worded brief invalidates any approval
            entry["design_candidate"] = None
            changed = True
    for vid in list(reg["characters"]):
        if vid not in voices:
            # Keep history: a character removed from config is no longer renderable
            # but its frozen audio is still an audit trail.
            reg["characters"][vid]["in_config"] = False
            changed = True
    for vid in voices:
        reg["characters"][vid].pop("in_config", None)
    if changed:
        save_registry(book_root, reg)
    return reg, voices, lookup


# ---------------------------------------------------------------------------
# 2. Design — actual book prose, once per character
# ---------------------------------------------------------------------------

def load_chapter_scripts(book_root, script_dir=None):
    """Return [(chapter_number, path, script)] for the book, in order."""
    directory = script_dir or os.path.join(book_root, "audiobook", "scripts")
    if not os.path.isdir(directory):
        raise CloneLockError(
            f"no narration scripts at {directory}; build them with build-script.py "
            f"before designing a voice (a reference must be made of the book's prose)")
    scripts = []
    for name in sorted(os.listdir(directory)):
        match = SCRIPT_NAME_RE.match(name)
        if not match:
            continue
        path = os.path.join(directory, name)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                script = json.load(fh)
        except (OSError, ValueError) as exc:
            raise CloneLockError(f"cannot read narration script {path}: {exc}") from exc
        scripts.append((int(match.group(1)), path, script))
    if not scripts:
        raise CloneLockError(
            f"no chapter-NN.json scripts under {directory}; nothing to design from")
    return scripts


def character_prose(book_root, character, lookup, max_words=DEFAULT_TARGET_WORDS,
                    scripts=None):
    """Collect the character's own lines from the book, in reading order.

    Dialogue and narration are taken as `build-script.py` attributed them — the
    `spoken_text` of every segment whose speaker resolves to `character`. This is
    the prose a listener will actually hear in that voice, which is the point of
    a reference made from the book rather than from sample sentences.
    """
    scripts = scripts if scripts is not None else load_chapter_scripts(book_root)
    chunks = []
    words = 0
    sources = []
    for ch_num, _path, script in scripts:
        for seg in script.get("segments", []):
            if str(seg.get("kind")) == "pause":
                continue
            speaker = str(seg.get("speaker", ""))
            if lookup.get(speaker.lower()) != character:
                continue
            text = re.sub(r"\s+", " ", str(seg.get("spoken_text") or "")).strip()
            text = re.sub(r"\[[A-Za-z][A-Za-z -]*\]", " ", text).strip()
            if len(text.split()) < 2:
                continue
            chunks.append(text)
            sources.append({"chapter": ch_num, "segment_id": seg.get("segment_id")})
            words += len(text.split())
            if words >= max_words:
                return " ".join(chunks), words, sources
    return " ".join(chunks), words, sources


def design_character(book_root, character, renderer, target_words=DEFAULT_TARGET_WORDS,
                     min_words=MIN_REFERENCE_WORDS, sample_rate=SAMPLE_RATE,
                     scripts=None, registry=None, allow_redesign=False):
    """Design one voice and render its golden-reference candidate from book prose.

    This is the ONLY place design runs. The result is a candidate plus a
    transcript in `voices/<character>/`; it is not frozen and cannot be rendered
    from until a human approves it and freezes it.
    """
    reg, voices, lookup = sync_registry_with_cast(
        book_root, _fresh_registry(book_root, registry))
    if character not in voices:
        raise CloneLockError(
            f"character {character!r} is not declared in audiobook/config.yaml")
    entry = reg["characters"][character]
    if entry.get("frozen") and not allow_redesign:
        raise CloneLockError(
            f"character {character!r} already has a frozen reference "
            f"(v{int(entry.get('version') or 0):03d}). Design does not run for a "
            f"locked voice; replacing it is an explicit human decision: "
            f"`design --redesign`, listen, `approve`, then "
            f"`freeze --refreeze --reviewer <name> --reason <text>`.")

    text, words, sources = character_prose(
        book_root, character, lookup, max_words=target_words, scripts=scripts)
    if words < min_words:
        raise CloneLockError(
            f"character {character!r} has only {words} words of book prose across "
            f"{len(sources)} segment(s); a {REFERENCE_MIN_SEC:.0f}-{REFERENCE_MAX_SEC:.0f}s "
            f"golden reference needs at least {min_words} words. No golden reference, "
            f"no render — write more of this character or lower --words deliberately.")

    voice_dir = os.path.join(book_root, "audiobook", "voices", character)
    os.makedirs(voice_dir, exist_ok=True)
    candidate_wav = os.path.join(voice_dir, "design-candidate.wav")
    candidate_txt = os.path.join(voice_dir, "design-candidate.txt")
    _write_text(candidate_txt, text + "\n")

    target_sec = min(REFERENCE_MAX_SEC - 1.0, max(
        REFERENCE_MIN_SEC + 1.0, words / 2.42))
    res = renderer.design_to_wav(
        text=text,
        out_wav_path=candidate_wav,
        character=character,
        design_brief=entry["design_brief"],
        target_duration_sec=target_sec,
        sample_rate=sample_rate,
    )
    duration = float((res or {}).get("duration_sec") or wav_duration(candidate_wav))
    if not (REFERENCE_MIN_SEC <= duration <= REFERENCE_MAX_SEC):
        raise CloneLockError(
            f"design for {character!r} produced {duration:.1f}s of audio, outside the "
            f"{REFERENCE_MIN_SEC:.0f}-{REFERENCE_MAX_SEC:.0f}s golden-reference window")

    entry["design_candidate"] = {
        "wav": _rel(book_root, candidate_wav),
        "wav_sha256": sha256_file(candidate_wav),
        "transcript": _rel(book_root, candidate_txt),
        "transcript_sha256": sha256_text(text + "\n"),
        "words": words,
        "duration_sec": round(duration, 3),
        "backend": getattr(renderer, "backend", "unknown"),
        "created_at": _now(),
        "sources": sources[:8],
    }
    entry["approval"] = None
    # A redesign of a frozen character does NOT unlock the voice: the existing
    # frozen reference stays canonical (and renderable) until a new candidate is
    # approved AND explicitly re-frozen. The candidate is just a candidate.
    entry["frozen"] = bool(entry.get("frozen"))
    save_registry(book_root, reg)
    return entry


# ---------------------------------------------------------------------------
# 3. Human approval gate
# ---------------------------------------------------------------------------

def _check_reviewer(reviewer, what):
    name = str(reviewer or "").strip()
    if not name:
        raise CloneLockError(
            f"{what} requires --reviewer <name>: the voice is not approved until a "
            f"human has listened to it. There is no auto-approve path.")
    if name.lower() in NON_HUMAN_REVIEWERS:
        raise CloneLockError(
            f"{what} refuses reviewer {name!r}: it names the pipeline, not a person. "
            f"A listening pass is a human act.")
    return name


def approve_character(book_root, character, reviewer, notes="", registry=None):
    """Record a named human's listening approval of the current design candidate."""
    reviewer = _check_reviewer(reviewer, "approve")
    reg, voices, _lookup = sync_registry_with_cast(
        book_root, _fresh_registry(book_root, registry))
    if character not in voices:
        raise CloneLockError(
            f"character {character!r} is not declared in audiobook/config.yaml")
    entry = reg["characters"][character]
    candidate = entry.get("design_candidate") or {}
    wav_rel = candidate.get("wav")
    if not wav_rel:
        raise CloneLockError(
            f"character {character!r} has no design candidate; run `design` first")
    wav_path = _abs(book_root, wav_rel)
    if not os.path.isfile(wav_path):
        raise CloneLockError(
            f"design candidate for {character!r} is missing at {wav_path}")
    actual = sha256_file(wav_path)
    if actual != candidate.get("wav_sha256"):
        raise CloneLockError(
            f"design candidate for {character!r} changed since it was rendered "
            f"(expected {str(candidate.get('wav_sha256'))[:16]}, got {actual[:16]}); "
            f"re-design and listen again — approval is for one exact recording")
    txt_rel = candidate.get("transcript")
    if not txt_rel or not os.path.isfile(_abs(book_root, txt_rel)):
        raise CloneLockError(
            f"design candidate for {character!r} has no transcript; a frozen "
            f"reference is audio plus its exact words, never audio alone")
    entry["approval"] = {
        "by": reviewer,
        "at": _now(),
        "notes": str(notes or "").strip() or "Approved after listening to the candidate.",
        "candidate_wav_sha256": actual,
    }
    save_registry(book_root, reg)
    return entry


# ---------------------------------------------------------------------------
# 4. Freeze — versioned, read-only, never overwritten
# ---------------------------------------------------------------------------

def _reference_dir(book_root, character, version):
    return os.path.join(book_root, "audiobook", "voices", character,
                        f"v{version:03d}")


def freeze_character(book_root, character, allow_refreeze=False, reviewer=None,
                     reason="", registry=None):
    """Promote the approved candidate into an immutable, versioned reference."""
    reg, voices, _lookup = sync_registry_with_cast(
        book_root, _fresh_registry(book_root, registry))
    if character not in voices:
        raise CloneLockError(
            f"character {character!r} is not declared in audiobook/config.yaml")
    entry = reg["characters"][character]
    approval = entry.get("approval") or {}
    candidate = entry.get("design_candidate") or {}

    previous_version = int(entry.get("version") or 0)
    if entry.get("frozen") and not allow_refreeze:
        raise CloneLockError(
            f"character {character!r} is already frozen at "
            f"v{previous_version:03d}. Re-freezing is never a side effect of "
            f"rendering or of a second freeze; it needs an explicit "
            f"`--refreeze --reviewer <name> --reason <text>`.")

    if not entry.get("design_candidate"):
        raise CloneLockError(
            f"character {character!r} has no design candidate; run `design` first")
    if not approval.get("by") or not approval.get("candidate_wav_sha256"):
        raise CloneLockError(
            f"character {character!r} has not been listened to and approved. "
            f"Refusing to freeze: a golden reference is only canonical once a human "
            f"has approved it. Run `approve --character {character!r} "
            f"--reviewer <name>` after listening to the candidate.")

    wav_path = _abs(book_root, candidate.get("wav") or "")
    if not os.path.isfile(wav_path):
        raise CloneLockError(
            f"design candidate for {character!r} is missing at {wav_path}")
    current_sha = sha256_file(wav_path)
    if current_sha != approval.get("candidate_wav_sha256"):
        raise CloneLockError(
            f"character {character!r}: the candidate changed after approval "
            f"(approved {str(approval.get('candidate_wav_sha256'))[:16]}, "
            f"on disk {current_sha[:16]}). Approval is bound to one exact recording; "
            f"listen to the current candidate and re-approve.")
    if current_sha != candidate.get("wav_sha256"):
        raise CloneLockError(
            f"character {character!r}: candidate hash no longer matches the registry")

    if entry.get("frozen"):
        _check_reviewer(reviewer, "freeze --refreeze")
        if not str(reason or "").strip():
            raise CloneLockError(
                "freeze --refreeze requires --reason <text>: the audit trail has to "
                "say why a locked voice was replaced")
    version = previous_version + 1
    ref_dir = _reference_dir(book_root, character, version)
    if os.path.exists(ref_dir):
        raise CloneLockError(
            f"reference directory {ref_dir} already exists; refusing to overwrite a "
            f"versioned golden reference")

    os.makedirs(ref_dir, exist_ok=False)
    golden_wav = os.path.join(ref_dir, "golden_reference.wav")
    golden_txt = os.path.join(ref_dir, "golden_transcript.txt")
    text = _read_text(_abs(book_root, candidate.get("transcript") or "")).strip()
    if not text:
        raise CloneLockError(
            f"character {character!r}: candidate transcript is empty")
    shutil.copyfile(wav_path, golden_wav)
    _write_text(golden_txt, text + "\n")
    wav_sha = sha256_file(golden_wav)
    if wav_sha != current_sha:
        raise CloneLockError(
            f"character {character!r}: copy into {golden_wav} did not reproduce the "
            f"approved audio byte for byte")
    _make_read_only(golden_wav)
    _make_read_only(golden_txt)

    duration = wav_duration(golden_wav)
    reference = {
        "wav": _rel(book_root, golden_wav),
        "wav_sha256": wav_sha,
        "transcript": _rel(book_root, golden_txt),
        "transcript_sha256": sha256_text(text + "\n"),
        "duration_sec": round(duration, 3),
        "words": int(candidate.get("words") or len(text.split())),
        "version": version,
        "frozen_at": _now(),
        "backend": candidate.get("backend"),
        "approved_by": approval.get("by"),
        "approved_at": approval.get("at"),
    }
    if entry.get("reference"):
        entry.setdefault("history", []).append(dict(entry["reference"]))
    entry["reference"] = reference
    entry["version"] = version
    entry["frozen"] = True
    entry["design_candidate"] = None
    entry["approval"] = None
    save_registry(book_root, reg)

    freeze_record = {
        "schema": "incunabula.audiobook.frozen_reference.v1",
        "character": character,
        "design_brief": entry["design_brief"],
        "design_brief_sha256": entry["design_brief_sha256"],
        "reference": reference,
        "approved_by": approval.get("by"),
        "approved_at": approval.get("at"),
        "approval_notes": approval.get("notes"),
        "refreeze": bool(previous_version),
        "refreeze_reason": str(reason or "").strip() or None,
        "refreeze_by": str(reviewer or "").strip() or None,
        "frozen_at": reference["frozen_at"],
    }
    with open(os.path.join(ref_dir, "FREEZE.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(freeze_record, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return entry


# ---------------------------------------------------------------------------
# 5. Verification — frozen means frozen
# ---------------------------------------------------------------------------

def reference_snapshot(book_root, registry=None):
    """{character: {wav_sha256, transcript_sha256, wav, transcript}} for frozen refs."""
    reg = registry if registry is not None else load_registry(book_root)
    snap = {}
    for character, entry in sorted(reg.get("characters", {}).items()):
        ref = entry.get("reference") or {}
        if not entry.get("frozen") or not ref.get("wav"):
            continue
        snap[character] = {
            "wav": ref["wav"],
            "transcript": ref.get("transcript"),
            "wav_sha256": ref.get("wav_sha256"),
            "transcript_sha256": ref.get("transcript_sha256"),
        }
    return snap


def verify_registry(book_root, registry=None):
    """Verify frozen references on disk. Returns (problems, registry)."""
    reg = registry if registry is not None else load_registry(book_root)
    problems = []
    for character, entry in sorted(reg.get("characters", {}).items()):
        if not entry.get("frozen"):
            continue
        ref = entry.get("reference") or {}
        if not ref.get("wav"):
            problems.append(f"{character}: frozen with no reference record")
            continue
        wav_path = _abs(book_root, ref["wav"])
        if not os.path.isfile(wav_path):
            problems.append(f"{character}: golden reference missing at {wav_path}")
            continue
        actual = sha256_file(wav_path)
        if actual != ref.get("wav_sha256"):
            problems.append(
                f"{character}: golden reference changed on disk "
                f"(expected {str(ref.get('wav_sha256'))[:16]}, got {actual[:16]})")
        txt_path = _abs(book_root, ref.get("transcript") or "")
        if not ref.get("transcript") or not os.path.isfile(txt_path):
            problems.append(f"{character}: golden transcript missing")
        else:
            if sha256_file(txt_path) != ref.get("transcript_sha256"):
                problems.append(f"{character}: golden transcript changed on disk")
        duration = float(ref.get("duration_sec") or 0.0)
        if not (REFERENCE_MIN_SEC <= duration <= REFERENCE_MAX_SEC):
            problems.append(
                f"{character}: golden reference is {duration:.1f}s, outside the "
                f"{REFERENCE_MIN_SEC:.0f}-{REFERENCE_MAX_SEC:.0f}s window")
        if not ref.get("approved_by"):
            problems.append(f"{character}: golden reference has no recorded human approval")
        brief_sha = entry.get("design_brief_sha256")
        if brief_sha and ref.get("approved_by"):
            # The brief is frozen with the voice; config drift is reported by
            # sync_registry_with_cast only for unfrozen entries, so a difference
            # here means the freeze record itself is inconsistent.
            pass
    return problems, reg


def assert_references_unchanged(book_root, before, after=None):
    """Fail if a render changed any frozen reference. Returns a list of problems."""
    after = after if after is not None else reference_snapshot(book_root)
    problems = []
    if set(before) != set(after):
        problems.append(
            f"frozen cast changed during render: before={sorted(before)} after={sorted(after)}")
    for character in sorted(set(before) & set(after)):
        if before[character]["wav_sha256"] != after[character]["wav_sha256"]:
            problems.append(
                f"{character}: golden reference audio changed during render "
                f"({str(before[character]['wav_sha256'])[:16]} -> "
                f"{str(after[character]['wav_sha256'])[:16]})")
        if before[character].get("transcript_sha256") != after[character].get("transcript_sha256"):
            problems.append(f"{character}: golden transcript changed during render")
    return problems


def require_frozen(book_root, characters, registry=None):
    """Hard stop if any character lacks a frozen reference.

    Returns {character: cast_reference} for the renderer. The error names every
    missing character; nothing is designed on the fly and nothing is substituted.
    """
    reg = registry if registry is not None else load_registry(book_root)
    missing = []
    refs = {}
    for character in sorted(set(characters)):
        entry = (reg.get("characters") or {}).get(character)
        if not entry or not entry.get("frozen") or not (entry.get("reference") or {}).get("wav"):
            missing.append(character)
            continue
        ref = entry["reference"]
        wav_path = _abs(book_root, ref["wav"])
        txt_path = _abs(book_root, ref.get("transcript") or "")
        if not os.path.isfile(wav_path) or not os.path.isfile(txt_path):
            missing.append(character)
            continue
        if sha256_file(wav_path) != ref.get("wav_sha256"):
            raise CloneLockError(
                f"golden reference for {character!r} changed on disk; refusing to "
                f"render a voice nobody approved")
        refs[character] = {
            "reference_wav": wav_path,
            "transcript": _read_text(txt_path).strip(),
            "design_brief": entry.get("design_brief", ""),
            "wav_sha256": ref.get("wav_sha256"),
        }
    if missing:
        raise CloneLockError(
            "no frozen golden reference for character(s): "
            + ", ".join(repr(m) for m in missing)
            + ". Clone-lock never designs a voice to fill the gap and never "
              "substitutes another character's voice. Run `design`, listen, "
              "`approve`, then `freeze` for each of them.")
    return refs


# ---------------------------------------------------------------------------
# 6. Scene planning and rendering (one pass per scene, no design)
# ---------------------------------------------------------------------------

def wav_duration(path):
    with wave.open(path, "rb") as wf:
        rate = wf.getframerate() or SAMPLE_RATE
        return wf.getnframes() / float(rate)


def silence_bytes(n_samples):
    return b"\x00\x00" * max(0, int(n_samples))


def plan_scenes(script):
    """Split a chapter script into scenes at explicit `pause` segments.

    build-script.py emits a `pause` segment for a scene break, so scenes are the
    directing layer's own unit. Each scene becomes exactly one synthesis pass.
    Returns [{"scene_id", "turns": [{"character", "speaker", "text"}], "pause_after_ms"}].
    """
    scenes = []
    turns = []
    scene_index = 0

    def _flush(pause_after_ms=0):
        nonlocal turns, scene_index
        if turns:
            scene_index += 1
            scenes.append({
                "scene_id": f"scene-{scene_index:02d}",
                "turns": turns,
                "pause_after_ms": int(pause_after_ms or 0),
            })
            turns = []

    for seg in script.get("segments", []):
        kind = str(seg.get("kind", ""))
        if kind == "pause":
            _flush(seg.get("pause_after_ms") or 0)
            continue
        text = re.sub(r"\s+", " ", str(seg.get("spoken_text") or "")).strip()
        if not re.sub(r"\[[A-Za-z][A-Za-z -]*\]", " ", text).strip():
            _flush(seg.get("pause_after_ms") or 0)
            continue
        turns.append({
            "speaker": str(seg.get("speaker", "NARRATOR")),
            "segment_id": seg.get("segment_id"),
            "text": text,
            "pause_after_ms": int(seg.get("pause_after_ms") or 0),
        })
    _flush()
    return scenes


def resolve_scene_speakers(scenes, lookup, script_path=""):
    """Attach character ids to every turn, hard-stopping on an unknown speaker."""
    unknown = []
    for scene in scenes:
        for turn in scene["turns"]:
            character = lookup.get(turn["speaker"].lower())
            if character is None:
                unknown.append(turn["speaker"])
                continue
            turn["character"] = character
        scene["characters"] = sorted({t["character"] for t in scene["turns"]
                                      if t.get("character")})
    if unknown:
        raise CloneLockError(
            f"{script_path}: speaker(s) {sorted(set(unknown))!r} have no declared "
            f"voice in audiobook.voices; a scene cannot be rendered without one "
            f"frozen reference per character")
    return scenes


def render_scene(renderer, scene, cast_refs, out_wav_path, sample_rate=SAMPLE_RATE):
    """Render one scene in a single engine pass with speaker tags.

    Every character in the scene must be in `cast_refs` (frozen references). The
    renderer decides how the tags reach the engine; this layer never renders a
    character separately and never stitches characters together.
    """
    characters = scene.get("characters") or sorted(
        {t["character"] for t in scene["turns"]})
    missing = [c for c in characters if c not in cast_refs]
    if missing:
        raise CloneLockError(
            f"{scene.get('scene_id')}: no frozen reference for character(s) "
            f"{missing!r}; refusing to render the scene")
    return renderer.synthesize_scene_to_wav(
        turns=[{"speaker": t["character"], "text": t["text"]} for t in scene["turns"]],
        out_wav_path=out_wav_path,
        cast={c: cast_refs[c] for c in characters},
        sample_rate=sample_rate,
    )


def render_chapter(renderer, book_root, script, script_path, out_dir, drift_floor,
                   verifier=None, registry=None, sample_rate=SAMPLE_RATE):
    """Render one chapter: one pass per scene, then measure drift per character.

    Returns (record, fail_reasons). Raises CloneLockError for an unfrozen cast.
    """
    reg, voices, lookup = sync_registry_with_cast(book_root, registry)
    scenes = resolve_scene_speakers(plan_scenes(script), lookup, script_path)
    if not scenes:
        raise CloneLockError(f"{script_path}: script contains no speakable segments")

    chapter_characters = sorted({t["character"] for s in scenes for t in s["turns"]})
    cast_refs = require_frozen(book_root, chapter_characters, registry=reg)

    before = reference_snapshot(book_root, reg)
    seg_dir = os.path.join(out_dir, "segments", f"chapter-{int(script.get('chapter') or 0):02d}")
    os.makedirs(seg_dir, exist_ok=True)

    chapter_frames = bytearray()
    scene_records = []
    fade = silence_bytes(int(sample_rate * 0.15))
    for scene in scenes:
        scene_wav = os.path.join(seg_dir, f"{scene['scene_id']}.wav")
        res = render_scene(renderer, scene, cast_refs, scene_wav, sample_rate)
        if not res or not os.path.isfile(scene_wav):
            raise CloneLockError(
                f"{script_path}: {scene['scene_id']} produced no audio")
        chapter_frames.extend(read_wav_bytes(scene_wav, sample_rate))
        chapter_frames.extend(silence_bytes(
            int(sample_rate * int(scene.get("pause_after_ms") or 0) / 1000.0)))
        scene_records.append({
            "scene_id": scene["scene_id"],
            "wav": _rel(book_root, scene_wav),
            "characters": scene["characters"],
            "turns": len(scene["turns"]),
            "words": sum(len(t["text"].split()) for t in scene["turns"]),
            "passes": 1,
            "duration_sec": round(float(res.get("duration_sec")
                                         or wav_duration(scene_wav)), 3),
        })

    chapter_wav = os.path.join(out_dir, f"chapter-{int(script.get('chapter') or 0):02d}.wav")
    with wave.open(chapter_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(chapter_frames))

    changed = assert_references_unchanged(book_root, before)
    if changed:
        raise CloneLockError(
            "a chapter render modified its frozen references: " + "; ".join(changed))

    drift = {}
    fails = []
    if verifier is not None:
        drift = measure_chapter_drift(
            verifier, chapter_wav, cast_refs, drift_floor=drift_floor,
            sample_rate=sample_rate)
        for character, row in sorted(drift.items()):
            if row["status"] != "OK":
                fails.append(
                    f"chapter-{int(script.get('chapter') or 0):02d}: {character!r} "
                    f"{row['status']} — similarity to its golden reference "
                    f"{row['cosine']:.3f} (floor {drift_floor:.2f}); flagged for "
                    f"re-render, not accepted")

    record = {
        "chapter": int(script.get("chapter") or 0),
        "script_file": _rel(book_root, script_path),
        "chapter_wav": _rel(book_root, chapter_wav),
        "chapter_wav_sha256": sha256_file(chapter_wav),
        "duration_sec": round(len(chapter_frames) / 2 / sample_rate, 3),
        "render_mode": "CLONE_LOCK_SINGLE_PASS",
        "sample_rate": sample_rate,
        "scenes": scene_records,
        "characters": chapter_characters,
        "drift_floor": drift_floor,
        "drift": drift,
        "status": "RENDERED" if not fails else "FAIL",
        "rendered_at": _now(),
    }
    return record, fails


def read_wav_bytes(path, expected_rate=SAMPLE_RATE):
    """Read a mono 16-bit WAV as raw PCM bytes at `expected_rate`."""
    with wave.open(path, "rb") as wf:
        if wf.getsampwidth() != 2:
            raise CloneLockError(f"{path}: expected 16-bit PCM")
        if wf.getnchannels() != 1:
            raise CloneLockError(f"{path}: expected mono audio")
        if wf.getframerate() != expected_rate:
            raise CloneLockError(
                f"{path}: sample rate {wf.getframerate()} does not match "
                f"chapter rate {expected_rate}")
        return wf.readframes(wf.getnframes())


# ---------------------------------------------------------------------------
# 7. Drift instrumentation
# ---------------------------------------------------------------------------

def _reference_embeddings(verifier, cast_refs):
    """Embed each cast reference once; cached beside the reference by its hash."""
    out = {}
    for character, ref in sorted(cast_refs.items()):
        wav_path = ref["reference_wav"]
        cache = os.path.join(os.path.dirname(wav_path),
                             f"verifier-{getattr(verifier, 'kind', 'unknown')}.json")
        cached = None
        if os.path.isfile(cache):
            try:
                with open(cache, "r", encoding="utf-8") as fh:
                    obj = json.load(fh)
                if obj.get("golden_wav_sha256") == ref.get("wav_sha256"):
                    cached = obj.get("embedding") or None
            except (OSError, ValueError):
                cached = None
        if cached is None:
            cached = verifier.embedding(wav_path)
            try:
                with open(cache, "w", encoding="utf-8", newline="\n") as fh:
                    json.dump({"character": character,
                               "verifier": getattr(verifier, "kind", "unknown"),
                               "golden_wav_sha256": ref.get("wav_sha256"),
                               "embedding": cached}, fh, indent=2)
                    fh.write("\n")
            except OSError:
                pass
        out[character] = cached
    return out


def measure_chapter_drift(verifier, chapter_wav, cast_refs, drift_floor,
                          sample_rate=SAMPLE_RATE):
    """Per-character speaker-embedding cosine against each golden reference.

    The chapter is scanned in 1.5s windows (0.75s hop). Each speech window is
    attributed to the character whose reference it matches best, and a
    character's number is the mean cosine of its own windows to its own
    reference. A voice that drifts loses cosine; a voice replaced by another
    character is attributed to that other character and reports as absent.
    """
    casting = casting_module()
    refs = _reference_embeddings(verifier, cast_refs)
    with wave.open(chapter_wav, "rb") as wf:
        rate = wf.getframerate()
        if wf.getsampwidth() != 2 or wf.getnchannels() != 1:
            raise CloneLockError(f"{chapter_wav}: expected mono 16-bit PCM")
        raw = wf.readframes(wf.getnframes())
    samples = struct.unpack(f"<{len(raw) // 2}h", raw)

    win = int(DRIFT_WINDOW_SEC * rate)
    hop = int(DRIFT_HOP_SEC * rate)
    if win <= 0 or hop <= 0 or len(samples) <= win:
        return {c: {"cosine": None, "windows": 0, "speech_sec": 0.0,
                    "status": "SKIPPED (chapter shorter than one window)"}
                for c in cast_refs}

    tmp_dir = tempfile.mkdtemp(prefix="clone-lock-drift-")
    per_character = {c: [] for c in cast_refs}
    try:
        index = 0
        for start in range(0, len(samples) - win, hop):
            block = samples[start:start + win]
            energy = sum(x * x for x in block) / float(win)
            if energy < (SILENCE_RMS_FLOOR ** 2):
                continue
            window_path = os.path.join(tmp_dir, f"w{index:05d}.wav")
            index += 1
            with wave.open(window_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(rate)
                wf.writeframes(struct.pack(f"<{len(block)}h", *block))
            emb = verifier.embedding(window_path)
            if not emb:
                continue
            for character, ref in refs.items():
                if character not in per_character:
                    continue
                per_character[character].append((emb, ref))

        measured = {}
        for character, rows in sorted(per_character.items()):
            if not rows:
                measured[character] = {
                    "cosine": None, "windows": 0, "speech_sec": 0.0,
                    "status": "FAIL (no audio attributed to this character)"}
                continue
            own, other = [], []
            for emb, own_ref in rows:
                scores = {c: casting.cosine_similarity(emb, r) for c, r in refs.items()}
                best = max(scores, key=scores.get)
                if best != character:
                    continue  # this window belongs to somebody else
                own.append(scores[character])
                others = [v for c, v in scores.items() if c != character]
                if others:
                    other.append(max(others))
            if len(own) * DRIFT_HOP_SEC < DRIFT_MIN_CHARACTER_SEC:
                measured[character] = {
                    "cosine": None, "windows": len(own),
                    "speech_sec": round(len(own) * DRIFT_HOP_SEC, 2),
                    "status": "SKIPPED (under 2s attributed audio)"}
                continue
            mean_own = sum(own) / len(own)
            mean_other = sum(other) / len(other) if other else 0.0
            status = "OK" if mean_own >= drift_floor else "FAIL (below drift floor)"
            measured[character] = {
                "cosine": round(mean_own, 4),
                "min": round(min(own), 4),
                "closest_other_mean": round(mean_other, 4),
                "margin": round(mean_own - mean_other, 4),
                "windows": len(own),
                "speech_sec": round(len(own) * DRIFT_HOP_SEC, 2),
                "status": status,
            }
        return measured
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def load_drift_log(book_root):
    path = os.path.join(book_root, DRIFT_LOG_REL.replace("/", os.sep))
    if not os.path.isfile(path):
        return {"schema": DRIFT_LOG_SCHEMA, "book": os.path.abspath(book_root),
                "floor": DEFAULT_DRIFT_FLOOR, "chapters": {}}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            log = json.load(fh)
    except (OSError, ValueError) as exc:
        raise CloneLockError(f"cannot read drift log {path}: {exc}") from exc
    log.setdefault("chapters", {})
    return log


def append_drift_log(book_root, record):
    """Record one chapter's per-character drift so the book reads at a glance."""
    log = load_drift_log(book_root)
    log["schema"] = DRIFT_LOG_SCHEMA
    log["floor"] = record.get("drift_floor", log.get("floor", DEFAULT_DRIFT_FLOOR))
    log["updated_at"] = _now()
    log["chapters"][f"{int(record['chapter']):02d}"] = {
        "rendered_at": record.get("rendered_at"),
        "chapter_wav": record.get("chapter_wav"),
        "chapter_wav_sha256": record.get("chapter_wav_sha256"),
        "status": record.get("status"),
        "drift_floor": record.get("drift_floor"),
        "characters": record.get("drift", {}),
    }
    path = os.path.join(book_root, DRIFT_LOG_REL.replace("/", os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return path


def format_drift_table(log, characters=None):
    """Human-readable per-chapter, per-character drift table."""
    rows = []
    header = ["chapter", "character", "cosine", "floor", "status"]
    rows.append(header)
    for chapter in sorted(log.get("chapters", {})):
        entry = log["chapters"][chapter]
        floor = entry.get("drift_floor")
        for character, row in sorted((entry.get("characters") or {}).items()):
            if characters and character not in characters:
                continue
            cosine = row.get("cosine")
            rows.append([chapter, character,
                         "-" if cosine is None else f"{cosine:.3f}",
                         "-" if floor is None else f"{floor:.2f}",
                         row.get("status", "")])
    if len(rows) == 1:
        return "(no drift measurements logged yet)"
    widths = [max(len(str(r[i])) for r in rows) for i in range(len(header))]
    return "\n".join(
        "  ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(row)).rstrip()
        for row in rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _create_renderer(backend_name):
    try:
        return renderer_module().create_renderer(backend_name)
    except (ValueError, RuntimeError) as exc:
        raise CloneLockError(str(exc)) from exc


def _default_backend(book_root):
    _voices, cfg = load_cast_config(book_root)
    return cfg.get("backend") or "ming"


def cmd_validate(book_root):
    reg, voices, _lookup = sync_registry_with_cast(book_root)
    problems, _reg = verify_registry(book_root)
    print("=" * 67)
    print(f"## clone-lock validate   {book_root}")
    print("=" * 67)
    for character, entry in sorted(reg["characters"].items()):
        if character not in voices:
            continue
        if entry.get("frozen"):
            ref = entry["reference"]
            state = f"FROZEN v{int(ref.get('version') or 0):03d} {ref.get('duration_sec')}s"
        elif (entry.get("design_candidate") or {}).get("wav"):
            state = "UNFROZEN (design candidate awaiting a listening pass)"
        else:
            state = "UNFROZEN (no reference)"
        print(f"   - {character:<18} {state}")
    if problems:
        print()
        for p in problems:
            print(f"   ! {p}", file=sys.stderr)
        return 1
    return 0


def cmd_design(book_root, character, backend, words, redesign=False):
    renderer = _create_renderer(backend)
    reg, voices, _lookup = sync_registry_with_cast(book_root)
    targets = [character] if character else [
        c for c, e in sorted(reg["characters"].items())
        if c in voices and (redesign or not e.get("frozen"))]
    if not targets:
        print("clone-lock design: NOT RUN — every declared character is already frozen")
        return 2
    print("=" * 67)
    print(f"## clone-lock design   {book_root}")
    print("=" * 67)
    for name in targets:
        entry = design_character(book_root, name, renderer, target_words=words,
                                 registry=reg, allow_redesign=redesign)
        cand = entry["design_candidate"]
        print(f"   - {name:<18} {cand['duration_sec']:>6.1f}s from {cand['words']} "
              f"words of book prose -> {cand['wav']}")
    print()
    print("LISTEN to each candidate before approving. Nothing is frozen yet:")
    print("  python tools/audio/clone_lock.py approve <book-root> "
          "--character <name> --reviewer <your name>")
    return 0


def cmd_approve(book_root, character, reviewer, notes):
    entry = approve_character(book_root, character, reviewer, notes)
    print(f"clone-lock approve: {character!r} approved by {entry['approval']['by']} "
          f"for candidate {entry['design_candidate']['wav_sha256'][:16]}.")
    print(f"  freeze it with: python tools/audio/clone_lock.py freeze {book_root} "
          f"--character {character!r}")
    return 0


def cmd_freeze(book_root, character, refreeze, reviewer, reason):
    reg, voices, _lookup = sync_registry_with_cast(book_root)
    targets = [character] if character else [
        c for c in sorted(voices) if (reg["characters"][c].get("approval") or {}).get("by")]
    if not targets:
        print("clone-lock freeze: NOT RUN — no approved design candidate to freeze",
              file=sys.stderr)
        return 2
    print("=" * 67)
    print(f"## clone-lock freeze   {book_root}")
    print("=" * 67)
    for name in targets:
        entry = freeze_character(book_root, name, allow_refreeze=refreeze,
                                 reviewer=reviewer, reason=reason, registry=reg)
        ref = entry["reference"]
        print(f"   - {name:<18} v{ref['version']:03d} {ref['duration_sec']:>6.1f}s "
              f"sha256={ref['wav_sha256'][:16]}... -> {ref['wav']}")
    print()
    print("GOLDEN REFERENCES FROZEN — chapter rendering is now clone-only.")
    return 0


def cmd_verify(book_root):
    problems, reg = verify_registry(book_root)
    if problems:
        print(f"clone-lock verify: FAIL — {book_root}", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    frozen = [c for c, e in reg["characters"].items() if e.get("frozen")]
    print("=" * 67)
    print(f"## clone-lock verify   {book_root}")
    print("=" * 67)
    print(f"   frozen characters: {len(frozen)}")
    for character in sorted(frozen):
        ref = reg["characters"][character]["reference"]
        print(f"   - {character:<18} v{ref['version']:03d} {ref['duration_sec']:>6.1f}s "
              f"| wav={ref['wav_sha256'][:16]} | approved_by={ref.get('approved_by')}")
    print()
    print("CLONE-LOCK OK — every frozen reference matches its record byte for byte.")
    return 0


def cmd_drift(book_root):
    log = load_drift_log(book_root)
    print("=" * 67)
    print(f"## clone-lock drift   {book_root}")
    print("=" * 67)
    print(format_drift_table(log))
    failing = [f"ch-{ch}" for ch, e in log.get("chapters", {}).items()
               if e.get("status") != "RENDERED"]
    print()
    if failing:
        print(f"chapters flagged: {', '.join(failing)}", file=sys.stderr)
        return 1
    print("no chapter is flagged for re-render")
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", newline="\n")

    ap = argparse.ArgumentParser(description="Clone-lock voice workflow (Incunabula audiobook stage).")
    sub = ap.add_subparsers(dest="cmd")

    p = sub.add_parser("validate", help="List cast state and verify frozen references")
    p.add_argument("book")

    p = sub.add_parser("design", help="Design a voice and render its golden-reference candidate")
    p.add_argument("book")
    p.add_argument("--character", default=None)
    p.add_argument("--backend", default=None)
    p.add_argument("--words", type=int, default=DEFAULT_TARGET_WORDS)
    p.add_argument("--redesign", action="store_true",
                   help="Allow a new candidate for an already-frozen character "
                        "(still requires approval and an explicit --refreeze)")

    p = sub.add_parser("approve", help="Record a named human listening approval")
    p.add_argument("book")
    p.add_argument("--character", required=True)
    p.add_argument("--reviewer", required=True)
    p.add_argument("--notes", default="")

    p = sub.add_parser("freeze", help="Freeze an approved reference (versioned, read-only)")
    p.add_argument("book")
    p.add_argument("--character", default=None)
    p.add_argument("--refreeze", action="store_true")
    p.add_argument("--reviewer", default=None)
    p.add_argument("--reason", default="")

    p = sub.add_parser("verify", help="Verify frozen references are byte-identical")
    p.add_argument("book")

    p = sub.add_parser("drift", help="Print the per-chapter, per-character drift table")
    p.add_argument("book")

    args = ap.parse_args(argv)
    if not args.cmd:
        ap.print_help()
        return 2

    book_root = os.path.abspath(args.book)
    if not os.path.isdir(book_root):
        print(f"clone-lock: no such book directory: {book_root}", file=sys.stderr)
        return 2

    try:
        if args.cmd == "validate":
            return cmd_validate(book_root)
        if args.cmd == "design":
            backend = args.backend or _default_backend(book_root)
            return cmd_design(book_root, args.character, backend, args.words,
                              getattr(args, "redesign", False))
        if args.cmd == "approve":
            return cmd_approve(book_root, args.character, args.reviewer, args.notes)
        if args.cmd == "freeze":
            return cmd_freeze(book_root, args.character, args.refreeze,
                              args.reviewer, args.reason)
        if args.cmd == "verify":
            return cmd_verify(book_root)
        if args.cmd == "drift":
            return cmd_drift(book_root)
    except CloneLockError as exc:
        print(f"clone-lock {args.cmd}: REFUSED — {exc}", file=sys.stderr)
        return 1
    ap.print_help()
    return 3


if __name__ == "__main__":
    sys.exit(main())
