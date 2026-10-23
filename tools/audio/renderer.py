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
            speaker_embedding=None,
        ) -> {"wav_path": ..., "duration_sec": ..., "sample_rate": ...}

      `speaker_embedding` is the frozen golden reference embedding (or None):
      when given, every utterance is conditioned on that identity — the engine
      re-samples its voice per call when left unconditioned, and per-call
      re-design drifts across a book (measured 0.40–0.81 cosine between
      same-design calls). Conditioning is what makes
      `render_mode=VOICE_CLONE_FROM_GOLDEN` true and keeps the speaker-drift
      gate comparing identity to identity.

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
          44.1 kHz waveform is resampled with the engine's own torchaudio and saved as
          PCM_S so every artifact — golden reference included — shares one sample rate,
          which the speaker-embedding drift gate requires (lags are sample-indexed).
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
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile

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
MING3_LOCAL_ROOT = os.path.join(HERE, ".ming3")
MING3_LOCAL_REPO = os.path.join(MING3_LOCAL_ROOT, "Ming-3.0-tts")
MING3_LOCAL_CHECKPOINT = os.path.join(MING3_LOCAL_ROOT, "Ming-3.0-tts-0.5b")

MING3_INSTALL_HELP = (
    "ming3 backend unavailable: the official 'ming_tts' package is not importable.\n"
    "Install the Ming-3.0-tts release (MIT, Ant inclusionAI) — e.g. the local setup:\n"
    "  git clone https://github.com/inclusionAI/Ming-3.0-tts tools/audio/.ming3/Ming-3.0-tts\n"
    "  python -m venv tools/audio/.ming3/venv\n"
    "  tools/audio/.ming3/venv/Scripts/python.exe -m pip install "
    "-r tools/audio/.ming3/Ming-3.0-tts/requirements.txt \"huggingface_hub[cli]\"\n"
    "  tools/audio/.ming3/venv/Scripts/hf.exe download inclusionAI/Ming-3.0-tts-0.5b "
    "--local-dir tools/audio/.ming3/Ming-3.0-tts-0.5b\n"
    "Then run the pipeline with tools/audio/.ming3/venv/Scripts/python.exe, or set "
    "MING3_MODEL_PATH to the checkpoint directory. GPU: needs a CUDA torch build; "
    "on AMD (ROCm, e.g. WSL2 + Ubuntu 24.04) or ZLUDA, set MING3_DEVICE if torch "
    "does not report a device itself."
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
# Backends
# ---------------------------------------------------------------------------

_casting_module = None


def _import_ming_tts():
    """Import the official `ming_tts` package, discovering the local engine checkout
    under `tools/audio/.ming3/Ming-3.0-tts` when no installed copy exists."""
    try:
        from ming_tts import MingTTS
        return MingTTS
    except ImportError:
        pass
    if os.path.isdir(MING3_LOCAL_REPO) and MING3_LOCAL_REPO not in sys.path:
        sys.path.insert(0, MING3_LOCAL_REPO)
        try:
            from ming_tts import MingTTS
            return MingTTS
        except ImportError:
            pass
    raise RuntimeError(MING3_INSTALL_HELP)


def _ming3_model_path():
    """Checkpoint resolution: explicit env, then the local setup directory, then the
    Hugging Face hub id (which `MingTTS` downloads via snapshot_download)."""
    env = os.environ.get("MING3_MODEL_PATH")
    if env:
        return env
    if os.path.isdir(MING3_LOCAL_CHECKPOINT):
        return MING3_LOCAL_CHECKPOINT
    return MING3_DEFAULT_MODEL


def _ming3_device():
    """Device resolution: explicit env, then whatever torch reports. On AMD setups
    (WSL2 + ROCm, or ZLUDA on Windows) torch exposes HIP as 'cuda:0', so auto-detect
    picks up the GPU the moment a GPU-capable torch build is installed."""
    env = os.environ.get("MING3_DEVICE")
    if env:
        return env
    try:
        import torch
        return "cuda:0" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


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


def _spkemb_file(embedding):
    """Materialize a frozen speaker embedding as the `torch.save` file the engine's
    `synthesize(spk_emb_path=...)` loader expects. Cached by content hash in the
    system temp dir so per-segment rendering writes it once per voice.

    Saved as bfloat16 to match the engine's own zero-embedding path exactly
    (`torch.zeros(1, 192, dtype=torch.bfloat16)`), avoiding a dtype mismatch in
    the `spk_head` projection."""
    import torch

    key = hashlib.sha256(
        json.dumps([round(float(x), 6) for x in embedding]).encode("utf-8")
    ).hexdigest()[:16]
    cache_dir = os.path.join(tempfile.gettempdir(), "ming3-spkemb-cache")
    path = os.path.join(cache_dir, f"spkemb-{key}.pt")
    if not os.path.isfile(path):
        os.makedirs(cache_dir, exist_ok=True)
        vec = torch.tensor([float(x) for x in embedding],
                           dtype=torch.bfloat16).unsqueeze(0)
        torch.save({"spk_emb": vec}, path)
    return path


class DeterministicRenderer:
    """The `ming` backend: delegates to casting.py's standalone synthesizer.

    Freeze-time golden references and render-time chapter audio pass through here,
    so both are produced by the same code with the same inputs."""

    backend = "ming"
    embedding_kind = "autocorr-64"

    def extract_speaker_embedding(self, wav_path):
        """Deterministic spectral voiceprint (autocorrelation lags). Text-sensitive:
        fine for the reference engine, not a speaker-verification instrument."""
        return _load_casting().extract_speaker_embedding_from_wav(wav_path)

    def synthesize_to_wav(
        self,
        text,
        out_wav_path,
        voice_id,
        voice_design,
        style=None,
        target_duration_sec=None,
        sample_rate=24000,
        speaker_embedding=None,  # accepted, unused: this engine's identity IS its
        # voice_design parameters — deterministic synthesis cannot drift from them
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
    embedding_kind = "camplus"
    _model = None

    def extract_speaker_embedding(self, wav_path):
        """Speaker-verification embedding via the engine's own CAM++ encoder
        (campplus.onnx, shipped with the checkpoint).

        This is the right instrument for the drift gate: unlike a spectral
        voiceprint it is trained to compare IDENTITY across different text and
        prosody. Measured on real engine output, the spectral voiceprint scored
        a cross-voice pair 0.94 and a same-voice cross-text pair 0.82 — inverted
        separation, i.e. an invalid gate."""
        import torch
        import torchaudio

        model = self._engine()
        waveform, rate = torchaudio.load(wav_path, backend="soundfile")
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if rate != 16000:
            waveform = torchaudio.functional.resample(waveform, rate, 16000)
        emb = model.spkemb_extractor(waveform.float().cpu())
        return [round(float(x), 6) for x in emb.flatten().tolist()]

    def _engine(self):
        if Ming3Renderer._model is None:
            MingTTS = _import_ming_tts()
            Ming3Renderer._model = MingTTS(
                _ming3_model_path(),
                device=_ming3_device(),
                # build-script.py already expands numbers, dates, currencies and
                # abbreviations into words, so the pynini FST normalizer (whose
                # wheels are unreliable on Windows) is neither needed nor wanted.
                text_normalization=False,
            )
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
        speaker_embedding=None,
    ):
        import torch
        import torchaudio

        model = self._engine()
        words, tags = split_paralinguistic_tags(text)
        if not words:
            raise RuntimeError(f"nothing speakable in segment for voice {voice_id!r}")
        instruction = build_ming3_instruction(voice_design, style, tags)

        # Identity conditioning: a frozen golden embedding pins the voice across
        # calls; without one the engine designs the voice afresh from the
        # instruction every call (freeze/audition deliberately do this — the voice
        # is designed from text with no reference audio, which keeps the
        # no-real-person-clone rule literal).
        if speaker_embedding:
            synth_kwargs = {
                "use_zero_spk_emb": False,
                "spk_emb_path": _spkemb_file(speaker_embedding),
                "use_spk_emb": True,
            }
        else:
            synth_kwargs = {"use_zero_spk_emb": True}

        # synthesize() returns the waveform tensor; writing the WAV here (rather
        # than round-tripping the engine's float32 container) keeps the contract's
        # 16-bit PCM format and lets torchaudio do the rate conversion properly.
        waveform = model.synthesize(
            task="FREEFORM",
            text=words,
            instruction=instruction,
            **synth_kwargs,
        )
        engine_rate = int(model.sample_rate)
        if waveform.device.type != "cpu":
            waveform = waveform.cpu()
        if engine_rate != sample_rate:
            waveform = torchaudio.functional.resample(waveform, engine_rate, sample_rate)

        # Silence-pad UP to `target_duration_sec` when natural speech is shorter
        # (never truncate). This is only safe because casting.verify_frozen_voices
        # separately requires >= 120s of actual speech: padding alone once turned a
        # 35s collapsed synthesis into a passing 180s artifact; the speech gate is
        # what distinguishes a fast voice from a collapse.
        duration_sec = waveform.shape[-1] / sample_rate
        if target_duration_sec is not None and duration_sec < float(target_duration_sec):
            pad = int((float(target_duration_sec) - duration_sec) * sample_rate)
            waveform = torch.nn.functional.pad(waveform, (0, pad))
            duration_sec = waveform.shape[-1] / sample_rate

        out_wav_path = os.path.abspath(out_wav_path)
        os.makedirs(os.path.dirname(out_wav_path), exist_ok=True)
        torchaudio.save(out_wav_path, waveform, sample_rate, encoding="PCM_S", bits_per_sample=16)

        meta_path = out_wav_path + ".meta.json"
        with open(meta_path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({
                "backend": "ming3",
                "engine_model": _ming3_model_path(),
                "engine_device": _ming3_device(),
                "voice_id": voice_id,
                "voice_design_sha256": hashlib.sha256(
                    voice_design.encode("utf-8")).hexdigest()[:16],
                "instruction": instruction,
                "speaker_conditioning": (
                    "frozen-golden:" + hashlib.sha256(
                        json.dumps([round(float(x), 6) for x in speaker_embedding]
                                   ).encode("utf-8")).hexdigest()[:16]
                    if speaker_embedding else "zero-voice-design"
                ),
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
