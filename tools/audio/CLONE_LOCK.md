# Clone-lock: one frozen voice per character

This is the workflow the audiobook stage renders chapters under. It exists because
of a specific, measurable failure: voices warped and drifted between chapters.

The cause was not the engine's quality. It was that every render **asked for a voice
again**. Voice design is stochastic — describe a voice in words and each design call
returns a slightly different person. A pipeline that designs per segment, per
chapter or per render therefore guarantees drift, no matter how good the
description is. Measured on this stage, two calls from the same design brief scored
0.40–0.81 cosine against each other. The listener hears that as the character
changing between lines.

Clone-lock removes the second design. A voice is designed once, listened to once,
frozen once — and from then on a chapter render can only *copy* it.

---

## The seven steps

### 1. Cast registry

`audiobook/voices/cast-registry.json` holds one entry per character:

| field | meaning |
| --- | --- |
| `character` | the name the scripts use |
| `design_brief` | the natural-language voice design used **only** at design time |
| `design_brief_sha256` | pins the brief the voice was made from |
| `reference` | golden WAV, golden transcript, both checksums, duration, version |
| `frozen` | `true` only after a human approved and froze it |
| `created_at` | when the entry first appeared |
| `approval` | who listened, when, and the SHA-256 of the exact audio they heard |
| `history` | every earlier frozen version, kept for audit |

The registry is the stage's only statement of who has a locked voice. A character
missing from it, or present with `frozen: false`, cannot be rendered.

### 2. Design — once per character, before first use

```
python tools/audio/clone_lock.py design test-books/muzzle-and-marrow
```

Design runs the voice design from the character's brief, then renders a **3–5
minute golden reference from that character's actual book prose** — the dialogue
and narration lines `build-script.py` attributed to them, in reading order. Not
generic sample sentences: the reference has to sound like the character *in this
book*.

The result is a **candidate**, written to
`audiobook/voices/<character>/design-candidate.wav` with its exact transcript.
Nothing is frozen. A candidate is not a voice yet.

If the character has too little prose in the book (under 450 words) to fill a 3–5
minute reference, design refuses and names the character. It does not pad the
reference with sample text.

### 3. Human listen-approval

```
python tools/audio/clone_lock.py approve test-books/muzzle-and-marrow \
    --character "Mittens Brisk" --reviewer "your name"
```

Approval records the reviewer, the time, and the SHA-256 of the exact candidate
file they listened to. There is **no auto-approve path**: an empty reviewer is
refused, and so are pipeline words (`auto`, `pipeline`, `bot`, `n/a`, …), because a
listening pass is a human act. If the candidate changes after approval, the
approval no longer matches and freezing refuses.

### 4. Freeze

```
python tools/audio/clone_lock.py freeze test-books/muzzle-and-marrow \
    --character "Mittens Brisk"
```

Freeze copies the approved candidate into

```
audiobook/voices/<character>/v001/golden_reference.wav
audiobook/voices/<character>/v001/golden_transcript.txt
audiobook/voices/<character>/v001/FREEZE.json
```

and marks the WAV and transcript read-only. Both hashes are recorded in the
registry. Versions are **never overwritten**: re-freezing is an explicit human
command

```
python tools/audio/clone_lock.py freeze <book> --refreeze \
    --character "Mittens Brisk" --reviewer "your name" --reason "why"
```

which starts `v002/` and keeps `v001/` intact in `history`. No render, no second
freeze and no script can trigger a re-freeze.

### 5. Render by cloning, never by designing

```
python tools/audio/render-book.py test-books/muzzle-and-marrow
```

Every scene is rendered in **one engine pass** with `speaker_N:` tags and one
frozen reference per character in the scene. Characters are never rendered
separately and stitched — a separate render can warp independently, which is the
same bug in a different shape.

A scene is the script's own unit: the segments between explicit `pause` segments,
whose silences are still honoured exactly. Within a scene, the engine now owns the
pacing and the sentence beats (`pause_after_ms`), because a single pass has no
per-segment seam to insert them at. That is the trade the single pass buys, and it
is the directing layer's unit, not a new one.

