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
            speaker_embedding=None, seed_salt="",
        ) -> {"wav_path": ..., "duration_sec": ..., "sample_rate": ...}

      `seed_salt` disambiguates identical (voice, text) calls: without it the
      engine is seeded per (voice, text), so a repeated line like "Mittens said."
      renders to byte-identical audio every time it appears — the listener hears
      machine echoes instead of three readings. Callers pass the segment id or
      clip name so repeats vary like a human narrator's, while re-renders of the
      same segment stay reproducible.

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

    Clone-lock (see clone_lock.py) splits the contract in two, so a chapter render
    cannot re-design a voice:

        renderer.design_to_wav(text, out_wav_path, character, design_brief, ...)
        renderer.synthesize_scene_to_wav(turns, out_wav_path, cast, sample_rate=...)

      `design_to_wav` is used ONLY by the design phase, once per character, to make
      the golden-reference candidate. `synthesize_scene_to_wav` renders a whole
      scene in ONE engine pass with speaker tags, conditioned on one frozen
      reference per character and taking no seed — chapter rendering has no design
      call and no draw selection to reach for.
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
import shutil
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

# Prosody controls. The engine's own defaults are temperature=0.0 (deterministic
# decoding: the single most likely acoustic path, i.e. the flattest possible
# delivery) and max_length=24 (text cut into ~24-token fragments generated
# separately and stitched, with the first fragment reused as the reference —
# sentence-level intonation does not survive that). Measured on Muzzle and
# Marrow ch-01, those defaults produced the same staccato, averaged reading in
# every voice. A little sampling temperature restores micro-variation; raw_text
# sends each segment as one utterance (the engine's benchmark mode). The seed is
# derived per (voice, text), so the same script re-renders to the same audio.
MING3_TEMPERATURE = 0.25
MING3_RAW_TEXT = True

# Long inputs must still be chunked. `raw_text=True` sends the whole string as one
# utterance, and past roughly a minute of speech the engine stops generating: the
# golden-reference freeze (a ~600-word passage, one call) returned zero audio
# frames and crashed on torch.cat. Sentences are packed up to this many words per
# call, then joined with a short gap, which keeps every call inside the range the
# engine reliably finishes.
MING3_MAX_CHUNK_WORDS = 45
MING3_CHUNK_GAP_MS = 120

MING3_DEFAULT_MODEL = "inclusionAI/Ming-3.0-tts-0.5b"
MING3_LOCAL_ROOT = os.path.join(HERE, ".ming3")
MING3_LOCAL_REPO = os.path.join(MING3_LOCAL_ROOT, "Ming-3.0-tts")
MING3_LOCAL_CHECKPOINT = os.path.join(MING3_LOCAL_ROOT, "Ming-3.0-tts-0.5b")

# Multi-speaker scenes are the `podcast` task, which only the tiny release
# implements; the 0.5b release has no speaker-tagged task at all. Clone-lock
# renders a scene in one pass or refuses — it never stitches characters.
MING3_TINY_DEFAULT_MODEL = "inclusionAI/Ming-3.0-tts-tiny"
MING3_TINY_LOCAL_CHECKPOINT = os.path.join(MING3_LOCAL_ROOT, "Ming-3.0-tts-tiny")
MING3_PODCAST_SEED = 1235  # the release's formal podcast seed
MING3_TINY_INSTALL_HELP = (
    "clone-lock multi-speaker scenes need the Ming-3.0-tts-tiny release (the "
    "podcast task); the 0.5b checkpoint has no speaker-tagged task. Install it:\n"
    "  tools/audio/.ming3/venv/Scripts/hf.exe download inclusionAI/Ming-3.0-tts-tiny "
    "--local-dir tools/audio/.ming3/Ming-3.0-tts-tiny\n"
    "or set MING3_TINY_MODEL_PATH to the checkpoint directory. Clone-lock refuses "
    "to stitch per-character renders instead: separate renders warp independently."
)

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


