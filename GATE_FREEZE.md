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
| `tools/prose/deslop-check.sh` | `09b242725673f331` | density + slop caps, HARD / DEMOTED / REPORT tiers (Freeze 20 - A10a scoped to a report for mode: nonfiction, via conventions.py; 2026-11-06 - P1 floor; 2026-11-07 - P1 and A25 take the 667-word document floor, below which both report UNMEASURED; Freeze 26 - A27 report row, the protected comparison; Freeze 27 - A28 and A30 report rows, the withheld-speech and hand-placement beats) |
| `tools/prose/check-world.py` | `8c388d1e6e58a699` | world-physics lexicon gate: reads <book>/WORLD_RULES.txt and fails a chapter that puts a ground vehicle, a wheeled cart, a road fuel or a rubber tyre in a city that carries on backs and flies its freight (Freeze 22 - added 2026-11-09 after two ground-vehicle leaks reached drafted chapters and were caught only by reading) |
| `tools/prose/check-diction.py` | `98503511d2abfa43` | book-declared lexical register gate: reads <book>/DICTION_RULES.txt and fails a chapter that dates the page, or that lets the book's modern vocabulary fall below the floor it declared (Freeze 24 - added 2026-11-14 after a 130,003-word book passed every cap while reading like 1880: its direction file called the city Victorian and its world rules removed every modern object without putting one back) |
| `tools/prose/check-uniformity.py` | `3bd21d61113564f2` | U1–U6 cross-chapter rows (Freeze 19 - mode reader via conventions.py) |
| `tools/prose/check-drift.py` | `3e1a6b33fbafc5b5` | voice drift, size-dependent floor (Freeze 2 - Spearman tie fix) |
| `tools/prose/check-arc.py` | `f2059aec8a9580cc` | A1 gate; A2–A4 report-only |
| `tools/prose/check-surplus.py` | `7107a75155e8ffb5` | S1–S4, report-only (Freeze 19 - mode reader via conventions.py) |
| `tools/prose/check-recoverable.py` | `591c61560d8c53b3` | tic × dialogue enrichment, report-only |
| `tools/prose/check-errata.py` | `9ec8ad323196a202` | protocol validator, reads no prose (Freeze 3 - floor 30) |
| `tools/prose/check-length.py` | `b0f77f89fba525ba` | declared-length row `L1` (Freeze 2 - added after the sons-of-heaven-v2 run exposed the deletion incentive; Freeze 8 - exit 3 for ungoverned) |
| `tools/prose/check-names.py` | `4c8f8dbdf470514a` | cross-book cast-name collisions + default-name filter, reads no prose (Freeze 4 - added after the author found `Priya` in two books; Freeze 21 - nonfiction case via `conventions.py`; Freeze 25 - reads inline flow-map cast entries and `handle + roster number` names) |
| `tools/prose/calibration/NAME_FREQUENCY.tsv` | `f17e837f6f2ae0a5` | the name-frequency data `check-names.py` reads (Freeze 4) |
| `tools/prose/calibration/NAME_FREQUENCY.md` | `75f6fa0dae36f327` | provenance + the tier reasoning; frozen because it states what the tiers mean (Freeze 4) |
| `tools/prose/validate-controls.sh` | `6b005f4cda33eecc` | the controls (Freeze 10; was `e940b825763c2281` at Freeze 9; Freeze 12 - name only; Freeze 13 - controls 13-16; Freeze 20 - control 17, NF scope arms; Freeze 21 - controls 18-19, names case + A24 pin) |
| `tools/prose/check-premise-distinct.py` | `852541b840442e94` | premise job+engine collision vs the author's own catalogue (Freeze 5) |
| `tools/prose/check-comps.py` | `9f47751a6a45aefa` | comp-title verification stamps; reads research/, not prose (Freeze 5) |
| `tools/prose/calibration/PREMISE_LEDGER.tsv` | `f4c03a83537f0270` | the spent-premise data `check-premise-distinct.py` reads (Freeze 5) |
| `tools/prose/check-narrative.py` | `3bf0bf46f318ab2c` | N1 debt (gates) / N2 beat repetition / N3 scene function / N4 ledger conformance (gates); reads no prose — the contract row, L1's class (re-keyed at the second update and Freezes 14–15; see below) |
| `tools/prose/check-figurative.py` | `394cd0e402a7f8b9` | G1/G2 figurative pile-up reporter; report-only (re-keyed at the fourth update) |
| `tools/prose/check-dialogue-tags.py` | `560f55fbbfbde7a8` | V1/V2 per-character speech-tag register reporter; report-only (re-keyed at the second, fourth and Freeze 16 updates) |
| `tools/prose/check-quantities.py` | `4cc4a538dde7309e` | Q1–Q4 quantity extraction, spread, sanity notes, counted-noun conflicts; report-only (re-keyed at the third and fourth updates) |
| `tools/prose/check-monotony.py` | `3d0e83da2b8b195d` | M1-M4 monotony inside the sentences: repeated five-grams, subject-opening share, negation density, texture density. **Calibrated 2026-11-11** against the six published English volumes; M1 is a share of chapters, M2-M4 are advisory bands (Freeze 23, revision 2) |
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
| `A25` antithesis | fail > 3/2000, **UNMEASURED below 667 words** | 1.5× the worst published chapter (0.93/1k); 410 published documents, 0 failures |
| `P1` anaphora | fail > 6/1000 or >15% of sentences, **UNMEASURED below 667 words** | 45 of 281 published documents under 667 fail the rate; 2 of 129 above 667 (5 and 9 instances) |
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

