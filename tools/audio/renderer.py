#!/usr/bin/env python3
"""renderer.py — Unified synthesis renderer for the Incunabula audiobook stage (Cluster E).

WHY THIS EXISTS
  Every acoustic artifact of an audiobook — audition passages, golden references,
  and chapter audio — must come from ONE synthesis engine behind ONE contract.
  If freezing and rendering can pick different engines, the golden reference stops
  being a reference: the voice a reviewer approved is not the voice a listener hears,
  and the speaker-embedding drift gate compares audio that was never meant to match.

  This module is the single entry point for speech synthesis:
    - `create_renderer(backend_name)` selects a backend from the registry and returns
      a renderer object exposing exactly one required method:

        renderer.synthesize_to_wav(
            text, out_wav_path, voice_id, voice_design,
            style=None, target_duration_sec=None, sample_rate=24000,
        ) -> {"wav_path": ..., "duration_sec": ..., "sample_rate": ...}

    - `ming3` — the production engine: Ant inclusionAI's Ming-3.0-tts (MIT,
      https://github.com/inclusionAI/Ming-3.0-tts). The contract maps onto it
      natively:
        * `voice_design` -> task FREEFORM's instruction: Ming-3.0-tts designs a voice
          from a written description with NO reference audio, which keeps the
          no-real-person-clone rule of `casting.py` literal — nothing to clone from.
        * `style` (speed/pitch/volume/emotion) -> folded into the same instruction as
          delivery phrases, the engine's free-form control surface.
        * paralinguistic tags (`[sigh]`, `[breath]`, `[laughter]`) -> delivery phrases
          in the instruction (the engine's inline-tag mode lives on its reference-audio
          task, which this pipeline refuses to touch).
        * output -> 16-bit mono WAV at the requested `sample_rate`; the engine's native
          44.1 kHz output is linearly resampled (stdlib) to the contract rate so every
          artifact — golden reference included — shares one sample rate, which the
          speaker-embedding drift gate requires (lags are sample-indexed).
      Engine acquisition (loud, never silent): the official `ming_tts` package must be
      importable and a checkpoint available (`MING3_MODEL_PATH`, default
      `inclusionAI/Ming-3.0-tts-0.5b`). If not, synthesis raises with install steps —
      a configured engine is NEVER quietly replaced by another voice.
    - `ming` (aliases `builtin`, `deterministic`, `reference`) — the deterministic
      formant-harmonic acoustic synthesizer whose math lives in
      `casting.py::synthesize_fallback_wav` so Cluster B keeps working standalone when
      this file is absent. Deterministic is not a limitation here, it is the contract:
      identical inputs must yield byte-identical WAVs, or `casting.py verify` would
      report hash drift on a golden reference nobody touched. It is also the offline
      test double for the whole pipeline.

  This file never reads or writes book state. Casting, audition, freeze, and render
  all call it; it knows nothing about any of them.

USAGE
  python tools/audio/renderer.py list
  python tools/audio/renderer.py synth --text "The tide turned at six." \\
      --voice-id NARRATOR --voice-design "a warm measured alto narrator" --out out.wav
  python tools/audio/renderer.py synth ... --backend ming3   # production engine

  (Library use: casting.py and render-book.py load this file via importlib and call
  `create_renderer(backend_name)`.)

EXIT CODES
  0  OK — backend listed or WAV synthesized
  1  REFUSED / FAIL — synthesis produced no WAV
  2  NOT RUN — nothing to do
  3  ERROR — unknown backend, engine unavailable, or invalid arguments
"""

import argparse
import array
import hashlib
import importlib.util
import json
import os
import re
import struct
import sys
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)

# Registry: canonical backend name -> accepted aliases.
BACKEND_REGISTRY = {
    "ming3": ("ming3", "ming-3", "ming-3.0", "ming-3.0-tts"),
    "ming": ("ming", "builtin", "deterministic", "reference"),
}

_BACKEND_DESCRIPTIONS = {
    "ming3": "Ant Ming-3.0-tts production engine (voice design from text, free-form "
             "delivery control; requires the official ming_tts package + checkpoint)",
    "ming": "deterministic formant-harmonic acoustic synthesizer (stdlib-only, "
            "byte-reproducible offline reference engine)",
}

MING3_DEFAULT_MODEL = "inclusionAI/Ming-3.0-tts-0.5b"

