# Twelve residual tells: what to review first

From `analysis/run/report.md`, run of 2026-11-06: Arm B (15 Flash-high books) against Arm C
(87 human books, after the 120,000-word filter). B-17 is not in these numbers — it is
`B-deepseek` and held out of the pooled comparison.

A residual tell is a mechanical feature where the Arm B median sits outside the central 80%
of Arm C, at least 0.5 sdC away, with a permutation p under 0.05. Ranked by effect, which is
`|median_B − median_C| / sdC`: one unit means the pipeline sits one human-standard-deviation
from the human middle.

## The twelve, in review order

| # | feature | family | effect | B med | C band | books outside | pairs toward human | replication | len rho |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `str_open_weather_share` | structure | 4.84 | 0.175 | 0.000..0.083 | 12/15 | 8/15 | no | +0.04 |
| 2 | `syn_tag_breath_share` | syntax | 3.72 | 0.163 | 0.002..0.090 | 11/15 | 1/15 | no | +0.14 |
| 3 | `lex_ttr_rarefied` | lexical | 2.86 | 0.506 | 0.383..0.464 | 15/15 | 0/15 | **yes** | −0.02 |
| 4 | `lex_opener_top1_share` | lexical | 2.48 | 0.183 | 0.075..0.166 | 10/15 | 4/15 | no | −0.11 |
| 5 | `lex_hedges_per_1k` | lexical | 2.00 | 0.090 | 0.820..2.434 | 15/15 | 9/15 | no | +0.16 |
| 6 | `syn_para_cv` | syntax | 1.92 | 68.57 | 75.61..142.57 | 0/15 | 1/15 | no | +0.10 |
| 7 | `lex_ly_adverbs_per_1k` | lexical | 1.81 | 5.26 | 7.77..16.97 | 12/15 | 14/15 | no | +0.14 |
| 8 | `lex_ai_terms_per_1k` | lexical | 1.62 | 0.126 | 0.000..0.122 | 8/15 | 5/15 | no | +0.11 |
| 9 | `lex_opener_as_share` | lexical | 1.42 | 0.003 | 0.004..0.017 | 12/15 | 12/15 | no | −0.00 |
| 10 | `lex_opener_but_share` | lexical | 1.42 | 0.009 | 0.011..0.059 | 12/15 | 13/15 | no | +0.15 |
| 11 | `syn_long_sent_share` | syntax | 1.07 | 0.042 | 0.057..0.335 | 0/15 | 0/15 | no | −0.05 |
| 12 | `syn_sent_words_sd` | syntax | 1.04 | 10.01 | 11.42..25.49 | 1/15 | 1/15 | **yes** | −0.08 |

"Books outside" counts books whose own value leaves the band, which is a different question
from whether the median does. Rows 6, 11 and 12 have a median outside the band and almost no
book outside it: those are arm-level effects, and a reviewer chasing them through single
chapters will not find the thing that moved.

## What to check, row by row

**1. Weather openers — the strongest and most book-like.** 12 of 15 books open chapters on
weather or time-of-day far more often than humans: B-07 (0.275), B-08 (0.250), B-05 (0.225)
against a human band topping out at 0.083 and a human median of 0.000. Check whether this is
a chapter-opening reflex ("the rain had not stopped", "morning came") or the premises'
setting doing the work. Read the first paragraph of ten chapters across B-07 and B-08 and
count how many start on sky, light or hour. If the count matches the feature, it is a real
habit and a good candidate for a check.

**2. Breath tags.** B sits at twice the top of the human band, and in 14 of 15 premise pairs
Arm A was closer to the human middle than Arm B was — the pipeline made this worse, it did
not merely fail to fix it. Worst: B-09 (0.228), B-07 (0.183), B-05 (0.182). Check that the
extractor is counting dialogue tags ("she let out a breath", "he breathed") and not literal
breathing in action. If it is tags, this is the clearest new tell in the set.

**3. Rarefied vocabulary — replication row, do not act yet.** All 15 books sit above the
band, in every one of 15 pairs. But this is a feature the repo has measured before as a null
or with the opposite sign. Before it becomes a check, re-measure at a second rarefaction
depth and confirm the direction holds; if it flips with depth, the tell is an artifact of the
depth and not of the prose. Exemplars: B-03 (0.533), B-15 (0.529).