### Change recorded 2026-11-06 — V3 gates on a measured corpus; four rejected measures enter the registry

`check-dialogue-tags.py` gains `V3`: the whole-book breath-family share of tagged spans,
failing above 0.107 and warning above 0.082. The corpus is 167 public-domain English
novels (stratum C-dist-2 of `tools/prose/study`, frozen extractor v2, disjoint from the
140 novels in `calibration/`), where 5% of books exceed the fail line; the pipeline's
fifteen books run at median 0.168 and 11 of 15 exceed it, against 6 of 20 naive drafts.
Below 40 tagged spans the row is UNMEASURED and gates nothing, so a dialogue-sparse book
cannot be failed for a rate it cannot support.

`check-uniformity.py` moves U5's warn line 75 -> 73.7, that stratum's p10, and prints its
basis (12 of 15 pipeline books, 0 of 20 naive). The fail line stays 55: moving it to the
p10 would fail 26% of the human books, which is the U4 lesson arriving a second time.

`check-errata.py` raises `REJECTED_FLOOR` 30 -> 34 to carry the four measures the study
disproved — the AI-term cap, the weather-opener gate, the name-reuse threshold and
opening similarity — each recorded with its arm counts in `PRINTERS_COPY.md` §4.
`validate-controls.sh` keeps its report-row control and now states why the tag tool's V3
cannot fail that fixture. `tools/run-gates.sh` moves the tag row from the report class to
the prose class, so a V3 failure blocks the book.

Evidence at the time of the change: `check-dialogue-tags.py` fails the study's B-01 at
0.136 (95 of 699 spans) and exits 1; `check-uniformity.py` warns B-01 at U5 63%;
`check-errata.py` reports the registry at 34 and the protocol intact; the three Python
files compile; both changed shell files pass `bash -n`. The re-keys above are for these
edits only — no other threshold moved.

### Change recorded 2026-11-06 — P1 stops judging a document shorter than its own denominator

`deslop-check.sh` gains a floor under `P1`: below `ceil(OPEN_PER_W / OPEN_PER_N)` = **167
words** the row reports `UNMEASURED` instead of failing, and the file exits 0 printing
`RESULT: UNMEASURED`. `tools/run-gates.sh` maps that to a new `UNMEASURED` status which
counts toward `unclear`, so it blocks a phase claim exactly like NOT RUN and is never
read as a pass. Both files pass `bash -n`.

**Why.** Scoping the prose gate per document layer for a `structure: layered` book put
P1 on documents of 78, 96, 131 and 132 words. The cap allows 6 occurrences per 1,000
words, so those documents allow 0.47 to 0.79 of an occurrence: the *first* repeated
opener fails, and the only way to pass is to lengthen the document. Two of the four
failures were arithmetic of exactly that kind. The other two were real repetition
('the garden' x4 in 540 words, 'I have' x4 in 650) and were fixed in the prose, not
accommodated by the instrument.

**No threshold moved.** Every cap, numerator and denominator is unchanged, and every
file at or above 167 words computes exactly what it computed before. The floor is taken
from the row's own constants, so a future change to `OPEN_PER_N` moves it rather than
leaving a stale number behind.

**Named basis, and its limit.** The derivation is arithmetic from P1's existing cap,
itself calibrated on 175,144 words of published narrative. No corpus of *document
layers* exists and none is claimed here: the entry does not assert that 167 words is the
right size for a document, only that below it the row cannot judge one. **Domain check:**
no chapter file in the catalogue is under 167 words except `test-books/_audio-smoke`
(102 and 126 words, an audio fixture outside the prose gate), so no finished book's
verdict can change — a proof by domain rather than a sample.

**Evidence at the time of the change.** `validate-controls.sh` with the shipped fixtures
exits 2 (PARTIAL): the harness-detects-bad-output arm passes, the human-corpus arm needs
`HUMAN_CORPUS` and remains unverified in that direction, exactly as the 2026-10-15 entry
records. The 638-file reference corpus in `calibration/corpus/` is too slow to serve as a
pre-commit control and was not used to gate this edit; that is a limitation of the
evidence, not a pass. `check-dialogue-tags.py` and the report-only rows are untouched.
The re-key above is for this edit only:
`deslop-check.sh` `7462cde6e0dafacd` -> `951d50fa406043ab`.

### Change recorded 2026-11-06, same day — the P1 floor keeps the scale-free test

The floor above suppressed the whole row below 167 words, including the **share** test,
which has no denominator and judges a short document perfectly well. A 150-word document
repeating one opener in four sentences is 20% of sentences and would have been recorded
UNMEASURED, which is wrong: the rate is unusable there, the share is not.

Below the floor the branch now applies the share test (fail above `OPEN_SHARE_PCT` = 15% of
sentences) and reports UNMEASURED only when that test is silent too. Above the floor nothing
changed: rate OR share, exactly as before.

