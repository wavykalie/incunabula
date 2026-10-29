# Clone-lock run log

Short record of the renders and checks this change was verified with. Dates are
2026-10-29. Machine: Windows, CPU (torch reports no CUDA device in this shell;
`MING3_DEVICE` overrides device selection on a ROCm/ZLUDA build).

## 1. Acceptance test suite

```
python -m unittest discover -s tools/audio/tests -v
```

```
test_same_character_across_three_chapters ... ok
test_two_speaker_scene_is_one_pass_and_distinct ... ok
test_render_book_cli_refuses_unfrozen_cast ... ok
test_unfrozen_character_hard_stops ... ok
test_rerender_reproduces_the_voice ... ok
test_frozen_references_survive_book_render ... ok
test_design_refuses_thin_book_material ... ok
test_design_renders_from_book_prose ... ok
test_drift_below_floor_fails_the_chapter ... ok
test_freeze_requires_a_human_listening_pass ... ok
test_refreeze_is_explicit_and_keeps_old_version ... ok
test_render_book_cli_writes_drift_log ... ok

Ran 12 tests in 22.6s
OK
```

The suite runs on the deterministic reference engine (`ming`), which needs no
model download and is byte-reproducible. It exercises the production workflow and
renderer interface, not the acoustic quality of a particular engine.

## 2. Test render — 3 chapters, 3 characters

Fixture book (three characters, one scene per chapter), references designed from
the fixture's own book prose, approved by a named listener, frozen at v001, then
rendered chapter by chapter:

```
ch-01 44.3s scenes=1 fails=[]
ch-02 45.1s scenes=1 fails=[]
ch-03 43.5s scenes=1 fails=[]

chapter  character        cosine  floor  status
01       Mittens Brisk    0.989   0.70   OK
01       NARRATOR         0.990   0.70   OK
01       Rocky Cavaltone  0.990   0.70   OK
02       Mittens Brisk    0.990   0.70   OK
02       NARRATOR         0.987   0.70   OK
02       Rocky Cavaltone  0.993   0.70   OK
03       Mittens Brisk    0.991   0.70   OK
03       NARRATOR         0.992   0.70   OK
03       Rocky Cavaltone  0.983   0.70   OK

reference versions:
  Mittens Brisk:    v001 181.0s wav=c9f07890843d16a0
  NARRATOR:         v001 181.0s wav=1b314ec3a3e3f3db
  Rocky Cavaltone:  v001 181.0s wav=4a9891ef539ed238
references unchanged after render: True
problems: []
```

Each chapter is one scene, one engine pass, three speakers, rendered once per
chapter — no draw selection, no per-character stitching. The same character stays
0.983–0.993 against its own reference across all three chapters.

Re-render check (acceptance #4): rendering chapter 1 twice into separate output
directories produced byte-identical chapter WAVs and a re-render similarity of
1.0 — the deterministic engine delivers the stronger form of the determinism
requirement.

## 3. Demo book — Muzzle and Marrow

The existing demo book predates clone-lock. Its five voices come from the old
freeze manifest (12–14 s single-take references, approval recorded as "user
directive … (no listening pass)"), which does not satisfy this workflow.

```
python tools/audio/clone_lock.py validate demo-books/muzzle-and-marrow

   - Mittens Brisk      UNFROZEN (no reference)
   - NARRATOR           UNFROZEN (no reference)
   - Rocky Cavaltone    UNFROZEN (no reference)
   - Tallow             UNFROZEN (no reference)
   - Teasel             UNFROZEN (no reference)
```

Rendering it is refused, as designed:

```
python tools/audio/render-book.py demo-books/muzzle-and-marrow --chapter 1 --verifier campplus

render-book: REFUSED — no frozen golden reference for character(s): 'Mittens Brisk',
'NARRATOR', 'Rocky Cavaltone', 'Tallow', 'Teasel'. Clone-lock never designs a voice
to fill the gap and never substitutes another character's voice. Run `design`,
listen, `approve`, then `freeze` for each of them.
exit 1
```

Regenerating the demo book under clone-lock needs, in order: `design` (per
character, from that character's book prose), a human listening pass, `approve`,
`freeze`, then `render-book.py`. That listening pass is deliberately not something
this change can perform.

## 4. Not exercised here

- **Ming-3.0-tts-tiny `podcast` engine.** Downloaded on 2026-10-29 (30 shards,
  16.7 GiB) and its release preflight passes (`tools/preflight_tiny.py`: config,
  tokenizer, decode and prompt contract all ok). It cannot execute on this machine:
  the checkpoint's Kimi-Delta layers need `fla-core`, which imports `triton`, and
  there is no Triton backend for Windows/AMD. Sequence of measurements:

  ```
  tiny preflight            ok  (16.7 GiB, transformers==4.46.3, no fla needed at
                                 preflight time)
  tiny load, CPU            ImportError: This checkpoint has Kimi-Delta
                                 linear-attention layers, which need fla-core
  pip install fla-core      ok  (fla-core 0.6.0)
  import fla                ModuleNotFoundError: No module named 'triton'
  pip install triton        no matching distribution (no Windows wheel)
  pip install triton-windows  cp312 abi3 wheel, CUDA backend only
  ```

  So the single-pass multi-speaker path is verified through the renderer
  contract with the deterministic backend, not against the production engine.
  With the tiny checkpoint absent or unloadable, a `ming3` scene render raises
  `MING3_TINY_INSTALL_HELP` rather than stitching — that refusal is the intended
  behaviour, and it is what a full-book render will report on this host.
- **ECAPA on production audio.** The drift numbers above come from the
  deterministic engine's voiceprint. The 0.70 floor's calibration note
  (`CLONE_LOCK.md`, step 6) comes from the 0.615–0.905 band recorded in
  `render-book.py`'s gate history; re-measure it on the first real clone-locked
  render and update `--drift-floor` if the measured band differs.
- **Listening.** No reference was approved here. The demo book's references are
  designed-but-unapproved until the user listens.
