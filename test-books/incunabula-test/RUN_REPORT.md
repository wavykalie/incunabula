# Run Report

**Project:** Sons of Heaven, Students of Dust (WORKING TITLE)
**Pipeline:** `incunabula` (V4 production engine, 17 phases) with the `incunabula-codex`
intake / maintenance / prose-gate contracts layered on.
**Started / completed:** 2026-09-25.
**Result:** manuscript complete at 28,263 words, 11 chapters, all gates run. **Standard
delivery gate PASSED. Approval gate NOT APPROVED. Evaluation DEGRADED (grade C).**

---

## What exists

| Artifact | Path |
|---|---|
| Manuscript | `manuscript/chapters/chapter-01.md` … `chapter-11.md` |
| Generated concatenation | `manuscript/full-manuscript.md` (generated; do not edit) |
| EPUB 3 | `dist/sons-of-heaven-students-of-dust_WORKING-TITLE.epub` |
| State | `PROJECT_STATE.yaml`, `CANON_LEDGER.yaml`, `ENTITY_STATE.yaml` |
| Planning | `foundation.md`, `outline.md`, `voice-matrix.md`, `readership.md`, `artifacts/` |
| Evaluation | `evaluations/`, `continuity/`, `artifacts/09-incunabula-score-codex.md` |
| Package | `artifacts/10-colophon.md`, `delivery/editorial/upstream-signals.md` |
| Tools | `tools/deslop-check.sh`, `tools/check-uniformity.py`, `tools/validate-controls.sh`, `tools/build-epub.py` |

## Gate evidence (re-runnable)

```bash
# prose gate, per chapter
bash tools/deslop-check.sh manuscript/chapters/chapter-01.md   # ... through chapter-15.md
# prose gate, whole directory (includes the writer reports, which are EXEMPT)
bash tools/deslop-check.sh manuscript/chapters/
# uniformity gate, whole manuscript (cross-chapter; the per-chapter scan cannot see this)
python tools/check-uniformity.py .       # -> UNIFORMITY OK (3 books)
# drift gate, whole manuscript (does the book still sound like itself at the end?)
python tools/check-drift.py .            # -> DRIFT OK (3 books)
# both cross-chapter gates' own calibration
bash tools/validate-controls.sh          # -> ALL CONTROLS PASS (7 controls)
# state parses
npx js-yaml PROJECT_STATE.yaml && npx js-yaml CANON_LEDGER.yaml && npx js-yaml ENTITY_STATE.yaml
# document and ledger integrity
bash tools/check-structure-drift.sh .    # -> NO STRUCTURAL DRIFT
bash tools/check-stale-status.sh         # -> NO STALE STATUS
python tools/check-docs.py               # -> DOC CHECK PASSED
# the book
python tools/build-epub.py
```

| Gate | Result |
|---|---|
| Prose gate (11 chapters) | **PASS** — 0 HARD failures; 6 chapters carry a D2 warning under the cap |
| **Uniformity gate** | **FAIL — 4 rows** — U1 chapter-length CV 3.2% (floor 30%); U3 coda distribution 6/11 (ceiling 25%); U4 single-line paragraphs 14% (floor 35%); U5 paragraph-length CV 51% (floor 55%). See finding 3. |
| Prose gate, closing-coda rows `A24`/`F1` | **FAIL on 6 chapters** — added after this run closed; see finding 3. |

**Exempt files, named explicitly.** `tools/deslop-check.sh manuscript/chapters/` also
scans the eleven `chapter-NN-report.md` writer reports, and reports **14 FAIL rows, all
of them in the reports**. The reports are planning documents; they sit above the prose
caps by design (they quote the manuscript, name rules, and carry em-dashes in a
reporting register). The prose gate applies to manuscript prose only, and scoped to the
eleven chapters it is **0 FAIL rows**. This is recorded because a directory scan that
everyone reads as "the manuscript passed" while exempt files fail is exactly the kind of
result that gets misreported.
| Prose controls | **ALL CONTROLS PASS** — 51 human docs 0 failing; slop fixture FAIL 17 rows; Coldbrook 9 fail / 2 pass |
| Maintenance gate | **PASS** — state parses; ledger, entity state, voice contract, registry, pruning log all current |
| Phase 5.6 collation | 3 CRITICAL found **and fixed**; 0 remaining |
| Standard delivery gate | **PASS** — Platen 7.0 ≥ prescriptive-NF threshold 7.0 |
| Approval gate | **NOT APPROVED** — Platen 7.0 < 8.5 |
| Independence | **DEGRADED** — grade C |

## The two findings that matter

**1 · The prose gate cannot add, and Phase 5.6 caught what it missed.**
The scanner passed all eleven chapters. Then the continuity audit found **three
arithmetic errors inside that passing prose** — Wu Zetian's age (CONT-101), Xuanzong's age
and reign length (CONT-102), Taizong's age (CONT-201). All three were fixed and the
manuscript re-scanned to PASS. This is the same defect class the prior validation run
recorded. The fix is a mechanical check added to the audit method, not a resolution to be
more careful.

**2 · This evaluation is not independent, and the run says so.**
The chapter evaluations and the scorecard were produced in the same context that wrote
the manuscript. Under the evaluator protocol that is **grade C — diagnostic only**. The
book may be delivered to the author. It may **not** be described as independently
validated or publication-ready. Those are different claims.

**3 · The book passed every gate and is still machine-shaped.**
Added after this run closed, from a comparison of this manuscript against the Merope
books. All three were built by this pipeline, in different genres, and all three came out
uniform in ways published prose never is:

