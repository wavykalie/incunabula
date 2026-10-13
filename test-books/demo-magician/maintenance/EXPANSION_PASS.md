# EXPANSION PASS — The Trick

**SUPERSEDED 2026-09-28 by `incunabula/DRAFTING_FRAMEWORK.md`.**

The version this replaces assigned every chapter a target word count and a bucket, and
produced a 24-of-34 clump inside 1,004 words. Merope 1 and 2, drafted with no targets at
all, produce a 4.8x range. The targets subtracted variance rather than adding it.

**The numeric columns are gone and are not to be restored.** Do not re-add a `target`
column to `outline.md`, and do not reinstate per-chapter counts in `PROJECT_STATE.yaml`'s
`length:` block beyond the book-level floor.

## What remains

The one column of the old table that meant anything was the one headed *why the outline says
it is long*. That survives, and it is now the whole brief. Per chapter, the question is:

> What is this chapter about that it has not finished saying?

A chapter that has an answer to that takes the time the answer takes. A chapter that has
not is not short — it is unfinished, and nothing can be added to it that would be true.

## The order of work is unchanged, and is not a word count

The remaining expansion is the material in batches 5–9 of the superseded plan, taken in the
same order, because that order is structural rather than arithmetic:

- **6, 8, 14** — the two rest chapters and the tent. These are the chapters where the book
  is allowed to be a pleasure, and they are short because the set-pieces are short, not
  because a number said so.
- **18, 21, 31** — Marseille 1931, the solve, and the highest beat.
- **25, 30, 34** — the procedure, the prediction, the four corrections.
- **2, 16, 26** — the three shortest-designated chapters. Under the new framework these are
  NOT automatically top-ups. Each is asked the question above and the answer decides.

## L1 and U1 are downstream, and are not targets

`check-length.py` will report the book short until the expansion is done. That is a true
reading of an unfinished book and it stops being true when the scenes are in, not when a
counter reaches a number. `check-uniformity.py` will report whatever distribution the
finished book actually has.

**Neither row is to be chased.** The old plan's "L1 clears at batch 4" line was a way of
making progress measurable and it turned out to be a way of optimising a proxy. The sweep
runs once, at the end, per `FULL_SWEEP.md`.
