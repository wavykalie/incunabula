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
       and checked against the frozen golden references twice. The instrument is chosen
       with `--verifier` (default `auto` = ECAPA-TDNN when installed, else the engine's
       own CAM++ encoder); see `verifier.py` for why the gate does not simply reuse the
       encoder that conditioned synthesis. Both numbers are measured on Ming-3.0-tts
       output, never assumed:
         a. ABSOLUTE FLOOR (default 0.55 cosine vs own frozen reference): catches
            catastrophic identity failure — collapse, unconditioned synthesis, or
            identity conditioning fed the wrong embedding space (the last of these
            measured 0.04–0.34 and refused a whole render on 2026-10-23). Correctly
            conditioned audio measures 0.615–0.905 on per-voice aggregates across
            sampling draws, so the floor sits under the whole measured same-voice
            band, not inside it.
         b. IDENTITY (own reference must beat every other cast voice by a margin,
            default -0.10): catches gross mix-ups, which land at margins around
            -0.15. Deliberately not 0.05: on this engine's synthetic speech ECAPA's
            margin on CORRECT audio is -0.054..+0.177 — the confusable pair
            (young-tenor Mittens vs alto narrator) sits near 0.0 whether or not the
            voices are swapped, so strict separation is outside the instrument's
            resolution and a strict gate only refuses correct audio. Enforce strict
            separation with `--drift-id-margin 0.05` when the cast is far apart.
       History: on 2026-10-23 a stricter predecessor of this gate refused a chapter
       whose narrator, Mittens and Rocky measured 0.85–0.89 against themselves and
       0.81–0.90 against each other — three designs collapsed into one register. That
       refusal was correct and the cast was redesigned; close-pair identity remains
       a listening question, not one this instrument can certify.
       Either failure FAILS the render — the audio exists but is refused as a
       release artifact.

  Audio layout (under <book>/audiobook/audio/, or --out-dir):
    chapter-NN.wav                          assembled chapter (16-bit mono)
    segments/chapter-NN/<segment_id>.wav    per-segment audio for ASR/QC alignment
    render-manifest.json                    render ledger: hashes, durations, drift
  Paralinguistic tags in spoken_text (`[sigh]`, `[breath]`, `[laughter]`) are
  performance cues, not words: they are passed to the synthesis backend (ming3 folds
  them into its delivery instruction; the deterministic reference engine speaks only
  their words) and preserved in the manifest. `pause_after_ms` silences (including
  explicit `pause` segments for scene breaks) are honored exactly.

USAGE
  python tools/audio/render-book.py <book-root> [--chapter <num-or-file>]
      [--backend <name>] [--out-dir <dir>] [--script-dir <dir>]
      [--drift-min-cosine <float>]

EXIT CODES
  0  RENDERED — all requested chapters rendered, drift-checked, and assembled
  1  REFUSED / FAIL — voice config refused, unfrozen/drifted voice, stale script,
     speaker below the drift floor, or unknown speaker in a script
  2  NOT RUN — missing book directory, missing audiobook/config.yaml, or no scripts
  3  ERROR — malformed config, script JSON, WAV of unexpected format, or a
     synthesis engine that is unavailable or misbehaving
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import math
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
# Calibrated on real Ming-3.0-tts output with the ECAPA verifier across repeated
# full-chapter renders (different sampling draws; see gate 4 in the header):
# correctly conditioned per-voice aggregates measure 0.615–0.905 vs their own
# golden and margins of -0.054..+0.177, so draw variance alone moves a healthy
# voice by ~0.1. Catastrophic identity failure measures 0.04–0.34 own, and a full
# voice mix-up lands at margins around -0.15. The floor and margin sit between
# those bands: this gate certifies "right pipeline, no gross mix-up" — close-pair
# identity (young tenor vs alto narrator sit at ~0.0 margin even when correct) is
# outside ECAPA's resolution on this engine's speech and remains a listening call.
DEFAULT_DRIFT_MIN_COSINE = 0.55
DEFAULT_DRIFT_ID_MARGIN = -0.10
MIN_DRIFT_AUDIO_SEC = 3.0

# Speech-rate plausibility gate + seeded retries. The engine's sampling draw can
# degenerate two ways, and both shipped in v4 until the listener heard them:
#   * rushed: the same 64-word segment rendered 18.0s on one draw and 8.7s
#     (441 wpm) on another; all 46 multi-word segments the listener accepted
#     measure 2.04-4.00 words/sec, the degenerate draw measured 7.34.
#   * looped: the engine stalls into repetition — a one-word "Mm." rendered
#     32.7s and a 6-word line rendered 32.4s (the audible "repeat
#     reverberations"). Caught by a max-plausible-duration bound on EVERY
#     segment, not just long ones.
# Out-of-range draws are re-rendered with a fresh seed up to MAX_SYNTH_ATTEMPTS,
# then refused.
MIN_RATE_WORDS = 8
MIN_WORDS_PER_SEC = 1.5
MAX_WORDS_PER_SEC = 4.8
MAX_SYNTH_ATTEMPTS = 4

