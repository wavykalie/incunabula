# KNOWN FINDINGS — findings the author has declined to fix

**Created:** 2026-09-28, by ruling, after a debate in which the same conclusion arrived
from two directions: Agent B (refusing a general framework) and the author's own
frustration with sessions that end in a list of problems instead of a finished book.

## What this file is for

A defect, from here on, means exactly one of two things:

1. a gate that fails, or
2. a contradiction between two files in `CANON_LEDGER.yaml` / `ENTITY_STATE.yaml`.

That is the whole definition. Anything that is neither is an **observation**, and an
observation that the author has seen and not acted on is **closed**. It goes here, in one
line, and it does not come back.

This file exists because the loop was self-feeding. A gate produced a finding; the
finding was read; the finding was not fixed; the next session re-ran the gate; the gate
produced the same finding again. The second report of a thing already reported is
indistinguishable from news, and that indistinguishability is what made the loop feel
endless. **The fix is not fewer gates. It is a place to put the answer "we know."**

## The closed list

| id | finding | gate | closed because | reopened if |
|---|---|---|---|---|
| KF-001 | `Okafor` appears as a surname in both `the-origin-point` and `Hollow Bridge` | `check-names.py` | Shared surnames are frequently deliberate; both are minor roles with different given names and different books' casts. The author has been told and has not ruled it a defect. | the author rules, or a *given* name collides rather than a surname |
| KF-002 | `Cora` is Nameberry tier-B (rank 28) | `check-names.py` | Tier B is WARN by design, not FAIL. `Cora` is correct for a woman born 1951 in a rural American county. The row is working as intended. | a Tier-A name appears |
| KF-003 | A18 flagged a genuine non-gerund as a gerund litany in `chapter-21.md` | `deslop-check.sh` | False positive with a real cause. The prose was rewritten to be unambiguous rather than the gate being argued with. Frozen gates do not accommodate one author's rhythm. | the same false positive appears in three different books |
| KF-007 | `The Trick` U1 reads CV 22.8% (warn band 22–28%) at 34 of 34 chapters | `check-uniformity.py` | Drafted under `DRAFTING_FRAMEWORK.md`, which forbids editing a manuscript to satisfy U1 twice and records that the row cannot tell genuine chapter-length variety from a plan with two buckets. Chapters are as long as their things take. Closed at the full sweep 2026-10-01. | a measure of genuine chapter-length variety exists and this book fails it |
| KF-008 | `The Trick` U6 reads the antithesis frame in 11/34 chapters (32%), above the 30% warn line | `check-uniformity.py` | 17 of the 18 instances are spoken. The one narrator's-desk instance (ch 34) was rewritten at the sweep and the row re-run. Spoken formulas are voice (COMMONPLACE 2026-09-30) and the gate cannot tell the speakers apart; the reader has to. | the frame-share crosses the 40% fail line, or a character hammers the formula (then it counts as narrative) |

## What does NOT go in this file

- **A gate that fails.** A failure is a finding with a decision pending. Fix it or
  escalate it, but do not close it — a failing gate closed silently is a broken freeze.
- **A ledger contradiction.** Same. These are factual conflicts and one of the two is
  wrong.
- **Anything the author has not seen.** This file is written *after* the author is told.
  Pre-emptively closing something unseen is how a finding gets lost.

## How a finding is closed

1. The gate reports it.
2. The author is shown the report, verbatim, with the file and line.
3. The author either fixes it, or says no.
4. If no, it is written here with the reason, and the gate is **not** changed to
   suppress it. Suppressing it would make the manifest dishonest; the row stays in the
   freeze and keeps firing, and the answer to it now lives in a table instead of in the
   reader's memory.

That last point is the design. **The gate keeps firing.** A frozen instrument is not
edited to make a book look better — that is the whole argument of `GATE_FREEZE.md`. What
changes is that the author reads the same finding a second time, sees it listed as
already declined, and moves on. One line, closed, permanently. The loop is broken by
*recognition*, not by suppression.

## Reading order for a new session

    1. this file            — what is already known and closed
    2. GATE_FREEZE.md       — what the instrument is, and is it still frozen
    3. the book             — go to work

A finding that appears in this file is not a finding. It is a line item with a decision
attached, and the decision was already made.

---

