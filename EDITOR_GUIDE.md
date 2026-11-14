# EDITOR GUIDE — the 2026-11-06 candidate set, and where it landed

The handoff of 2026-11-06 (nine Bookfox craft tricks, eight Bookfox twists, twelve
engine-review candidates, the story-spine candidate, and five ergodic stress-test
candidates) was rolled out on the editor's instruction. This file records where each diff
landed, what was already done before it, and what the adoption does and does not claim.
It condenses that handoff; the long form — sources, transcripts, per-candidate hypotheses —
lives with the video batch it came from.

## What this adoption is, and is not

**It is a hand-mode adoption.** `SELF_IMPROVEMENT.md` §4 says a change is promoted because
it passed falsification, not because a person read it — and §3 says a promotion with any
SKIPPED verifier is held, not adopted, except as a `hand`-mode act. This is that act: the
editor directed the rollout, so the changes are in, and the record says plainly that **no
falsifier ran**. Specifically, for every row below:

- no held-out comparison was written against the changed text;
- no proof-panel judged a passage with and without the device;
- no catalogue regression re-scored a finished book against the new guidance;
- the mechanical controls (`validate-controls.sh`, `verify-freeze.sh`) still apply to the
  frozen tools, which this rollout did not touch.

So nothing here is evidence. It is a set of craft and process changes made on editorial
judgement, dated, and reversible in one commit.

**It is not a bundle of ten promotions.** §5's "at most one promotion per channel per book"
was not followed; the editor chose to roll out the set at once. That is a departure from the
rate limit, not a reinterpretation of it, and it is written here rather than assumed away.

## What was already done before this rollout

| Item | Finding |
|---|---|
| Candidate 5 — merge `humanizer` into `deslopify` | **Already complete, 2026-10-15.** `skills/_archive/humanizer/MOVED.md` records the merge; the 24-pattern catalog is `skills/deslopify/references/style_guide.md`; the constructive half ("add a pulse") is that guide's closing section; the merge is in `ERRATA.md`. Nothing to do. |
| The quoin's 9-vs-8 operations discrepancy | **No longer exists.** `skills/quoin/SKILL.md`, the orchestrator (three places), `tools/phase-map.yaml` and `PROGRAM_MAP.md` all said *nine*. There was nothing to reconcile — and the count itself is now gone (candidate 1). |

## Where each candidate landed

