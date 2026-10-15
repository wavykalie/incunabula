# Gate freeze

**Frozen:** the shipped instrument. `bash tools/prose/verify-freeze.sh` is the check:
`FREEZE HOLDS` means the tools below are byte-identical to the ones recorded here.

A book generated against these gates is a test against a *known instrument*. If a gate
changes afterwards, the freeze is what tells you the book was not tested against the thing
you are now looking at. Without it, a re-derived floor silently rewrites what a
generation run was evidence for — which is exactly what happened to `U1` earlier today,
when its published band turned out to come from a translated light novel.

## This file in plain words

**What a gate is.** A gate is an automatic check that reads your book and can fail it.
Three matter most: one checks the prose — each chapter and the whole book — one checks the shape of
the story, one checks the project's bookkeeping. The pipeline will not move past a
failed gate. Full dictionary: `INCUNABULA_LEXICON.md`.

**What a freeze is.** When the checks were found trustworthy, their files were
fingerprinted and the fingerprints written into the manifest below. A *freeze* is that
locked state. From then on, any change to a check must be logged in this file with a
date and a reason. A book keeps the freeze it was written under, so every result can be
traced back to the exact tool that produced it.

**Why all the hashes.** A hash is a file's fingerprint: change one character anywhere
and it changes completely. Comparing hashes proves the check that ran on your book is
byte-identical to the one recorded here. Run `bash tools/prose/verify-freeze.sh`:
`FREEZE HOLDS` is the good answer, `CHANGED` means a result from before the edit no
longer applies.

**What this file is for.** Most of it is the historical record — the evidence for why
each number is what it is, written for whoever changes a check next. The guide and the
table below are the parts for a first read. After them: the manifest is the list of
locked tools, and each entry underneath tells the story of one change.

## Manifest (FREEZE 4 - current)

| file | sha256 (first 16) | role |
|---|---|---|
| `tools/prose/deslop-check.sh` | `35ed380c20db520e` | density + slop caps, HARD / DEMOTED / REPORT tiers (Freeze 20 - A10a scoped to a report for mode: nonfiction, via conventions.py) |
| `tools/prose/check-uniformity.py` | `9aa47f622e7ea61d` | U1–U6 cross-chapter rows (Freeze 19 - mode reader via conventions.py) |
| `tools/prose/check-drift.py` | `814ca33e9e684ee7` | voice drift, size-dependent floor (Freeze 2 - Spearman tie fix) |
| `tools/prose/check-arc.py` | `f2059aec8a9580cc` | A1 gate; A2–A4 report-only |
| `tools/prose/check-surplus.py` | `7107a75155e8ffb5` | S1–S4, report-only (Freeze 19 - mode reader via conventions.py) |
| `tools/prose/check-recoverable.py` | `591c61560d8c53b3` | tic × dialogue enrichment, report-only |
| `tools/prose/check-errata.py` | `e9724056d7a3f18c` | protocol validator, reads no prose (Freeze 3 - floor 30) |
| `tools/prose/check-length.py` | `6dd9d862d275bff3` | declared-length row `L1` (Freeze 2 - added after the sons-of-heaven-v2 run exposed the deletion incentive; Freeze 8 - exit 3 for ungoverned) |
| `tools/prose/check-names.py` | `f5f169b0704e6e46` | cross-book cast-name collisions + default-name filter, reads no prose (Freeze 4 - added after the author found `Priya` in two books; Freeze 21 - nonfiction case via `conventions.py`) |
| `tools/prose/calibration/NAME_FREQUENCY.tsv` | `f17e837f6f2ae0a5` | the name-frequency data `check-names.py` reads (Freeze 4) |
| `tools/prose/calibration/NAME_FREQUENCY.md` | `75f6fa0dae36f327` | provenance + the tier reasoning; frozen because it states what the tiers mean (Freeze 4) |
| `tools/prose/validate-controls.sh` | `b3346a394925788e` | the controls (Freeze 10; was `e940b825763c2281` at Freeze 9; Freeze 12 - name only; Freeze 13 - controls 13-16; Freeze 20 - control 17, NF scope arms; Freeze 21 - controls 18-19, names case + A24 pin) |
| `tools/prose/check-premise-distinct.py` | `852541b840442e94` | premise job+engine collision vs the author's own catalogue (Freeze 5) |
| `tools/prose/check-comps.py` | `9f47751a6a45aefa` | comp-title verification stamps; reads research/, not prose (Freeze 5) |
| `tools/prose/calibration/PREMISE_LEDGER.tsv` | `1751102150c3ad6b` | the spent-premise data `check-premise-distinct.py` reads (Freeze 5) |
| `tools/prose/check-narrative.py` | `3bf0bf46f318ab2c` | N1 debt (gates) / N2 beat repetition / N3 scene function / N4 ledger conformance (gates); reads no prose — the contract row, L1's class (re-keyed at the second update and Freezes 14–15; see below) |
| `tools/prose/check-figurative.py` | `53962ce04c430d4f` | G1/G2 figurative pile-up reporter; report-only (re-keyed at the fourth update) |
| `tools/prose/check-dialogue-tags.py` | `b646cff207ef723f` | V1/V2 per-character speech-tag register reporter; report-only (re-keyed at the second, fourth and Freeze 16 updates) |
| `tools/prose/check-quantities.py` | `4cc4a538dde7309e` | Q1–Q4 quantity extraction, spread, sanity notes, counted-noun conflicts; report-only (re-keyed at the third and fourth updates) |
Manifest completeness, 2026-10-13: the seven rows above for
The narrative and research checks — `check-premise-distinct.py`, `check-comps.py`,
`calibration/PREMISE_LEDGER.tsv`, `check-narrative.py`, `check-figurative.py`,
`check-dialogue-tags.py` and `check-quantities.py` — are in the manifest with the
hashes of the freeze that introduced them. A frozen row recorded *outside* the
manifest region is frozen in fact and unchecked in fact, which is how several of
them went unchecked for days after they joined the set; `verify-freeze.sh` now
fails on any frozen row the manifest region does not carry, so a row recorded in
the wrong place cannot hide again.

