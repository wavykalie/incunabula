# RUN REPORT — Book 1 (clean restart)

**Reported:** 2026-09-22
**Rule:** a phase is only "complete" here if its file is actually on disk. No chat claims.

---

## Phase status

| Phase | V4 name | Status | Evidence file |
|---|---|---|---|
| 0 | Intake (upgrade layer) | **complete** | `INTAKE.md`, `ASSUMPTIONS.md`, `PROJECT_STATE.yaml`, `artifacts/00-brief.md` |
| — | Reference reading (not a V4 phase) | **complete** | `references/tone-references.md` |
| 1 | Research | **partial** | `artifacts/01-market-map.md` (desk analysis; no live research) |
| 1.5 | Reader personas | **RUN LATE — it had never run and was blocking Phase 4** | `reader-personas.md` |
| 2 | Foundation | **complete — GATE PASSED** | `foundation.md`, `outline.md`, `scene-packets/` (7) |
| 2.5 | Voice DNA | **complete** | `voice-dna.md` |
| 2.7 | Entity tracking (BUILD) | **complete** | `ENTITY_STATE.yaml` |
| 2.8 | Continuity (outline) | **RUN LATE — 4 CRITICAL · FAIL, then CLEARED** | `continuity/outline-audit.md`, `CANON_LEDGER.yaml`, `maintenance/SESSION_LOG.md` |
| — | Maintenance layer (canon ledger, session log, pruning log) | **RUN LATE — created this session as a REPAIR** | `CANON_LEDGER.yaml` (series + book), `maintenance/PRUNING_LOG.md`, `maintenance/SESSION_LOG.md` |
| 3 | Writing | **complete — all 7 chapters drafted, gate PASS on each** | `manuscript/chapters/chapter-01..07.md` |
| 3 | Writing — polish pass | **complete** | 4 defects fixed in `chapter-01/03/05/07.md`; re-gated PASS |
| 4 | Adversarial Audit | **complete — structural criticism + four-reader simulation + anti-AI reading pass** | `continuity/adversarial-audit.md` |
| 5 | Literary Barrier Revision Loop | **NOT ACTIVATED** — its activation condition is a user quality target and none has been set | `artifacts/05-barrier-note.md` |
| 5.6 | Continuity (manuscript) | **RAN FOR THE FIRST TIME — 2 CRITICAL, FAIL, then CLEARED** | `continuity/manuscript-audit.md` |
| 6 | Final Score | **complete — 7.7 composite, both gates green** | `artifacts/06-scorecard.md` |
| 7 | Editorial Package | **complete — and the validation build was produced** | `artifacts/07-editorial-package.md`, `dist/merope-book-one_WORKING-TITLE.epub` |

## Closing verdict — 2026-09-22

**Book 1 is closed.** 7 chapters, 15,531 words, prose gate 7/7 PASS with controls green, Phase 2.8
and 5.6 gates cleared, Phase 4 passed, scored 7.7, packaged, and built into an EPUB.

**The single most important result of the whole run:** Phase 5.6 had never been run, and running it
found **2 CRITICAL defects in prose that had already passed the prose gate on all seven chapters.**
A manuscript can be 7-for-7 on a mechanical scanner and still contain a chapter that asserts an act
no chapter shows. That is a measurement, not an opinion, and it is the reason the workflow has more
than one gate in it.

**Phases that ran LATE, all recorded as late rather than backdated:** 2.8 (after ch.1), the mainte-
nance layer (never instantiated until Phase 3), 1.5 (never run at all, and *blocking* Phase 4), the
voice bank (4 of 10 until after drafting). The pattern is consistent and is reported as a pattern:
**this pipeline under-runs its own preconditions and only notices when something downstream blocks.**

**What is not claimed:** no chapter has been read aloud. Phase 5 has never run, so there is no cali-
brated lens score, only a self-assessment that says so itself. The cover-the-name exercise has still
not been performed against the drafted chapters. Six author items are open, including every title
and both leads' appearance. The launch viability score is 4.5 and the reason is written down.

**The last unmet success criterion is the one that matters most:** a fresh session resuming
correctly. That test is Book 2, and it is next.

## Maintenance layer — created 2026-09-22, late