MING3_INSTALL_HELP = (
    "ming3 backend unavailable: the official 'ming_tts' package is not importable.\n"
    "Install the Ming-3.0-tts release (MIT, Ant inclusionAI):\n"
    "  git clone https://github.com/inclusionAI/Ming-3.0-tts\n"
    "  cd Ming-3.0-tts && pip install -r requirements.txt\n"
    "  pip install \"huggingface_hub[cli]\"\n"
    "  hf download inclusionAI/Ming-3.0-tts-0.5b --local-dir Ming-3.0-tts-0.5b\n"
    "Then set MING3_MODEL_PATH to the checkpoint directory "
    f"(default: {MING3_DEFAULT_MODEL})."
)

# Paralinguistic tags this pipeline emits (build-script rationing) mapped to delivery
# phrases the FREEFORM instruction can express. The engine's inline-tag vocabulary
# ([Sigh], [Breathing], [Laughter], ...) belongs to its reference-audio task modes.
PARALINGUISTIC_PHRASES = {
    "sigh": "with a sigh",
    "sighing": "with a sigh",
    "breath": "after a breath",
    "breathing": "after a breath",
    "laughter": "with a laugh",
    "laugh": "with a laugh",
    "chuckle": "with a chuckle",
    "cough": "with a cough",
}

TAG_RE = re.compile(r"\[([A-Za-z][A-Za-z -]*)\]")

EMOTION_PHRASES = {
    "whisper": "in a hushed whisper",
    "soft": "softly",
    "weary": "with weariness",
    "tense": "with tension",
    "breathless": "breathlessly",
    "urgent": "urgently",
    "sharp": "sharply",
    "low": "in a low voice",
    "wry": "with wry humour",
    "grief": "with grief",
    "strained": "with strained effort",
}


def strip_paralinguistic_tags(text):
    """Remove inline [tag] markers and collapse whitespace. The deterministic engine
    cannot perform tags, so it speaks only their words."""
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", text)).strip()


def split_paralinguistic_tags(text):
    """Return (clean_words, tag_keys) — words without markers plus recognised tag keys."""
    tags = []
    def _repl(m):
        key = m.group(1).strip().lower()
        if key in PARALINGUISTIC_PHRASES:
            tags.append(key)
        return " "
    return re.sub(r"\s+", " ", TAG_RE.sub(_repl, text)).strip(), tags


def delivery_phrases(style):
    """Map the segment style contract {speed, pitch, volume, emotion} to free-form
    delivery phrases. Baseline style (1.0/0.0/0.0/neutral) contributes nothing."""
    phrases = []
    style = style or {}
    emotion = str(style.get("emotion", "neutral") or "neutral").lower()
    if emotion in EMOTION_PHRASES:
        phrases.append(EMOTION_PHRASES[emotion])
    try:
        speed = float(style.get("speed", 1.0) or 1.0)
    except (TypeError, ValueError):
        speed = 1.0
    if speed > 1.03:
        phrases.append("a little faster")
    elif speed < 0.97:
        phrases.append("a little slower")
    try:
        pitch = float(style.get("pitch", 0.0) or 0.0)
    except (TypeError, ValueError):
        pitch = 0.0
    if pitch > 0.01:
        phrases.append("slightly higher in pitch")
    elif pitch < -0.01:
        phrases.append("slightly lower in pitch")
    try:
        volume = float(style.get("volume", 0.0) or 0.0)
    except (TypeError, ValueError):
        volume = 0.0
    if volume > 0.5:
        phrases.append("louder")
    elif volume < -0.5:
        phrases.append("quieter")
    return phrases


def build_ming3_instruction(voice_design, style, tags):
    """One natural-language instruction: the frozen voice identity first (so every
    utterance of a voice is designed from the same sentence), then delivery."""
    instruction = str(voice_design).strip().rstrip(".") + "."
    phrases = delivery_phrases(style)
    phrases += [PARALINGUISTIC_PHRASES[t] for t in tags if t in PARALINGUISTIC_PHRASES]
    phrases = list(dict.fromkeys(phrases))
    if phrases:
        instruction += " Speak " + ", ".join(phrases) + "."
    return instruction


# ---------------------------------------------------------------------------
# WAV plumbing shared by backends (stdlib only)
# ---------------------------------------------------------------------------

