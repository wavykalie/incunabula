# PREDICTION — recorded 2026-09-29, BEFORE any prose exists

**This file is written before chapter 1. That is the entire point of it.** A measurement
taken after the fact gets a story fitted to it; a measurement taken in advance can break
the story, and this project has spent the last three days learning what happens when a
number is explained after the manuscript that produced it is already written.

Nothing below may be edited to fit the result. If the book breaks the prediction, the
prediction is wrong and says so, and the correction is recorded here rather than
quietly dropped.

## The observation that prompted it

The from-scratch pilot, `muzzle-and-marrow`, 10 chapters, 16,686 words. Mean sentence
length, chapter by chapter:

    16.4  19.0  18.9  24.4  22.4  24.6  20.8  22.4  26.6  25.0

This rises. Not smoothly — there are dips at chapter 7 and it is not monotonic — but the
first chapter is 16.4 and the last is 25.0, and the middle sits between. Chapter lengths
over the same ten chapters are flat: 1,322 to 2,029, CV 12.1%.

So the prose got more expansive while the chapters stayed the same size.

## The two readings, and why the book can tell them apart

**Reading A — a curve.** Sentence length expands and then settles. A writer warms up,
overshoots, and finds a register. Under this reading the climb decelerates: big early
gains, then a plateau somewhere in the second third.

**Reading B — a line.** Sentence length keeps climbing for as long as the book runs. The
pilot stopped at 25.0 because the pilot stopped, not because the climb finished. Under
this reading a 45-chapter book ends somewhere in the high thirties and the pilot looked
stable only because it was short.

**These make opposite predictions and the difference is measurable at chapter 20.**

## The prediction

    P1.  Mean sentence length in chapters 11-45 will be HIGHER than the pilot's
         chapter-10 value of 25.0 for the majority of chapters.

    P2.  The gain is front-loaded, not linear. Mean sentence length across chapters
         36-45 will be within about 3 words of the mean across chapters 26-35.
         If the curve is still climbing steeply at chapter 45, P2 is wrong.

    P3.  Sentence length will NOT track chapter length within this book. The pilot's
         climb was a change in prose style, not the same prose stretched over more
         room. LONG-CHAPTERS-HAVE-LONGER-SENTENCES would be FALSE.

P3 is the one that matters most, and it is the one the pilot could not test at all with
ten chapters in a 1.3x range. If sentence length tracked chapter length, the climb would
not be the prose getting older — it would be the same prose stretched over more room, and
the honest description of the pilot's curve would be "the chapters got longer on average",
which is a different and much less interesting claim.

### P3 was falsified before this book was written, against the published corpus

Checked on 2026-09-29, the same day, against `corpus/multivolume/` — six published
volumes, 303 chapters, real chapter boundaries. Correlation between a chapter's word
count and its mean sentence length, within each volume:

| volume | r |
|---|---|
| *Pride and Prejudice* | +0.10 |
| *Jane Eyre* | **−0.24** |
| *Wuthering Heights* | **−0.29** |
| *Middlemarch* | +0.11 |
| *Tess of the d'Urbervilles* | −0.09 |
| *Dracula* | +0.16 |

Median r = **0.00**, range −0.29 to +0.16. In published English fiction, sentence length
does not track chapter length, and where the relationship leans at all it leans
**negative** — the long chapters are not the ones with the long sentences.

**So the mechanism the pilot's curve was assumed to have is not a real feature of the
genre.** The climb in `muzzle-and-marrow` was not the same prose stretched over more
room, because that effect does not exist to be had. P3 as originally written predicted
the opposite and is recorded here as **falsified**, in advance, by a measurement that did
not involve this book at all.

This is the cheaper fix applied in time: the state is named before it can be mistaken for
a finding. Had this waited until chapter 45, the same correlation would have been
computed on our own manuscript, found weak, and explained — which is the shape of the
mistake this project has now made twice.

## How it gets checked

`check-uniformity.py` already prints a per-chapter mean sentence length next to the word
count, so this costs nothing to measure and needs no new instrument. Freeze 6 holds: no
gate is added for this.

Measured with the gate's own tokenizer, which is what produced the ten numbers above:

    python incunabula/tools/prose/check-uniformity.py "D:/KDP Books/marrow-light"

## What this is not

It is not a quality target and nothing is written to hit it. If the book comes out at 21
words per sentence throughout and reads better for it, that is a pass, and P1/P2/P3 are
recorded as broken along with the reason.