**This is the bigger version of the same failure as Phase 2.8, and unlike Phase 2.8 it had not been
recorded as skipped.**

`book-genesis/SKILL.md` → *Before V4 starts*, item 5 requires `CANON_LEDGER.yaml`, the active voice
contracts, and `maintenance/PRUNING_LOG.md` **before dispatching the first V4 phase.** At the time
this was discovered the project was at Phase 3 with a drafted chapter 1, and **none of those
artifacts existed at any scope.** So the workflow's machine-readable half was never active: no fact
carried provenance, no decision had a session record, no conflict had anywhere to live, and no
maintenance decision — including the deletion of the torn-down earlier build — was ever recorded.

### What exists now

| Artifact | Content |
|---|---|
| `../CANON_LEDGER.yaml` (series) | stable entity IDs, series-wide rules, and the **pre-registered Book 2 scoped changes** |
| `CANON_LEDGER.yaml` (book) | **46 facts** with provenance, **10 conflicts**, **24 registered documents** |
| `maintenance/PRUNING_LOG.md` | 8 entries, including the unrecoverable loss |
| `maintenance/SESSION_LOG.md` | first session entry, establishing the format |
| `voice-dna.md` | extended with the chapter-narration and fact-presentation contracts |
| pipeline, both skills | `maintenance_gate: required` on all 8 phases, plus a gate block in the phase-gate checklist |

### What the ledger found on its first build

**`CONF-001` — narration tense.** `INTAKE.md` is the user-authority document and says **present
tense**. `foundation.md`, `PROJECT_STATE.yaml` and the drafted chapter 1 are **retrospective past
tense**. The schema's precedence rule puts the explicit user decision first, which means **chapter 1
may need to be rewritten.** The state file had previously been edited to match foundation without
reconciling `INTAKE.md` — the source that should have won.

Nothing in the continuity audit, the calibration work, or the prose gate would have caught this. It
is only visible when a user-sourced answer and a downstream document are compared side by side with
their authorities attached. That is the argument for the ledger, made by the ledger.

### Two records that could not be fixed, only written down

**The torn-down earlier build was deleted, not archived.** Protocol §7 says pruning reduces active
context, it does not erase history, and every archival action records its original path, archive
path, reason, replacement and date. There was no ledger at the time, so nothing was recorded. The
build produced a foundation, an outline, nine scene packets, a voice contract and an entity state —
all reproducing Coldbrook Junction's engine — and it is unrecoverable. The diagnosis survives in
`INTAKE.md` §3, which is now the only evidence it existed.

**The intake schema's persistence round was never asked** (update frequency, archival permission,
immutable sources, existing project). The default `archive_superseded: true` is applied and **labelled
as the schema's default, not a user decision**, so a default cannot harden into a fake canon choice.

### Honest scope note

The maintenance layer is now *running*, not *complete*. Six conflicts are open, `ENTITY_STATE.yaml`
still needs an UPDATE pass (no provenance fields, ch.3 object untracked, `LOC-004`/`LOC-005`
duplicated, no timeline entry for ch.2 or ch.5), the voice bank is still 4 of a required 10, and
Phase 1.5 has still never run. Those are recorded in the ledger's `unresolved_reviews` rather than
fixed here, so the next session's check-in reads them instead of rediscovering them.

## Phase 2.8 gate — CLEARED 2026-09-22

**Gate state: PASSED.** Zero CRITICAL findings open. Chapter 3 is unblocked.

| ID | Was | Now |
|---|---|---|
| CRIT-001 | Achird's silence specified four incompatible ways; ch.6 packet contradicted its own required elements | **Applied.** One rule across four packet lines plus a per-chapter speech budget in `ENTITY_STATE.yaml` |
| CRIT-002 | The ending had no author | **Applied.** The sleigh decides and she is carried; `foundation.md`'s arc line, Movement III row and warning 7 revised |
| CRIT-003 | ch.4 required Merope to recognise a ch.3 object she was never shown | **Applied.** She comes, looks, dismisses it; tracked as `ITM-002`, shelf renumbered `ITM-003` |
| CRIT-004 | `PROJECT_STATE.yaml` did not parse | **Applied.** Fixed and re-verified with a real parser |
| CONF-001 | *found afterwards by the ledger* — narration tense | **Applied.** Retrospective past settled; three ch.1 sentences normalised; **no rewrite** |

