# Arm B briefing — the pipeline arm, from a frozen commit to a filed row

**Written 2026-11-03, before B-01.** This is the operating packet for the pipeline books:
twenty primary (`B-01`…`B-20`), six voice (`B-02V/W`, `B-03V/W`, `B-09V/W`), three long
(`B-L01`…`B-L03`). `RUNBOOK.md` §9 is the one-screen summary; this is what an operator —
person or agent — keeps open while a book runs.

It assumes `DECISIONS.md` as written: Gemini 3.8 Flash drafts, sampling is harness-fixed,
the CLI resolver's id is the model evidence, and primary Arm B carries **no** ductus.

## 0. What the arm is and what it is not

Arm A is one naive conversation per book. Arm B is **the same premise fed to this repo's own
pipeline**: seventeen gated phases, specialist skills, real gates. One variable changes —
the pipeline — so the pipeline has to be an artifact with a hash, and every human decision
along the way has to be counted. A pipeline book that a person rescued is not evidence about
the pipeline; it is evidence about that person.

Two consequences that shape everything below:

- **One response per book.** The pipeline returns the book; it is filed once. Arm B never
  receives §3's continuation sentence — that cadence is Arm A's condition, not a shared one.
- **The operator is a covariate, not a participant.** What the operator may do is bounded
  here (§5) and the count lands in `operator_interventions`.

## 1. The freeze — `8265c48d12962ca233ed98bd10083edb072ec7f0`

**This needs Kalie's yes**: every B row records it, and `manifest.py` rejects a B row
without it, so it has to be chosen before B-01 opens, not reconstructed afterwards.

Why this commit — measured today, not assumed:

```bash
git diff --stat HEAD -- skills tools/*.sh tools/check-*.py tools/lint-chapter.py \
    tools/phase-state.py tools/init-book.py tools/roll-brief.py tools/ductus.py \
    tools/phase-map.yaml BOOKS.yaml COMMONPLACE.md ductus ductus.yaml
# prints nothing: the pipeline is identical to HEAD
```

HEAD also contains `run/dispatch.py` and `manifest.py` exactly as the rows are filed by.

