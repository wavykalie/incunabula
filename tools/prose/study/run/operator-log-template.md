# Operator log — <BOOK_ID>

Copy this file to `books-armb/<BOOK_ID>/logs/operator.md` before step 1, and write to it at
the time, not afterwards. It is the only source of the row's `--interventions` number, so a
line added in hindsight is a count nobody can audit (`ARM_B_BRIEFING.md` §5).

Book: `<BOOK_ID>` · pipeline commit: `<40-char>` · started: `YYYY-MM-DDTHH:MMZ`

---

## What was sent (step 2)

| field | value |
|---|---|
| premise sha256 | `<from RUNPLAN.csv, checked by preflight.py>` |
| premise, first line | `<verbatim>` |
| foundation logline | `<what the pipeline rewrote it into — §4, the validity check>` |
| genre / length / band | `<from the plan row>` |
| contract + ledger digests | `<from ductus.py contract, step 3>` |

## Rows

One line per action, in order.

| ts | phase | kind | what happened | option taken | counted |
|---|---|---|---|---|---|
| | | | | | |

`kind` is one of exactly four:

| kind | meaning | counted |
|---|---|---|
| `transcribe` | verbatim from the premise or the plan row | **no** |
| `gate` | a decision among options, including accepting the default | **yes**, one per answer |
| `approve` | a ductus / voice / cast candidate accepted without editing its text | **yes** |
| `prose` | should never appear — see below | — |

`--interventions` is the number of `yes` rows. A gate **firing** is not an intervention: it
is the pipeline working, and it is recorded as a `--deviation` if it forced a rewrite. The
operator's answer to it is the intervention, if there was one. Zero is a legitimate count; an
unrecorded three is not.

## If you are about to do one of these, stop the book instead

Writing, rewriting, selecting between or extending prose · editing the pipeline's output for
any reason, including "it ends mid-word" · switching a gate off or lowering a threshold or
editing a threshold's input · hand-merging two drafts or splicing a repaired chapter · editing
`PROJECT_STATE.yaml` plan numbers so C1 agrees after the draft diverged.

A `prose` row means the book is a stop condition and its row is not filed.

## End of book

```
interventions (rows with counted=yes):  <N>
deviations filed:                       <N — gate firings that forced a rewrite, band, parts>
word count / chapters / band:           <from manifest.py --check>
```