**Six WARNINGs applied** (004, 006, 007, 008, 011, 012). **Six deferred with a named trigger each**
(001, 002, 003, 005, 009, 010) — recorded in `PROJECT_STATE.yaml → continuity.deferred_warnings`
and in the ledger, because deferring without a record is how the canon layer went missing in the
first place.

### `CONF-001` settled without a rewrite, and the measurement is the point

Every present-tense construction in chapter 1 was extracted and classified rather than eyeballed.
Fifty-odd are legitimate asides. **Three were event narration in the present**, all in the opening
in-transit passage: *"We are somewhere that is not on any chart"* → *"We were…"*; *"Tonight the shape
it has taken is Delphinus"* → *"That night the shape it had taken was Delphinus"*; *"I am steering
it"* → *"I was steering it."*

Word count 2,398 → **2,399**, re-measured, and the prose gate **re-run: PASS, exit 0, 0 failing rows.**
The option that would have cost a full rewrite is the one that lost. `INTAKE.md` was corrected in
place with the reason recorded, since a user-sourced document losing an argument must not happen
quietly.

## Phase 2.8 — continuity audit, run late

The pre-writing continuity audit was **skipped before drafting and run afterwards**, on instruction.
It is recorded as **late**, not as on schedule and not as never run.

**Scope:** six independent audits (`/continuity-guardian`, Audits 1–6) over `outline.md`,
`foundation.md`, `voice-dna.md`, `ENTITY_STATE.yaml`, `PROJECT_STATE.yaml`, all seven scene packets,
and the drafted chapter 1 — because a contract that contradicts the chapter already written off it is
the most expensive kind of finding to leave sitting.

**Result: 22 findings — 4 CRITICAL, 12 WARNING, 6 MINOR. The 2.8 → 3 gate FAILS**, because the gate
requires zero CRITICAL findings and four are open.

| ID | Finding | Blocks | Status |
|---|---|---|---|
| CRIT-001 | Achird's silence is specified four incompatible ways; the ch.6 packet contradicts its own required elements | ch.5–7 | proposed fix, needs sign-off |
| CRIT-002 | The ending has no author — foundation gives Merope the step, ch.6 gives it to the sleigh while she follows still talking | ch.6–7, and what the ending *means* | **escalated to you** |
| CRIT-003 | ch.4 requires Merope to recognise the ch.3 object, which she was never shown | **ch.3 — the next chapter** | proposed fix |
| CRIT-004 | `PROJECT_STATE.yaml` did not parse — bad indentation put a mapping key under a scalar at line 66 | every phase gate, and Book 2's state load | **fixed this pass** |

### CRIT-004 is the one that should bother you

The primary state file — the thing every gate reads and the thing Book 2 is told to load — **failed to
parse.** Verified with a real parser rather than a grep:

```
$ npx --yes js-yaml validation-series/book-1/PROJECT_STATE.yaml
YAMLException: bad indentation of a mapping entry (66:7)
  65 |     pipeline_gate: "required at pipeline Phases 3 (Drafting), ..."
  66 |       note: "caps are tuned to light-novel narrative register ..."
------------^
  67 |     exempt: "..."
```

`ENTITY_STATE.yaml` parsed clean; only `PROJECT_STATE.yaml` was broken. It had been broken **since
the pipeline-gate decision was written**, which means the earlier claim that the state file had been
updated was never verifiable. That is the failure mode this validation run exists to catch, and it
was sitting in the file that certifies the run. Fixed, and re-verified: exit 0, 21 top-level keys,
29 decisions, phase history now `0 1 2 2/gate_passed 2.5 2.7 2.8/late 3`.

### What the audit did *not* find

Worth as much as the findings, and recorded so the result is not read as a list of problems only.
**Decision C survives intact:** across all seven packets and the drafted chapter, no being states,
hints at, warns about, or approaches the truth; there is no host, no spokesperson, no chase. The
exclusion rule holds (no ledger, no companion who pays, no damaged relationship, no title pattern).
The naming rule holds. Achird's voice card survives contact with prose. Merope does not wink. No
competence cascade. Nobody is damaged. The tension map and structural ledger hold.