Evidence, on synthetic probe documents with real sentence counts: 144 words, 10 sentences,
one repeat (10% share) -> UNMEASURED; 121 words, 3 of 10 sentences (30% share) -> FAIL on the
share test; 318 words above the floor with one repeat (3.1/1k) -> PASS on the rate. An earlier
draft of this entry quoted a probe whose sentences carried no full stops, which made "share of
sentences" meaningless; the figures above are the rerun, and the bad figures are recorded here
rather than quietly replaced.
The eight per-layer scans are unchanged by the refinement: 4 PASS, 4 UNMEASURED, and the
four UNMEASURED rows sit at 5.3% and 10.0% share, both under the 15% test.

**Fingerprint supersedes the one in the entry above**, which is left as written because a
dated entry records what was done on its date: `deslop-check.sh` `951d50fa406043ab` -> `dfaa5a58b68dd6fd`.

### Change recorded 2026-11-07 — both rate rows take the 667-word document floor; the widened corpus overturns the 44-document zero

`deslop-check.sh` now reports both `P1` and `A25` as UNMEASURED below **667 words**. `P1`'s
floor moves from 167 (the arithmetic minimum for one occurrence) to 667; the share test is
not applied below 667 either. A25's floor is `ceil(2,000/3)` = 667, from its own fail
denominator. `tools/run-gates.sh` already maps `RESULT: UNMEASURED` to `unclear`.

**The widened corpus.** `fetch-document-layers.py` now stages seven public-domain epistolary
novels at their own document boundaries - Evelina (41 documents), Frankenstein (3), Humphry
Clinker (40), Pamela (20), Clarissa vol. 1 (20), The Coquette (67), Emily Montague (219) -
**410 documents**: 23 under 167 words, 124 at 167-400, 134 at 400-667 and 129 at 667-1,500.

**What it measured, and what it overturns.** Under the 167-word floor, **47 of 410 documents
fail P1** (Emily Montague 33, The Coquette 11, Humphry Clinker 3), 45 of them under 667
words. The earlier "0 P1 failures in 44 documents" did not generalize: 41 of those 44 were
Evelina, whose letters happen not to repeat an opener, while Emily Montague's letters open
"I have"/"I am" as a matter of form. The share test failed 22 of the same human documents, so
it is not a scale-free rescue below chapter size. Above 667, P1 fails **2 of 129** documents
(1.6%): 1,303 and 1,434 words, carrying 5 and 9 instances. Those are repetition the row is
entitled to name. With the floor in place the human corpus has **2 P1 failures, 0 A25
failures, and 1 A25 UNMEASURED** (a 264-word document with one antithesis).

**The floor is not an amnesty.** The two surviving P1 failures and the 18 documents that fail
another row are unchanged. What the floor stops is a rate rule failing a published letter for
opening two sentences the same way at 176 words, which is what 45 of 281 human documents did.

**Probes.** A 285-word published letter that failed `P1 "i am" x2 (10.5%)` now reports
`UNMEASURED at 285 words` and exits 0; a 1,303-word published letter still fails
`P1 "it is" x5 (16.7%)` and exits 1. On a 656-word letter with one antithesis appended: at
666 words the old A25 row reads `FAIL 1.50 per 1k` and exits 1, the new row reads
`UNMEASURED at 666 words` and exits 0; at 667 words both pass; with two antitheses at 678
words both fail `2.95 per 1k`.

**Evidence at the time of the change.** All 410 documents were re-scanned through the frozen
scanner after the edit: **20 failing files, 2 P1, 0 A25, 265 UNMEASURED**. The AI-written
control (`study/books/C-dist2-094`, 32 chapters) still fails **12 of 32** (D3, A11a, A4, A17),
so discrimination is intact. `bash -n` passes. The shipped fingerprint supersedes `dfaa5a58b68dd6fd`;
the intermediate probe builds were not used for a generation run and are not recorded as
freezes. The re-key is `dfaa5a58b68dd6fd` -> `e63d9ccda4f03b10`; `verify-freeze.sh` is re-run
below.

### Change recorded 2026-11-09 - a new gate: `check-world.py` (Freeze 22)

Added because the same defect reached the page twice. Two sweeps of the drafted chapters of
the parts still warm found ground vehicles the world forbids: a delivery truck, two vans, four
trucks, a tram, a diesel exhaust and a hand-truck in prose that had already passed every cap in
the deslop gate. The slop gate measures how prose is written and cannot see what it asserts, so a
chapter can be clean and still put a lorry in a city whose streets carry nothing heavier than a
barrow.

This gate closes that class: the lexicon is book-local, one rule per line, and a book with no
lexicon exits 2 rather than passing. It is wired into the phase-4 gate set beside `deslop`, which
means a chapter cannot be counted as drafted while contradicting its own artifacts.

Evidence at the time of the change: positive control (a plant line naming a truck, diesel and
tyres) fails with three rule hits and exit 1; negative control (a barrow, iron rims, coal smoke)
passes with exit 0; a book directory with no rules file exits 2; and the four drafted chapters of
the parts still warm pass after the prose was corrected. The tool measures no style, holds no caps,
and cannot be mistaken for a change to an existing gate: nothing already in the manifest moved, and
`verify-freeze.sh` reports FREEZE HOLDS with the new row in place.

### Change recorded 2026-11-11 - a new gate: `check-monotony.py`, calibrated the same day (Freeze 23)

