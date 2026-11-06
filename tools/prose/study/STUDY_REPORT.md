# Pipeline-generated novels against a human distribution

### A paired, feature-based study of twenty premises, with two human baselines

**Status:** final report, 2026-11-06. Companion documents: `PREREGISTRATION.md` (feature
registry and rules; still a *draft*, not a frozen hash), `REDTEAM.md` (amendments B1–B6),
`DECISIONS.md` (protocol decisions, the extractor-v2 deviation and the C-dist-2 stratum),
`RUNBOOK.md` (operator procedure), `RESIDUAL_TELLS_MEMO.md` (the candidate-tell review),
`B17_RUN_REPORT.md` (the held-out cohort).

---

## Abstract

We ask whether a multi-phase generation pipeline moves prose toward or away from a measured
human distribution, and whether the difference can be expressed as candidate scanner checks
with human baselines and false-positive rates. Twenty premises were drafted by a naive continuing conversation (Arm A, n = 20); sixteen were
also drafted through the repository's own generation pipeline with its mechanical gates
(Arm B, n = 15, plus one self-drafted cohort book held out), so the paired comparison rests on
fifteen premises. Both arms were measured with a frozen 56-feature mechanical extractor against
109 public-domain novels (Arm C-dist), of which 87 fall under the 120,000-word analysis filter.

