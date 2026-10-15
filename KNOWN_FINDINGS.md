# KNOWN FINDINGS — findings the author has declined to fix

**Created:** 2026-09-28, by ruling, after a debate in which the same conclusion arrived
from two directions: Agent B (refusing a general framework) and the author's own
frustration with sessions that end in a list of problems instead of a finished book.

## What this file is for

A defect, from here on, means exactly one of two things:

1. a gate that fails, or
2. a contradiction between two files in `CANON_LEDGER.yaml` / `ENTITY_STATE.yaml`.

That is the whole definition. Anything that is neither is an **observation**, and an
observation that the author has seen and not acted on is **closed**. It goes here, in one
line, and it does not come back.

This file exists because the loop was self-feeding. A gate produced a finding; the
finding was read; the finding was not fixed; the next session re-ran the gate; the gate
produced the same finding again. The second report of a thing already reported is
indistinguishable from news, and that indistinguishability is what made the loop feel
endless. **The fix is not fewer gates. It is a place to put the answer "we know."**

## The closed list

| id | finding | gate | closed because | reopened if |
|---|---|---|---|---|

## What does NOT go in this file

- **A gate that fails.** A failure is a finding with a decision pending. Fix it or
  escalate it, but do not close it — a failing gate closed silently is a broken freeze.
- **A ledger contradiction.** Same. These are factual conflicts and one of the two is
  wrong.
- **Anything the author has not seen.** This file is written *after* the author is told.
  Pre-emptively closing something unseen is how a finding gets lost.

## How a finding is closed

1. The gate reports it.
2. The author is shown the report, verbatim, with the file and line.
3. The author either fixes it, or says no.
4. If no, it is written here with the reason, and the gate is **not** changed to
   suppress it. Suppressing it would make the manifest dishonest; the row stays in the
   freeze and keeps firing, and the answer to it now lives in a table instead of in the
   reader's memory.

That last point is the design. **The gate keeps firing.** A frozen instrument is not
edited to make a book look better — that is the whole argument of `GATE_FREEZE.md`. What
changes is that the author reads the same finding a second time, sees it listed as
already declined, and moves on. One line, closed, permanently. The loop is broken by
*recognition*, not by suppression.

## Reading order for a new session

    1. this file            — what is already known and closed
    2. GATE_FREEZE.md       — what the instrument is, and is it still frozen
    3. the book             — go to work

A finding that appears in this file is not a finding. It is a line item with a decision
attached, and the decision was already made.

---


---

## The closed list is empty

**Nothing has been closed yet**, which is the correct state for a fresh install:
this file is where a finding the author has seen and declined to fix goes, in one
line, so it does not come back disguised as news.

The loop this prevents is worth stating, because it is the reason the file exists:
a gate produces a finding, the finding is read, the finding is not fixed, and the
next session re-runs the gate and reports it again. The second report of a thing
already reported is indistinguishable from news, and that indistinguishability is
what makes a project feel endless. The fix is not fewer gates; it is this place to
put the answer "we know."