**4. Paragraph-opening repetition.** `lex_opener_top1_share` at 0.183 is what the pipeline
default is set to and the humans are at 0.105. B-12 (0.258) and B-15 (0.215) are the worst.
Check which word is doing the repeating in the worst books before deciding this is a tell —
a book with one recurring narrator and one recurring setting will score high legitimately.

**5. Hedges — the most interesting row, and not obviously a defect.** Humans hedge at 1.386
per 1,000 words; the pipeline is at 0.090, which is 36× lower and below *every* human book.
This may be the one residual that is a prose-quality difference rather than a mechanical
habit: human narration qualifies itself ("perhaps", "I think", "sort of") and the pipeline
almost never does. Check whether removing hedges is what the pipeline's own gates encourage —
if a gate penalises hedging, this row is a gate design question, not a scanner check.

**7. Adverbs — already moving in the right direction.** Arm A was at 3.52, Arm B at 5.26, the
human middle at 11.24. The pipeline closed part of the gap and stopped outside the band, so
the class is `unclear`: improved but not enough, not a fresh tell. Worth a look only to see
whether the remaining gap is a rule the pipeline enforces (adverb budgets) that humans do not
observe.

**8. AI vocabulary.** 8 of 15 books outside, worst B-06 (0.422 per 1,000), B-04 (0.347). Post
`deslop-check`, this should be near zero. Print the matched terms for B-06 and B-04: if they
are `delve`/`tapestry`/`testament` the deslop list has a hole; if they are domain words
("signal", "channel") the extractor's term list needs the exclusion. Settled below: neither.
The remainder of this file records the three checks that were worth running.

**9 and 10. Human opener habits the pipeline does not share** — `As …` and `But …` sentence
openers. Humans open 0.4% and 3.2% of sentences that way; the pipeline 0.3% and 0.9%. In 13
of 15 pairs Arm A was already closer to the humans than Arm B. Treat both as one finding:
the pipeline avoids two constructions humans use freely. Check a chapter from a human book
and one from B-14 side by side, and decide whether the absence is a style choice worth
keeping.

**6, 11 and 12. Arm-level, not book-level.** Paragraph-length variance, long-sentence share
and sentence-length variance all have a median below the band with almost no individual book
outside it. That pattern means the distribution is shifted for the arm as a whole, and the
cause is a house style (uniform paragraph length, uniform sentence length), not a raisable
per-book flag. Each is marked `replication` where the repo has measured it before. Check one
thing only: whether the same 40-chapter shape and similar word targets make paragraph length
uniform by construction.

## What this memo is not

Mechanical features find tells; they do not judge whether a book is good. A residual here is
a hypothesis with a number attached, not a defect. Three of the twelve are arm-level, two are
replication rows that need a fresh measurement before anyone touches the pipeline, and the
hedge row may be a gate design question. The remaining seven are specific enough to check by
reading named books, and rows 1, 2, 4 and 8 are the ones where a grep on the text can settle
the question in an afternoon.

Before any of these becomes a scanner check it still needs what RUNBOOK §10 asks for: a human
baseline measured on C-dist,a threshold derived from that corpus, a false-positive rate measured on it, and Kalie's review.

## Checks run on the matched text (2026-11-06)

Three rows were cheap enough to settle by reading what the regex actually matched rather than
by another analysis pass. The extractor was not changed and no feature was re-measured; these
are readings of the frozen features against the filed text.

