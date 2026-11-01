# Pre-registration (draft — not yet frozen)

**Status:** draft, 2026-10-30. This file and `extract/features.py` are frozen together,
before any book is generated (design §9.1, §13). Freezing means: hash both, record the
hash in the manifest, and treat any later change as a protocol deviation. A feature whose
name is pre-registered and whose code is not is not a measurement — this repo's arc gate
shipped four defects without its name ever changing (REDTEAM.md M4).

```
sha256(PREREGISTRATION.md || extract/features.py)   # computed at freeze, recorded in manifest
```

## 1. Primary endpoints (one per family)

Everything else exists to be reported. These five are the claims the study is allowed to
headline, and the only rows where a family-level statement is made.

| family | endpoint | direction | why this one |
|---|---|---|---|
| lexical | `lex_ai_terms_per_1k` (pooled §8.1 list) | lower | the design's own starter set, measured against humans rather than assumed |
| syntax | `syn_chapter_sentlen_spread` | higher | the *surviving* form of the uniformity hypothesis. Within-document burstiness is a measured null (REDTEAM.md B2); the across-chapter spread is `U2`, which separates published prose from this project's books |
| structure | `str_coda_share` | lower | `F1`: 0 of 50 published chapters close on a coda, 6 of 11 in one project book. A positional tell, not a rate |
| names | cross-book first-name reuse (arm-level, `reuse_rate`) | lower | the row a per-book scanner cannot compute at all, and the study's clearest contribution |
| cross-book | opening-sentence similarity, median pairwise | lower | premise cannot explain the same opening shape in two unrelated books |

The names and cross-book endpoints are arm-level. They are compared as distributions
(Arm B's reuse count against Arm C's), not paired per premise — no human book shares a
premise, and pretending otherwise would be a pairing that does not exist.

## 2. Feature status

`primary` = §1. `secondary` = reported, BH-corrected within family, never headlined.
`replication` = already measured in this repo as a null or with the opposite sign; the
study re-measures it to confirm, and it cannot become a finding.
`descriptive` = a book-level outcome with no human direction; reported, never scored.

### lexical (11)

| feature | direction | status |
|---|---|---|
| `lex_ai_terms_per_1k` | lower | **primary** |
| `lex_ai_term_hits` | lower | secondary (raw count behind the rate) |
| `lex_ly_adverbs_per_1k` | lower | secondary |
| `lex_hedges_per_1k` | lower | secondary |
| `lex_opener_and_share` | lower | secondary |
| `lex_opener_but_share` | lower | secondary |
| `lex_opener_as_share` | lower | secondary |
| `lex_opener_when_share` | lower | secondary |
| `lex_opener_suddenly_share` | lower | secondary |
| `lex_opener_top1_share` | lower | secondary |
| `lex_ttr_rarefied` | twosided | replication — machine prose measures *more* varied (VERMILLION AUC 0.739) |

### syntax (20)

| feature | direction | status |
|---|---|---|
| `syn_chapter_sentlen_spread` | higher | **primary** (`U2` form) |
| `syn_sent_words_mean` | twosided | secondary |
| `syn_sent_words_median` | twosided | secondary |
| `syn_sent_words_sd` | twosided | replication (burstiness, measured null) |
| `syn_short_sent_share` | twosided | secondary |
| `syn_long_sent_share` | twosided | secondary |
| `syn_em_dash_per_1k` | twosided | replication (`D1` report-only: control inside the human distribution) |
| `syn_semicolon_per_1k` | twosided | secondary |
| `syn_colon_per_1k` | twosided | secondary |
| `syn_exclamation_per_1k` | lower | secondary |
| `syn_ellipsis_per_1k` | twosided | secondary |
| `syn_dialogue_share` | twosided | secondary |
| `syn_tag_said_share` | twosided | secondary |
| `syn_tag_breath_share` | lower | secondary |
| `syn_correlative_per_1k` | lower | replication (`A5` fires on normal English at 0.61/1k) |
| `syn_passive_proxy_per_1k` | lower | secondary, **proxy** — auxiliary+participle, over-counts adjectival passives |
| `syn_commas_per_sentence` | twosided | secondary |
| `syn_para_words_mean` | twosided | secondary |
| `syn_para_cv` | higher | secondary (`U5`: 0 of 140 published novels fail it) |
| `syn_oneline_para_share` | twosided | replication (`U4` direction reverses between corpora) |

### structure (15)

| feature | direction | status |
|---|---|---|
| `str_coda_share` | lower | **primary** (`F1`) |
| `str_chapter_cv` | higher | secondary (`U1`) |
| `str_frame_max_share` | lower | secondary (`U6`) |
| `str_ngram_repeat_per_1k` | lower | secondary |
| `str_open_wake_share` | twosided | secondary |
| `str_open_weather_share` | twosided | secondary |
| `str_open_time_share` | twosided | secondary |
| `str_open_habitual_share` | twosided | secondary, proxy |
| `str_scene_mark_per_1k` | twosided | secondary |
| `str_arc_turns` | higher | secondary (`A1`; **unmeasured** under ~8,000 words) |
| `str_arc_range` | twosided | secondary (`A2`, never gated in the pipeline either) |
| `str_chapters` | none | descriptive |
| `str_words` | none | descriptive |
| `str_chapter_min` | none | descriptive |
| `str_chapter_max` | none | descriptive |

