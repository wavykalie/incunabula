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
| `tools/prose/deslop-check.sh` | `7462cde6e0dafacd` | density + slop caps, HARD / DEMOTED / REPORT tiers (Freeze 20 - A10a scoped to a report for mode: nonfiction, via conventions.py) |
| `tools/prose/check-uniformity.py` | `64a8ce620b389687` | U1–U6 cross-chapter rows (Freeze 19 - mode reader via conventions.py) |
| `tools/prose/check-drift.py` | `3e1a6b33fbafc5b5` | voice drift, size-dependent floor (Freeze 2 - Spearman tie fix) |
| `tools/prose/check-arc.py` | `f2059aec8a9580cc` | A1 gate; A2–A4 report-only |
| `tools/prose/check-surplus.py` | `7107a75155e8ffb5` | S1–S4, report-only (Freeze 19 - mode reader via conventions.py) |
| `tools/prose/check-recoverable.py` | `591c61560d8c53b3` | tic × dialogue enrichment, report-only |
| `tools/prose/check-errata.py` | `e9724056d7a3f18c` | protocol validator, reads no prose (Freeze 3 - floor 30) |
| `tools/prose/check-length.py` | `b0f77f89fba525ba` | declared-length row `L1` (Freeze 2 - added after the sons-of-heaven-v2 run exposed the deletion incentive; Freeze 8 - exit 3 for ungoverned) |
| `tools/prose/check-names.py` | `b09d89d8ca4b7765` | cross-book cast-name collisions + default-name filter, reads no prose (Freeze 4 - added after the author found `Priya` in two books; Freeze 21 - nonfiction case via `conventions.py`) |
| `tools/prose/calibration/NAME_FREQUENCY.tsv` | `f17e837f6f2ae0a5` | the name-frequency data `check-names.py` reads (Freeze 4) |
| `tools/prose/calibration/NAME_FREQUENCY.md` | `75f6fa0dae36f327` | provenance + the tier reasoning; frozen because it states what the tiers mean (Freeze 4) |
| `tools/prose/validate-controls.sh` | `4d559c43529c6a02` | the controls (Freeze 10; was `e940b825763c2281` at Freeze 9; Freeze 12 - name only; Freeze 13 - controls 13-16; Freeze 20 - control 17, NF scope arms; Freeze 21 - controls 18-19, names case + A24 pin) |
| `tools/prose/check-premise-distinct.py` | `852541b840442e94` | premise job+engine collision vs the author's own catalogue (Freeze 5) |
| `tools/prose/check-comps.py` | `9f47751a6a45aefa` | comp-title verification stamps; reads research/, not prose (Freeze 5) |
| `tools/prose/calibration/PREMISE_LEDGER.tsv` | `f4c03a83537f0270` | the spent-premise data `check-premise-distinct.py` reads (Freeze 5) |
| `tools/prose/check-narrative.py` | `3bf0bf46f318ab2c` | N1 debt (gates) / N2 beat repetition / N3 scene function / N4 ledger conformance (gates); reads no prose — the contract row, L1's class (re-keyed at the second update and Freezes 14–15; see below) |
| `tools/prose/check-figurative.py` | `394cd0e402a7f8b9` | G1/G2 figurative pile-up reporter; report-only (re-keyed at the fourth update) |
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

### Change recorded 2026-10-15 — de-identification. No measurement moved.

The instruments' comments and one data file named the books of the project this
instrument was extracted from. A public copy of the tools should not carry them, so every
identifier was replaced with a neutral label: the two validation books keep their numbers
(`validation 1`, `validation 2`), the nonfiction book is `the nonfiction fixture`, the
demo book is `the demo book`, and a book slug was replaced by a description of what the
row measured.

Every changed line in the Python and shell files is a comment or a docstring line. No
regex, cap, threshold, arithmetic or control assertion was touched, and the eight rows
re-keyed above are the fingerprints of that text-only edit.