Added because a book passed every prose row in this directory while cycling a template
inside its sentences: 597 "did not" in 130,000 words, nine uses of "Tap Two looked at the"
across seven chapters, eight of "the man said, his voice" across four. `check-uniformity.py`
compares chapters to each other and cannot see any of that; `deslop-check.sh` counts
per-chapter rates and each of those is a low rate in every chapter. Both instruments were
working as designed and the defect sat between them.

Four rows: M1 repeated five-grams (six or more uses across four or more chapters), M2
subject-opening share, M3 "did not" per 10k, M4 texture density. M4 subtracts the determiner
and partitive senses of *flat*, because in the test book that word is the apartment and raw
counting made the row report 349 texture uses of a noun - an instrument error found by using
the instrument, fixed in the row with its reason as a comment.

**The thresholds are provisional and the row says so in its own docstring.** They sit just
above one book's post-repair baseline (M1 6, M2 0.34, M3 45, M4 150) and are not derived
from a named corpus. By this file's own rule a threshold without a named corpus is not a
measurement, and this entry does not claim one. The calibration TODO is to run the row over
the same six English fiction volumes `check-uniformity.py` was calibrated on; until that is
done the row can lock in a repair but cannot say what published prose reads like.

It is wired into phases 3.8 and 4 in `tools/phase-map.yaml`, and into the prose class of
`tools/run-gates.sh`, for the reason the 3.8 row exists: a gate that is not wired is not run,
and a gate that is not run cannot be calibrated against books as they are actually drafted.
`run-gates.sh` carries its own row list, so wiring the phase map alone would have left the
row unrun in the direct suite - which is the same defect this entry is about, one layer up.

Evidence at the time of the change. On the test book, before the prose repair the row exited
1 with M1 six runs (worst 9), M3 42.9 and M4 135.3; after the repair it exits 0 with M1 0,
M2 29.3%, M3 42.8 and M4 135.2, two warnings standing. A first automatic pass was reverted
after the row showed it had created a new eight-chapter cluster ("kept his head still") and
left a sentence reading "kept his head still toward the door"; the thirty hand edits that
replaced it are the only prose changes in that report. `check-world.py` exits 0,
`check-length.py` exits 4 (the book still declares `status: in_progress`), and
`verify-freeze.sh` reports FREEZE HOLDS with the new row in place.

### Revision 2, 2026-11-11 — the provisional monotony thresholds were calibrated, and one row changed shape

The entry above shipped `check-monotony.py` with thresholds set just above one book's
post-pass baseline and labelled provisional. They were then calibrated the same day, by
`tools/prose/calibration/monotony-units.py`, which stages each of the six published English
fiction volumes `check-uniformity.py` uses as chapters and runs the **shipped** gate over
it — a threshold derived from a second implementation measures the second implementation.

What the six volumes measured:

    volume              chapters   M2 subj. openings   M3 "did not"/10k   M4 texture/10k
    Austen, P&P            61            8.3%               10.1               2.2
    Bronte, Jane Eyre      38            5.3%                7.0              15.7
    Bronte, Wuthering      33            8.9%                8.9               9.7
    Eliot, Middlemarch     86            9.0%                9.3               6.8
    Hardy, Tess            60           10.1%               13.0              14.0
    Stoker, Dracula        25            9.2%                n/a               6.9

**M1 changed shape, and that is the finding.** Its absolute test — a five-word run used six
times or more across four or more chapters — **failed five of the six published volumes**.
A count does not scale with book length: Middlemarch repeats one run twenty times across 86
chapters, and a rule that calls Middlemarch monotonous is measuring length, not prose. M1
now fails a run that appears in 30% or more of a book's chapters. Every published volume
passes at that share, and this book's original defect (one formula in 7 of 13 chapters,
54%) still fails it, so the row keeps the power it was built for.

**M2, M3 and M4 are printed against the band and are not enforced**, and each refusal is a
measurement rather than a preference:

- **M2** the corpus is 1813–1897, where periodic syntax suppresses subject openings. The
  measured band is 5.3–10.1%; a 1.5×-headroom line at 15% would fail most contemporary
  commercial fiction, and this project owns no modern corpus with which to check that.
- **M3** the corpus is contraction-free exactly as this book is (557 "did not" to four
  "didn't"), so the comparison is fair — and the book is 3.3× the worst volume. A fair
  comparison is not the same thing as a defect, and enforcement of a rate the voice
  contract declares as its own mode would be a gate punishing an author for their voice.
- **M4** the palette (gray, cold, heavy, dry) is this book's subject matter. Gating it
  would push the author off the word the book is about, which is the judgement U6 already
  recorded when it removed "Nobody X" from its frame list.

All six volumes now exit 0, and the book exits 0 with three warnings that state its
distance from published practice. The old pass was weaker than it looked: the negation
line was 45.0 against a measured worst of 13.0, so no book could have failed it. Removing a
line that could not fire is not a loosening of the gate; it is the gate saying what it
knows. Enforcement of M2–M4 waits on a modern commercial corpus, and that requirement is
recorded in the tool's docstring rather than in a comment nobody reads.

### Change recorded 2026-11-14 — a new gate: `check-diction.py` (Freeze 24)

Added because a finished 130,003-word book passed every row in this suite and still read
like 1880, and its author heard it before any tool did: *"Who says Washings, or shillings
or all these dated terms."*

