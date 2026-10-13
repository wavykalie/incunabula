# FULL SWEEP — The Trick, one pass, one decision

**Created 2026-09-28, by ruling.** This is the replacement for per-chapter gate hunting.
It runs once, at chapter 34, and it is designed to *terminate*.

## Why one sweep and not continuous checking

The previous book's failure was not that gates missed things. It was that gates ran too
early to mean anything and too often to be finished.

A cross-chapter measurement run at chapter 4 of 34 is measuring 12% of the book. `U1`
needs a spread; four chapters have no spread. `check-drift` needs a trend; four points
is not a trend. Whatever such a run reports, it is a statement about the *incompleteness*
rather than the prose — and it is read as a statement about the prose, because the exit
code says `FAIL` either way.

So those gates do not run during drafting. They run here, once, when there is a book.

**The sweep produces one list. The author makes one decision about that list. There is no
per-chapter equivalent, and a finding produced outside this file is a finding about a
gate, not about the book.**

## When it runs

Chapter 34 exists, all 34 files are named `chapter-NN.md`, and no further prose is being
written. Not before. A sweep run at 90% produces findings that the last 10% will create
and uncreate, and re-running it is the loop in a new costume.

## The commands

Run in this order. Each is a measurement; together they are the book.

    # Run from the workspace root (the parent of incunabula/). No absolute
    # paths: this template used to hardcode one machine's root and broke
    # everywhere else. Paths are relative by design now.
    INC="incunabula/tools/prose"
    BOOK="demo-magician"

    # 0. the instrument is still the instrument
    bash "$INC/verify-freeze.sh"

    # 1. length contract  (L1)
    python "$INC/check-length.py" "$BOOK"

    # 2. per-chapter prose  (the only gate kept during drafting)
    bash "$INC/deslop-check.sh" "$BOOK/manuscript/chapters"

    # 3. cross-chapter monotony  (U1-U6)
    python "$INC/check-uniformity.py" "$BOOK"

    # 4. voice drift across the book
    python "$INC/check-drift.py" "$BOOK"

    # 5. emotional direction  (A1 gate, A2-A4 report)
    python "$INC/check-arc.py" "$BOOK"

    # 6. dialogue carries plot  (S1-S4, report-only)
    python "$INC/check-surplus.py" "$BOOK"

    # 7. tic x dialogue enrichment  (report-only)
    python "$INC/check-recoverable.py" "$BOOK"

    # 8. names, premise, comps  (read no prose)
    python "$INC/check-names.py" "$BOOK"
    python "$INC/check-premise-distinct.py" "$BOOK"
    python "$INC/check-comps.py" "$BOOK"   # the gate takes the BOOK directory, not the
    # file. The first full sweep ran it with the file path and it exited on
    # 'no such book directory' - the command above was stale, the gate was not.

    # 9. outline still matches what was drafted
    python "$BOOK/verify_outline.py"

    # 10. the two hand checks no script does
    #    - does the manuscript contradict CANON_LEDGER / ENTITY_STATE
    #    - does the cold solve still hold against the finished text

## The output format — one page, not ten

The sweep writes **one** file, `maintenance/SWEEP.md`, and it has exactly this shape:

| row | result | verdict | action |
|---|---|---|---|
| L1 length | 84,102 / 80,000 | PASS | — |
| deslop | 2 warns | PASS w/ warnings | note the two sentences, move on |
| U1 spread | 31.2% | **WARN** | *the one decision* |

A row that passes gets one line and no discussion. **A row that passes is not evidence
of quality and must not be written up as if it were** — six of the fifteen rows are
advisory or report-only, so most of a green sweep is a statement that nothing was
gated. Writing it up as a victory is how a sweep becomes a morale document.

**The sweep's entire value is the failing rows, and there should be three or fewer.**

## The decision rule

At the end of the sweep there are three buckets, and the author assigns each failing row
to exactly one:

1. **Fix now.** It is a defect and the fix is local. Do it. Re-run *that gate only*.
2. **Close it.** It is a real finding the author does not want to fix. Write one line in
   `incunabula/KNOWN_FINDINGS.md` with the reason. The gate is **not** suppressed — it
   keeps firing, and the answer now lives in a table. *This is the bucket that was
   missing, and its absence is what made the last five sessions endless.*
3. **It is a gate defect.** The row is wrong, not the book. It goes to `ERRATA.md` with
   evidence, and it does **not** become work on the manuscript. Evidence required: the
   corpus, the control, and a negative case. No exceptions to the evidence requirement,
   because the cheapest repair in the world is to declare correct prose defective.

**No fourth bucket. In particular, no "note for later"** — a note for later is an
unclosed finding, and an unclosed finding is the loop.

## What the sweep does not do

- It does not rewrite anything. The sweep is measurement. Fixes happen after, in one
  pass, and each fix is re-checked by its own gate.
- It does not run the expansion pass. That is Phase 4 and it is a separate decision with
  its own scope.
- It does not re-open questions the author has already ruled. A closed finding in
  `KNOWN_FINDINGS.md` is closed; the sweep may report it and must not relitigate it.

## Termination

The sweep is finished when every row is in a bucket. Not when every row passes — a book
that passes fifteen gates is a book nobody has read. Finished is: three or fewer
findings, each assigned, each either fixed or closed, and the manuscript file count
unchanged.

**That is a state this project can reach. Per-chapter hunting could not reach it at all,
which is the entire argument for this file.**
