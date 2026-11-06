# B-17 run report — cohort `B-deepseek`

Written 2026-11-06, after filing. This is the study's record of how B-17 was produced,
what it is comparable to, and what it is not.

## 1. Why this book exists on this route

B-17 (`sf-01`, "the fragment") was dispatched as a clean B-sub row on
`gemini-3.8-flash-high`. It could not be drafted on that route. The measurement is in
`ARM_B_SUB_AMENDMENT.md`: `agy` accepted one-line probes and one 400-word file write
(112 s, 11,656 output tokens) and then returned `429` on three identical calls with
`Resets in 73h58m`. A book at 60,000 words is roughly 150 substantive model calls. The
route was abandoned on measurement, not preference.

The operator (this agent) therefore drafted the book itself, under the
`B-deepseek` cohort declared in `DECISIONS.md` on 2026-11-06. Every chapter is a declared
`prose` row in `books-armb/B-17/logs/operator.md`; the drafting model is the executing
agent, and no API `modelVersion` exists for it — H3 is a session-identity claim, not a
version string.

## 2. What was produced

| | |
|---|---|
| book | B-17, `sf-01`, "the fragment", science fiction |
| words | 64,593 (chapter files), within the declared 54,000–66,000 band |
| chapters | 40 |
| pipeline | `8265c48d12962ca233ed98bd10083edb072ec7f0`, unmodified |
| premise payload | sent verbatim; `premise.md` sha256 matches the frozen payload |
| payload | `run/out/armb-wt/books-armb/B-17/premise.md` |
| filed text | `books/B-17/manuscript/pipeline-text.md` |

The premise was not altered, the length band was never used as a reason to regenerate,
and no prose was hand-repaired after filing. Two mechanical rewrites were made *before*
filing in response to deslop rows, and both are logged: `facts as reported` matched the
A4 serves-as regex (false positive, reworded), and `ledger` matched the A22
cross-contamination guard (reworded to `volume`).

## 3. Gates — what actually ran

Run through `tools/run-phases.sh books-armb/B-17 --from 3`, which parses exit codes and
refuses to advance on anything but 0. Final state: chain CLEAR through phase 6,
`PROJECT_STATE.yaml` at COMPLETE.

| gate | result |
|---|---|
| deslop (40 chapters) | CLEAR |
| uniformity U1 | CV 29.9% (published fiction 33.4–45.1%; fail under 22, warn under 28) |
| uniformity U2/U3/U5/U6 | spread 8.46; codas 0/40; paragraph CV 84%; signature frame 30% |
| drift D1 | 0.52 (fail above 1.40) |
| arc A1 | 0.54 over 16 windows (fail under 0.45) |
| narrative N1/N4 | OK — ledger conforms, 10 debts closed or deferred with reasons |
| length L1 | 10,593 above the floor, 1,407 below the ceiling |
| pass-evidence | 64,593 / 64,593 gated |
| check-eval | citations, floor = minimum of seven dimensions, no delta violations |

## 4. Declared confounds — read these before using the row

1. **Operator and drafter are the same context.** The study's whole design rests on an
   operator who did not write the book. Here the operator wrote every sentence. Any
   comparison against the 15 Flash-high pairs measures the route, the harness, and the
   author, and cannot separate them.
2. **The self-evaluation is a self-sort.** `register`'s blind sort was performed by the
   drafter, who cannot be blind. `check-eval` prints the −0.8 self-evaluation calibration
   for exactly this reason; the raw floors in `evaluations/` are inflated by construction.
3. **The harness record is a session claim.** `run/harness-deepseek.json` records what
   the context exposes: no settable temperature, top-p, or system prompt. Every sampling
   field is `settable: false`. It is not comparable to a CLI probe record.
4. **Pairing with A-16…A-20 is confounded** by (1) and (2). B-17 is filed as its own
   cohort row and must not be pooled into the Flash-high B-sub means.
5. **Length was reached by expansion, not by drafting to length.** First-pass draft was
   30,780 words. Nineteen scenes were spliced in before each chapter's closing paragraph,
   and one long climactic sequence was added to chapter 33. The chapter-length CV of
   29.9% is a product of that process.
6. **`preflight.py` does not cover this cohort.** It validates the Flash-high harness
   record. Its READY verdict on the study was obtained before the cohort amendment and
   does not extend to this row.

## 5. How the row is kept out of the pooled analysis

The pooled comparison is produced by `analysis/analyze.py` at the study root. B-17 is a
`B-` id, so the tool would count it as a sixteenth pipeline book and average a
self-drafted text into the fifteen Flash-high pairs. The row says so itself: its
`deviations` field begins `cohort B-deepseek: operator=drafter`, and `analyze.py` reads
that declaration, holds the book out of the primary distributions and the pairing, and
measures it separately against the same Arm C band.

```bash
python extract/features.py --all books --out features
python analysis/analyze.py --features features --manifest books/manifest.csv \
    --out analysis/run --max-words 120000 --exclude-books "V,W"
```

That run reports `books A=20 B=15 C=87`, prints `held out by declaration: B-deepseek
(n=1)`, and writes `analysis/run/cohort-B-deepseek.md`, which puts the book's medians
against the same band the fifteen pairs are scored on. The exclusion is a property of the
filing row and not of the command line: an operator who never reads this report still gets
the fifteen pairs, because the book has already declared itself out of the pool.

The first version of this section documented `--exclude-books "V,W,B-17"` instead. A flag
that has to be retyped is one typo away from pooling a self-drafted book into the arm, and
the declaration is not.

**The voice arm did not run, and this is a gap in the corpus, not in the tool.**
`analysis/voices.py` compares `B-NNV` and `B-NNW` twins against their `B-NN` parents. No
book in this study was drafted with a voice suffix, so there are no twins to compare and
the script exits 2 with a message that names Arm C as the cause. That message is wrong —
Arm C has 109 books in `features/` — and the real cause is the missing voice books. I did
not edit the script's wording mid-study, because a message is not a measurement and the
honest record is the one that says the arm has no corpus.

One caption *was* corrected before the analysis was committed. `analyze.py` printed
"these are the voice-sensitivity books" over any `--exclude-books` list, which would have
described B-17 as a voice twin in the committed report. The note now names the voice books
as one class and leaves every other excluded id to its own run report. No metric,
threshold, corpus or comparison changed; the caption is the only edit.

## 6. What this run does not show

It says nothing about whether the pipeline produces good books, and it says nothing about
voice sensitivity, because the voice twins that arm needs were never drafted. Every gate here is
mechanical; `run-phases` states plainly that a CLEAR covers the gates and never the human
column. It says nothing about the Flash-high comparison — that comparison has no B-17 in
it. And it says nothing about reproducibility: a second `B-deepseek` run would be a
different session, a different draft, and a different book.

The one thing it does show is that the pipeline is executable end to end by an agent
context with no drafting model behind it, and that every gate it depends on can be
satisfied by prose written in that context — which is a statement about the gates'
reach, not about the prose.
