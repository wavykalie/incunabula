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

## 5. What this run does not show

It says nothing about whether the pipeline produces good books. Every gate here is
mechanical; `run-phases` states plainly that a CLEAR covers the gates and never the human
column. It says nothing about the Flash-high comparison — that comparison has no B-17 in
it. And it says nothing about reproducibility: a second `B-deepseek` run would be a
different session, a different draft, and a different book.

The one thing it does show is that the pipeline is executable end to end by an agent
context with no drafting model behind it, and that every gate it depends on can be
satisfied by prose written in that context — which is a statement about the gates'
reach, not about the prose.