The render path has no design method to call. If a chapter references a character
with no frozen reference, the render **hard-stops** with an error naming that
character. It never designs a voice to fill the gap and never substitutes another
character's voice:

```
render-book: REFUSED — no frozen golden reference for character(s): 'Teasel'.
Clone-lock never designs a voice to fill the gap and never substitutes another
character's voice. Run `design`, listen, `approve`, then `freeze` for each of them.
```

### 6. Drift instrumentation

After each chapter, speaker-embedding cosine similarity between the rendered audio
and each character's golden reference is measured **per character** and appended to
`audiobook/audio/drift-log.json`:

```
python tools/audio/clone_lock.py drift test-books/muzzle-and-marrow
```

```
chapter  character      cosine  floor  status
01       Mittens Brisk  0.989   0.70   OK
01       NARRATOR       0.990   0.70   OK
02       Mittens Brisk  0.988   0.70   OK
02       NARRATOR       0.991   0.70   OK
```

A character below the floor FAILS the chapter, is printed to stderr, and is
flagged for re-render. It is never accepted silently.

A scene is one engine pass, so the engine does not hand back per-turn boundaries.
The chapter is therefore embedded in 1.5 s windows (0.75 s hop) and each speech
window is attributed to whichever character's reference it matches best; a
character's number is the mean cosine of its own windows to its own reference. A
voice that drifts pulls its own mean down. A voice replaced by another character's
audio has its windows attributed to that character and reports as missing.

The floor defaults to **0.70**. Same-voice material on the production engine
measured 0.615–0.905 in the pre-clone-lock pipeline; clone-locked single-pass
rendering removes most of that draw-to-draw spread, so the floor sits at the bottom
of the healthy band rather than inside it. Calibrate it per verifier with
`--drift-floor` and record the measured numbers in the run log.