| # | Item | Landed in | State |
|---|---|---|---|
| 1 | Quoin quota → diagnostic | `skills/quoin/SKILL.md` (description, operations preamble, report template); `skills/incunabula/SKILL.md` (quoin paragraph, 3.5→3.7 gate, maintenance artifact row, dispatch); `tools/phase-map.yaml` 3.5; `PROGRAM_MAP.md` | adopted |
| 2 | Chaos mandate → devices, not requirements | `skills/incunabula/SKILL.md` 2→2.5 gate; `skills/voice-matrix/SKILL.md` (device field, assign step); `tools/phase-map.yaml` 2 | adopted |
| 3 | Variety rule, stated once | `skills/incunabula/SKILL.md` — new section, gates now cite *(variety rule)* instead of restating | adopted |
| 4 | Simulated-reader stack → personas + proof-panel | `skills/reader-swarm/SKILL.md` (new "Where this sits"); `skills/bestseller-studio/SKILL.md` steps 3–4 | adopted |
| 5 | Merge humanizer into deslopify | — | already done, 2026-10-15 |
| 6 | Score precision → bands; drop the Originality quota | `skills/incunabula/SKILL.md` score section + dimension table | adopted |
| 7 | Tic list: measured rows vs taste | `skills/incunabula/SKILL.md` tic scan | adopted |
| 8 | Exposition carriers: closed list → open diagnostic | `skills/incunabula/SKILL.md` 3→3.1 gate; `skills/setting/SKILL.md` §5 | adopted |
| 9 | State files: stop re-deciding the primary | `skills/incunabula/SKILL.md` modes paragraph | adopted |
| 10 | Three orchestrators reconciled | `skills/incunabula/SKILL.md` new "Three runners, one engine"; `PROGRAM_MAP.md` §3 | adopted |
| 11 | Maintenance ceremony → automate the bookkeeping | `skills/incunabula/SKILL.md` maintenance gate (preflight + check-registry as the mechanical half) | **partial** — see below |
| 12 | Chapter-count inflation → multi-scene chapters | `DRAFTING_FRAMEWORK.md` new section; `skills/incunabula/SKILL.md` (phase line, new section, drafting dispatch); `skills/setting/SKILL.md` §5.1; `PROGRAM_MAP.md` | adopted |
| 13 | Story spine / payoff map | `skills/forme/SKILL.md` new §6 + output list; `skills/incunabula/SKILL.md` (2→2.5 gate, new section, foundation dispatch); `skills/collator/SKILL.md` audit 7; `tools/phase-map.yaml` phase 2 artifact | adopted |
| 14 | Per-layer canon and voice ledgers | `skills/case-keeper/SKILL.md` (layer key, cross-layer rule); `skills/collator/SKILL.md` audit 7 | adopted as declaration |
| 15 | Document-set structure: outline as architecture | `skills/forme/SKILL.md` §6; `skills/incunabula/SKILL.md` "Layered books" | adopted |
| 16 | Layout-as-meaning pass | `skills/composing/SKILL.md` §10 — inside 3.8, not a new chain phase | adopted, differently placed |
| 17 | Gates re-scoped per layer | `skills/incunabula/SKILL.md` "Layered books"; `skills/collator/SKILL.md` | adopted as declaration |
| 18 | Score and indices re-scoped for ergodic books | `skills/incunabula/SKILL.md` "Layered books" | adopted as declaration |
| Tricks 1, 2, 3, 4, 6, 9 | Drafting devices | `skills/setting/SKILL.md` §5, §5.1 | adopted |
| Tricks 2, 7, 8 | Voice-level devices and description density | `skills/voice-matrix/SKILL.md` §1, §2, method | adopted |
| Tricks 5 | Returning phrase | `skills/composing/SKILL.md` §9 | adopted |
| Twists 1, 2, 4, 5, 6, 7 | Outline-time recontextualisation | `skills/forme/SKILL.md` §6 (seed map) | adopted |
| Twists 3, 8 | Voice-contract devices | `skills/voice-matrix/SKILL.md` (devices, pressure voices) | adopted |

## What was not done, and why

- **The frozen tools were not rewritten.** Candidate 17 (per-layer gates) and candidate 14
  (per-layer canon) are declared in the skill text and the `layer:` key; `deslop-check.sh`,
  `check-uniformity.py` and the collation tools still measure a book as one manuscript. A
  layered book's per-layer evidence is currently assembled by the run, layer by layer, using
  the same instrument. That is a real gap and it is stated in `skills/incunabula/SKILL.md`
  rather than hidden.
- **No new phase entered the chain.** Candidate 16 wanted a layout pass between 3.8 and 4.
  It runs inside the composing pass instead, so `tools/phase-map.yaml`, `run-phases.sh` and
  the seventeen-phase claim stay true. A new phase would have meant a new gate row and a new
  artifact for every book, including conventional ones that need neither.
- **Candidate 11 is partial.** `preflight.sh` and `check-registry.py` now stand as the
  mechanical half of the check-in, and the runner's phase record stands as the history entry
  for a phase that did not run. The pruning-log ceremony itself is unchanged.
- **No book-specific device set was written.** The worked example (the Death Game book's two
  twists and three tricks) is per-book guidance for that book, not a repo change.

## Rollout order, as against the handoff's

The handoff's order was: merge first (already done), then the quoin, multi-scene chapters on
their own test book, the story spine with the Death Game book, then the rest ranked per book.
This rollout does the quoin and the story spine immediately and implements multi-scene
chapters in text without a test book. That inverts the handoff's caution: multi-scene
chapters are now the documented normal and untested. Treat the first book drafted that way
as the test, and record what it finds.

## First falsifier — the test book (2026-11-06)

A four-chapter test novella, `test-books/tide-register` (gitignored; 5,579 words), was cut
through the new guidance to give the quoin diagnostic, the story spine and multi-scene chapters
their first run against the real gates. Full record: the book's `maintenance/SESSION_LOG.md`,
`evaluations/ch0N-passes.md`, and `outline.md`'s actuals section.