The cause was not a missing cap. It was a rule that only subtracted. `WORLD_RULES.txt`
removed the van, the tyre, the fuel and the bus from that city, on a world history that
says freight flies and the ground carries what a back and a barrow can. Every rule was
correct and every rule removed something, and nothing put a noun back. With no modern
object permitted and no modern vocabulary required, the writer reached for the last nouns
that still fitted the permitted world, and the prose came out a hundred years older than
the city it described. The book's own direction file supplied the period - "A Victorian
port city that industrialised without the engine". Fourteen briefs in the same project
said "Nothing Victorian". None of them could fail anything.

`check-diction.py` reads `<book>/DICTION_RULES.txt` and has two row kinds, and the second
is the one the world gate could not express: `X` bans a word that dates the page, `R`
requires a word the book must keep, at a floor per 10,000 words. A book with no rules file
exits 2, the stance `check-world.py` already takes.

Evidence at the time of the change, on the book it was built for. The first run exited 1
with 34 hits in four classes, and the reading of those hits is the argument for the shape
of the rules: 13 "washing" (correct English - "a bag of washing"), 19 "chandler" and
"cooper" (correct port trades), 1 "on the parish" (a real 1834 institution), and 1
"halfpenny" in chapter 10 that the 2026-11-14 diction pass had missed. The three
false-positive classes were narrowed and the real coin was fixed; the gate now exits 0 with
R1 8.6/10k against a floor of 2.5, R2 4.2 against 1.4, R3 3.5 against 1.0.

**What the census found, which is not a gate result.** R3's word list was set from a count
of the thirteen chapters: radio 30, screen 5, steel 6, concrete 2, enamel 1, zinc 1 - and
plastic, photocopier, transistor, telephone, neon and lino at zero. The direction file says
the modern surface is "the only one on the page most of the time" and the prose does not do
that. The floor is set where the book is, not where the direction hoped; the gap is an open
craft finding, not a threshold, and it is recorded in `PRINTERS_COPY.md` section 5.

No existing cap, floor or threshold moved. The new tool is the only change to the
instrument.

### Correction recorded 2026-11-14 — a stale hash cell, not a changed gate

`verify-freeze.sh` reported `check-monotony.py` CHANGED during the Freeze 24 change: the
manifest cell held `5cd4b18586b77829` and the file hashes `3d0e83da2b8b195d`. The file was
not modified here. `git show HEAD:` and the working tree agree at `3d0e83da2b8b195d`, and
the only commit that touched the file is `04b0fc0` (2026-11-13), which is also the commit
that wrote the Freeze 23 revision-2 entry. The code does what that entry says - M1 is
enforced as a share of chapters, M2-M4 print as advisory - so the entry and the manifest's
own role text both describe the code that is on disk, and only the hash cell was left
behind.

This is the failure mode the freeze exists to catch, and it caught it: a gate changed under
a recorded hash and nothing noticed for a day. The repair is the cell, not the code, and it
is recorded here rather than silently overwritten. `verify-freeze.sh` now reports FREEZE
HOLDS across all twenty-two rows.

Worth adding to the freeze ritual: a change entry and a hash re-key are two edits, and
`verify-freeze.sh` is what proves both were made. The 2026-11-13 change made one.

### Change recorded 2026-11-14 - `check-names.py` reads the cast it was given (Freeze 25)

The gate was not wrong about anything it measured. It was blind to two forms of declaration
that two books in this tree actually use, and the blindness had a cost that looked like an
absence: `the-parts-still-warm` declares fifteen characters and the gate read all fifteen as
nothing, exited 2, and "no cast found" went into the suite as NOT RUN.

Two independent defects, and each one alone was enough:

1. Every entry in that book's `characters:` block is an inline flow map,
   `- { name: "Tap Two", role: "..." }`. `DECL_RE` anchors on `- name:` and never matched a
   single line. A probe with a control name proves the syntax and not the name was the
   problem: block style `- name: "Delphine Rusk"` harvested, and the same name in flow style
   harvested nothing.
2. The book names people by `<handle> <roster number>` - "Tap Two", "Rule Six", "Chump Four"
   does not occur but "Chit Four" does. Numerals sit in `STOP` because in prose a stray
   "Two" is junk, so `clean()` removed the half of the name that made it unique and the
   remainder - one bare token - was then correctly refused as a place or an object.

WHAT CHANGED
`FLOW_RE` reads `name:` / `canonical_name:` from inside a `{ ... }` mapping, so the two
declaration styles now read alike. `clean()` takes `keep_numerals` in declaration position
only, and a numeral is kept as a disambiguator, never as a surname: "Tap Two" contributes the
full name and the first name, and no surname, because "Two" is not a family. The same
permission covers the handle's first word when a numeral follows it, which is what reads
"Rule Six" - "Rule" is craft vocabulary in `STOP`.

WHAT DID NOT CHANGE
Exit codes, the severity ladder, and the refusal to read prose. A single bare token is still
not a person, so four of that book's cast remain unread by design: "Nemi", "Tava",
"Provision", "Ullage", and the job-named Doorman. The gate now reads 11 of 15, reports "cast:
10 first names", and passes; the four it cannot see are named in the book's own ledger note
rather than renamed to suit the instrument.