def _engine_chunks(text, max_words):
    """Pack sentences into engine calls of at most `max_words` words."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?\u2026])\s+", text or "") if s.strip()]
    if not sentences:
        return [text] if (text or "").strip() else []
    chunks, current, count = [], [], 0
    for sentence in sentences:
        n = len(sentence.split())
        if current and count + n > max_words:
            chunks.append(" ".join(current))
            current, count = [], 0
        if n > max_words:
            # A single run-on sentence: split on clause punctuation, then on words.
            clauses = [c.strip() for c in re.split(r"(?<=[,;:])\s+", sentence) if c.strip()]
            for clause in clauses:
                # A clause can itself be run-on; fall back to a word window.
                words_in = clause.split()
                while len(words_in) > max_words:
                    if current:
                        chunks.append(" ".join(current))
                        current, count = [], 0
                    chunks.append(" ".join(words_in[:max_words]))
                    words_in = words_in[max_words:]
                if not words_in:
                    continue
                clause = " ".join(words_in)
                m = len(words_in)
                if current and count + m > max_words:
                    chunks.append(" ".join(current))
                    current, count = [], 0
                current.append(clause)
                count += m
            continue
        current.append(sentence)
        count += n
    if current:
        chunks.append(" ".join(current))
    return chunks


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


def _import_ming_tiny():
    """Import the tiny release's `ming_tiny` package (podcast / multi-speaker)."""
    try:
        from ming_tiny import MingTinyTTS
        return MingTinyTTS
    except ImportError:
        pass
    if os.path.isdir(MING3_LOCAL_REPO) and MING3_LOCAL_REPO not in sys.path:
        sys.path.insert(0, MING3_LOCAL_REPO)
        try:
            from ming_tiny import MingTinyTTS
            return MingTinyTTS
        except ImportError:
            pass
    raise RuntimeError(MING3_TINY_INSTALL_HELP)


def _ming3_tiny_model_path():
    env = os.environ.get("MING3_TINY_MODEL_PATH")
    if env:
        return env
    if os.path.isdir(MING3_TINY_LOCAL_CHECKPOINT):
        return MING3_TINY_LOCAL_CHECKPOINT
    return MING3_TINY_DEFAULT_MODEL


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


def _read_pcm16(path, expected_rate):
    """Read a mono 16-bit WAV's raw frames, refusing a rate mismatch."""
    import wave

    with wave.open(path, "rb") as wf:
        if wf.getsampwidth() != 2 or wf.getnchannels() != 1:
            raise RuntimeError(f"{path}: expected mono 16-bit PCM")
        if wf.getframerate() != expected_rate:
            raise RuntimeError(
                f"{path}: rate {wf.getframerate()} does not match {expected_rate}")
        return wf.readframes(wf.getnframes())


