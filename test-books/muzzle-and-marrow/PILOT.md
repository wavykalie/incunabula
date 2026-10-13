# PILOT — what ten chapters from scratch actually produced

**Book:** *Muzzle and Marrow* (working title; deferred to the author)
**Drafted:** 2026-09-29, from scratch, under `DRAFTING_FRAMEWORK.md`
**Purpose:** the first book drafted from scratch under the current framework.

## Why this book exists

Every prior book — Merope 1, Merope 2, and `incunabula-test` — was **re-chaptered after
the fact**. All three then served as evidence that a chapter spread *survives a repair*
under the new framework. None of them is evidence that drafting under the new framework
*produces* that spread. `REWRITE.md` in `validation-series/` and step 9 of
`skills/rewrite/SKILL.md` both say so in their own words.

That gap was the reason this book was written.

## The rule it was drafted under

**A chapter is as long as the thing in it takes, and not a word more.**

No per-chapter target. No floor. No ceiling. No planned word count anywhere in
`foundation.md`, `outline.md` or the phase notes. The only number in the project is the
book-level total, which is a contract with the author and is enforced by
`check-length.py`.

---

## The measurement

| ch | words | approach | sentence len |
|---|---|---|---|
| 1 | 1,322 | cold open | 16.4 |
| 2 | 1,866 | two threads, cut | 19.0 |
| 3 | 1,633 | dialogue, single room | 18.9 |
| 4 | 1,666 | chase | 24.4 |
| 5 | 1,400 | document | 22.4 |
| 6 | 1,705 | rest | 24.6 |
| 7 | 1,799 | set piece | 20.8 |
| 8 | 1,530 | POV shift | 23.1 |
| 9 | 1,736 | wide, fast | 26.6 |
| 10 | 2,029 | set piece, cold | 25.0 |

    n         10
    total     16,686
    range     1.53x  (1,322 – 2,029)
    CV        12.7% by my count / 12.1% by the gate

### Gate results

| gate | exit | result |
|---|---|---|
| `deslop-check.sh` | **0** | PASS with warnings. A25 **0.00/1k**. D2 over the advisory line, reported not gated. |
| `check-uniformity.py` | **1** | **FAIL, 2 rows.** U1 CV 12.1% (fail under 22%). U6 antithesis frame in 5/10 chapters (fail above 40%). |
| `check-drift.py` | **0** | OK. D1 voice-step 1.31 warn. D2 `fw_it` rho +0.92 warn. |
| `check-length.py` | **1** | **FAIL.** 16,686 against a declared 22,000 floor. |

---

## The finding

**The framework's central claim did not survive its first from-scratch test.**

`DRAFTING_FRAMEWORK.md` says, of the two untargeted books:

> "The variance came from the places nobody had decided in advance."

This book had **nothing decided in advance** — no per-chapter numbers, no floors, no
bands, no planned distribution. And it produced **CV 12.1%**, against a published fiction
band of 33.4–45.1% and a gate failure line of 22%. It is the most uniform book in the
project. The three books that justified the framework scored 23.7%, 40.0% and 40.9%; this
one scored 12.1%.

So the honest statement is: **removing the numbers did not produce the spread. The spread
in the two Merope books did not come from the absence of targets.** Something else about
those two books produced it, and this pilot has just demonstrated that the explanation
currently in `DRAFTING_FRAMEWORK.md` is not the right one.

**I am not going to quietly widen the band or trim chapters to chase the number.** That
is the failure mode the whole document exists to prevent — the measurement being laundered
into a preference and a preference into a verdict. The gate says the chapters are too
alike to have been written by a person moving through a book, and on this evidence it is
right to say so.

### What I think actually happened

Look at the sentence-length column. It climbs monotonically: 16.4, 19.0, 18.9, 24.4,
22.4, 24.6, 20.8, 23.1, 26.6, 25.0. Early chapters are tight and short-sentenced; late
chapters are long and expansive. **The prose genuinely gets more expansive as the book
goes on, and the chapter lengths did not follow it.** Each chapter was written to finish
its own question, and the questions were all roughly the same size of thing, so the
chapters came out roughly the same size.

