# Red team: the 50-novel prose-tell study (design v1)

Reviewed 2026-10-30 against the design as pasted, and against the instrument this
repository already owns (`tools/prose/`, `calibration/CALIBRATION.md`).

**Verdict.** The question is worth asking and the A/A/B/C pairing is the right shape. Four
problems would stop the study delivering what §10 promises, and three of them are cheap to
fix before generation and impossible to fix after it. The design's own instincts —
pairing, per-1k normalisation, "negative results are results", the §10 non-goals — are
sound and are not questioned here.

Nothing below disputes the *purpose*. It disputes whether 40 generated books plus ten
public-domain novels can produce a calibrated scanner check, which is the stated point.

---

## Blocking

### B1. Ten human books cannot set a threshold, and §10's deliverable is thresholds

`tools/prose/README.md` states the project's own rule about sample size, in the course of
refusing to derive a non-fiction floor: **"six volumes from five authors can refute a
floor, not set one."** Arm C is ten books. Every §10 candidate check needs a threshold
"derived from the human distribution", and §9.5 defines the residual tell as Arm B's
median sitting outside Arm C's interquartile range.

An IQR from ten books is the gap between roughly the 3rd and the 8th book. That makes it:

- **Insensitive.** For B (n=20) to clear C's IQR requires a gap of roughly 0.7–0.9 Arm-C
  standard deviations. Moderate tells will read "unclear" no matter how real they are.
- **Unstable at the boundary.** Each quartile of a 10-sample sits about a third of a
  standard deviation from its population value. A feature sitting near the rule's edge
  will classify differently on a different ten books, and the study has no way to say so.
- **Circular for the §10 false-positive test.** "How often does the check fire on Arm C
  itself?" is answered by construction when the check's boundary *is* Arm C. The question
  needs a human set held out from threshold derivation.

The precedent in this repo is exact and costly. `U4`'s 50–62% band was derived from one
dialogue-dense commercial corpus; across 140 public-domain novels the median is 33.2%,
**below its own failure line**, and 82 of 140 fail it. The row is now advisory because of
that measurement. A ten-book Arm C would have reproduced the original mistake with better
manners.

**Fix — split Arm C by job:**

| set | n | used for |
|---|---|---|
| **C-deep** | 10 books | excerpt rating (§8.6), face validity, close reading, the era-sensitive feature report |
| **C-dist** | ≥100 novels | every distribution, IQR, threshold and false-positive rate in §9 and §10 |

`calibration/fetch-multivolume.py` already fetches Gutenberg volumes (six are installed in
this checkout, 303 chapters, all 1813–1897), and `CALIBRATION.md` records a 140-novel,
13.06M-word public-domain set measured with this repo's own code (`check-arc.py` reproduces
its published distribution to three decimals). **That larger set is not in this checkout**
— `vermillion-study/` is referenced throughout the docs and is absent from every branch —
so locating or rebuilding it is a prerequisite for the C-dist run, not an assumption.
C-dist should be that set, re-measured through the study's frozen extractor and stratified
by era and genre. The study then says "threshold from n=140, excerpts from n=10", which is
defensible; "threshold from n=10" is not.

This also discharges most of §5's era warning, because era becomes a stratum instead of a
confound.

### B2. Six of the pre-registered features are already measured in this repo — as nulls, or backwards

§9.1 makes pre-registration the study's central credibility rule. Pre-registering a feature
this project has already measured as non-discriminating does not add credibility; it spends
20 pipeline runs re-deriving a published null.

