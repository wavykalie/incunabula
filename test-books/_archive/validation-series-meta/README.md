# validation-series

A two-book sequential short-novel series, run through the **Book Genesis V4** workflow.

**The purpose of this project is not the books. It is the workflow.** This run exists to answer one
question: *does the persistent layer — canon ledger, voice contracts, maintenance protocol, provenance
— actually work?* The stories are the instrument.

---

## The deliverable

**`book-1/dist/merope-book-one_WORKING-TITLE.epub`** — EPUB 3, 7 chapters, 15,531 words.
**`book-2/dist/merope-book-two_WORKING-TITLE.epub`** — EPUB 3, 7 chapters, 15,148 words.

Both built with the Python standard library only (`book-1/tools/build-epub.py`, `book-2/tools/build-epub.py`).
Both verified: 14 entries, `mimetype` first and stored, `nav.xhtml` + `toc.ncx`, zip integrity OK.

> **Working titles.** The series name, both book titles and every chapter title are **deferred by the
> author** and were not invented for either build. Neither EPUB carries a `dc:creator` rather than a
> made-up one, and both label their chapter headings as provisional.

**Read them / send them:** open the files above, or run `python tools/build-epub.py` from `book-1/` or
`book-2/` to rebuild.

---

## The verdict

**`book-2/continuity/resume-test.md`** — the seven success criteria of the original run brief, each with
evidence. If you read one file from the early phases, read that one.

| # | Criterion | Verdict |
|---|---|---|
| 1 | A fresh session resumes correctly | **cold load: yes · cold session: STILL NOT ESTABLISHED** |
| 2 | Book 2 recognises the same character IDs and voices | yes |
| 3 | Legitimate sequel changes become scoped facts | yes — and both were **consumed**, with their content decided by the author |
| 4 | Contradictions stay visible and unresolved until approved | yes — and it caught one **the layer itself had created** |
| 5 | `PRUNING_LOG.md` records maintenance decisions | yes — 6 entries, none of them deletions |
| 6 | V4 phases reported, not the compact pipeline | yes — Phases 0–7, each with a file on disk |
| 7 | Files, not chat claims, prove each phase | yes — including a ZIP structure check and parser exit codes re-runnable by anyone |

### The two findings that matter

**1 · The layer promoted its own inference to canon, and only the author caught it.**
→ `book-2/continuity/provenance-audit.md` · `book-2/CANON_LEDGER.yaml → conflicts.CONF-011`

Book 1's ending leaves the acknowledgement unsaid. That is manuscript fact. The layer then turned that
**ending** into a **Book 2 rule** — *"it is NOT reciprocation stated on the page"* — and recorded the rule
on a fact whose `authority` field said `user_decision`. Nothing distinguished the inference from the
author's own words, and the three relationship-delta options offered to the author were all built to obey
it, which is why the author recognised none of them:

> *"I didn't really say nothing said, that was a rule once again the AI Added for some reason."*

It was struck, both values were preserved, and the correction was pushed into the foundation, the voice
contract and the chapter beats. **It is the second instance of its class** — compare `CONF-007` in Book 1.
The generalisable statement is in the audit file: *the layer can say where a fact came from, but not which
sentence inside a fact came from where.*

**2 · Phase 5.6 found a CRITICAL defect in prose that had already passed the prose gate.**
→ `book-2/continuity/manuscript-audit.md`

Phase 5.6 (manuscript continuity) **had never been run when Book 1 shipped**, and running it then found two
CRITICALs in chapters the scanner had passed 7/7. For Book 2 it ran **before** delivery, and it found
`CONT-201`: **a character who leaves in ch.4 was still present in ch.5 and ch.7.** The prose gate checks
sentence shape, adverb density, anaphora and negative litany. It cannot check whether a character is in the
room. Nothing else in the pipeline can either.

---

## What exists

```
CANON_LEDGER.yaml              series scope: stable entity IDs, series rules, both books' scoped changes
README.md                      this file
DOC_POLICY.md                  the document registry policy and the reconciliation loop
                               the checks in tools/ enforce
tools/                         check-docs.py   run-checks.sh   <- the doc gate; run from HERE
                               check-structure-drift.sh   check-stale-status.sh
                               deslop-check.sh   validate-controls.sh   calibration/

book-1/                        COMPLETE - 15,531 words, all gates passed, scored 7.7, EPUB built
book-2/                        COMPLETE - 15,148 words, prose 7/7 PASS, scored 7.5, EPUB built
  INTAKE.md ASSUMPTIONS.md RUN_REPORT.md PROJECT_STATE.yaml
  CANON_LEDGER.yaml ENTITY_STATE.yaml
  foundation.md outline.md
  manuscript/chapters/ (7)
  continuity/                resume-test.md  provenance-audit.md
                             outline-audit.md  manuscript-audit.md  adversarial-audit.md
  artifacts/                 01-market-map  06-scorecard  07-editorial-package
                             engine-samples.md  location-and-delta-options.md   (both superseded, both kept)
  maintenance/               SESSION_LOG.md (7)  PRUNING_LOG.md (8)
  tools/                     build-epub.py
  dist/                      merope-book-two_WORKING-TITLE.epub
```

