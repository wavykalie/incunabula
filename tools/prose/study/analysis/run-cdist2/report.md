# Study analysis

Books: A=20  B=15  C=167   band=central 80% of Arm C   min effect=0.5 sdC

> Length filter: books above 120,000 analysis words are excluded. The long-form stratum is exploratory and is never pooled with the primary pairs (`DECISIONS.md` §2).

> Excluded by id: `V,W`. Voice-sensitivity books are compared to their own twins separately (`DECISIONS.md` §3); every other excluded id is excluded for the reason recorded in that book's run report. None are pooled into the primary distributions or pairing.

## Classification by family

| family | fixed | partial | unchanged | worsened | unclear | unmeasured | descriptive |
|---|---|---|---|---|---|---|---|
| lexical | 3 | 0 | 1 | 2 | 5 | 0 | 0 |
| syntax | 16 | 0 | 0 | 2 | 2 | 0 | 0 |
| structure | 6 | 1 | 0 | 0 | 4 | 0 | 4 |
| names | 4 | 0 | 0 | 0 | 2 | 0 | 4 |

`descriptive` rows are book-level outcomes (length, chapter count, cast size) with no human direction; they are reported and never scored.

## lexical

| feature | A med | B med | C med | C band | class | closed | pairs | p | q | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `lex_ai_term_hits` | 2.00 | 7.00 | 3.00 | 0.00..10.00 | fixed | -3.00 | 5/15 | 0.010 | 0.013 |  |
| `lex_ai_terms_per_1k` | 0.04 | 0.13 | 0.05 | 0.00..0.14 | fixed | -5.11 | 5/15 | 0.001 | 0.002 |  |
| `lex_ly_adverbs_per_1k` | 3.52 | 5.26 | 11.89 | 7.60..16.37 | unclear | 0.21 | 14/15 | 0.000 | 0.000 | **residual** |
| `lex_hedges_per_1k` | 0.07 | 0.09 | 1.31 | 0.71..2.23 | unchanged | 0.01 | 9/15 | 0.000 | 0.000 | **residual** |
| `lex_opener_and_share` | 0.02 | 0.01 | 0.02 | 0.01..0.05 | unclear | - | 4/15 | 0.089 | 0.089 | no A-vs-C gap |
| `lex_opener_but_share` | 0.00 | 0.01 | 0.03 | 0.01..0.06 | unclear | 0.19 | 13/15 | 0.003 | 0.005 | **residual** |
| `lex_opener_as_share` | 0.00 | 0.00 | 0.01 | 0.00..0.02 | unclear | 0.18 | 12/15 | 0.004 | 0.006 | **residual** |
| `lex_opener_when_share` | 0.01 | 0.01 | 0.01 | 0.00..0.02 | unclear | - | 4/15 | 0.045 | 0.049 | no A-vs-C gap |
| `lex_opener_suddenly_share` | 0.00 | 0.00 | 0.00 | 0.00..0.00 | fixed | 0.00 | 3/5 | 0.023 | 0.028 |  |
| `lex_opener_top1_share` | 0.16 | 0.18 | 0.11 | 0.08..0.17 | worsened | -0.40 | 4/15 | 0.000 | 0.000 | **residual** |
| `lex_ttr_rarefied` | 0.48 | 0.51 | 0.43 | 0.39..0.46 | worsened | -0.60 | 0/15 | 0.000 | 0.000 | replication **residual** |

## syntax

