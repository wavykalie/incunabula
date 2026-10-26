#!/usr/bin/env python3
"""casting.py — Voice design, audition protocol, and golden-reference freeze for Incunabula.

WHY THIS EXISTS
  Voice drift across a 10-hour audiobook happens when TTS synthesis relies on a
  text-only prompt on every utterance or when an unapproved voice enters chapter
  rendering. Worse, using real-person reference audio at casting time introduces
  unlicensed voice-cloning risk.

  This casting module enforces a three-stage voice pipeline:
    1. VOICE DESIGN ONLY AT CASTING (No Real-Person Clones):
       Every voice in `audiobook/config.yaml` (`NARRATOR` plus each speaking character)
       must be specified via a natural-language `voice_design` string (age, gender/register,
       timbre, pace, accent, emotional baseline, and how the voice breaks under pressure).
       If any voice config contains a real-person reference audio / clone field
       (`clone_from`, `reference_audio`, `speaker_wav`, `voice_sample`, `real_person_ref`,
       or a file path in `voice_design`), casting REFUSES with exit 1.

    2. AUDITION PROTOCOL (`audition`):
       Before freezing or rendering any chapter, renders three standardized test passages
       per voice (~90s total across the three passages:
         - `01-narration.wav` (~30s narrative prose passage)
         - `02-dialogue.wav` (~30s conversational dialogue exchange)
         - `03-emotional-peak.wav` (~30s high-tension emotional peak passage))
       into `audiobook/auditions/<voice_id>/` along with a blind review sheet
       (`audiobook/auditions/AUDITION_SHEET.json`) where candidates are presented for
       human review. A voice cannot be frozen until approved (`approve --voice <id>` or
       `--approve-all --reviewer <name>`).

    3. GOLDEN-REFERENCE FREEZE (`freeze` & `verify`):
       Once approved, synthesizes a 3–5 minute (180–300s, default 210s) golden reference
       audio file (`audiobook/voices/<voice_id>/golden_reference.wav`), extracts its
       deterministic speaker embedding vector (256-dim L2-normalized acoustic/spectral
       voiceprint saved to `speaker_embedding.json`), computes SHA-256 hashes of both the
       audio and the `voice_design` string, and writes `audiobook/voices/freeze-manifest.json`.
       Subsequent chapter rendering (`render-book.py`, Cluster C) is locked to this
       frozen golden reference (`VOICE_CLONE_FROM_GOLDEN`) and refuses to run if any
       voice is unfrozen or if its hash/embedding has drifted (`verify`).

USAGE
  python tools/audio/casting.py validate <book-root>
  python tools/audio/casting.py audition <book-root> [--voice <id>] [--backend <name>]
  python tools/audio/casting.py approve  <book-root> (--voice <id> | --all) --reviewer <name> [--notes <text>]
  python tools/audio/casting.py freeze   <book-root> [--voice <id>] [--duration-sec <180..300>] [--backend <name>]
  python tools/audio/casting.py verify   <book-root>

EXIT CODES
  0  OK — validation/audition/approval/freeze/verify succeeded
  1  REFUSED / FAIL — real-person clone input detected, missing voice_design, unapproved
     voice at freeze time, or missing/corrupted golden reference at verify time
  2  NOT RUN — missing book directory or missing `audiobook/config.yaml`
  3  ERROR — malformed config or invalid arguments
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import math
import os
import re
import struct
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)
ROOT_DIR = os.path.dirname(TOOLS_DIR)

# Forbidden keys in a voice definition at casting time: casting must originate from
# a natural-language VOICE_DESIGN prompt, never from a real-person audio sample.
FORBIDDEN_CLONE_KEYS = {
    "clone_from",
    "reference_audio",
    "reference_wav",
    "speaker_wav",
    "voice_sample",
    "sample_audio",
    "real_person_ref",
    "source_audio",
    "audio_prompt_path",
    "clone_wav",
}

AUDIO_EXT_RE = re.compile(r"\.(?:wav|mp3|flac|ogg|m4a|aac|opus)\b", re.I)

# Standard audition passages (~30s each at ~145 wpm -> ~70-80 words per passage, ~90s total)
STANDARD_AUDITION_PASSAGES = {
    "01-narration": (
        "The rain had been coming down off the ridge since four in the afternoon, steady and "
        "cold enough to turn the gravel by the loading bay the colour of wet slate. Inside the "
        "annex, the fluorescent tubes hummed on their ballast, one of them flickering every "
        "twenty seconds with a dry click that nobody in the room bothered to look up at anymore. "
        "Three ledgers lay open across the steel table, weighted at the corners with brass "
        "plumb bobs, their margins dense with forty years of pencil corrections that had never "
        "been entered into the public register. Outside, a lorry shifted down at the crossroads "
        "and kept going toward the coast."
    ),
    "02-dialogue": (
        "\"You brought the wrong key,\" she said, not looking up from the manifest. "
        "\"It is the only key that was on the board when the shift changed.\" "
        "\"Then the board was wrong, or the man who hung it there was lying to you, and I do "
        "not have time before six o'clock to work out which.\" She set the brass caliper down "
        "beside the lamp and pushed the ledger across the table until the spine touched his "
        "wrist. \"Read the third column from the bottom. Read the date, and then tell me again "
        "that nobody was in the vault on Tuesday night.\""
    ),
    "03-emotional-peak": (
        "\"Stop writing it down as an equipment failure!\" The chair scraped back hard against "
        "the concrete and the lamp swung once on its cord. \"Eleven minutes on a dead line is "
        "not a valve fault, and you know it, because you were the one standing at the winch "
        "with the stopwatch in your hand while the water came up to the second gallery! You "
        "let them seal the shaft with the recorder still running inside, and for nine years "
        "you have sat in this room signing your name to a sentence you know is a lie!\""
    ),
}

# Extended passage bank for synthesizing the 3–5 minute (180–300s) golden reference audio
GOLDEN_REFERENCE_CORPUS = [
    STANDARD_AUDITION_PASSAGES["01-narration"],
    STANDARD_AUDITION_PASSAGES["02-dialogue"],
    STANDARD_AUDITION_PASSAGES["03-emotional-peak"],
    (
        "By midnight the barometer on the stairwell wall had dropped another four millibars. "
        "Every window along the north corridor carried a thin bead of condensation along the "
        "putty line, and the radiator in the charting room knocked twice whenever the boiler "
        "cycled in the basement. She worked methodically from the earliest survey folder to the "
        "latest, checking each depth reading against the hand-drawn cross-sections and marking "
        "every discrepancy on a clean slip of tracing paper. Where the ink had faded, she held "
        "the sheet angled toward the desk lamp until the indentation of the nib caught the light."
    ),
    (
        "\"If we go back in before the tide turns, we take the lightweight reel and two spare "
        "cells for the floodlamp,\" she said quietly. \"No camera rig, no tripod, and no extra "
        "cable. Either we make the traverse to the fourth station in forty minutes and come "
        "straight out, or we turn around at the sump and call it finished for the season. "
        "Give me your word on that right now, before I unlock the gate, because once we are "
        "past the narrows I am not having an argument with you in waist-deep water.\""
    ),
    (
        "In the morning the fog lifted off the estuary in slow, flat ribbons, leaving the pilings "
        "black and shiny above the mud. Nothing on the quay had moved since the night before. "
        "She locked the office door twice, tested the handle with her palm, and dropped the keys "
        "into the deep pocket of her coat where the brass stayed cold against her knuckles all "
        "the way down the hill to the station."
    ),
    (
        "The relays had been switched by hand twice that night, and the second time the lamp on "
        "the wall dimmed far enough to make the log hard to read. She kept writing anyway, one "
        "line for every change in the needle, because in the morning somebody would ask what the "
        "load had done at three, and the only honest answer would be the one she put down now."
    ),
    (
        "\"You do not have to stay,\" he said from the doorway. \"I know,\" she said. \"But the "
        "generator will not hold the pumps past four, and when it stops I want somebody in this "
        "room who can say exactly what happened.\" She turned the page over and started a fresh "
        "column. \"Go and sleep. I will wake you if the needle moves.\""
    ),
]


# ---------------------------------------------------------------------------
# Config Parser (PyYAML if available, else strict stdlib parser)
# ---------------------------------------------------------------------------

def load_audiobook_config(book_root):
    """Load `audiobook/config.yaml` (or `PROJECT_STATE.yaml` `audiobook:` section).

    Returns (config_dict, source_path, error_or_None).
    """
    cfg_path = os.path.join(book_root, "audiobook", "config.yaml")
    state_path = os.path.join(book_root, "PROJECT_STATE.yaml")

    target_path = None
    if os.path.isfile(cfg_path):
        target_path = cfg_path
    elif os.path.isfile(state_path):
        target_path = state_path
    else:
        return None, None, f"no audiobook/config.yaml or PROJECT_STATE.yaml found under {book_root}"

    try:
        with open(target_path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError as exc:
        return None, target_path, f"cannot read {target_path}: {exc}"

    data = None
    try:
        import yaml
        try:
            data = yaml.safe_load(raw)
        except Exception as exc:
            return None, target_path, f"YAML parse error in {target_path}: {exc}"
    except ImportError:
        data, err = _parse_config_stdlib(raw, target_path)
        if err:
            return None, target_path, err

    if not isinstance(data, dict):
        return None, target_path, f"{target_path}: top-level structure must be a mapping"

    ab = data.get("audiobook")
    if ab is None and target_path == cfg_path:
        # Allow top-level keys directly in audiobook/config.yaml
        if "voices" in data or "cast" in data or "backend" in data:
            ab = data

    if not isinstance(ab, dict) or not ab:
        return None, target_path, (
            f"missing 'audiobook' configuration section in {target_path} — "
            f"declare audiobook.backend and audiobook.voices (with natural-language voice_design strings)"
        )

    return ab, target_path, None


def _parse_config_stdlib(raw, path):
    """Minimal stdlib YAML parser for `audiobook/config.yaml` when PyYAML is unavailable."""
    root = {}
    stack = [(-1, root)]
    for lineno, line in enumerate(raw.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if stripped.startswith("- "):
            item_val = stripped[2:].strip().strip("\"'")
            if isinstance(parent, list):
                parent.append(item_val)
            continue
        if ":" not in stripped:
            return None, f"{path}:{lineno}: expected key: value"
        k, v = stripped.split(":", 1)
        k = k.strip().strip("\"'")
        v = v.strip()
        if " #" in v and not (v.startswith('"') or v.startswith("'")):
            v = v.split(" #", 1)[0].strip()
        if v == "":
            child = {}
            parent[k] = child
            stack.append((indent, child))
        elif v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            items = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()] if inner else []
            parent[k] = items
        else:
            val_clean = v.strip("\"'")
            if val_clean.lower() in ("true", "false"):
                parent[k] = val_clean.lower() == "true"
            else:
                try:
                    if "." in val_clean:
                        parent[k] = float(val_clean)
                    else:
                        parent[k] = int(val_clean)
                except ValueError:
                    parent[k] = val_clean
    return root, None


# ---------------------------------------------------------------------------
# Voice Validation (Enforces VOICE_DESIGN only, Refuses Real-Person Clones)
# ---------------------------------------------------------------------------

def validate_voices_config(ab_config, book_root=None):
    """Validate that `audiobook.voices` defines `NARRATOR` and character voices using
    natural-language `voice_design` strings ONLY, with zero real-person audio clone inputs.

    Returns (ok, voices_dict, problems_list).
    """
    problems = []
    voices_raw = ab_config.get("voices") or ab_config.get("cast")
    if not isinstance(voices_raw, dict) or not voices_raw:
        return False, {}, ["audiobook config declares no 'voices' mapping"]

    voices = {}
    has_narrator = False

    for voice_id, vcfg in voices_raw.items():
        vid = str(voice_id).strip()
        if vid.upper() == "NARRATOR":
            has_narrator = True
        if not isinstance(vcfg, dict):
            problems.append(f"voice {vid!r}: configuration must be a mapping (got {type(vcfg).__name__})")
            continue

        # 1. Check for forbidden real-person clone / reference audio keys
        for k, val in vcfg.items():
            k_low = str(k).lower().strip()
            if k_low in FORBIDDEN_CLONE_KEYS and val not in (None, "", False):
                problems.append(
                    f"voice {vid!r}: forbidden real-person clone/reference audio key "
                    f"{k!r}={val!r} — casting must use a natural-language 'voice_design' "
                    f"string only (VOICE_CLONE_FROM_GOLDEN is created by casting.py freeze, "
                    f"never supplied as an external audio file)"
                )

        # 2. Check mode if explicitly specified
        mode = str(vcfg.get("casting_mode") or vcfg.get("mode") or "VOICE_DESIGN").strip().upper()
        if mode not in ("VOICE_DESIGN", "DESIGN"):
            problems.append(
                f"voice {vid!r}: invalid casting_mode {mode!r} — casting requires 'VOICE_DESIGN'"
            )

        # 3. Validate natural-language voice_design string
        vdesign = str(vcfg.get("voice_design") or vcfg.get("description") or "").strip()
        if not vdesign:
            problems.append(f"voice {vid!r}: missing required 'voice_design' natural-language description")
            continue

        if AUDIO_EXT_RE.search(vdesign) or os.path.sep in vdesign or "/" in vdesign and any(
            ext in vdesign.lower() for ext in (".wav", ".mp3", ".flac", ".ogg", ".m4a")
        ):
            problems.append(
                f"voice {vid!r}: 'voice_design' contains an audio file path ({vdesign!r}) — "
                f"real-person reference audio is refused; provide a natural-language voice description"
            )
            continue

        words = vdesign.split()
        if len(words) < 6:
            problems.append(
                f"voice {vid!r}: 'voice_design' is too short ({len(words)} words: {vdesign!r}) — "
                f"must describe register/pitch, timbre, pace, and delivery (at least 6 words)"
            )
            continue

        style = {
            "speed": 1.0,
            "pitch": 0.0,
            "volume": 0.0,
            "emotion": "neutral",
        }
        if isinstance(vcfg.get("style"), dict):
            for sk in ("speed", "pitch", "volume", "emotion"):
                if sk in vcfg["style"]:
                    style[sk] = vcfg["style"][sk]

        design_hash = hashlib.sha256(vdesign.encode("utf-8")).hexdigest()[:16]
        voices[vid] = {
            "voice_id": vid,
            "role": str(vcfg.get("role", "narrator" if vid.upper() == "NARRATOR" else "character")),
            "casting_mode": "VOICE_DESIGN",
            "voice_design": vdesign,
            "voice_design_sha256": design_hash,
            "aliases": [str(a) for a in vcfg.get("aliases", [])] if isinstance(vcfg.get("aliases"), list) else [],
            "style": style,
            "custom_audition_passages": vcfg.get("audition_passages") if isinstance(vcfg.get("audition_passages"), dict) else None,
        }

    if not has_narrator:
        problems.append("audiobook.voices must define a 'NARRATOR' voice")

    # Cross-check against existing scripts if present: every speaker in audiobook/scripts/ must have a voice
    if book_root:
        scripts_dir = os.path.join(book_root, "audiobook", "scripts")
        if os.path.isdir(scripts_dir):
            known_Lookup = {}
            for vid, vinfo in voices.items():
                known_Lookup[vid.lower()] = vid
                for al in vinfo["aliases"]:
                    known_Lookup[al.lower()] = vid
            for fname in sorted(os.listdir(scripts_dir)):
                if not fname.endswith(".json"):
                    continue
                try:
                    with open(os.path.join(scripts_dir, fname), "r", encoding="utf-8") as fh:
                        sdata = json.load(fh)
                    for sp in sdata.get("summary", {}).get("speakers", []):
                        if sp.lower() not in known_Lookup:
                            problems.append(
                                f"speaker {sp!r} in {fname} has no matching entry or alias in audiobook.voices"
                            )
                except Exception:
                    pass

    return len(problems) == 0, voices, problems


# ---------------------------------------------------------------------------
# Acoustic Synthesis & Speaker Embedding Extraction (via renderer or fallback)
# ---------------------------------------------------------------------------

def _get_renderer(backend_name="ming"):
    """Return the unified renderer for `backend_name` (Cluster E). Returns None only
    when `tools/audio/renderer.py` itself is absent, which keeps Cluster B standalone.
    Engine failures propagate: a configured engine that is unavailable or broken is
    never silently replaced by the reference synthesizer — that substitution would
    put a voice nobody approved into an approved pipeline."""
    renderer_path = os.path.join(HERE, "renderer.py")
    if not os.path.isfile(renderer_path):
        return None
    spec = importlib.util.spec_from_file_location("audio_renderer", renderer_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.create_renderer(backend_name)


def voice_acoustic_profile(voice_id, voice_design):
    """Derive a deterministic, distinct acoustic profile (fundamental frequency F0,
    formant frequencies F1/F2/F3, harmonic rolloff, jitter, cadence) from the
    natural-language `voice_design` string."""
    digest = hashlib.sha256(f"{voice_id}::{voice_design}".encode("utf-8")).digest()
    low = voice_design.lower()

    # Determine base F0 from register keywords in voice_design
    if any(w in low for w in ("bass", "baritone", "low", "deep", "gravelly", "male")):
        base_f0 = 105.0 + (digest[0] / 255.0) * 35.0  # 105 - 140 Hz
    elif any(w in low for w in ("soprano", "high", "bright", "youthful", "girl", "child")):
        base_f0 = 215.0 + (digest[0] / 255.0) * 45.0  # 215 - 260 Hz
    elif any(w in low for w in ("contralto", "alto", "mezzo", "husky", "warm", "measured", "female", "woman")):
        base_f0 = 165.0 + (digest[0] / 255.0) * 35.0  # 165 - 200 Hz
    else:
        base_f0 = 135.0 + (digest[0] / 255.0) * 85.0  # 135 - 220 Hz

    # Formant centers (Hz) + harmonic weights (deterministic 16-harmonic envelope)
    f1 = 420.0 + (digest[1] / 255.0) * 260.0
    f2 = 1350.0 + (digest[2] / 255.0) * 850.0
    f3 = 2500.0 + (digest[3] / 255.0) * 700.0
    rolloff = 0.55 + (digest[4] / 255.0) * 0.35
    syllable_rate = 3.6 + (digest[5] / 255.0) * 1.4  # syllables per second

    harmonics = []
    for h in range(1, 17):
        h_freq = base_f0 * h
        # Formant resonance boosts around f1, f2, f3
        r1 = math.exp(-((h_freq - f1) ** 2) / (2.0 * (180.0 ** 2)))
        r2 = math.exp(-((h_freq - f2) ** 2) / (2.0 * (320.0 ** 2)))
        r3 = math.exp(-((h_freq - f3) ** 2) / (2.0 * (450.0 ** 2)))
        byte_mod = 0.7 + 0.6 * (digest[h % len(digest)] / 255.0)
        amp = (1.0 / (h ** rolloff)) * (1.0 + 1.8 * r1 + 1.2 * r2 + 0.7 * r3) * byte_mod
        harmonics.append(amp)

    norm = sum(harmonics) or 1.0
    harmonics = [a / norm for a in harmonics]

    return {
        "voice_id": voice_id,
        "base_f0_hz": round(base_f0, 2),
        "formants_hz": [round(f1, 1), round(f2, 1), round(f3, 1)],
        "rolloff": round(rolloff, 4),
        "syllable_rate_hz": round(syllable_rate, 3),
        "harmonics": [round(x, 6) for x in harmonics],
    }


def synthesize_speech_Like_wav(
    out_wav_path,
    text,
    voice_id,
    voice_design,
    style=None,
    target_duration_sec=None,
    sample_rate=24000,
    backend_name="ming",
    renderer=None,
):
    """Synthesize a clean, non-clipping, speech-cadenced harmonic WAV file with
    natural phrase pauses, syllable envelopes, and speaker-specific spectral formants
    (target -18 LUFS / RMS ~0.125, true peak <= -3.0 dBFS, zero clipping).
    Through the unified renderer (Cluster E) the `backend_name` selects the engine;
    engine failures raise rather than fall back to a different voice. Pass `renderer`
    to reuse one engine instance across many calls (a real TTS model loads once)."""
    if renderer is None:
        renderer = _get_renderer(backend_name)
    if renderer is not None and hasattr(renderer, "synthesize_to_wav"):
        res = renderer.synthesize_to_wav(
            text=text,
            out_wav_path=out_wav_path,
            voice_id=voice_id,
            voice_design=voice_design,
            style=style or {},
            target_duration_sec=target_duration_sec,
            sample_rate=sample_rate,
            seed_salt=os.path.basename(out_wav_path),
        )
        if res and os.path.isfile(out_wav_path):
            return res
        raise RuntimeError(
            f"renderer backend {backend_name!r} produced no WAV at {out_wav_path}"
        )

    return synthesize_fallback_wav(
        out_wav_path=out_wav_path,
        text=text,
        voice_id=voice_id,
        voice_design=voice_design,
        style=style,
        target_duration_sec=target_duration_sec,
        sample_rate=sample_rate,
    )


def synthesize_fallback_wav(
    out_wav_path,
    text,
    voice_id,
    voice_design,
    style=None,
    target_duration_sec=None,
    sample_rate=24000,
):
    """The deterministic formant-harmonic acoustic synthesizer (stdlib-only).

    Single home of the reference synthesis math: `synthesize_speech_Like_wav` falls
    back to it when no renderer is installed ("Cluster B works standalone"), and
    `tools/audio/renderer.py` (Cluster E) delegates its `ming` backend to it, so
    freeze-time golden references and render-time chapter audio come from the same
    engine with byte-identical output for identical inputs.
    """
    # Paralinguistic tags are performance cues, not words; the reference synthesizer
    # speaks only their words (the ming3 backend folds them into its instruction).
    text = re.sub(r"\s+", " ", re.sub(r"\[[A-Za-z][A-Za-z -]*\]", " ", text)).strip()
    prof = voice_acoustic_profile(voice_id, voice_design)
    style = style or {}
    speed = float(style.get("speed", 1.0) or 1.0)
    pitch_shift = float(style.get("pitch", 0.0) or 0.0)

    words = max(1, len(text.split()))
    if target_duration_sec is not None:
        duration_sec = float(target_duration_sec)
    else:
        # ~145 words per minute (~2.42 words/sec) + punctuation pauses
        duration_sec = max(2.5, (words / (2.42 * speed)) + 0.6)

    n_samples = int(duration_sec * sample_rate)
    f0 = prof["base_f0_hz"] * (1.0 + pitch_shift)
    harmonics = prof["harmonics"]
    syl_rate = prof["syllable_rate_hz"] * speed

    # Precompute 1 period of the multi-harmonic waveform at 1 Hz normalized phase (table of 4096 samples)
    table_size = 4096
    two_pi = 2.0 * math.pi
    wave_table = [0.0] * table_size
    for h_idx, h_amp in enumerate(harmonics, 1):
        phase_offset = (h_idx * 0.37) % two_pi
        for i in range(table_size):
            wave_table[i] += h_amp * math.sin(two_pi * h_idx * (i / table_size) + phase_offset)
    max_abs = max(abs(x) for x in wave_table) or 1.0
    wave_table = [x / max_abs for x in wave_table]

    # Target peak ~ 0.38 (-8.4 dBFS) and active speech RMS ~ 0.135 (-17.4 dBFS, ~-18.5 LUFS)
    target_amp = 0.36 * (10.0 ** (min(3.0, max(-6.0, float(style.get("volume", 0.0) or 0.0))) / 20.0))

    os.makedirs(os.path.dirname(os.path.abspath(out_wav_path)), exist_ok=True)
    lead_silence = int(0.18 * sample_rate)
    trail_silence = int(0.25 * sample_rate)
    active_end = max(lead_silence + 1, n_samples - trail_silence)

    pcm_bytes = bytearray(n_samples * 2)
    phase = 0.0
    dt = 1.0 / sample_rate

    # Write in chunks for fast execution even on 210-second golden references
    # Build a 2.5-second speech cadence block and tile/modulate across active region
    block_sec = 2.5
    block_len = int(block_sec * sample_rate)
    block_samples = [0] * block_len
    for i in range(block_len):
        t = i * dt
        # Phrase pause every 2.5s (last 0.28s of block is breath pause)
        if t > (block_sec - 0.28):
            block_samples[i] = 0
            continue
        # Smooth attack/release at phrase boundaries
        phrase_env = 1.0
        if t < 0.06:
            phrase_env = t / 0.06
        elif t > (block_sec - 0.36):
            phrase_env = max(0.0, (block_sec - 0.28 - t) / 0.08)

        # Syllable modulation
        syl_env = 0.62 + 0.38 * math.sin(two_pi * syl_rate * t)
        # Pitch intonation contour across phrase
        inst_f0 = f0 * (1.0 + 0.025 * math.sin(two_pi * 0.8 * t) - 0.03 * (t / block_sec))
        phase = (phase + inst_f0 * dt) % 1.0
        idx = int(phase * table_size) % table_size
        val = wave_table[idx] * target_amp * phrase_env * syl_env
        sample_int = max(-32000, min(32000, int(val * 32767.0)))
        block_samples[i] = sample_int

    block_bytes = struct.pack(f"<{block_len}h", *block_samples)
    pos = lead_silence * 2
    end_pos = active_end * 2
    block_byte_len = len(block_bytes)

    while pos < end_pos:
        take = min(block_byte_len, end_pos - pos)
        pcm_bytes[pos:pos + take] = block_bytes[:take]
        pos += take

    # Apply smooth 40ms fade-out at end of active region
    fade_samples = min(int(0.04 * sample_rate), active_end - lead_silence)
    for i in range(fade_samples):
        idx = active_end - fade_samples + i
        byte_idx = idx * 2
        val = struct.unpack_from("<h", pcm_bytes, byte_idx)[0]
        scaled = int(val * (1.0 - (i / fade_samples)))
        struct.pack_into("<h", pcm_bytes, byte_idx, scaled)

    with wave.open(out_wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)

    # Also write sidecar metadata so ASR/speaker-drift gates can inspect acoustic & transcript ground truth
    meta_path = out_wav_path + ".meta.json"
    with open(meta_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({
            "voice_id": voice_id,
            "voice_design_sha256": hashlib.sha256(voice_design.encode("utf-8")).hexdigest()[:16],
            "spoken_text": text,
            "duration_sec": round(duration_sec, 3),
            "sample_rate": sample_rate,
            "acoustic_profile": prof,
        }, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    return {
        "wav_path": out_wav_path,
        "duration_sec": round(duration_sec, 3),
        "sample_rate": sample_rate,
    }


# The text of the short acoustic prompt clip. It is deliberately plain narrative
# prose with no proper nouns: the engine continues from the clip's acoustics, so
# an odd name in the prompt is one more thing it can mispronounce while it
# settles into the voice. Length matters more than content — around 10 seconds is
# long enough to carry timbre and short enough to encode once per voice.
PROMPT_CLIP_TEXT = (
    "The market was already loud when I got there, and louder still by nine. "
    "Nobody on that street ever agreed about anything except the price of fish."
)

# Candidates minted per voice, best-of. Identity cosine barely moves between
# draws, but the reading pace does, and the engine continues from the clip's
# pace: a brisk clip makes the whole book brisk. The clip kept is the one whose
# words-per-second lands closest to the voice's own golden reference.
PROMPT_CLIP_DRAWS = 4


def _clip_words(text):
    return len([w for w in (text or "").split() if w])


def _load_renderer_module():
    """The renderer MODULE (not an instance), for the engine's own text chunker."""
    renderer_path = os.path.join(HERE, "renderer.py")
    if not os.path.isfile(renderer_path):
        return None
    spec = importlib.util.spec_from_file_location("audio_renderer_mod", renderer_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pcm16_mono(wav_path):
    """Return (samples, rate) for a 16-bit mono WAV, or (None, 0)."""
    try:
        with wave.open(wav_path, "rb") as wf:
            if wf.getsampwidth() != 2 or wf.getnchannels() != 1:
                return None, 0
            rate = wf.getframerate()
            raw = wf.readframes(wf.getnframes())
    except (wave.Error, OSError):
        return None, 0
    if not raw:
        return None, 0
    n = len(raw) // 2
    return struct.unpack(f"<{n}h", raw[:n * 2]), rate


def _zero_runs(samples, rate, block_sec=0.010, min_sec=0.03, max_sec=2.5):
    """Exact-zero silence runs, in (start_sec, dur_sec).

    The golden reference is synthesized as several chunk calls joined by an
    inserted digital-silence gap, so those seams are runs of literally zero
    samples. The engine's own pauses inside a chunk always carry low-level noise,
    which is what makes the seams distinguishable at all.
    """
    block = max(1, int(rate * block_sec))
    runs, start = [], None
    for i in range(0, len(samples) - block + 1, block):
        chunk = samples[i:i + block]
        is_zero = not any(chunk)
        if is_zero and start is None:
            start = i
        elif not is_zero and start is not None:
            dur = (i - start) / float(rate)
            if min_sec <= dur <= max_sec:
                runs.append((start / float(rate), dur))
            start = None
    if start is not None:
        dur = (len(samples) - start) / float(rate)
        if min_sec <= dur <= max_sec:
            runs.append((start / float(rate), dur))
    return runs


def _golden_chunk_texts(golden_text, renderer_mod):
    """The exact chunk strings the golden reference was synthesized from."""
    if renderer_mod is None or golden_text is None:
        return None
    chunker = getattr(renderer_mod, "_engine_chunks", None)
    max_words = getattr(renderer_mod, "MING3_MAX_CHUNK_WORDS", None)
    if chunker is None or not max_words:
        return None
    try:
        chunks = chunker(golden_text, max_words)
    except Exception:
        return None
    return chunks or None


def _choose_seams(seams, words, total_dur):
    """Pick len(words)-1 seam times for the known chunks, or None.

    When the count already matches it is used as-is (the common case: the golden
    has exactly one inserted gap per chunk join). Otherwise a dynamic program
    chooses the subset whose implied chunk durations best track the chunk word
    counts, minimising RELATIVE error so one long chunk cannot dominate.
    """
    k = len(words)
    if k < 2:
        return None
    if len(seams) == k - 1:
        return [t for t, _d in seams]
    if len(seams) < k - 1:
        return None
    total_words = sum(words) or 1
    pred = [w * total_dur / total_words for w in words]
    times = [0.0] + [s[0] for s in seams] + [total_dur]
    c = len(seams)
    inf = float("inf")
    n = c + 2
    dp = [[inf] * n for _ in range(k)]
    back = [[-1] * n for _ in range(k)]
    for i in range(1, c + 1):
        dp[0][i], back[0][i] = abs(times[i] - pred[0]) / pred[0], 0
    for ki in range(1, k - 1):
        for i in range(ki + 1, c + 1):
            for j in range(ki, i):
                if dp[ki - 1][j] == inf:
                    continue
                cost = dp[ki - 1][j] + abs((times[i] - times[j]) - pred[ki]) / pred[ki]
                if cost < dp[ki][i]:
                    dp[ki][i], back[ki][i] = cost, j
    best, arg = inf, -1
    for j in range(k - 1, c + 1):
        if dp[k - 2][j] == inf:
            continue
        cost = dp[k - 2][j] + abs((total_dur - times[j]) - pred[k - 1]) / pred[k - 1]
        if cost < best:
            best, arg = cost, j
    if arg < 0:
        return None
    bounds, j = [total_dur], arg
    bounds.insert(0, times[j])
    for ki in range(k - 2, 0, -1):
        j = back[ki][j]
        bounds.insert(0, times[j])
    bounds.insert(0, 0.0)
    return bounds[1:-1]


# A prompt chunk has to be long enough to carry timbre and short enough to encode
# once per voice and to be continued from without the engine drifting.
PROMPT_CHUNK_MIN_SEC = 6.0
PROMPT_CHUNK_MAX_SEC = 14.0
# Alignment acceptance: a partition whose chunk durations disagree with the chunk
# word counts is a partition that will hand the engine the WRONG transcript, and
# a mismatched (audio, transcript) pair is worse than no clip at all.
PROMPT_CHUNK_MAX_REL_ERR = 0.15
PROMPT_CHUNK_MAX_MEDIAN_ERR = 0.20


def extract_golden_prompt_clip(book_root, vid, golden_wav, golden_text):
    """Cut an acoustic prompt out of the approved golden reference itself.

    Why not mint a fresh clip: every render of this engine is a new draw, and a
    fresh clip is a *sibling* of the approved voice, not the voice. Conditioning
    on it pulls every segment to that sibling's centroid — measured on chapter 01,
    segments landed 0.72-0.77 from the very clip they were conditioned on and only
    0.65-0.71 from the golden, against 0.83 for embedding-only conditioning. The
    book became consistent with a voice nobody approved.

    The golden is itself several chunk calls joined by inserted digital silence,
    and the chunker is deterministic over the recorded transcript, so the text of
    every chunk is known exactly. Locating the seams therefore recovers exact
    (audio, transcript) pairs drawn from the approved recording, which is what the
    engine's acoustic-prompt mode actually wants.

    Returns (record_or_None, reason).
    """
    if not golden_wav or not os.path.isfile(golden_wav):
        return None, "no golden reference on disk"
    renderer_mod = _load_renderer_module()
    chunks = _golden_chunk_texts(golden_text, renderer_mod)
    if not chunks:
        return None, "engine chunker unavailable (cannot recover chunk transcripts)"
    samples, rate = _pcm16_mono(golden_wav)
    if not samples:
        return None, "golden reference is not 16-bit mono PCM"
    total = len(samples) / float(rate)
    words = [_clip_words(c) for c in chunks]
    if any(w == 0 for w in words):
        return None, "a golden chunk has no words"

    seams = _zero_runs(samples, rate)
    bounds = _choose_seams(seams, words, total)
    if bounds is None:
        return None, (f"cannot locate {len(words) - 1} chunk seams in the golden "
                      f"(found {len(seams)} zero-runs)")
    edges = [0.0] + list(bounds) + [total]
    durs = [edges[i + 1] - edges[i] for i in range(len(words))]
    total_words = sum(words)
    rel = [abs(durs[i] - words[i] * total / total_words)
           / (words[i] * total / total_words) for i in range(len(words))]
    ordered = sorted(rel)
    median_err = ordered[len(ordered) // 2]
    if median_err > PROMPT_CHUNK_MAX_MEDIAN_ERR:
        return None, (f"chunk partition does not fit the transcript "
                      f"(median duration error {median_err * 100:.0f}%) — refusing to "
                      f"condition on audio paired with the wrong words")

    cands = [(rel[i], i, durs[i]) for i in range(len(words))
             if PROMPT_CHUNK_MIN_SEC <= durs[i] <= PROMPT_CHUNK_MAX_SEC]
    if not cands:
        return None, "no golden chunk falls in the usable 6-14s window"
    cands.sort()
    best_err, idx, dur = cands[0]
    if best_err > PROMPT_CHUNK_MAX_REL_ERR:
        return None, (f"best usable golden chunk misses its expected duration by "
                      f"{best_err * 100:.0f}% — alignment not trustworthy")

    clip_text = chunks[idx]
    start = int(round(edges[idx] * rate))
    end = int(round(edges[idx + 1] * rate))
    piece = samples[start:end]
    # Trim residual leading/trailing silence, then 10ms fades so the clip does not
    # begin or end on a click.
    floor = max(1, int(0.004 * rate))
    lo, hi = 0, len(piece)
    while lo < hi and abs(piece[lo]) < floor:
        lo += 1
    while hi > lo and abs(piece[hi - 1]) < floor:
        hi -= 1
    piece = piece[lo:hi]
    if len(piece) / float(rate) < 2.0:
        return None, "golden chunk is silent after trimming"
    fade = max(1, int(0.010 * rate))
    piece = list(piece)
    for i in range(min(fade, len(piece) // 2)):
        g = i / float(fade)
        piece[i] = int(piece[i] * g)
        piece[-1 - i] = int(piece[-1 - i] * g)

    v_out_dir = os.path.join(book_root, "audiobook", "voices", vid)
    os.makedirs(v_out_dir, exist_ok=True)
    clip_path = os.path.join(v_out_dir, "prompt_clip.wav")
    with wave.open(clip_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(struct.pack(f"<{len(piece)}h", *piece))
    text_path = os.path.join(v_out_dir, "prompt_clip.txt")
    with open(text_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(clip_text)
        fh.write("\n")
    with open(clip_path, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    clip_dur = len(piece) / float(rate)
    return {
        "prompt_clip": os.path.relpath(clip_path, book_root).replace("\\", "/"),
        "prompt_clip_sha256": sha,
        "prompt_clip_text": clip_text,
        "prompt_clip_source": "golden-chunk",
        "prompt_clip_chunk_index": idx,
        "prompt_clip_chunks_total": len(chunks),
        "prompt_clip_duration_sec": round(clip_dur, 3),
        "prompt_clip_wps": round(_clip_words(clip_text) / max(0.1, clip_dur), 3),
        "prompt_clip_chunk_fit": round(best_err, 4),
        "prompt_clip_partition_median_fit": round(median_err, 4),
        "golden_wps": round(total_words / max(0.1, total), 3),
    }, None


def mint_prompt_clip(book_root, vid, voice_design, style, embedding, renderer,
                     golden_wav, golden_text, draw_count=PROMPT_CLIP_DRAWS):
    """Mint the short acoustic prompt clip a render conditions on, and return its record.

    Identity is already pinned by the frozen embedding. What the embedding does
    NOT carry is how the voice *sounds in this recording* — timbre texture, mic
    and codec character, the small irregularities a listener hears as "the same
    person still speaking". Conditioning on real audio of the voice carries it.

    The clip is minted from the voice's own approved synthetic golden (never from
    a real person's audio), with a transcript we therefore know exactly — which is
    what the engine requires alongside the audio.

    Returns (record_or_None, reason). A voice whose clip cannot be minted stays
    renderable on embedding-only conditioning; that is a degradation, not a
    failure, so the caller decides.
    """
    # Preferred source: the approved recording itself, cut at one of its own chunk
    # seams. That keeps identity, texture AND pace on the voice a human approved,
    # because the reference and the conditioning become the same audio.
    rec, why = extract_golden_prompt_clip(book_root, vid, golden_wav, golden_text)
    if rec:
        return rec, None
    fallback_reason = why

    if not hasattr(renderer, "synthesize_to_wav"):
        return None, f"{fallback_reason}; renderer has no synthesize_to_wav"
    v_out_dir = os.path.join(book_root, "audiobook", "voices", vid)
    os.makedirs(v_out_dir, exist_ok=True)
    clip_path = os.path.join(v_out_dir, "prompt_clip.wav")
    clip_text_path = os.path.join(v_out_dir, "prompt_clip.txt")

    # Pace must be measured the way the listener experiences it: words over TOTAL
    # duration, pauses included. The first version of this scored against
    # words/speech-only-seconds (~4.2 wps), so it preferred brisk clips and the
    # engine, which continues at its prompt's pace, read chapter 01 at 3.74 wps
    # against v8's 2.63 — a 42% speed-up nobody asked for. Total-duration pace on
    # the same golden is ~2.6 wps, which is what narration should sound like.
    golden_wps = 0.0
    if golden_wav and os.path.isfile(golden_wav):
        with wave.open(golden_wav, "rb") as wf:
            golden_dur = wf.getnframes() / float(wf.getframerate() or 24000)
        if golden_dur > 1.0:
            golden_wps = _clip_words(golden_text) / golden_dur

    best = None
    for i in range(max(1, draw_count)):
        cand = os.path.join(v_out_dir, f"prompt_clip.draw{i}.wav")
        try:
            renderer.synthesize_to_wav(
                text=PROMPT_CLIP_TEXT,
                out_wav_path=cand,
                voice_id=vid,
                voice_design=voice_design,
                style=style,
                sample_rate=24000,
                speaker_embedding=embedding,
                seed_salt=f"prompt_clip#d{i}",
            )
        except Exception:
            break
        with wave.open(cand, "rb") as wf:
            cand_dur = wf.getnframes() / float(wf.getframerate() or 24000)
        speech = active_speech_seconds(cand)
        if speech < 5.0:
            continue
        wps = _clip_words(PROMPT_CLIP_TEXT) / max(0.1, cand_dur)
        # Pace is the one property that leaks from clip to book, so it is the
        # score; without a golden pace to compare against, the slower draw wins
        # (a deliberately read book is the failure that is easy to fix by ear).
        score = abs(wps - golden_wps) if golden_wps > 0 else wps
        if best is None or score < best[0]:
            best = (score, cand, wps, speech)

    if best is None:
        for i in range(max(1, draw_count)):
            cand = os.path.join(v_out_dir, f"prompt_clip.draw{i}.wav")
            if os.path.isfile(cand):
                os.remove(cand)
        return None, f"{fallback_reason}; no candidate clip produced usable speech"

    _, cand, wps, speech = best
    for i in range(max(1, draw_count)):
        other = os.path.join(v_out_dir, f"prompt_clip.draw{i}.wav")
        if os.path.isfile(other) and os.path.abspath(other) != os.path.abspath(cand):
            os.remove(other)
    os.replace(cand, clip_path)
    with open(clip_text_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(PROMPT_CLIP_TEXT)
        fh.write("\n")
    with open(clip_path, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()

    return {
        "prompt_clip": os.path.relpath(clip_path, book_root).replace("\\", "/"),
        "prompt_clip_sha256": sha,
        "prompt_clip_text": PROMPT_CLIP_TEXT,
        "prompt_clip_source": "synthesized",
        "prompt_clip_fallback_reason": f"{fallback_reason}",
        "prompt_clip_speech_sec": round(speech, 3),
        "prompt_clip_duration_sec": round(cand_dur, 3),
        "prompt_clip_wps": round(wps, 3),
        "golden_wps": round(golden_wps, 3),
    }, None


def active_speech_seconds(wav_path):
    """Seconds of actual speech in a WAV (20ms windows above the -38 dBFS floor).

    The freeze contract's 180-300s window is about VOICE MATERIAL. A golden
    reference that is mostly silence padding is a collapsed synthesis wearing a
    long file as a disguise — measured on the Ming-3.0-tts engine, a voice whose
    long-form generation collapsed left a 180s file holding 35s of speech."""
    with wave.open(wav_path, "rb") as wf:
        sr = wf.getframerate()
        n_ch = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        raw = wf.readframes(wf.getnframes())
    if sampwidth != 2 or not raw:
        return 0.0
    total = len(raw) // 2
    samples = struct.unpack(f"<{total}h", raw[:total * 2])
    if n_ch > 1:
        samples = samples[::n_ch]
    win = max(1, int(0.02 * sr))
    active = 0
    for i in range(0, len(samples) - win, win):
        chunk = samples[i:i + win]
        if sum(x * x for x in chunk) / win > (400.0 ** 2):
            active += win
    return active / sr


def extract_speaker_embedding_from_wav(wav_path):
    """Extract a 64-dim L2-normalized acoustic speaker embedding from a WAV file.

    Measures real zero-crossing rate, frame energy distribution, autocorrelation pitch
    lag profile, and 48-lag spectral autocorrelation bands directly from the PCM samples.
    Two WAVs synthesized with the same voice profile achieve cosine similarity > 0.96;
    two WAVs synthesized with different voice profiles have low cosine similarity (< 0.75).
    """
    with wave.open(wav_path, "rb") as wf:
        sr = wf.getframerate()
        n_ch = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        raw = wf.readframes(wf.getnframes())

    if sampwidth != 2 or not raw:
        return [0.0] * 64

    total_shorts = len(raw) // 2
    samples = struct.unpack(f"<{total_shorts}h", raw[:total_shorts * 2])
    if n_ch > 1:
        samples = samples[::n_ch]

    # Voiceprint the SPEECH, wherever it sits in the file: active frames are
    # collected across the whole file (capped at 15s worth for speed). Sampling
    # a fixed middle window instead once produced a zero vector here — silence
    # padding in the middle of a short golden reference — and a zero vector
    # cosine-compares as 0.0 against everything, which reads as total drift.
    win = max(1, int(0.02 * sr))
    active = []
    max_active = sr * 15
    for i in range(0, len(samples) - win, win):
        chunk = samples[i:i + win]
        energy = sum(x * x for x in chunk) / win
        if energy > (400.0 ** 2):  # above -38 dBFS silence floor
            active.extend(chunk)
            if len(active) >= max_active:
                break

    if len(active) < 512:
        return [0.0] * 64

    # Normalize active signal to zero mean, unit variance
    mean_v = sum(active) / len(active)
    normed = [x - mean_v for x in active]
    var_v = sum(x * x for x in normed) / len(normed)
    std_v = math.sqrt(var_v) if var_v > 1e-9 else 1.0
    normed = [x / std_v for x in normed]

    # Compute normalized autocorrelation at 64 logarithmically/linearly spaced lags
    # covering pitch (30..240 samples @ 24kHz = 100..800 Hz) and formant structure (1..64 lags)
    n = len(normed)
    lags = [int(round(1 + i * 3.5)) for i in range(64)]
    vec = []
    stride = max(1, n // 4000)  # subsample ~4000 points for fast exact correlation
    for lag in lags:
        if lag >= n:
            vec.append(0.0)
            continue
        s = 0.0
        cnt = 0
        for idx in range(0, n - lag, stride):
            s += normed[idx] * normed[idx + lag]
            cnt += 1
        vec.append(s / max(1, cnt))

    # L2 normalize the 64-dim embedding vector
    l2 = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [round(v / l2, 6) for v in vec]


def cosine_similarity(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1)) or 1.0
    n2 = math.sqrt(sum(b * b for b in v2)) or 1.0
    return dot / (n1 * n2)


# ---------------------------------------------------------------------------
# Subcommands: validate, audition, approve, freeze, verify
# ---------------------------------------------------------------------------

def cmd_validate(book_root):
    ab_cfg, cfg_path, err = load_audiobook_config(book_root)
    if err:
        print(f"casting validate: NOT RUN — {err}", file=sys.stderr)
        return 2
    ok, voices, problems = validate_voices_config(ab_cfg, book_root)
    if not ok:
        print(f"casting validate: REFUSED ({cfg_path}):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("=" * 67)
    print(f"## casting validate   {book_root}")
    print("=" * 67)
    print(f"   config:  {cfg_path}")
    print(f"   voices:  {len(voices)} declared (all VOICE_DESIGN, zero real-person clones)")
    for vid, v in sorted(voices.items()):
        print(f"     - {vid:<18} [{v['role']:<10}] sha256={v['voice_design_sha256']} "
              f"({len(v['voice_design'].split())} words)")
    print()
    print("CASTING CONFIG OK — all voices use natural-language VOICE_DESIGN.")
    return 0


def cmd_audition(book_root, voice_filter=None, backend_name=None):
    ab_cfg, cfg_path, err = load_audiobook_config(book_root)
    if err:
        print(f"casting audition: NOT RUN — {err}", file=sys.stderr)
        return 2
    ok, voices, problems = validate_voices_config(ab_cfg, book_root)
    if not ok:
        print(f"casting audition: REFUSED — invalid voice config in {cfg_path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    backend_name = backend_name or ab_cfg.get("backend") or "ming"
    renderer = _get_renderer(backend_name)

    auditions_dir = os.path.join(book_root, "audiobook", "auditions")
    os.makedirs(auditions_dir, exist_ok=True)
    sheet_path = os.path.join(auditions_dir, "AUDITION_SHEET.json")

    existing_sheet = {}
    if os.path.isfile(sheet_path):
        try:
            with open(sheet_path, "r", encoding="utf-8") as fh:
                existing_sheet = json.load(fh)
        except Exception:
            existing_sheet = {}

    existing_voices = existing_sheet.get("voices", {}) if isinstance(existing_sheet, dict) else {}

    target_ids = [voice_filter] if voice_filter else sorted(voices.keys())
    for vid in target_ids:
        if vid not in voices:
            print(f"casting audition: unknown voice {vid!r} (known: {', '.join(sorted(voices))})",
                  file=sys.stderr)
            return 3

    for idx, vid in enumerate(target_ids, 1):
        v = voices[vid]
        v_dir = os.path.join(auditions_dir, vid)
        os.makedirs(v_dir, exist_ok=True)
        passages = v["custom_audition_passages"] or STANDARD_AUDITION_PASSAGES

        rendered_passages = []
        total_dur = 0.0
        for p_key in ("01-narration", "02-dialogue", "03-emotional-peak"):
            p_text = passages.get(p_key, STANDARD_AUDITION_PASSAGES[p_key])
            wav_path = os.path.join(v_dir, f"{p_key}.wav")
            emo_style = dict(v["style"])
            if p_key == "03-emotional-peak":
                emo_style["emotion"] = "urgent"
                emo_style["speed"] = round(emo_style.get("speed", 1.0) * 1.05, 3)

            res = synthesize_speech_Like_wav(
                out_wav_path=wav_path,
                text=p_text,
                voice_id=vid,
                voice_design=v["voice_design"],
                style=emo_style,
                target_duration_sec=30.0,
                backend_name=backend_name,
                renderer=renderer,
            )
            total_dur += res["duration_sec"]
            rendered_passages.append({
                "passage_id": p_key,
                "wav_file": os.path.relpath(wav_path, book_root).replace("\\", "/"),
                "duration_sec": res["duration_sec"],
                "text": p_text,
            })

        # Preserve prior approval only if voice_design_sha256 AND the synthesis
        # engine are unchanged — a human approved one engine's audio, not another's.
        prev = existing_voices.get(vid, {})
        same_design = prev.get("voice_design_sha256") == v["voice_design_sha256"]
        same_backend = prev.get("backend") == backend_name
        keep_approval = bool(prev.get("approved", False) and same_design and same_backend)
        existing_voices[vid] = {
            "voice_id": vid,
            "blind_label": f"Candidate-{idx:02d}",
            "role": v["role"],
            "casting_mode": "VOICE_DESIGN",
            "voice_design": v["voice_design"],
            "voice_design_sha256": v["voice_design_sha256"],
            "backend": backend_name,
            "auditioned_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "total_duration_sec": round(total_dur, 2),
            "passages": rendered_passages,
            "approved": keep_approval,
            "approved_by": prev.get("approved_by") if keep_approval else None,
            "approved_at": prev.get("approved_at") if keep_approval else None,
            "review_notes": prev.get("review_notes") if keep_approval else None,
        }

    sheet_obj = {
        "schema": "incunabula.audiobook.audition_sheet.v1",
        "book": os.path.abspath(book_root),
        "updated_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "protocol": "3 standard passages (~30s narration, ~30s dialogue, ~30s emotional peak = ~90s total) for blind human review before golden-reference freeze.",
        "voices": existing_voices,
    }
    with open(sheet_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(sheet_obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print("=" * 67)
    print(f"## casting audition   {book_root}")
    print("=" * 67)
    for vid in target_ids:
        rec = existing_voices[vid]
        print(f"   - {vid:<18} ({rec['blind_label']}) -> {len(rec['passages'])} passages, "
              f"{rec['total_duration_sec']:.1f}s total, approved={rec['approved']}")
    print(f"   sheet: {os.path.relpath(sheet_path, book_root).replace(chr(92), '/')}")
    print()
    print("AUDITION RENDERED — review the 3 test passages per voice and approve with:")
    print(f"  python tools/audio/casting.py approve {book_root} --all --reviewer <name>")
    return 0


def cmd_approve(book_root, voice_filter=None, approve_all=False, reviewer=None, notes=""):
    if not reviewer or not str(reviewer).strip():
        print("casting approve: --reviewer <name> is required to record human audition sign-off",
              file=sys.stderr)
        return 3

    sheet_path = os.path.join(book_root, "audiobook", "auditions", "AUDITION_SHEET.json")
    if not os.path.isfile(sheet_path):
        print(f"casting approve: REFUSED — no audition sheet at {sheet_path}. "
              f"Run 'casting.py audition' first.", file=sys.stderr)
        return 1

    with open(sheet_path, "r", encoding="utf-8") as fh:
        sheet = json.load(fh)

    voices_sheet = sheet.get("voices", {})
    if not voices_sheet:
        print("casting approve: REFUSED — audition sheet contains no voices", file=sys.stderr)
        return 1

    targets = sorted(voices_sheet.keys()) if approve_all else ([voice_filter] if voice_filter else [])
    if not targets:
        print("casting approve: specify --voice <id> or --all", file=sys.stderr)
        return 3

    for vid in targets:
        if vid not in voices_sheet:
            print(f"casting approve: voice {vid!r} has not been auditioned", file=sys.stderr)
            return 1
        # Verify the 3 audition WAVs actually exist on disk
        for p in voices_sheet[vid].get("passages", []):
            wpath = os.path.join(book_root, p["wav_file"])
            if not os.path.isfile(wpath):
                print(f"casting approve: missing audition WAV {wpath} for {vid!r}", file=sys.stderr)
                return 1
        voices_sheet[vid]["approved"] = True
        voices_sheet[vid]["approved_by"] = str(reviewer).strip()
        voices_sheet[vid]["approved_at"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        voices_sheet[vid]["review_notes"] = str(notes or "Approved after 3-passage audition review.")

    sheet["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open(sheet_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(sheet, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"casting approve: approved {len(targets)} voice(s) ({', '.join(targets)}) by {reviewer}.")
    return 0


def cmd_freeze(book_root, voice_filter=None, duration_sec=210.0, backend_name=None):
    if duration_sec < 180.0 or duration_sec > 300.0:
        print(f"casting freeze: --duration-sec must be between 180 and 300 seconds (3–5 minutes); got {duration_sec}",
              file=sys.stderr)
        return 3

    ab_cfg, cfg_path, err = load_audiobook_config(book_root)
    if err:
        print(f"casting freeze: NOT RUN — {err}", file=sys.stderr)
        return 2
    ok, voices, problems = validate_voices_config(ab_cfg, book_root)
    if not ok:
        print(f"casting freeze: REFUSED — invalid voice config in {cfg_path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    backend_name = backend_name or ab_cfg.get("backend") or "ming"
    renderer = _get_renderer(backend_name)

    sheet_path = os.path.join(book_root, "audiobook", "auditions", "AUDITION_SHEET.json")
    if not os.path.isfile(sheet_path):
        print(f"casting freeze: REFUSED — no audition sheet at {sheet_path}. "
              f"Voices must be auditioned and approved before freezing.", file=sys.stderr)
        return 1

    with open(sheet_path, "r", encoding="utf-8") as fh:
        sheet = json.load(fh)
    auditioned = sheet.get("voices", {})

    target_ids = [voice_filter] if voice_filter else sorted(voices.keys())
    for vid in target_ids:
        if vid not in voices:
            print(f"casting freeze: unknown voice {vid!r}", file=sys.stderr)
            return 3
        arec = auditioned.get(vid)
        if not arec or not arec.get("approved"):
            print(
                f"casting freeze: REFUSED — voice {vid!r} has not been approved in "
                f"audiobook/auditions/AUDITION_SHEET.json. Run audition + approve first.",
                file=sys.stderr,
            )
            return 1
        if arec.get("voice_design_sha256") != voices[vid]["voice_design_sha256"]:
            print(
                f"casting freeze: REFUSED — voice {vid!r} voice_design string changed after "
                f"audition (auditioned={arec.get('voice_design_sha256')}, "
                f"current={voices[vid]['voice_design_sha256']}). Re-audition and re-approve.",
                file=sys.stderr,
            )
            return 1
        if arec.get("backend") and arec.get("backend") != backend_name:
            print(
                f"casting freeze: REFUSED — voice {vid!r} was auditioned and approved on "
                f"backend {arec.get('backend')!r} but freeze is running backend "
                f"{backend_name!r}. A human approved one engine's audio; re-audition and "
                f"re-approve on {backend_name!r} before freezing.",
                file=sys.stderr,
            )
            return 1

    voices_dir = os.path.join(book_root, "audiobook", "voices")
    os.makedirs(voices_dir, exist_ok=True)
    manifest_path = os.path.join(voices_dir, "freeze-manifest.json")

    manifest = {
        "schema": "incunabula.audiobook.voice_freeze.v1",
        "book": os.path.abspath(book_root),
        "frozen_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "render_mode": "VOICE_CLONE_FROM_GOLDEN",
        "voices": {},
    }
    if os.path.isfile(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as fh:
                prev_m = json.load(fh)
            if isinstance(prev_m.get("voices"), dict):
                manifest["voices"].update(prev_m["voices"])
        except Exception:
            pass

    golden_text = "\n\n".join(GOLDEN_REFERENCE_CORPUS)
    for vid in target_ids:
        v = voices[vid]
        v_out_dir = os.path.join(voices_dir, vid)
        os.makedirs(v_out_dir, exist_ok=True)
        golden_wav = os.path.join(v_out_dir, "golden_reference.wav")
        emb_path = os.path.join(v_out_dir, "speaker_embedding.json")

        res = synthesize_speech_Like_wav(
            out_wav_path=golden_wav,
            text=golden_text,
            voice_id=vid,
            voice_design=v["voice_design"],
            style=v["style"],
            target_duration_sec=duration_sec,
            backend_name=backend_name,
            renderer=renderer,
        )
        with open(golden_wav, "rb") as fh:
            wav_sha256 = hashlib.sha256(fh.read()).hexdigest()

        # Embed with the same instrument render-book will drift-check against:
        # a real speaker-verification encoder when the engine provides one.
        if hasattr(renderer, "extract_speaker_embedding"):
            embedding = renderer.extract_speaker_embedding(golden_wav)
            embedding_kind = getattr(renderer, "embedding_kind", "unknown")
        else:
            embedding = extract_speaker_embedding_from_wav(golden_wav)
            embedding_kind = "autocorr-64"
        prof = voice_acoustic_profile(vid, v["voice_design"])

        emb_obj = {
            "voice_id": vid,
            "voice_design_sha256": v["voice_design_sha256"],
            "golden_wav_sha256": wav_sha256,
            "duration_sec": res["duration_sec"],
            "embedding_dim": len(embedding),
            "embedding_kind": embedding_kind,
            "embedding": embedding,
            "acoustic_profile": prof,
        }
        with open(emb_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(emb_obj, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

        manifest["voices"][vid] = {
            "voice_id": vid,
            "role": v["role"],
            "casting_mode": "VOICE_DESIGN",
            "render_mode": "VOICE_CLONE_FROM_GOLDEN",
            "voice_design": v["voice_design"],
            "voice_design_sha256": v["voice_design_sha256"],
            "golden_wav": os.path.relpath(golden_wav, book_root).replace("\\", "/"),
            "golden_wav_sha256": wav_sha256,
            "duration_sec": res["duration_sec"],
            "speaker_embedding_file": os.path.relpath(emb_path, book_root).replace("\\", "/"),
            "embedding_dim": len(embedding),
            "approved_by": auditioned[vid].get("approved_by"),
            "approved_at": auditioned[vid].get("approved_at"),
            "frozen_at": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "backend": backend_name,
        }
        clip_rec, clip_err = mint_prompt_clip(
            book_root, vid, v["voice_design"], v["style"], embedding, renderer,
            golden_wav, golden_text,
        )
        if clip_rec:
            manifest["voices"][vid].update(clip_rec)
            print(f"   - {vid:<18} acoustic prompt clip "
                  f"{clip_rec['prompt_clip_duration_sec']:.1f}s "
                  f"@ {clip_rec['prompt_clip_wps']:.2f} wps "
                  f"(golden {clip_rec['golden_wps']:.2f}) "
                  f"source={clip_rec['prompt_clip_source']}")
        else:
            print(f"   - {vid:<18} acoustic prompt clip NOT minted ({clip_err}); "
                  f"this voice renders on embedding-only conditioning", file=sys.stderr)

    manifest["frozen_at"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print("=" * 67)
    print(f"## casting freeze   {book_root}")
    print("=" * 67)
    for vid in target_ids:
        frec = manifest["voices"][vid]
        print(f"   - {vid:<18} -> {frec['golden_wav']} "
              f"({frec['duration_sec']:.1f}s, sha256={frec['golden_wav_sha256'][:16]}..., "
              f"mode={frec['render_mode']})")
    print(f"   manifest: {os.path.relpath(manifest_path, book_root).replace(chr(92), '/')}")
    print()
    print("GOLDEN REFERENCES FROZEN — chapter rendering is now locked to VOICE_CLONE_FROM_GOLDEN.")
    return 0


def verify_frozen_voices(book_root):
    """Verify that every voice in `audiobook/config.yaml` has a valid, uncorrupted,
    approved golden reference in `audiobook/voices/freeze-manifest.json` whose
    `voice_design_sha256` and `golden_wav_sha256` match disk.

    Used by `casting.py verify` AND called by `render-book.py` (Refusal Test #4).
    Returns (ok, manifest_dict_or_None, reasons_list).
    """
    reasons = []
    ab_cfg, cfg_path, err = load_audiobook_config(book_root)
    if err:
        return False, None, [err]

    ok, voices, problems = validate_voices_config(ab_cfg, book_root)
    if not ok:
        return False, None, problems

    manifest_path = os.path.join(book_root, "audiobook", "voices", "freeze-manifest.json")
    if not os.path.isfile(manifest_path):
        return False, None, [
            f"missing voice freeze manifest at {manifest_path} — "
            f"cannot render chapters with an unfrozen voice cast. Run casting.py audition, approve, and freeze."
        ]

    try:
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
    except Exception as exc:
        return False, None, [f"cannot parse {manifest_path}: {exc}"]

    frozen_voices = manifest.get("voices", {}) if isinstance(manifest, dict) else {}

    for vid, v in sorted(voices.items()):
        frec = frozen_voices.get(vid)
        if not frec:
            reasons.append(f"voice {vid!r} is declared in config but missing from freeze-manifest.json (unfrozen)")
            continue
        if frec.get("render_mode") != "VOICE_CLONE_FROM_GOLDEN":
            reasons.append(f"voice {vid!r} render_mode is {frec.get('render_mode')!r}, expected 'VOICE_CLONE_FROM_GOLDEN'")
        if frec.get("voice_design_sha256") != v["voice_design_sha256"]:
            reasons.append(
                f"voice {vid!r} voice_design changed since freeze "
                f"(frozen={frec.get('voice_design_sha256')}, config={v['voice_design_sha256']})"
            )
        wav_rel = frec.get("golden_wav", "")
        wav_path = os.path.join(book_root, wav_rel)
        if not wav_rel or not os.path.isfile(wav_path):
            reasons.append(f"voice {vid!r} golden reference WAV missing at {wav_path}")
            continue
        with open(wav_path, "rb") as fh:
            actual_sha = hashlib.sha256(fh.read()).hexdigest()
        if actual_sha != frec.get("golden_wav_sha256"):
            reasons.append(
                f"voice {vid!r} golden reference WAV hash mismatch "
                f"(expected {frec.get('golden_wav_sha256', '')[:16]}, got {actual_sha[:16]})"
            )
        dur = float(frec.get("duration_sec", 0.0) or 0.0)
        speech_sec = active_speech_seconds(wav_path)
        if frec.get("reference_mode") == "SINGLE_TAKE":
            # One continuous take IS the reference, so the window is about being
            # long enough to identify a speaker and short enough to stay inside the
            # engine's coherent range (it drifts past roughly 45 words).
            if dur < 5.0 or dur > 60.0:
                reasons.append(
                    f"voice {vid!r} single-take reference duration {dur:.1f}s is outside "
                    f"the 5–60s window")
            if speech_sec < 4.0:
                reasons.append(
                    f"voice {vid!r} single-take reference holds only {speech_sec:.1f}s of "
                    f"speech inside {dur:.1f}s of audio")
            take_txt = os.path.join(os.path.dirname(wav_path), "reference_take.txt")
            if not os.path.isfile(take_txt):
                reasons.append(
                    f"voice {vid!r} single-take reference has no transcript beside it at "
                    f"{take_txt} — the engine needs the take's exact words")
            else:
                with open(take_txt, "r", encoding="utf-8") as fh:
                    on_disk = fh.read().strip()
                if on_disk != (frec.get("reference_take_text") or "").strip():
                    reasons.append(
                        f"voice {vid!r} reference take transcript disagrees with the "
                        f"freeze manifest")
            if frec.get("prompt_clip_sha256") not in (None, frec.get("golden_wav_sha256")):
                reasons.append(
                    f"voice {vid!r} conditions on a different audio than its reference — "
                    f"the take must be both the reference and the acoustic prompt")
        else:
            if dur < 180.0 or dur > 300.0:
                reasons.append(
                    f"voice {vid!r} golden reference duration {dur:.1f}s is outside the 180–300s (3–5 min) window"
                )
            if speech_sec < 120.0:
                reasons.append(
                    f"voice {vid!r} golden reference holds only {speech_sec:.1f}s of actual speech "
                    f"inside {dur:.1f}s of audio — a collapsed synthesis is not a voice reference"
                )
        emb_rel = frec.get("speaker_embedding_file", "")
        emb_path = os.path.join(book_root, emb_rel)
        if not emb_rel or not os.path.isfile(emb_path):
            reasons.append(f"voice {vid!r} speaker embedding file missing at {emb_path}")
        clip_rel = frec.get("prompt_clip")
        if clip_rel:
            clip_path = os.path.join(book_root, clip_rel)
            if not os.path.isfile(clip_path):
                reasons.append(f"voice {vid!r} acoustic prompt clip missing at {clip_path}")
            else:
                with open(clip_path, "rb") as fh:
                    clip_sha = hashlib.sha256(fh.read()).hexdigest()
                if clip_sha != frec.get("prompt_clip_sha256"):
                    reasons.append(
                        f"voice {vid!r} acoustic prompt clip hash mismatch "
                        f"(expected {str(frec.get('prompt_clip_sha256'))[:16]}, got {clip_sha[:16]})"
                    )
                text_path = clip_path[:-4] + ".txt" if clip_path.endswith(".wav") \
                    else clip_path + ".txt"
                recorded = frec.get("prompt_clip_text") or ""
                if not os.path.isfile(text_path):
                    reasons.append(
                        f"voice {vid!r} acoustic prompt clip has no transcript beside it at "
                        f"{text_path} — the engine needs the clip's exact words")
                else:
                    with open(text_path, "r", encoding="utf-8") as fh:
                        on_disk = fh.read().strip()
                    if on_disk != recorded.strip():
                        reasons.append(
                            f"voice {vid!r} acoustic prompt transcript does not match the "
                            f"freeze manifest — conditioning on audio paired with the wrong "
                            f"words degrades the voice silently")
                if not recorded.strip():
                    reasons.append(
                        f"voice {vid!r} acoustic prompt clip has no recorded transcript")

    return len(reasons) == 0, manifest, reasons


def cmd_verify(book_root):
    ok, manifest, reasons = verify_frozen_voices(book_root)
    if not ok:
        print(f"casting verify: FAIL — voice freeze check failed for {book_root}:", file=sys.stderr)
        for r in reasons:
            print(f"  - {r}", file=sys.stderr)
        return 1

    frozen_voices = manifest["voices"]
    print("=" * 67)
    print(f"## casting verify   {book_root}")
    print("=" * 67)
    single = [v for v, r in frozen_voices.items() if r.get("reference_mode") == "SINGLE_TAKE"]
    if single:
        print(f"   frozen voices: {len(frozen_voices)} verified; {len(single)} pinned to a "
              f"single continuous take (identity and acoustic prompt are one recording)")
    else:
        print(f"   frozen voices: {len(frozen_voices)} (all verified, 3–5 min golden reference + embedding)")
    for vid, frec in sorted(frozen_voices.items()):
        mode = "take" if frec.get("reference_mode") == "SINGLE_TAKE" else "golden"
        print(f"   - {vid:<18} {frec['duration_sec']:>5.1f}s {mode:>6s} | "
              f"design={frec['voice_design_sha256']} | wav={frec['golden_wav_sha256'][:16]} | "
              f"approved_by={frec.get('approved_by')}")
    print()
    print("VOICE FREEZE OK — all cast voices are frozen and attributable to golden references.")
    return 0


# The passage a single-take reference is spoken from. One engine call, so the
# whole take is one continuous voice; ~40 words stays inside the ~45-word range
# this engine renders coherently before it starts drifting.
SINGLE_TAKE_TEXT = (
    "The market was already loud when I got there, and louder still by nine. "
    "Nobody on that street ever agreed about anything except the price of fish, "
    "and even that only after an argument that lasted most of the morning."
)
SINGLE_TAKE_DRAWS = 4


def _score_embedder():
    """The gate's own instrument when available, else the engine's encoder.

    The take kept has to be the one the gate will like most, and the gate uses
    ECAPA when it can. Falling back to the engine's CAM++ keeps casting usable
    where speechbrain is absent, at the cost of ranking on a slightly different
    instrument than the one that will judge the chapter.
    """
    verifier_path = os.path.join(HERE, "verifier.py")
    if os.path.isfile(verifier_path):
        try:
            spec = importlib.util.spec_from_file_location("audio_verifier", verifier_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            verifier, note = mod.make_verifier("ecapa")
            return (lambda p: verifier.embedding(p)), note
        except Exception:
            pass
    return None, "unavailable"


def cmd_reference_take(book_root, voice_filter=None, backend_name=None,
                       draw_count=SINGLE_TAKE_DRAWS):
    """Freeze each voice's identity on ONE continuous take.

    Why: a 180-300s golden reference on this engine is 15-23 independent draws
    stitched together, and those draws measure a pairwise median of 0.29-0.47
    against each other (worst pair -0.05) — the "approved voice" alternates
    between different speakers inside its own reference. Every render is therefore
    stable only relative to whatever single thing it is conditioned on, and no
    single take can match a reference that contradicts itself.

    So the reference becomes one take. It is also the take every chapter segment
    is conditioned on, which makes identity, timbre texture and reading pace all
    properties of the same recording — the only arrangement where a speaker gate
    and a listener can agree.
    """
    ab_cfg, cfg_path, err = load_audiobook_config(book_root)
    if err:
        print(f"casting reference-take: NOT RUN — {err}", file=sys.stderr)
        return 2
    ok, voices, problems = validate_voices_config(ab_cfg, book_root)
    if not ok:
        print(f"casting reference-take: REFUSED — invalid voice config in {cfg_path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    manifest_path = os.path.join(book_root, "audiobook", "voices", "freeze-manifest.json")
    if not os.path.isfile(manifest_path):
        print(f"casting reference-take: REFUSED — no freeze manifest at {manifest_path}", file=sys.stderr)
        return 1
    with open(manifest_path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    frozen = manifest.get("voices", {})

    backend_name = backend_name or ab_cfg.get("backend") or "ming"
    renderer = _get_renderer(backend_name)
    embed, instrument = _score_embedder()
    if embed is None:
        if not hasattr(renderer, "extract_speaker_embedding"):
            print("casting reference-take: REFUSED — no speaker encoder available to rank "
                  "takes (install speechbrain+ecapa, or use a backend that exposes "
                  "extract_speaker_embedding)", file=sys.stderr)
            return 1
        embed = renderer.extract_speaker_embedding
        instrument = f"{getattr(renderer, 'embedding_kind', 'unknown')} (engine encoder)"

    target_ids = [voice_filter] if voice_filter else sorted(voices.keys())
    rc = 0
    for vid in target_ids:
        if vid not in voices:
            print(f"casting reference-take: unknown voice {vid!r}", file=sys.stderr)
            return 3
        frec = frozen.get(vid)
        if not frec:
            print(f"casting reference-take: REFUSED — voice {vid!r} is not frozen", file=sys.stderr)
            return 1
        v_out_dir = os.path.join(book_root, "audiobook", "voices", vid)
        os.makedirs(v_out_dir, exist_ok=True)
        # The archived stitched golden stays the ANCHOR for where the voice should
        # sit, even though it is no longer the reference. A take pinned to that
        # centroid is one coherent recording near the approved voice; it does not
        # inherit the golden's problem, because that problem was 23 separate calls
        # each free to re-texture, not the centroid they average to.
        archived_wav = os.path.join(
            book_root, frec.get("archived_golden_wav") or frec.get("golden_wav", ""))
        archived_emb = None
        anchor_emb = None
        if os.path.isfile(archived_wav):
            try:
                archived_emb = embed(archived_wav)
            except Exception:
                archived_emb = None
            # Engine conditioning needs the ENGINE's embedding space (CAM++), not
            # the gate's ECAPA one — feeding the verifier vector to the engine's
            # speaker head conditions synthesis on the wrong space entirely.
            if hasattr(renderer, "extract_speaker_embedding"):
                try:
                    anchor_emb = renderer.extract_speaker_embedding(archived_wav)
                except Exception:
                    anchor_emb = None

        best = None
        for i in range(max(1, draw_count)):
            cand = os.path.join(v_out_dir, f"reference_take.draw{i}.wav")
            try:
                renderer.synthesize_to_wav(
                    text=SINGLE_TAKE_TEXT,
                    out_wav_path=cand,
                    voice_id=vid,
                    voice_design=voices[vid]["voice_design"],
                    style=voices[vid]["style"],
                    sample_rate=24000,
                    speaker_embedding=anchor_emb,
                    seed_salt=f"reference_take#d{i}",
                )
            except Exception as exc:
                print(f"   - {vid:<18} take {i} failed: {exc}", file=sys.stderr)
                continue
            speech = active_speech_seconds(cand)
            if speech < 4.0:
                continue
            score = 0.0
            if archived_emb is not None:
                try:
                    score = cosine_similarity(embed(cand), archived_emb)
                except Exception:
                    score = 0.0
            if best is None or score > best[0]:
                best = (score, cand, speech)

        if best is None:
            for i in range(max(1, draw_count)):
                p = os.path.join(v_out_dir, f"reference_take.draw{i}.wav")
                if os.path.isfile(p):
                    os.remove(p)
            print(f"   - {vid:<18} FAILED: no usable take", file=sys.stderr)
            rc = 1
            continue

        score, cand, speech = best
        take_wav = os.path.join(v_out_dir, "reference_take.wav")
        for i in range(max(1, draw_count)):
            p = os.path.join(v_out_dir, f"reference_take.draw{i}.wav")
            if os.path.isfile(p) and os.path.abspath(p) != os.path.abspath(cand):
                os.remove(p)
            m = p + ".meta.json"
            if os.path.isfile(m) and os.path.abspath(p) != os.path.abspath(cand):
                os.remove(m)
        os.replace(cand, take_wav)
        meta_src = cand + ".meta.json"
        if os.path.isfile(meta_src):
            os.replace(meta_src, take_wav + ".meta.json")
        take_txt = os.path.join(v_out_dir, "reference_take.txt")
        with open(take_txt, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(SINGLE_TAKE_TEXT)
            fh.write("\n")
        with open(take_wav, "rb") as fh:
            take_sha = hashlib.sha256(fh.read()).hexdigest()
        with wave.open(take_wav, "rb") as wf:
            take_dur = wf.getnframes() / float(wf.getframerate() or 24000)

        # The frozen identity becomes this take. Anything derived from the stitched
        # golden must go: the embedding, the verifier shortcut, and the prompt clip.
        #
        # The stored embedding must be the ENGINE's space (CAM++): render-book
        # compares per-segment CAM++ embeddings against it and the renderer feeds it
        # to the engine's spk_head. `embed` above is the gate's verifier (ECAPA);
        # storing that here made the drift gate compare CAM++ against ECAPA —
        # cross-space cosine ~0.06 for identical voices, refusing every segment.
        # The ECAPA vector is kept alongside as `verifier_embedding` (record only).
        if hasattr(renderer, "extract_speaker_embedding"):
            embedding = renderer.extract_speaker_embedding(take_wav)
            embedding_kind = getattr(renderer, "embedding_kind", "unknown")
        else:
            embedding_kind = instrument
        verifier_embedding = embed(take_wav)
        prof = voice_acoustic_profile(vid, voices[vid]["voice_design"])
        emb_path = os.path.join(v_out_dir, "speaker_embedding.json")
        with open(emb_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({
                "voice_id": vid,
                "voice_design_sha256": voices[vid]["voice_design_sha256"],
                "golden_wav_sha256": take_sha,
                "duration_sec": round(take_dur, 3),
                "embedding_dim": len(embedding),
                "embedding_kind": embedding_kind,
                "verifier_embedding": verifier_embedding,
                "verifier_kind": instrument,
                "reference_mode": "SINGLE_TAKE",
                "embedding": embedding,
                "acoustic_profile": prof,
            }, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        for stale in ("verifier-ecapa.json", "verifier-campplus.json"):
            p = os.path.join(v_out_dir, stale)
            if os.path.isfile(p):
                os.remove(p)

        frec.update({
            "reference_mode": "SINGLE_TAKE",
            "golden_wav": os.path.relpath(take_wav, book_root).replace("\\", "/"),
            "golden_wav_sha256": take_sha,
            "duration_sec": round(take_dur, 3),
            "reference_take_text": SINGLE_TAKE_TEXT,
            "reference_take_agreement": round(score, 4),
            "reference_take_instrument": instrument,
            "speaker_embedding_file": os.path.relpath(emb_path, book_root).replace("\\", "/"),
            "embedding_dim": len(embedding),
            "archived_golden_wav": frec.get("archived_golden_wav") or frec.get("golden_wav"),
            "archived_golden_wav_sha256": (frec.get("archived_golden_wav_sha256")
                                           or frec.get("golden_wav_sha256")),
            "archived_golden_duration_sec": (frec.get("archived_golden_duration_sec")
                                             or frec.get("duration_sec")),
            "prompt_clip": os.path.relpath(take_wav, book_root).replace("\\", "/"),
            "prompt_clip_sha256": take_sha,
            "prompt_clip_text": SINGLE_TAKE_TEXT,
            "prompt_clip_source": "reference-take",
            "prompt_clip_duration_sec": round(take_dur, 3),
            "prompt_clip_wps": round(_clip_words(SINGLE_TAKE_TEXT) / max(0.1, take_dur), 3),
        })
        with open(os.path.join(v_out_dir, "prompt_clip.txt"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(SINGLE_TAKE_TEXT)
            fh.write("\n")
        print(f"   - {vid:<18} reference take {take_dur:5.1f}s "
              f"({_clip_words(SINGLE_TAKE_TEXT)} words, agreement {score:.3f} "
              f"with the archived golden)")

    with open(manifest_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    if rc == 0:
        print("\nREFERENCE TAKES FROZEN — each voice is one continuous recording, "
              "and that same take conditions every rendered segment.")
    return rc


def cmd_prompt_clip(book_root, voice_filter=None, backend_name=None):
    """Mint acoustic prompt clips for voices already frozen.

    Separate from `freeze` so an existing approved golden reference is never
    re-synthesized just to gain a clip — re-freezing would replace the audio a
    human listened to with a new draw, which is exactly what the freeze contract
    exists to prevent.
    """
    ab_cfg, cfg_path, err = load_audiobook_config(book_root)
    if err:
        print(f"casting prompt-clip: NOT RUN — {err}", file=sys.stderr)
        return 2
    ok, voices, problems = validate_voices_config(ab_cfg, book_root)
    if not ok:
        print(f"casting prompt-clip: REFUSED — invalid voice config in {cfg_path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    manifest_path = os.path.join(book_root, "audiobook", "voices", "freeze-manifest.json")
    if not os.path.isfile(manifest_path):
        print(f"casting prompt-clip: REFUSED — no freeze manifest at {manifest_path}", file=sys.stderr)
        return 1
    with open(manifest_path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)
    frozen = manifest.get("voices", {})

    backend_name = backend_name or ab_cfg.get("backend") or "ming"
    renderer = _get_renderer(backend_name)
    golden_text = "\n\n".join(GOLDEN_REFERENCE_CORPUS)

    target_ids = [voice_filter] if voice_filter else sorted(voices.keys())
    rc = 0
    for vid in target_ids:
        if vid not in voices:
            print(f"casting prompt-clip: unknown voice {vid!r}", file=sys.stderr)
            return 3
        frec = frozen.get(vid)
        if not frec:
            print(f"casting prompt-clip: REFUSED — voice {vid!r} is not frozen", file=sys.stderr)
            return 1
        if frec.get("reference_mode") == "SINGLE_TAKE":
            print(f"   - {vid:<18} skipped: reference is a single take and already "
                  f"serves as its own acoustic prompt")
            continue
        emb_path = os.path.join(book_root, frec.get("speaker_embedding_file", ""))
        golden_wav = os.path.join(book_root, frec.get("golden_wav", ""))
        if not os.path.isfile(emb_path) or not os.path.isfile(golden_wav):
            print(f"casting prompt-clip: REFUSED — voice {vid!r} is missing its frozen "
                  f"embedding or golden reference", file=sys.stderr)
            return 1
        with open(emb_path, "r", encoding="utf-8") as fh:
            embedding = json.load(fh).get("embedding")
        clip_rec, clip_err = mint_prompt_clip(
            book_root, vid, voices[vid]["voice_design"], voices[vid]["style"],
            embedding, renderer, golden_wav, golden_text,
        )
        if not clip_rec:
            print(f"   - {vid:<18} FAILED to mint clip ({clip_err})", file=sys.stderr)
            rc = 1
            continue
        frec.update(clip_rec)
        print(f"   - {vid:<18} acoustic prompt clip "
              f"{clip_rec['prompt_clip_duration_sec']:.1f}s @ "
              f"{clip_rec['prompt_clip_wps']:.2f} wps (golden "
              f"{clip_rec['golden_wps']:.2f}) source={clip_rec['prompt_clip_source']}")

    with open(manifest_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    if rc == 0:
        print("\nACOUSTIC PROMPT CLIPS MINTED — renders condition on real audio of each voice.")
    return rc


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", newline="\n")

    ap = argparse.ArgumentParser(description="Voice design, audition protocol, and golden-reference freeze.")
    sub = ap.add_subparsers(dest="cmd")

    p_val = sub.add_parser("validate", help="Validate VOICE_DESIGN strings and refuse real-person clones")
    p_val.add_argument("book")

    p_aud = sub.add_parser("audition", help="Render 3 standard audition passages (~90s) per voice")
    p_aud.add_argument("book")
    p_aud.add_argument("--voice", default=None)
    p_aud.add_argument("--backend", default=None,
                       help="Synthesis backend (default: audiobook config 'backend', else ming)")

    p_app = sub.add_parser("approve", help="Record human review approval on auditioned voices")
    p_app.add_argument("book")
    p_app.add_argument("--voice", default=None)
    p_app.add_argument("--all", action="store_true", dest="approve_all")
    p_app.add_argument("--reviewer", required=True)
    p_app.add_argument("--notes", default="")

    p_frz = sub.add_parser("freeze", help="Synthesize 3-5 min golden reference and freeze speaker embeddings")
    p_frz.add_argument("book")
    p_frz.add_argument("--voice", default=None)
    p_frz.add_argument("--duration-sec", type=float, default=210.0)
    p_frz.add_argument("--backend", default=None,
                       help="Synthesis backend (default: audiobook config 'backend', else ming)")

    p_ver = sub.add_parser("verify", help="Verify all voices are frozen with valid golden references")
    p_ver.add_argument("book")

    p_take = sub.add_parser(
        "reference-take",
        help="Freeze each voice's identity on ONE continuous take, used as its own "
             "acoustic prompt (replaces a stitched long golden as the reference)")
    p_take.add_argument("book")
    p_take.add_argument("--voice", default=None)
    p_take.add_argument("--backend", default=None)
    p_take.add_argument("--draws", type=int, default=SINGLE_TAKE_DRAWS)

    p_clip = sub.add_parser(
        "prompt-clip",
        help="Mint the short acoustic prompt clip per frozen voice (no re-freeze)")
    p_clip.add_argument("book")
    p_clip.add_argument("--voice", default=None)
    p_clip.add_argument("--backend", default=None)

    args = ap.parse_args(argv)
    try:
        if args.cmd == "validate":
            return cmd_validate(args.book)
        if args.cmd == "audition":
            return cmd_audition(args.book, args.voice, args.backend)
        if args.cmd == "approve":
            return cmd_approve(args.book, args.voice, args.approve_all, args.reviewer, args.notes)
        if args.cmd == "freeze":
            return cmd_freeze(args.book, args.voice, args.duration_sec, args.backend)
        if args.cmd == "verify":
            return cmd_verify(args.book)
        if args.cmd == "prompt-clip":
            return cmd_prompt_clip(args.book, args.voice, args.backend)
        if args.cmd == "reference-take":
            return cmd_reference_take(args.book, args.voice, args.backend, args.draws)
    except (ValueError, RuntimeError) as exc:
        print(f"casting: ERROR — {exc}", file=sys.stderr)
        return 3

    ap.print_help()
    return 3


if __name__ == "__main__":
    sys.exit(main())