Twenty-nine features classify as `fixed` (Arm B's median inside the human band), seven as
`worsened`, eleven `unclear`, one `unchanged` and eight `descriptive`. Twelve features satisfy
the pre-declared residual-tell rule. Doubling the human baseline to a disjoint 167-book
stratum leaves ten of the twelve intact; an extractor correction that removed 2,657
mis-attributed dialogue tags and a third of the weather lexicon leaves both corrected rows
intact; residualising every feature on book length leaves the same ten intact. Two rows are
not stable: the AI-term rate, a primary endpoint, falls inside the wider human band, and the
long-sentence share fails the permutation test.

The two robust findings are narrow. The pipeline's dialogue is tagged with breath-family
verbs — whisper and murmur first — at 0.168 of tagged turns against a human band topping out
at 0.107, and only 3 of 15 premise pairs improved on their naive twin. Both machine arms open
chapters on weather approximately twice as often as human novels, but Arm A does so slightly
*more* than Arm B, so that row is a property of machine drafting in this setting, not of the
pipeline. Four of the five primary endpoints are null or backwards. Nothing here rates prose
quality, and no row is shippable as a check without the review §10 requires.

---

## 1. Introduction

Repositories that generate long fiction accumulate rules: lexical bans, dialogue-tag budgets,
structural gates. Those rules are usually justified by craft opinion. This study asks a
narrower, measurable question: when the same twenty premises are drafted naively and through a
pipeline, which counted properties of the resulting prose differ from a large sample of
published human novels, and which of those differences are stable enough to become a check?

The study contributes (i) a paired comparison that holds premise constant; (ii) a human
distribution large enough to set quantiles, with a held-out false-positive measurement; (iii)
an explicit account of two measurement errors found in the instrument itself, and of what
correcting them does to the findings; and (iv) a stability test in which the human baseline is
doubled. It does not contribute a quality judgement, a detector, or a claim about AI prose in
general.

## 2. Design

### 2.1 Arms

| arm | n | condition | drafting route |
|---|---|---|---|
| A, naive | 20 | one continuing conversation per premise, fixed continuation cadence, no steering | Gemini 3.8 Flash via subagents |
| B, pipeline | 15 | same premise through the repository's phase pipeline and mechanical gates, no ductus, operator limited to declared fields and gate defaults | Gemini 3.8 Flash via subagents |
| B-deepseek | 1 | pipeline, but operator and drafter are the same context | DeepSeek V4.1 Flash (held out) |
| C-dist | 87 of 109 | public-domain novels, one work per author | Project Gutenberg |
| C-dist-2 | 167 of 188 | a disjoint second public-domain stratum, same selection rule | Project Gutenberg |

Pairing is by premise id: A-01…A-20 against B-01…B-15. B-17 declares itself a cohort in its
manifest row (`cohort B-deepseek: operator=drafter`) and is excluded from every pooled
distribution and pair by `analyze.py` itself, not by a command-line flag; it is reported
against the same band in `analysis/run-v2/cohort-B-deepseek.md`.

### 2.2 Endpoints

Five primary endpoints were declared, one per family: `lex_ai_terms_per_1k` (lexical, lower is
human), `syn_chapter_sentlen_spread` (syntax, higher), `str_coda_share` (structure, lower),
cross-book first-name reuse (names, lower) and opening-sentence similarity (cross-book, lower).
Everything else is secondary and labelled exploratory; six features the repository had already
measured as nulls or with the opposite sign are marked `replication` and cannot become
findings.

### 2.3 Classification and the residual rule

Arm C's central 80% band (10th–90th percentile) and a robust SD (IQR/1.349) define five
classes: `fixed` (B's median inside the band), `worsened` (further from the human median than
A by more than 0.2 SD), `partial` (at least half the A-to-C gap closed), `unchanged` (B's
median within 0.2 SD of A's), and `unclear` (everything else, including the case where A
already sat at the human median — no gap to close, no credit to take). A **residual tell**
requires all three of: B's median outside the band, an effect of at least 0.5 human SD, and a
permutation p < .05 over 10,000 relabellings of the B-versus-C medians. Benjamini–Hochberg
within family is reported, not used as a fourth condition.

## 3. Corpora

Generated books: Arm A median 55,314 words (54,054–58,885), median 47 chapters; Arm B median
55,292 (54,560–57,458), exactly 40 chapters in all 15 books; B-17 64,593 words, 40 chapters.

Fifteen of the twenty premises have a complete pair. The route that drafted Arm B was
exhausted at B-15 (`DECISIONS.md`, the `B-deepseek` amendment): premises 16–20 were reassigned
to a cohort in which the operator is also the drafter, and only B-17 was filed before the study
closed. B-18 to B-20 have no manuscript, so the paired comparison is 15 of 20 premises, not
20, and Arm B's n is not a sampling decision.

Human baselines were built by a deterministic rule from the Project Gutenberg catalogue
(English, `Type=Text`, "Fiction" subject, poetry/drama/short-story headings excluded, one work
per author, round-robin across era × genre cells). C-dist fetched 109 novels; 22 exceed the
120,000-word filter, leaving 87. C-dist-2 selected 206, fetched 188 after 18 length rejections,
leaving 167, with zero author overlap with C-dist by construction. Era is an author-birth-year
proxy, not a publication year, and both strata are pre-1930 prose:

| stratum | born <1800 | 1800–29 | 1830–59 | 1860–89 | ≥1890 | unknown | words, median |
|---|---|---|---|---|---|---|---|
| C-dist (109) | 16 | 21 | 24 | 22 | 13 | 13 | 66,823 |
| C-dist-2 (188) | 26 | 26 | 36 | 38 | 34 | 28 | — |

The era confound is not repaired by either stratum. A 2026 generated novel is being compared
with Victorian and Edwardian prose, and no row in this study separates "machine" from
"modern".

## 4. Measures

Fifty-six features in four families (lexical 11, syntax 20, structure 15, names 10), computed
by `extract/features.py`, which imports the repository's shipped gate regexes rather than
copying them. Two features were corrected after the first measurement, as version 2
(`DECISIONS.md` §"Extractor v2"): the dialogue-tag window now ends at the next opening quote
instead of reading a flat 80 characters, and the weather lexicon is atmospheric only, with a
capitalised match counting solely as a sentence's first word. Version 1 values remain in
`features/` and `analysis/run/`; version 2 is in `features-v2/`, `analysis/run-v2/` and
`corpus/dist-features-2/`. Every number below is v2.

## 5. Results

### 5.1 Classification

| baseline | fixed | partial | unchanged | worsened | unclear | descriptive |
|---|---|---|---|---|---|---|
| C-dist, n = 87 | 29 | 0 | 1 | 7 | 11 | 8 |
| C-dist-2, n = 167 | 29 | 1 | 1 | 4 | 13 | 8 |

Half the registry lands inside the human band, which is the study's main negative result: the
pipeline's prose is not globally displaced on the measured rows. The rows that move are
specific.

### 5.2 Primary endpoints

| endpoint | A | B | C (n=87) | class | effect | p | C-dist-2 verdict |
|---|---|---|---|---|---|---|---|
| `lex_ai_terms_per_1k` | 0.036 | 0.126 | 0.050 | worsened | 1.62 | .0002 | **fails**: band top rises to 0.135, B inside |
| `syn_chapter_sentlen_spread` | 13.68 | 8.98 | 12.52 | unclear (no A–C gap) | 0.55 | .078 | fixed, p = .17 |
| `str_coda_share` | 0.00 | 0.00 | 0.00 | unclear (C has no spread) | 0.00 | 1.00 | unchanged |
| first-name reuse | 12.0/book | 5.7/book | 7.8/book | — | — | — | no separation |
| opening similarity, median | 0.07 | 0.07 | 0.04 | — | — | — | B = A |

Four of the five primary endpoints are null, backwards or uninterpretable; the fifth clears at
n = 87 and fails at n = 167. The AI-term row was
already the weakest of the twelve on inspection: its matches were `profound`, literal
`navigate` and literal `landscape`, none of which appear in the repository's calibrated tic
families, and it is measured with an ad-hoc lexicon the repo never calibrated. The names
endpoint is confounded by construction: reuse is counted at `max(2, 20% of the arm)`, so the
threshold is 3 books in Arm B, 4 in Arm A and 18 in Arm C-dist — a name must recur far more
often in the large human sample to count. Recomputed at a fixed threshold of two books, reuse
per book is 12.0 (A), 5.7 (B), 7.8 (C-dist) and 7.8 (C-dist-2): the expected direction is
absent, and the human top names are place and nationality tokens (*English*, *England*,
*French*, *London*), which the extractor's own docstring warns about.

### 5.3 Residual tells

Twelve rows satisfy the rule on C-dist; ten survive all three sensitivity analyses below.

| # | feature | B median | C band (n=87) | effect | p | C-dist-2 | length-adjusted effect |
|---|---|---|---|---|---|---|---|
| 1 | `syn_tag_breath_share` | 0.168 | 0.000..0.107 | 3.62 | .0001 | holds | 3.19 |
| 2 | `str_open_weather_share` | 0.100 | 0.000..0.085 | 3.51 | .0007 | holds | 2.86 |
| 3 | `lex_ttr_rarefied` | 0.506 | 0.383..0.464 | 2.86 | .0001 | holds | 2.79 |
| 4 | `lex_opener_top1_share` | 0.183 | 0.075..0.166 | 2.48 | .0001 | holds | 2.01 |
| 5 | `lex_hedges_per_1k` | 0.090 | 0.820..2.434 | 2.00 | .0001 | holds | 2.16 |
| 6 | `syn_para_cv` | 68.57 | 75.61..142.56 | 1.92 | .0001 | holds | 1.23 |
| 7 | `lex_ly_adverbs_per_1k` | 5.256 | 7.77..16.97 | 1.81 | .0001 | holds | 1.99 |
| 8 | `lex_ai_terms_per_1k` | 0.126 | 0.000..0.122 | 1.62 | .0002 | **fails** | inside band |
| 9 | `lex_opener_as_share` | 0.003 | 0.004..0.017 | 1.42 | .0004 | holds | 1.22 |
| 10 | `lex_opener_but_share` | 0.009 | 0.011..0.059 | 1.42 | .0003 | holds | 1.12 |
| 11 | `syn_long_sent_share` | 0.042 | 0.057..0.335 | 1.07 | .0044 | **fails** (p = .0585) | p = .057 |
| 12 | `syn_sent_words_sd` | 10.01 | 11.42..25.49 | 1.04 | .0038 | holds | 0.95 |

One row enters on the larger baseline: `str_scene_mark_per_1k` (B 0.036, band 0.05..0.45,
effect 0.88, p = .0089), `fixed` on the smaller baseline and outside the larger one by one
hundredth. A row within 0.01 of a band edge is not stable at this n in either direction, and
that caveat applies to entries 9, 10, 11 and 12 as much as to the entrant.

### 5.4 Cross-book rows

Arm B produces exactly 40 chapters in every book (chapter-count SD 0.00) where Arm A varies
(SD 9.35) and the human strata vary more (11.08). Part of that is a target, not a habit, but it
is the clearest structural signature in the study. Opening-sentence similarity is 0.07 median
in both generated arms against 0.04 in C-dist, with maximum 0.16 (A), 0.19 (B) and 0.57 (C) —
human novels share formulaic openings far more at the maximum, so the row does not support the
"pipeline reuses one opening shape" hypothesis.

Dialogue share moves in the opposite direction from the study's expectation: B 0.404, C 0.362,
A 0.254 (classified `fixed`, p = .43). The pipeline's books contain substantially more quoted
speech than their naive twins and slightly more than human novels.

### 5.5 Two measurement audits

**Dialogue tags.** Version 1 read 80 characters after each closing quote, which ran past the
next opening quote: of 6,713 turns it called tagged, only 4,056 survive the corrected window,
and breath tags fall from 914 to 597. The defect was in the count, not the finding: B's median
rises from 0.163 to 0.168. Whisper and murmur remain about four fifths of breath tags; literal
breathing was 63 of 914 in the v1 read, and action beats ("Barnaby sighed") still count.

**Weather openers.** Of 97 v1 firings, 59 survive the corrected lexicon. Of the 46 dropped, 27
are plainly not weather (object and body temperature, interior heating, the place name *Cold
Repository* counted twice, a metaphor's "choking cloud"), 18 are ambient temperature or bare
`sun` — a different habit — and 1 is a landscape `sun`. Arm B's median falls from 0.175 to
0.100 while Arm A's falls from 0.152 to 0.112, which inverts the ordering: the row is a
machine-drafting habit that the pipeline slightly reduces, not one it introduces.

## 6. Sensitivity analyses

### 6.1 Extractor correction

Reported in §5.5 and `analysis/run-v2/`. The residual set is unchanged at twelve; the ordering
of the top two swaps (breath 3.62 against weather 3.51).

### 6.2 Doubling the human baseline

C-dist-2 is a disjoint 167-book stratum under the same selection rule, derived through the same
extractor. Bands move by about 0.001 on the two audited rows and by fewer than four points on
any row measured in percent (paragraph CV, the largest, moves 3.0). Ten of twelve rows keep
band and test; the AI-term row and long-sentence share fall out, and one
row enters by a hundredth (§5.3). Held-out false-positive rates on the new stratum: weather
2% (z = −1.6), breath 5% (z = −0.8), AI terms 11%, openers 14–15%, adverbs/hedges/TTR 18%,
sentence-length SD 20%, long sentences 21%, paragraph CV 26%.

### 6.3 Length adjustment

Every feature was residualised on log10 word count fitted within Arm C-dist-2, and the full
classifier and permutation test re-run. Ten of twelve rows remain residual with effects between
0.95 and 3.19; the same two rows fail (AI terms inside the band, long-sentence share p = .057).
The result of interest is that breath tags (3.19) and weather openers (2.86) are not length
artefacts, despite Arm B's books being shorter than the human median.

### 6.4 Filing-check false positives

The two duplicate-detection checks used at filing time were measured on all 5,886 pairs of
unrelated human novels: 0 opening matches and 1 shared 24-word passage (0.017% of pairs, 2 of
109 books). At the primary arm's exposure (20 books, 190 pairs) the expected number of false
refusals is 0.032. The gates are quiet on unrelated prose; the one passage collision is a
genuine shared text (*The Pilgrim's Progress* quoted inside *Middlemarch*), which is the
correct behaviour.

## 7. Discussion

**What the pipeline actually does.** On the four families, the pipeline's prose lands inside
the human band on half the registry. Its drag is concentrated in register conventionsrather than syntax: it uses far fewer hedges (0.09 per 1,000 words against 1.31 in the larger
human stratum), fewer adverbs (5.26 against 11.89), less lexical variety at fixed window size, and it flattens paragraph
length and sentence-length variance. Those are the rows this repository's own gates are
designed to police, and the direction is toward *uniformity*, not toward any particular tic —
except the one it adds: breath-tagged dialogue.

**The one tell that survives everything.** `syn_tag_breath_share` survives the window
correction, the baseline doubling and the length adjustment, and 12 of 15 premise pairs moved
away from the human median. It is the only row that is both large and pipeline-specific. It is
also exactly the failure the repository's own `check-dialogue-tags.py` was written to catch
for a different reason, which suggests the instrument and the gate agree about what the
behaviour is.

**The row that looks biggest and is not pipeline-specific.** Weather openers are shared with
the naive arm and are slightly worse there. If a scanner adopted this row it would fire on
naive generation too, and any user reading it as evidence of pipeline behaviour would be
mistaken.

**Primary endpoints mostly failed.** Four of five are null, backwards, or uninterpretable, and
the one that cleared at n = 87 (AI terms) does not clear at n = 167. The honest reading is
that the study's headline claims are not carried by its primary endpoints but by the residual
sweep — which is worth stating plainly, because a pre-registration that is wrong is a result,
not a problem to be managed.

## 8. What this study cannot claim

- It does not rate quality. There is no human rating layer; decision 5 of `DECISIONS.md`
  dropped it and no LLM judge substitutes. No row says a book is good or bad.
- It is not a humanizer, a detector-evasion benchmark, or a claim about AI prose in general.
- It cannot separate era from machine. Both human strata are pre-1930; the generated books
  are 2026. Every row is potentially era-driven, and the C-dist-2 stratum tests stability,
  not era.
- It cannot speak about voice sensitivity. The voice arm (`analysis/voices.py`) requires
  `B-NNV`/`B-NNW` twins that were never drafted; the script exits 2 and the arm is empty.
- It cannot support genre statements: two premises per genre is a sentence about two books.
- Its Arm B estimate rests on one model, one route and fifteen books; the sixteenth is a
  self-drafted cohort that cannot be pooled with them, and premises 16–20 have no complete
  pair — four planned books were never produced.
- Its names rows are a proper-noun inventory, not a cast list; place and nationality tokens
  dominate the human top names.
- A null at n = 15 pairs is not evidence of absence. The registry is 56 rows; at α = .05
  roughly three would clear a test by chance before any real effect, which is why every
  secondary is labelled exploratory and BH-corrected within family.

## 9. Reproducibility

Every number above is produced from committed feature trees and committed run outputs.

```bash
cd tools/prose/study
python extract/features.py --selfcheck
python extract/features.py --all books --out features-v2          # 145 books
python analysis/analyze.py --features features-v2 --manifest books/manifest.csv \
    --out analysis/run-v2 --max-words 120000 --exclude-books V,W
python corpus/fetch-dist.py --check                               # C-dist: 109, 0 problems
python corpus/fetch-dist.py --check --log corpus/dist-fetch-log-2.tsv  # C-dist-2: 188
python analysis/cdist.py --features corpus/dist-features-2 --out corpus/dist-features-2
python analysis/check-fp.py --selftest                            # filing-check machinery
python analysis/length-adjusted.py                                # the B6 sensitivity
```

The baseline-doubling run is `analysis/run-cdist2/`; the length-adjusted run residualises each
feature on log10 words within Arm C-dist-2 and re-applies the primary classifier. Texts are not
committed: `books/C-*/` is git-ignored, and only counts, hashes and feature values are tracked.

## Appendix A — registry status

| family | features | primary | replication |
|---|---|---|---|
| lexical | 11 | 1 | 1 |
| syntax | 20 | 1 | 4 |
| structure | 15 | 1 | 0 |
| names | 10 | 0 (reuse is arm-level) | 0 |
| cross-book | 6 rows | 2 | 0 |

## Appendix B — artefact index

| artefact | what it holds |
|---|---|
| `analysis/run-v2/` | primary analysis on C-dist, n = 87, extractor v2 |
| `analysis/run-cdist2/` | the same analysis on C-dist-2, n = 167 |
| `corpus/dist-features/` | C-dist baseline table, extractor v1 (shipped thresholds) |
| `corpus/dist-features-2/` | C-dist-2 feature tree and `cdist.csv` |
| `analysis/filing-checks-fp.md` | duplicate-check false positives on 5,886 human pairs |
| `analysis/run-v2/cohort-B-deepseek.md` | B-17 against the same band, never pooled |
| `RESIDUAL_TELLS_MEMO.md` | per-row review, the measurement audits, the baseline check |
| `DECISIONS.md` | protocol decisions, extractor-v2 deviation, C-dist-2 stratum |

## References

Internal to this repository: `PREREGISTRATION.md`; `REDTEAM.md`; `DECISIONS.md`;
`RUNBOOK.md`; `RESIDUAL_TELLS_MEMO.md`; `B17_RUN_REPORT.md`; `ARM_B_BRIEFING.md`;
`corpus/SOURCE_POLICY.md`; `analysis/filing-checks-fp.md`; `calibration/CALIBRATION.md`;
`tools/prose/check-dialogue-tags.py`; `tools/prose/check-uniformity.py`;
`tools/prose/check-arc.py`; `tools/prose/calibration/measure.py`.