| feature | A med | B med | C med | C band | class | closed | pairs | p | q | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `syn_sent_words_mean` | 17.56 | 16.83 | 19.64 | 14.39..29.57 | fixed | -0.35 | 4/15 | 0.103 | 0.147 |  |
| `syn_sent_words_median` | 14.00 | 15.00 | 16.00 | 12.00..26.00 | fixed | 0.50 | 11/12 | 0.689 | 0.765 |  |
| `syn_sent_words_sd` | 13.89 | 10.01 | 14.65 | 10.27..23.87 | unclear | - | 2/15 | 0.011 | 0.036 | replication **residual** no A-vs-C gap |
| `syn_short_sent_share` | 0.19 | 0.11 | 0.12 | 0.05..0.20 | fixed | 0.87 | 13/15 | 0.558 | 0.656 |  |
| `syn_long_sent_share` | 0.11 | 0.04 | 0.12 | 0.05..0.32 | unclear | - | 0/15 | 0.058 | 0.117 | no A-vs-C gap |
| `syn_em_dash_per_1k` | 3.92 | 1.25 | 0.00 | 0.00..2.30 | fixed | 0.68 | 15/15 | 0.000 | 0.001 | replication |
| `syn_semicolon_per_1k` | 2.37 | 1.22 | 5.38 | 0.86..13.32 | fixed | -0.38 | 0/15 | 0.007 | 0.030 |  |
| `syn_colon_per_1k` | 4.01 | 3.24 | 1.06 | 0.27..3.90 | fixed | 0.26 | 12/15 | 0.000 | 0.001 |  |
| `syn_exclamation_per_1k` | 0.87 | 1.72 | 4.37 | 1.14..10.89 | fixed | 0.24 | 12/15 | 0.019 | 0.054 |  |
| `syn_ellipsis_per_1k` | 0.97 | 0.21 | 0.00 | 0.00..1.86 | fixed | 0.79 | 14/15 | 0.030 | 0.067 |  |
| `syn_dialogue_share` | 0.25 | 0.40 | 0.39 | 0.11..0.54 | fixed | 0.93 | 8/15 | 0.876 | 0.876 |  |
| `syn_tag_said_share` | 0.81 | 0.68 | 0.71 | 0.50..0.88 | fixed | 0.69 | 10/15 | 0.432 | 0.540 |  |
| `syn_tag_breath_share` | 0.08 | 0.17 | 0.04 | 0.00..0.11 | worsened | -1.87 | 3/15 | 0.000 | 0.001 | **residual** |
| `syn_correlative_per_1k` | 0.02 | 0.07 | 0.07 | 0.01..0.16 | fixed | 0.93 | 11/15 | 0.875 | 0.876 | replication |
| `syn_passive_proxy_per_1k` | 4.11 | 3.41 | 4.71 | 2.89..7.50 | fixed | -1.17 | 5/15 | 0.025 | 0.063 |  |
| `syn_commas_per_sentence` | 1.08 | 1.09 | 1.45 | 0.91..2.66 | fixed | 0.02 | 4/15 | 0.078 | 0.136 |  |
| `syn_para_words_mean` | 22.97 | 32.06 | 44.58 | 27.80..99.09 | fixed | 0.42 | 15/15 | 0.082 | 0.136 |  |
| `syn_para_cv` | 89.72 | 68.57 | 100.75 | 72.62..131.61 | worsened | -1.92 | 1/15 | 0.000 | 0.001 | **residual** |
| `syn_oneline_para_share` | 0.74 | 0.41 | 0.35 | 0.18..0.50 | fixed | 0.84 | 15/15 | 0.099 | 0.147 | replication |
| `syn_chapter_sentlen_spread` | 13.68 | 8.98 | 11.86 | 5.11..24.06 | fixed | -0.58 | 6/15 | 0.172 | 0.229 |  |

## structure

