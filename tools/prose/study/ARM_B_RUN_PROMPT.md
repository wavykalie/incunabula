You are the operator for **Arm B** of a prose study. This prompt is self-contained: read it
once, then work. It tells you what the study is, what you may and may not do, where every
file is, and the exact commands. Nothing here needs you to have been in a previous
conversation.

---

## 1. What the study is

The study asks one question: **does a gated, multi-phase writing pipeline produce prose that
a naive single conversation does not?** Same premises, two arms, one variable — the pipeline.

- **Arm A is finished.** Twenty books, each one fresh prompt to a model, filed under
  `tools/prose/study/books/A-01 … A-20`. Do not touch them.
- **Arm B is what you are running.** The same twenty premises fed through this repo's own
  seventeen-phase pipeline (`bash tools/run-phases.sh`), plus six voice books and three
  long books. Each B book is filed as one row in `tools/prose/study/books/manifest.csv`.

Your job right now is **B-01, alone, end to end**, and then a report. One book is not twenty;
the point of doing one alone is to measure what one costs before twenty are attempted.

## 2. The one rule that governs everything

**A pipeline book that a person rescued is not evidence about the pipeline. It is evidence
about that person.** So your actions are bounded, and they are counted:

**Allowed (four things, nothing else)**
1. Fill declared intake fields from the premise text or the plan row, verbatim.
2. Answer any gate prompt with the pipeline's own default or recommended option.
3. Approve a ductus / voice / cast candidate **without editing its text**.
4. Stop the book and report it.

**Forbidden — any one of these is a stop condition, not an "intervention"**
- writing, rewriting, selecting between, or extending prose;
- editing the pipeline output for any reason, including "it ends mid-word";
- switching a gate off, lowering a threshold, or editing a threshold's input;
- hand-merging two drafts, or splicing a repaired chapter;
- editing `PROJECT_STATE.yaml` plan numbers so that C1 agrees after the draft diverged.

**Counting.** Every action you take goes in `books-armb/B-01/logs/operator.md`, one row per
action, at the time you take it:

```
| ts | phase | kind | what happened | option taken | counted |
```

`kind` is one of: `transcribe` (verbatim from premise or plan — logged, **not counted**),
`gate` (a decision among options, including accepting the default — **counted, one per
answer**), `approve` (a candidate accepted unchanged — **counted**), `prose` (**should never
appear**; if it does, the book is a stop condition and its row is not filed).

`--interventions N` at filing time is the number of `counted=yes` rows. A gate **firing** is
not an intervention — it is the pipeline working. Your answer to it is the intervention, if
there was one. Zero is a legitimate count. An unrecorded three is not.

## 3. Where everything is

Let `REPO` be the repository root, `STUDY=$REPO/tools/prose/study`, and `WT` the run's
worktree at `$STUDY/run/out/armb-wt` (`run/out/` is git-ignored).

| thing | path |
|---|---|
| the book, while it runs | `$WT/books-armb/B-01/` |
| its operator ledger | `$WT/books-armb/B-01/logs/operator.md` |
| the premise you must send | `$STUDY/run/out/payloads/B-01.txt` |
| the dispatch card (read it) | `$STUDY/run/out/briefs/B-01.md` |
| the plan row | `$STUDY/run/out/RUNPLAN.csv` (line for `B-01`) |
| assembled text you will file | `$STUDY/run/out/responses/B-01/final.txt` |
| chapter tree you must copy | `$WT/books-armb/B-01/manuscript/chapters/` → `$STUDY/books/B-01/manuscript/` |
| design records | `$STUDY/DECISIONS.md`, `$STUDY/ARM_B_BRIEFING.md`, `$STUDY/RUNBOOK.md` |

Read `$STUDY/ARM_B_BRIEFING.md` before you start. It is the long form of this prompt.

## 4. The frozen instrument

Every B row records `pipeline_commit`, the hash of the pipeline that wrote the book:

```
8265c48d12962ca233ed98bd10083edb072ec7f0
```

The run happens **at** that commit, in a git worktree, not beside it. The pipeline code in
`WT` must never be edited. Three data files in that tree legitimately differ, all recorded in
`$STUDY/DECISIONS.md`:

1. `BOOKS.yaml` — `books: []` became `books:` so a book can be registered at all. Without it
   the first `init-book` writes YAML that does not parse and `ductus.py contract` refuses with
   "BOOKS.yaml is missing or does not parse".