| §8 feature | what this repo already measured | consequence |
|---|---|---|
| §8.2 sentence-length **uniformity** (burstiness) | published SD 9.5 / 10.1 / 10.4; project books 13.2 / 13.3 / 14.5 — machine prose *more* varied. VERMILLION: within-window burstiness identical to human, p = .72 | The within-document form is a measured null. The surviving form is **spread of mean sentence length across chapters** (`U2`). |
| §8.1 **type-token ratio** | length-confounded (flagged, not gated); VERMILLION measures machine prose as *more* varied, moving-avg TTR AUC 0.739, and one machine text out-varied all 140 novels | Must be rarefied to a fixed window, and the sign must be pre-declared as unknown, not assumed. |
| §8.2 **em dash** rate | `D1` is report-only because the AI control sits *inside* the published distribution (0.00/1k — the control writes `--`) | Measure it; do not hypothesise it as a tell. |
| §8.1/8.2 **rule of three**, correlatives | `D2` report-only for the same reason; `A5` ("not just X, but Y") fires on normal English at 0.61/1k in published prose | Same. |
| §8.3 **ending patterns / moral close** | `F1`: **0 of 50** published chapters close on a coda; one project book did it 6 of 11. Zero tolerance by *position*, not rate | This is a known, fixed tell. It belongs in the "fixed" column as a regression check, not a finding. |
| §8.1 **lexical variety / "AI vocabulary is impoverished"** | backwards: VERMILLION's sensory-density cue runs AUC 0.672 for the *machine* side; imprecise-abstraction cue has no signal (p = .16) | Drop "machine prose is less sensory / less varied" as a hypothesis entirely. |

The same record says what *did* survive, and it is a strong prior the design should adopt
rather than re-test from zero: **local syntax, clause moulds, punctuation variety,
structural repetition, positional tics, cross-chapter sameness, and arc direction.** Every
row that survived in this repo is one of those; every row that failed was a register
convention (word choice, paragraph shape, sensory density). §8 as written weighs heavily
toward the class that keeps failing.

**Fix:** mark the six rows above `already-measured` in the pre-registration, with the
number and the citation, and either drop them or convert them to *replication* rows
explicitly labelled as such — which is a legitimate, cheap thing to have in a study whose
headline claim is calibration.

### B3. Chapter-level features compare units that the two arms do not share

Arm A produces one continuous blob per book, or "Chapter One" headings the model chose.
Arm B produces `chapter-NN.md` files with titles, front matter and the pipeline's own
chaptering. The design then measures chapter-opening patterns (§8.3), chapter-length
variance, coda position, and per-chapter frames (§8.5) across arms — on units defined
differently by each arm.

This is not a small formatting detail. Chapter count and chapter length are exactly the
variables `U1`, `U3` and `U6` gate, and the repo has already been bitten by the milder
version of this (a `ch-NN.md` naming convention silently disabling six gates for a whole
book, `README.md` "Known tool defects" §0).

**Fix:** two different things, kept apart.

- **Chapter structure is an outcome**, measured per book and reported as such (count, CV,
  titles, opening type). It is a finding, not an analysis unit.
- **The analysis unit is uniform**: segment every book into fixed 2,500-word units on
  paragraph boundaries, in both arms, with the same splitter. Chapter-level rows
  (`U1`-style, opening-type, coda position) are computed on the book's *own* chapters and
  compared only as an outcome, never as a paired feature.

Also declare a single header-stripping rule (`^#` lines, YAML front matter, "Chapter N"
lines) and record both raw and analysis word counts, or the pipeline's front matter will
show up as prose in Arm B and not in Arm A.

### B4. The operator is an unmeasured treatment variable, and Arm A has no operator

Arm B, run "as it actually exists", includes human decisions: gate failures that require a
person, ductus approval, casting/voice approval, premise-ledger entries. The clone-lock
commit in this repo is explicit — *"a voice is designed once, approved by a human."*
`PRINTERS_COPY.md` §7 reserves certain threshold decisions to a person. Arm A has no such
steps.

§4 forbids human *rewriting*, which is right, but it does not bound human *deciding*, and
deciding is where a pipeline book gets rescued. Twenty Arm B books each receiving an
operator's judgment at gate failures is a large uncontrolled treatment that the design
currently attributes to "the pipeline."

**Fix: a written operator script, filed with the study.** The operator may only:

1. fill declared fields from the premise text verbatim where the pipeline asks for premise
   fields;
2. answer any gate prompt with the pipeline's own default or recommended option;
3. approve a ductus/voice/cast candidate without editing its text;
4. never write, rewrite, select between, or extend prose.

Every operator action is logged with a timestamp, and the *count and kind* of operator
interventions per book goes in the manifest as a covariate. If a book cannot proceed
without the operator writing prose, that is a stop condition (§13), not an intervention.

