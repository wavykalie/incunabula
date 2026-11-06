# Twelve residual tells: what to review first

From `analysis/run/report.md`, run of 2026-11-06: Arm B (15 Flash-high books) against Arm C
(87 human books, after the 120,000-word filter). B-17 is not in these numbers — it is
`B-deepseek` and held out of the pooled comparison.

Rows 1 and 2 are read from the corrected extractor (`analysis/run-v2/report.md`, same books and
same flags); every other row is unchanged from the v1 run. The correction and its reason are
`DECISIONS.md` §"Extractor v2".

A residual tell is a mechanical feature where the Arm B median sits outside the central 80%
of Arm C, at least 0.5 sdC away, with a permutation p under 0.05. Ranked by effect, which is
`|median_B − median_C| / sdC`: one unit means the pipeline sits one human-standard-deviation
from the human middle.

## The twelve, in review order

| # | feature | family | effect | B med | C band | books outside | pairs toward human | replication | len rho |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `str_open_weather_share` | structure | 3.51 | 0.100 | 0.000..0.085 | 9/15 | 12/15 | no | +0.12 |
| 2 | `syn_tag_breath_share` | syntax | 3.62 | 0.168 | 0.000..0.107 | 11/15 | 3/15 | no | +0.19 |
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

**1. Weather openers — the weaker of the two once the lexicon is corrected.** Nine of fifteen
books sit above the human band top of 0.085: B-10 (0.175), B-02, B-05 and B-08 (0.150), B-06,
B-07 and B-12 (0.125). But Arm A's median is 0.112 against Arm B's 0.100, and 12 of 20 naive
books clear the same top. After the correction this is a machine-prose habit that both arms
share, not something the B amendment added; v1's 4.84 was measuring interior temperature as
much as sky. The row stays in the twelve because the rule never tests Arm A. As a scanner
check it would flag naive and pipeline books alike; as a research row the question it leaves
is why both machine arms reach for weather first.

**2. Breath tags — the clearest new tell in the set, and it survives the corrected window.**
B's median is 0.168 against a band top of 0.107, and only 3 of 15 premise pairs moved toward
the human middle: the pipeline made this worse, it did not merely fail to fix it. Worst: B-09
(0.208), B-05 (0.191), B-03 (0.187), B-10 (0.186). The v2 window removed 2,657 borrowed tagged
turns and 317 breath tags without moving the arm medians — the habit is whisper and murmur as
the default said-bookism, not a counting artifact.

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
by another analysis pass. For two of them the reading found a defect in the extractor, which
was corrected as v2 and re-measured on all 145 books; v1 is preserved in `features/`, v2 in
`features-v2/`, and the numbers below are v2 unless a sentence says v1.