THE FIRST VERSION OF THIS CHANGE WAS WRONG, AND THE CONTROLS CAUGHT IT
It kept any `STOP` word when it arrived from an `name:` key. That promoted "The" out of
`name: "The Vell"`, `name: "The gauge"` and `name: "The fourth chamber"` - objects and places
in `marrow-light` and `muzzle-and-marrow` - and both books immediately failed with
`FIRST The: also a character in ...`. The permission is now numeral-adjacent only: "Rule Six"
is a person because a number follows the word, and "The Vell" is a place because nothing
does. Both books are back to exit 0 and `the-parts-still-warm` still reads 10 handles.

Evidence: `test-books/the-parts-still-warm/CANON_LEDGER.yaml` (15 declared characters, flow
style), the four harvest probes (block real name, block roster handle, block single handle,
flow real name), `validate-controls.sh` controls 18-19 (names case) passing, and the five
books' casts re-read after the narrowing - ashgrove 3/1, marrow-light 9/8, muzzle-and-marrow
8/8, tide-register 4/3, the-parts-still-warm 10/0.

No other hash in the manifest moved. The book's ledger note was corrected in the same change,
because it had recorded the gate's blindness as a permanent property.

### Change recorded 2026-11-14 — `check-agency.py` joins the suite as a report row; no manifest row, deliberately

`tools/prose/check-agency.py` is now a row in the report class of `tools/run-gates.sh`, beside
the figurative and quantity reporters. It gets **no manifest row above**, and that is a
decision rather than an omission: a report row cannot fail a book, so freezing it would assert
a threshold the tool does not hold. The manifest exists for the rows a book's verdict depends
on; this one contributes no verdict, only a list.

Two rows, printed per chapter with the sentence that carries them. `R1` object agency —
"The hall knows", "the city remembered", "the car waited" — is report-only on measurement,
not for want of one: 23 hits in 4,531,815 words of published prose, deliberate where they
occur (*the fire refused to burn*; *The city knows. It remembers.*), and the directory's 1.5×
cap lands at roughly 0.55/1k, a line every manuscript measured already clears. A cap there
would be a gate in name only, which is the D1/D2 failure this file has recorded twice. `R2`
motive by absence — "because it didn't need to be said" — is the zero-tolerance candidate:
0.00/1k across all six published registers against 0.04 on the demo book. That is ten hits,
which is a hypothesis, and promoting it is the freeze event. It will need a named corpus, a
cap and a hash, and that call is the author's.

**Why wire it at all.** The Freeze 23 entry's own lesson, one layer up: a gate that is not
wired is not run, and a row that is not run cannot be calibrated or corrected by anyone using
the suite. A report row earns its place only if it actually appears in a run.