### names (10)

| feature | direction | status |
|---|---|---|
| arm-level first-name reuse | lower | **primary** (computed in `analysis/analyze.py`) |
| `nme_ssa_top20_share` | lower | secondary |
| `nme_popular_list_share` | lower | secondary |
| `nme_reference_unlisted_share` | twosided | secondary — *not* a verdict on invention: the reference covers 220 names |
| `nme_syllables_mean` | twosided | secondary |
| `nme_a_endings_share` | twosided | secondary |
| `nme_shared_surname_share` | twosided | secondary |
| `nme_distinct_first` | none | descriptive |
| `nme_distinct_surnames` | none | descriptive |
| `nme_names_per_1k` | none | descriptive |
| `nme_alliterative_pairs` | none | descriptive |

### cross-book (arm-level, `analysis/analyze.py`)

| row | status |
|---|---|
| opening-sentence similarity, median pairwise | **primary** |
| opening-sentence similarity, max pairwise | secondary |
| closing-sentence similarity, median/max | secondary |
| first names recurring in ≥ max(2, 20%) of an arm's books | **primary** (as a rate) |
| chapter-count spread within arm | secondary |
| share of books closing any chapter on a coda | secondary |
| dominant frame per arm | descriptive |

## 3. Declared as NOT measured

| §8 feature | why not |
|---|---|
| adjective density, adjective-before-noun clustering | requires a POS tagger; this repo has none, and a new instrument is a new calibration problem, not a free row |
| passive-voice share | no POS; only the proxy above, labelled as such |
| gendered name distribution | no gender reference in this repo; `NAME_FREQUENCY.tsv` gives frequency tiers only. Adding one is a decision, not an inference |
| "show vs tell" (emotion-naming vs bodily description) | both sides are unvalidated proxies; measuring them would produce two numbers and no interpretation. Exploratory at best |
| chapter-opening classification as a mutually exclusive typology | the four classes are multi-label regex flags. A mutually exclusive classifier would be an unmeasured instrument with an unknown error rate |

## 4. Classification rules (as implemented in `analysis/analyze.py`)

Per feature, with Arm C as the human baseline:

- `c_sd` = IQR/1.349 of Arm C (robust; equals the SD when n is large).
- `band` = Arm C's 10th to 90th percentile (default; `--band`).
- `no A-vs-C gap` when |medianA − medianC| ≤ 0.25·c_sd. These rows are **unclear**, never
  fixed: the pipeline cannot be credited with closing a gap that was not there.
- **fixed**: medianB lies inside `band`.
- **worsened**: |medianB − medianC| > |medianA − medianC| + 0.2·scale.
- **partial**: B closed at least half the gap.
- **unchanged**: |medianB − medianA| ≤ 0.2·scale.
- **unclear**: everything else, retained in the report and never counted as fixed.
- `scale` is `c_sd`, falling back to the gap when every human book scored identically
  (otherwise "unchanged" is unreachable on a zero-variance row).

`twosided` features are compared on absolute distance from the human median. A signed
test on a burstiness or TTR row would invert on half the rows.

## 5. Residual-tell rule (the §10 candidates)

All three conditions, not one:

1. medianB outside Arm C's `band`;
2. effect ≥ 0.5·c_sd (`--min-effect`);
3. permutation p < .05 on the 20-vs-C comparison (10,000 relabellings, seeded).

BH q is reported within family and is **not** a fourth condition — it is there so a family
of 20 syntax rows cannot present three coincidences as three findings.

A residual tell is a **candidate**, not a check. §10's remaining steps are unchanged: a
C-dist baseline, a threshold measured on it, a false-positive rate on it, and Kalie's
review. A row that clears all three conditions with Arm C at n=10 is still not shippable.

## 6. Fixed analysis parameters

| parameter | value | note |
|---|---|---|
| random seed | 20261030 | sampling, permutation |
| permutation iterations | 10000 | 500 in selftest |
| C band | 10th–90th percentile | 5/95 reported as a sensitivity in the C-dist run |
| minimum effect | 0.5·c_sd | |
| paired test | exact sign test on (B−A) direction toward the human median | |
| multiple comparisons | Benjamini–Hochberg within family | secondaries only |
| length check | Spearman ρ of feature vs analysis word count | flags `len-confounded` at \|ρ\| ≥ 0.5 |

## 7. Known limits that must appear in the report

1. Arm C at n=10 cannot set a threshold (REDTEAM.md B1). The report prints its own Arm C
   size and warns below 30; the shipped threshold comes from C-dist (109 novels), not from
   the human ten, which `DECISIONS.md` defers to after generation.
2. A null at n=20 pairs is not evidence of absence (design §9.8).
3. Names are a proper-noun inventory, not a cast list (extractor docstring).
4. Mechanical rows do not judge quality (design §10).
5. Any per-genre sentence is a sentence about two books (REDTEAM.md M6).
6. No human rating layer exists (decision 5, `DECISIONS.md`): §8.6 is dropped, no LLM judge
   substitutes for it, and nothing in this study rates readability, voice or human-likeness.
   Every claim is about counted features, never about quality.