## Added 2026-09-28 — a gate that did not run, recorded as a pass

**KF-004 is NOT closed, and is recorded here to be explicit about that.** The finding below
was found, fixed, and closed inside one session, so it is in this file only as a note that
the category exists and was used correctly.

`check-length.py` reads `target_floor_words` / `target_ceiling_words`. A book declared
`declared_floor` / `declared_target`. The gate did not run, exited 2, and printed
`NOT RUN, and not a pass` — **and the book's own state file listed the row under `gates:`
as a pass.** The gate said the right thing. The report did not.

This is the same shape as every entry in this file and the reason the definition of a
defect at the top is a *definition*: a finding that is re-reported as news is a measurement
nobody read. The instrument was honest. What failed was a person reading an exit code as a
verdict.

**The rule this produces, now standing:** *a gate that exits 0 and a gate that ran are
different claims, and exit 2 exists to tell them apart.* Any row in a report that has not
been seen running in this session is not a result.

## Added 2026-09-28 — the gate was not reading the files (closed under Freeze 7)

Two defects in `deslop-check.sh`, both found by running the gate on a book it had never
been run on. Neither was found by a control failing, because both sat *under* the caps.
Full record and the regression table are in `GATE_FREEZE.md`, Freeze 7. Summarised here
because the shape is the point.

**KF-005 (closed).** The sentence tokenizer splits on `[.!?] ` — punctuation followed by a
**space**. Fifteen of Merope's twenty-two chapters carried `\r\r\n`, and the stray CR sits
exactly where that space belongs, so the split never happened. The awk counted 22
sentences in a chapter that has 43, and P1's share was computed against half the text it
claimed to cover. Two chapters read `ok` and read `FAIL` once normalised. They were not
passing; they were evading.

**KF-006 (closed).** A25 had no word boundary after `not`, so `was NOTHING in it worth the
walk. It was ...` matched — the pattern took `was not` and `hing in it worth the walk` as
the intervening clause. Read out one at a time, **24 of Merope's 25 hits are the real
construction and 1 is that accident.** Fixed with `\b`, which can only ever remove matches.

**The part that generalises past line endings and word boundaries.** Both fixes were found
only because the chapters were read. Neither control could see them: the slop fixture is
built to trip caps, not to notice that the tokenizer under-counts, and the human corpus is
commercial prose that is deliberately not shipped, so `validate-controls.sh` exits 2 and
the caps stay UNVERIFIED by that path. **A gate's controls test its thresholds. Nothing
tests whether it is reading the file.** Running a gate on a book it has never touched is
what surfaced both, and it cost two chapters of prose edits to find — against 22 chapters
and 30,000 words that were quietly passing the wrong way.

**And the third recurrence of the same shape, which is the one worth keeping.** A locator
written to find the offending lines disagreed with the gate on 22 of 22 chapters. Three
causes, all three bugs in the locator: it read files with Python's universal newlines, it
compared A25 as `n*1000 > 3*w` when that cap is `3/2000`, and it printed rows whose keys
could not match. Fixed, and it now agrees with the gate on all 22. Three times in a row
the instrument was right and the thing measuring it was wrong — the same lesson as the
clone test in `GATE_FREEZE.md` and the never-firing CR guard in Freeze 7, one layer down:
**a check that has never been seen to fail is not yet known to work.**

## Added 2026-09-28 — the deletion layer disarms gates silently (OPEN, by decision)

**This one is not closed, because the fix chosen was to leave it open and make it visible.**
Both Merope books are ungoverned by the `L1` row on purpose. What follows is why that is a
decision rather than an accident, and what it would take to close.

**The finding.** Archiving is governed by a real, well-written policy in
`skills/incunabula-codex/references/maintenance-protocol.md`: never delete a canonical
source, archive only once no active phase still reads it, mark redundant before archiving,
keep the original path / archive path / reason / replacement in the ledger. That policy was
followed exactly. `validation-series/book-{1,2}/PROJECT_STATE.yaml` was superseded, so it
went to `_archive/validation-series-meta/`.

**The gap.** It went *out of the book's own directory and into a different top-level
project*. No gate can see it from there. `check-length.py` had one code path for both
"no state file" and "state file with no target declared," printed one sentence for both,
and exited 2 — so the archive was invisible, and the exit code said something reassuring
and untrue. **The policy governs files. It does not govern the gates' view of where those
files live**, and nothing in it says a gate may still be reading that path.

