# RUN REPORT — Book 2

**Reported:** 2026-09-22
**Rule (inherited from Book 1):** a phase is only "complete" here if its file is actually on disk. No
chat claims.

**Book 2's state in one line:** **DRAFTED AND DELIVERED.** 7 chapters, 15,148 words, prose gate 7/7 PASS,
both continuity gates run, scored 7.5, editorial package written, EPUB 3 built — and the run's most
important finding is a canon defect the pipeline put there itself and the author caught (`CONF-011`).

> **Update, 2026-09-24 — the run is complete.** Everything below this line is the Phase 0 report and is
> kept as the record. Phases 1–7 have since run. See `PROJECT_STATE.yaml → phase.history` for the phase
> log, `continuity/provenance-audit.md` for `CONF-011`, `continuity/manuscript-audit.md` for the
> CRITICAL found in prose that had already passed the gate, `artifacts/06-scorecard.md` for the score
> and `artifacts/07-editorial-package.md` for the package.

> **Update, 2026-09-22 (later the same day):** `PROBE-001` is **CLOSED**, and every hygiene debt is
either closed, satisfied, or explicitly carried with a deadline. Book 2 now has **zero open
conflicts**. The one thing still blocking drafting is the author's **engine choice** — see the
bottom of this file.

> **Update, 2026-09-23:** **the engine is chosen.** Engine A, "the work" — a world where everyone has
a job and the job is the whole point, nobody is kept, everyone is *needed*. Recorded as
`book-2.engine` with `authority: user_decision`, and the three options were offered without a
recommendation. The commercial contract is **re-confirmed** (ceiling 20,000 → 22,000 words, shape
unchanged at 7 chapters), closing debt D-3. **Phase 0's gate PASSES.** The two decisions that remain
open — the new location's content and the relationship delta's content — are the author's, and Phase 2
cannot build an outline without them. No prose yet, and none will be until they are settled: those are
the remaining decisions, and inventing them is the failure this layer exists to prevent.

---

## Phase status

| Phase | V4 name | Status | Evidence file |
|---|---|---|---|
| 0 | Intake (upgrade layer) | **GATE PASSED 2026-09-23**, then COMPLETE 2026-09-24 — resumed from canon, every decision taken, **engine, location, population, interval and delta all decided**, and one inference corrected | `INTAKE.md`, `ASSUMPTIONS.md`, `CANON_LEDGER.yaml` → `book-2.engine` / `.location` / `.population` / `.interval` / `.relationship-delta` |
| 1 | Research | **COMPLETE** — desk analysis only, as Book 1's | `artifacts/01-market-map.md` |
| 1.5 | Reader personas | **inherited, NOT recalibrated** — a recorded gap, not a pass | `../book-1/reader-personas.md` |
| 2 | Foundation + Architecture | **COMPLETE** — engine, location, population, delta, `R-013`–`R-021`, 7-chapter outline | `foundation.md`, `outline.md` |
| 2.5 | Voice DNA | **COMPLETE — appended, not copied** | `../book-1/voice-dna.md` (Book 2 section) |
| 2.7 | Entity tracking | **COMPLETE** — new entities issued, UPDATE pass over the drafted chapters | `ENTITY_STATE.yaml` |
| 2.8 | Continuity (outline) | **GATE CLEARED** — 3 CRITICAL found and applied | `continuity/outline-audit.md` |
| 3 | Writing | **COMPLETE** — 7/7 chapters drafted, **prose gate 7/7 PASS**, 15,148 words | `manuscript/chapters/` |
| 4 | Adversarial Audit | **COMPLETE** — 7 exposures; item 1 escalated to the author, not fixed | `continuity/adversarial-audit.md` |
| 5 | Literary Barrier Loop | **STILL NOT ACTIVATED** (no quality target set) — for either book | — |
| 5.6 | Continuity (manuscript) | **GATE CLEARED** — **1 CRITICAL found in prose that had already passed the prose gate**, fixed, re-gated | `continuity/manuscript-audit.md` |
| 6 | Final Score | **COMPLETE** — composite **7.5**, lowest lens pacing/coherence and emotion at 7.0 | `artifacts/06-scorecard.md` |
| 7 | Editorial Package | **COMPLETE** — synopses, blurb, 3 cover directions, formatting; **EPUB 3 built and verified** | `artifacts/07-editorial-package.md`, `dist/merope-book-two_WORKING-TITLE.epub` |
| — | Resume / validation test | **complete** | `continuity/resume-test.md` |
| — | Provenance audit (**new this run**) | **complete** — the run's central finding | `continuity/provenance-audit.md` |
| — | Maintenance layer | **RUN at every phase** — 5 session entries, 5 pruning entries | `maintenance/` |

