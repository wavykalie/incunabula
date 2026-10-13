# Phase 5 — Literary Barrier Revision Loop

**Run:** 2026-09-22
**Status: NOT ACTIVATED.**

## Why

The phase definition is explicit about its activation condition:

> ## Phase 5: Literary Barrier Revision Loop
> - **activate when the user sets a quality target such as 8.5**
> - score calibrated literary lenses
> - revise weakest lens until approved or blocked

No quality target has been set at any point in this project. The nearest thing to one is the standing
prose rule (`PROJECT_STATE.yaml → standing_rules.prose`), which is a *scanner* gate with an exit-code
criterion, not a quality target on a literary lens — and the scanner's own output states it is
mechanical only.

Setting a target on the author's behalf would be the pipeline inventing a success condition and then
declaring it met. That is the exact failure this run exists to catch, so the phase is recorded as
**not activated**, with the condition that would activate it.

## What would activate it

A stated target on one or more lenses — the phase's own example is 8.5. Available lenses for this
book, and the honest current read on each (from `artifacts/06-scorecard.md`, which is an assessment,
not a calibrated lens score):

| Lens | Current read | Notes |
|---|---|---|
| Voice | strongest | The book's actual asset |
| Structure | strained | ch.3's sag; three same-shaped chapters in movement II |
| Emotional precision | strong at the shelf and the ending, flat by design through the middle |
| Prose at line level | strong, with three named irritants (`adversarial-audit.md` Part 3) |

## What Phase 5 cannot fix, and should not be asked to

Author decisions rather than lens failures, and a revision loop would burn cycles against them without
resolving them. Two of them were in fact closed on 2026-09-22 **without** a lens loop, which is the
point: they needed a decision, not a quality target.

| Item | State |
|---|---|
| ~~`AUTH-1`~~ the ch.6 cruelty line | **CLOSED** — rewritten to its budget, re-gated PASS |
| ~~`AUTH-2`~~ restore or drop Achird's shelf act | **CLOSED** — left removed; the restore option was proven geographically impossible |
| `AUTH-3` two prose judgement calls | open |
| `AUTH-4` titles | open |

**Recommendation:** if a target is set, set it against **Structure**, because it is the weakest lens
and the only one with a known cause (S-2/S-3 in the Phase 4 audit).
