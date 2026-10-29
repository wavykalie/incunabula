#!/usr/bin/env python3
"""verifier.py — speaker-verification instrument for the render identity gate.

WHY THIS EXISTS
  The render gate has to answer one question: is this chapter's audio spoken by the
  voice whose golden reference was approved? Two instruments answer it, and they do
  not cost the same.

  * `campplus` — the engine's own speaker encoder (CAM++ via onnxruntime, 192-d),
    already used to condition synthesis. Cheap and already installed, but its
    same-voice cosines on Ming-3.0-tts output are only ~0.80–0.89 and its
    cross-voice cosines reach ~0.87, so the identity margin between "own voice" and
    "closest other voice" lands around 0.01–0.04 — inside its own noise.
  * `ecapa` — ECAPA-TDNN trained on VoxCeleb (speechbrain's `spkrec-ecapa-voxceleb`),
    192-d, run on CPU so it never competes with synthesis for VRAM. On the same
    audio it separates the cast by 0.16–0.69 where CAM++ separated by 0.55–0.97,
    i.e. it measures the difference the gate is looking for.

  The engine's CAM++ embedding keeps its own job — it is what `renderer.py` feeds to
  `synthesize(spk_emb_path=...)` for identity conditioning. This module only exists
  so the *gate* is measured with an instrument that can resolve the question.

  Measured on Muzzle and Marrow ch-01, 2026-10-23: the three lowest-cast voices
  (narrator, Mittens, Rocky) score 0.85–0.89 against their own references and
  0.81–0.90 against each other under both instruments — they were genuinely the
  same register, not a measurement artefact. That is a voice-design problem the
  gate is right to refuse; see `audiobook/config.yaml` voice_design notes.

WINDOWS NOTE
  speechbrain fetches its checkpoint through huggingface_hub, which prefers a
  symlink. Windows without Developer Mode cannot create symlinks, and the fetch
  raises `WinError 1314`. `_patch_speechbrain_symlinks()` falls back to a copy.
  The model directory (`tools/audio/.ming3/ecapa-voxceleb`) is downloaded once with
  `huggingface_hub.snapshot_download`; see ECAPA_INSTALL_HELP.

USAGE
  from verifier import make_verifier
  v, note = make_verifier("auto")        # ECAPA if importable, else CAM++
  emb = v.embedding("path/to/audio.wav")  # normalised float list
"""

import hashlib
import json
import os
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ECAPA_LOCAL_DIR = os.path.join(HERE, ".ming3", "ecapa-voxceleb")
ECAPA_HF_REPO = "speechbrain/spkrec-ecapa-voxceleb"
ECAPA_SAMPLE_RATE = 16000

ECAPA_INSTALL_HELP = (
    "ecapa verifier unavailable: speechbrain is not importable, or the local model "
    f"directory {ECAPA_LOCAL_DIR} is missing.\n"
    "Install with (the same venv that runs the audio pipeline):\n"
    "  <venv>/python -m pip install speechbrain\n"
    "  HF_HUB_DISABLE_SYMLINKS=1 <venv>/python -c \"from huggingface_hub import "
    f"snapshot_download; snapshot_download('{ECAPA_HF_REPO}', "
    f"local_dir=r'{ECAPA_LOCAL_DIR}')\"\n"
    "Then re-run with --verifier ecapa (or --verifier auto)."
)


def _patch_speechbrain_symlinks():
    """Make speechbrain's fetcher copy instead of symlink when symlinks are refused.

    Must run before any `from_hparams` call. Harmless when symlinks work: the
    original strategy is tried first and its result (including exceptions that are
    not permission errors) is preserved."""
    import shutil

    import speechbrain.utils.fetching as fetching

    original = fetching.link_with_strategy

    def link_or_copy(src, dst, strategy):
        try:
            return original(src, dst, strategy)
        except OSError:
            dst = str(dst)
            if not os.path.exists(dst):
                shutil.copyfile(str(src), dst)
            return dst

    fetching.link_with_strategy = link_or_copy


def _cache_path(kind, wav_path):
    """Content-addressed embedding cache: re-embedding the same audio is free."""
    digest = hashlib.sha256()
    with open(wav_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    cache_dir = os.path.join(tempfile.gettempdir(), "incunabula-verifier-cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"{kind}-{digest.hexdigest()[:24]}.json")


class EcapaVerifier:
    """ECAPA-TDNN (VoxCeleb) speaker verification, CPU only."""

    kind = "ecapa"
    embedding_dim = 192

    def __init__(self):
        _patch_speechbrain_symlinks()
        from speechbrain.inference.speaker import EncoderClassifier  # noqa: F401

        if not os.path.isdir(ECAPA_LOCAL_DIR):
            raise RuntimeError(ECAPA_INSTALL_HELP)
        self._model = EncoderClassifier.from_hparams(
            source=ECAPA_LOCAL_DIR,
            savedir=ECAPA_LOCAL_DIR,
            run_opts={"device": "cpu"},
        )

    def embedding(self, wav_path):
        cached = _cache_path(self.kind, wav_path)
        if os.path.isfile(cached):
            try:
                with open(cached, "r", encoding="utf-8") as fh:
                    return json.load(fh)["embedding"]
            except (OSError, ValueError, KeyError):
                pass

        import torch
        import torchaudio

        waveform, rate = torchaudio.load(wav_path)
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        if rate != ECAPA_SAMPLE_RATE:
            waveform = torchaudio.functional.resample(
                waveform, rate, ECAPA_SAMPLE_RATE)
        with torch.no_grad():
            emb = self._model.encode_batch(waveform).squeeze()
        emb = (emb / emb.norm()).tolist()

        try:
            with open(cached, "w", encoding="utf-8", newline="\n") as fh:
                json.dump({"kind": self.kind, "wav": os.path.basename(wav_path),
                           "embedding": emb}, fh)
        except OSError:
            pass
        return emb


class RendererVerifier:
    """Fallback: whatever speaker encoder the synthesis backend exposes (CAM++)."""

    kind = "campplus"

    def __init__(self, renderer):
        if not hasattr(renderer, "extract_speaker_embedding"):
            raise RuntimeError(
                "backend exposes no extract_speaker_embedding; cannot verify identity")
        self._renderer = renderer
        self.embedding_dim = getattr(renderer, "embedding_dim", 192)

    def embedding(self, wav_path):
        return self._renderer.extract_speaker_embedding(wav_path)


def make_verifier(preference="auto", renderer=None):
    """Return (verifier, note).

    `preference`: "ecapa", "campplus", or "auto" (ECAPA when importable, else the
    backend's own encoder). The note is a one-line explanation for the manifest, so
    a reader can always tell which instrument produced the gate numbers."""
    preference = (preference or "auto").strip().lower()
    if preference not in ("auto", "ecapa", "campplus"):
        raise ValueError(
            f"unknown verifier {preference!r}; expected auto, ecapa, or campplus")

    if preference in ("auto", "ecapa"):
        try:
            return EcapaVerifier(), "ecapa-tdnn (voxceleb), cpu"
        except Exception as exc:  # import error, missing weights, ...
            if preference == "ecapa":
                raise RuntimeError(f"{ECAPA_INSTALL_HELP}\n({exc})") from exc
            note = f"campplus (ecapa unavailable: {type(exc).__name__})"
            return RendererVerifier(renderer), note

    return RendererVerifier(renderer), "campplus (engine encoder)"