Also frozen, because they change what the gates *see* rather than what they assert:

- `tools/prose/calibration/CALIBRATION.md` — every measurement behind the numbers
- `PRINTERS_COPY.md` — the standing brief the gates answer to
- `ERRATA.md` — the ledger of corrections and observations
- `skills/` — the prose skills that generate the text under test

Those four are deliberately described without counts. The registries' own sizes live in
the files themselves, and a second copy here is a second thing to keep true — which is
exactly the drift `tools/prune-stale.py` exists to catch.

## Load-bearing thresholds at this freeze

How to read the table: each row is one measurement a gate enforces, with its current
value. "fail < 22%, warn < 28%" means the row fails the book below 22% and warns below
28%; "report-only" and "advisory" rows print findings but cannot fail anything.
"derived from" records the published prose that produced the number.

| row | value | derived from |
|---|---|---|
| `U1` chapter-length CV | fail < 22%, warn < 28% | worst of 6 English fiction volumes = 33.4% |
| `U2` sentence-length spread | fail < 3.0, warn < 4.0 | published min 4.32 |
| `U3` coda share | fail > 25% of chapters | 0 of 50 published chapters |
| `U4` one-line paragraph share | **advisory by default** | 59% of 140 PD novels fail it |
| `U5` paragraph-length CV | fail < 55%, warn < 75% | 0 of 140 PD novels fail it |
| `U6` signature-frame spread | fail > 40% of chapters | worst published volume 23% |
| `D1` em dash | **report-only** | control sits at 0.00/1k; cap clears 14% of published chapters |
| `D2` rule of three | **report-only** | cap clears 18.6% of published chapters |
| `D3` adverb density | enforced | clears every published chapter; detector value unproven |
| `A25` antithesis | fail > 3/2000 | 1.5× the worst published chapter (0.93/1k) |
| `A1` reversals per bin | size-dependent, 0.35 at ≤2 windows | 0 of 40 published novel means fall below |
| drift | size-dependent, 3.41 at 4 ch → 1.40 at 20+ | worst published book at each chapter count |

**Convention-scoped rows.** A book declaring `mode: nonfiction` (or the legacy
`positioning: nonfiction`) carries `U1`, `U4`
and `U5` as advisory, and deslop row `A10a` as reported-not-failed (Freeze 20;
`NF_SCOPED` in conventions.py). A book declaring `paragraph_convention:
commercial-dialogue` holds
`U4` to the market gate. `Sons of Heaven, Students of Dust` declares
`positioning: "nonfiction"`.

## What a pass does and does not mean

- A green run means the prose cleared the rows listed above. It does **not** mean the
  gates were all able to see the book's actual weaknesses — `A1` misses the AI control
  entirely, `D1` reads 0.00/1k on it, and the drift floor is known to miss roughly one
  real voice change in eight.
- Six of the rows are advisory or report-only, so a green run is partly a statement that
  nothing was *gated*, not that nothing was found.
- The gates are calibrated on 1813–1905 English prose. Nothing commercially recent is in
  the corpus, and a stylometric finding about period prose measures the period.


---

## How a change is recorded

The manifest above is the locked set. From here on, any change to a gate is appended to
this file with a **date**, a **reason**, and the **new fingerprint** — which is why the
history of a long-running project is the bulk of this file. Freeze numbers cited by the
skills (`Freeze 13`, `Freeze 19`) refer to entries in the history of the project this
instrument was extracted from; a project's own numbering starts at its own first change.

**No changes have been made to this project's copy yet.**

Two rules govern the recording, and both exist because the opposite produced a false
green light somewhere: a change is recorded *in the manifest region*, above the first
`## Freeze` heading, or it is frozen in fact and unchecked in fact; and a change that
moves a threshold needs a **named corpus**, because a threshold re-derived from six
books somebody liked has laundered a period confound into a permanent constant.