The cost was paid in the same session that wrote the policy's own lesson down: an exit 2
was read aloud as evidence that `DRAFTING_FRAMEWORK.md` had removed the books' length
targets. It had removed nothing. The targets were in the archive, still carrying
`average_words_per_chapter_planned: 2450` and `chapter_count_planned: 7` — against books
that have eleven chapters.

**What is fixed.** `check-length.py` now exits 3, UNGOVERNED, for a missing state file,
distinct from exit 2, NOT APPLICABLE, for a declared absence. Under Freeze 8. The condition
is no longer silent; it says its own name.

**What is still open, and belongs to the maintenance protocol rather than to a gate:**

1. Nothing requires that archiving a file leaves the gates that read it still able to read
   it. The rule should be: *a file may be archived out of a book's directory only if no
   gate in `GATE_FREEZE.md` reads that path.* If it must move, the archive location is
   still the book root, or a stub is left behind.
2. `maintenance/PRUNING_LOG.md` exists in 2 of 9 live projects (`the-origin-point`,
   `incunabula-test`). `demo-magician` has `SWEEP.md` and `FULL_SWEEP.md` but no pruning
   log. A policy that is kept in a minority of the places it governs is not being applied.
3. `_archive/` holds 587 files / 68 MB, so archiving demonstrably happens. The problem was
   never volume. It was that **archiving looked finished** — files were moved, the folder
   looked tidy, and nothing reported that a gate had gone blind.

**The general form.** Every entry in this file is one sentence: the instrument was honest
and something read it wrong. This is the first one where the *storage layer* created the
wrong reading rather than a reader doing it. Deletion is not neutral — removing a file
changes what the gates can see, and that change is silent unless something is built to
notice it. Freeze 8 is that something, for one row and one book family; the protocol gap is
still open for every row that reads a file an archive could take away.

### Escalation, 2026-09-28 — this stopped being near-miss — **and I first overstated it**

Asked to act on the gap above, the first question was no longer *which row went blind* but
*how much has already gone missing*. The answer was one manuscript.

`validation-series` was re-chaptered 7 → 11, and the rewrite **overwrote the seven chapter
files in place**. The v1 metadata was archived correctly. The v1 **manuscript** was not
archived at all, and no gate reported anything, because the gates read the *current*
manuscript and that one was complete. The seven chapters survived only inside the three v1
EPUBs in `epubs/` — a build artefact no index pointed at.

So the freeze held at 15/15 the entire time a book version was being quietly erased. The
freeze guarantees the *instruments* are unmodified. It says nothing about whether the thing
measured is still there. **A frozen gate over missing inputs passes.**

Recovered 2026-09-28 by extracting the chapter XHTML back out of the v1 EPUBs, then proving
it: rebuild with the archived v1 `build-epub.py` and diff against the original — **all 14
chapter files byte-identical**, the only differences being a `dcterms:modified` timestamp and
a title-page note the archived script no longer emits. Recorded CVs came back at 5.7% and
10.8% against the 5.8% and 10.8% written down in `incunabula-test/RUN_REPORT.md` before the
rewrite happened.

What made this survivable was luck with a cause: the v1 EPUBs were still sitting in `epubs/`
under their v1 names. **The rewrite was not a deletion**, and treating a re-chapter as an
in-place edit is what put the old text out of reach of everything the protocol governs.

This sharpens item 1 above into something that is not a gate question at all:

> **A rewrite that re-chapters a book must archive the manuscript it replaces, in the book,
> before it writes the new one.** Not the metadata. The manuscript.

It is in `skills/rewrite/SKILL.md` step 8 as a rebuild-and-read-back step, but that step was
written to catch *stale artifacts* and did not anticipate *absent sources*. The archive rule
belongs in `maintenance-protocol.md` beside the pruning rules, since that is where
"never delete a canonical source" already lives — and this time the deletion was not a deletion.

## Added 2026-09-28 — the calibration gate reported absent, and 449 documents were installed (closed under Freeze 9)

**Same defect class as KF-004 and Freeze 8, in the one gate whose job is to certify the others.**

