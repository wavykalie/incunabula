# Study analysis

Books: A=20  B=15  C=87   band=central 80% of Arm C   min effect=0.5 sdC

> Length filter: books above 120,000 analysis words are excluded. The long-form stratum is exploratory and is never pooled with the primary pairs (`DECISIONS.md` §2).

> Excluded by id: `V,W`. Voice-sensitivity books are compared to their own twins separately (`DECISIONS.md` §3); every other excluded id is excluded for the reason recorded in that book's run report. None are pooled into the primary distributions or pairing.

## Classification by family

| family | fixed | partial | unchanged | worsened | unclear | unmeasured | descriptive |
|---|---|---|---|---|---|---|---|
| lexical | 3 | 0 | 1 | 3 | 4 | 0 | 0 |
| syntax | 15 | 0 | 0 | 4 | 1 | 0 | 0 |
| structure | 8 | 0 | 0 | 1 | 2 | 0 | 4 |
| names | 3 | 0 | 0 | 0 | 3 | 0 | 4 |

`descriptive` rows are book-level outcomes (length, chapter count, cast size) with no human direction; they are reported and never scored.

## lexical

| feature | A med | B med | C med | C band | class | closed | pairs | p | q | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `lex_ai_term_hits` | 2.00 | 7.00 | 3.00 | 0.00..9.00 | fixed | -3.00 | 5/15 | 0.020 | 0.025 |  |
| `lex_ai_terms_per_1k` | 0.04 | 0.13 | 0.05 | 0.00..0.12 | worsened | -4.38 | 5/15 | 0.000 | 0.000 | **residual** |
| `lex_ly_adverbs_per_1k` | 3.52 | 5.26 | 11.24 | 7.77..16.97 | unclear | 0.22 | 14/15 | 0.000 | 0.000 | **residual** |
| `lex_hedges_per_1k` | 0.07 | 0.09 | 1.39 | 0.82..2.43 | unchanged | 0.01 | 9/15 | 0.000 | 0.000 | **residual** |
| `lex_opener_and_share` | 0.02 | 0.01 | 0.02 | 0.01..0.05 | unclear | - | 5/15 | 0.142 | 0.142 | no A-vs-C gap |
| `lex_opener_but_share` | 0.00 | 0.01 | 0.03 | 0.01..0.06 | unclear | 0.18 | 13/15 | 0.000 | 0.001 | **residual** |
| `lex_opener_as_share` | 0.00 | 0.00 | 0.01 | 0.00..0.02 | unclear | 0.17 | 12/15 | 0.000 | 0.001 | **residual** |
| `lex_opener_when_share` | 0.01 | 0.01 | 0.01 | 0.00..0.02 | fixed | -1.05 | 7/15 | 0.015 | 0.021 |  |
| `lex_opener_suddenly_share` | 0.00 | 0.00 | 0.00 | 0.00..0.00 | fixed | 0.00 | 3/5 | 0.093 | 0.102 |  |
| `lex_opener_top1_share` | 0.16 | 0.18 | 0.10 | 0.08..0.17 | worsened | -0.38 | 4/15 | 0.000 | 0.000 | **residual** |
| `lex_ttr_rarefied` | 0.48 | 0.51 | 0.43 | 0.38..0.46 | worsened | -0.56 | 0/15 | 0.000 | 0.000 | replication **residual** |

## syntax