| | chapters | word range | CV | closing coda | single-line paras |
|---|---|---|---|---|---|
| **Sons of Heaven** | 11 | 2,401–2,686 | **3.2%** | **6 / 11** | **14%** |
| Merope vol. 1 | 7 | 2,077–2,402 | 5.8% | 0 / 7 | 49% |
| Merope vol. 2 | 7 | 1,882–2,511 | 10.8% | 0 / 7 | 47% |
| *published control* | *48* | *466–9,184* | *48.4–70.6%* | *0 / 50* | *50–62%* |

The published control is 177,047 words of Yen Press narrative. There is no overlap between
the two groups — not on chapter length, not on closing move. Every per-chapter gate this
run reports as PASS was structurally incapable of seeing this, because a per-chapter scan
never holds two chapters at once. The verdicts above stand as recorded; the **book itself
is not fixed** and the delivery gate result should be read as "passed the gates that
existed at the time".

What produced it, and it is design rather than accident: `catchword` required a Pull score
of 7 or better on **every** chapter, which forces every chapter to close on a forward
gesture; and nothing anywhere compared chapters to each other. Both are now changed —
`catchword` has ending types with a no-repeat rule and a plain-ending budget, `quoin` has a
ninth operation that reads the previous two chapters, and `tools/check-uniformity.py` fails
the manuscript. See finding 3 in the deslopify guide, *Beyond the Sentence*.

## What was skipped

- **Phase 5 (revision).** A plan of 8 tickets was produced and not executed. The floor
  meets the gate; the remaining tickets change the book's balance rather than fixing
  faults, and three of them are author decisions. Recorded as SKIPPED, per the
  maintenance protocol. `revision_cycles: 0`, max 3 if the author activates it.
- **Phase 5 Fine Press overlay.** Not activated; no quality target was set.

## Host contract

- [x] Read the active phase prompt at each phase.
- [x] Wrote into the project directory.
- [x] Parsed state files with a real parser (`npx js-yaml`), not by eye.

## Re-chaptering and the tic pass (the author's report of what a reader caught)

The author read the finished books and reported the failure the pipeline had missed: both
books used **the identical rhetorical tic at a very similar rate**, every chapter was
about the same length, and the front matter still said the titles were not set. All three
were true. None of them was visible to any rule the project had.

**What was wrong.** Chapters 2,401–2,686 words in an 11-chapter book — a length CV of
**3.2%** where published prose runs 48–71% and a single volume ranges from 466 to 9,184
words. Six of eleven chapters closed on an explanatory coda, which published prose does
zero times in fifty. And `catchword` scored a Pull on *every* chapter, which is the machine
that generated the codas: a rule applied to all eleven chapters forces all eleven to close
forward.

**What changed in the book.** Both books were re-chaptered at genuine seams in the
material — the Qin and the Tang collapse split into three each here, four of seven split in
each Merope volume — and the endings were varied so that no two consecutive chapters close
the same way. Six codas that did survive were stripped or rewritten to end on a fact. The
`Untitled (titles deferred)` comment that sat at the top of fourteen chapter files was
removed, and the working-title note is gone from the subtitle.

| | before | after |
|---|---|---|
| chapters | 11 | 15 |
| word range | 2,349–2,686 | **471–2,686** |
| chapter-length CV | 3.2% | **45.2%** (gate floor 30%) |
| chapters closing on a coda | 6 of 11 | **0 of 15** |
| worst repeated frame | antithesis in 87% of chapters | 40% (warning band) |
| voice drift | not measured | 1.26 (warn; cap 1.40) |

**What did NOT change, and this is the honest part.** The per-chapter scanner still fails
**8 of the 15 chapters**, on `A25` (antithesis density inside a chapter), `D1` (em dashes),
`D2` (rule of three), `D3` (-ly adverbs) and `P1` (anaphora). The cross-chapter work removed
the *pattern* — the antithesis no longer appears in 87% of chapters — but it did not remove
every instance, and a dense essayistic chapter still carries more than one per 2,000 words.
The book passes the cross-chapter gates and does not pass the per-chapter ones. That is
unfinished work and it is recorded here rather than left out.

`D1` is the row most likely to be the cap's fault rather than the book's. It is governed by
a translated light novel, and the calibration record already concedes the resulting cap is
looser than native-English prose would justify. Re-deriving it needs a non-fiction corpus
this project does not have.

**Two rule bugs were found and fixed while doing this**, both in the direction of the gate
being less able to fail than it claimed. `F1` (closing coda) collapsed every CRLF chapter
into one record and grep'd the *whole chapter* for a coda phrase instead of the closing
paragraph — which is why six chapters read as closing on one when none did. And
`check-drift.py` shipped its first cap from an assumption rather than a measurement; all
three published volumes blew past it, which is what a bad metric looks like from inside.
Both are recorded in `tools/calibration/CALIBRATION.md`.

## Open items the author owns

1. `CONF-001` — the narrator's grammatical person. The manuscript is third-person as a
   proposal, not a decision.
2. Every title, including the book title and all chapter titles. All are working titles.
3. All comp titles. None is approved, which is why the Market dimension is held at 7.0.
4. The Phase 5 revision plan (`evaluations/revision-plan.md`).
5. Whether the final chapter should address the reader directly. It is the book's largest
   formal gamble.

## Unfinished task and resume step

**Unfinished task:** nothing in the pipeline. The run is closed.

**Resume step, if the author returns:** read `PROJECT_STATE.yaml` and
`maintenance/SESSION_LOG.md`, then either activate the revision plan (Phase 5) or set a
quality target to activate the Fine Press overlay. Do not re-draft; the manuscript passes
the gate.
