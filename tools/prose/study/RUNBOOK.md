# RUNBOOK — getting one book from a subagent to a manifest row

The operator procedure, for one book at a time. Assumes `run/dispatch.py --plan` has been
run once and the premise sign-off is in (`premises/frozen/premises-v1-review.md`). Design
sections referenced are design v1; decisions are `DECISIONS.md`.

Nothing in this file is a shortcut. Every rule below exists because the thing it prevents
is unobservable after the fact: a reconstructed prompt, a rescued chapter, a shared
conversation, a re-rolled opening.

## 0. Before the first book

```bash
cd tools/prose/study
python selftest.py                      # 51/51, rc 0. A red check stops the run.
python run/dispatch.py --plan           # once. 52 books -> run/out/{RUNPLAN.csv,briefs,payloads}
python preflight.py                     # rc 0 before you dispatch. Run it every session.
python run/rehearse-armb.py             # before B-01: the filing path on throwaway books
```

`preflight.py` re-verifies the three things a session takes for granted: the frozen
premises still match their hashes and their own render, every plan payload still matches
the digest in `RUNPLAN.csv` and still reproduces a frozen premise byte for byte, and the
probe record is a measurement. Exit **1** means something disagrees — do not dispatch.
Exit **2** means nothing is broken but the probe record is blank, which is the expected
state before A-01's first call: dispatch can continue, no row can be filed.

- `--plan` refuses to overwrite an existing plan. **Never** pass `--force` after a book has
  been drafted — the plan is the prompt record, and rewriting it relabels books already
  filed (`DECISIONS.md` §7).
- `run/out/` holds `RUNPLAN.csv`, one card per book in `briefs/`, the exact bytes in
  `payloads/`. It is git-ignored and derived; the filed books are not.
-Two facts about the route are still unmeasured (`DECISIONS.md` §7 item O3), and both decide
what a row may claim. They are probed once, on the first call of the first book, and then
read by every filing after it.

### The probe record — once, on A-01

```bash
python run/harness.py --template     # the questions
python run/harness.py --init         # writes run/harness.json to fill in
python run/harness.py --check        # validates, and prints what every row will record
```

Fill it from A-01's **first** call and never by hand again: the route is a property of the
run, not of a book, and retyping a value 52 times is how a wrong one gets in. `model_sent` is
what we asked for; `model_returned` is what the response said it was. They are different
facts and both are recorded.

| what you find | what it forces |
|---|---|
| temperature or top-p can be set | `settable: true` and the **observed** value — the one the call actually used |
| they cannot be set | `settable: false` and `applied`: the harness's own value. The report carries "sampling fixed" as a limitation |
| the system prompt is harness-fixed | the same, under `system_prompt` |
| every response reports `modelVersion` | record it; each row carries it |
| no version is reported | `model_returned: null` and **stop**: `--check` refuses, because H3 is a claim about the version that wrote |

From then on `dispatch.py` reads the record: it supplies each row's sampling values, refuses
a `--temperature` the probe says cannot be set (a logged request is not a measurement), and
refuses a book whose response reports a different `modelVersion` — design §7's mid-run model
change — unless `--deviation` files it as a second sub-cohort.

Both filing checks were calibrated before generation, on human novels and on the premises
themselves: `analysis/filing-checks-fp.md` (1 collision in 5,886 unrelated-human pairs) and
`analysis/filing-checks-premises.md` (0 in 780 premise pairs). Re-run either if a premise
file or a gate constant changes; a calibration that is not re-run is a claim about an older
version of the check.

## 1. Pick the next book, in this order

| order | stratum | ids | why here |
|---|---|---|---|
| 1 | Arm A, primary | `A-01` … `A-20` | the control; nothing depends on it but the pairing |
| 2 | Arm B, primary | `B-01` … `B-20` | follows its own premise's Arm A book, same day if possible |
| 3 | voice books | `B-02V`, `B-02W`, `B-03V`, `B-03W`, `B-09V`, `B-09W` | each needs its UNASSIGNED twin (`B-02`, `B-03`, `B-09`) filed first |
| 4 | long-form | `A-L01`…`A-L03`, `B-L01`…`B-L03` | separate stratum; never pooled with the primary |

One book at a time, start to finish, before starting the next. Interleaving two books in
one subagent is the leak the filing checks exist to catch, and catching it costs a book.

## 2. Dispatch — a fresh subagent, the payload only

