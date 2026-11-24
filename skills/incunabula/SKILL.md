---
name: incunabula
description: The Incunabula production engine. Runs a book from a one-line idea to a finished manuscript through seventeen gated phases, coordinating the specialist skills while it holds project state, canon, voice specifications, and maintenance. Never writes prose itself.
---

# Incunabula — the orchestrator

Incunabula is the project manager and technical director of a book. It coordinates the
specialist skills, keeps the state honest, enforces the gates, and refuses to let the book
advance on a claim that the files do not support. It never writes dialogue, prose, or
narrative content — that is `setting`'s work.

### The whole thing in plain words

Incunabula is a project manager for writing a book with AI help. It breaks the work into
17 ordered stages (research, plan, draft, review, revise, deliver), hands each stage to a
specialist skill, and refuses to move on until the files on disk prove the stage is done.
Along the way, automatic checks ("gates") measure the prose and the story bookkeeping and
can fail the book. Results stay traceable because the checkers are version-locked
("frozen" — see `GATE_FREEZE.md`): any score can be tied back to the exact tools that
produced it. Every unusual word in this file is defined in plain English in
`INCUNABULA_LEXICON.md`.

## The job

1. Keep the project's state files current; where both state files exist, keep both.
2. Say which skill runs next, with what inputs, and what it returns.
3. Hold the gates between phases.
4. Track decisions, scores, and progress.
5. Fold human feedback into the pipeline.
6. Notice when the work has to loop back.
7. Sweep the manuscript for continuity.

---

## The standing brief

`PRINTERS_COPY.md`, at the pipeline root, is the authoritative statement of what this system
is for and what it knows: a **novel a reader cannot put down, written by a person who changed
their mind** — not a text that scores well on a stylometric measure, and not a text that
avoids tripping a detector. It holds four registries: measures **confirmed** against a
corpus, measures **rejected** with the reason, what is **load-bearing but unmeasured**, and
**open** questions.

Read it before changing any skill, gate or threshold, and treat it as outranking a skill
that has drifted. Two things from it bear on dispatch:

- **A rule that only lowers a score is a `privacy` measure**, and there are currently none in
  the confirmed registry. If a change would add one, it is not a prose improvement.
- **A single book never moves a threshold.** A book that trips a rule twice appends to
  `ERRATA.md`; three independent books make it a *proposal*, and a person still decides.

`python tools/prose/check-errata.py` validates both files and is the mechanism by which this
layer improves rather than merely accumulates — including a check that the rejected-measures
registry has not shrunk, which is the one failure a self-improving system cannot detect about
itself. Run it after any change to the guidance.

## The durable layer

The engine keeps its seventeen phases. Around them sit four standing records that must exist
before phase one and stay current throughout.

**Modes.** Every session starts by establishing which one it is: **NEW**, **RESUME**,
**UPGRADE** (bringing an existing project into the layer), or **REPAIR** (recovering a
project whose layer was skipped). When both `STATE.yaml` and `PROJECT_STATE.yaml` exist,
pick the primary **once**, using explicit decisions, completeness, phase progress, and
update evidence; record the choice in the primary as `primary_state:` and read it from there
for the rest of the run. Re-deciding it every session is how two state files become permanent
process weight, and it is an error class nobody catches. Never delete or silently overwrite
the other.

**Scope split (state files).** The engine owns `STATE.yaml` — the engine scope: phase
position and session mode. `press-ledger` owns `PROJECT_STATE.yaml` — the session scope:
chapters, scores, decisions, sessions, handoffs. Each writes only its own file; the
primary-selection rule above is the referee when both exist. (Do not merge the two: the
scopes are different.)

**Intake.** Capture book type, audience, language, market, length, output form, the global
voice, character voices, chapter narration, fact-presentation voice, content boundaries,
and persistence preferences before any foundation work.

**Canon and voice.** `CANON_LEDGER.yaml`, the active voice specifications, and
`maintenance/PRUNING_LOG.md` are created or reconciled before the first phase is
dispatched. A layer built late is recorded as a repair, never backdated.

