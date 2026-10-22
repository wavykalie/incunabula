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

    - The `ming` backend (default; aliases `builtin`, `deterministic`, `reference`)
      is the deterministic formant-harmonic acoustic synthesizer whose math lives in
      `casting.py::synthesize_fallback_wav` so Cluster B keeps working standalone when
      this file is absent. Deterministic is not a limitation here, it is the contract:
      identical inputs must yield byte-identical WAVs, or `casting.py verify` would
      report hash drift on a golden reference nobody touched.
    - A future real TTS engine (or a licensed voice-cloning service fed ONLY the
      golden reference produced by `casting.py freeze`) registers itself in
      `BACKEND_REGISTRY` and is selected with `--backend <name>`. Unknown backends
      are refused loudly — synthesis never silently falls back to a different voice.

  This file never reads or writes book state. Casting, audition, freeze, and render
  all call it; it knows nothing about any of them.

USAGE
  python tools/audio/renderer.py list
  python tools/audio/renderer.py synth --text "The tide turned at six." \\
      --voice-id NARRATOR --voice-design "a warm measured alto narrator" --out out.wav

  (Library use: casting.py and render-book.py load this file via importlib and call
  `create_renderer(backend_name)`.)

EXIT CODES
  0  OK — backend listed or WAV synthesized
  1  REFUSED / FAIL — synthesis produced no WAV
  2  NOT RUN — nothing to do
  3  ERROR — unknown backend or invalid arguments
"""

import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(HERE)

# Registry: canonical backend name -> accepted aliases. One engine today; the
# contract is the seam where a real TTS backend plugs in without touching callers.
BACKEND_REGISTRY = {
    "ming": ("ming", "builtin", "deterministic", "reference"),
}

_BACKEND_DESCRIPTIONS = {
    "ming": "deterministic formant-harmonic acoustic synthesizer (stdlib-only, byte-reproducible)",
}

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

    Raises ValueError on an unknown backend — never silently substitutes another
    voice engine."""
    canon = resolve_backend_name(backend_name)
    if canon is None:
        known = ", ".join(sorted(BACKEND_REGISTRY))
        raise ValueError(f"unknown renderer backend {backend_name!r} (known: {known})")
    if canon == "ming":
        return DeterministicRenderer()
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
            print(f"  {canon:<14} {desc}")
        return 0

    if args.cmd == "synth":
        try:
            renderer = create_renderer(args.backend)
        except ValueError as exc:
            print(f"renderer: ERROR — {exc}", file=sys.stderr)
            return 3
        res = renderer.synthesize_to_wav(
            text=args.text,
            out_wav_path=args.out,
            voice_id=args.voice_id,
            voice_design=args.voice_design,
            target_duration_sec=args.duration_sec,
            sample_rate=args.sample_rate,
        )
        if not res or not os.path.isfile(args.out):
            print(f"renderer: FAIL — backend {renderer.backend!r} produced no WAV at {args.out}",
                  file=sys.stderr)
            return 1
        print(f"renderer: OK — {args.out} ({res['duration_sec']:.2f}s @ {res['sample_rate']} Hz, "
              f"backend={renderer.backend})")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