**What the hash does not cover.** The study-side work in the working tree is uncommitted —
`DECISIONS.md`, `README.md`, `RUNBOOK.md`, the premise sign-off, and the untracked
`preflight.py`, `run/drive.py`, `run/harness.json`, `books/`. If the hash should describe the
whole apparatus, commit those first and freeze the new hash. If it describes the **pipeline**
(design §11's reading, and the one `pipeline_commit` names), `8265c48` is correct and this
paragraph is the record of the gap.

Run *at* the commit rather than beside it, so the claim is true by construction:

```bash
git worktree add tools/prose/study/run/out/armb-wt 8265c48d12962ca233ed98bd10083edb072ec7f0
cd tools/prose/study/run/out/armb-wt && git status --porcelain   # must print nothing
```

`run/out/` is git-ignored, so the worktree is not a change to this repo. If the hash is
re-frozen, every row filed before the change belongs to the old sub-cohort — say so in
`deviations`, do not pool them.

## 2. Where the pieces live

| piece | path | why there |
|---|---|---|
| the book, while it runs | `<worktree>/books-armb/B-<id>/` | inside the frozen tree, registered in that tree's `BOOKS.yaml` |
| what analysis reads | `books/B-<id>/manuscript/chapters/chapter-NN.md` | the layout the gates and `extract/features.py` both resolve |
| what filing records | `books/B-<id>/manuscript/pipeline-text.md` | written by `dispatch.py`, the filed text |
| the §4 phase log | `<worktree>/books-armb/B-<id>/` | `PROJECT_STATE.yaml`, `RUN_REPORT.md`, verdicts |
| the operator ledger | `<worktree>/books-armb/B-<id>/logs/operator.md` | §5 |

Verified today: `extract/features.py <book-dir>` resolves `manuscript/chapters/*.md` and reads
them as chapters (a two-chapter fixture got past loading and stopped only at the 33-word
floor), while a book directory holding nothing but a flat `*-text.md` is **refused** —
`no chapters and no text files`. So the chapter tree is the artifact that gets measured, and
the copy in step 6 is not optional.

## 3. One book, end to end

All paths relative to the worktree unless said otherwise. `<ID>`, `<premise_id>`, `<genre>`,
`<target>`, `<lo>`/`<hi>`, `<label>` come from that row of `run/out/RUNPLAN.csv`.

```bash
STUDY="$(cd ../../.. && pwd)"   # tools/prose/study in the main checkout; this worktree has its own copy
```

**1. Scaffold**

```bash
BOOKS_WORKSPACE="$PWD/books-armb" python tools/init-book.py --path B-01 \
    --title "<label>" --status drafting --floor 54000 --ceiling 66000 \
    --chapters-planned 40 --words-per-chapter 1500
```

- `--chapters-planned × --words-per-chapter` must land inside the declared band, and
  `check-progress` C1 re-checks that agreement for the life of the book. Changing those two
  numbers later to match a drafted reality is a plan edit; it is not free (see §5).
- Long books: `--floor 180000 --ceiling 220000 --chapters-planned 100
  --words-per-chapter 2000`.
- `init-book` needs a title before the pipeline has one, so it gets the plan's `title_label`
  — one to three words, logged as `transcribe`. It is the study's label for the pair, not a
  premise field, and it is never used to steer content.

**2. Intake — transcription only**

| field | value | source |
|---|---|---|
| premise / concept | the exact bytes of `run/out/payloads/<ID>.txt` | check `sha256` against `RUNPLAN.csv` **before** pasting |
| genre | the plan row's `genre` | plan |
| length | `<target>` words, band `<lo>`–`<hi>` | plan, `DECISIONS.md` §2 |
| language | English | plan |
| audience, market, structure, output form | the pipeline's own default or recommendation | rule 2 in §5 |

The payload for Arm B is the **bare premise text** — no §3 wrapper. `preflight.py` checks
that every B payload reproduces a frozen premise byte for byte; run it and do not paste from
anywhere else.

**3. Resolve the voice — before phase 2.5, again before any prose**

```bash
python tools/ductus.py contract books-armb/B-01                 # primary: expect UNASSIGNED
python tools/ductus.py contract books-armb/B-02V --ductus study-voice-a
```

- `UNASSIGNED` (exit 0) is the row's `ductus_id`. It is a fact the tool asserts, which is why
  the field is never typed by hand and never left blank.
- A book that is not registered says `UNREGISTERED`, which is a different fact and not the
  one a row may record. Scaffold first (step 1).
- `REFUSED` (exit 1) stops the phase. Do not fall back to the root ledger.
- Record the contract + ledger digests it prints, per book, in the ledger.

**4. Walk the phases**

```bash
bash tools/run-phases.sh books-armb/B-01            # from the resume pointer
bash tools/run-phases.sh books-armb/B-01 --from 3.5 # explicit resume after a halt
bash tools/run-phases.sh --list
```

The runner parses gate **exit codes**, never a report, and hard-stops on anything but 0,
writing the resume pointer into `PROJECT_STATE.yaml`. A CLEAR covers the gates it ran; it
never covers the `human` column, which no tool enforces. That column is §5's job.

**5. Assemble**

```bash
cd books-armb/B-01/manuscript/chapters
ls -v chapter-*.md | xargs cat > "$STUDY/run/out/responses/B-01/final.txt"
cd - >/dev/null
```

`ls -v` (version sort) matters: `init-book` writes zero-padded `chapter-NN.md`, so a plain
glob is correct up to 99 chapters and then silently wrong — at one hundred, `chapter-100.md`
sorts before `chapter-11.md` and the novel is reordered without a word changing. The long
stratum plans exactly 100, so use `ls -v` for any book that can pass 99; it is harmless
below that. Keep the `# Chapter NN` headings — they are what `dispatch` counts chapters
from (§6, trap 1).

If the pipeline returns the book in parts, concatenate the parts **in order** into this one
file and file it once with `--deviation "assembled from N pipeline returns"`.

**6. Copy the chapter tree, then file once**

```bash
cp -r books-armb/B-01/manuscript/chapters "$STUDY/books/B-01/manuscript/"

cd "$STUDY"
python run/dispatch.py --ingest B-01 \
    --response run/out/responses/B-01/final.txt \
    --model-returned gemini-3.8-flash-high \
    --pipeline-commit 8265c48d12962ca233ed98bd10083edb072ec7f0 \
    --interventions <N> --finalize [--deviation "..."]
```

`--model-returned` is the id the **drafting phase's** own calls resolved to (the resolver
line in the `agy` log, per `DECISIONS.md`). If a non-drafting phase resolved to something
else, that belongs in `deviations` as text — §1 records one model per row, and the drafting
model is the one H3 is about.