**Evidence at the time of the change.** In the suite, `check-agency.py` reports exit 0 and
`REPORTED` on three books: ashgrove 0 observations, tide-register 0, the parts still warm 9 in
5 of 13 chapters. On the controls, a fixture built from the constructions the row names fires
7 observations and exits 0; a courtesy fixture ("You didn't have to", "He didn't need to
answer") and clean prose both exit 0 with nothing listed; an empty directory exits 1, so an
empty read is not reported as a pass. `bash -n` passes on `run-gates.sh`, whose row count
moves 22 → 23: the premise row is declared twice, once inside the ledger branch, so the
count is of declarations, not of rows in a run. 17 gate rows, unchanged, plus 5 report rows
(one of which, the premise row, is still one row in a given run). No other row's status moved on
the three books: the parts still warm is NOT CLEAR on the empty premise ledger exactly as
before, ashgrove fails `check-drift.py` and `check-length.py` (its own book-state rows, both
files untouched here), and `verify-freeze.sh` reports FREEZE HOLDS with the new row in place.

### Change recorded 2026-11-14 — `check-agency.py` R1 splits into R1a place agency and R1b object agency

The row was asked for as object agency. Run over every manuscript in this checkout — 18 books,
213 chapters, 517,822 words — it returned fifteen hits, and not one of them was an object:
`hall` ×5, `room` ×3, `town` ×2, `street` ×2, `ceiling`, `office`, `House`. Every carrier was
the setting. Counted as one number the row was reporting *object agency 15* about fifteen
places, which is the wrong answer to the question it was built for, and a reader had no way to
see that from the output.

R1 is now two rows over the same construction: **R1a place agency**, the setting given a mind
(*The hall waited.*), and **R1b object agency**, a discrete article given one (*The car waited,
idling at the curb.*). The lexicon splits at whether the noun can stand for the scene itself: a
wall is the room, so it goes in `PLACE`; a brick is a brick, so it goes in `THING`, and building
materials (timber, tile, wallpaper) sit with the things. The two lists are disjoint, so nothing
is counted twice and the totals still add up to the fifteen this row reported before.

**Why it matters beyond bookkeeping.** A place with a mind is the *genius loci*, and it has a
tradition behind it — Muir's *The city knows. It remembers.* is a published instance, and the
parts still warm's nine hits read as a chorus, not a tic. An object with a mind is a stranger
claim and materially rarer: zero in 517,822 words here, and the published instances are the
car-and-fire kind (*the car waited, idling at the curb*). The two do not deserve the same
reading, and a single count invited exactly that.

**Evidence at the time of the change.** `py_compile` passes. A fixture built to separate the
classes reads 2 place + 3 object + 1 motive-by-absence = 6 and exits 0; the constructions
fixture reads 4 + 1 + 2 = 7; the courtesy and clean fixtures read 0 with nothing listed; an
empty directory exits 1, so an empty read is still not a pass. The no-argument sweep over the
whole tree reads 18 manuscripts and reports **place 15, object 0, motive-by-absence 7**, exit 0
— the same 15 R1 hits and 7 R2 hits as before the split, which is the check that re-cutting the
lexicon moved no count. `bash -n` passes on `run-gates.sh`, which this edit does not touch: the
row keeps its name and its report class. No manifest hash moves, for the reason the previous
entry gives. `verify-freeze.sh` reports FREEZE HOLDS.

### Correction recorded 2026-11-14 — the agency baseline was measured with a retyped instrument, and the shipped one reads two numbers differently

Both entries above expire on one point of method, not of judgement. The 23 hits and the
worst-document 0.37/1k behind them were measured with a scratch copy of the patterns, taken
before the shipped tool was tightened (pronoun guard, preposition guard, `meant` removed). That
is the Freeze 23 lesson in the direction nobody checks: a measurement and the instrument that
will run on a book must be the same instrument, or the numbers are attributable to neither.
Re-measured with `check-agency.py` itself over the same 4,531,815 words, R1 reads **11 hits
(0.0024/1k)** — 6 place, 5 object — and the worst published document is 0.21/1k, not 0.37/1k.
R2 reads **2 hits, not zero**.

What survives unchanged: R1 is report-only, R2 is report-only, no hash moves, and no cap is
derived here. What must not be repeated: "a cap would be a gate in name only" was true of the
0.55/1k line; the 1.5× line from the real worst document is ~0.32/1k, and this project's own
chapter 14 (three deliberate hits in 4,075 words, 0.74/1k) would fail it. Whether published
*chapters* would also fail it is unmeasured — that is the D1/D2 document-vs-chapter mismatch
again, and settling it needs a chapter-level published corpus and a freeze entry of its own.

The measurement is in `tools/prose/calibration/CALIBRATION.md`, under "The agency baseline,
2026-11-14", with the per-lane table, the place:object ratio, and the reading of all eleven hits.
`bash tools/prose/verify-freeze.sh` still reports FREEZE HOLDS: nothing here touches a hashed
file.

### Correction recorded 2026-11-14 — R1's gap closes to adverbs and auxiliaries, and the published baseline moves from 11 hits to 6

The agency row's first published reading counted eleven hits, five of which were a noun a
neighbouring verb already owned. Two mechanisms: a compound in the gap (*the house physician
watches*, *The Steel Ministry wants*) and a transitive verb immediately before the determiner
(*rent the house wanted*, *mended the road demanded*). The gap is now a closed list of adverbs
and auxiliaries, and a closed list of transitive verbs (`TAKING`) refuses the second class.

Re-measured over the same 4,531,815 words: published R1 reads **6 hits (0.0013/1k)** — 3 place,
3 object — with 5 of the 6 genuine on reading, the sixth being the institutional metonymy *The
Church decides*. The project tree is unchanged at 15 place, 0 object, 7 motive. The worst
published document stays 0.21/1k, so the 1.5× line and the chapter-14 finding in the entry above
both stand.

Two guards disappear into the structure: a pronoun cannot occupy the gap any more, so the
separate pronoun blocklist and the `FUNCTION` constant are deleted with it. No manifest hash
moves — `verify-freeze.sh` reports FREEZE HOLDS — and the row keeps its name, its class and its
verdict of none. Measurement and both versions of the table are in `CALIBRATION.md` under "The
agency baseline, 2026-11-14" and its revision.



### Change recorded 2026-11-18 — a new report row: `A27`, the protected comparison (Freeze 26)

`A27` counts `the way you / the way people / the way a / the way the` and **cannot fail a book**.
It joins `D1` and `D2` in the REPORT tier, and it belongs there for the same reason: on this form
the two arms of the instrument do not separate.

WHY IT EXISTS

A 46,305-word collection in this tree used the construction 89 times. Its own direction file calls
it "the book's grammar, not a tic to be sanded off" and permits thinning "only when it runs to
four". Nine of twenty-four chapters were over four. Read on three chapters the form looked like a
protected tic used well; read on all twenty-four it was the only comparison the book owned. That
is a different finding, and it is the one a hostile reader can put a number on.

THE MEASUREMENT

1,409 published documents in `tools/prose/calibration/corpus`, 6,419,470 words: **151 hits,
0.02/1k**. Worst single document 1.21/1k (Stoker, Dracula ch. 18 - 2 hits in 1,655 words); p90 and
median both 0.00/1k. The collection above, after thinning, runs **71 hits in 46,305 words =
1.53/1k** - 76x the corpus rate and above the worst published document. The cap is 3 per 2,000
words (1.5/1k), which keeps the worst reference document passing with headroom; the warn band is
2 per 2,000.

WHY A REPORT AND NOT A GATE

The construction is ordinary English, and any per-chapter cap fails published prose: Dracula ch. 18
carries 2 hits in 1,655 words, and a 1,900-word chapter with four of them is not a defect, it is a
paragraph that reached for the same clause twice. The DEMOTED block one tier up states the rule
this row obeys - a form English uses is only a tell at a rate. So the row keeps a cap, a warn band
and a number, and it cannot accuse.

WHAT DID NOT CHANGE

No gating row was added, no exit code moved, and no book's verdict can change because of this row.
`HARD`, `DENSITY`, `DEMOTED` and the `D1`/`D2` report rows are untouched. The id is `A27` because
`A1`-`A26` are taken.

EVIDENCE AT THE TIME OF THE CHANGE

`bash -n tools/prose/deslop-check.sh` passes. On the slop fixture the row prints its number and the
fixture's verdict is unchanged, because a report row can neither rescue nor worsen a book. On
chapter 19 of the collection (4 hits, 2,376 words, 1.68/1k) the row reports over its cap without
failing the file. `bash tools/prose/verify-freeze.sh` reports FREEZE HOLDS with the re-key below.

Manifest re-keyed: `deslop-check.sh` -> `d75b4e1cc8d197f5`. The matching catalogue entry is
`skills/deslopify/references/style_guide.md`, "The Comparison That Becomes the Book's Only Engine",
which carries the same measurements and the thinning rule - keep the clause that is the best in its
paragraph, replace the rest with plain description, never with a different simile.


### Change recorded 2026-11-18 — two report rows: `A28`, the withheld-speech beat, and `A30`, the hand-placement beat (Freeze 27)

Both rows count a construction that ordinary prose uses, and **neither can fail a book**. They join
`D1`, `D2` and `A27` in the REPORT tier. `A29` is deliberately unassigned: it was reserved for the
gloss (*That was the part / thing*), which the same survey measured and declined.

WHY THEY EXIST

`A27` was added the same day for a form the collection's own direction file protects. The obvious
next question was whether the tree holds the same shape in other words, so every manuscript in the
checkout was counted — 22 under `test-books/` including archives, and 314 study controls — and each
candidate was measured on the same 1,247 published documents (6,419,470 words) that the caps come
from. Two constructions clear the test, where clearing means: a manuscript in this tree exceeds the
worst published document, not merely the corpus median.

THE MEASUREMENT

`A28` — `did not / didn't` + `say, move, answer, look, turn, stop`. Corpus **0.06/1k** (p90 0.26,
worst document **1.33/1k**). Above it: `validation-series/book-1` **1.76/1k** (27 hits),
`under-three-coats` **1.60** (11), `validation-series/book-2` **1.40** (21). `marrow-light` 0.94
(73). Cap **2 per 1,000** — 1.5× the worst document — warn above 1 per 1,000.

`A30` — `put his / her / both hand(s)`. Corpus **0.01/1k** (p90 0.00, worst document **0.73/1k**).
`the-parts-still-warm` runs **1.13/1k** (147 hits) and ran **0.25** (34 hits) in its own 2026-11-12
draft: this one grew 4.5× during revision, which is why it was not visible in any first-draft
reading. `under-three-coats` 0.87, `the-emptying` 0.65. Cap **1 per 1,000** — the nearest
representable cap above the worst document, since 1.5× would be 1.1/1k — warn above 1 per 2,000.

THE ROW NOT ADDED

The gloss measured 18 hits in the collection, **0.39/1k**, roughly 490× the corpus rate and the
reason this survey was run. It was declined: 5 hits across 5 published documents put the worst
document at **0.44/1k**, so the book is inside the published distribution, and a cap that clears
0.44 would clear the book too. A row there would print a number that cannot accuse — precisely the
D1/D2 failure this block exists to prevent. It stays a direction-file rule (one per story), not a
row.

WHY REPORTS AND NOT GATES

`A28` is how prose writes a pause; `A30` is how prose writes a hand. A per-chapter cap on either
fails published chapters at the same rate the caps were built to tolerate, and the separation test
that promoted `A25` does not apply: the AI control does not sit above the human distribution on
either form. So both rows keep a cap, a warn band and a number, and cannot accuse.

WHAT DID NOT CHANGE

No gating row, no exit code, and no book's verdict can move because of these rows. `HARD`,
`DENSITY`, `DEMOTED` and the `D1`/`D2`/`A27` report rows are untouched. The survey that produced
them, including the eleven constructions checked and cleared, is
`tools/prose/calibration/tic-survey-2026-11-18.md` with per-book data in the matching `.tsv`.

EVIDENCE AT THE TIME OF THE CHANGE

`bash -n tools/prose/deslop-check.sh` passes and the file carries no stray control byte. The first
draft of these rows was written with a word-boundary escape that arrived as a literal backspace, so
both rows counted zero everywhere while still printing a plausible 0.00. It was caught by scanning
a synthetic fixture that says `put his hand` and `did not answer` on purpose, and the rows now use
the same `[Tt]`-style case handling as `A27` instead of a boundary escape.

On `the-parts-still-warm` chapter 12 the `A30` row reports **1.95/1k** (20 hits, 10,240 words)
against its 1.00/1k cap; on `validation-series/book-1` chapter 11 the `A28` row reports **4.15/1k**
(7 hits, 1,688 words) against 2.00/1k. Both print `--` and neither file's exit code moves -
book-1 and the-parts-still-warm both still exit 0, because a report row cannot set a verdict.

`bash tools/prose/verify-freeze.sh` reports FREEZE HOLDS with the re-key below, and
`bash tools/prose/validate-controls.sh` exits 0 with ALL CONTROLS PASS; its REPORT-tier control
lists the ids and printed `D1,D2,A27,A28,A30 cannot fail anything`. Control 3 (the
AI-discrimination arm) skipped for want of an AI control at that path, which is the one arm of the
suite this change is not evidenced by.

Manifest re-keyed: `deslop-check.sh` -> `09b242725673f331`.