| feature | A med | B med | C med | C band | class | closed | pairs | p | q | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `str_chapters` | 47.00 | 40.00 | 23.00 | 12.00..36.40 | descriptive | 0.29 | 11/14 | 0.000 | 0.001 |  |
| `str_words` | 55313.50 | 55292.00 | 58709.00 | 31316.40..97553.20 | descriptive | - | 7/15 | 0.539 | 0.734 | no A-vs-C gap len-confounded |
| `str_chapter_cv` | 38.48 | 29.51 | 20.63 | 4.78..48.62 | fixed | 0.50 | 15/15 | 0.109 | 0.205 |  |
| `str_chapter_min` | 485.00 | 848.00 | 1179.00 | 466.00..2500.00 | descriptive | 0.52 | 15/15 | 0.179 | 0.293 |  |
| `str_chapter_max` | 2551.00 | 2374.00 | 3112.00 | 2573.40..7924.80 | descriptive | -0.32 | 7/15 | 0.195 | 0.293 |  |
| `str_open_wake_share` | 0.00 | 0.00 | 0.00 | 0.00..0.04 | unclear | - | 1/3 | 1.000 | 1.000 | no A-vs-C gap |
| `str_open_weather_share` | 0.11 | 0.10 | 0.00 | 0.00..0.09 | unclear | 0.11 | 12/15 | 0.000 | 0.001 | **residual** |
| `str_open_time_share` | 0.19 | 0.15 | 0.08 | 0.00..0.27 | fixed | 0.33 | 9/15 | 0.069 | 0.148 |  |
| `str_open_habitual_share` | 0.02 | 0.00 | 0.05 | 0.00..0.17 | fixed | -0.71 | 3/12 | 0.051 | 0.128 |  |
| `str_coda_share` | 0.00 | 0.00 | 0.00 | 0.00..0.00 | unclear | - | 0/0 | 1.000 | 1.000 | no A-vs-C gap |
| `str_frame_max_share` | 0.12 | 0.07 | 0.07 | 0.00..0.17 | fixed | 0.85 | 9/14 | 0.786 | 0.982 |  |
| `str_ngram_repeat_per_1k` | 6.65 | 2.34 | 0.87 | 0.34..2.88 | fixed | 0.75 | 13/15 | 0.001 | 0.005 |  |
| `str_scene_mark_per_1k` | 0.76 | 0.04 | 0.16 | 0.05..0.45 | partial | 0.79 | 14/15 | 0.009 | 0.033 | **residual** |
| `str_arc_turns` | 0.58 | 0.58 | 0.57 | 0.54..0.61 | unclear | - | 11/15 | 0.873 | 1.000 | no A-vs-C gap |
| `str_arc_range` | 0.03 | 0.04 | 0.05 | 0.04..0.06 | fixed | 0.62 | 10/15 | 0.026 | 0.078 |  |

## names

| feature | A med | B med | C med | C band | class | closed | pairs | p | q | note |
|---|---|---|---|---|---|---|---|---|---|---|
| `nme_distinct_first` | 88.50 | 53.00 | 57.00 | 27.20..116.40 | descriptive | 0.87 | 13/15 | 0.858 | 0.994 |  |
| `nme_distinct_surnames` | 18.00 | 10.00 | 8.00 | 2.00..19.00 | descriptive | 0.80 | 12/14 | 0.438 | 0.876 |  |
| `nme_names_per_1k` | 1.86 | 1.05 | 1.18 | 0.62..2.03 | descriptive | 0.82 | 13/15 | 0.598 | 0.905 |  |
| `nme_ssa_top20_share` | 0.01 | 0.01 | 0.00 | 0.00..0.03 | fixed | -0.36 | 6/10 | 0.158 | 0.525 |  |
| `nme_popular_list_share` | 0.04 | 0.07 | 0.03 | 0.00..0.07 | fixed | -1.48 | 6/13 | 0.001 | 0.004 |  |
| `nme_reference_unlisted_share` | 0.95 | 0.93 | 0.96 | 0.91..1.00 | fixed | -1.11 | 8/14 | 0.001 | 0.004 |  |
| `nme_syllables_mean` | 2.08 | 2.08 | 2.10 | 1.87..2.32 | unclear | - | 8/15 | 0.894 | 0.994 | no A-vs-C gap |
| `nme_alliterative_pairs` | 0.50 | 0.00 | 0.00 | 0.00..2.00 | descriptive | 1.00 | 6/7 | 1.000 | 1.000 |  |
| `nme_a_endings_share` | 0.06 | 0.08 | 0.07 | 0.02..0.15 | unclear | - | 4/15 | 0.634 | 0.905 | no A-vs-C gap |
| `nme_shared_surname_share` | 0.17 | 0.12 | 0.05 | 0.00..0.28 | fixed | 0.37 | 7/13 | 0.415 | 0.876 |  |