`validate-controls.sh` had answered `NOT VALIDATED — no calibration corpus installed` and exited 2,
which was reported for a long time as *"the calibration corpus is commercial prose, deliberately not
shipped."* That was true of the **repository** and false of the **machine**. Three corpora were
installed on this machine — 449 documents of published fiction and non-fiction — and the script was
looking for a fourth name, `corpus/elaina`, that has never existed in any clone.

The corpus is untracked by design (`calibration/.gitignore` excludes it; the reasoning is written
down and is the same as for `USER_PREFERENCES.md`). So "not in the repo" and "not on the machine"
are both true, and the message could only report the first.

**What it cost.** Every threshold in `deslop-check.sh`, `check-uniformity.py` and `check-drift.py`
was labelled UNVERIFIED — including on every book result in this file. The thresholds were almost
certainly fine; they had been re-derived from the same published corpus. But "almost certainly"
is a claim about a gate that never ran, which is precisely the claim this project exists to stop
making. It was carried as a standing caveat across several sessions and one commit.

**Verified, not assumed.** Pointing the script at what was installed:

    HUMAN_CORPUS=.../corpus/montgomery VOLUME_CORPUS=.../corpus/multivolume \
      bash validate-controls.sh

→ `ALL CONTROLS PASS`, **exit 0**, 10 of 11 controls green, fiction and non-fiction.
**No cap moved.** Control 3 (AI discrimination) still `skip`s with no control installed, and is
reported as a skip rather than folded into the pass.

**The fix is a message, not a threshold.** When the configured corpus is missing but
`calibration/corpus/` is not, the script now lists what it found and prints the command that runs
the suite. Not-gone and not-pointed-at are different sentences now.

**The general form, stated once more because it keeps recurring:** the recurring failure in this
project is not a gate being wrong. It is a gate being *unable to distinguish two states*, and a
reader — including me — filling the gap with the more convenient story. That has now happened
four times: a state file under a key the gate does not read (KF-004), CR invisible to grep
(KF-005), a missing file reported as a declared absence (Freeze 8), and a corpus present
reported as a corpus absent (Freeze 9). The first two were closed by fixing the detector. The
second two were closed by making the gate name its own state. The second kind is the cheaper one
and it is the one to reach for first.

### Correction, 2026-09-28 — the prose was not erased, and the escalation above said it was

The escalation immediately above calls this "a book version being quietly erased" and the
headline calls it "how much has already gone missing". **Both overstate it, and the record has to
say so.**

Checked against the second re-chaptered book, `incunabula-test`, which went 11 → 15 chapters the
same way. The old chapter 1 was *The Book Burner*. It is now chapter 2, *The Book Burn*, and the
sentence the pre-re-chaptering evaluation quotes as its evidence — *"he was driven home behind a
load of fish"* — is still there, in the current chapter 2. The old chapter 1's text was **split
across the new chapters 1 and 2, not replaced.**

So the accurate statement is:

- **The prose survived.** Redistributed into a new chapter division. Merope lost about 119 words
  across fourteen chapters; `incunabula-test` lost none that I could find.
- **The old chapter division is gone.** That is the real loss — the before-state, the 5.7% CV
  version, the thing the framework was written against. It is evidence, and evidence is what
  actually got destroyed.
- **The safety net was naming luck both times.** Merope's v1 survived in `epubs/`; had those not
  been built under their v1 names, the before-state would be unrecoverable. `incunabula-test` has
  no such copy, and its 11-chapter division is gone for good. One out of two is a coin flip, and a
  coin flip is not a policy.

This makes the finding *smaller and more precise*, not weaker. The claim `DRAFTING_FRAMEWORK.md`
rests on is the CV change from 5.7% to 41% — and that claim is only checkable **because** the
before-state was recovered. Had the epub not been sitting there, the headline number would be an
assertion made after the fact by the same process that produced it. The recovery is what turned
"we fixed the variance" into a measurement.

`maintenance-protocol.md` §7a stands, with the reason restated correctly: archive the manuscript a
rewrite replaces **because the before-state is the evidence**, and because the current habit is to
discard it and keep only the after.

The general failure is the one already named at the top of this file, and this is the fifth
instance: the instrument was honest, and I filled the gap with the more dramatic story. Two of my
own sentences in the escalation were wrong before the day was out.