That suggests the real variable is not chapter-length targets at all. It is **how much
material a chapter's question turns out to need** — and a writer who knows the shape of
their chapter before they sit down, even without numbers, will produce a uniform book.
Merope's spread may have come from chapters written *into*, where the chapter found out
what it was.

That is a hypothesis. It is not established, and `KNOWN_FINDINGS.md` and the third
registry in `PRINTERS_COPY.md` exist precisely so that a hypothesis is not written down as
a finding. **This is one book, and one measurement.**

### U6 is a separate and more tractable finding

Antithesis frames in 5 of 10 chapters, against a fail line of 40%. The frames are
concentrated where the theme does its work — chapter 10 has two — so this is partly the
book's construction rather than a tic. But 50% is over the line and it is worth a pass.
It is a craft note for a later revision phase, not a framework finding.

---

## What this book does prove

Stated separately, because the failure above should not be read as a failure of
everything:

1. **The prose gate passes on a from-scratch book with no repairs.** A25 — the negation
   tic that needed 30 hand repairs in `incunabula-test` — reads **0.00/1k** across 16,686
   words. Not because anything was suppressed. Because the chapters were written this
   way. That is a real result and it is the first from-scratch one.
2. **One voice holds across ten chapters.** Drift exit 0.
3. **A cast built on a naming convention can be made visible to a frozen parser** without
   modifying the parser or bending a line of prose. See below.
4. **A failed gate is survivable and worth having.** U1 failed on the first from-scratch
   book and the failure is the most informative result in this project so far. A framework
   with no book drafted under it had no way of knowing.

## What it does not prove

- **Not** that drafting under the framework produces a chapter spread. It shows the
  opposite, on one book.
- **Not** that the framework is wrong. It shows the *explanation* in it is incomplete, and
  one book cannot settle a distributional claim about a corpus.

---

## The name-gate finding (resolved before drafting)

Probed the frozen `check-names.py` parser against this book's naming convention *before*
drafting, because the premise is a cast named with pet names and ordinals and the gate
splits a declared name on whitespace.

Measured on the frozen parser:

    "Mittens the 7th"              -> IGNORED (single bare part)
    "Pipp O'Halloran"              -> IGNORED (clean() drops the digit)
    "Duke Rocky of Cavalton"       -> first="Duke"       surname="Rocky"
    "Sergeant Pips Quill"          -> first="Sergeant"   surname="Pips"
    "Baroness Whiskers von Fluff"  -> first="Baroness"   surname="Whiskers"

A title lands in the **first-name** slot, and several of this book's names are
**invisible** to the gate. A cast of pet-named characters would have been largely
unchecked — the gate would have passed a book it never looked at, which is the exact
class of defect Freeze 8 and Freeze 9 were about.

Resolved in `ENTITY_STATE.yaml` by declaring each character twice: `canonical_name:` in a
two-part form the parser reads correctly, and `called_in_prose:` recording what the reader
sees. Verified by `_verify_cast.py` against the real parser — 6 characters visible, no
titles, no connectors, no collisions.

**The frozen gate was not modified and no manuscript text was changed to satisfy a
parser.** A declaration-format decision, and the cheapest kind of fix.

---

## Status

Phase 3 complete, 10 of 10 chapters. **Two gates failing, both recorded rather than
fixed: U1 at 12.1% and the length contract at 16,686 against 22,000.**

No revision attempted. `phase 3.1` (register) was skipped and recorded as skipped. The
U1 failure is written up here *before* any revision, so that a later session cannot read
the current numbers as support for the framework.

**The next decision is not a craft decision.** It is whether `DRAFTING_FRAMEWORK.md`'s
explanation of where variance comes from is wrong, and if so what replaces it — because
three books, two gates, and the framework's stated mechanism are currently resting on an
account this pilot has now falsified.