## Residual tells (candidate scanner checks)

| feature | B med | C band | effect (sd) | perm p | BH q |
|---|---|---|---|---|---|
| `lex_ly_adverbs_per_1k` | 5.26 | 7.60..16.37 | 1.88 | 0.0001 | 0.0003 |
| `lex_hedges_per_1k` | 0.09 | 0.71..2.23 | 2.24 | 0.0001 | 0.0003 |
| `lex_opener_but_share` | 0.01 | 0.01..0.06 | 1.14 | 0.0028 | 0.0051 |
| `lex_opener_as_share` | 0.00 | 0.00..0.02 | 1.22 | 0.0039 | 0.0061 |
| `lex_opener_top1_share` | 0.18 | 0.08..0.17 | 2.12 | 0.0001 | 0.0003 |
| `lex_ttr_rarefied` | 0.51 | 0.39..0.46 | 2.68 | 0.0001 | 0.0003 |
| `syn_sent_words_sd` | 10.01 | 10.27..23.87 | 0.96 | 0.0107 | 0.0357 |
| `syn_tag_breath_share` | 0.17 | 0.00..0.11 | 3.14 | 0.0001 | 0.0007 |
| `syn_para_cv` | 68.57 | 72.62..131.61 | 1.27 | 0.0001 | 0.0007 |
| `str_open_weather_share` | 0.10 | 0.00..0.09 | 3.07 | 0.0002 | 0.0015 |
| `str_scene_mark_per_1k` | 0.04 | 0.05..0.45 | 0.88 | 0.0089 | 0.0334 |

Each row still needs §10's remaining steps before it is a check: a human baseline from C-dist, a threshold measured on that corpus, a false-positive rate on it, and Kalie's review.

## Cross-book rows (arm-level)

| row | A | B | C |
|---|---|---|---|
| opening_similarity_median | 0.07 | 0.07 | 0.04 |
| opening_similarity_max | 0.16 | 0.19 | 0.71 |
| closing_similarity_median | 0.07 | 0.07 | 0.03 |
| closing_similarity_max | 0.23 | 0.25 | 1.00 |
| names_at_or_above_threshold | 51 names | 35 names | 17 names |
| chapter_count_sd | 9.35 | 0.00 | 10.58 |
| books_closing_on_coda | 0.00 | 0.00 | 4.00 |

- Arm A: recurring first names (>= threshold): English (14 books), Arthur (11 books), London (11 books), Julian (10 books), German (9 books), Dutch (9 books)
- Arm B: recurring first names (>= threshold): Arthur (8 books), London (8 books), Marcus (7 books), Saint (7 books), French (6 books), English (6 books)
- Arm C: recurring first names (>= threshold): English (83 books), French (83 books), England (74 books), American (59 books), London (55 books), John (52 books)

## Limits of this run

- Mechanical features only. They find tells; they do not judge whether a book is good (design §10).
- A null result at these n is not evidence the tell is absent, only that it was not large enough to show (design §9.8).
- Names are extracted from prose as a proper-noun inventory, so recurring place names inflate the counts. Both arms are measured identically, which is what makes the comparison fair; the inventory is not a cast list.
- Every row this repo has already measured as a null or with the opposite sign is marked `replication` and is not a primary endpoint (study/REDTEAM.md B2).
- `len-confounded` marks |Spearman rho| >= 0.5 against book length; the length-matched sensitivity run in design §7 has not been applied here.
- `no A-vs-C gap` marks a feature on which Arm A already sat at the human median. Those rows are counted as unclear, not fixed: the pipeline cannot be credited with closing a gap that was not there.
- `C has no spread` marks a feature every human book scored identically on. No effect size can be computed against a zero-variance baseline, so those rows are reported and never called residual tells.

## Held-out cohorts

- `B-deepseek`: `B-17` - 23 feature(s) outside the Arm C band, table in `cohort-B-deepseek.md`. Declared in the manifest, not excluded by hand (DECISIONS.md).