| What was tested | Result |
|---|---|
| **Quoin diagnostic** (candidate 1) | **Holds on the case it was built for.** Chapter 3 needed one operation; the old five-of-nine rule would have forced four more edits into a chapter that passed the scanner clean. Operation 9 caught a real shape question and made it a recorded judgement instead of an automatic vary. |
| **Quoin's reach** | **Falsified, usefully.** The quoin judged every chapter locally and found nothing wrong, while `check-uniformity` failed the book on U2 (rhythm spread 2.11) and U6 (the antithesis frame in 3 of 4 chapters). A pass that judges chapters cannot see a profile the book shares — which is what the row, not the quoin, is for. |
| **Story spine** (candidate 13) | **Holds.** Written before the outline, it caught one real defect at 2.8 (Euan's well was a chapter-four payoff with no seed planted) and supplied every twist seed and the flipped line. All five debt entries resolved on the page; the sixth is deliberately deferred with a reason, and N1 passes. |
| **Multi-scene chapters** (candidate 12) | **Holds mechanically, with a caveat.** Chapter 2 was drafted in two calls, assembled under one file, and passed every gate, including `check-length`'s per-file counting. But the run reproduced the mechanism the candidate describes from the other side: four chapters produced 5,579 words against a 9,200-word plan, 1,395 words per chapter — under the 2,250 planned, and the long chapter absorbed the surplus rather than adding chapters. |
| **The suite** | No prose row failed after three revisions made at the cause. Nothing was waived, no threshold moved. |

**What failed.** The book is 30% short of its own 8,000-word floor and `check-length.py`
fails it the moment it stops declaring `status: in_progress`. That is the book's failure, not
the guidance's: four chapters of drafting do not reach a plan written at 2,250 words each.
Whether that is a defect in the drafting skill or in the plan's arithmetic is the question the
next test book should answer.

**Three instrument findings, recorded and not fixed:** `check-premise-distinct.py` cannot run
in this checkout (the frozen `PREMISE_LEDGER.tsv` holds no rows); `check-comps.py` does not
recognise a comp table whose first header cell is `Comp title` rather than `Comp`; and a
self-report named `chapter-[N]-report.md` — the name the skills document — would be counted as
a chapter file by `check-length.py` and `check-pass-evidence.py` (read from the code, not
run). All three are frozen-instrument issues and belong in `ERRATA.md` with their own
attribution, not in a silent edit here.

## Second falsifier — the layered test book (2026-11-06)

Candidates 14–18 were adopted as declarations: the skill text said what a layered book is,
and no book had been one. `test-books/ashgrove-inventory` is the first: a four-layer document
set (film log, 1974 municipal survey, present-day annotations, dated correspondence), six
document clusters, `structure: layered` declared at intake, four clusters drafted and gated,
phase 4 run on the first at independence grade C only.
The book is gitignored like every other book; its record is
`maintenance/SESSION_LOG.md`, `evaluations/layer-gates-ch01.md` and `evaluations/composing-ch01.md`.

**What the run added to the repo.** `tools/split-layers.py` extracts each layer's runs from
the fenced chapter files into `artifacts/layers/<id>/`, so the frozen scanner can be pointed
at one layer at a time. Without it, "the gates run per layer" was a sentence; with it, the
run produces per-layer evidence from the instrument that was frozen when the run started.
That held for cluster 1. It stopped holding on 2026-11-06, when cluster 2 reproduced the
finding and the floor described below was added to `deslop-check.sh` under the freeze
procedure.

| Candidate | Verdict on first contact |
|---|---|
| **14** per-layer canon and voice ledgers | **Holds, and needed a state it lacked.** `UNRESOLVED` and silence were the only two options; an unreliable narrator produces a within-layer contradiction that must be *raised* and must *not* be resolved. Both instances now carry `flag: DECLARED` with a spine reference. Cross-layer divergence has its own section and is never raised as a conflict. |
| **15** outline as architecture | **Holds.** The spine carries the layer map, nesting depth and interruption rules; the outline's rows are document clusters. The architecture also prescribes drafting order (survey before annotation), which the draft followed layer by layer. |
| **16** layout-as-meaning at 3.8 | **Holds, with its limit now visible.** Three of five rules are machine-checkable in plain text (fence, strike-through, monospace); two are print instructions (second colour, narrowing indentation) and are checked by counting rather than by a scanner. The composing report says which is which instead of implying all five were verified. |
| **17** gates re-scoped per layer | **Mechanism holds; the row did not survive the move, so the instrument gained a floor.** `P1` fails when `count x 1000 > 6 x words`, so one repeated opener fails any document under 167 words. Cluster 1: 2 of 4 layers red. Cluster 2 reproduced it on **4 of 4** layers before any fix — two arithmetic (131 and 132 words, a single occurrence each), two real repetition. The floor (`ceil(OPEN_PER_W / OPEN_PER_N)` = 167 words, below which the row reports UNMEASURED) went in under the freeze procedure on 2026-11-06. The same two cluster-1 files then went FAIL -> UNMEASURED, while the 553- and 647-word layers stayed FAIL until their prose changed. Cluster 3 found the same arithmetic on a second row: `A25`'s cap (3 per 2,000) fails any layer under 667 words, and a 612-word annotations layer failed on one real antithesis. Recorded in `ERRATA.md` and not fixed, because a floor added in the run that failed on it is the sequencing the freeze forbids. Cluster 4 reproduced it on `P1`: a 280-word film layer fails on two identical openers (4.3% of sentences), and fixing one only moves the count to the next. Against that, 44 published documents of 167-1,500 words show **zero** `P1`/`A25` failures - so the caps are not too tight for human prose at this size, and the floor question is about whether a 280-word shot list can be judged by a sentence-share rule at all. |
| **18** score re-scoped for ergodic books | **Declared, and now enforced by the validator.** Phase 4 ran on cluster 1 at grade C: raw floor 6.0, calibrated 5.2, and the floor did not move when dimension 5 was suspended — the minimum of the six scored rows is also 6.0. `check-eval.py` gained rule 5 (SCOPE): a row may read `SUSPENDED` only if the book declares `score_scoping: mode: ergodic` with a `reason:` and the dimension in `suspended_dimensions`; an undeclared suspension, an undeclared dimension, a missing reason in the declaration, a missing reason in the row, and a non-ergodic mode all fail. Nine probe arms behave as predicted. The fix was made **outside** the scoring run, as the evaluation required, and by the same agent that wrote the evaluation — a caveat recorded rather than hidden. A declared suspension the evaluation ignores is reported, so the declaration cannot be invisible in the run that overrides it. |

**The finding worth keeping.** Scoping a rate rule to a smaller unit changes its verdict
without changing its threshold. The whole-chapter scan passed a cluster containing two
failing layers. That is the blind spot candidate 17 was written to close, seen from the
other side: the per-layer run's value is **attribution**, not a different answer. The floor
below does not change that; it only stops the row judging a document smaller than its own
denominator.

**The floor, and what it cost.** `deslop-check.sh` now reports `P1` as UNMEASURED below
`ceil(OPEN_PER_W / OPEN_PER_N)` = 167 words, and `run-gates.sh` gives that state its own
name, which counts as `unclear` and blocks a phase claim like NOT RUN. Recorded in
`GATE_FREEZE.md` with the fingerprint re-keyed (`7462cde6e0dafacd` -> `951d50fa406043ab`),
`verify-freeze.sh` re-run and holding. No cap, numerator or denominator moved, and the
same files below the floor compute exactly what they computed before.

The cost is worth naming. Three things had to be true for that edit to be legitimate and
only two of them were verified to the standard the guide asks for elsewhere. No corpus of
document layers exists, so the floor is arithmetic from `P1`'s own cap rather than a
measured minimum; the domain check that no catalogue chapter but an audio fixture falls
under it is a proof about this catalogue, not about prose. `validate-controls.sh` now exits
**0** with all 19 controls behaving as predicted (2026-11-07), control 1 ran over the full
reference corpus - 51 documents, 0 failing - and control 3 runs again (32 AI-written chapters,
12 failing, 20 passing). So the floor is a derived constant with a domain check, a verified
human-prose arm, and a discrimination arm.

**And the layer corpus this paragraph said could not exist does.**
`fetch-document-layers.py` stages published prose at its own document boundaries - epistolary
novels, not chapters cut into pieces, because a cut manufactures opener repetition at every
boundary. 44 documents (Evelina's 41 letters, the 3 Walton letters), 167-1,500 words, all
scanned with the frozen instrument: **0 `P1` failures, 0 `A25` failures**, including the 19
under 667 words. The caps are not too tight for human documents of layer size; human letters do
not contain the formula often enough for a rate to bite. The floor remains derived rather than
measured, but the assumption under it is now tested instead of asserted.

**Widened 2026-11-07.** The corpus is no longer 44 documents from two books. The fetcher now
stages seven epistolary novels and **410 documents** of 167-1,500 words (23 under 167, 124 at
167-400, 134 at 400-667, 129 at 667-1,500). The zero did not generalize: under the 167-word
floor, **47 documents fail `P1`**, 45 of them under 667 words, and the share test fails 22 of
the same human documents. Above 667 only 2 of 129 fail (both with 5+ instances). `A25` has 0
failures and 1 unmeasured. Both rate rows therefore take a **667-word document floor**, below
which they report UNMEASURED. Both decisions and their probes are in `GATE_FREEZE.md`,
2026-11-07.

**What the floor does not buy.** It is not an amnesty. Two of cluster 2's four layer
failures were real repetition — "the garden" four times in 540 words, "I have" four times
in 650 — and those layers stayed red until the prose changed. One of the prose fixes then
created a fresh repetition ("the wall" x4 in 647 words) that the very next scan caught.
That sequence is the argument for the rule: 131-word and 132-word documents were being
failed for arithmetic, and 550- and 650-word documents were being failed for writing.

**What failed.** Cluster 1's phase 4 ran and produced a score, but at independence grade C
— the same context drafted and evaluated — so the raw 6.0 is diagnostic and the calibrated
5.2 is the number to quote, and neither advances a phase. Clusters 2, 3 and 4 have five pass rows
each recorded as NOT RUN rather than fabricated. `check-length.py`, uniformity, drift, arc,
surplus and recoverable all report NOT RUN: four chapter files is fewer than every one of
those rows requires, which exposes a second convention unit — a layered book built as three
long clusters would never be length-judged at all. Candidate 12's multi-call path was **not
exercised in either of the first two clusters**: both were assembled in one pass. It was
exercised on cluster 3, drafted in six calls and assembled in a seventh: the survey's two runs
merged into one 422-word layer that passes, the annotations' three runs into 608 words that
passed after one real `A25` fix, and the 161-word reel stands alone and is UNMEASURED. Assembly
works. What that run could not claim was the harder half of the candidate — all six calls shared
one context, so continuity was partly guaranteed by the harness rather than by the mechanism.

**Cluster 4 ran the remaining test on 2026-11-07, in five `codex exec` processes** with no
shared context, assembled in a sixth: 2,078 words, **4 of 4 layers passing** after three prose
repairs. What survived: the numbering, the measurements (0.25 reveal, 0.90 clear width, 4.21 x
3.40 x 1.47, area 14.31) and the depth-3 nesting, with note `[22]` quoting Ren's letter quoting
the appendix. What did not survive: the quotation. `[22]` attributed a sentence to Ren's letter
that the letter does not contain, which is exactly the failure a session writing commentary on
a document it cannot see will produce. No rate rule reads across layers, so it was found by
comparing two files. The instrument did notice the change of hand: `check-drift.py` reads a
voice-step of **5.52** against a fail line of 3.41, the largest steps being `fw_to` 22.82 and
`punct` 6.25. Separate sessions hold the facts and lose the voice, and that is now in the
book's gate record rather than in a claim.

**The prose fix, stated as a prose fix.** The annotations layer repeated "I have" five
times in 671 words. That was a real defect and rewriting it moved the layer to pass. It is
the only sentence-level change made in response to a gate, and it was made because the prose
was repetitive, not because a layer needed a number.

## Reversal

Every change is in one commit. `git revert <sha>` restores the previous guidance;
`skills/_archive/humanizer/` is untouched (the merge it records happened in October and is
not part of this). No attribution record, no freeze manifest and no `BOOKS.yaml` entry was
edited.


## House rule recorded 2026-11-11 — talk about the prose in the prose's words

Reports on *The Parts Still Warm* drifted into the bookkeeping's register: a chapter was
summarised as "he came down without using the wall (C-061)", which is a docket entry and
reads as though the manuscript had been written by the ledger. The author's response was
to ask whether the *prose* was archaic. It was not. The report was.

The rule: a passage is described in the words a reader would use about it — a sentence
quoted, a paragraph paraphrased, a scene named by what it does. Fact ids, gate names and
exit codes belong to the ledger, the freeze and the run report. When a summary of a chapter
reads like minutes of a meeting, it has stopped being about a book, and the author will
correctly conclude that nobody is reading the book.

This is the same failure the project has a rule for elsewhere: the apparatus leaking into
the artefact. It has now happened in the prose (C-022, the fighters talking like insurance
clerks) and in the criticism, which is the direction nobody was watching.