**Status at the time of writing:** P3 falsified in advance by the published corpus, as
recorded above. P1 and P2 remain open and will be measured on this book.

---

## RESULTS — recorded 2026-09-30, after the manuscript was finished

**The prediction above is unedited. Nothing in it was changed after chapter 38 was written,
and the three outcomes are reported as they fell, including the one that did not come out
clean.**

Measured with the gate's own tokenizer, the same instrument that produced the ten pilot
numbers this file was written from. 38 chapters, 78,070 words.

### P1 — HOLDS

> *Mean sentence length in chapters 11-45 will be HIGHER than the pilot's chapter-10 value
> of 25.0 for the majority of chapters.*

**24 of 28 chapters (86%) sit above 25.0.** Range 21.1 to 35.0, mean 28.95.

Prediction was "the majority." 86% is the majority, comfortably, and it is not marginal.

### P2 — HOLDS, on an incomplete window

> *Mean sentence length across chapters 36-45 will be within about 3 words of the mean
> across chapters 26-35.*

| window | chapters that exist | mean |
|---|---|---|
| 26-35 | 10 | 28.79 |
| 36-45 | **3** (chapters 36, 37, 38) | 29.63 |

**Difference: 0.84 words.** Prediction was "about 3." The observed difference is a quarter
of the predicted tolerance.

**This one is marked as holding but it is the weakest result in the file, and the reason
needs stating plainly: the second window is three chapters wide, not ten.** The book
finished at 38 chapters, seven short of the 45 this file was written against, so the window
36-45 could not be filled. **A three-chapter mean is a real measurement and it is a much
weaker one than a ten-chapter mean, and the margin (0.84 against a 3-word tolerance) is wide
enough that filling the window would not plausibly have broken the result.** But it would
have been better to have the ten, and the reason there are three is that the chapter count
was a quota that got withdrawn in September, which is recorded in
`artifacts/05-outline.md`, Amendment 1, and which was not known when this prediction was
written.

**The honest reading: P2 is supported, and the support is thinner than the prediction's
author had any reason to expect.** The prediction was written for a 45-chapter book. It was
measured on a 38-chapter one.

### P3 — FALSIFIED, as recorded in advance

Already falsified before chapter 1 was written, against six published volumes. The published
corpus is the relevant evidence for a mechanism claim and this book is not, so nothing here
reopens it. **It remains false: sentence length in published English fiction does not track
chapter length.**

### What the shape of the curve actually was

Not recorded in advance, and therefore not a prediction — but it is the first thing worth
knowing, and it is not what either reading anticipated.

| block | chapters | mean |
|---|---|---|
| Block I - II, opening | 11-19 | 28.34 |
| Block III, the archive | 20-28 | 28.93 |
| Block IV-V, the truth | 29-38 | 29.52 |

**28.34, 28.93, 29.52.** The whole climb from chapter 11 to chapter 38 is **1.18 words.**
That is not a curve and it is not a line. It is a book that arrives at its register almost
immediately and holds it for twenty-eight chapters with a drift of less than a word and a
quarter.

**The pilot's ten-point climb from 16.4 to 25.0 does not recur, and the likeliest reading is
that it was the pilot's first ten chapters rather than the pilot's method** — which is
exactly the shape of explanation this project has already had to withdraw once, on a
different subject, and it is offered here as a *hypothesis about another book*, explicitly
not as a finding about this one. **This file makes no claim about what the pilot's climb
was.** It would require measuring the pilot again, and nothing in this book can settle it.

### The honest summary

| | outcome | strength |
|---|---|---|
| P1 | holds | strong — 86%, well clear of "the majority" |
| P2 | holds | weak — 0.84 against a 3-word tolerance, on a 3-chapter window |
| P3 | falsified in advance, and correctly so | not applicable to this book |

**Two out of two open predictions held and the third was correctly killed before the book
was written. That is a better record than the predictions deserve** — both were cheap tests
on a number the gate prints for free, and the fact that they came out this way is evidence
about the *number being stable*, not about the *theory being right*. Nothing in this file
now supports a claim about how a book should be written. It reports what a book's sentences
happened to average, which is information, not guidance.


A prediction that can only be satisfied by writing badly is not a prediction, it is a
quota wearing a lab coat. The framework removed length numbers from drafting documents
for exactly this reason, and the same rule applies here: **this file is measured, never
written to.**