**7. Verify the row**

```bash
python manifest.py --check books/manifest.csv        # 0 problems; a band note is data
python extract/features.py books/B-01 --out /tmp/chk
```

The extraction line must report the same chapter count as the row. If it says `1ch`, the
chapter tree was not copied or the headings were stripped — fix the copy before B-02, not
after twenty books.

## 4. What the pipeline does to the premise — log it

REDTEAM.md B4's second point: if the foundation phase rewrites the premise into its own
logline and beats, then B's input is no longer literally A's input, and the pair's
comparison has a gap nobody measured. So each book's ledger records the foundation's logline
beside the premise's first line. It costs one line and it is either a validity check or a
finding.

## 5. The operator script

REDTEAM.md B4 says the operator may only do four things. This is that list as the arm's
rule, with the counting rule attached, because a count whose definition is chosen after the
fact is not a covariate.

**Allowed**

1. Fill declared intake fields from the premise text or the plan row, verbatim.
2. Answer any gate prompt with the pipeline's own default or recommended option.
3. Approve a ductus / voice / cast candidate **without editing its text**.
4. Stop the book and report it.

**Forbidden — any one of these is a stop condition, not an intervention**

- writing, rewriting, selecting between, or extending prose;
- editing the pipeline's output for any reason, including "it ends mid-word";
- switching a gate off, lowering a threshold, or editing a threshold's inputs;
- hand-merging two drafts into one, or splicing a repaired chapter;
- editing `PROJECT_STATE.yaml` plan numbers to make C1 agree after the draft diverged.

**Counting**

`books-armb/B-<id>/logs/operator.md`, one line per action. Copy the sheet from
`run/operator-log-template.md` before step 1 rather than writing the format out again per
book — it carries the four permitted kinds, the counting rule and the §4 logline field:

```
| ts | phase | kind | what happened | option taken | counted |
| 2026-11-04T10:12Z | 2 | gate | outline approval prompt | pipeline's recommended outline | yes |
| 2026-11-04T09:40Z | 1 | transcribe | genre, length, band from RUNPLAN | — | no |
```

- `transcribe` — verbatim from the premise or the plan. Logged, not counted.
- `gate` — a decision among options: count **one** per answer, including a default.
- `approve` — accepting a candidate unchanged: count one.
- `prose` — should never appear. If it does, the book is a stop condition and the row is not
  filed.

`--interventions` is the number of `yes` lines. **A gate that fires is not an intervention**;
it is the pipeline working, and it is logged as a gate outcome (a `--deviation` if it forced
a rewrite). The operator's answer to it is the intervention, if there was one. Zero is a
legitimate count — an unrecorded three is not.

## 6. Traps, each one already paid for somewhere