### Three more gaps the audit put on the record

These are run-contract failures, not story ones, and none of them had been written down before:

1. **The voice bank has 4 samples against a required 10** (including ≥3 voice-breaking and ≥2
   irrelevant-thought). The missing registers are exactly the ones chapters 2–7 need — ch.6's cruelty
   is a voice-break with no sample behind it.
2. **Phase 1.5 (reader personas) never ran and is absent from phase history**, while Phase 4's
   evaluation is specified as a four-reader simulation with no personas to simulate.
3. **`CANON_LEDGER.yaml` (series and book) and `maintenance/PRUNING_LOG.md` have never been created**
   at either level. Success criterion 5 — "PRUNING_LOG.md records maintenance decisions" — cannot be
   satisfied by a file that does not exist, and `canon.series_ledger` is the exact path Book 2 is
   told to load.

### How the findings were handled

CRIT-004 was fixed immediately, because a file that will not parse is a defect and not a choice. The
rest were held until the user released them, and were then **applied rather than absorbed** — see the
gate-cleared section above for what actually changed in each document. Where a finding was a tone or
story decision rather than a defect (WARN-002, the dread curve) the document still points at the
finding instead of quietly resolving it.

Only the two lines that were factually false were changed: `foundation.md`'s header still said the
Phase 2 gate was awaiting approval, and its movement table still called itself provisional pending a
structural revision that had already been selected.

### Determinations after the report

**CRIT-002 is decided: the sleigh decides and she is carried.** The user's choice from three options.
Merope does not choose to leave, so `foundation.md`'s arc must change while ch.6 and ch.7 stand as
written. Recorded in full at `continuity/outline-audit.md → DETERMINATIONS`.

Consequences worth stating: the theme sharpens rather than weakens — the place kept her from acting
at all, so she is the evidence rather than the exception — and the sleigh becomes the theme's answer,
because the only thing that can move without anyone deciding is what breaks a world built to make
movement unnecessary. The risk carries into ch.7: with no decision, the book can read as fatalism,
and the entire counterweight is the acknowledgement beats, which are two and small.

**Two findings were the agent's own inferred rules, not the user's, and are corrected.** The phrase
"the sleigh saving anyone" in `scene-packets/chapter-07.md`'s forbidden list is the agent's
extension of decision C — only "a chase" traces to the user — and it was then reported as a conflict
with the user's own decision that the sleigh will save someone if it needs to. Likewise, "no bodies,
anywhere, ever" is the agent's wording: the user's rule was scoped to chapter 4's discovery and
protects the absence of **visitor** remains, so a body of a different species never conflicted with
it. Both narrowed at `continuity/outline-audit.md → D-2, D-3`.

**All story-side edits are held.** `foundation.md`'s arc line, the ch.7 forbidden clause, the packets'
remains wording and the CRIT-001 / CRIT-003 fixes are all **unapplied** at the user's instruction. The
resulting contradiction between D-1 and `foundation.md` is recorded deliberately, so the next Phase
5.6 audit finds it flagged rather than discovers it.

## Chapter 1 — prose gate evidence

Required by the gate itself: the command, the exit status, what was scanned, what failed, and the
control run.

```
tools/deslop-check.sh book-1/manuscript/chapters/chapter-01.md
  scanned 1 document (2,398 words), 0 failing rows, exit 0
  D2 rule of three      1.67 per 1k (cap 5)
  D3 -ly adverbs        3.34 per 1k (cap 26)
  P1 anaphora           "i did" x8, 4.3% of sentences (cap 6/1k, 15%)
  P2 duplicates         0 (allowed 1)
  P3 fragment run       3 in a row (cap 6)
  HARD rules            all 0

tools/validate-controls.sh
  human 51 files: 0 failing | slop fixture: FAIL, 17 rows | Coldbrook: 9 of 11 fail
```

**The first pass failed, and the failure was real.** Draft 1 was 1,677 words against a 2,450-word
target and scored D2 at 5.40/1k against a cap of 5. Two of the twelve matches were genuine
rhetorical triads; the rest were ordinary compound sentences. The fix was to **write the missing
700 words and rework the two real triads**, which brought D2 to 1.67/1k. The cap was not touched.