def read_wav_mono16(path):
    """Read a WAV as 16-bit mono frames. Raises RuntimeError on formats this
    pipeline cannot concatenate losslessly."""
    try:
        with wave.open(path, "rb") as wf:
            n_ch = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
    except wave.Error as exc:
        raise RuntimeError(
            f"{path}: unsupported WAV container ({exc}) — the ming3 backend handles "
            f"integer PCM WAV only; re-export the engine output as 16-bit PCM"
        )
    if sampwidth != 2:
        raise RuntimeError(
            f"{path}: expected 16-bit PCM, got {sampwidth * 8}-bit — the ming3 backend "
            f"handles 16-bit PCM only"
        )
    if n_ch > 1:
        total = len(frames) // 2
        samples = struct.unpack(f"<{total}h", frames)
        mono = array.array("h", bytes((total // n_ch) * 2))
        for i in range(len(mono)):
            acc = 0
            base = i * n_ch
            for c in range(n_ch):
                acc += samples[base + c]
            mono[i] = acc // n_ch
        frames = mono.tobytes()
    return frames, rate


def resample_pcm16(frames, src_rate, dst_rate):
    """Linear-interpolation resample of 16-bit mono frames. Stdlib-only on purpose;
    artifacts of one book all share one sample rate so this runs once per segment."""
    if src_rate == dst_rate:
        return frames
    n_src = len(frames) // 2
    if n_src < 2:
        return frames
    samples = struct.unpack(f"<{n_src}h", frames)
    n_dst = max(1, int(round(n_src * dst_rate / src_rate)))
    step = (n_src - 1) / max(1, n_dst - 1)
    out = array.array("h", bytes(n_dst * 2))
    for j in range(n_dst):
        pos = j * step
        i0 = int(pos)
        frac = pos - i0
        i1 = i0 + 1 if i0 + 1 < n_src else i0
        out[j] = int(samples[i0] + (samples[i1] - samples[i0]) * frac)
    if sys.byteorder != "little":
        out.byteswap()
    return out.tobytes()


def write_wav_mono16(path, frames, sample_rate):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(frames)


# ---------------------------------------------------------------------------
# Backends
# ---------------------------------------------------------------------------

_casting_module = None


def _load_casting():
    """Load `tools/audio/casting.py` for `synthesize_fallback_wav` (pure function,
    never calls back into this module) and `voice_acoustic_profile`. Cached: the
    acoustic math must be one code path for every artifact."""
    global _casting_module
    if _casting_module is None:
        spec = importlib.util.spec_from_file_location(
            "audio_casting_reference", os.path.join(HERE, "casting.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _casting_module = mod
    return _casting_module


class DeterministicRenderer:
    """The `ming` backend: delegates to casting.py's standalone synthesizer.

    Freeze-time golden references and render-time chapter audio pass through here,
    so both are produced by the same code with the same inputs."""

    backend = "ming"

    def synthesize_to_wav(
        self,
        text,
        out_wav_path,
        voice_id,
        voice_design,
        style=None,
        target_duration_sec=None,
        sample_rate=24000,
    ):
        casting = _load_casting()
        return casting.synthesize_fallback_wav(
            out_wav_path=out_wav_path,
            text=text,
            voice_id=voice_id,
            voice_design=voice_design,
            style=style,
            target_duration_sec=target_duration_sec,
            sample_rate=sample_rate,
        )


class Ming3Renderer:
    """The `ming3` backend: Ant Ming-3.0-tts via its official `ming_tts` package.

    Identity comes from `voice_design` through task FREEFORM (a voice designed from
    text, no reference audio); delivery comes from `style` and paralinguistic tags
    folded into the same instruction. The engine model is loaded once and reused
    for every segment. Engine failures propagate — see MING3_INSTALL_HELP."""

    backend = "ming3"
    _model = None

    def _engine(self):
        if Ming3Renderer._model is None:
            try:
                from ming_tts import MingTTS
            except ImportError as exc:
                raise RuntimeError(MING3_INSTALL_HELP) from exc
            model_path = os.environ.get("MING3_MODEL_PATH", MING3_DEFAULT_MODEL)
            Ming3Renderer._model = MingTTS(model_path)
        return Ming3Renderer._model

    def synthesize_to_wav(
        self,
        text,
        out_wav_path,
        voice_id,
        voice_design,
        style=None,
        target_duration_sec=None,
        sample_rate=24000,
    ):
        model = self._engine()
        words, tags = split_paralinguistic_tags(text)
        if not words:
            raise RuntimeError(f"nothing speakable in segment for voice {voice_id!r}")
        instruction = build_ming3_instruction(voice_design, style, tags)

        out_wav_path = os.path.abspath(out_wav_path)
        os.makedirs(os.path.dirname(out_wav_path), exist_ok=True)
        engine_wav = out_wav_path + ".ming3.wav"
        model.synthesize(
            task="FREEFORM",
            text=words,
            instruction=instruction,
            use_zero_spk_emb=True,
            output_path=engine_wav,
        )
        if not os.path.isfile(engine_wav):
            raise RuntimeError(f"ming3 engine produced no WAV at {engine_wav}")

        frames, engine_rate = read_wav_mono16(engine_wav)
        frames = resample_pcm16(frames, engine_rate, sample_rate)
        try:
            os.remove(engine_wav)
        except OSError:
            pass

        duration_sec = len(frames) / 2 / sample_rate
        if target_duration_sec is not None and duration_sec < float(target_duration_sec):
            # Keep the freeze contract (golden references span 180-300s) without
            # truncating speech: pad the tail with silence, never clip words.
            pad = int((float(target_duration_sec) - duration_sec) * sample_rate) * 2
            frames += b"\x00\x00" * (pad // 2)
            duration_sec = len(frames) / 2 / sample_rate

        write_wav_mono16(out_wav_path, frames, sample_rate)

        meta_path = out_wav_path + ".meta.json"
        with open(meta_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({
                "backend": "ming3",
                "engine_model": os.environ.get("MING3_MODEL_PATH", MING3_DEFAULT_MODEL),
                "voice_id": voice_id,
                "voice_design_sha256": hashlib.sha256(
                    voice_design.encode("utf-8")).hexdigest()[:16],
                "instruction": instruction,
                "paralinguistic_tags": tags,
                "spoken_text": words,
                "duration_sec": round(duration_sec, 3),
                "sample_rate": sample_rate,
                "engine_sample_rate": engine_rate,
            }, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

        return {
            "wav_path": out_wav_path,
            "duration_sec": round(duration_sec, 3),
            "sample_rate": sample_rate,
        }


def resolve_backend_name(backend_name):
    """Map a backend name/alias to its canonical registry name, or None if unknown."""
    want = str(backend_name or "ming").strip().lower()
    for canon, aliases in BACKEND_REGISTRY.items():
        if want == canon or want in aliases:
            return canon
    return None


def available_backends():
    """Sorted list of (canonical_name, description) for every registered backend."""
    return [
        (canon, _BACKEND_DESCRIPTIONS.get(canon, ""))
        for canon in sorted(BACKEND_REGISTRY)
    ]


def create_renderer(backend_name="ming"):
    """Return a renderer object for `backend_name`.

    Raises ValueError on an unknown backend and RuntimeError when a known real
    engine is unavailable — never silently substitutes another voice engine."""
    canon = resolve_backend_name(backend_name)
    if canon is None:
        known = ", ".join(sorted(BACKEND_REGISTRY))
        raise ValueError(f"unknown renderer backend {backend_name!r} (known: {known})")
    if canon == "ming":
        return DeterministicRenderer()
    if canon == "ming3":
        renderer = Ming3Renderer()
        renderer._engine()  # availability check up front: fail before any artifact
        return renderer
    raise ValueError(f"backend {canon!r} is registered but has no implementation")


# ---------------------------------------------------------------------------
# CLI: list / synth (debug entry points; production callers use the library API)
# ---------------------------------------------------------------------------

def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", newline="\n")

    ap = argparse.ArgumentParser(description="Unified synthesis renderer (Cluster E).")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("list", help="List registered synthesis backends")

    p_synth = sub.add_parser("synth", help="Synthesize one WAV through the selected backend")
    p_synth.add_argument("--text", required=True)
    p_synth.add_argument("--voice-id", required=True)
    p_synth.add_argument("--voice-design", required=True)
    p_synth.add_argument("--out", required=True)
    p_synth.add_argument("--backend", default="ming")
    p_synth.add_argument("--duration-sec", type=float, default=None)
    p_synth.add_argument("--sample-rate", type=int, default=24000)

    args = ap.parse_args(argv)

    if args.cmd == "list":
        print("registered synthesis backends:")
        for canon, desc in available_backends():
            print(f"  {canon:<6} {desc}")
        return 0

    if args.cmd == "synth":
        try:
            renderer = create_renderer(args.backend)
            res = renderer.synthesize_to_wav(
                text=args.text,
                out_wav_path=args.out,
                voice_id=args.voice_id,
                voice_design=args.voice_design,
                target_duration_sec=args.duration_sec,
                sample_rate=args.sample_rate,
            )
        except (ValueError, RuntimeError) as exc:
            print(f"renderer: ERROR — {exc}", file=sys.stderr)
            return 3
        if not res or not os.path.isfile(args.out):
            print(f"renderer: FAIL — backend {args.backend!r} produced no WAV at {args.out}",
                  file=sys.stderr)
            return 1
        print(f"renderer: OK — {args.out} ({res['duration_sec']:.2f}s @ {res['sample_rate']} Hz, "
              f"backend={renderer.backend})")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