1. **Chapter count reads headings.** `finalize` counts `^#{1,3}\s*(?:chapter|\d+[.:])` in the
   filed text. Strip the headings on assembly and the row files `chapter_count: 1` while the
   manuscript has forty — and the primary endpoint `syn_chapter_sentlen_spread` has one
   chapter to work with.
2. **Never file parts as continuations.** The logged prompt would then be §3's sentence,
   which is not what the pipeline was given. Assemble, then file once.
3. **`--pipeline-commit` is the full 40 characters.** Short hashes are not a version.
4. **`ductus_id` comes from `ductus.py contract`,** not from memory. Blank is rejected;
   `UNREGISTERED` is a different fact from `UNASSIGNED`.
5. **Voice books: a gate firing under the contract is data, not a bug.** The contract was
   authored for reach and its long uniform sentences may trip `check-uniformity`'s spread
   gate — REDTEAM M7's risk firing. Log it in `deviations`; do not tune the contract, and do
   not waive the gate to get the book through.
6. **`--finalize-only` exists** for the case where the last ingest already ran and only the
   row is missing. Re-running the ingest instead appends the text twice.

## 7. Before B-01 — the make-ready

```bash
cd tools/prose/study
python run/rehearse-armb.py                      # the filing path on throwaway books, rc 0
python preflight.py                              # READY, rc 0
python selftest.py                               # the harness on fixtures, rc 0
python ../../tools/ductus.py check               # from tools/prose/study
cd run/out/armb-wt && git rev-parse HEAD && git status --porcelain
```

- `run/rehearse-armb.py` writes two throwaway pipeline books in a temp tree and files them
  through the exact commands in §3: the payload check, `ls -v` assembly, one-response filing,
  the short-commit refusal, `--finalize-only`, and the heading-strip that files
  `chapter_count: 1`. It touches nothing real and can be re-run; **if it is red, do not open
  B-01.**
- `preflight.py` re-verifies the frozen premises, every plan payload digest against
  `RUNPLAN.csv`, and the probe record. **All twenty B payloads are covered by it**; it was
  run today and returned `VERDICT: READY`.
- The worktree must be clean and at the frozen hash. A modified file there means the run is
  not at the commit it will claim.
- `ductus.py check` must not report a skeleton or an isolation failure for either study
  voice; the digests in `ductus/study-voice-*/ductus.md.sha256` must still match.

**Not about Arm B, but blocking §10:** `extract/features.py books/A-01` currently exits 1
(`no chapters and no text files under books/A-01`) because the naive books have
`manuscript/naive-text.md` and no chapter tree, and `--all books` therefore stops on the
first book. Arm B will be extractable by construction (step 6). Arm A is not, today. Fix the
Arm A side before the analysis run, not during it.

## 8. Stop conditions

Stop the book, keep every file, and report — do not improvise — if:

- the drafting model's resolver id changes mid-run (`dispatch` refuses the row anyway);
- the frozen commit changes mid-run;
- a gate is bypassed, or a threshold or its inputs are edited;
- the book cannot proceed without the operator writing prose;
- the pipeline returns a book far outside the band — file it with the band note and the
  outcome, and decide with Kalie before the next book, not by regenerating this one;
- two books refuse to file for a reason no deviation explains.

## 9. Shape of the block

One book is not twenty. Run **B-01 alone**, end to end, then look at four numbers before
committing to the rest: wall-clock per book, drafting-phase token usage, the intervention
count, and the pipeline's own word count against 60,000. Arm A's cost (2.05M input / 0.49M
output tokens for eight calls on one book) is not a forecast for a seventeen-phase run with
revision loops — the pipeline makes many more calls, at gate time and in the revision cycles.

The author has ruled cost irrelevant (3% of a weekly limit on a whole book), so the binding
resource is **operator attention** — which is exactly what `operator_interventions` measures.
A block of twenty books is twenty times that attention, not twenty times Arm A's eight calls.

Long books (`B-L01`…`B-L03`) last, as their own stratum, never pooled with the twenty.