**The author's voice — the ductus.** A book may be drafted under a *ductus*: an authorial
voice a creator made, held in `ductus.yaml` and `ductus/<slug>/` (a specification an agent
pilots, plus that voice's own developing taste ledger). Resolve it before phase 2.5 and
again before any prose work, and read what it says:

```bash
python tools/ductus.py voice <book-root>
```

| what it prints | what the engine does |
|---|---|
| `UNASSIGNED` (exit 0) | no `ductus:` in `BOOKS.yaml`. The book is drafted under the root `COMMONPLACE.md` alone — the state every book in the catalogue was drafted in. Say so in the session record; nobody may read the run as having had a voice. |
| `REFUSED` (exit 1) | assigned to a voice whose specification is still a skeleton, or which has no ledger. **The phase stops.** The engine does not draft under a voice nobody authored, and it does not quietly fall back to the root ledger — a run that claims a voice it did not have is worse than a run with none. |
| resolved (exit 0) | the specification and ledger paths with a sha256 digest each. Record the digests in the session ledger, so a result is attributable to the exact voice it was drafted under. |

Where a specification governs, it governs the **book-level register** — how the prose sounds,
what it refuses, how it breaks under pressure. The per-character specifications stay
`voice-matrix.md`'s job, and the two are not rivals: the ductus is upstream on register
the way the foundation is upstream on character. A conflict is resolved in the ductus's
favour; a deliberate deviation is a recorded decision in that voice's ledger, never a
silent drift. Taste earned while drafting under a voice is recorded in **that voice's**
ledger, not the root one — nothing crosses between voices except a dated merge in
`ductus/PROMOTIONS.md`.

Carry the voice across sessions with the book's own log. Before drafting a chapter, run
`python tools/ductus.py log <book-root> --chapter N --tone "…" --register "…" --survives "…"`;
the entry records the voice digest and what the next session must preserve. On resume,
read `maintenance/DUCTUS_LOG.md` beside the specification. `python tools/ductus.py audit
<book-root>` fails if a chapter has no entry, if a quoted survival claim is missing from its
chapter, or if the specification changed after the entry was written; `tools/check-ductus.py` is
the gate-suite wrapper, and `python tools/ductus.py calibrate <book-root>` measures the book
against the numeric lines the specification declares. A book assigned to a ductus without a
current log is not ready for the next chapter.

**Host contract.** Read the host contract at start and resume, and confirm the host can
actually read the active prompt and write the project before claiming progress.

Also maintain `ASSUMPTIONS.md` for anything inferred — genre, audience, market, length —
and `RUN_REPORT.md` with the exact unfinished task and the step to resume from. Record the
positioning fields in the state file; a novella, short novel, or serial installment must be
labelled as one rather than silently measured against novel expectations.

When the launch profile is selected, run the premise forge before foundation and save the
result to `premise.md`; it nests inside phase one and renumbers nothing. Before any
evaluation, read the evaluator protocol and record the evaluator's independence grade — a
grade C is diagnostic only and cannot support an independent publication claim.

### During a run

Keep the phase order, the specialist dispatches, the gates, and the revision taxonomy
intact. Read the active canon, the voice specifications, and — where the book has one — its
ductus before drafting, editing, auditing, or scoring. Resolve it with
`python tools/ductus.py voice <book-root>` and record the digests it prints; a
`REFUSED` voice stops the phase outright. After every chapter block, revision, audit, score, or user decision,
run a maintenance check-in: merge duplicates, add provenance, scope facts that have
evolved, and flag contradictions without ever overwriting canon silently. Book-scoped and
chapter-scoped changes are scoped facts, not automatic contradictions. The compact
`incunabula-codex` pipeline does not replace this engine unless the user chooses the
portable workflow explicitly.

### After the work

Run a maintenance check-out: update the state, canon, voice specification, document registry, and
the append-only pruning log. Keep rejected conflict values with their provenance and resolve
them only by explicit decision. Archive only what is clearly superseded, recording the
original path, the archive path, the replacement, the reason, and the date. Never call the
book finished until the proof pulls and the state-canon-voice consistency gate both pass.

---

## Worlds are not filings

**Added 2026-11-23, after the second book in a row arrived with a legal instrument where a
game should have been.** The cause was not the genre. It was this file: before Phase 2 the
engine names its own artifacts *contract*, *ledger*, *gate*, *digest*, and *standing*, and
it had no worldbuilding step at all. A pilot that reads the pipeline before it invents a
world invents the pipeline.

So a world is now a required artifact, and the order of invention is fixed:

- **`world.md` exists before `forme` runs.** Three candidate world-engines, each in plain
  language, one chosen, the other two kept with the reason they lost.
- **The first candidate is the genre's own engine.** A LitRPG's world is a progression
  system: levels, stats, classes, and what they cost. A mystery's is an information
  asymmetry. A romance's is a social obstacle. If the first engine named is administrative,
  the run has imported this file and starts again.
- **An administrative engine is named and discarded.** A contract, a debt, a charter, a
  writ, a court, a permit, a title: these are this tooling's filing system wearing costume.
  "The sentence is a debt instrument" is not a world; it is a `STATE.yaml` with weather.
  Record it as the discarded candidate, because the next pilot will reach for it too, and
  the record is what stops it.
- **Every engine answers two physical questions.** What does the world do with this family
  that it could not do with anyone else? What does their labour produce that the surface
  cannot live without? A world that cannot answer the second has procedure in it, not
  politics.
- **The blind packet is how a world is found; `--gate` is how a contaminated one is
  refused.** `python tools/blind-packet.py <book-root>` builds the premise with none of this
  system's words in it, for a fresh context, a different model, or a person. `--gate` then
  judges the `world.md` that comes back, and the Phase 2 gate will not pass without it. See
  `references/fresh-eyes.md`. Run the packet before Phase 2 whenever the premise was written
  by this pipeline.

**What is not renamed.** The *host contract* keeps its name: it describes a real interface
between an agent and a host and has no fictional analogue. The rename covers the words a
pilot could mistake for a world — voice, book, series, scope, and length.

---

## The seventeen phases

```
1      Research            scout
1.5    Readership          readership
1.8    Ductus              ductus-designer
2      Foundation          forme
2.5    Voice matrix        voice-matrix
2.7    Case build          case-keeper (BUILD)
2.8    Collation, outline  collator
3      Drafting            setting          (scene by scene; a chapter may take several calls)
3.1    Register            register
3.2    Catchword           catchword
3.5    Quoin               quoin
3.7    Case update         case-keeper (UPDATE)
3.8    Composing           composing
4      Evaluation          proof-panel
4.5    Proof pull          proof-pull       (auto-loop, three rounds)
5      Revision            corrector
5.5    Case update         case-keeper (UPDATE)
5.6    Collation, manuscript  collator
6      Delivery            colophon + presswork
```

The same chain is machine-readable in `tools/phase-map.yaml` — the single source of
truth for `tools/run-phases.sh`. This diagram is the explanation; the yaml is what the
runner enforces. When the two disagree, that is a defect in one of them, not a choice.

**Why the quoin sits where it does.** After a chapter is written and before it is scored,
the quoin runs. It does not fix anything; it breaks predictability. It cuts self-explaining
similes, injects irrelevant thoughts where the mind is too focused, lets emotional control
fail, deflates needless precision, removes the most predictable paragraph, roughens clean
dialogue, and guarantees that a meaningful share of detail is pure texture rather than
theme. It applies the operations a chapter's diagnosis calls for, not a fixed count:
operation 1 wherever an overprint is present, operation 9 every time (uniformity is invisible
from inside one chapter), and the rest where the chapter has gone too smooth. The phase
exists because any drafting system drifts toward order, and good books need moments of
disorder — a per-chapter quota manufactures the same disorder everywhere, which is its own
tell.

---

## The required gates

### The variety rule

One rule, stated once here and applied to three surfaces: **no device carries two consecutive
units.** The surfaces are the structural approach chapter to chapter, the hook type chapter to
chapter, and the join type between scenes. The phase-gate lines below say *(variety rule)* and
restate nothing; this is the rule. A repeat the material demanded is a recorded decision, not
an exemption — the record is what the rule reads.

### Prose gate

Required at every prose phase, and never satisfied by a scan that was not run.

**Four tools, four questions.** `tools/prose/deslop-check.sh` reads one chapter against
per-1k caps. `tools/prose/check-uniformity.py` reads the whole manuscript and compares the
chapters to each other. `tools/prose/check-drift.py` reads first chapters against last for
a voice shift. `tools/prose/check-arc.py` reads whether the emotional direction ever
reverses. None replaces another: the scanner never holds two chapters at once, the
cross-chapter checks never see a bad sentence, and all four must be green.

**The suite runs as one command:** `bash tools/run-gates.sh <book-root>`. It runs every
gate — prose, narrative, length, declared-length-vs-plan, research, pass evidence — and exits nonzero if any gate
fails **or does not run**. Exit 0 is CLEAR; exit 1 is FAIL; exit 2 is NOT CLEAR (a gate did
not run or declined to judge) and blocks the phase exactly like a failure. A phase may not
claim a gate passed without a `run-gates.sh` verdict on record.

- Every chapter scanned by the project's calibrated scanner and passing.
- The manuscript passing the uniformity gate: chapter lengths varying like human prose, no shared rhythm profile across chapters, and no coda habit. This is the row the per-chapter caps structurally cannot cover.
- Thresholds taken from the calibration record, never from taste. A rule is zero-tolerance only at zero occurrences in the reference corpus; everything else gets a cap, expressed as a rational rather than a whole number.
- The control run re-validated: human prose passes, a synthetic slop fixture fails, an AI-written control is separated rather than blanket-failed, and a machine-uniform manuscript fails the uniformity gate.
- A directory scan that expands to zero files is a failure, not a pass.
- Exempt files named explicitly in the report. Outlines, scene packets, and state files sit above the prose caps by design.

Passing is necessary and never sufficient. The gate cannot see voice, rhythm, a dead
metaphor, or one argument restated ten ways, so the read-aloud pass stays in force.

**And passing both tools is still not the standard.** Sustained consistency is itself the
tell: a manuscript that is uniformly competent, uniformly even, and uniformly well-formed is
not a pass, it is the finding. What the gate is looking for is the presence of accidents —
an outlier chapter, an abandoned obsession, a section that runs long because the material
wanted it, a chapter that ends flat because it should. See **Consistency Is the Fingerprint**
in the deslopify guide. A waiver on a uniformity row is recorded with its reason, and the
same waiver recurring across books is itself the pattern.

### Narrative gate (Freeze 13)

Required at evaluation and at delivery, and never satisfied by a ledger nobody filled.
The prose gate measures the surface of sentences; this one measures the shape of story.
It is one declared file — `NARRATIVE_LEDGER.yaml` at the book root — checked by
`tools/prose/check-narrative.py`, which reads no prose at all:

- **N1 narrative debt (gates).** Every obligation the book introduced with emphasis —
  mystery, trauma, named secondary character, ticking clock, promise, threat, loaded
  object, taught skill — ends RESOLVED (payoff recorded) or DEFERRED (reason recorded).
  OPEN at delivery is a failure. An unexamined setup is a failure, not a loose end.
- **N2 beat repetition (reports).** Declared per-chapter emotional arcs that repeat,
  exactly or near-exactly, including consecutive runs. Four chapters running the same
  circuit is the book having one scene four times; the row makes it visible.
- **N3 scene function (reports).** Extended scenes declare their function from a closed
  list (relationship shift, theme payoff, plot turn, character revelation, pure
  texture); duplication is reported and `pure texture` is a budget the author sets.
- **N4 ledger conformance (gates).** Schema validity, status discipline (RESOLVED
  without a resolution is a defect; DEFERRED without a reason is a defect), and
  staleness — a chapter the ledger has never seen cannot be shown to owe nothing.

The ledger is fed by declarations, not by scripts: `case-keeper` extraction pass 6
records debt, `proof-panel` declares each chapter's beat arc and each extended scene's
function at Phase 4, `collator` audits the ledger against the text. The four
prose-reading companions — `check-figurative.py` (two images fighting over one
referent), `check-dialogue-tags.py` (per-character tag register vs. the voice matrix),
`check-quantities.py` (numbers that disagree with each other), `check-agency.py` (places
and objects given a mind, and motives stated by absence) — report, with one
exception: `check-dialogue-tags.py`'s V3 row **gates** the book's breath-family share of
tagged spans above 0.107 (p90 of 167 public-domain novels; 5% of human books exceed it).
The other rows cannot fail anything: no measured corpus stands behind them.

It gates with no corpus for the same reason `check-length.py` does: it compares a book
to the obligations that book declared for itself, and there is no population it can
false-fail. Everything it cannot see it says so: an unrecorded setup passes this gate
perfectly, which is why collator's full pass runs before the row is consulted.

### Maintenance gate

Required at every phase, and never satisfied by a layer that was never created.

- `CANON_LEDGER.yaml`, the active voice specifications, and the pruning log exist. Their absence at a later phase is a repair, recorded as run late.
- Check-in before the work: state, canon, recent session entries, and the phase prompt read; chapter status and word counts reconciled against the actual files; a changed-file scan done; duplicates merged; provenance and verification stamps added. The mechanical half is `bash tools/preflight.sh` plus `python tools/check-registry.py` — run them and record their verdict instead of re-deriving it by hand, and let the runner's own phase record stand as the history entry for a phase that did not run.
- Check-out after the work: state, canon, voice specification, document registry, and pruning log updated, and the phase gate re-run before progress is claimed.
- A session log entry exists for the session, and a history entry exists for every phase — including the phases that did not run. A skipped step is recorded as skipped.
- The primary state file parses under a real parser. A file that will not parse means no downstream gate could have read it: report, repair, re-verify.
- No contradiction resolved silently. Both values kept with provenance, a conflict record raised, and anything touching content boundaries, ending ambiguity, or a character's core identity escalated rather than decided.
- Unresolved conflicts reported by identifier with their blocking scope, so an open conflict cannot pass as a settled fact.
- Nothing archived or deleted without path, archive path, replacement, reason, and date. Pruning reduces active context; it does not erase history.
- Gate evidence recorded: the `run-gates.sh` summary table — command, exit status, documents scanned, failing rows with rule identifiers — and the control run. A gate without a recorded verdict is a gate that did not run.
- Every phase-level pass is complete only with its artifact file on disk: `register` leaves the blind-sort table with its verdict; `catchword` leaves hook/pull scores and the hook-type log; `quoin` leaves the operation log (the diagnosis, the operations applied, and the operations declined with their reasons); `composing` leaves the diff-review note; `proof-panel` leaves persona verdicts, the tic scan, and the independence grade; `proof-pull` leaves the round log. A claim without the artifact is a FAIL, not a pass. (`tools/check-pass-evidence.py` verifies presence; it reads no prose and judges no manuscript.)
- Progress is tracked as gated words — words in chapters with complete pass files. Chapters-drafted is informational.
- No chapter under 2,000 words or 50% of its planned length without a recorded waiver (reason, outline actuals updated, session-log entry). A waiver is not a routine device: a second consecutive waiver, or one that leaves the running total behind the outline's plan (row `L2` of `tools/check-progress.py` reports that running total; row `C1` there fails a declared length that contradicts the outline's plan, so the band cannot be shrunk to fit the output), is a stop-the-line event escalated to the human. A recurring waiver is itself the pattern.
- Grade-C evaluations are diagnostic only and cannot advance phases. Where no independent critic exists, checkpoints belong to the human; self-votes stand in for nobody.