---

## Document reconciliation is part of the process

The layer is only worth anything if a later session can trust it, so **reconciling stale documents is
a step in the run, not a cleanup after it.** It runs with the other checks at every phase gate and at
run close:

| Check | Guards |
|---|---|
| `tools/deslop-check.sh` | the prose, calibrated against published prose |
| `tools/validate-controls.sh` | the prose gate's own calibration |
| `tools/check-structure-drift.sh` | the structural ledger agreeing between `foundation.md` and `outline.md` |
| `tools/check-stale-status.sh` | a state/planning file asserting the work is unfinished while its own fields say it is done |
| `tools/check-docs.py` | the registry: a registered file that is missing, an unregistered file, a supersession or archive inconsistency, a dead file reference, a duplicate record |

`tools/run-checks.sh` runs all of them and returns one combined status. The policy they enforce — what
must be registered, how a superseded document is disposed of, and the five-step reconciliation loop — is
written down in **`DOC_POLICY.md`**.

Dated records — `maintenance/SESSION_LOG.md`, `PRUNING_LOG.md`, `continuity/*.md`, `artifacts/*` — are
**exempt by design**: they hold past and present together because they are logs. Reconciliation corrects
or clearly historicises the stale prose and logs the change, keeping the superseded wording in
`PRUNING_LOG.md` rather than erasing it. Both books were delivered with stale status prose that no gate
caught; that is the failure this step exists to close.

---

## What the author decided, and what is still theirs

**Decided for Book 2** (each recorded with `authority: user_decision`, each from written options offered
without a recommendation):

| Decision | Value | Date |
|---|---|---|
| The engine | **Engine A, "the work"** — everyone is needed, constantly; usefulness never ends | 2026-09-23 |
| The location | **"The unfinished thing"** — one enormous work, no finish, everyone load-bearing | 2026-09-23 |
| The population | **Something new** — not Book 1's beings, not ordinary humans | 2026-09-24 |
| The interval | **Not load-bearing** — not dated, not leaned on | 2026-09-24 |
| The relationship delta | **Merope notices, and tests Achird in subtle ways** | 2026-09-24 |

**Still the author's — nothing here blocks anything, because the drafting is done:**

1. **Sign-off on the population's mechanics** (`R-013`–`R-021`). The author chose the *category*; the
   concrete design is the pipeline's and is marked `proposed` rather than `active`, deliberately.
2. **The instructed hair-styling change** (given 2026-09-23, never specified). Appearance is author-decided
   series canon, so it was raised rather than invented. The prose describes neither lead physically, as in
   Book 1, so this blocks a figure cover only.
3. **Whether ch.7 should say more.** `CONF-011` struck the prohibition on directness, but the drafted
   chapter still resolves on two words — *"I know."* That may be exactly right, and it is
   indistinguishable from obeying the rule that was struck. Raised, not fixed.
4. **Every title**, and the comps — for both books. No comp has ever been approved.
5. **Phase 5 (the literary barrier loop) has never been activated, for either book**, because its
   activation condition — a quality target set by the author — has never been met. If one is ever set,
   point it at Book 1's **structure** and Book 2's **pacing**.

---

## The honest caveat

This validation was performed by the same agent that built the thing being validated, and **Book 2 was
drafted, audited and scored inside a single context.** The scoring is the least independent evidence in the
project and the scorecard says so itself. The contradiction probe is a self-test.

What *is* independent is the evidence: file paths, grep counts, parser exit codes, ZIP structure checks,
word counts that reconcile to the digit. Those can be re-checked by anyone with a terminal. The judgements
cannot, and are labelled as judgements.

**The reader personas were inherited and never re-run for Book 2**, so its casual-reader verdict is
predicted rather than simulated. That is a gap, not a pass, and it is recorded as one.

The real test is still **one new session and one prompt**: the prompt is written out at the bottom of
`book-2/continuity/resume-test.md`, and it has still never been run by anyone who did not write the books.