One caveat worth keeping: D2's regex matches any `X, Y, and Z` comma shape, so it also flags normal
sentences carrying an `, and` clause. Read the hits before rewriting them. Recorded in
`tools/calibration/CALIBRATION.md`.

## Phase 3 — all seven chapters drafted

**15,553 words against a 15,000–18,000 target.** Every chapter run through the gate on its own, in
the same session, from the packet that specifies it.

| Ch | Working title | Structure | Movement | Words | Gate | Passes |
|---|---|---|---|---|---|---|
| 1 | arrival | chronological | I | 2,399 | PASS | 3 |
| 2 | the welcome, from two sides | parallel | I | 2,321 | PASS | 2 |
| 3 | she is happy here | spiral | I | 2,358 | PASS | 2 |
| 4 | the belongings | fragmented | II | 2,102 | PASS | 3 |
| 5 | what the beings are | reverse | II | 2,078 | PASS | 2 |
| 6 | the refusal | stream | III | 2,101 | PASS | 2 |
| 7 | leaving, and the acknowledgement | chronological | III | 2,194 | PASS | 2 |

**The gate fired on six of the seven first passes. Every failure was fixed mechanically.**

| Chapter | What failed | What was done |
|---|---|---|
| 2 | D2 rule of three 5.16/1k (cap 5) | five ordinary `, and` compounds rewritten; first-pass material not cut |
| 3 | D2 5.08/1k | four chains broken; one genuine triad reworked |
| 4 | **A18 negative litany** (`Nothing was scattered. Nothing was tipped over.`), D2 **7.00/1k**, P1 anaphora `there was` x13 | litany rewritten, openers varied, ~250 words of missing length written |
| 5 | D2 5.84/1k, 1,712 words | ~370 words written, triads reworked |
| 6 | D2 5.31/1k, then P1 anaphora `I said` x13 | openers varied; monologue extended, not trimmed |
| 7 | D2 5.90/1k, twice | three true triads flattened |

No cap was loosened and no target was cut to make a chapter pass. The two structural failures that
matter are both recorded: **A18 fired for the first time in the project** (ch. 4), and the **P1
anaphora cap is the one that bites hardest on the fragmentary and stream structures** (ch. 4, ch. 6).

Aggregate controls re-run and green:

```
tools/validate-controls.sh
  human 51 files: 0 failing | slop fixture: FAIL, 17 rows | Coldbrook: 9 of 11 fail
  ALL CONTROLS PASS
```

### Two conflicts closed while drafting, not deferred again