A related, cheaper point: if the pipeline's foundation phase rewrites the premise into its
own logline/beats, then B's input is no longer literally A's input. Log the divergence
(foundation logline vs premise text) per pair; it is both a validity check and, plausibly,
a finding.

### B5. The naive arm's protocol is not the naive condition it claims

A model asked for a 50,000-word novel writes a few thousand words and stops. So Arm A is
not "one prompt" — it is prompt-plus-N-continuations, where each continuation sees a
context window that may have truncated the beginning. That is a *specific* condition, and
it is not what a competent person actually gets (they ask chapter by chapter, in chat,
with a running summary).

The design permits continuation "only when the model stops" and forbids "new direction, no
reminders". That is faithful to the letter, and in practice it produces a book assembled
from rolling continuations of a truncating context — plausibly a *harder* condition than
naive human use, in ways that will show up as repetition and drift and will be attributed
to "naive generation."

**Fix:** choose the cadence and write it down before generation, because it is the single
largest procedural difference between the arms:

- fixed cadence: issue `Continue the novel from where you left off.` every time the model
  stops, with no other text, for both arms' naive equivalent — and record, per
  continuation, the response's prompt-token count and any truncation;
- identical for all 20 books;
- report continuations-per-book as a covariate, because a 40-continuation book and a
  6-continuation book are not the same object.

Do not "fix" this by giving Arm A a person who steers — that converts the control into an
operator arm and destroys the contrast with B4.

### B6. Length is a covariate, not only an outcome

§7 rightly says short naive books are data. But at 40,000 vs 55,000 words, many measured
features move for arithmetic reasons: n-gram repetition counts, TTR, cross-chapter spread,
chapter count, opening/closing similarity. The repo has already recorded the mirror-image
lesson in `L1`: *a rate is satisfied by a book that is shorter than intended.*

**Fix:** pre-declare a length-matched sensitivity analysis (drop the longest/shorter third
of each arm, or regress the feature on word count within arm) and report every headline
paired result both raw and length-adjusted. If a result survives only before adjustment,
it is a length finding.

---

## Major, non-blocking

### M1. §2's distance-closed formula is A−B, and its denominator is noisy

`(A − C) − (B − C)` reduces to `A − B`. That is fine as a *change*, but the "share of the
original gap" is `(A − B) / (A − C)`, and at n=10 `A − C` is estimated from ten books. For
features where Arm A already sits at the human median, the denominator goes to zero and
the share explodes. Pre-declare: share reported only when `|A − C|` exceeds a stated
threshold; otherwise the feature is reported as "no A-vs-C gap", which is a *result*
(the hypothesis died) and belongs in the report.

Also declare, per feature, which direction means "human". Without it the
fixed/partial/worsened classifier silently inverts for every rate where lower is better.
Several §8 features are genuinely two-sided (TTR, sentence-length variance, dialogue
share) and must be classified by *absolute distance* from the C median, not by sign.

### M2. §9.5, §9.6 and §10 disagree about "unclear"

§9.5 makes borderline features "unclear". §9.6's four categories have no "unclear", so every
feature must be one of fixed/partial/unchanged/worsened — which forces a borderline case
into a win or a loss. §10 then lists only residuals and fixed tells, so "unclear" features
leave the study entirely and are lost.

**Fix:** five categories everywhere, with "unclear" carrying an explicit definition (inside
the noise band, outside the effect-size floor), and a rule that unclear features are
*retained as a named list in the report* rather than dropped.

### M3. Multiple comparisons across ~60 features

Five families, twenty pairs, dozens of features. At α = .05 that is roughly three
false positives per family before any real effect. §9.7 says report families first, which
is right but is not a decision rule.

**Fix:** pre-declare **one primary endpoint per family** (I'd take: lexical hit rate pooled;
across-chapter sentence-length spread; coda-in-closing-paragraph share; cross-book first-name
reuse; opening-sentence similarity), test those with a stated procedure, and report all
other features as descriptive with confidence intervals. Benjamini–Hochberg within family
on the secondaries, and label every secondary "exploratory" on the face of it.

### M4. A feature *name* is not a measurement