---

## What this session actually produced

Not prose. **Four artifacts that did not exist and now do**, plus a tested negative result:

1. A **resume** that loaded six canon artifacts from disk, in order, with citations — and reproduced
   the character IDs, the four voice cards and their non-negotiable properties.
2. A **scoped-change recognition**: the two changes pre-registered in the series ledger before Book 1
   was finished were consumed as `planned` facts for `book-2` rather than raised as conflicts.
3. A **contradiction probe** (`PROBE-001`) that was recognised, recorded with both values preserved,
   left **unresolved**, and prevented from leaking into the series ledger.
4. **Three escalated decisions** instead of three invented ones.

## Why the engine was blocked, and how it closed

Drafting Book 2 requires an engine. Book 1's is *hospitality — nothing is asked of you and that is how
you die*. Book 2 needed a different mechanism, and that is a creative decision, not a derived one.

**The pipeline was not qualified to make it.** The canon layer's first rule is that a fact is created
from user consultation and not from model inference, and the reason for that rule is on the record:
the torn-down early build wrote its canon without asking, and it had to be deleted. A validation run
about whether this layer can be trusted would be self-defeating if it ended by inventing a premise.

So the engine was escalated with three written options and three short **non-canon** samples
(`artifacts/engine-samples.md`), each labelled as discarded on selection. **On 2026-09-23 the author
chose A, "the work",** and that is now `book-2.engine`. All three samples are superseded — the file is
kept as evidence of *how* the decision was made, and nothing in it is canon.

**Still no prose, and for a reason that is still the same rule.** Phase 2 cannot build an outline
around an unknown world: the location's content and the relationship delta's content are the two
remaining decisions, they belong to the author, and they will be offered as options rather than
guessed at.

## Gates

| Gate | State |
|---|---|
| Maintenance check-in / check-out | **RUN** — session log entry 001, pruning log entries 001-002 |
| Prose gate | **n/a** — nothing drafted |
| Continuity | **not started** — no outline exists |
| **Open conflicts** | **0.** (`PROBE-001` was the deliberate probe; it has since been **CLOSED** — see below) |

## Debt this session opened, with deadlines

| # | Debt | Status | Deadline |
|---|---|---|---|
| 1 | Close or remove `PROBE-001` | **CLOSED 2026-09-22** — resolved as validation scaffolding by author instruction; both values preserved, series value upheld | done |
| 2 | Log the removal in the pruning log | **CLOSED** — pruning log entry 003 | done |
| 3 | Re-confirm the commercial contract (Book 2's copy is `confirmed_by_user: false`) | **CLOSED 2026-09-23** — re-confirmed with the engine choice; ceiling raised to 22,000 words | done |
| 4 | Carry Book 1's **remaining three** author items forward (`AUTH-3`, `AUTH-4`, `AUTH-6`; `AUTH-1`, `AUTH-2` and `AUTH-5` were closed 2026-09-22) | **carried** — registered, not lost | at Phase 2 |
| 7 | Inherit the appearance canon rather than redesigning it; do not resolve `APPEAR-1`..`APPEAR-4` by inference | **satisfied** — recorded in Book 2 entity state | at Phase 2 |
| 5 | Recalibrate the reader personas if the engine targets a different reader | **carried** | at Phase 2 |
| 6 | The cover-the-name exercise still has not been run, for either book | **carried** — not a drafting blocker | before Phase 7 |

## Next action

**Phase 1 (Research), then Phase 2 (Foundation).** The engine is decided, the probe is closed and the
contract is re-confirmed, so the order is now: research → foundation and outline → Phase 2.8 continuity
→ draft.

**Before Phase 2 can produce an outline, two decisions must come from the author:**

1. **The new location's content** — which world, and what it is like. The scoped change is registered;
   its content is not.
2. **The relationship delta's content** — what has actually changed between Merope and Achird since
   Book 1's ending. Only the direction is registered (a fact both carry and neither will name), and the
   plain sentence stays off the page because stating it would change a series-scoped voice contract.

Both will be written up as options, exactly as the engine was, so they can be decided by reading rather
than by description. Nothing has been drafted, and nothing will be, until they are settled.

The full validation result — all seven of the run brief's success criteria, with evidence and with the
one that is only partially satisfied labelled as such — is in **`continuity/resume-test.md`**. It is
the document to read if only one is read.
