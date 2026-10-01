# Incunabula Score

The one scoring contract for the codex engine. Prompts, adapters, examples, reports,
and manual review all have to produce it the same way, or the number stops meaning
anything across runs.

## The question the score answers

> Would this book hold up against readers who are hard to please, agents who are paid to
> say no, and the specific market it claims to belong to?

When a literary target is active, the report also states whether the calibrated Fine
Press floor cleared it.

## When it may run

Never before phase 4 has finished. If phase 5 is active, the score waits until the loop
either approves the manuscript or names its blocker.

A Devil's Audit verdict of `MAJOR REWRITE` does not forbid publishing a provisional
number, but it does make the manuscript ineligible for approval regardless of the score.

## Ten dimensions

| # | Dimension | Weight |
|---|---|---|
| 1 | Originality | 1.1 |
| 2 | Theme | 1.0 |
| 3 | Characters | 1.2 |
| 4 | Prose | 1.0 |
| 5 | Pacing | 1.0 |
| 6 | Emotion | 1.1 |
| 7 | Coherence | 0.9 |
| 8 | Market | 0.8 |
| 9 | Voice | 1.1 |
| 10 | Opening | 0.8 |

### What each one is actually measuring

**Originality** — whether the premise, the angle, or the execution gives the reader
something they have not already had. Penalty for recognisable imitation of a recent
success.

**Theme** — how far the book's central question reaches past its own plot mechanics.

**Characters** — wound, want, need, self-contradiction, and whether the reader will still
be able to recall them a week later.

**Prose** — sentence control, precision, texture, and how much of the page is doing work
rather than explaining work already done.

**Pacing** — control of tension, variation between modes of scene, and whether the next
page keeps pulling.

**Emotion** — whether the book lands the feeling it was built to land.

**Coherence** — internal logic, continuity, and cause leading believably to effect.

**Market** — whether the comparisons are honest, the audience is legible, and the thing
could actually be packaged.

**Voice** — whether the narration is distinguishable from generic competence and whether
it survives page after page.

**Opening** — first-page grip, the promise chapter one makes, and whether the ending
ultimately keeps that promise.

## Rules of evidence

- competence is the assumed baseline, not excellence
- anything above 8.0 needs a citation behind it
- anything above 9.0 needs more than one
- citations are textual, structural, or grounded in reader impact — never vibes
- a self-scored run tends to read roughly 0.8 high; report the calibrated figure whenever
  the number is being compared to a stated threshold
- market legibility must never be allowed to paper over literary weakness when literary
  quality is what was asked for

## Arithmetic

- **Platen score** = the lowest single dimension
- **Weighted average** = the weighted mean across all ten

The Platen score carries more weight than the average on purpose: a book is only as good
as its worst dimension.

## Approval gate

All of the following, together:

- Platen score ≥ 8.5
- weighted average ≥ 9.0
- no dimension below 8.0
- every dimension carries evidence
- Devil's Audit is not marked `MAJOR REWRITE`
- if a Fine Press target is active, the calibrated Fine Press score is above it

## When it fails

1. Name the weakest dimension.
2. State the concrete intervention that would move it.
3. Check that intervention against the strong dimensions — a fix that damages two others
   is not a fix.
4. Rescore after the revision, from scratch.

## Report contract

`artifacts/09-incunabula-score.md` must contain:

- project and runtime context
- the dimension table with evidence for each row
- a calibrated dimension table when no outside human critique is attached
- Platen score
- weighted average
- Fine Press score and its threshold, when a target is active
- gate verdict
- weakest dimension
- the required intervention, or the approval note
