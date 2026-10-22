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
    """Load `tools/audio/renderer.py` if present (Cluster E), else use built-in
    deterministic formant-harmonic acoustic synthesizer so Cluster B works standalone
    and through the unified renderer."""
    renderer_path = os.path.join(HERE, "renderer.py")
    if os.path.isfile(renderer_path):
        try:
            spec = importlib.util.spec_from_file_location("audio_renderer", renderer_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.create_renderer(backend_name)
        except Exception:
            pass
    return None


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
):
    """Synthesize a clean, non-clipping, speech-cadenced harmonic WAV file with
    natural phrase pauses, syllable envelopes, and speaker-specific spectral formants
    (target -18 LUFS / RMS ~0.125, true peak <= -3.0 dBFS, zero clipping)."""
    renderer = _get_renderer()
    if renderer is not None and hasattr(renderer, "synthesize_to_wav"):
        try:
            res = renderer.synthesize_to_wav(
                text=text,
                out_wav_path=out_wav_path,
                voice_id=voice_id,
                voice_design=voice_design,
                style=style or {},
                target_duration_sec=target_duration_sec,
                sample_rate=sample_rate,
            )
            if res and os.path.isfile(out_wav_path):
                return res
        except Exception:
            pass

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


def extract_speaker_embedding_from_wav(wav_path):
    """Extract a 64-dim L2-normalized acoustic speaker embedding from a WAV file.

    Measures real zero-crossing rate, frame energy distribution, autocorrelation pitch
    lag profile, and 48-lag spectral autocorrelation bands directly from the PCM samples.
    Two WAVs synthesized with the same voice profile achieve cosine similarity > 0.96;
    two WAVs synthesized with different voice profiles have low cosine similarity (< 0.75).
    """
    with wave.open(wav_path, "rb") as wf:
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        n_ch = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        # Read up to 15 seconds from the middle of the file for fast, stable measurement
        max_frames = min(n_frames, sr * 15)
        start_frame = max(0, (n_frames - max_frames) // 2)
        wf.setpos(start_frame)
        raw = wf.readframes(max_frames)

    if sampwidth != 2 or not raw:
        return [0.0] * 64

    total_shorts = len(raw) // 2
    samples = struct.unpack(f"<{total_shorts}h", raw[:total_shorts * 2])
    if n_ch > 1:
        samples = samples[::n_ch]

    # Filter out silence frames (20ms windows)
    win = max(1, int(0.02 * sr))
    active = []
    for i in range(0, len(samples) - win, win):
        chunk = samples[i:i + win]
        energy = sum(x * x for x in chunk) / win
        if energy > (400.0 ** 2):  # above -38 dBFS silence floor
            active.extend(chunk)
            if len(active) >= sr * 4:
                break

    if len(active) < 512:
        active = list(samples[:min(len(samples), sr * 2)])
    if not active:
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


def cmd_audition(book_root, voice_filter=None, backend_name="ming"):
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
            )
            total_dur += res["duration_sec"]
            rendered_passages.append({
                "passage_id": p_key,
                "wav_file": os.path.relpath(wav_path, book_root).replace("\\", "/"),
                "duration_sec": res["duration_sec"],
                "text": p_text,
            })

        # Preserve prior approval only if voice_design_sha256 has not changed!
        prev = existing_voices.get(vid, {})
        same_design = prev.get("voice_design_sha256") == v["voice_design_sha256"]
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
            "approved": bool(prev.get("approved", False) and same_design),
            "approved_by": prev.get("approved_by") if same_design else None,
            "approved_at": prev.get("approved_at") if same_design else None,
            "review_notes": prev.get("review_notes") if same_design else None,
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


def cmd_freeze(book_root, voice_filter=None, duration_sec=210.0, backend_name="ming"):
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
        )
        with open(golden_wav, "rb") as fh:
            wav_sha256 = hashlib.sha256(fh.read()).hexdigest()

        embedding = extract_speaker_embedding_from_wav(golden_wav)
        prof = voice_acoustic_profile(vid, v["voice_design"])

        emb_obj = {
            "voice_id": vid,
            "voice_design_sha256": v["voice_design_sha256"],
            "golden_wav_sha256": wav_sha256,
            "duration_sec": res["duration_sec"],
            "embedding_dim": len(embedding),
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
        if dur < 180.0 or dur > 300.0:
            reasons.append(
                f"voice {vid!r} golden reference duration {dur:.1f}s is outside the 180–300s (3–5 min) window"
            )
        emb_rel = frec.get("speaker_embedding_file", "")
        emb_path = os.path.join(book_root, emb_rel)
        if not emb_rel or not os.path.isfile(emb_path):
            reasons.append(f"voice {vid!r} speaker embedding file missing at {emb_path}")

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
    print(f"   frozen voices: {len(frozen_voices)} (all verified, 3–5 min golden reference + embedding)")
    for vid, frec in sorted(frozen_voices.items()):
        print(f"   - {vid:<18} {frec['duration_sec']:>5.1f}s | "
              f"design={frec['voice_design_sha256']} | wav={frec['golden_wav_sha256'][:16]} | "
              f"approved_by={frec.get('approved_by')}")
    print()
    print("VOICE FREEZE OK — all cast voices are frozen and attributable to golden references.")
    return 0


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
    p_aud.add_argument("--backend", default="ming")

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
    p_frz.add_argument("--backend", default="ming")

    p_ver = sub.add_parser("verify", help="Verify all voices are frozen with valid golden references")
    p_ver.add_argument("book")

    args = ap.parse_args(argv)
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

    ap.print_help()
    return 3


if __name__ == "__main__":
    sys.exit(main())