| feature | A med | B med | C med | C band | class | closed | pairs | p | q | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `syn_sent_words_mean` | 17.56 | 16.83 | 20.14 | 15.92..31.68 | fixed | -0.28 | 4/15 | 0.035 | 0.058 |  |
| `syn_sent_words_median` | 14.00 | 15.00 | 17.00 | 13.00..26.00 | fixed | 0.33 | 11/12 | 0.347 | 0.408 |  |
| `syn_sent_words_sd` | 13.89 | 10.01 | 15.28 | 11.42..25.48 | worsened | -2.79 | 1/15 | 0.004 | 0.018 | replication **residual** |
| `syn_short_sent_share` | 0.19 | 0.11 | 0.12 | 0.07..0.19 | fixed | 0.91 | 13/15 | 0.719 | 0.757 |  |
| `syn_long_sent_share` | 0.11 | 0.04 | 0.14 | 0.06..0.33 | worsened | -2.54 | 0/15 | 0.004 | 0.018 | **residual** |
| `syn_em_dash_per_1k` | 3.92 | 1.25 | 0.00 | 0.00..8.45 | fixed | 0.68 | 15/15 | 0.069 | 0.103 | replication |
| `syn_semicolon_per_1k` | 2.37 | 1.22 | 7.31 | 0.95..15.75 | fixed | -0.23 | 0/15 | 0.002 | 0.014 |  |
| `syn_colon_per_1k` | 4.01 | 3.24 | 1.52 | 0.23..5.95 | fixed | 0.31 | 11/15 | 0.031 | 0.057 |  |
| `syn_exclamation_per_1k` | 0.87 | 1.72 | 4.16 | 1.22..11.52 | fixed | 0.26 | 13/15 | 0.010 | 0.024 |  |
| `syn_ellipsis_per_1k` | 0.97 | 0.21 | 0.00 | 0.00..1.04 | fixed | 0.79 | 14/15 | 0.006 | 0.020 |  |
| `syn_dialogue_share` | 0.25 | 0.40 | 0.36 | 0.15..0.53 | fixed | 0.62 | 4/15 | 0.428 | 0.475 |  |
| `syn_tag_said_share` | 0.83 | 0.69 | 0.76 | 0.64..0.88 | fixed | -0.16 | 7/15 | 0.074 | 0.103 |  |
| `syn_tag_breath_share` | 0.08 | 0.16 | 0.03 | 0.00..0.09 | worsened | -1.69 | 1/15 | 0.000 | 0.001 | **residual** |
| `syn_correlative_per_1k` | 0.02 | 0.07 | 0.08 | 0.02..0.19 | fixed | 0.85 | 11/15 | 0.849 | 0.849 | replication |
| `syn_passive_proxy_per_1k` | 4.11 | 3.41 | 4.88 | 3.28..7.52 | fixed | -0.92 | 6/15 | 0.007 | 0.021 |  |
| `syn_commas_per_sentence` | 1.08 | 1.09 | 1.55 | 0.97..2.67 | fixed | 0.01 | 4/15 | 0.031 | 0.057 |  |
| `syn_para_words_mean` | 22.97 | 32.06 | 47.96 | 28.59..88.57 | fixed | 0.36 | 15/15 | 0.017 | 0.038 |  |
| `syn_para_cv` | 89.72 | 68.57 | 106.54 | 75.61..142.56 | worsened | -1.26 | 1/15 | 0.000 | 0.001 | **residual** |
| `syn_oneline_para_share` | 0.74 | 0.41 | 0.35 | 0.21..0.55 | fixed | 0.86 | 15/15 | 0.183 | 0.229 | replication |
| `syn_chapter_sentlen_spread` | 13.68 | 8.98 | 12.51 | 6.02..23.25 | unclear | - | 7/15 | 0.078 | 0.103 | no A-vs-C gap |

## structure