# PER-SEGMENT IDENTITY (added 2026-10-24). The gate above embeds each speaker's
# whole chapter, so 70 independently drawn narrator segments averaged to a passing
# 0.86 while the listener heard "a different person" repeatedly. Measured on v6:
# per-narrator-segment cosine to the frozen conditioning embedding ranged 0.137–
# 0.907 (median 0.788); F0 ranged 113–393 Hz; the fraction of energy above 4 kHz
# ranged 0.073–0.684. Those are the muffled/off-voice segments, and the aggregate
# gate cannot see them. Draw-to-draw spread on the SAME text is the cause: one
# 44-word line drew 0.542, 0.892 and 0.896 on three seeds. So every segment is now
# embedded against its own frozen conditioning embedding, a low-identity draw is
# re-drawn, and the best draw is kept. Reliability rises with utterance length
# (14-word line: 0.836–0.882; 2-word line: 0.276–0.726), which is why narration is
# packed into paragraph-length calls below rather than one sentence per call.
IDENTITY_GOOD_COS = 0.80     # a draw at/above this is kept immediately
MAX_IDENTITY_DRAWS = 3       # plausible draws allowed when the first is below it

# CONTINUITY + LIVELINESS (added 2026-10-25). v7 selected each draw against the
# frozen golden only, so two consecutive lines could each score well and still
# sound like different people: measured adjacent-segment cosine ran 0.24–0.87
# ("Rocky agreed." landed at 0.24 against the line before it). Selection now
# also scores the draw against the PREVIOUS accepted segment of the same voice,
# and rejects monotone draws: a 'robotic' take measures f0 movement well under
# the voice's own golden movement (probe: a flat "Mittens the seventh." drew
# 0.352 oct std vs the golden's 0.552, while a lively take drew 0.755).
CONTINUITY_WEIGHT = 0.45     # blend weight of draw-vs-previous-segment cosine
CONTINUITY_GOOD_COS = 0.72   # draw coherent with the previous line at/above this
FLAT_F0MOVE_FLOOR = 0.55     # draw f0 movement / golden below this = monotone
FLAT_F0MOVE_GOOD = 0.70      # at/above this ratio the draw is lively enough
IDENTITY_MAX_OCTAVES = 0.60  # reject a draw this far from the voice's own pitch
PITCH_ALLOWED_OCTAVES = 0.45  # normal intonation range before a draw is penalised
IDENTITY_MEDIAN_FLOOR = 0.70  # chapter-level distribution gate (audible drift)
IDENTITY_P10_FLOOR = 0.50
IDENTITY_MIN_SEGMENTS = 5
# The gate only judges utterances long enough for the instrument: measured on the
# accepted v7 chapter, >=8-word segments sit at 0.705–0.866 while 1–2-word lines
# span 0.31–0.82 whatever the audio sounds like (CAM++ has ~1s to work with).
# Gating short lines would refuse audio the listener accepts — the exact mistake
# this pipeline's history warns about. Short lines are still SELECTED on identity
# and pitch, just not certified by the distribution gate.
IDENTITY_MIN_WORDS = 4

# NARRATION PACKING. build-script.py splits narration one sentence per segment for
# pacing (measured: a whole paragraph in one engine call came back flat), but every
# segment is an independent engine draw, so sentence-sized calls produce ~70 voice
# lotteries per chapter and the shortest ones ("Rocky said.") carry almost no
# identity. Packing consecutive narration sentences of one paragraph into a single
# call up to the engine's reliable input length keeps the sentence beats inside one
# draw while preserving the paragraph pause at the run's end.
MERGE_MAX_WORDS = 45          # = renderer.MING3_MAX_CHUNK_WORDS: one chunk, one draw
MERGE_INTRA_PAUSE_MAX_MS = 500  # pause_after_ms at/below this is a sentence beat

# LEVEL MATCHING. v6 narrator segments ranged -26.4 to -17.1 dBFS RMS (9.3 dB) with
# no relation to the text, because the engine's output level is draw-dependent and
# the only processing was an attenuate-only ceiling. The jumps read as "muffled"
# and as a different recording; every segment is now brought to one speech level.
TARGET_SPEECH_RMS_DBFS = -20.0
PEAK_CEILING = 0.89
SPEECH_GATE_DBFS = -40.0


def max_plausible_sec(words_n):
    """Upper duration bound for a plausible reading of `words_n` words.

    Calibrated against accepted and rejected draws: accepted 1-word lines land
    1.0-1.5s (a reverberant looping "Mm." once slipped through at 4.0s and the
    listener heard it), 2-word lines ~2.0s, a 42-word line 10.6s; loop draws ran
    32s+ on a single word."""
    return 1.2 + 1.3 * words_n


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sanitize_filename(name):
    return re.sub(r"[^A-Za-z0-9_-]+", "-", str(name)).strip("-") or "speaker"


def silence_bytes(n_samples):
    return b"\x00\x00" * max(0, int(n_samples))


def spoken_word_count(text):
    """Words the engine will actually speak (paralinguistic tags excluded)."""
    return len(PARALINGUISTIC_TAG_RE.sub(" ", text or "").split())