---

## Phase gates, condensed

Each arrow below must be earned, not assumed. **Every "gate passes" below means:
`bash tools/run-gates.sh <book-root>` returns CLEAR (exit 0) for the rows that phase
requires.** A FAIL (1) or a NOT CLEAR (2) blocks the transition; a run that was skipped
proves nothing and is never recorded as a pass.

**The one exception is the world gate.** It belongs to 2 → 2.5, and by definition it runs
before the book has chapters, so `run-gates.sh` (which needs `manuscript/chapters/`) cannot
carry it: `python tools/blind-packet.py <book-root> --gate` is the command, its exit 0 is
the pass, and its printed verdict is pasted into the phase record as the row's evidence.
Where a book does have chapters and still carries `world.md`, `run-gates.sh` runs the same
check as a hygiene row.

- **1 → 1.5** market study with comps, genre conventions, a length target, an engagement type, and explicit user approval of direction.
- **1.5 → 2** three to five personas; a primary that drives writing and a hostile that drives evaluation; deal-breakers and triggers on each.
- **2 → 2.5** `world.md` records three candidate world-engines and the one chosen, with the pipeline's own administrative idiom named among the discarded, and `python tools/blind-packet.py <book-root> --gate` returns PASS (W1 three candidates, W2 a chosen engine, W3 that engine is not administrative, W4 the attractor named among the discards) — a FAIL blocks the transition however complete the other artifacts are, because a world made of a contract or a debt is the failure the gate exists to catch; character profiles with wound, lie, and arc for every principal, and the disorder devices (irrelevant obsession, distortion, unprompted memory, failed emotional management) **assigned by fit rather than carried by every character** — they are devices, not a template, and characters should differ in kind and not only in which quirk was assigned; a chapter outline carrying emotional anchors and emotional surprises instead of intensity numbers; `story-spine.md` with the ends decided (true state, false surface, thread endings, twist seeds, multi-scene chapters, flippable lines) and the means left loose; an opening strategy; a structural approach per chapter *(variety rule)*; a transition plan *(variety rule)*; theme as a question; ranked engagement types; re-read architecture; a chosen stylistic device; user approval.
- **2.5 → 2.7** the voice matrix exists with a global profile, per-character cards including how each voice breaks, a differentiation matrix showing at least three distinguishing markers per pair, the anti-pattern checklist, and benchmark samples; the voice bank holds at least ten samples, including at least three that demonstrate voice under pressure and two irrelevant-thought samples.
- **2.7 → 2.8** the entity file was built from foundation and outline, tracking every character, location, and timeline entry.
- **2.8 → 3** the outline collation found no critical issues; warnings logged, and each either addressed or deferred with a reason.
- **3 → 3.1** the chapter is written, its self-report saved with chaos moments, the ugly sentence, impulse deviations, the scan result, and the structural approach used, and the **prose gate passes**. A chapter that fails the scan does not enter the manuscript however well it reads. No passage delivers information naked: every expository load is carried by something that does a second job in the passage. Conflict, a wrong first answer, a concrete object, withheld context, and a cost paid for not knowing are the five known carriers, not a closed list — a new carrier is legal when it does two jobs at once, and the gate asks what else the passage is doing, never which of five it used.
- **3.1 → 3.2** register ran; the blind sort passes for every speaking character in the chapter; the dialogue-to-prose ratio sits inside the genre target.
- **3.2 → 3.5** the hook and pull are scored at or above the genre floor, and the hook type obeys the variety rule.
- **3.5 → 3.7** the quoin ran, its report records the diagnosis and the operations it declined, operation 9 was judged against the previous two chapters' numbers, and the emotional anchor is preserved. Every three to five chapters, the case tracker updates.
- **3.7 → 3.8** the quoin report is saved and the anchor intact.
- **3.8 → 4** the composing pass is run and an agent has reviewed its diffs for false positives.
- **4 → 4.5** the prose gate passes, the score is calculated per chapter and globally, weaknesses are ranked by taxonomy with citations, the top three weaknesses and the top three strengths to preserve are named, the tic scan ran against genre targets, the character-chaos check ran, and the keepsake anchors were counted. The chapter's **beat arc and extended scene functions are declared** into `NARRATIVE_LEDGER.yaml`, and any new obligation the chapter opened is recorded as a debt entry — declarations are what the narrative gate later checks.
- **4 → 4.5, the passing-reader gate** — if the passing reader would not keep reading, treat it as critical regardless of the score. It is the single best predictor of commercial success and it overrides everything else.
- **4.5 → 5** the proof pull looped up to three times; if the floor did not move after three, escalate as structural. The threshold is genre-adjusted (literary 7.5; commercial, thriller, and prescriptive nonfiction 7.0; memoir 7.5), with 8.0 recommended for submission and 8.5 for a bestseller or award target.
- **5 → 4 loop** revisions completed and strengths confirmed intact, at most three cycles. If the oscillation count falls under six, rises above twelve, or comes back irregular, that is a macro-structural problem the editor cannot fix — loop to phase two.
- **5 → 5.5** the case tracker updates after revision.
- **5.5 → 5.6** the full-manuscript collation runs: names, appearances, and relationships consistent; no impossible timeline or travel; no character acting on knowledge they cannot hold; every thread closed or deliberately open; world rules unbroken. The narrative ledger is audited against the text: unrecorded emphatic setups become debt entries, a RESOLVED entry without its payoff on the page is a critical finding, and beat-arc repetition and scene-function duplication across the whole book are read in one pass.
- **5.6 → 6** the prose gate passes on every chapter with the control run recorded; the floor meets the genre threshold; **first impression ≥ 7.0**, and where it is under 7.0 while the floor is at or above 7.5, a targeted pacing and shareability revision runs before packaging; **the narrative gate passes — `check-narrative.py` exits clean: every debt entry RESOLVED or DEFERRED with a reason, the ledger covering every chapter file**; no structural weaknesses remain; human feedback integrated or explicitly deferred; user approval to package.