| feature | A med | B med | C med | C band | class | closed | pairs | p | q | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `str_chapters` | 47.00 | 40.00 | 24.00 | 11.60..38.40 | descriptive | 0.30 | 11/14 | 0.002 | 0.010 |  |
| `str_words` | 55313.50 | 55292.00 | 57906.00 | 29978.60..100509.00 | descriptive | - | 8/15 | 0.324 | 0.442 | no A-vs-C gap len-confounded |
| `str_chapter_cv` | 38.48 | 29.51 | 23.76 | 7.52..45.47 | fixed | 0.61 | 15/15 | 0.188 | 0.282 |  |
| `str_chapter_min` | 485.00 | 848.00 | 1365.00 | 457.40..2501.40 | descriptive | 0.41 | 15/15 | 0.054 | 0.101 |  |
| `str_chapter_max` | 2551.00 | 2374.00 | 3290.00 | 2623.40..7311.60 | descriptive | -0.24 | 6/15 | 0.087 | 0.145 |  |
| `str_open_wake_share` | 0.00 | 0.00 | 0.00 | 0.00..0.05 | unclear | - | 1/3 | 1.000 | 1.000 | no A-vs-C gap |
| `str_open_weather_share` | 0.15 | 0.17 | 0.00 | 0.00..0.08 | worsened | -0.15 | 8/15 | 0.000 | 0.001 | **residual** |
| `str_open_time_share` | 0.19 | 0.15 | 0.06 | 0.00..0.23 | fixed | 0.27 | 10/15 | 0.005 | 0.020 |  |
| `str_open_habitual_share` | 0.02 | 0.00 | 0.07 | 0.00..0.17 | fixed | -0.45 | 3/12 | 0.011 | 0.032 |  |
| `str_coda_share` | 0.00 | 0.00 | 0.00 | 0.00..0.00 | unclear | - | 0/0 | 1.000 | 1.000 | no A-vs-C gap |
| `str_frame_max_share` | 0.12 | 0.07 | 0.08 | 0.00..0.20 | fixed | 0.86 | 6/14 | 0.827 | 0.954 |  |
| `str_ngram_repeat_per_1k` | 6.65 | 2.34 | 0.95 | 0.34..2.60 | fixed | 0.76 | 13/15 | 0.000 | 0.003 |  |
| `str_scene_mark_per_1k` | 0.76 | 0.04 | 0.14 | 0.02..0.33 | fixed | 0.84 | 14/15 | 0.013 | 0.032 |  |
| `str_arc_turns` | 0.58 | 0.58 | 0.57 | 0.54..0.61 | fixed | 0.03 | 10/15 | 0.468 | 0.585 |  |
| `str_arc_range` | 0.03 | 0.04 | 0.05 | 0.04..0.06 | fixed | 0.63 | 10/15 | 0.043 | 0.093 |  |

## names

| feature | A med | B med | C med | C band | class | closed | pairs | p | q | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `nme_distinct_first` | 88.50 | 53.00 | 53.00 | 26.60..102.20 | descriptive | 1.00 | 13/15 | 1.000 | 1.000 |  |
| `nme_distinct_surnames` | 18.00 | 10.00 | 8.00 | 2.00..21.00 | descriptive | 0.80 | 12/14 | 0.654 | 1.000 |  |
| `nme_names_per_1k` | 1.86 | 1.05 | 1.03 | 0.60..2.03 | descriptive | 0.98 | 14/15 | 1.000 | 1.000 |  |
| `nme_ssa_top20_share` | 0.01 | 0.01 | 0.01 | 0.00..0.04 | unclear | - | 8/10 | 0.693 | 1.000 | no A-vs-C gap |
| `nme_popular_list_share` | 0.04 | 0.07 | 0.03 | 0.00..0.07 | fixed | -2.28 | 7/13 | 0.003 | 0.033 |  |
| `nme_reference_unlisted_share` | 0.95 | 0.93 | 0.96 | 0.89..1.00 | fixed | -1.77 | 7/14 | 0.014 | 0.071 |  |
| `nme_syllables_mean` | 2.08 | 2.08 | 2.10 | 1.81..2.33 | unclear | - | 9/15 | 0.852 | 1.000 | no A-vs-C gap |
| `nme_alliterative_pairs` | 0.50 | 0.00 | 0.00 | 0.00..2.00 | descriptive | 1.00 | 6/7 | 1.000 | 1.000 |  |
| `nme_a_endings_share` | 0.06 | 0.08 | 0.06 | 0.01..0.12 | unclear | - | 6/15 | 0.126 | 0.419 | no A-vs-C gap |
| `nme_shared_surname_share` | 0.17 | 0.12 | 0.05 | 0.00..0.25 | fixed | 0.37 | 7/13 | 0.367 | 0.918 |  |

## Residual tells (candidate scanner checks)