def pack_narration_segments(segments):
    """Pack consecutive narration sentences of one paragraph into one engine call.

    A run is merged only while all of these hold: same speaker, kind 'narration',
    identical delivery style, the previous segment's pause is an intra-paragraph
    beat (<= MERGE_INTRA_PAUSE_MAX_MS, so paragraph breaks stay breaks), and the
    combined text stays within MERGE_MAX_WORDS (the engine's reliable call length).
    The merged unit keeps the first segment's id and the last segment's pause, and
    records which segments it absorbed so per-segment QC can still map back.
    """
    def style_key(seg):
        return json.dumps(seg.get("style") or {}, sort_keys=True)

    out = []
    for seg in segments:
        prev = out[-1] if out else None
        mergeable = (
            prev is not None
            and str(seg.get("kind", "")) == "narration"
            and str(prev.get("kind", "")) == "narration"
            and str(seg.get("speaker", "")) == str(prev.get("speaker", ""))
            and style_key(seg) == style_key(prev)
            and int(prev.get("pause_after_ms", 0) or 0) <= MERGE_INTRA_PAUSE_MAX_MS
            and spoken_word_count(prev.get("_packed_text", prev.get("spoken_text", "")))
            + spoken_word_count(seg.get("spoken_text", "")) <= MERGE_MAX_WORDS
        )
        if not mergeable:
            out.append(dict(seg))
            if "_packed_text" not in out[-1]:
                out[-1]["_packed_text"] = str(seg.get("spoken_text", ""))
            continue
        packed = f"{prev['_packed_text']} {seg.get('spoken_text', '')}".strip()
        prev["_packed_text"] = packed
        prev["spoken_text"] = packed
        prev["raw_text"] = f"{prev.get('raw_text', '')} {seg.get('raw_text', '')}".strip()
        prev["pause_after_ms"] = int(seg.get("pause_after_ms", 0) or 0)
        prev["paralinguistic_tags"] = list(prev.get("paralinguistic_tags") or []) + \
            list(seg.get("paralinguistic_tags") or [])
        prev.setdefault("packed_from", [prev.get("segment_id")])
        prev["packed_from"].append(seg.get("segment_id"))
    for seg in out:
        seg.pop("_packed_text", None)
    return out


def f0_voiced_stats(wav_path):
    """(median F0 Hz, F0 movement octaves std, voiced-frame count) over the file's
    voiced frames. (0.0, 0.0, 0) when there is no voiced speech.

    Octave-robust lag choice: among autocorrelation lags within 90% of the peak,
    the LARGEST lag (lowest F0) wins. The naive argmax picks the 2x octave on
    bright excited frames — measured on v7 narrator segments the naive median read
    453 Hz where the robust median reads 293 Hz — and the pitch guard then
    penalised correct draws for a measurement artifact. The movement figure is the
    anti-'robotic' instrument: a monotone draw measures well under its own voice's
    golden movement (probe: flat "Mittens the seventh." drew 0.352 oct std vs the
    golden's 0.552; a lively take drew 0.755).
    """
    try:
        import numpy as np
    except ImportError:
        return 0.0, 0.0, 0
    with wave.open(wav_path, "rb") as wf:
        rate = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    if not raw:
        return 0.0, 0.0, 0
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    win = max(64, int(rate * 0.04))
    hop = win // 2
    if x.size < win * 2:
        return 0.0, 0.0, 0
    frames = np.lib.stride_tricks.sliding_window_view(x, win)[::hop]
    rms = np.sqrt((frames ** 2).mean(axis=1))
    keep = frames[rms >= 0.01]
    if keep.shape[0] == 0:
        return 0.0, 0.0, 0
    keep = keep - keep.mean(axis=1, keepdims=True)
    spec = np.fft.rfft(keep, n=2 * win, axis=1)
    ac = np.fft.irfft(spec * np.conj(spec), n=2 * win, axis=1)[:, :win]
    ac /= (ac[:, :1] + 1e-9)
    lo = max(1, int(rate / 450))
    hi = min(win - 1, int(rate / 60))
    if hi <= lo:
        return 0.0, 0.0, 0
    band = ac[:, lo:hi]
    strength = band.max(axis=1)
    voiced = strength > 0.3
    if not voiced.any():
        return 0.0, 0.0, 0
    thr = 0.9 * strength[voiced][:, None]
    cand = band[voiced] >= thr
    lags = lo + np.array([
        int(np.max(np.atleast_1d(np.nonzero(np.atleast_1d(c))[0])))
        for c in cand
    ])
    f0 = rate / lags
    movement = float(np.std(np.log2(f0))) if f0.size > 1 else 0.0
    return float(np.median(f0)), movement, int(f0.size)


def median_f0_hz(wav_path):
    """Median voiced F0 in Hz, or 0.0 when the file holds no voiced speech.

    Used only to keep a draw in its voice's register. Measured on v6, one narrator
    swung 113–393 Hz across her own segments — a male-register draw on a female
    design is the single most audible "different person", and CAM++ cosine does not
    fully catch it on one-second utterances.
    """
    return f0_voiced_stats(wav_path)[0]


def mean_mfcc_vector(wav_path, n_coeffs=13):
    """Mean MFCC vector of a segment's speech frames, or None when unmeasurable.

    Deliberately simple (13 coefficients, mel-spaced, speech frames only) because
    it only has to answer one question: does this segment have the same timbre
    texture as the same voice's other segments? It is not a classifier, and it is
    not used for identity — the speaker encoder is.
    """
    try:
        import numpy as np
    except ImportError:
        return None
    with wave.open(wav_path, "rb") as wf:
        rate = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    if not raw or rate < 8000:
        return None
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    win = max(64, int(rate * 0.025))
    hop = max(1, int(rate * 0.010))
    if x.size < win * 3:
        return None
    frames = np.lib.stride_tricks.sliding_window_view(x, win)[::hop]
    rms = np.sqrt((frames ** 2).mean(axis=1))
    frames = frames[rms >= 0.01]
    if frames.shape[0] < 5:
        return None
    spec = np.abs(np.fft.rfft(frames * np.hamming(win), axis=1)) ** 2
    bins = np.fft.rfftfreq(win, 1.0 / rate)

    def hz2mel(f):
        return 2595.0 * np.log10(1.0 + f / 700.0)

    def mel2hz(m):
        return 700.0 * (10.0 ** (m / 2595.0) - 1.0)

    lo, hi = hz2mel(80.0), hz2mel(min(7600.0, rate / 2.0 - 100.0))
    points = mel2hz(np.linspace(lo, hi, n_coeffs + 3 + 22))
    n_bands = len(points) - 2
    fb = np.zeros((n_bands, spec.shape[1]))
    for b in range(n_bands):
        a, c, d = points[b], points[b + 1], points[b + 2]
        rising = (bins >= a) & (bins <= c)
        falling = (bins > c) & (bins <= d)
        if c > a:
            fb[b, rising] = (bins[rising] - a) / (c - a)
        if d > c:
            fb[b, falling] = (d - bins[falling]) / (d - c)
    mel = np.log(spec @ fb.T + 1e-10)
    dct = np.cos(np.pi / n_bands * (np.arange(n_bands)[None, :] + 0.5)
                 * np.arange(n_coeffs)[:, None])
    return (mel @ dct.T).mean(axis=0)


