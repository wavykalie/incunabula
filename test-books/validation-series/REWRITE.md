# Merope 1 and 2 — rewrite through `DRAFTING_FRAMEWORK.md`

Both books, end to end, 2026-09-28. This is the second book the framework has been tested
on, which is the bar it was written to clear: one book is not evidence.

## What the framework claimed, and what happened

The framework says chapters are not sized, they **end** — so a book carrying no length
targets should still show a wide spread after a prose repair. If the spread collapsed, the
spread would have been coming from the targets rather than from content, and the premise
would be wrong.

Measured on the gate's own word count, before and after:

| book | range before | range after | CV before | CV after |
|---|---|---|---|---|
| Merope 1 | 478 – 2,304 (4.8×) | 475 – 2,304 (**4.9×**) | 40.9% | **41.0%** |
| Merope 2 | 519 – 2,406 (4.6×) | 519 – 2,393 (**4.6×**) | 40.0% | **39.9%** |
| The Trick | 1,460 – 3,442 (2.4×) | unchanged | 23.7% | 23.7% |

The spread survived the repair, and moved slightly wider. Sixteen cuts were made to fix a
prose tic and **not one of them was a chapter that had been sized**: the repairs were
subtractive (Merope 1: 15,391 → 15,377 words; Merope 2: 14,994 → 14,962), which is what
"as long as the thing takes, and not a word more" predicts. For contrast, The Trick still
shows 2.4× — the book that *had* targets, unchanged and untouched.

## What the terminal sweep found

Both stubs were read whole, because the judgement is whether a chapter **ends** or merely
stops:

- **Merope 1 ch10 (475 w).** The departure. Opens on "I steered us out", states the
  withheld thing plainly — *she flies it, and I narrate as though I do* — and ends on the
  light that does not change because they are above it. The withholding is **spent**, not
  deferred. Legitimate stub. This is the chapter `DRAFTING_FRAMEWORK.md` names as its own
  worked example, and the framework's claim about it survives contact with the text.
- **Merope 2 ch06 (519 w).** Three questions, the third built so that any answer is a
  trap, and Achird answers a different question than the one asked. Ends on "I do not know
  when I stopped being able to tell the two halves apart." Legitimate stub.

No filler and no quota chapters. `check-length.py` exits **2 — not run, never pass** —
because neither book declares a target length, which is the framework's outcome and an
independent confirmation that no targets survive in these projects.

## What the repairs were

Sixteen cuts across ten chapters, all by hand, none by regex substitution. Every rewrite
folded a negation into a positive statement rather than deleting meaning:

| | chapters | row | cuts |
|---|---|---|---|
| Merope 1 | 01, 05, 07, 08, 10 | P1 anaphora, A25 antithesis | 6 |
| Merope 2 | 03, 07, 09, 10, 11 | A25, A6, P1 | 10 |

The representative case is Merope 1 ch07, which needed three of four antithesis hits cut.
The fourth is Achird's dialogue — `"It is not watching. It is the same movement every
time."` — and it stays, because a character's voice is the one place the construction is
doing work rather than being a tic. Every other instance became a positive sentence:
`It is not arranged for a guest. It is arranged around one.` → `The arrangement is around a
guest, not for one.` Same claim, one clause, sharper.

**The antithesis tic is the real defect, and it is pipeline-wide.** Read out one at a time,
24 of 25 A25 hits across both books are the genuine construction. This is the same tic the
user identified in The Trick and it is the dominant prose failure in two independently
written books — which is a fact about the drafting habit, not about either manuscript.

## What blocked it, and is the more useful result

The rewrite could not start, because **the gate was not reading the files.** Two defects,
both in `deslop-check.sh`, both found only by running it on a book it had never been run
on. Neither was visible to a control, because both sat *under* the caps.

1. **The sentence tokenizer was blind to a stray CR.** It splits on `[.!?] ` — punctuation
   followed by a *space* — and 15 of 22 chapters carried `\r\r\n`, so the split never
   happened. The awk counted 22 sentences in a chapter that has 43. Two chapters read `ok`
   and read `FAIL` once normalised. They were not passing; they were evading.
2. **A25 matched inside a word.** No boundary after `not`, so `was NOTHING in it worth the
   walk. It was ...` matched. 24 of 25 hits are real; that one is a substring accident.

Both are fixed under **Freeze 7**, recorded in `GATE_FREEZE.md`, with the regression table.
The correction is to the read path and one character of regex: no cap moved, no rule added,
no gate added. `demo-magician` is byte-identical across all 79,204 bytes of its output; the
slop fixture still fails; `verify-freeze.sh` holds 15/15.

**The lesson is the general one and it is not about line endings:** *a gate's controls test
its thresholds, and nothing tests whether it is reading the file.* Thirty thousand words were
passing the wrong way, and the thing that found it was reading the chapters.

## Status

    deslop-check.sh    book-1 exit 0, book-2 exit 0, demo-magician exit 0
    check-uniformity   book-1 exit 0, book-2 exit 0   (U1 ok 41.0% / 39.9%)
    check-length       exit 2, NOT RUN - no target length declared, which is correct

**Open, deliberately:** U6 warns `"stall"` in 4/11 chapters (36%) on both books — a warn, not
a failure, with the fail line at 40%. Per `maintenance/FULL_SWEEP.md` there is no fourth
bucket, so this is a decision to make at the sweep rather than a per-chapter repair now.
Book-2 also reports `"antithesis"` in 4/11, which is the tic above seen from the other side
and is expected to fall as drafting practice changes rather than to be chased by hand.

**Not yet done:** the epubs in `book-1/dist` and `book-2/dist` predate this rewrite and must
be rebuilt before either book ships, so their PDFs and EPUBs do not carry the old text.