Open `run/out/briefs/<ID>.md`. It has two parts:

- **Operator rules** — for you. Never send these lines.
- **`## PAYLOAD`** — the exact bytes the model receives.

1. Start a **new subagent with no shared context**: not the conversation that drafted any
   other book. One conversation per book, for its whole life (`DECISIONS.md` §7).
2. Set the model to `gemini-3.8-flash`.
3. Paste the payload **verbatim, with nothing before or after it**. Do not introduce the
   book, do not name the study, do not say what to avoid.
4. Note the `modelVersion` the response reports. No returned version, no filing.

**Arm A** gets the payload once, then only the continuation sentence (§5).
**Arm B** is the pipeline: the payload is the premise the pipeline is entered with. Run
every phase and every gate as it exists at the frozen commit, and log gate outcomes.

## 3. Save the response — exact, unedited

```
run/out/responses/<ID>/01.txt      the first response
run/out/responses/<ID>/02.txt      each continuation, in order
```

- Save the text exactly as returned. No trimming, no fixing typos, no removing fences or
  markdown (`§3`, `§7`). A fence gets a `--deviation` line, not an edit.
- Never hand-edit the manuscript afterwards, for any reason including "it ends mid-word".
- If the subagent stalls: save what came back, and record the stall as an outcome.

## 4. File it

```bash
python run/dispatch.py --ingest A-01 --response run/out/responses/A-01/01.txt \
    --model-returned <version>            [--temperature T] [--top-p P] [--deviation "..."]

python run/dispatch.py --ingest A-01 --response run/out/responses/A-01/02.txt \
    --model-returned <version> --continuation
```

Ingest appends the text to `books/<ID>/manuscript/naive-text.md` (Arm A) or
`pipeline-text.md` (Arm B), and writes `books/<ID>/logs/prompts.jsonl` **at call time**,
with the payload digest.

It refuses, and the refusal is the point:

| refusal | meaning |
|---|---|
| payload digest mismatch | the payload file was edited; the log would describe something never sent |
| second opening response | a re-roll is a deviation, not an overwrite: file it under a new id |
| continuation before an opening | §3's continuation wording only follows a real opening |
| no `--model-returned` | H3 is a claim about the version that wrote, not the one we intended |
| shared opening sentence | a shared subagent context; re-dispatch, or explain with `--deviation` |
| shared 24-word passage | the same leak, found further in; same two options |
| two model versions in one book | §7's stop condition — report two sub-cohorts, never one row |

## 5. Arm A continuations

When the model stops mid-book, the prompt is exactly this sentence and nothing else:

```
Continue the novel from where you left off.
```

No reminder of the premise, no word count, no style note, no "keep going in the same
voice". Any added instruction is a style treatment the naive arm is not allowed to have
(§3). File each continuation with `--continuation`; the count becomes
`naive_continuations` in the manifest.

## 6. Finish the book

Finalise **on the last ingest**, so the last text and the manifest row are written by one
call. Arm A, when the book is as long as the model will make it:

```bash
python run/dispatch.py --ingest A-01 --response run/out/responses/A-01/NN.txt \
    --model-returned <version> --finalize [--interventions 0]
```

Arm B, one response per book — the manuscript as the pipeline returned it:

```bash
python run/dispatch.py --ingest B-01 --response run/out/responses/B-01/final.txt \
    --model-returned <version> --pipeline-commit <40-char hash> \
    --interventions <count> --finalize [--deviation "..."]
```

- `--pipeline-commit` is required for Arm B; `manifest.py` rejects the row without it.
- `--interventions` counts human gate decisions taken during the run (REDTEAM B4). Zero is
  a legitimate count; an unrecorded three is not.
- If the pipeline returns the book in parts, concatenate the parts in order into one file
  and file that once, with `--deviation "assembled from N pipeline returns"`. Do not file
  part one as the opening and the rest as continuations: the logged prompt would then be
  §3's continuation sentence, which is not what the pipeline was given.
- `finalize` refuses a book whose responses report two model versions, and refuses a row
  that `manifest.py` would reject.

**If the last response is already filed and only the row is missing**, do not re-ingest it:
that appends the same text to the manuscript a second time. Write the row from the prompt
log instead, which touches no prose:

```bash
python run/dispatch.py --finalize-only A-01
```

It refuses a book with no log, no manuscript, a model change inside the book, or a row
that already exists — a duplicate is a re-roll question, not a retry.

Then verify:

```bash
python manifest.py --check books/manifest.csv
```

A `note:` about the word band is expected and is data (§7). A `problem:` is not.

## 7. When a filing check fires

Read the evidence it prints before deciding anything: it names the other book and quotes
the sentence or passage.

- **Re-dispatch** to a fresh subagent if the overlap looks like a shared context — the
  ordinary fix, and the one that keeps the arm clean.
- **`--deviation`** if the overlap is coincidence (two novels quoting the same scripture,
  say). The collision is written into the prompt log and the manifest row, so the report
  sees it. The 24-word bar was calibrated on 109 unrelated human novels: 1 pair in 5,886
  fires by coincidence (`analysis/filing-checks-fp.md`).
- Never pre-empt a check by rewording an opening. That is the one edit the study cannot see
  anyone make.

## 8. Short books, stalls, collapses

File what exists and move on. A 41,000-word book against a 60,000-word target is an
outcome, and `manifest.py` prints it as a **note**, not an error, so it can be reported
rather than rescued. Log the stall with `--deviation "stalled at N words after K
continuations"`. Do not quietly substitute a premise, do not regenerate a book to make the
number nicer, and do not lower the target.

A book that never produces novel-length text in **both** arms is design §13's stop
condition: stop and report it, do not improvise a replacement.

## 9. Arm B specifics

The operating packet for this arm — the frozen commit, the per-book procedure, the operator
script and the intervention count — is `ARM_B_BRIEFING.md`. Read it before B-01; the bullets
below are the filing rules it expands.

- **Primary B books carry no ductus.** `ductus_id` is the literal `UNASSIGNED`, the
  pipeline's own no-voice state (`DECISIONS.md` §3). Do not assign one; do not leave the
  field blank.
- **Voice books (`…V`, `…W`) resolve their contract first**, read-only:

  ```bash
  python tools/ductus.py contract books/B-02V --ductus study-voice-a   # from the repo root
  python tools/ductus.py check                                         # contracts still authored?
  ```

  Then run the pipeline and file with `--pipeline-commit`, as any Arm B book.
- A gate that fires and forces a rewrite is **data**: log it with `--deviation`. A gate
  switched off mid-run is a protocol deviation and is logged the same way (§4). Never edit
  the pipeline's output.

## 10. After the last book

```bash
python extract/features.py --all books --out features     # includes C-dist as Arm C
python analysis/analyze.py --features features --manifest books/manifest.csv \
    --out analysis/run --max-words 120000 --exclude-books V,W
python analysis/voices.py --features features --manifest books/manifest.csv \
    --out analysis/voices
python analysis/cdist.py --features corpus/dist-features --out corpus/dist-features
```

- `--max-words 120000` keeps the 200k long-form stratum out of the primary distributions
  and pairing; report that stratum separately.
- `--exclude-books V,W` drops the six voice books, which would otherwise inflate Arm B from
  20 to 26. Their premise ids (`02V`) can't enter the 20-pair comparison anyway.
- Arm C is inferred from the id prefix, so `books/C-dist-*` is the human distribution
  without any manifest rows. Without it `analyze.py` has no baseline and `voices.py`
  refuses to scale its deltas.
- Candidate scanner checks come out of `analysis/run/report.md` §"Residual tells" and go to
  Kalie for review before anything ships (§10). Nothing becomes a pipeline check on
  statistics alone.

## 11. Stop and ask

Stop the run, keep every file, and report — do not improvise — if: the drafting model
version changes mid-run, the pipeline commit changes mid-run, a premise proves unworkable,
a gate is bypassed or a naive book is edited, the human ten cannot meet §5's criteria, or
two books refuse to file for a reason no deviation explains.

## 12. One-book checklist

```
[ ] plan exists, premises verify (dispatch --plan refuses otherwise)
[ ] card read; only the PAYLOAD section was sent
[ ] fresh subagent, no shared context, gemini-3.8-flash
[ ] modelVersion recorded from the response
[ ] probe record filled on A-01 and passing `harness.py --check`
[ ] response saved verbatim under run/out/responses/<ID>/
[ ] ingest ran; no refusal, or a refusal I answered on purpose
[ ] continuations: §3 sentence only, --continuation each time (Arm A)
[ ] finalize on the last ingest (or --finalize-only if it was missed)
[ ] Arm B row has --pipeline-commit and --interventions
[ ] manifest.py --check: 0 problems (band notes are expected)
[ ] deviations written, not remembered
```