def normalize_speech_level(wav_path, target_dbfs=TARGET_SPEECH_RMS_DBFS,
                           peak_ceiling=PEAK_CEILING):
    """Bring a rendered segment to one speech level (RMS over speech frames only).

    Returns the applied gain. The engine's output level varies by draw, not by text,
    so without this the chapter steps 9 dB between neighbouring sentences — heard as
    muffling and as a change of recording. Gains are clamped and a peak ceiling is
    enforced so a loud draw is never pushed into 16-bit clipping.
    """
    with wave.open(wav_path, "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            return 1.0
        rate = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    if not raw:
        return 1.0
    try:
        import numpy as np
    except ImportError:
        return 1.0
    samples = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    if not samples.size:
        return 1.0
    frame = max(1, int(rate * 0.02))
    n = samples.size // frame
    if n == 0:
        return 1.0
    frames = samples[:n * frame].reshape(n, frame)
    rms = np.sqrt((frames ** 2).mean(axis=1))
    gate = 10 ** (SPEECH_GATE_DBFS / 20.0)
    speech = rms[rms >= gate]
    if speech.size == 0:
        return 1.0
    cur = float(np.sqrt((speech ** 2).mean()))
    if cur <= 0:
        return 1.0
    gain = (10 ** (target_dbfs / 20.0)) / cur
    peak = float(np.abs(samples).max())
    if peak * gain > peak_ceiling:
        gain = peak_ceiling / peak if peak > 0 else 1.0
    gain = max(0.2, min(6.0, gain))
    if abs(gain - 1.0) < 0.01:
        return 1.0
    out = np.clip(samples * gain, -1.0, 1.0)
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes((out * 32767.0).astype("<i2").tobytes())
    return gain


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
    drift_id_margin,
    frozen_embeddings,
    conditioning_embeddings,
    verifier,
    golden_pitch=None,
    golden_movement=None,
    acoustic_prompts=None,
    reuse_segments=False,
):
    """Render one narration script to per-segment WAVs + an assembled chapter WAV,
    then run the speaker-drift gate. Returns (chapter_record, fail_reasons).

    `conditioning_embeddings` (CAM++, from `speaker_embedding.json`) pin each
    segment's voice in the engine; `frozen_embeddings` (verifier space) are only
    ever compared by the drift gate — the two must never be swapped.
    `golden_pitch` maps voice_id -> median F0 of its frozen golden reference, used
    to keep each draw in its voice's register; `golden_movement` maps voice_id ->
    its F0 movement (octaves std), the anti-monotone reference."""
    golden_pitch = golden_pitch or {}
    golden_movement = golden_movement or {}
    acoustic_prompts = acoustic_prompts or {}
    prev_accepted = {}  # voice_id -> embedding of the last accepted draw
    fails = []
    script_segments = script.get("segments", [])
    if not script_segments:
        return None, [f"{script_path}: script contains no segments"]
    # One engine call per narration paragraph instead of one per sentence: fewer
    # independent identity draws, and each draw carries a whole paragraph of context.
    segments = pack_narration_segments(script_segments)

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
        spoken_clean = re.sub(r"\s+", " ", PARALINGUISTIC_TAG_RE.sub(" ", spoken)).strip()

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
        cond = conditioning_embeddings.get(voice_id)
        if not cond:
            fails.append(
                f"{script_path}: segment {seg_id} voice {voice_id!r} has no frozen "
                f"CAM++ conditioning embedding (speaker_embedding.json missing from "
                f"the freeze manifest) — unconditioned renders drift apart per call"
            )
            continue
        seg_wav = os.path.join(seg_out_dir, f"{seg_id}.wav")
        words_n = len(spoken_clean.split())
        res, attempts = None, 0
        rate_notes = []
        identity_used = 0
        identity_cos = None
        identity_octaves = None
        identity_cont = None
        f0_movement = 0.0
        f0_move_ratio = None
        best = None  # (score, candidate_wav, res, rate, cosine, octaves_off, cont, move, ratio, emb)
        candidates = []
        reused = bool(reuse_segments and os.path.isfile(seg_wav))
        if reused:
            # Re-gate/assemble already rendered audio (used to calibrate a gate or
            # re-assemble after a threshold change) without paying for synthesis.
            with wave.open(seg_wav, "rb") as wf:
                dur = wf.getnframes() / float(wf.getframerate() or sample_rate)
            frames, seg_rate = read_wav_frames(seg_wav)
            if seg_rate != sample_rate:
                raise ValueError(
                    f"{seg_wav}: sample rate {seg_rate} does not match chapter rate {sample_rate}")
            res = {"duration_sec": round(dur, 3)}
            rate_notes = [round(words_n / max(0.1, dur), 2)]
            try:
                emb = renderer.extract_speaker_embedding(seg_wav)
                identity_cos = _CASTING.cosine_similarity(emb, cond)
                prev_emb = prev_accepted.get(voice_id)
                if prev_emb is not None:
                    identity_cont = _CASTING.cosine_similarity(emb, prev_emb)
                prev_accepted[voice_id] = emb
            except Exception:
                pass
            golden_f0 = golden_pitch.get(voice_id) or 0.0
            golden_move = golden_movement.get(voice_id) or 0.0
            voiced_n = 0
            if golden_f0 > 0:
                draw_f0, f0_movement, voiced_n = f0_voiced_stats(seg_wav)
                if draw_f0 > 0:
                    identity_octaves = abs(math.log2(draw_f0 / golden_f0))
            if golden_move > 0 and f0_movement > 0 and voiced_n >= 8:
                f0_move_ratio = f0_movement / golden_move
        for attempt in ([] if reused else range(MAX_SYNTH_ATTEMPTS)):
            attempts = attempt + 1
            cand_wav = f"{seg_wav}.draw{attempt}.wav"
            candidates.append(cand_wav)
            res_try = renderer.synthesize_to_wav(
                text=spoken,  # tags included: each backend decides what to do with them
                out_wav_path=cand_wav,
                voice_id=voice_id,
                voice_design=vinfo["voice_design"],
                style=seg.get("style") or {},
                sample_rate=sample_rate,
                # Repeated lines must not render byte-identically ("Mittens said."
                # three times sounded like machine echoes); salt the seed with the
                # segment id so repeats vary while re-renders stay reproducible,
                # and re-draw degenerate deliveries on retry.
                seed_salt=f"{seg_id}#d{attempt}",
                # VOICE_CLONE_FROM_GOLDEN: every segment is conditioned on the frozen
                # golden identity (CAM++ space). Unconditioned, the engine re-designs
                # the voice per call and same-design calls drift apart (measured
                # 0.40–0.81 cosine) — the drift gate below would rightly refuse the
                # whole book.
                speaker_embedding=cond,
                # ...and on the voice's own frozen prompt clip, which is the
                # stronger conditioning: real audio of the voice keeps its timbre
                # and recording character across calls, where an embedding alone
                # leaves it free to re-texture every draw.
                prompt_clip_path=acoustic_prompts.get(voice_id, (None, None))[0],
                prompt_clip_text=acoustic_prompts.get(voice_id, (None, None))[1],
            )
            if not res_try or not os.path.isfile(cand_wav):
                break
            dur = max(0.1, float(res_try["duration_sec"]))
            wps = words_n / dur
            rate_notes.append(round(wps, 2))
            plausible = dur <= max_plausible_sec(words_n)  # no loop/stall draws
            if words_n >= MIN_RATE_WORDS:
                plausible = plausible and MIN_WORDS_PER_SEC <= wps <= MAX_WORDS_PER_SEC
            if not plausible:
                continue  # degenerate draw (looped, rushed, or crawling) — re-render

            # Identity check on this draw: how close is the voice to its own frozen
            # golden? The chapter-level drift gate averages this away; the listener
            # does not. Keep the best draw, and spend at most one extra draw when the
            # first is below IDENTITY_GOOD_COS. (Continuity + liveliness, 2026-10-25:
            # the draw is also scored against the previous ACCEPTED segment of this
            # voice — selection against the golden alone lets neighbouring lines each
            # score well and still sound like different people, measured adjacent
            # cosine 0.24–0.87 on v7 — and a monotone draw is penalised against the
            # voice's own golden f0 movement, which is the 'robotic' Teasel take.)
            emb = None
            cos = None
            try:
                emb = renderer.extract_speaker_embedding(cand_wav)
                cos = _CASTING.cosine_similarity(emb, cond)
            except Exception:
                emb, cos = None, None
            identity_used += 1
            cont = None
            prev_emb = prev_accepted.get(voice_id)
            if emb is not None and prev_emb is not None:
                try:
                    cont = _CASTING.cosine_similarity(emb, prev_emb)
                except Exception:
                    cont = None
            octave_off = None
            movement = 0.0
            move_ratio = None
            golden_f0 = golden_pitch.get(voice_id) or 0.0
            golden_move = golden_movement.get(voice_id) or 0.0
            voiced_n = 0
            if golden_f0 > 0:
                draw_f0, movement, voiced_n = f0_voiced_stats(cand_wav)
                if draw_f0 > 0:
                    octave_off = abs(math.log2(draw_f0 / golden_f0))
            # Movement std over <8 voiced frames is noise, not prosody — one-second
            # lines must not be judged monotone on two frames of evidence.
            if golden_move > 0 and movement > 0 and voiced_n >= 8:
                move_ratio = movement / golden_move
            score = (cos if cos is not None else 0.0) - 1.5 * max(
                0.0, (octave_off or 0.0) - PITCH_ALLOWED_OCTAVES)
            if cont is not None:
                score = ((1.0 - CONTINUITY_WEIGHT) * score
                         + CONTINUITY_WEIGHT * cont)
            if move_ratio is not None:
                score -= 1.0 * max(0.0, FLAT_F0MOVE_GOOD - move_ratio)
            if best is None or score > best[0]:
                best = (score, cand_wav, res_try, rate_notes[-1], cos, octave_off,
                        cont, movement, move_ratio, emb)
            good = (cos is not None and cos >= IDENTITY_GOOD_COS
                    and (octave_off is None or octave_off <= IDENTITY_MAX_OCTAVES)
                    and (cont is None or cont >= CONTINUITY_GOOD_COS)
                    and (move_ratio is None or move_ratio >= FLAT_F0MOVE_FLOOR))
            if good:
                break
            if identity_used >= MAX_IDENTITY_DRAWS:
                break

        for cand in candidates:
            if best is not None and cand == best[1]:
                continue
            if os.path.isfile(cand):
                try:
                    os.remove(cand)
                except OSError:
                    pass
        if best is not None:
            try:
                os.replace(best[1], seg_wav)
            except OSError:
                best = None
            else:
                res = best[2]
                identity_cos = best[4]
                identity_octaves = best[5]
                identity_cont = best[6]
                f0_movement = best[7]
                f0_move_ratio = best[8]
                if best[9] is not None:
                    prev_accepted[voice_id] = best[9]

        if not res or not os.path.isfile(seg_wav):
            if rate_notes:
                fails.append(
                    f"{script_path}: segment {seg_id} refused after {attempts} draw(s) — "
                    f"no plausible delivery: rates {rate_notes} words/sec, "
                    f"max plausible duration {max_plausible_sec(words_n):.1f}s")
            else:
                fails.append(f"{script_path}: segment {seg_id} synthesis produced no WAV")
            continue

        # Level-match to one speech RMS so adjacent sentences do not step 9 dB.
        level_gain = normalize_speech_level(seg_wav)

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
            "synthesis_attempts": None if reused else attempts,
            "speech_rate_wps": rate_notes[-1] if rate_notes else None,
            "words": words_n,
            "reused": reused,
            "identity_cos": None if identity_cos is None else round(identity_cos, 4),
            "continuity_cos": None if identity_cont is None else round(identity_cont, 4),
            "pitch_octaves_from_golden": None if identity_octaves is None
            else round(identity_octaves, 3),
            "f0_movement_oct": round(f0_movement, 4),
            "f0_move_ratio": None if f0_move_ratio is None else round(f0_move_ratio, 3),
            "identity_draws": None if reused else identity_used,
            "level_gain_db": (None if reused else round(20 * math.log10(level_gain), 2)
                              if level_gain and level_gain != 1.0 else 0.0),
            "packed_from": seg.get("packed_from"),
        })

    if fails:
        return None, fails

    # Per-SEGMENT identity distribution gate: the aggregate gate below passes a voice
    # whose segments alternate between two voices. A chapter is refused when the
    # segment-level median or 10th percentile sits under the audible-drift floor.
    segment_identity = {}
    for vid in sorted({r.get("voice_id") for r in seg_records if r.get("voice_id")}):
        vals = [r["identity_cos"] for r in seg_records
                if r.get("voice_id") == vid and r.get("identity_cos") is not None
                and int(r.get("words") or 0) >= IDENTITY_MIN_WORDS]
        if len(vals) < IDENTITY_MIN_SEGMENTS:
            continue
        ordered = sorted(vals)
        median = ordered[len(ordered) // 2]
        p10 = ordered[max(0, int(round(0.10 * (len(ordered) - 1))))]
        entry = {"segments": len(vals), "min": round(ordered[0], 4),
                 "p10": round(p10, 4), "median": round(median, 4),
                 "max": round(ordered[-1], 4), "status": "OK"}
        if median < IDENTITY_MEDIAN_FLOOR or p10 < IDENTITY_P10_FLOOR:
            entry["status"] = "FAIL"
            fails.append(
                f"chapter-{ch_num:02d}: segment identity for {vid!r} is inconsistent — "
                f"median {median:.3f} (floor {IDENTITY_MEDIAN_FLOOR:.2f}), p10 {p10:.3f} "
                f"(floor {IDENTITY_P10_FLOOR:.2f}) across {len(vals)} segments; the voice "
                f"changes between utterances even though the chapter aggregate passes"
            )
        segment_identity[vid] = entry

    # Continuity distribution (report-only, 2026-10-25): cosine between each
    # accepted segment and the previous accepted segment of the same voice. v7
    # (selection against the golden alone) measured 0.24–0.87 on the narrator —
    # this is the number that tracks "sounds like a different person between
    # lines". Reported per voice; not gated, because the achievable floor on
    # 1-second lines is not yet calibrated (the same trap that refused Mittens).
    segment_continuity = {}
    for vid in sorted({r.get("voice_id") for r in seg_records if r.get("voice_id")}):
        vals = [r["continuity_cos"] for r in seg_records
                if r.get("voice_id") == vid and r.get("continuity_cos") is not None
                and int(r.get("words") or 0) >= IDENTITY_MIN_WORDS]
        if len(vals) < IDENTITY_MIN_SEGMENTS:
            continue
        ordered = sorted(vals)
        segment_continuity[vid] = {
            "segments": len(vals), "min": round(ordered[0], 4),
            "p10": round(ordered[max(0, int(round(0.10 * (len(ordered) - 1))))], 4),
            "median": round(ordered[len(ordered) // 2], 4),
            "max": round(ordered[-1], 4),
        }

    # TEXTURE spread (report-only, 2026-10-25): speaker cosine answers "is this the
    # same identity", which is a coarse question. Two draws of one voice can score
    # 0.85 against the golden and still differ audibly in timbre — the thing heard
    # as "it changed again". Mean-MFCC distance between a voice's own segments
    # catches that: on ch-01 the narrator measured 34.4 when every call was
    # conditioned on the embedding alone, and 14.2 when the same calls were also
    # conditioned on a real clip of the voice. Reported per voice so a regression
    # is visible instead of passing a cosine gate.
    segment_texture = {}
    try:
        import numpy as np
    except ImportError:
        np = None
    for vid in sorted({r.get("voice_id") for r in seg_records if r.get("voice_id")}):
        if np is None:
            break
        vecs = []
        for r in seg_records:
            if r.get("voice_id") != vid or int(r.get("words") or 0) < IDENTITY_MIN_WORDS:
                continue
            seg_path = os.path.join(seg_out_dir, f"{r['segment_id']}.wav")
            if not os.path.isfile(seg_path):
                continue
            try:
                vec = mean_mfcc_vector(seg_path)
            except Exception:
                vec = None
            if vec is not None:
                vecs.append(vec)
        if len(vecs) < IDENTITY_MIN_SEGMENTS:
            continue
        dists = [float(np.linalg.norm(vecs[i] - vecs[j]))
                 for i in range(len(vecs)) for j in range(i + 1, len(vecs))]
        dists.sort()
        segment_texture[vid] = {
            "segments": len(vecs),
            "median_mfcc_dist": round(dists[len(dists) // 2], 2),
            "p90_mfcc_dist": round(dists[max(0, int(round(0.90 * (len(dists) - 1))))], 2),
            "max_mfcc_dist": round(dists[-1], 2),
        }

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
        emb = verifier.embedding(tmp_wav)
        try:
            os.remove(tmp_wav)
        except OSError:
            pass
        cos = _CASTING.cosine_similarity(emb, frozen)
        # Identity check: the aggregate must match its own frozen voice better than
        # every other frozen cast voice, by a margin (gate 4b in the header).
        others = [(v2, _CASTING.cosine_similarity(emb, e2))
                  for v2, e2 in frozen_embeddings.items()
                  if v2 != voice_id and e2]
        best_other, best_other_cos = max(others, key=lambda kv: kv[1]) if others else (None, None)
        id_margin = None if best_other is None else cos - best_other_cos
        status = "OK"
        if cos < drift_min_cosine:
            status = "FAIL"
            fails.append(
                f"chapter-{ch_num:02d}: speaker drift for {voice_id!r} — rendered audio "
                f"cosine {cos:.4f} vs frozen golden embedding is below the drift floor "
                f"{drift_min_cosine:.2f} (Refusal Test #4 extension)"
            )
        elif id_margin is not None and id_margin < drift_id_margin:
            status = "FAIL"
            fails.append(
                f"chapter-{ch_num:02d}: voice mix-up for {voice_id!r} — rendered audio "
                f"identifies closest as {best_other!r} (margin {id_margin:.4f} over "
                f"own frozen voice is below {drift_id_margin:.2f}) (Refusal Test #4 extension)"
            )
        drift[voice_id] = {"cosine": round(cos, 6), "audio_sec": round(audio_sec, 2),
                           "closest_other": best_other,
                           "id_margin": None if id_margin is None else round(id_margin, 6),
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
        "script_segments": len(script_segments),
        "rendered_segments": rendered_count,
        "audio_source": ("reused-segments" if any(r.get("reused") for r in seg_records)
                         else "synthesized"),
        "duration_sec": round(duration_sec, 3),
        "speakers": sorted({s["speaker"] for s in seg_records}),
        "paralinguistic_tags": paralinguistic_used,
        "drift": drift,
        "segment_identity": segment_identity,
        "segment_continuity": segment_continuity,
        "segment_texture": segment_texture,
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
    ap.add_argument("--backend", default=None,
                    help="Synthesis backend (default: audiobook config 'backend', else ming)")
    ap.add_argument("--out-dir", default=None,
                    help="Audio output directory (default: <book>/audiobook/audio)")
    ap.add_argument("--script-dir", default=None,
                    help="Narration script directory (default: <book>/audiobook/scripts)")
    ap.add_argument("--drift-min-cosine", type=float, default=DEFAULT_DRIFT_MIN_COSINE,
                    help=f"Speaker-drift cosine floor (default: {DEFAULT_DRIFT_MIN_COSINE})")
    ap.add_argument("--drift-id-margin", type=float, default=DEFAULT_DRIFT_ID_MARGIN,
                    help="Required cosine margin of own frozen voice over the closest "
                         f"other cast voice (default: {DEFAULT_DRIFT_ID_MARGIN})")
    ap.add_argument("--reuse-segments", action="store_true",
                    help="Skip synthesis for segments already on disk, re-running the "
                         "gates and assembly only (gate calibration / re-assembly). "
                         "Never fabricates audio: a missing segment is still rendered.")
    ap.add_argument("--verifier", default="auto", choices=("auto", "ecapa", "campplus"),
                    help="Speaker-verification instrument for the identity gate: "
                         "ecapa (speechbrain ECAPA-TDNN on CPU), campplus (the engine's "
                         "own encoder), or auto (ECAPA when installed). Default: auto")
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

    backend_name = args.backend or ab_cfg.get("backend") or "ming"
    try:
        renderer = renderer_mod.create_renderer(backend_name)
    except (ValueError, RuntimeError) as exc:
        print(f"render-book: ERROR — {exc}", file=sys.stderr)
        return 3

    speaker_lookup = build_speaker_lookup(voices)

    # Frozen golden embeddings for the drift gate
    # The gate's instrument is deliberately NOT the engine's conditioning encoder:
    # CAM++ cannot separate the cast on this engine's output (see verifier.py). The
    # reference side is embedded from the frozen golden WAVs with the same verifier
    # used on the rendered side. `speaker_embedding.json` keeps its own job — it is
    # what the renderer feeds the engine for identity conditioning — so switching
    # instrument changes no audio, only how the gate measures it.
    verifier_mod = load_module("audio_verifier", os.path.join(HERE, "verifier.py"))
    try:
        verifier, verifier_note = verifier_mod.make_verifier(args.verifier, renderer)
    except (ValueError, RuntimeError) as exc:
        print(f"render-book: ERROR — {exc}", file=sys.stderr)
        return 3

    frozen_embeddings = {}
    for vid, frec in manifest.get("voices", {}).items():
        golden_rel = frec.get("golden_wav", "")
        if not golden_rel:
            continue
        golden_path = os.path.join(book_root, golden_rel)
        if not os.path.isfile(golden_path):
            continue
        cache_path = os.path.join(
            os.path.dirname(golden_path), f"verifier-{verifier.kind}.json")
        golden_sha = frec.get("golden_wav_sha256", "")
        cached = None
        if os.path.isfile(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as fh:
                    obj = json.load(fh)
                if obj.get("golden_wav_sha256") == golden_sha:
                    cached = obj.get("embedding") or None
            except (OSError, ValueError):
                cached = None
        if cached is None:
            cached = verifier.embedding(golden_path)
            try:
                with open(cache_path, "w", encoding="utf-8", newline="\n") as fh:
                    json.dump({"voice_id": vid, "verifier": verifier.kind,
                               "golden_wav_sha256": golden_sha,
                               "embedding": cached}, fh, indent=2)
                    fh.write("\n")
            except OSError:
                pass
        frozen_embeddings[vid] = cached

    # Identity CONDITIONING is a different vector than the gate's. The engine's
    # spk_head consumes CAM++ embeddings (what freeze stores in
    # `speaker_embedding.json`); the verifier embeddings above live in ECAPA's
    # space and feeding them to the engine would condition synthesis on the wrong
    # embedding space — the rendered voice would be arbitrary and the drift gate
    # would rightly refuse all of it. Switching verifier instruments must change
    # how the gate measures, never what the audio is.
    # Each voice's register, from its own frozen golden reference: a draw an octave
    # away from it is a different person even when the embedding still scores well.
    golden_pitch = {}
    golden_movement = {}
    for vid, frec in manifest.get("voices", {}).items():
        golden_rel = frec.get("golden_wav", "")
        golden_path = os.path.join(book_root, golden_rel) if golden_rel else ""
        if golden_path and os.path.isfile(golden_path):
            try:
                f0, move, _n = f0_voiced_stats(golden_path)
            except Exception:
                f0, move = 0.0, 0.0
            if f0 > 0:
                golden_pitch[vid] = f0
            if move > 0:
                golden_movement[vid] = move

    conditioning_embeddings = {}
    expected_kind = getattr(renderer, "embedding_kind", "")
    for vid, frec in manifest.get("voices", {}).items():
        emb_rel = frec.get("speaker_embedding_file", "")
        emb_path = os.path.join(book_root, emb_rel)
        if emb_rel and os.path.isfile(emb_path):
            try:
                with open(emb_path, "r", encoding="utf-8") as fh:
                    obj = json.load(fh)
                vec = obj.get("embedding") or []
                kind = str(obj.get("embedding_kind") or "")
                if vec:
                    # A vector from the wrong embedding space scores ~0.06 against
                    # identical voices and conditions the engine on nothing. This
                    # happened once (reference-take stored the verifier's ECAPA
                    # vector here); refuse instead of rendering an hour on it.
                    if expected_kind and expected_kind not in kind:
                        print(
                            f"render-book: REFUSED — {emb_path} holds a {kind!r} "
                            f"embedding but the engine conditions and the gate "
                            f"measures in {expected_kind!r}; re-run `casting freeze` "
                            f"or `casting reference-take`", file=sys.stderr)
                        return 1
                    conditioning_embeddings[vid] = vec
            except (OSError, ValueError):
                pass

    # ACOUSTIC PROMPTS: (clip path, known transcript) per voice. An embedding
    # pins identity but not how the voice sounds in this recording, so segments
    # conditioned on the embedding alone varied 34.4 in mean-MFCC distance from
    # each other on ch-01 while identity cosine stayed at 0.795 — the listener
    # heard "a different person" on audio the drift gate passed. With the clip,
    # the same measurement is 14.2. Minted by `casting.py prompt-clip` from each
    # voice's own synthetic golden, never from a real person.
    acoustic_prompts = {}
    for vid, frec in manifest.get("voices", {}).items():
        clip_rel = frec.get("prompt_clip") or ""
        clip_path = os.path.join(book_root, clip_rel) if clip_rel else ""
        clip_text = frec.get("prompt_clip_text") or ""
        if clip_rel and clip_text and os.path.isfile(clip_path):
            acoustic_prompts[vid] = (clip_path, clip_text)

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
        "verifier": verifier.kind,
        "verifier_note": verifier_note,
        "drift_min_cosine": args.drift_min_cosine,
        "drift_id_margin": args.drift_id_margin,
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
                drift_id_margin=args.drift_id_margin,
                frozen_embeddings=frozen_embeddings,
                conditioning_embeddings=conditioning_embeddings,
                verifier=verifier,
                golden_pitch=golden_pitch,
                golden_movement=golden_movement,
                acoustic_prompts=acoustic_prompts,
                reuse_segments=args.reuse_segments,
            )
        except (ValueError, RuntimeError) as exc:
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
    print(f"   verifier:     {verifier_note}")
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