Companion tooling: [earshot](https://github.com/Leonxlnx/earshot) is useful next to
this gate for level and sound-character measurements, but it does **not** measure
speaker identity. Its description and match scores are not voice-identity metrics
and must never be substituted for the speaker-embedding cosine above.

### 7. Determinism

The same chapter rendered from the same frozen references reproduces the same
voices. Rendering takes no random seed and performs no draw selection: identity
comes only from the frozen reference. On the deterministic reference engine a
re-render is byte-identical; on the production engine it is the same voice within
the similarity floor.

---

## What changed in the stage

| before | after |
| --- | --- |
| voice designed per segment/chapter from the brief | designed once, candidate approved by a human, frozen |
| per-segment draw selection (keep the best of up to 3–4 draws) | one deterministic pass per scene, no draws |
| characters rendered separately and concatenated | whole scene in one pass with speaker tags |
| missing voice filled by designing on the fly | hard stop naming the character |
| drift reported but not gated | drift measured per character, logged, below floor = FAIL |
| references written by the renderer | references read-only, versioned, checksum-verified before and after render |

The directing layer (`build-script.py`), the engine-swappable renderer interface
(`renderer.py`), and the humanistic voice guidelines are unchanged.

---

## Engine note

Single-pass multi-speaker rendering is the `podcast` task. It exists in
Ming-3.0-tts-**tiny**; the 0.5b checkpoint has no speaker-tagged task. When the tiny
checkpoint is absent, a scene render refuses with install instructions — it does
not fall back to per-character stitching.

```
tools/audio/.ming3/venv/Scripts/hf.exe download inclusionAI/Ming-3.0-tts-tiny \
    --local-dir tools/audio/.ming3/Ming-3.0-tts-tiny
```

`MING3_TINY_MODEL_PATH` overrides the checkpoint location. Device selection is
automatic: any torch build that reports a device (CUDA, ROCm/HIP, ZLUDA) is used;
`MING3_DEVICE` overrides it.

Two practical constraints of the tiny release, measured on this checkout:

- **16.7 GiB of bf16 weights** (`8.98B parameters`). They cannot be held on an 8 GiB
  card, and this host's torch build is CPU-only, so the card is not used at all: the
  scene renders on the CPU out of system RAM. The 0.5b checkpoint (2.8 GiB) is the
  one that fits on small GPUs, and it is the design/freeze engine only.
- **Triton runtime, worked around.** The checkpoint has Kimi-Delta linear-attention
  layers, so the engine imports `fla-core`, which imports `triton`. There is no CPU
  Triton backend and no AMD Triton backend on Windows, so the import fails before a
  weight is read. `ming_torch_kda.py` supplies the four symbols `ming_tiny` imports
  in plain torch, and the renderer installs it automatically before importing the
  engine (`_install_tiny_kda_backend`), then applies the release's two CPU shims
  (`_patch_tiny_cpu_runtime`).

Verified on this checkout (Windows, CPU, AMD RX 6600 XT present but unusable from
this torch build):

- `ming_torch_kda` matches `fla`'s own naive KDA reference to float precision:
  both gate modes `0.0`, chunked `4.8e-06`, incremental-vs-full `6e-08`.
- Audio-VAE round-trip of a frozen reference transcribes back to its own text
  verbatim, so the encode/decode path is sound.
- A three-turn, two-character `podcast` scene through
  `renderer.synthesize_scene_to_wav` produced 9.84 s of audio whose transcript is
  the script line for line, with `kda_backend: ming_torch_kda (pure-torch KDA; no
  triton)` recorded in the scene metadata.
- Throughput: **~8x slower than realtime** (91.7 s wall for 9.84 s of audio,
  including 14 s of model load; ≈0.6 s per 80 ms latent step). A 10-minute scene
  is roughly 80 minutes. Decode, not prompt prefill, is the cost.

The renderer refuses a GPU device while the pure-torch backend is active, so a host
without Triton cannot silently appear to be using its card.

### Why not quantize it onto the card

Measured, so it is not re-litigated:

- **The card has no compute path on this OS.** WSL2 exposes `/dev/dri` and
  `/dev/dxg` (DirectX passthrough) but no `/dev/kfd`, which HIP/ROCm requires, and
  RX 6600 XT (`gfx1032`, RDNA2) is outside AMD's ROCm support matrix on both
  Windows and WSL. Ming on ROCm is real, but on a supported Linux card
  (`gfx110x`, MI series), not on this one.
- **int8 weight-only is slower here**, not faster: LM-head GEMV (`157184x1536`)
  33.8 ms int8 versus 20.0 ms bf16, because torch's CPU int8 kernel is not
  bandwidth-bound at these shapes. 4-bit needs bitsandbytes, which has no CPU and
  no Windows backend.
- **The weights are not the bottleneck anyway.** Eight expert GEMVs cost 0.36 ms
  per MoE layer (~25 ms per token of 740 ms), and the whole 16.7 GiB is only read
  for the experts actually routed.
- **Size still rules it out.** bf16 is 16.7 GiB, int8 ~9 GiB (already over 8 GiB),
  and only 4-bit (~4.5 GiB) would fit — the one format with no CPU path.

Where a 740 ms decode step does go: ~43% the flow sampler (10 Euler passes of a
16-layer DiT under CFG=2) and ~57% the LLM's per-op overhead across 24 layers.
`flow_steps` is the only meaningful dial and it is part of the release's formal
sampling contract: on the verification scene 4 steps rendered in 46.5 s against
74.6 s at 10 with the transcript still exact, but 6 steps drifted off-script — so
it needs per-scene verification, not a global default.

---

## Files

```
tools/audio/clone_lock.py            the workflow: registry, design/approve/freeze,
                                     scene rendering, drift log, CLI
tools/audio/render-book.py           chapter renderer (clone-lock only)
tools/audio/tests/test_clone_lock.py acceptance tests
tools/audio/CLONE_LOCK_RUN_LOG.md    run log of the test renders
audiobook/voices/cast-registry.json  per-book cast state
audiobook/voices/<name>/vNNN/        frozen references (read-only, versioned)
audiobook/audio/drift-log.json       per-chapter, per-character similarity
```

## Tests

```
python -m unittest discover -s tools/audio/tests -v
```