§13 files the feature list before the script. This repo's arc gate is the standing argument
against that: four separate defects, each of which changed the number while the feature name
stayed correct — a hand-truncated lexicon (53 of 143 negative words dropped, mean moved
0.077), a different tokenizer, the wrong analysis window (0.08, "looking entirely
plausible"), and a machine corpus that had passed a boilerplate filter this code doesn't
reproduce.

**Fix:** pre-register each feature *with its formula and its tokenizer/regex*, i.e. freeze
the extractor's constants in the same commit as the feature list. Report each feature's
sensitivity to the two or three most plausible alternative operationalisations (quote
detection, sentence split, window size) as an appendix. That appendix is cheap and is what
makes a residual tell credible.

Related, concrete: three §8 families cannot be computed with this repo's current
instrument.

| §8 feature | status |
|---|---|
| adjective density, adjective-before-noun clustering | needs a POS tagger; none in this repo. New dependency, new calibration problem. |
| passive voice | no POS; only a `was/were + -ed/-en` proxy, which over-counts adjectival passives. Ship it as `proxy`, never as passive share. |
| gendered name distribution | no gender reference in this repo; `NAME_FREQUENCY.tsv` gives frequency tiers, not gender. Either add a reference dataset or mark unmeasured. |

Everything else in §8.1–8.5 is computable today from `measure.py`'s regexes,
`check-arc.py`'s lexicons/windowing, `check-uniformity.py`'s paragraph and frame logic,
`check-names.py`'s harvest plus `NAME_FREQUENCY.tsv`, and `check-dialogue-tags.py`'s quote
and tag sets. **Those should be imported, not reimplemented** — the `arc-units.py` idiom.

### M5. §8.6 blind rating is under-specified for the labour it costs

150 excerpts (3 × 50), 1,000 words each, four items each. Real raters read 150k words of
excerpt plus forms. Not stated: how many raters, inter-rater reliability, how disagreement
is resolved, or what happens to the 50 books whose excerpts were rated by only one person.

"no rater sees more than one excerpt from the same book **in sequence**" is not blinding —
over a 150-item sitting they will see the same book's other excerpts. Real blinding needs
one excerpt per book per rater and a design that crosses raters over books.

Also: excerpt *content* will dominate human-likeness ratings. A quiet 1,000-word interior
scene from a published novel will read as less "novel-like" than a fight scene from a naive
one. Random position sampling adds that variance deliberately.

**Fix:** stratify excerpts by position (one from each third, as designed) and *include
position as a factor in the analysis*; 3 raters minimum, report Krippendorff's α or
ICC per item; treat the free-text "felt off" codes as the primary qualitative output, since
they are what generates new candidate checks, and the 1–7 scores as secondary. If no pool
exists, drop the layer and say so — the design already says this, and it is right.

### M6. Two premises per genre supports no genre claim, and genre is the strongest covariate

Dialogue share, paragraph shape, em-dash rate and chapter length all move with genre far
more than with authorship. With n=2 per genre, genre can be *blocked* (it is, by pairing)
but never analysed, and any per-genre sentence in the report is a sentence about two books.

**Fix:** say so explicitly in §9 and forbid per-genre conclusions; report genre as a
blocking factor with a within-genre paired check as the sensitivity analysis (10 pairs of
2). Also record the pipeline's *declared* genre per Arm B book, since a mismatch between
the premise's genre label and the pipeline's genre handling is itself a finding.

### M7. Ductus: "neutral" is a register choice, and the caps were calibrated on one register

§4's shared neutral ductus removes the voice confound, and it is the right default. But a
neutral voice is still a register, and this repo's caps are tuned to a translated
light-novel register — `CALIBRATION.md` says so and says what it costs (a looser em-dash
cap than native prose would justify). If the neutral ductus sits outside the calibrated
register, Arm B will pass or fail gates for reasons unrelated to prose quality.

**Fix:** choose the test ductus to sit *inside* the register the gates were calibrated on,
file its text, and — if the budget allows — run a 2-ductus × 3-premise sensitivity arm and
report whether the conclusion survives a voice change. That is six books and it is the
single cheapest robustness test available.

### M8. Reproducibility: reuse the freeze mechanism this repo already has

`GATE_FREEZE.md` + `verify-freeze.sh` + `check-errata.py` already implement "a rule cannot
enter the pipeline because it was written down confidently" — dates, fields, append-only,
a rejected-measures registry that may not shrink. §4/§11 needs exactly that and should
adopt it rather than inventing a hash file: the study's freeze record is a gate freeze, and
the study's rejected features belong in the same registry `check-errata.py` guards.

Two operational notes from the repo's own defect log, both of which will bite this study:

- **Never read an exit code through a pipe.** `out=$(cmd); rc=$?`.
- **A run that read zero files is a failure, not a pass.** 40 books of generation with a
  mis-globbed output directory will otherwise produce a beautiful, empty dataset.

### M9. Unresolved in the design itself

- §12.6 ("both") is still open, and it changes the book count and the pairing. Not a
  review finding; it is the first thing to answer.
- §12.7 (executing AI and route) is open, and it decides whether the prompt logs in §3 can
  be reproduced at all.
- §6 says premises are sampled from a 40-premise pool "stratified by genre", but the pool
  itself is generated by whom, and against which model? For H3 (model fingerprint) to mean
  anything, the premise generator must not be the drafting model — otherwise premise
  idiom and drafting idiom share a source.

---

## What survives, unamended

Worth stating plainly, because a red team that only lists problems is a bad instrument:

- **Pairing A and B on the same 20 premises** is the strongest structural idea in the
  design, and nothing above weakens it.
- **Per-1k normalisation, raw counts retained** — right, and the repo's `L1` lesson is the
  reason.
- **The §10 non-goals** (not a humanizer, not detector evasion, not a claim about AI prose
  in general) are the most important paragraphs in the document. Keep them in the body of
  the report, not the appendix.
- **"Negative results are results"** and **"a candidate that shows no gap drops out"** are
  exactly this repo's rule about a threshold you have not measured, applied to a study.
- **The three-arm comparison is answerable at n=20/20/10** for large effects. It is a
  real study. It is just not a threshold-derivation study at that size.

## Amendment list, in order of when it must be decided

| # | amendment | decided before | cost if deferred |
|---|---|---|---|
| 1 | C-dist (≥100 novels) for all distributions and thresholds; C-deep (10) for excerpts | premise freeze | every §10 check is uncalibrated; the study produces a features list, not checks |
| 2 | Six already-measured features marked reported-null/replication, not hypotheses | pre-registration | 40 books spent re-deriving published nulls |
| 3 | Chapter structure = outcome; fixed 2,500-word segments = analysis unit | extractor freeze | chapter-level comparisons invalid across arms |
| 4 | Operator script + intervention counts in the manifest | first Arm B book | human rescue attributed to the pipeline |
| 5 | Naive continuation cadence fixed and logged | first Arm A book | arm is not the condition it claims |
| 6 | Length-matched sensitivity analysis pre-declared | pre-registration | results are length findings |
| 7 | Direction declared per feature; five categories incl. "unclear" | pre-registration | classifier inverts on some rows; unclear features vanish |
| 8 | One primary endpoint per family + BH on secondaries | pre-registration | headline chosen post hoc |
| 9 | Feature frozen *with* code/constants; operationalisation appendix | extractor freeze | a name is not a measurement |
| 10 | Excerpt design: raters, IRR, position as factor | Arm C assembly | 150k words of rating yields an anecdote |
| 11 | Test ductus inside the calibrated register; optional 2-voice sensitivity | first Arm B book | gate outcomes are register artefacts |
| 12 | Freeze record via `GATE_FREEZE.md`/`check-errata.py` conventions | first generation | freeze claim is a hash nobody verifies |

## The honest scope of what this design can deliver

With **no** amendments: a paired, pre-registered comparison of 20 premises across naive and
pipeline generation, against ten human calibration books, with mechanical features and a
small blind-rating layer. It can say *whether the pipeline moves prose toward or away from
this human sample*, per feature, with stated uncertainty. It cannot say what a scanner
threshold should be, and §10 should be rewritten to say so.

With amendments 1–3 at minimum: the same, plus calibrated candidate checks with human
baselines and false-positive rates, which is what §10 actually wants.