def _write_scene_meta(out_wav_path, backend, turns, cast, sample_rate, extra):
    """Audit record for one scene pass: who spoke, under which frozen reference."""
    meta = {
        "backend": backend,
        "mode": "single-pass-scene",
        "conditioning": "frozen-golden-references",
        "characters": [
            {"character": c,
             "reference_wav": os.path.basename(cast[c].get("reference_wav", "")),
             "reference_sha256": cast[c].get("wav_sha256")}
            for c in sorted(cast)
        ],
        "turns": [{"speaker": t["speaker"], "words": len(t["text"].split())}
                  for t in turns],
        "sample_rate": sample_rate,
    }
    meta.update(extra or {})
    with open(out_wav_path + ".meta.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


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
        seed_salt="",  # accepted, unused: this engine is deterministic already
        prompt_clip_path=None,  # accepted, unused: no acoustic conditioning here
        prompt_clip_text=None,
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

    def design_to_wav(self, text, out_wav_path, character, design_brief,
                      target_duration_sec=None, sample_rate=24000):
        """Design phase only: one voice designed from its brief, no reference."""
        return self.synthesize_to_wav(
            text=text,
            out_wav_path=out_wav_path,
            voice_id=character,
            voice_design=design_brief,
            target_duration_sec=target_duration_sec,
            sample_rate=sample_rate,
        )

    def synthesize_scene_to_wav(self, turns, out_wav_path, cast, sample_rate=24000):
        """One scene, one call. No randomness: this engine is byte-reproducible.

        Each turn is spoken with the identity of the character's FROZEN design
        brief, which is the parameter set the approved golden reference was made
        from. The deterministic engine has no draw-to-draw variance at all, so a
        re-render from the same frozen references is byte-identical — the strongest
        possible form of the clone-lock guarantee. It is still one scene render: the
        caller never joins per-character passes.
        """
        casting = _load_casting()
        missing = sorted({t["speaker"] for t in turns} - set(cast))
        if missing:
            raise RuntimeError(
                f"scene references character(s) {missing!r} with no frozen reference")
        tmp_dir = tempfile.mkdtemp(prefix="clone-lock-scene-")
        frames = []
        try:
            for index, turn in enumerate(turns):
                reference = cast[turn["speaker"]]
                part_path = os.path.join(tmp_dir, f"turn-{index:04d}.wav")
                casting.synthesize_fallback_wav(
                    out_wav_path=part_path,
                    text=turn["text"],
                    voice_id=turn["speaker"],
                    voice_design=reference["design_brief"],
                    style={},
                    sample_rate=sample_rate,
                )
                frames.append(_read_pcm16(part_path, sample_rate))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        out_wav_path = os.path.abspath(out_wav_path)
        os.makedirs(os.path.dirname(out_wav_path), exist_ok=True)
        import wave

        with wave.open(out_wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(frames))
        _write_scene_meta(out_wav_path, self.backend, turns, cast, sample_rate,
                          {"determinism": "byte-reproducible"})
        return {
            "wav_path": out_wav_path,
            "duration_sec": round(sum(len(f) // 2 for f in frames) / sample_rate, 3),
            "sample_rate": sample_rate,
        }


class Ming3Renderer:
    """The `ming3` backend: Ant Ming-3.0-tts via its official `ming_tts` package.

    Identity comes from `voice_design` through task FREEFORM (a voice designed from
    text, no reference audio); delivery comes from `style` and paralinguistic tags
    folded into the same instruction. The engine model is loaded once and reused
    for every segment. Engine failures propagate — see MING3_INSTALL_HELP."""

    backend = "ming3"
    embedding_kind = "camplus"
    _model = None
    _tiny_model = None

    def _tiny_engine(self):
        """Ming-3.0-tts-tiny, the release that carries the `podcast` task.

        Loading is lazy because design and single-voice work never need it. A
        missing checkpoint raises with install steps: clone-lock refuses to fall
        back to per-character stitching, which is the drift bug in another shape.
        """
        if Ming3Renderer._tiny_model is None:
            try:
                MingTinyTTS = _import_ming_tiny()
                Ming3Renderer._tiny_model = MingTinyTTS.from_pretrained(
                    _ming3_tiny_model_path(), device=_ming3_device())
            except Exception as exc:
                raise RuntimeError(
                    f"{MING3_TINY_INSTALL_HELP}\n({type(exc).__name__}: {exc})") from exc
        return Ming3Renderer._tiny_model

    def design_to_wav(self, text, out_wav_path, character, design_brief,
                      target_duration_sec=None, sample_rate=24000):
        """Design phase only: a voice designed from its brief with no reference.

        This is the one place the engine is allowed to invent a voice.
        """
        return self.synthesize_to_wav(
            text=text,
            out_wav_path=out_wav_path,
            voice_id=character,
            voice_design=design_brief,
            target_duration_sec=target_duration_sec,
            sample_rate=sample_rate,
        )

    def synthesize_scene_to_wav(self, turns, out_wav_path, cast, sample_rate=24000):
        """Render a whole scene in ONE `podcast` pass, one frozen reference each.

        The engine sees `speaker_N:` tags for the entire scene plus the ordered
        reference audio/transcripts, so every turn is continued from the same
        reference in the same generation. No character is rendered separately and
        no audio is stitched. The seed is the release's formal podcast seed and
        temperature is 0: voice selection carries no randomness.
        """
        import torch
        import torchaudio

        missing = sorted({t["speaker"] for t in turns} - set(cast))
        if missing:
            raise RuntimeError(
                f"scene references character(s) {missing!r} with no frozen reference")
        order = []
        for turn in turns:
            if turn["speaker"] not in order:
                order.append(turn["speaker"])
        lines = [f"speaker_{order.index(t['speaker']) + 1}: {t['text']}" for t in turns]
        script = "\n".join(lines)
        prompt_wavs = [cast[c]["reference_wav"] for c in order]
        prompt_texts = [cast[c]["transcript"] for c in order]

        model = self._tiny_engine()
        waveform = model.generate(
            task="podcast",
            text=script,
            prompt_wav=prompt_wavs,
            prompt_text=prompt_texts,
            seed=MING3_PODCAST_SEED,
            temperature=0.0,
        )
        if waveform is None or waveform.numel() == 0:
            raise RuntimeError(
                f"engine produced no audio for a {len(turns)}-turn scene "
                f"({', '.join(order)})")
        waveform = waveform.detach().cpu().to(torch.float32).reshape(1, -1)
        engine_rate = int(model.engine.sample_rate) if hasattr(model, "engine") else 44100
        if engine_rate != sample_rate:
            waveform = torchaudio.functional.resample(waveform, engine_rate, sample_rate)
        peak = float(waveform.abs().max())
        if peak > 0.89:
            waveform = waveform * (0.89 / peak)

        out_wav_path = os.path.abspath(out_wav_path)
        os.makedirs(os.path.dirname(out_wav_path), exist_ok=True)
        torchaudio.save(out_wav_path, waveform, sample_rate, encoding="PCM_S",
                        bits_per_sample=16)
        duration = waveform.shape[-1] / float(sample_rate)
        _write_scene_meta(out_wav_path, self.backend, turns, cast, sample_rate, {
            "task": "podcast",
            "speaker_order": order,
            "engine_model": _ming3_tiny_model_path(),
            "seed": MING3_PODCAST_SEED,
            "temperature": 0.0,
            "duration_sec": round(duration, 3),
        })
        return {"wav_path": out_wav_path, "duration_sec": round(duration, 3),
                "sample_rate": sample_rate}

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
        seed_salt="",
        prompt_clip_path=None,
        prompt_clip_text=None,
    ):
        import torch
        import torchaudio

        model = self._engine()
        words, tags = split_paralinguistic_tags(text)
        if not words:
            raise RuntimeError(f"nothing speakable in segment for voice {voice_id!r}")
        instruction = build_ming3_instruction(voice_design, style, tags)

        # Identity conditioning, strongest first.
        #
        # 1. ACOUSTIC PROMPT (frozen prompt clip + its exact transcript). The
        #    engine encodes the clip into VAE latents and continues from them, so
        #    every segment inherits the clip's timbre, room, and codec character,
        #    not just a 192-dim identity vector. This is the difference between
        #    "the same person" and "the same recording": on chapter 01 the same
        #    voice's segments scattered 34.4 in mean-MFCC distance when only the
        #    embedding was passed, and 14.2 with the clip — while identity cosine
        #    was unchanged (0.795 vs 0.787). The ear hears the 34/14 difference;
        #    a speaker-cosine gate cannot, which is why the drift gate passed
        #    audio the listener rejected as changing voice to voice.
        #
        # 2. SPEAKER EMBEDDING ONLY (no clip): pins who, not how it sounds.
        #    Kept as the fallback for a voice with no frozen clip.
        #
        # 3. NOTHING: the engine designs the voice afresh from the instruction
        #    every call (freeze/audition deliberately do this — the voice is
        #    designed from text with no reference audio, which keeps the
        #    no-real-person-clone rule literal: a prompt clip is minted from the
        #    voice's own synthetic golden, never from a real person).
        if prompt_clip_path and prompt_clip_text:
            synth_kwargs = {
                "use_zero_spk_emb": False,
                "prompt_wav_path": prompt_clip_path,
                "prompt_text": prompt_clip_text,
                "use_spk_emb": True,
            }
        elif speaker_embedding:
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
        engine_rate = int(model.sample_rate)
        chunks = _engine_chunks(words, MING3_MAX_CHUNK_WORDS)
        gap = torch.zeros(1, int(engine_rate * MING3_CHUNK_GAP_MS / 1000.0))
        # 15ms edge fades on every piece: chunk seams and segment joins land on
        # fade->silence->fade instead of raw onsets, which is where the audible
        # clicks/stutters at concatenation boundaries came from.
        fade_n = max(1, int(engine_rate * 0.015))
        fade_in = torch.linspace(0.0, 1.0, fade_n).reshape(1, -1)
        pieces = []
        for chunk in chunks:
            segment_seed = int(
                hashlib.sha256(
                    f"{voice_id}\x00{seed_salt}\x00{chunk}".encode("utf-8")
                ).hexdigest()[:8], 16)
            if MING3_TEMPERATURE > 0:
                torch.manual_seed(segment_seed)
            part = model.synthesize(
                task="FREEFORM",
                text=chunk,
                instruction=instruction,
                temperature=MING3_TEMPERATURE,
                raw_text=MING3_RAW_TEXT,
                **synth_kwargs,
            )
            if part.device.type != "cpu":
                part = part.cpu()
            part = part.to(torch.float32).reshape(1, -1)
            if part.shape[-1] == 0:
                raise RuntimeError(
                    f"engine produced no audio for voice {voice_id!r} on chunk "
                    f"{len(pieces) + 1}/{len(chunks)} ({len(chunk.split())} words)"
                )
            if part.shape[-1] > 2 * fade_n:
                # out-of-place: the engine returns inference tensors, which
                # refuse in-place slice assignment
                part = torch.cat([
                    part[:, :fade_n] * fade_in,
                    part[:, fade_n:-fade_n],
                    part[:, -fade_n:] * fade_in.flip(1),
                ], dim=-1)
            if pieces:
                pieces.append(gap)
            pieces.append(part)
        waveform = torch.cat(pieces, dim=-1)
        if engine_rate != sample_rate:
            waveform = torchaudio.functional.resample(waveform, engine_rate, sample_rate)

        # Attenuate-only ceiling at -1 dBFS. The engine's float output exceeds
        # +/-1.0 on stressed segments and torchaudio's PCM_S save hard-clips those
        # samples flat — audible digital corruption on exactly the loudest words.
        peak = float(waveform.abs().max()) if waveform.numel() else 0.0
        if peak > 0.89:
            waveform = waveform * (0.89 / peak)

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
                "acoustic_prompt": (
                    {
                        "prompt_clip": os.path.basename(prompt_clip_path),
                        "prompt_clip_sha256": hashlib.sha256(
                            open(prompt_clip_path, "rb").read()).hexdigest()[:16],
                        "prompt_text_sha256": hashlib.sha256(
                            prompt_clip_text.encode("utf-8")).hexdigest()[:16],
                    }
                    if prompt_clip_path and prompt_clip_text else None
                ),
                "temperature": MING3_TEMPERATURE,
                "raw_text": MING3_RAW_TEXT,
                "seed": int(hashlib.sha256(
                    f"{voice_id}\x00{seed_salt}\x00{words}".encode("utf-8")).hexdigest()[:8], 16),
                "seed_salt": seed_salt,
                "chunks": len(chunks),
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
