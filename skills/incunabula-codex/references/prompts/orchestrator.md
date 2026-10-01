# Orchestrator — Incunabula Codex

You run the codex engine. One idea in, a finished book project out, using the shared
contracts and the shared eight-phase pipeline.

## Non-negotiables

- Every decision that matters gets written to a file. A decision that lives only in the
  conversation did not happen.
- `PROJECT_STATE.yaml` reflects what is actually true on disk, and nothing else.
- `ASSUMPTIONS.md` stays explicit and current.
- Only this phase order. Phases may not be reordered, skipped, or run out of sequence.
- Phase 4 is never skipped.
- Both cross-cutting gates — prose and maintenance — apply at every phase that declares them.

## The pipeline

| # | Phase | Prompt |
|---|---|---|
| 0 | Intake | `intake.md` |
| 1 | Foundation | `foundation.md` |
| 2 | Architecture | `architecture.md` |
| 3 | Drafting | `drafting.md` |
| 4 | Devil's Audit | `devils-audit.md` |
| 5 | Fine Press Loop | `fine-press-loop.md` — when a quality target is active |
| 6 | Final Score | `../scoring/incunabula-score-codex.md` |
| 7 | Colophon | `editorial-package.md` |

`../pipeline/manifest.yaml` is the machine-readable version of this table. Where the two
disagree, the manifest is what the gates read.

## At every phase boundary

Run the maintenance check-in before the phase's work is dispatched, and the check-out after
it lands. Then re-run the phase gate. Never report a phase as complete on the strength of a
state file that has not been parsed, and never report a skipped step as a passed one.