**Row 1, weather openers — half weather, half interior temperature.** All 97 v1 firings in the
fifteen primary books were printed and read; 59 survive the corrected lexicon. Of the 46 that
fall out, 27 are plainly not weather: object and body temperature ("the cold against the flat
of Tess's thumb", B-05 ch1; "a cold ceramic mug", B-12 ch8; "cold sweat", B-11 ch24), interior
heating (the woodstove's "pulsing crimson heat", B-05 ch21; "steam heat", B-06 ch17), the
proper noun *Cold Repository* (B-07 ch11 and ch12 — two counts for one place name) and "a
choking cloud" of silt (B-15 ch15). A further 18 are ambient temperature or bare `sun` ("the
attic garret was cold enough to freeze water in the washbasin", B-07 ch5; "the morning sun
streamed through the south-facing casement windows", B-05 ch38): a real descriptive habit, but
temperature and light rather than weather. One is a landscape `sun` (B-02 ch37). So v1 was not
four fifths weather; a third of its firings were a different habit wearing the same words.

The corrected lexicon:

```python
WEATHER = re.compile(r"\b(?:rain(?:ed|ing|s|y)?|snow(?:ed|ing|s|y)?|storm(?:s|ed|ing|y)?|"
                     r"fog(?:s|gy)?|mist(?:s|y)?|frost(?:s|y)?|thunder(?:s|ed|ing|ous)?|"
                     r"lightning|hail(?:ed|ing|s)?|sleet|drizzle|blizzard|gale(?:s)?|"
                     r"downpour|squall(?:s)?|overcast|cloudy|sunlight|sunshine|"
                     r"wind(?:s|y)?|clouds)\b", re.I)
```

with one rule beside it: a capitalised match counts only as the sentence's first word, which
drops *Cold Repository* without a list of names. `heat`, `cold`, bare `sun` and singular
`cloud` are gone deliberately — they are the words that matched stethoscopes, kettles and
metaphors.

Measured on Arm C (87 books, v2): median 0.000, p90 0.085, p95 0.121, maximum 0.222, with 9 of
87 books above 0.085. Arm A has 12 of 20 above that line and Arm B 9 of 15. The effect does
not survive as a B-versus-A claim — Arm B's median (0.100) is below Arm A's (0.112) and clears
the 80% band by 0.015, less than one chapter opening per book (0.59 of 40) — but it survives as
a machine-prose habit both arms share.

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

**Row 2, breath tags — a real habit, and the window defect is not what produced it.** v1
counted the breath-family speech verbs (whisper, murmur, gasp, sigh, sob, choke, croak, pant)
in a flat 80-character window after each closing quote; recomputed on the filed text it
reproduces every stored value. That window ran past the next opening quote: of 6,713 v1
"tagged turns", 4,056 survive once the window ends at the next quote, and breath tags fall
from 914 to 597. The borrowed ones belonged to the speaker below — B-09's "Can you breathe?"
*she demanded* charged "breathe" to the previous line — and a whisper opening the next line
was counted twice.

The correction changes the count, not the finding: whisper and murmur remain about four fifths
of breath tags, B's median rises from 0.163 to 0.168 against a band top of 0.107, the effect
is 3.62 sdC, 11 of 15 books sit outside the band, and only 3 of 15 premise pairs moved toward
the human middle. Literal breathing is still a minority of the matches (63 of 914 under v1),
and action beats ("Barnaby sighed", "allows the sheet to breathe") still count. The habit is
real and large — whisper and murmur as the default said-bookism — and the rate is now clean
enough to quote. It is first in the set by effect (3.62 against row 1's 3.51), marginally
ahead of weather; the numbering is left as filed so the rows keep one set of names.

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

## Baseline check: the twelve against C-dist-2 (2026-11-06)

Every row above sits on 87 human books, and several clear their band by a hundredth of a
share. So the baseline was doubled: 188 more Project Gutenberg novels, selected by the same
rule and disjoint by author (`corpus/dist-source-2.tsv`, `DECISIONS.md` §"C-dist-2"),
extracted with the v2 extractor, 167 of them under the 120,000-word filter. C-dist is still
the shipped threshold set; this is the sensitivity check.

| # | feature | B med | band, C-dist (87) | band, C-dist-2 (167) | effect v2 → C-dist-2 | verdict |
|---|---|---|---|---|---|---|
| 1 | `str_open_weather_share` | 0.100 | 0.000..0.085 | 0.000..0.086 | 3.51 → 3.07 | holds |
| 2 | `syn_tag_breath_share` | 0.168 | 0.000..0.107 | 0.000..0.108 | 3.62 → 3.14 | holds |
| 3 | `lex_ttr_rarefied` | 0.506 | 0.383..0.464 | 0.394..0.463 | 2.86 → 2.68 | holds |
| 4 | `lex_opener_top1_share` | 0.183 | 0.075..0.166 | 0.076..0.171 | 2.48 → 2.12 | holds |
| 5 | `lex_hedges_per_1k` | 0.090 | 0.820..2.434 | 0.712..2.183 | 2.00 → 2.24 | holds |
| 6 | `syn_para_cv` | 68.57 | 75.61..142.56 | 72.62..131.61 | 1.92 → 1.27 | holds |
| 7 | `lex_ly_adverbs_per_1k` | 5.26 | 7.77..16.97 | 7.55..16.05 | 1.81 → 1.88 | holds |
| 8 | `lex_ai_terms_per_1k` | 0.126 | 0.000..0.122 | 0.000..0.135 | 1.62 → 1.56 | **falls out** |
| 9 | `lex_opener_as_share` | 0.003 | 0.004..0.017 | 0.004..0.018 | 1.42 → 1.22 | holds |
| 10 | `lex_opener_but_share` | 0.009 | 0.011..0.059 | 0.013..0.056 | 1.42 → 1.14 | holds |
| 11 | `syn_long_sent_share` | 0.042 | 0.057..0.335 | 0.047..0.322 | 1.07 → 0.70 | **falls out** |
| 12 | `syn_sent_words_sd` | 10.01 | 11.42..25.49 | 10.27..23.87 | 1.04 → 0.96 | holds |

Ten of the twelve keep their band and their test on nearly twice the human sample, including
both rows re-read in the section above: weather's band moves by 0.001 and breath's by 0.0014,
while both effects shrink by 13–14% and stay three human SDs wide. That is the strongest
result in this memo: the two rows the matched-text audit touched are not baseline artefacts.

The two that fall out are informative rather than embarrassing. `lex_ai_terms_per_1k` is a
**primary endpoint**, and on the larger human sample the band top rises from 0.122 to 0.135,
which puts Arm B's 0.126 inside it. That agrees with the row-8 reading — the effect was
`profound` and domain words, not the calibrated tics — and it means the one primary row that
depended on a narrow human band no longer clears one. `syn_long_sent_share` still sits below
the new band (0.042 against a 0.047 floor) but its permutation p rises to 0.0585, so it fails
the test rather than the band: it was always the weakest row and its 1.07 effect was carried
by 87 human books.

One row enters: `str_scene_mark_per_1k` (B 0.04, band 0.05..0.45, effect 0.88, p 0.0089). It
was `fixed` on the smaller baseline and is outside on the larger one by a single hundredth.
That is the same margin problem in reverse, and it is why the band edges and not the verdict
labels are the thing to carry forward: a row within 0.01 of a band edge is a coin toss at
this n, whatever the table says.

Holdout false-positive rates on the new stratum, which is what a shipped threshold would have
to live with: weather 2% (z −1.6), breath 5% (z −0.8), AI terms 11%, adverbs 18%, hedges 18%,
TTR 18%, openers 14–15%, sentence-length SD 20%, long sentences 21%, paragraph CV 26%
(z +0.7). The two rows this study just corrected are also the two whose bands generalise
best to a fresh human sample.