`tools/prose/calibration/PREMISE_LEDGER.tsv` also lost its seeded rows. They were the
premises of the author's own unpublished books, and a public template should not carry
them. The file now documents its own format and ships empty. Nothing was destroyed: the
seed is kept outside the public tree, and `check-premise-distinct.py` already refuses an
empty ledger with exit 2, so an empty file cannot read as a pass.

Three files outside the hash manifest were de-identified in the same pass: the same prose
in `calibration/CALIBRATION.md`, one archived-tree path named in `skills/rewrite/SKILL.md`,
and the hard-coded corpus path in `calibration/measure-pd-corpus.py`. That last one is a
behaviour change, not a text change: the script now requires its corpus directory and
exits 2 with a message when it gets none, because a path that points at one machine's
directory is a broken argument on every other machine.

**Evidence at the time of the change.** `bash tools/prose/validate-controls.sh` ran
19/19 controls and passed every one that needs only the shipped fixtures; it exits 2
(PARTIAL) because no calibration corpus is installed on this machine, which is that
suite's documented state and not a result of this change. The five changed Python files
compile. `bash -n` passes on both shell files. That is evidence the harness still detects
bad output. It is **not** evidence that the caps still match published prose: that needs
`HUMAN_CORPUS` pointed at reference text, and it was equally unverified before this
change.

### Change recorded 2026-10-15 — `check-eval.py` is enforcement, not a gate.

`tools/prose/check-eval.py` was added beside the instruments. It is **not** a gate and
gets no manifest row: it enforces rules that already exist — the anti-inflation section
of the engine's contract and the evaluator protocol (every score cites a passage; no
dimension moves more than +0.5 per revision cycle without textual evidence; the floor is
the minimum of the seven dimensions; self-evaluation carries a measured −0.8 bias). It
reads no prose, measures nothing new, and fails bookkeeping, never a manuscript. The
self-evaluation calibration is applied in the tool's own arithmetic, so no agent is asked
to subtract a bias from its own score.

It is the same exemption class as `check-pass-evidence.py`: make-ready hygiene around the
instrument. Its entry here exists so the next reader does not mistake it for a
unfrozen gate — a check that enforces an existing rule is not a change to what any gate
asserts. The rules it enforces predate it and did not move.

### Change recorded 2026-10-15 — `check-waivers.py` is enforcement, not a gate.

`tools/prose/check-waivers.py` was added beside the instruments. It is **not** a gate and
gets no manifest row: it enforces rules that already exist — the composing review gate's
"fixed or waived in writing", and the standing rule that a recurring waiver is itself the
pattern ("reproducing the same exemption across books is itself the pattern this check
exists to catch", `check-uniformity.py`; "a recurring waiver is itself the pattern", the
maintenance gate). It reads no manuscript prose, measures nothing new, and fails
bookkeeping: the same rule waived in more than three consecutive chapters of one book's
`maintenance/WAIVERS.md` (N=3 default, documented in the tool, overridable). The ledger is
appended by the phase runner's `--waive` command, so a waiver is one declaration in one
auditable home instead of a sentence in a per-chapter report. It clears no gate, honors no
waiver, and no threshold moved.

It is the same exemption class as `check-pass-evidence.py`: make-ready hygiene around the
instrument. Its entry here exists so the next reader does not mistake it for an unfrozen
gate — a check that enforces an existing rule is not a change to what any gate asserts.
The rules it enforces predate it and did not move.

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
`U4` to the market gate. A book that declares `positioning: "nonfiction"` is scoped
this way.

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

**One change has been made to this project's copy**, on 2026-10-15, and it is recorded
above this heading in the manifest region: de-identification of the instruments' own
comments. It moved no measurement.

Two rules govern the recording, and both exist because the opposite produced a false
green light somewhere: a change is recorded *in the manifest region*, above the first
`## Freeze` heading, or it is frozen in fact and unchecked in fact; and a change that
moves a threshold needs a **named corpus**, because a threshold re-derived from six
books somebody liked has laundered a period confound into a permanent constant.