2. `tools/prose/calibration/PREMISE_LEDGER.tsv` — the public template ships **empty** (the
   author's own premises were de-identified out of it). Phase 1's premise gate refuses an
   empty ledger with exit 2 **by design**, so no B book can clear phase 1 without the seed.
   Restore it: keep the file's `#` header lines, append the rows from
   `$REPO/.private/record/PREMISE_LEDGER.seed.tsv` (three rows, six tab-separated fields).
3. `GATE_FREEZE.md` — the ledger's recorded hash must be re-recorded to
   `f06f9c4baabc47d5` with a dated note, or `verify-freeze.sh` reports
   `CHANGED (frozen f4c03a83537f0270)` and `preflight.sh` fails with "results would not be
   attributable", which refuses the whole run.

**If the worktree already exists and `books-armb/B-01/PROJECT_STATE.yaml` is there, all three
are already done** — confirm with the two commands below and do not repeat them:

```bash
cd "$WT"
bash tools/prose/verify-freeze.sh   # must print FREEZE HOLDS, rc 0
bash tools/preflight.sh             # must print VERDICT: READY, rc 0
```

If either fails, stop and report. Do not "fix" a gate.

## 5. B-01's exact values (from RUNPLAN.csv — verify, do not assume)

| field | value |
|---|---|
| premise id | `adv-01` ("the wet season", adventure) |
| payload | `run/out/payloads/B-01.txt`, 77 words, `sha256 66c44e43257c125dac7f293f018b191acc53370f8c22713aa132221e7808f7ee` |
| target | 60,000 words; accepted band **54,000–66,000** |
| plan | 40 chapters × 1,500 words |
| `ductus_id` | `UNASSIGNED` (primary books carry no voice — do not assign one, do not leave it blank) |
| model | sent `gemini-3.8-flash`; the resolver reports `gemini-3.8-flash-high`; **one model id per row** |

`premise.md` in the book root is already the payload, byte for byte (sha matches, nothing
appended). Do not rewrite it.

## 6. The walk

Run everything from `$WT` unless a `cd` is shown.

```bash
cd "$WT"
bash tools/run-phases.sh books-armb/B-01            # resumes from the state's pointer, else phase 1
bash tools/run-phases.sh books-armb/B-01 --from 3.5 # explicit resume after a halt
bash tools/run-phases.sh --list                     # the seventeen phases
```

The runner runs each phase's **gate tools** itself and parses their **exit codes** — never a
report — and hard-stops on anything but 0, writing a resume pointer into `PROJECT_STATE.yaml`.
It does not do content work: each phase is a specialist skill you invoke. A CLEAR means the
gates passed; it never means the book is good, and it never covers the map's `human` column.

**Phase 1 (Research, skill `scout`) is where you are.** Its exit gates are `comps` and
`premise`, and both refuse right now for correct reasons:

- `check-comps.py` needs `books-armb/B-01/research/market-research.md`, and every comp row in
  it must carry a verification line:
  `| Author, *Title* (year) | **VERIFIED** <YYYY-MM-DD> — publisher, ISBN; comp slot |`
  A comp that is neither verified nor explicitly marked a falsification fails the gate. This
  gate exists because four of six comps in one book's research file turned out not to exist.
- `check-premise-distinct.py` needs three axes declared in `PROJECT_STATE.yaml`
  (`premise_axes: profession / engine / relationship`) — the block is there, commented out,
  waiting for phase 1 to declare from the premise rather than before it. It compares them
  against the three spent premises in the ledger and fails on a two-axis match.

Do the phase-1 content work so those gates can pass honestly. That is research and
declaration, not prose: no drafting happens before phase 3.

## 7. Assemble and file (after the walk reaches delivery)

**Assemble with `ls -v`, not a plain glob.** Chapter files are zero-padded, so a plain glob is
correct to 99 chapters and silently wrong at 100 — `chapter-100.md` sorts before `chapter-11.md`
and the novel is reordered with no word changed. Keep the `# Chapter NN` headings: they are
what filing counts chapters from.

```bash
mkdir -p "$STUDY/run/out/responses/B-01"
cd "$WT/books-armb/B-01/manuscript/chapters"
ls -v chapter-*.md | xargs cat > "$STUDY/run/out/responses/B-01/final.txt"
cd "$WT"
```

**Copy the chapter tree — this is mandatory.** It is what the gates and the extractor measure.

```bash
cp -r "$WT/books-armb/B-01/manuscript/chapters" "$STUDY/books/B-01/manuscript/"
```

**File once. One response per book.** Arm B never receives Arm A's continuation cadence.

```bash
cd "$STUDY"
python run/dispatch.py --ingest B-01 \
    --response run/out/responses/B-01/final.txt \
    --model-returned gemini-3.8-flash-high \
    --pipeline-commit 8265c48d12962ca233ed98bd10083edb072ec7f0 \
    --interventions <N> --finalize \
    --deviation "freeze ledger row re-recorded 2026-11-03 (PREMISE_LEDGER.tsv seeded from .private; DECISIONS.md)"
```

If the pipeline returned the book in parts, concatenate the parts **in order** into that one
file and file it once with an extra `--deviation "assembled from N pipeline returns"`. Never
file parts as continuations: the logged prompt would then be Arm A's sentence, which is not
what the pipeline was given.

`--finalize-only` exists for the case where the last ingest already ran and only the row is
missing. Re-running the ingest instead appends the text twice.

## 8. Verify before you stop

```bash
cd "$STUDY"
python manifest.py --check books/manifest.csv     # 0 problems; a band note is data, not an error
python extract/features.py books/B-01             # chapter count MUST equal the row's
```

The second line is the check nobody else will catch: if extraction says `1ch` while the book
has forty, the chapter tree was not copied or the headings were stripped. Fix the copy before
anyone files another book. A book outside 54,000–66,000 is an **outcome** — file it with the
band note. Never regenerate a book to make a number nicer.

## 9. Stop and report — do not improvise — if

- the drafting model's resolver id changes mid-run (the dispatcher refuses the row anyway);
- the frozen commit changes mid-run;
- a gate is bypassed, or a threshold or its inputs are edited;
- the book cannot proceed without you writing prose;
- the pipeline returns a book far outside the band (file it, then decide with the author
  before the next book — never by regenerating this one);
- two books refuse to file for a reason no deviation explains.

A gate that fires and forces a rewrite is **data**: log it as a `--deviation`. A gate switched
off is a protocol deviation and the book is not evidence.

## 10. What to report back

Four numbers, because they decide whether twenty books are worth running:

1. wall-clock time for B-01, start to filed row;
2. the drafting phase's token usage (input and output);
3. the intervention count — your `counted=yes` rows, and what kind of decisions they were;
4. the pipeline's own word count against 60,000, and the chapter count.

Then: the manifest row, the extraction line, `manifest.py --check` output, and anything that
surprised you. If something about this prompt was wrong or out of date, say so — the record is
worth more than the run looking clean.