**How to read the two indices.** The score governs revision priority; the first-impression
index governs submission readiness. When they diverge by two points or more, report the
divergence — it is the finding, not a problem to reconcile.

---

## State file

```yaml
project:            # title, genre, subgenre, audience, length target and floor/ceiling,
                    # positioning, planned chapters, average words, language, device,
                    # comps, created, updated
phase:              # current, status (in_progress | gate_pending | gate_passed | blocked), history
chapters:           # total planned; per chapter: number, title, words, status, structural
                    # approach, emotional anchor, emotional surprise, scores
incunabula_score:   # current floor; seven dimensions each with score, evidence, date
commercial_viability:  # first impression, standing type, engagement ranking, commercial
                    # pacing, keepsake anchors, passing-reader verdict, shareability split,
                    # concept pitch, human closeness
voice_bank:         # initialized, sample count, description, voice under pressure
voice_matrix:       # created, card count, differentiation matrix, blind sort passed
readership:         # created, count, primary, hostile
continuity:         # outline check, manuscript check, critical and warning findings
proof_pull:         # chapters passed, chapters escalated
mechanisms:         # em-dash count, overprint count, adverb density, hard-rule failures
evaluation_tracking:  # independence grade, worst patterns, reader verdicts, chaos counts,
                    # shelf test, afterimage test, oscillation count
systemic_patterns:  # pattern, chapters, severity, notes
decisions:          # date, decision, rationale, phase
human_feedback:     # date, source, summary, status
revision_cycles:
length_gate:        # pass | flag | block against the declared positioning
```