**Row 1, weather openers — a real habit, and not one Arm B introduced.** Every firing in the
fifteen primary B books was printed and read: 97 chapter openings, about a fifth of which are
not weather. The false positives are one consistent class — object temperature
and interior heating ("the cold against the flat of Tess's thumb", B-05 ch1; "a cold ceramic
mug", B-12 ch8; "cold sweat", B-11 ch24; the woodstove's "pulsing crimson heat", B-05 ch21),
the proper noun *Cold Repository* (B-07 ch11 and ch12, two counts for one place name), and "a
choking cloud" of silt (B-15 ch15). B-09 loses four of its nine firings to this class. The
other four fifths are genuine scene-setting weather, often the first thing the chapter says:
"The rain began at midnight" (B-07 ch17), "The first autumn frost fell from the gray sky"
(B-08 ch10), "At twilight, the snow began to fall over Antwerp" (B-09 ch38).

So the feature measures a real textual habit. What it does not measure is an Arm B effect:
Arm A's median is 0.152 with 17 of 20 books outside the same band; Arm B's is 0.175 with 12
of 15. The 4.84 effect is a distance from the human corpus that the baseline arm already has.
Row 1 belongs in a list of pipeline tells, not in a list of things the B amendment caused —
the memo's "8/15 A outside" column was the hint.

**Time-of-day openers — the feature is not measuring time of day.** `str_open_time_share` is
a temporal-preposition test (`^(when|at|on|in|by|that|the next|later|after|before|each|every|
it was|for)`), and 9 of its 95 firings are locative ("At the base of the flowstone cascade",
"In Room 14b", "In clinical veterinary cardiology"). The reading is still sound: 90% of
firings are temporal and the habit is unmistakable where it appears — B-04 opens 13 of 40
chapters on a clock time ("At ten minutes past four", "At half-past one that afternoon"),
B-11 13 of 40 ("On Tuesday morning at 11:20 AM", "By 08:40 AM"), B-14 11 of 40, and all six
of B-12's firings are clock times.
That is a real timestamp-opening habit. It is also entirely an Arm A habit: A's median is
0.186, B's 0.150. There is no B-vs-A difference to explain, which is why the row is not in
the twelve.

**Row 2, breath tags — real habit, wrong denominator.** The feature counts the breath-family
speech verbs (whisper, murmur, gasp, sigh, sob, choke, croak, pant) in an 80-character window
after each closing quote; recomputed on the filed text it reproduces every stored value.
Across the fifteen primary books: 914 such tags on 6,713 tagged turns, and whisper plus murmur
are about four fifths of them. Literal breathing is 63 of 914, or 6.9%.

Two defects matter more than the label. First, 317 of 914 (35%) are counted against a quote
after a *second* opening quote has already appeared in the window: the tag belongs to the next
speaker's line, and sometimes the matched verb is inside that line's speech — B-09's "Can you
breathe?" *she demanded* counts "breathe" as a tag on the previous quote. Second, the
remaining literal-breath hits include action beats: "Barnaby sighed", "breathing in the scent
of chamomile", "allows the sheet to breathe".

The habit is real and large — whisper and murmur as the default said-bookism, B 0.163 against
A 0.080 and humans 0.031, worst B-09 at 0.228 — but the metric should not become a check
until its window stops at the next quote. As an observation it is usable; as a rate it is 35%
noise, and the noise sits in exactly the dialogue exchanges that carry the habit.

**Row 8, AI vocabulary — not a hole in the deslop list.** The matched terms for the two worst
books:

```
B-06  profound 12, navigate 6, navigating 2, landscape 1, in the heart of 1, a world where 1  (23)
B-04  profound 11, landscape 4, vibrant 2, navigating 1, a world where 1                    (19)
```

No `delve`, `tapestry`, `intricate`, `testament` or `resonate` in either book: after
`deslop-check` the calibrated tics are gone. What remains is the extractor's own ad-hoc list
(the `AI_TERMS` tuple in `extract/features.py`), which includes ordinary English. `navigate`
is literal in B-06 — a book about a blind theatre interpreter, "navigate a flight of
twenty-two metal stairs", "navigate street crossings". `landscape` is literal geography in
B-04: "the physical landscape appeared before him", "landscape gardeners". `profound` is
purple, not AI, and it is half of both books' counts.

That leaves a real but narrower finding: Arm B uses `profound` eleven or twelve times a book,
where Arm A's entire AI-term median is two hits. The row is measuring one intensifier habit,
not AI vocabulary, and it is measuring it with a lexicon the repo never calibrated — the
calibrated families in `calibration/measure.py` (A1, A3) contain none of `profound`,
`navigate`, `landscape` or `vibrant`. If the row is kept, it should use those families; if a
check is wanted, `profound` is the word, not `delve`.
