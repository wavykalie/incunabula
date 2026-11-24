# Phase 0 — Intake

## What you are given

One idea. That is the whole required input. Everything else — language, genre, audience,
length, narrative mode, market position — may be inferred, and every inference you make
gets written into `ASSUMPTIONS.md` so the author can see it and push back.

## What you leave behind

- `maintenance/IDEA.md` — the author's own sentence, before anything touches it
- `ASSUMPTIONS.md`
- `artifacts/00-brief.md`
- `artifacts/01-market-map.md`
- `artifacts/02-story-engine.md`
- `PROJECT_STATE.yaml`
- `premise.md`, only when the launch/bestseller profile is selected

## How to treat the idea

The idea is a seed, not a brief. Do not read a full specification into it. Do convert
every hidden assumption you are making into a visible one.

Find two to four honest comparison titles. Name the gap in the market the book could take.
Say what the reader is being promised.

Then work out what makes this version *legible* to the market it wants — legible, not
generic. Those are different goals and only one of them is worth having.

## The discard record

This project has built engines it threw away, and they are recorded in the root
`COMMONPLACE.md` under **Do not rebuild**. Read that section before you accept an engine,
then run the refusal:

```bash
python tools/blind-packet.py <book-root> --discards
```

It reads `premise.md` and the chosen engine in `world.md` and refuses a premise that rebuilds
a scrapped one, naming the entry that scrapped it. Two are on the list today:

- **the-debt-engine** — the family as collateral on an ancestor's surety, where cleared
  terms bought standing, standing bought shares, and shares bought a charter. Scrapped
  2026-11-24 with the book that carried it.
- **the-clerk-narrator** — a narrator who is a device the story casts: a clerk, notary or
  registrar recording the book from inside the fiction. Scrapped for the same book, on the
  author's rule that *"the author should not take the shape of a device the story casts."*

A refusal is not a taste note, and it is not cleared by softening the premise until the
pattern hides from the scanner. New nouns over the same ladder is the same engine. There are
two ways past it, and only one of them is silent:

1. **Change the engine.** The gate reads shapes, not words: if the family is not collateral,
   there is no ladder to rename.
2. **Overturn the record.** Append a dated entry to the root `COMMONPLACE.md` saying what the
   old diagnosis missed and why this premise is not that engine, then re-run with
   `--allow-discard <slug>`. That leaves a record of who was wrong and why, which is the
   point of having a record at all.

## Keep the idea in the author's words

Before you rewrite anything, write what the author actually said into `maintenance/IDEA.md`,
verbatim, in their phrasing, with the date. A paragraph is enough. Do not tidy it, do not add
the genre, do not turn it into a logline: the file's entire value is that this engine has
not touched it.

That file is the input to `tools/blind-packet.py`, which builds the packet a fresh context —
another model, a fresh subagent, or a person — turns into the book's world. A packet built
from `premise.md` is already contaminated: by the time a premise exists, these phases' nouns
are in it, and a world grown from them comes back as a contract, a debt, or a court. So the
raw sentence has to survive somewhere untouched, and this is where.

If the author gave no sentence — only a title, or a genre, or a feeling — ask for one
sentence in their own words and record the answer. Carrying that question into the session is
cheaper than inventing an answer and discovering it three phases later.

Never overwrite this file later in the run. If the author revises the idea, append the new
wording under a date; the history of the sentence is the record of what the book was asked
to be.

## Brief contents

`artifacts/00-brief.md` carries: the original idea as the author worded it; the direction
you inferred; language; genre; audience; target length with floor and ceiling; positioning
(full-length book, short novel, novella, serial installment, or nonfiction); planned
chapter count and average words per chapter; narrative mode; and the reader promise.

## Market map contents

`artifacts/01-market-map.md` carries: market signals, comparison titles, the patterns those
titles share, and where the whitespace is.

## Story engine contents

`artifacts/02-story-engine.md` carries: the premise expanded, the central conflict, the
logic by which pressure escalates, and what differentiates this book from the comparisons.

## When to run premise-forge first

If the launch/bestseller profile is active, or the premise is structurally unsure of itself,
run `premise-forge.md` before any foundation work. Keep the author's idea recognisable, record
which contradiction or irony engine won, and save the result to `premise.md`. This is an extra
gate wrapped around the engine's existing intake — it replaces neither the research nor the
foundation phase.

## Before you finish

Confirm `maintenance/IDEA.md` exists and carries the author's wording rather than a rewrite.
The blind packet reads it verbatim, and an empty file is the one failure that shows up much
later, as a world that sounds like the tooling.

Run `python tools/blind-packet.py <book-root> --discards` and record the verdict with the
intake, beside the voice resolution. A premise that has not been checked against the discard
record has not passed intake; a premise that fails it has no engine yet.

Run the maintenance check-in. `CANON_LEDGER.yaml`, the live voice specifications, and
`maintenance/PRUNING_LOG.md` must exist before phase 1 is dispatched.

Also settle the author this book is drafted as, because phase 3 will need the answer:
`python tools/ductus.py voice <book-root>`. A resolved voice means `ductus/<slug>/` is
read before every prose phase and its digest recorded in the state file's `voice:` block;
`UNASSIGNED` means the root `COMMONPLACE.md` alone, and that absence is recorded rather
than left blank; a `REFUSED` assignment stops the run at intake rather than at the first
chapter, which is the cheapest place to find out that a persona was never authored.