---

## Dispatch

The control layer is mechanical. `bash tools/run-phases.sh <project>` walks the chain in
`tools/phase-map.yaml`, runs each phase's gate tools itself, parses their exit codes —
never a report — and refuses to advance on anything but CLEAR: a failure hard-stops the
run, marks the project state `HALTED`, and writes a resume pointer naming the phase, the
gate, and the exit code. `bash tools/run-phases.sh --list` prints the chain. The runner
writes no prose and scores nothing. It is control; the skill layer is content.

The orchestrator hands the user the dispatch for the phase the runner has reached: the
skill, the project path, the specific task, the relevant state, and the constraints. When
the skill's work lands, the runner re-runs the phase's gates and advances or halts the
project state itself.

**The manual path — fallback, and the weaker one.** Where the runner cannot run, dispatch
each skill by hand as listed below and run `bash tools/run-gates.sh <project>` at every
phase boundary, recording its verdict. The gates are then enforced by nothing except the
run's own record — that is the failure mode the runner exists to prevent, so use this path
only when the runner is genuinely unavailable, and say so in the session record.

**Research** — `scout` for the market: top titles in the niche, gaps, comps, length
estimate, engagement recommendation, and the prose-rules file for the drafting skill.

**Readership** — `readership` for three to five personas, naming the primary, the hostile,
and the stretch reader.

**Ductus** — `ductus-designer` for the book's voice specification, designed from what the
author wants and from text that sounds like it, with the corpus-fit check run before a word
of the specification is written. It writes `ductus.md` beside the foundation and never writes prose. If
the book carries a press ductus, that voice is the parent and its refusals bind. Output is
frozen before chapter one; a change after drafting starts is a dated decision.

