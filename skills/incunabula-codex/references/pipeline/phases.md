# Incunabula Codex — Pipeline

Eight phases, numbered 0 through 7. The order is fixed; nothing may be reordered,
skipped, or run out of sequence, and no phase may be re-entered to repair a phase
that comes after it.

| # | Phase | Prompt | Gate it must pass |
|---|---|---|---|
| 0 | Intake | `prompts/intake.md` | intake + maintenance |
| 1 | Foundation | `prompts/foundation.md` | foundation + maintenance |
| 2 | Architecture | `prompts/architecture.md` | architecture + maintenance |
| 3 | Drafting | `prompts/drafting.md` | drafting + maintenance + prose |
| 4 | Devil's Audit | `prompts/devils-audit.md` | audit + maintenance + prose |
| 5 | Fine Press Loop | `prompts/fine-press-loop.md` | loop + maintenance |
| 6 | Final Score | `scoring/incunabula-score-codex.md` | score + maintenance + prose |
| 7 | Colophon | `prompts/editorial-package.md` | package + maintenance + prose |

## Two gates sit across all eight phases

### The prose gate

No chapter enters the manuscript, no score is published, and no package is assembled
until the calibrated scanner has cleared the prose. A gate that was never actually
run is not a gate that passed.

Four rules govern it, and each of them exists because the opposite rule produced a
false green light somewhere:

1. **Numbers are derived, not picked.** A pattern may be banned outright only when it
   never occurs in the calibration corpus of published prose. Everything else gets a
   ceiling. Those ceilings are fractions, not whole numbers per thousand, because
   integer-per-thousand arithmetic silently floors any limit tighter than 1 in 1,000
   down to nothing.
2. **A pass has to be earned from both sides.** The scanner must stay silent on human
   prose, must fire on a deliberately bad fixture, and must *partially* fire on the
   machine-written control. A scanner that condemns the AI control wholesale is not
   discriminating; it is guessing.
3. **Scanning nothing is a failure.** Point the scanner at a directory and it finds no
   files, and the honest result is FAIL. Zero files is not zero violations.
4. **Manuscript prose only.** Outlines, scene packets, and state documents are written
   to be exact, and their register deliberately sits above the prose ceilings. Say so
   whenever a run is reported so nobody reads a planning document as if it were prose.

And a fifth thing the per-chapter scan cannot do at all. A scanner that reads one chapter
against a rate is structurally blind to uniformity: it never holds two chapters at once, so
"every chapter is within a few percent of every other" is invisible to it. That is the
failure that matters most, because it is the one no human writes by accident. So the gate is
two tools, not one — a per-chapter scan for the sentences and a whole-manuscript scan for the
shape:

- **the delivered word count is inside the range the book declared for itself** — see
  below, because this one is different in kind from everything else in the gate;
- chapter lengths distributed like published prose rather than clustered;
- no single rhythm profile shared across chapters;
- no habit of closing chapters on an explanatory coda, and no chapter ending that explains
the chapter's meaning to the reader;
- a manuscript that is uniformly even is a **finding, not a pass.** Sustained competence
  without a single accident in it is the signature, not the absence of one.

Thresholds, tiers, control expectations, and the blind spots of this gate are in
`scoring/prose-gate.md`. The corpus and the commands that re-derive the numbers belong
to the project's own calibration record.

#### The one row in this gate that is not a corpus measurement

Every other row above is a *rate*, and a rate is satisfied by a book that is shorter than
intended. The chapter-length row is worse than that: it is a variance, so it is
scale-invariant, and the cheapest way to pass it is to **delete prose from the long
chapters** rather than write the missing chapters. Measured on a real run: cutting the two
longest chapters by 40% raised the chapter-length CV from 30.3% to 22.5% — still passing —
while removing 1,892 words from a book that was already 40% short of its target.

So the shape rows need a floor, and the floor is `tools/prose/check-length.py` (row `L1`),
which compares the manuscript to `word_floor` / `word_ceiling` in this file's
`project:` block. Two things make it safe to enforce where the corpus rows are advisory:

1. It makes no claim about human prose, so there is no population it can false-fail.
2. It is enforced on exactly the books whose `positioning` declaration switched the
   variance row off — which is where a half-length book previously went unnoticed.