| feature | B med | C band | effect (sd) | perm p | BH q |
|---|---|---|---|---|---|
| `lex_ai_terms_per_1k` | 0.13 | 0.00..0.12 | 1.62 | 0.0002 | 0.0004 |
| `lex_ly_adverbs_per_1k` | 5.26 | 7.77..16.97 | 1.81 | 0.0001 | 0.0003 |
| `lex_hedges_per_1k` | 0.09 | 0.82..2.43 | 2.00 | 0.0001 | 0.0003 |
| `lex_opener_but_share` | 0.01 | 0.01..0.06 | 1.42 | 0.0003 | 0.0005 |
| `lex_opener_as_share` | 0.00 | 0.00..0.02 | 1.42 | 0.0004 | 0.0006 |
| `lex_opener_top1_share` | 0.18 | 0.08..0.17 | 2.49 | 0.0001 | 0.0003 |
| `lex_ttr_rarefied` | 0.51 | 0.38..0.46 | 2.86 | 0.0001 | 0.0003 |
| `syn_sent_words_sd` | 10.01 | 11.42..25.48 | 1.04 | 0.0038 | 0.0176 |
| `syn_long_sent_share` | 0.04 | 0.06..0.33 | 1.07 | 0.0044 | 0.0176 |
| `syn_tag_breath_share` | 0.16 | 0.00..0.09 | 3.72 | 0.0001 | 0.0010 |
| `syn_para_cv` | 68.57 | 75.61..142.56 | 1.92 | 0.0001 | 0.0010 |
| `str_open_weather_share` | 0.17 | 0.00..0.08 | 4.84 | 0.0001 | 0.0015 |

Each row still needs §10's remaining steps before it is a check: a human baseline from C-dist, a threshold measured on that corpus, a false-positive rate on it, and Kalie's review.

## Cross-book rows (arm-level)

| row | A | B | C |
|---|---|---|---|
| opening_similarity_median | 0.07 | 0.07 | 0.04 |
| opening_similarity_max | 0.16 | 0.19 | 0.57 |
| closing_similarity_median | 0.07 | 0.07 | 0.03 |
| closing_similarity_max | 0.23 | 0.25 | 1.00 |
| names_at_or_above_threshold | 51 names | 35 names | 19 names |
| chapter_count_sd | 9.35 | 0.00 | 11.08 |
| books_closing_on_coda | 0.00 | 0.00 | 1.00 |

- Arm A: recurring first names (>= threshold): English (14 books), Arthur (11 books), London (11 books), Julian (10 books), German (9 books), Dutch (9 books)
- Arm B: recurring first names (>= threshold): Arthur (8 books), London (8 books), Marcus (7 books), Saint (7 books), French (6 books), English (6 books)
- Arm C: recurring first names (>= threshold): English (48 books), England (45 books), John (40 books), French (40 books), London (35 books), Mary (27 books)

## Limits of this run

- Mechanical features only. They find tells; they do not judge whether a book is good (design §10).
- A null result at these n is not evidence the tell is absent, only that it was not large enough to show (design §9.8).
- Names are extracted from prose as a proper-noun inventory, so recurring place names inflate the counts. Both arms are measured identically, which is what makes the comparison fair; the inventory is not a cast list.
- Every row this repo has already measured as a null or with the opposite sign is marked `replication` and is not a primary endpoint (study/REDTEAM.md B2).
- `len-confounded` marks |Spearman rho| >= 0.5 against book length; the length-matched sensitivity run in design §7 has not been applied here.
- `no A-vs-C gap` marks a feature on which Arm A already sat at the human median. Those rows are counted as unclear, not fixed: the pipeline cannot be credited with closing a gap that was not there.
- `C has no spread` marks a feature every human book scored identically on. No effect size can be computed against a zero-variance baseline, so those rows are reported and never called residual tells.

## Held-out cohorts

- `B-deepseek`: `B-17` - 24 feature(s) outside the Arm C band, table in `cohort-B-deepseek.md`. Declared in the manifest, not excluded by hand (DECISIONS.md).