`CONF-003` (the beings' answer boundary) was settled in ch. 2 — a being answers only from possession
and present tense, never origin or ownership — and `CONF-004` (the sleigh-and-steed mechanism) in
ch. 7 — the constellation is both the road and the shape, so ch. 1 was already correct and needed no
edit. **That closes the last two open conflicts; all ten are now resolved, with both values kept.**

### One packet instruction was overruled, and recorded

The ch. 5 packet asks for the fact to be *"stated once, flatly, not by a character."* The voice
contract requires the opposite: Merope's wrong reading must be the **only** explicit interpretation
the narrator offers, and she must not state the truth. A draft in which the narrating Merope spelled
out the mechanism in hindsight was cut before the gate. Achird states the fact once instead, in one
sentence, and Merope answers the question she wanted to have been asked.

## Drafted is not finished

All seven chapters are drafted and gate-passing. **None** has been through 3.1 dialogue polish, 3.2
hook craft, 3.5 disruption, 3.8 mechanical preprocess, 4 adversarial audit, 4.5 quality gate, 5
revision, scoring, or a read-aloud — and the prose gate's own output says it is mechanical only, so a
PASS is not a craft verdict. Phase 4 is **blocked**: it is specified as a four-reader simulation and
Phase 1.5 (reader personas) has still never run, so there are no personas to simulate. The voice bank
is still 4 samples against a required 10. Titles remain **DEFERRED** by instruction.

## On disk

```
validation-series/
├── book-1/
│   ├── INTAKE.md                 user-sourced answers + OPEN list
│   ├── ASSUMPTIONS.md            source rule, exclusion rule, content boundary, OPEN
│   ├── PROJECT_STATE.yaml        authoritative state; Phase 2 history + decision log
│   ├── foundation.md             theme, engine, characters, sleigh, structural decisions A/B/C
│   ├── outline.md                7 chapters, structure ledger, tension map, gate checklist
│   ├── voice-dna.md              Phase 2.5 voice contract: global voice, 4 voice cards, matrix
│   ├── ENTITY_STATE.yaml         Phase 2.7 entity state: stable series-wide IDs, knowledge, rules
│   ├── RUN_REPORT.md             this file
│   ├── manuscript/
│   │   └── chapters/
│   │       └── chapter-01.md     2,398 words, prose gate PASS
│   ├── artifacts/
│   │   ├── 00-brief.md
│   │   └── 01-market-map.md
│   ├── references/
│   │   └── tone-references.md    the three supplied works, read and analysed
│   └── scene-packets/
│       ├── chapter-01.md  … chapter-07.md
├── tools/
│   ├── deslop-check.sh           AI-slop scanner; a chapter must PASS it to count as drafted
│   └── calibration/              how the thresholds were measured + the validation controls
├── book-1/references/
│   └── tone-references.md        what was read, and what it changed
└── book-2/                       empty by design (fresh-session target)
```

Also installed, outside the book folder: `.agents/skills/deslopify/` — the third-party rule set
(`github.com/glaforge/deslopify`, grounded in tropes.fyi) that the scan is built from.

**Not yet created** (rebuilt as their phases run): `CANON_LEDGER.yaml` (series + book),
`voice-dna.md`, `ENTITY_STATE.yaml`, `reader-personas.md`, `maintenance/PRUNING_LOG.md`,
`continuity/`.

## Reference reading

Three works were supplied by the user and **read in full** — because every creative decision so far
had been made without knowing the register they were being written in.

- **A — *Wandering Witch: The Journey of Elaina*** (epubs, Vols 1/2/5): POV and register. Vol. 1
  Ch. 1, Vol. 5 Ch. 4 and Ch. 8 read in full, plus complete chapter-title lists for all three
  volumes.
- **B — *Twinstar Cyclone Runaway*** (neocities): tone, texture, the two-girl dynamic. Prologue and
  Chs. 1–2.
- **C — *Shoujo Seikan Hyouryuuki*** (mangafire link): **format** — one conceit per episode, two
  girls, a horse-drawn vehicle, a welcome that is the mechanism of harm. **Chapter 1 read in full,
  44 pages**, retrieved from MangaDex's public API after the linked page proved to be a
  JavaScript shell.

Two corrections were made to earlier notes: I had wrongly merged B and C into a single work, and I
had wrongly claimed I could not read images. Both are corrected in `references/tone-references.md`,
which also records the one thing that cannot transfer — **Elaina winks, and Merope must not.**

## What changed from the torn-down build

The previous run reached Phase 2.8 with a complete architecture. Its **story engine was
Coldbrook Junction's**, not this book's, and it authored character wounds, names, a theme and nine
chapter titles without user consultation. It was deleted at user instruction.

The restart enforces a source rule (`ASSUMPTIONS.md`): facts are user-sourced, gate-approved, or
flagged provisional. **Phase 2 is built with the user at the gate, not before it.**

## What changed in this pass

The reading changed the book, not just the prose. The outline and **all seven scene packets were
rewritten**:

- **The chariot is gone.** It is an old-style sleigh — a glazed enclosed cabin on runners — whose
  steed is drawn from a constellation and **morphs into that constellation's shape**. It is its own
  character and will act on its own to save someone.
- **Structural decisions A/B/C adopted** to separate the book from Reference C: the world was
  expecting them; Achird finds the belongings first and is **not believed**; no host, no
  confrontation, no chase.
- **Titles withdrawn.** All 7 are removed from disk and marked DEFERRED, per your instruction.
- **Tone corrected.** Dread no longer announces itself; movement I must read as genuinely wonderful.

## Prose rule (2026-09-22)

Standing instruction: draft with the humanizer's rules and the tropes.fyi anti-pattern list active,
then **prove it** rather than assert it.

```
bash tools/deslop-check.sh book-1/chapters/chapter-01.md
```

`tools/deslop-check.sh` implements the tropes.fyi categories (word choice, sentence structure,
paragraph structure, tone, formatting, composition) plus four things plain pattern matching
cannot do: **anaphora abuse** (one sentence opener dominating the chapter), **duplicate
sentences**, and **short-fragment runs**. A FAIL means the chapter is not drafted, whatever it
reads like.

**Thresholds recalibrated from published prose (2026-09-22).** Every cap was re-derived from
**175,144 words / 48 narrative documents** of *Wandering Witch: The Journey of Elaina* (Yen Press,
vols. 1/2/5) — the register this book targets — with *Coldbrook Junction* chs. 1–11 as a
native-English control. The earlier caps were guesses, and wrong: the old em-dash cap of 4 per
1,000 words **failed 22 of 48 published chapters** of the reference itself.

The rule *list* was calibrated too, not just the numbers. A phrase stays zero-tolerance only if it
has **0 hits** in that corpus, so `delve`, `tapestry`, `seamless`, `at its core`, `underscoring` and
`experts say` remain hard rules — while `quietly`, `deeply`, `landscape`, `realm`, em-dash
appositives, `in order to` and *Not X. Not Y.* were demoted to density caps, because published
prose does all of them. Also fixed: integer division made every sub-1-per-1,000-word cap
unenforceable, and A20 was failing 100% of published prose by treating curly quotes as slop.

**Validation, both directions.** Elaina: 51 files scanned, **0 failing rows**. The synthetic slop
fixture **FAILS with 17 failing rows**. And *Coldbrook Junction* — a published book from this same
pipeline — **fails 9 of 11 chapters**, on `seamless`/`leverage`, `at its core`, the excluded-engine
guard, duplicate sentences, and rule-of-three density. The scanner rejects the AI-written book and
accepts the human-written one.

**Three bugs found while re-validating that section (2026-09-22).** All three ran in the
permissive direction, which is the only direction that matters for a gate.

1. **The negative control was vacuous.** Directory mode globbed `*.md` only, so the Elaina control,
   which is `.txt`, matched **zero files**, ran no checks, left the failure flag at 0, and printed
   `RESULT: PASS`. The earlier "48/48 PASS" was that pass. The real number on the fixed scanner is
   0 failing rows out of 51 files. An empty scan is now a failure.
2. **The D2 cap came from the wrong corpus.** The rule-of-three worst-document figure of 5.8/1k was
   never a human document: it was Coldbrook chapter 3, read off the AI-written control. The human
   corpus tops out at 3.6, so the old cap of 7 straddled both corpora instead of separating them.
   D2 is now 5/1k.
3. **P3 could never fail.** The short-fragment check printed the opener's second word where its run
   length belonged, so the comparison was always an error and an error is false. It reported `ok`
   for every document ever scanned. Fixing the read-back then exposed a wrong threshold: the
   reference corpus reaches a run of 6, so the cap moved from 6 to 7.

All three are recorded in `tools/calibration/CALIBRATION.md`. `tools/validate-controls.sh` re-runs
all three controls, refuses to report success on an empty scan, and exits nonzero if any control
misbehaves.

**A correction to the earlier record.** This file previously reported the scan as finding "genuine
tells" in Coldbrook: a 10× repeat of *"it was"*, two *Not X. Not Y.*, and a four-sentence fragment
run. Under measured caps all three are **false positives** — published human prose does all of
them. Those were cap errors, not findings, and they are corrected.

Derivation, evidence and the commands to re-derive: `tools/calibration/CALIBRATION.md`.

**Its limits, on the record:** it only sees mechanical patterns. It cannot see a voice, a rhythm, a
dead metaphor, or one argument restated ten ways. Its P2 check false-positives on deliberate
refrains. Passing is necessary and not sufficient.

## Next

**Phase 2 is held at the gate.** The chapters must be approved before drafting.

Runnable without further input: Phase 1 completion (live market research, if wanted) and Phase 1.5
reader personas.

Blocked on you: **approval of the chapter beats in `outline.md`**, plus the OPEN items in
`foundation.md`. Chapter titles are deferred and will not be proposed again until the chapters
exist.
