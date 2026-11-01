# study — the 50-novel prose-tell study (harness)

**State: harness plus the human distribution corpus. No A/B book has been generated.**
Five of design §12's seven decisions are settled (`DECISIONS.md`): Gemini 3.8 Flash drafts
both arms through subagents, DeepSeek runs the study, there are no blind raters, the human
ten are deferred until after generation, the primary target is **60,000 words** with a
separate 200,000-word long-form stratum, and **Arm B carries no ductus** — UNASSIGNED is the
state every catalogue book was drafted in, so that is the pipeline as it exists (§12.3).
The long-form premises are frozen too (`premises-v2.json`: adv-03, hor-01, sf-03) and
`run/dispatch.py --plan` writes all **52** books — 20 primary pairs, 6 voice books, 3 long
pairs, **3.96M words** of target. Generation now waits only on the premise sign-off and on
the two Antigravity facts that decide what each row can record; no §12 answer is outstanding.
Nothing here is a finding about AI prose and nothing here should be quoted as one; the one
measured artifact is a *human* baseline.

What exists is everything that can be built without those answers: the premise pool and
its freeze, the frozen feature extractor, the manifest schema, the analysis, the self-test
that proves they connect, and — the amendment REDTEAM.md lists first — Arm C's distribution
half: 109 public-domain novels measured through the frozen extractor (`corpus/`). Arm C's
ten, the excerpt ratings, and every A-vs-B or B-vs-C comparison still need the §12 answers.

Everything in this directory was written against **design v1 (2026-10-30)** and the review
in `REDTEAM.md`. Where the two disagree, `REDTEAM.md` says why and the code follows the
review; the deviations are listed below rather than left in the diff.

## Layout

```
study/
  RUNBOOK.md            the operator procedure: one book, from a fresh subagent to a
                        finalized manifest row
  REDTEAM.md            the review of design v1, with an ordered amendment list
  DECISIONS.md          design §12 answered in writing: what is settled, and what blocks what
  PREREGISTRATION.md    primary endpoints, every feature's status, the classification rules
  README.md             this file
  manifest.py           the only place the manifest columns are defined
  selftest.py           23 checks over the whole harness, run on fixtures
  premises/
    candidates.json     40 premises, 4 per genre, no person names, no style language
    premise.py          validate / render / seeded stratified sample / freeze / verify
    frozen/             premises-v1.json + .sha256  (the twenty, provisional pending Kalie)
                        premises-v2.json + .sha256  (the 3 long-form premises, exploratory)
  ductus/
    README.md           why the primary arm has no voice, and what the sensitivity arm is
  run/
    dispatch.py         the run plan, the per-book dispatch card, and response ingest
    out/                RUNPLAN.csv, briefs/, payloads/  (git-ignored, derived)
  extract/
    features.py         the frozen extractor; imports the shipped gates, does not copy them
  analysis/
    analyze.py          distributions, paired A-vs-B, five-way classification, residual rule
    voices.py           the voice arm: this hand or voice-ness, per feature
  fixtures/
    make-fixtures.py    synthetic A/B/C books; NOT data, exists to test the plumbing
  corpus/
    fetch-dist.py       C-dist: select from Gutenberg's catalogue, file, verify
    dist-source.tsv     the 120 selected slots — ids, authors, era and genre strata
    dist-fetch-log.tsv  what was filed: raw and segmented word counts, chapters, sha256
    dist-rejects.tsv    the slots that could not be filed, with the reason
    pg_catalog.csv      Gutenberg's catalogue, 21MB (git-ignored, refetchable)
  books/                A-01 … A-20, B-01 … B-20, C-01 … C-10, C-dist-NNN  (from the runs)
```

Book directories use `<book>/manuscript/chapters/chapter-NN.md`, the layout the existing
gates resolve. Point `check-uniformity.py`, `check-drift.py` and `check-arc.py` at the same
tree and they work unchanged; the study does not need its own gates.

## Running it

