# Prose gate — measured thresholds and a required control run

**Required. It cannot be skipped, and it cannot be deferred by a phase that is otherwise
satisfied.** No chapter, manuscript, or package advances while this gate is failing.

The gate has two halves and both must hold: thresholds measured from published prose, and
a control run proving the scanner still discriminates.

Read the project's calibration record before changing a cap or quoting a number from this
file. The record holds the corpus, the method, the raw measurements, and the command that
re-derives them. A project without one has unverified caps and should build one before
treating this gate as calibrated.

## 1. Where it applies

Manuscript prose only. Planning and engineering documents — outlines, scene packets,
foundation, state files — are exempt, because they need precision and sit above the prose
caps by design. State the exemptions when reporting, so an exempt file failing the scan is
not read as a defect.

| Phase | Requirement |
|---|---|
| Drafting | Each chapter is scanned once written. A chapter that fails is not accepted into the manuscript however well it reads. No line-level anti-slop work during drafting; the scan belongs here, at the boundary. |
| Devil's audit | The scan result is an input, not a substitute. The audit cannot clear a chapter the scanner rejects, and must not treat a pass as evidence the prose is good. |
| Final score | The gate must be green on every chapter before a score is reported, with the control run recorded beside it. |
| Colophon | No package is produced from a manuscript with a failing scan. Packaging a failing manuscript is the exact failure this gate exists to prevent. |

It does not replace the tic scan, the evaluator, or the read-aloud pass. It is the
mechanical floor beneath all of them.

## 2. Two tiers, and the corpus decides

Do not promote a phrase to zero-tolerance because it looks like slop. Promote it only if
published prose never does it.

- **Hard (zero tolerance)** — zero occurrences in the calibration corpus, so any occurrence is a tell.
- **Density (capped)** — published prose does this, so it can only be overdone, never banned. The cap sits above the worst single document in the corpus, so the reference passes with headroom rather than squeaking through.
- **Pattern (algorithmic)** — checks grep cannot do, such as anaphora abuse, duplicated sentences, and runs of short fragments.
- **Note (reported only)** — too noisy to judge mechanically; counted, never failed. Curly quotation marks belong here, since typeset books use them.

An earlier version of this ruleset banned words such as *quietly*, *deeply*, *landscape*,
*realm*, and *in order to*, along with every em-dash appositive. All of them appear in
published prose many times over. Those bans were indefensible and are gone.

## 3. The caps

Print the live table with the scanner's caps flag. Defaults, derived from a 175,144-word
light-novel narrative corpus:

| id | rule | allowance |
|---|---|---|
| A1b | leverage / harness | 1 per 2,000 words |
| A2b | manner adverbs | 2 per 1,000 |
| A3b | literal nouns | 7 per 1,000 |
| A4 | serves-as dodge | 1 per 2,000 |
| A5 | negative parallelism | 2 per 1,000 |
| A6 | *Not X. Not Y.* | 2 per 1,000 |
| A7 | the X? a Y | 1 per 2,000 |
| A9 | teacher voice | 1 per 2,000 |
| A10b | forum filler | 2 per 1,000 |
| A11b | soft conclusion | 1 per 2,000 |
| A15b | participial -ing | 3 per 1,000 |
| A17 | invented label | 1 per 2,000 |
| A23 | parenthetical dash | 3 per 1,000 |
| D1 | em dash | 10 per 1,000 (warn above 7) |
| D2 | rule of three | 5 per 1,000 (warn above 4) |
| D3 | -ly adverbs | 26 per 1,000 (warn above 20) |
| P1 | repeated sentence opener | fail above 6 per 1,000, or above 15% of sentences |
| P2 | duplicate sentences | fail above 1 per 2,000 |
| P3 | consecutive short sentences | fail at a run of 7 or more |

Warnings are not defects. They flag prose above the reference median, which is information
for the reader rather than a failure.

Two details, both of which were bugs once and are worth keeping:

- **Caps are rationals, not integers per thousand.** Integer per-thousand arithmetic truncated, which silently disabled every cap below one per thousand: a single hit in a 2,500-word chapter evaluated to zero.
- **A name on the page is not a defect.** Constellation names, invented terminology, and world vocabulary are the book's material. The gate targets tropes, not invention.

## 4. The control run is part of the gate

Before trusting any scan result in a report, run the controls. The runner exits nonzero if
any control is not what it claims:

| # | Control | Kind | Must be |
|---|---|---|---|
| 1 | published human prose corpus | negative | zero failing rows |
| 2 | synthetic slop fixture | positive | fails, with failing rows |
| 3 | machine-written published chapters | discrimination | some fail, some pass |

Control 3 matters most. A scanner that fails the machine-written book and passes the
human-written one is calibrated. One that fails everything is a blanket rule; one that
passes everything is decoration.

**An empty scan is a failure, not a pass.** This is not hypothetical: directory mode once
matched only one extension, so the corpus control, written in another, expanded to zero
files, ran no checks, left the failure flag at zero, and printed a pass. The clean result
that day was that vacuous pass. Both the scanner and the control runner now treat a
zero-file expansion as a failure.

**A check that cannot fail is not a check.** One rule once printed the wrong field in its
comparison, so the comparison was always an error and an error is false: it reported
success on every document and was never once seen to fail. When a check is added, prove it
can fail before trusting it to pass. Both of these failures ran in the permissive
direction, which is the direction that costs.

## 5. Recording

A gate that claims to have passed leaves evidence, not a claim: the exact command and its
exit status; documents scanned and failing rows with their identifiers; which files were
excluded and why; the control run result including control 3 or the reason it was skipped;
and, where a cap changed, the re-measurement that justified it and the corpus it came from.
Never report the gate as passing on the strength of a scan that never ran.

## 6. What it cannot see

Passing is necessary and never sufficient.

- It cannot see voice, rhythm, a dead metaphor, or one argument restated ten ways. Clean and voiceless is still slop.
- These caps are tuned to a narrative light-novel register. Fiction of other kinds, nonfiction, or a different pace needs its own derivation from its own corpus — re-derive rather than assume, and record the new corpus.
- It is a floor, not a style. A manuscript can sit inside every cap and still be dull, so the read-aloud pass stays in force.
- One rule is a canon guard rather than a slop rule: it fires on anything resembling an excluded book's engine. Treat a hit as a flag for a human, not a verdict.