**`word_floor` and `word_ceiling` are therefore required before Phase 1, not optional
metadata.** With them unset, `L1` exits 2, which means not run and never a pass.

### The maintenance gate

Canon, state, and the maintenance log are reconciled twice per phase: once before the
work is dispatched, once after it lands. Nothing about this gate is optional, and a
required artifact that was never produced is reported as a failure — not added to a
list of things to do later.

- **The canon layer precedes phase 0.** `CANON_LEDGER.yaml` at both series and book
  scope, the live voice contracts, and `maintenance/PRUNING_LOG.md` must exist before
  anything else starts. Finding them missing at a later phase is a REPAIR, and it gets
  recorded as handled late rather than as if it had been there all along.
- **Check-in, before dispatch.** Open the primary state file, the ledger, the recent
  session entries, and the prompt for the phase about to run. Confirm every chapter's
  status and word count against the file on disk. Scan what changed for new facts.
  Fold duplicates into the fact IDs that already exist. Stamp provenance and a
  verification date.
- **Check-out, after the work.** Write the primary state, the ledger, the voice
  contract, and the document registry. Append to the pruning log, which is append-only.
  Re-run the phase's gate before anyone claims the phase advanced.
- **Contradictions are surfaced, never smoothed.** Hold both values with their sources,
  open a conflict record, and escalate anything that moves content boundaries, changes
  how the book ends, or rewrites who a character is.
- **A step that did not happen is written down as not having happened.** A phase that
  never ran, an artifact that does not exist, a precondition nobody met — each keeps its
  own status line. Absence is not evidence of success, and neither is a file that is
  missing because each party assumed another party would make it.
- **State is read with a parser.** A state file that fails to parse means no downstream
  gate could have read it either. Report that as the failure it is, repair it before
  overwriting anything, then verify again.
- **The pruning log also records what was left alone.** Choosing not to prune, not to
  archive, and not to overrule a source are all entries. A log that only ever lists
  deletions can never demonstrate that anything was protected.

`maintenance-protocol.md` holds the operational detail: the four modes, the check-in and
check-out sequences, how duplicates are recognised, how stale facts are handled, and the
point at which the agent must stop and ask. The ledger, intake, and voice-contract
schemas sit alongside it.

## Phase notes

**Phase 0 — Intake.** Take the user's idea, infer the assumptions, persist the brief.
Maintenance gate: stand up `CANON_LEDGER.yaml`, the live voice contracts, and
`maintenance/PRUNING_LOG.md` here. A project that reaches phase 1 without them has
already broken the gate.

**Phase 1 — Foundation.** Premise expansion, theme, characters, market framing.

**Phase 2 — Architecture.** Outline, emotional curve, opening strategy, the promise the
ending has to keep.

**Phase 3 — Drafting.** Write in chapter blocks and let the blocks differ from one
another structurally. Maintenance gate: check in before each block, check out after it,
reconcile the new chapter's word count against the file, register every new proper noun,
and log a conflict instead of quietly harmonising it. Prose gate: scan the chapter once
it exists. A chapter the scanner rejects does not join the manuscript no matter how well
it reads. Do not run line-level anti-slop edits mid-draft; the scan lives at the
boundary, not inside the writing.

**Phase 4 — Devil's Audit.** Structural criticism runs before any score is reported;
cut, merge, reorder, or rewrite as the findings require. Maintenance gate: unresolved
ledger conflicts are an input. An audit may not clear a phase whose open conflicts were
never recorded, and it may not close one by editing canon. Prose gate: the scan result is
also an input. A passing scan never implies the prose is good.

**Phase 5 — Fine Press Loop.** Run the optional calibrated literary loop. Evaluator,
revising editor, and final approver stay separate roles. Exit on approval or on a stated
blocker; never keep looping without a reason.

**Phase 6 — Final Score.** Run the score. Record the verdict and what happens next.
Maintenance gate: no score is reported while the ledger holds unrecorded conflicts, and a
primary state file that will not parse stops the score outright. Prose gate: every chapter
green, with the control-validation run filed beside the result.

**Phase 7 — Colophon.** Synopses, cover brief, formatting package. Maintenance gate: the
package quotes the ledger's current fact values rather than paraphrasing them, and marks
which facts are scoped to this book alone. Prose gate: a manuscript with a failing scan
produces no package.