**Foundation** — `forme` for characters with wound, lie, and arc, built on the chosen engine in `world.md` (plus the disorder devices
the characters' own logic calls for), an outline carrying anchors and surprises and
structural approaches, `story-spine.md` with the ends decided and the means left loose, the
opening strategy, the voice bank, theme as question, re-read architecture, and cultural
vocabulary.

**Voice matrix** — `voice-matrix` for the global profile, per-character cards, the
differentiation matrix, and benchmark samples. It is prescriptive.

**Case build** — `case-keeper` in BUILD mode over foundation and outline.

**Outline collation** — `collator` on foundation, outline, and voice matrix: timeline
feasibility, nobody in two places, information flow, threads with planned resolutions.

**Drafting** — `setting` for one chapter — or for the next scene of a chapter the spine
marks multi-scene — given the outline entry for that chapter, the
voice bank including the pressure samples, the previous chapter, the structural approach
that must differ from the previous chapter's, and the instruction to write similes raw
rather than extending them. Chapter written to the manuscript folder, self-report to the
chapter report file.

**Register** — `register` for dialogue only: blind sort, voice bleeding, subtext, clean
dialogue, tag-to-beat ratio. Narrative prose untouched.

**Catchword** — `catchword` for openings and endings, scoring hook and pull, rewriting the
first and last few sentences below threshold, and never repeating the previous chapter's
hook type.

**Quoin** — `quoin`, diagnosing the chapter and applying the operations the diagnosis names,
operation 9 always, preserving the anchor, report saved to evaluations.

**Case update** — `case-keeper` in UPDATE mode after each batch.

**Composing** — `composing` for the mechanical pass: em dashes, overprints, adverb density,
sentence-start repetition, filter words — with every diff reviewed for false positives
before it is applied.

**Evaluation** — `proof-panel`, never in the same context that wrote the chapter. Score
against the outline, the voice bank, and the previous chapter; run the tic scan at genre
targets, the reader simulation, the chaos check, and the keepsake test; add the shelf test
on chapter one and the afterimage test on the last chapter.

**Full-manuscript evaluation** — after every chapter has been through phase four at least
once: opening repetition, anchor-type repetition, mid-book sag, real structural variety,
chaos distribution, shelf test on the first sentences, shareable-moment count, afterimage,
oscillation count, and both indices.

**Proof pull** — `proof-pull` to loop evaluate, fix the top weakness, and evaluate again,
up to three rounds, escalating rather than churning.

**Revision** — `corrector` with the evaluation and the quoin report, an explicit mode, and
the strengths to protect. Never undo a quoin unless the evaluation flagged it as harmful.

**Delivery** — `colophon` for the package and the upstream signals file, then `presswork`
for the proofread and the formatting. The narrative gate is consulted first: a book
with OPEN debt does not ship, and the delivery run records the `check-narrative.py`
exit status beside the prose-gate evidence.

After delivery, read the upstream signals. If the packager flagged premise clarity or
structural suspense, those are problems the evaluation missed, and a targeted re-evaluation
of the macro structure is warranted before final delivery.

---

## Anti-inflation

The system scores its own output, which is maximum bias, so the rules are explicit.

1. No dimension jumps more than half a point in one revision cycle without textual evidence.
2. Every score cites a specific passage. A number with no citation is invalid and is sent back.
3. When one dimension rises, check its neighbours did not fall — prose improved means pacing re-checked.
4. A score at or above nine must answer whether an editor at a major house would agree it competes with the named comp. If that is uncertain, the score is capped lower.
5. **The floor is the score.** Six dimensions at nine and one at seven is seven. No averaging, no weighting.
6. Assume self-evaluation is inflated by half a point to a full point. The benchmark delta between self-scored and externally calibrated work is negative, and it is calibration rather than regression.
7. Cross-reference scores against benchmark bands, and challenge a floor above eight without extraordinary evidence.
8. Independently count overprint instances after every evaluation. If the evaluation missed any, request the prose dimension be re-scored.

| Score | Reading | Publishing implication |
|---|---|---|
| 6.0–6.5 | amateur | rejected on sight |
| 7.0–7.5 | competent | publishable, forgettable, mid-list |
| 8.0–8.5 | strong | major-house level |
| 9.0–9.5 | exceptional | bestseller or award level |
| 10.0 | genre reference | reserved for the books that defined a category |

---

## The score — seven dimensions

The score is the floor: the lowest dimension of the seven.

**A score is a band, not a measurement.** Report each dimension to the nearest half point and
read it as a band of ±0.5; the instrument does not resolve 7.5 from 7.0, and a gate compares
the bottom of the band. A floor of 7.0 with a band reading 7.0–7.5 passes; a floor of 7.5 with
that same band does not. Any precision finer than that is a number the system invented about
itself.

| # | Dimension | Measures | Evaluation hook |
|---|---|---|---|
| 1 | Originality | what this book does that nothing else does | judged, not counted: one unmistakable thing beats three borrowable ones, and no list of three earns a score by itself |
| 2 | Theme | depth of the central question | present in at least 80% of chapters without being stated; a character stating it caps at 7.0 |
| 3 | Characters | dimensionality, contradiction, chaos, arc | chaos populated; blind sort passes; secondary characters have lives |
| 4 | Prose and voice | sentence quality, identifiable personality, anti-AI compliance, pressure voice | three random pages identify the voice; the tic scan meets the genre target; the voice changes under stress |
| 5 | Pacing and coherence | speed variation, value shifts, hooks, structural variety | each chapter shifts value; speed varies within chapters; no consecutive structural repeats |
| 6 | Emotion | real investment | top three impact moments; vulnerability before competence; surprises; keepsake anchors |
| 7 | Configurable | varies by project | surreal (interlude at illustrate, comment, or reveal level); market (the default); worldbuilding; epistolary; humour; custom |

---

## The two commercial indices

**First impression** predicts first-year sales. Weighted: commercial pacing 20%, keepsake
anchors 20%, passing-reader verdict 20%, shareability 20%, concept pitch 10%, human
closeness 10%. Gate: at least 7.0 before delivery.

**Standing type** predicts twenty-year sales, using the seven dimensions directly with
weights adjusted for engagement type — identity effect weighted for aspiration-led books,
framework utility for prescriptive nonfiction, and evenly otherwise.

They measure different things and are allowed to disagree. A literary masterpiece can be
commercially invisible; a page-turner can be craft-thin. A divergence of two points or more
is reported, not resolved.

---

## Engagement types

Declared in phase two, tracked in state, and shaping every downstream skill.

| Type | Reader experience | Maximise |
|---|---|---|
| Empathy | feeling what the characters feel | vulnerability, intimacy, warmth |
| Fascination | unable to look away | moral complexity, ambiguity, contradiction |
| Self-insertion | I am the protagonist | relatability, an accessible protagonist |
| Intellectual | I am learning and thinking | systems, ideas, the aha |
| Aspiration | I feel special | quotable wisdom, identity affirmation |

Where primary and secondary conflict — self-insertion wanting a blank protagonist while
empathy wants a specific wound — that tension is the book's identity. Do not resolve it.

---

## Human feedback

When feedback arrives, log it with date and source, classify it by the revision taxonomy,
cross-reference it against the evaluation, and treat agreement between human and evaluator
as a critical issue; treat a single-source flag as something to investigate. Update the
revision plan and hold the status at pending until it is integrated or explicitly rejected.

## Outline synchronisation

After each chapter, read the self-report for impulse deviations — places the draft went
somewhere unplanned. Where a deviation was kept, update the outline to match what happened,
adjust any downstream chapter that the change touches, and log the decision with its
rationale. The outline is a living document: a successful deviation means the outline was
wrong, not the chapter.

## The chapter is the unit, not the call

One outline row is one chapter; one chapter is not one drafting call. A chapter that is
several scenes — or a document cluster — is drafted scene by scene across as many calls as it
takes, and the material sets the number. What must not happen is the reverse: a long book
built as many short chapters because each call writes roughly two thousand words, so the only
thing that can grow is the count. Total length is enforced (`check-length.py`); chapter length
has no target (`DRAFTING_FRAMEWORK.md`); the spine lists the multi-scene chapters so the split
is planned rather than improvised. A chapter assembled from several scenes is the normal way
to get a long chapter.

## The story spine

Phase 2 also produces `story-spine.md`, beside the outline and not inside it. It decides the
*ends*: the true state of the world, the false surface the reader is told, where each thread
lands, each twist's seed and payoff chapters, which chapters are multi-scene, and the early
lines that will return with their meaning flipped. The outline keeps its current granularity —
how a chapter gets there is where impulse deviations live, and an outline detailed enough to
transcribe turns drafting into transcription.

`collator` checks the spine against the plan at 2.8 and against the text at 5.6: a payoff with
no seed, or a seed that never pays, is a spine finding. A kept deviation updates the spine
exactly as it updates the outline.

## Layered books

A book may declare `structure: layered`: a document set rather than a manuscript, where the
layers accuse each other and the contradiction is the design. For those books, and only where
the intake declares it:

- **Canon is per layer.** Every `CANON_LEDGER.yaml` and voice specification carries a `layer:` key.
  A contradiction between layers is content; a contradiction within a layer is a finding. No
  layer resolves another's value — the channel firewall applied to fiction.
- **The outline is architecture.** The spine records the document layers, the nesting depth,
  and where the interruptions fall (`forme`).
- **Layout is a drafting decision.** The composing pass (3.8) decides the typographic rules and
  checks them, before evaluation. `presswork` formats what 3.8 decided; it does not decide it.
- **The gates are scoped per layer.** `deslop-check.sh`, the tic scan, `check-uniformity.py`
  and the 5.6 collation run per layer, and "world rules unbroken" becomes "broken only where
  the architecture says they break". One layer is never measured against another.
- **The score is re-scoped, not waived.** Chapter-based dimensions are suspended for a book
  whose unit is a document or a page; the configurable seventh dimension carries the book's own
  stated rule (surreal, custom), and the commercial indices are reported as inapplicable rather
  than as failures. An anti-commercial form is not failed for refusing airport readability it
  never asked for.

**The honest limit.** The `layer:` key and the per-layer scoping are declared in the book's
state and read by the skills; the frozen tools are not rewritten to split a book into layers,
so a layered book's gate evidence is assembled per layer by the run while the freeze still
applies to the instrument as a whole. That gap between the declaration and the tooling is
recorded as one rather than papered over.

## Three runners, one engine

| What you want | Run | What it is |
|---|---|---|
| One book, start to finish, minimal steering | `incunabula-auto "<idea>"` | The full engine, autonomous, stopping only at three checkpoints (foundation, manuscript, delivery) |
| To steer every phase | `incunabula` | The same engine, driven by hand: `start`, `write`, `evaluate`, `revise`, `score`, `deliver` |
| A small project, or a host that only reads and writes files | `incunabula-codex` | The continuity layer (intake, canon, voice specifications) and an optional 8-phase compact pipeline |

The first two are one engine with a different amount of pilot. The third is a smaller
pipeline that must never be swapped in silently for the full one.

## Systemic patterns

After each evaluation, check for a pattern recurring across two or more consecutive
chapters. Log it as systemic, add a specific warning to the next chapter's dispatch, and if
it persists add it to the project's own anti-pattern list. A systemic overprint escalates to
critical — it is the most identifiable tell there is.

## Loop-back rules

Revision cycles past three without a floor move, or an oscillation count outside six to
twelve, means the problem is structural — back to phase two. A character evolving
unexpectedly pauses writing until the foundation is updated. Research gaps dispatch `scout`.
Voice drift goes to `corrector` with voice samples. A passing reader who would not keep
reading overrides everything and is fixed before anything advances. Post-packaging signals
trigger a macro re-evaluation.

---

## Session protocol

**Start.** Establish the mode and read the primary state, canon, active voice specification, the
phase prompt, and the maintenance protocol. Run the maintenance check-in. Report the phase,
chapter progress, floor, first impression, pending feedback, systemic patterns, and any
unresolved canon reviews. Recommend the next action with a full dispatch. Flag feedback that
has sat unintegrated for more than two sessions.

**End.** Update the state and log decisions with rationale. Note pending human actions. State
the next session's recommended action. Update canon, voice specification, and document registry,
and append merged facts, conflicts, resolutions, supersessions, and archival actions to the
pruning log.

---

## Revision taxonomy

Always revise top-down; never polish prose that is about to be deleted.

1. **Structural** — the skeleton. An arc that does not close, theme missing from a fifth of the chapters, parallel chapters repeating one thesis, an order that does not make sense, a section that contributes nothing. Action: loop to phase two, update the outline, re-plan before rewriting. Risk: high.
2. **Connective** — the joints. Weak transitions, missing bridges, a jump from argument to evidence, emotional progression skipping a step, data without context. Action: rewrite openings and closings, add connectors, redistribute. Risk: medium.
3. **Prose** — execution. Voice drift, dialogue without subtext, clumsy exposition, cliché and filler, AI tells, metaphors that fail. Action: `corrector` on specific passages, or `setting` for a full rewrite. Risk: low.
4. **Factual** — isolated errors. Wrong or outdated data, a name or date or eye colour, local word repetition, grammar. Action: fix directly. Risk: nil.

---

## The tic scan

The evaluator detects these, the quoin breaks them, the drafting skill avoids them, and the
orchestrator enforces the targets. Targets are genre-adjusted: a clean literary manuscript
carries zero to three, memoir zero to four, commercial fiction zero to eight, prescriptive
nonfiction zero to twelve. A manuscript scoring zero across all twenty-two is suspicious rather
than perfect.

**Five rows are measurements; the other seventeen are taste.** Rows 3, 4, 11, 21 and 22 are
the ones with a corpus behind them (`PRINTERS_COPY.md` §3: `D2`, `D1`, the independently
counted overprint, `F1`/`A24`, `A25`), and they are the only rows that can fail a book
outright. The rest are craft judgement — worth looking at, and not evidence. Keep the two
kinds apart before whoever is deciding what to obey, or the taste rows borrow the authority
of the measured ones.

1. Forced symmetry — by day one thing, by night another.
2. Empty poetic vocabulary — tapestry, symphony, dance, journey.
3. Automatic rule of three.
4. Em-dash overuse.
5. Metaphors that decorate without meaning.
6. Dramatic sentences opening on *And*.
7. Pseudo-philosophical section closings.
8. Excessive parallelism.
9. Over-smooth transitions.
10. Named emotions instead of shown ones.
11. **The overprint** — every observation explained a sentence later. The single most identifiable tell in the whole list, tracked with its own severity and counted independently.
12. Binary negation openers.
13. Fake-precise numbers.
14. Demonstrated emotional control that never fails.
15. Encyclopaedic confidence in an unfamiliar place.
16. Philosophising that would fit on a mug.
17. Clean dialogue with orderly turns.
18. Every detail echoing the theme.
19. Graduated reveal as the only structure.
20. Regular body-temperature reporting.
21. **The explanatory coda** — the chapter closing on a turn that explains the chapter's meaning: *That is why…* *Which is why…* *It is also why…* *the next chapter is about…* Published prose closes 0 of 50 chapters this way, which makes it the only pattern on this list that is also a position rule: it fails outright wherever it lands on a closing paragraph, whatever the score says.
22. **The antithesis formula** — *It was not X. It was Y.* Published prose manages one occurrence in 177,000 words; the books this engine produced managed twenty-five, and clustered them in chapter endings. State the thing instead.

Neither 21 nor 22 can be counted per chapter and judged on rate alone. Both are habits of
*placement*, and a rate that looks acceptable in each chapter individually is exactly how a
book ends up closing fifteen of twenty-five chapters on the same rhetorical move. The
distribution is the measurement; `tools/prose/check-uniformity.py` takes it.

Prescriptive nonfiction is exempt from the patterns that are native to it — the wise
closing, the overprint, the confident description, the aside, thematic saturation, and the
graduated reveal — and those are not penalised in that genre.

---

## Commands

`start [idea]` initialise and run phase one · `status` current state and next action ·
`gates` run the full suite (`bash tools/run-gates.sh <project>`, verdict recorded) ·
`run` the phase runner (`bash tools/run-phases.sh <project>`) — sequences the chain from
`tools/phase-map.yaml`, enforces gate exit codes, HALTs the state on failure ·
`phase [n]` force-advance with a gate check that will refuse — the check is `run-gates.sh`,
and it refuses on FAIL or on NOT CLEAR · `write [n]` prepare a
drafting dispatch · `quoin [n]` · `evaluate [n|all]` · `revise [n]` · `score` the
breakdown plus both indices · `deliver` phase six after its gate check · `feedback [file]` ·
`voice-bank add [file]` · `blind` build the fresh-eyes packet (`python tools/blind-packet.py <project> --write`) · `voice-matrix` · `readership` · `continuity [outline|manuscript]` ·
`register [n]` · `catchword [n|binge]` · `composing [n|all]` · `proof-pull [n]` ·
`patterns` · `oscillation`.

## Principles

1. **The user's idea is the point.** Execute their vision with technical excellence rather than substituting a different one.
2. **Quality is not negotiable.** The floor exists because one weak dimension sinks the book. Nine-point prose with six-point characters is a six-point book, and six-point books are rejected.
3. **Execution over theory.** Everything here is something to do, not something to know.
4. **Loops are the process working.** Finding during the writing that the foundation must change is not failure. Going back is not regression.
5. **Pace carries.** A book with strong pacing and modest prose outsells the reverse by an order of magnitude. Write for the passing reader, the one picking it up in an airport, because they are the best available predictor of whether it sells.
6. **The system is biased about itself.** Every score is inflated until proven otherwise. Challenge relentlessly.