```bash
cd tools/prose/study

python premises/premise.py                    # validate the 40-premise pool
python premises/premise.py --sample           # freeze 20, 2 per genre, writes a hash
python premises/premise.py --verify           # re-hash; refuses to say ok if tampered
python premises/premise.py --render lit-01    # the exact text both arms receive
python premises/review-sheet.py              # the 20-premise sign-off sheet (§13)
python premises/premise.py --sample-long --out premises/frozen/premises-v2.json
                                            # freeze the 3 long-form premises (v2)

python extract/features.py --selfcheck        # constants, lexicons, registry
python extract/features.py BOOK_DIR --out DIR # one book
python extract/features.py --all books --out features

# Arm C-dist: the human baseline every §10 threshold is derived from (REDTEAM.md B1)
python corpus/fetch-dist.py --select          # 120 stratified slots -> dist-source.tsv
python corpus/fetch-dist.py --fetch           # download, split, file books/C-dist-NNN
python corpus/fetch-dist.py --check           # every filed book against its logged counts
python extract/features.py --all books --out corpus/dist-features
python analysis/cdist.py --features corpus/dist-features

python analysis/analyze.py --features features --manifest books/manifest.csv --out analysis
# --max-words 120000 keeps the exploratory 200k long-form stratum out of the primary run

# the voice arm only, against its own twins (DECISIONS.md §3)
python analysis/voices.py --features features --manifest books/manifest.csv

# the run: plan first, then one ingest per response
python run/dispatch.py --plan                # 52 books -> run/out/{RUNPLAN.csv,briefs,payloads}
python run/dispatch.py --ingest A-01 --response resp.txt \
    --model-returned gemini-3.8-flash-001 --finalize

# the run itself, per book, step by step: RUNBOOK.md
python selftest.py                            # the whole harness on fixtures, 51 checks
```

Before generation: `python manifest.py --init books/manifest.csv`, then one `--add` per
book. The manifest validates the fields a study row cannot omit — pipeline commit and
ductus for Arm B, prompt logs for both generated arms, operator interventions, naive
continuation count.

## Deviations from design v1, and why

Each of these is reversible before generation. None is silent.

| # | deviation | reason |
|---|---|---|
| 1 | **Arm C is split**: C-deep (10 books, excerpts and face validity) and C-dist (≥100 public-domain novels for every distribution and threshold) — **built**, `corpus/` | §10's deliverable is a threshold, and ten books cannot set one. `README.md` in `tools/prose/` already states the rule: six volumes can refute a floor, not set one. REDTEAM.md B1 |
| 2 | Six §8 features are pre-registered as `replication`, not hypotheses | this repo has already measured them as nulls or with the opposite sign. Re-testing them is fine; treating them as new is not. REDTEAM.md B2, PREREGISTRATION.md §2 |
| 3 | Chapter structure is an **outcome**; the analysis unit is the book plus fixed segments | the arms produce different chapter conventions, so chapter-level rows compare units that do not match. REDTEAM.md B3 |
| 4 | An operator script is required, and interventions are counted in the manifest | Arm B contains human gate decisions and Arm A contains none; without a script, rescue is attributed to the pipeline. REDTEAM.md B4 |
| 5 | Naive continuation cadence is fixed and logged per book | a 50k-word "one prompt" is really N continuations of a truncating context. That is a condition, and it must be chosen rather than discovered. REDTEAM.md B5 |
| 6 | The premise pool renders at 64–91 words, not §6's 100–200 | a shorter premise leaves the arms more room and raises cross-premise diversity, which is what makes H3 interpretable. Recorded by the validator on every run. §13 still requires Kalie's yes on the list before generation |
| 7 | Premises carry **no person names** and no `tone`/`ending` fields | §8.4 measures which names a model reaches for; a premise that supplies "Mira" removes the measurement. A tone hint is a style instruction at the margin, and §6 forbids those. Uniform omission keeps the fields identical across premises, as §6 requires |
| 8 | Five classification categories, with "unclear" defined, and `no A-vs-C gap` excluded from "fixed" | §9.5 and §9.6 disagree; forcing a borderline case into a win or a loss is how a report acquires findings it did not measure |

## What is frozen, and what that means

- `premises/frozen/premises-v1.json` is hashed and refuses to overwrite. Changing a premise
  is a protocol deviation, not an edit: write a new version with `--out` and log it.
- `extract/features.py` and `PREREGISTRATION.md` are frozen together at the start of
  generation. The feature names and the code that computes them are one artifact, because
  this repo has four recorded cases of a feature name staying correct while the number
  moved (`check-arc.py`'s truncated lexicon, tokenizer and window).
- The pool hash is inside the frozen file, so the sample can be tied back to the 40.

## Stop conditions (design §13, unchanged)

Stop and ask rather than improvise if: the drafting model version changes mid-run, the
pipeline version changes mid-run, a premise proves unworkable, a naive book is edited or a
gate is bypassed, or the human ten cannot meet §5's criteria without changing them.

Two operational rules from this repo's own defect log apply to every run here:

- capture an exit code before piping (`out=$(cmd); rc=$?`), and
- a run that read zero files is a failure, never a pass.

## What this study is not

Not a humanizer, not a detector-evasion benchmark, not a claim about AI prose in general,
not a substitute for reading the books, and not a claim that pipeline output "passes as
human". Design §10's non-goals belong in the body of any write-up, not an appendix.
