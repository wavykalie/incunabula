# SESSION LOG — Book 1

**Append-only.** One entry per session, per `.agents/skills/book-genesis-codex/references/maintenance-protocol.md` §4.3:

> Append a session entry with decisions, changed files, facts merged, conflicts, and next step.

`book-genesis/SKILL.md` → *Session Start* step 0 requires reading "recent session entries" at
check-in. Before 2026-09-22 there was no session log, so check-in read nothing and every session
started amnesiac. Entry 001 establishes the format; entries are appended, never rewritten.

---

## 001 — 2026-09-22 — Retrofit of the canon and maintenance layer

**Mode:** REPAIR, then RESUME. (§1: *"state or ledger is malformed, contradictory, or out of sync;
stop before overwriting and report the repair boundary."*)

**Phase at start:** 3 (in_progress) — chapter 1 drafted, prose gate PASS.
**Phase at end:** 3 (in_progress). Phase 2.8 now run late and **FAILING its gate.**

### What was repaired, and why

The project was running with a well-maintained `PROJECT_STATE.yaml` and **no canon layer at all**.
The maintenance protocol is mandated before the first V4 phase; it was never run. Four artifacts were
missing: the series ledger, the book ledger, the pruning log, and any session record. Facts had no
provenance, no `last_verified`, and nowhere to record a conflict.

Additionally, `PROJECT_STATE.yaml` **did not parse** — a mapping key indented under a scalar at
line 66 (`bad indentation of a mapping entry`). It had been that way since the pipeline-gate decision
was written, so every phase gate that claimed to read the primary state file could not have.

### Decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | Instantiate the canon layer as a **retrofit**, recording it as late rather than backdating it | A ledger created today that pretended to have been maintained all along would be the same class of false record the run exists to catch |
| 2 | **`CONF-001` (narration tense) escalated, not resolved** | `INTAKE.md` is user-authority and says present tense; foundation, state and the drafted chapter are past tense. Precedence says the user wins — which would require rewriting chapter 1. Not the agent's call |
| 3 | Do **not** rewrite `INTAKE.md` | User-sourced. Its stale OPEN section and its tense line are flagged `needs_review` in the registry instead |
| 4 | Apply `archive_superseded: true` **as the schema's default, labelled as a default** | Round 4 of the intake was never asked, so there is no user preference to honor. Labelling it prevents a default from hardening into a fake user decision |
| 5 | Record the deleted earlier build as an **unrecoverable loss** rather than omit it | §7: pruning reduces active context, it does not erase history. The erasure already happened; the record of it had to be made |
| 6 | Keep both values on every resolved conflict | §6: resolving preserves provenance. `CONF-006` keeps foundation's contradicted arc line next to the decision that overrides it |
| 7 | Hold all **story-side** edits (CRIT-001, CRIT-003, D-1's foundation change) | User instruction: "hold all story-side edits." Canon-layer repairs are not story edits; the conflicts are recorded and visible instead |

### Changed files

**Created**
- `CANON_LEDGER.yaml` (book scope) — 46 facts, 10 conflicts, 24 registered documents
- `../CANON_LEDGER.yaml` (series scope) — stable entity IDs, series rules, pre-registered Book 2 changes
- `maintenance/PRUNING_LOG.md`
- `maintenance/SESSION_LOG.md` (this file)

**Updated**
- `voice-dna.md` — extended with the chapter-narration and fact-presentation contracts
- `PROJECT_STATE.yaml` — canon pointers corrected, maintenance block added, parse error fixed
- `RUN_REPORT.md` — the skipped-precondition gap recorded
- `continuity/outline-audit.md` — determinations appended

### Facts merged

33 `PROJECT_STATE.yaml` decisions + 10 `ENTITY_STATE.yaml` world rules + all entity entries → 46
facts. No duplicates created; six merges documented in `PRUNING_LOG.md` entry 003. One merge
**corrected the record**: `ENTITY_STATE.yaml`'s knowledge entry for Merope omitted a fact the drafted
chapter establishes (that she heard *"Somebody lost this"*), so the manuscript became the authority.

### Conflicts

**Resolved (4, both values preserved):** `CONF-005` non-visitor remains · `CONF-006` who authorises
the ending · `CONF-007` the rescue clause · `CONF-008` no-remains scope.

**Flagged, unresolved (6):**
- `CONF-001` **narration tense — GATE-CRITICAL, needs a user decision.** Found by the ledger on first build.
- `CONF-002` Achird's silence — blocks ch.5–7
- `CONF-003` the beings' answer boundary — ch.2 is where it is tested
- `CONF-004` sleigh-and-steed mechanism — ch.1's draft reopened the question
- `CONF-009` Achird's "never explains" — ch.1's own dialogue violates it as written
- `CONF-010` the ch.3 object — **blocks ch.3, the next chapter**

### Gate state at end of session

| Gate | State |
|---|---|
| 2.8 → 3 continuity | **FAIL** — 4 CRITICAL: CRIT-001, CRIT-002 (decided, unapplied), CRIT-003, CRIT-004 (fixed) |
| Prose gate, ch.1 | **PASS** — `tools/deslop-check.sh`, exit 0, 0 failing rows |
| 2.5 → 2.7 voice bank | **UNMET** — 4 samples against a required 10 |
| Maintenance check-in / check-out | **NOW RUNNING** — this is the first entry that exists |

### Next step

1. **User decision on `CONF-001`** (narration tense). It is the only finding that can invalidate drafted prose — if present tense wins, chapter 1 is rewritten.
2. **User sign-off on CRIT-001 and CRIT-003**, then apply them plus D-1's foundation change, which clears the Phase 2.8 gate.
3. Then draft chapter 3 — which is currently blocked by `CONF-010`.
4. Outstanding, not blocking: Phase 1.5 reader personas; voice bank to 10 samples; `ENTITY_STATE.yaml` UPDATE pass.

---

## 002 — 2026-09-22 — CONF-001 settled, CRITICALs applied, Phase 2.8 gate CLEARED

**Mode:** RESUME.
**Phase at start:** 3 (in_progress), Phase 2.8 gate FAILING.
**Phase at end:** 3 (in_progress), **Phase 2.8 gate PASSED.** Chapter 3 is unblocked.

### Decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | `CONF-001` RESOLVED as retrospective past tense; the intake's "present tense" loses | The retrospective frame is load-bearing for ch.7's ending, ch.5's reversal and the narrator's hindsight. The reference the intake itself names as governing (Elaina, on POV and register) writes past-for-event with present-for-opinion |
| 2 | **No chapter rewritten.** Three sentences normalized instead | Chapter 1 already complied except at three points in the in-transit passage. Extracting and classifying every present-tense construction showed the three event-narration slips; the other fifty-odd present constructions are legitimate asides. The option that would have cost a rewrite was the one that lost |
| 3 | `INTAKE.md` corrected **in place, with the reason recorded** | A user-sourced document losing an argument must not happen quietly. The original wording is kept struck through |
| 4 | CRIT-001 applied to four packet lines **plus** a per-chapter speech budget in `ENTITY_STATE` | The packets agreed with each other but nothing recorded the rule as one thing, so a renumbering would have reopened it |
| 5 | CRIT-003 applied as "she comes, looks, dismisses" rather than "she never looks" | It satisfies the ch.4 recognition AND makes ch.5's reversal cost her something. The cheaper fix was the better one |
| 6 | D-2 and D-3 follow-through applied even though not named in the instruction | Both were already user determinations with `follow_through_owed` recorded in the ledger. Leaving them would mean the ledger claimed resolved conflicts it had not resolved in the documents |
| 7 | Six WARNINGs **deferred with a named trigger each** | The gate allows deferral. It does not allow silence |

### Changed files

**Manuscript**
- `manuscript/chapters/chapter-01.md` — three in-transit sentences normalized to past. 2,398 to **2,399** words. Prose gate re-run: **PASS**, exit 0, 0 failing rows

**Beat specs**
- `scene-packets/chapter-03.md` — second object is now looked at and dismissed; marked required, not optional
- `scene-packets/chapter-04.md` — remains rule narrowed to visitor remains; shelf constraint names ITM-001/ITM-002
- `scene-packets/chapter-05.md` — silence line, exit pull and required elements aligned
- `scene-packets/chapter-06.md` — no longer contradicts its own required elements
- `scene-packets/chapter-07.md` — silence line, rescue clause narrowed to chase/pursuit/danger
- `scene-packets/chapter-02.md` — chapter is now explicitly **day two**

**Contracts and state**
- `foundation.md` — arc line revised for D-1, Movement III row corrected, warnings 7 and 14 updated, audit header now says GATE CLEARED
- `voice-dna.md` — tense section rewritten as settled, Achird's never-explains narrowed, report allowance added
- `ENTITY_STATE.yaml` — **UPDATE pass**: provenance on every entity, ITM-002 added and shelf renumbered ITM-003, LOC-005 merged and retired, ch.2 and ch.5 timeline entries added, per-chapter speech budget, R-011 and R-012 added, knowledge state corrected
- `INTAKE.md` — tense corrected in place; the stale OPEN items moved to a "Settled since" subsection; the never-asked persistence round recorded as still open
- `PROJECT_STATE.yaml` — gate PASSED, 4 new decisions, word count, maintenance conflicts split into open two / resolved eight
- `CANON_LEDGER.yaml` (both scopes) — statuses updated, resolutions recorded with `follow_through_done`
- `maintenance/PRUNING_LOG.md` — entry 009

### Facts merged

No new duplicate fact IDs. Nine conflicts resolved (both values preserved); two remain open. `series.narration` and `book-1.pov-tense` were the same finding expressed at two scopes, and are now consistent instead of both being marked conflicted.

### Conflicts

**Open (2):** `CONF-003` beings' answer boundary (tested in ch.2) - `CONF-004` sleigh-and-steed mechanism (deferred to the ch.7 pass).
**Resolved (8):** `CONF-001`, `002`, `005`, `006`, `007`, `008`, `009`, `010`.

### Gate state at end of session

| Gate | State |
|---|---|
| 2.8 to 3 continuity | **PASSED** - 0 CRITICAL open, 6 WARNINGs applied, 6 deferred with rationale |
| Prose gate, ch.1 | **PASS** - re-run after the tense edit, exit 0, 0 failing rows |
| Maintenance check-in / check-out | **RUN** - this entry, plus `PRUNING_LOG.md` 009 |
| 2.5 to 2.7 voice bank | still UNMET - 4 samples against 10 |

### Next step

**Draft chapter 3.** Nothing blocks it. Before drafting, read `CANON_LEDGER.yaml -> conflicts` (two open, neither blocking) and `voice-dna.md` (tense settled, Achird's rule narrowed).

Non-blocking, carried forward: `CONF-003` must be settled when ch.2 is drafted; `CONF-004` with the ch.7 pass; `WARN-003` with a ch.1 polish pass; Phase 1.5 personas before Phase 4; voice bank to 10 samples.

### Standing corrections to how this project is run

- **The maintenance check-in and check-out are now phase gates** (see `book-genesis/SKILL.md` and `references/pipeline/`). A skipped precondition has to be recorded as skipped, the way Phase 2.8's was.
- **No phase may report progress on the strength of a state file that has not been parsed.** `PROJECT_STATE.yaml` was unreadable for an unknown part of this project's life and nothing noticed.

---

## 003 — 2026-09-22 — Phase 3 completed; all seven chapters drafted

**Mode:** RESUME. Phase at start: 3 (in_progress). **Phase at end: 3 (completed).**

### Decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | Draft chapters 2-7 from the scene packets, in packet order | User instruction: *"Draft all the remaining chapters, following the rubric."* |
| 2 | `CONF-003` **resolved** while drafting ch.2 — a being answers only from possession and present tense, never origin or ownership | The ch.2 packet requires a being to be asked directly about a dead visitor's object and to answer with no pause. The schema's proposed boundary was applied rather than re-proposed |
| 3 | `CONF-004` **resolved** while drafting ch.7 — the constellation is both the road and the shape | Ch.7 requires a new shape as the sleigh goes; ch.1 already showed the old shape drifting loose while the sleigh sat. Under this reading ch.1 needed no edit |
| 4 | The ch.5 packet's *"stated once, flatly, not by a character"* **loses to the voice contract** | voice-dna requires Merope's wrong reading to be the only explicit interpretation the narrator offers, and ENTITY_STATE requires that she not learn or state the truth. A draft had her spell out the mechanism in hindsight; that was cut, and Achird states the fact once instead |
| 5 | Every gate failure fixed **mechanically**, never by loosening a cap | Standing rule since ch.1. It held for all six chapters here |

### Changed files

- `manuscript/chapters/chapter-02.md` … `chapter-07.md` — **created** (six new chapters)
- `CANON_LEDGER.yaml` — `CONF-003` and `CONF-004` moved to resolved with `follow_through_done`; `flagged_conflicts` empty; resolved list to ten
- `ENTITY_STATE.yaml` — `COL-001.answer_boundary` resolved, `OBJ-001.steed_conflict` closed, timeline and item statuses `planned` → `drafted`, knowledge state ch.2-5 `drafted`
- `PROJECT_STATE.yaml` — seven chapters recorded with word counts and gate evidence, Phase 3 moved to completed, four new decisions, maintenance conflicts to ten resolved / zero open
- `maintenance/PRUNING_LOG.md` — entry 010

### Facts merged

No new duplicate IDs. The two remaining open conflicts were closed. Two **new** determinations were made that the packets did not cover, both recorded as decisions rather than left implicit: the ch.5 voice-contract precedence, and the ch.7 steed handover.

### Conflicts

**Open (0).** **Resolved (10):** all of them. `CONF-003` and `CONF-004` closed this session, with both competing values preserved in the ledger.

### Gate state at end of session

| Gate | State |
|---|---|
| Prose gate, ch.1-7 | **PASS** — each chapter run on its own, exit 0, 0 failing rows. Six fired on the first pass and were fixed, not waived |
| Three-control validation | **PASS** — 51 human docs 0 failing; slop fixture FAIL 17 rows; Coldbrook 9/11 FAIL |
| 2.8 to 3 continuity | PASSED (earlier session) — unchanged |
| Maintenance check-in / check-out | **RUN** — this entry, plus `PRUNING_LOG.md` 010 |
| 2.5 to 2.7 voice bank | still UNMET — 4 samples against 10 |
| Phase 4 adversarial audit | **BLOCKED** — Phase 1.5 reader personas still do not exist |

### Next step

**Phase 1.5 (reader personas), then Phase 2.9/4 adversarial audit.** Drafting is done; evaluation has not begun. No chapter has had a read-aloud, the Phase 5 quality gate, the Phase 5.6 manuscript continuity pass, a revision cycle, or scoring. The prose gate is mechanical only.

Non-blocking, carried forward: `WARN-003` with a ch.1 polish pass; voice bank to 10 samples; the two open story questions (how long they had been there when the shelf was found; whether anything else is alive on the planet). Titles remain DEFERRED, as instructed.

---

## 004 — 2026-09-22 — Book 1 closed: Phases 1.5, 4, 5.6, 6 and 7 all run

**Mode:** RESUME, then CLOSE.
**Phase at start:** 3 (gate_pending). Phase 4 **BLOCKED** on Phase 1.5, which had never run.
**Phase at end:** 7 (completed). **Book 1 is closed.**

### The headline, and it is the reason this run existed

**Phase 5.6 had never run. Running it found 2 CRITICAL defects in prose that had already passed the
prose gate on all seven chapters.**

| ID | Defect | Fix |
|---|---|---|
| `CONT-001` | ch.7 asserted a shelf act no chapter shows, and gave Achird an act ch.4 assigns to the beings | clause removed; wording preserved verbatim in `CANON_LEDGER.yaml → chapter_07.departure_act.supersedes` |
| `CONT-002` | ch.7 stated Achird's hand-taking as "the second time in her life"; the manuscript shows three earlier | `second` → `fourth` |

The scanner checks sentence shape, adverb density, anaphora and negative litany. It cannot check
whether a character was in the room. **7-for-7 on the gate is not a continuity result**, and this
project now has a worked example of the difference rather than an assertion about it.

### Decisions this session

| # | Decision |
|---|---|
| 1 | Ran Phase 1.5 for the first time (3 personas + a simulated casual reader). It had been blocking Phase 4 the whole time. |
| 2 | Fixed `CONT-003` (ch.5 discovery day), `CONT-004` (ch.3's word **"packet"** — pipeline vocabulary in the narration; the word a hostile reader would have caught), `CONT-005` (`WARN-003`, whose named trigger had fired), `CONT-008`/`CONT-009` (state: `ITM-001`'s stale form; the untracked strap-end, new `ITM-004`). |
| 3 | Reported and did **not** change 4 findings: `CONT-006`, `CONT-007`, `CONT-010`, `CONT-011`. Two are prose judgement calls, one is a contract-versus-draft disagreement, one is a resonance question. |
| 4 | Phase 5 recorded **NOT ACTIVATED** — its activation condition is a user quality target and none has ever been set. Running it against a self-chosen target would be the pipeline declaring its own success condition. |
| 5 | Voice bank closed 4 → **10 of 10** (`WARN-009`), late, after drafting, recorded as late. |
| 6 | Scored 7.7 composite; weakest lens pacing 7.0. Commercial viability scored **low on launch (4.5)** with the reason stated: the horror-adjacent reader abandons at ch.3. |
| 7 | Built the EPUB with the Python standard library only. No Calibre, no pandoc, no install. |
| 8 | Invented **no** title, author name, or physical description for the build. The deferral is carried, not filled. |

### Changed files

`PROJECT_STATE.yaml` · `ENTITY_STATE.yaml` (2nd UPDATE pass) · `CANON_LEDGER.yaml` (book: +6 facts,
+8 documents, 3 superseded values preserved) · `../CANON_LEDGER.yaml` (series: book-1 complete) ·
`voice-dna.md` (voice bank) · `reader-personas.md` **(new)** · `continuity/manuscript-audit.md`
**(new)** · `continuity/adversarial-audit.md` **(new)** · `artifacts/05-barrier-note.md` **(new)** ·
`artifacts/06-scorecard.md` **(new)** · `artifacts/07-editorial-package.md` **(new)** ·
`tools/build-epub.py` **(new)** · `dist/merope-book-one_WORKING-TITLE.epub` **(new)** ·
`manuscript/chapters/chapter-01,03,05,07.md` (4 fixes) · `maintenance/*`

### Facts merged

`merope.hand_taking_count` (4, load-bearing) · `world.stay_scale` (weeks, decided *by the prose*, not
by a decision — `CONT-007`) · `chapter_07.departure_act` · `item.ITM-004` · `world.name_refusal` ·
`voice_bank.status` · `series.book-1.completed`.

### Conflicts

**None new. Zero open.** All ten remain resolved, including the two settled during drafting.

### What is still not true, stated plainly

- **Phase 5 has never run.** There is no calibrated lens score for this book, only a self-assessment that says so.
- **The cover-the-name exercise has still not been performed** against the drafted chapters.
- **No chapter has been read aloud.** The gate says so itself: *"mechanical only — read it aloud before calling it clean"*, and that has not happened.
- **Six author items are open** (`AUTH-1..AUTH-6`), including every title and both leads' appearance.
- **The launch score is 4.5.** The book is finished-and-ready-to-be-targeted, not finished-and-ready-to-sell.

### Next step

**Book 2, in a fresh session, loading only from disk.** The resume test is the last unmet success
criterion and it is the one that decides whether this whole layer works. Book 2 must recognise
`CHR-001`/`CHR-002` and the voice contracts from the series ledger, treat its two pre-registered
changes (`series.book-2.scoped-change`) as legitimate rather than as contradictions, and flag any
*other* departure from a series-scoped fact.

---

## 005 — 2026-09-22 — The two escalated prose items closed (`AUTH-1`, `AUTH-2`)

**Mode:** RESUME. Phase unchanged (7, completed). Book 1 remains closed.
**Trigger:** user instruction to close the two items Phase 4 had escalated.

### Outcome

| Item | Resolution | Words |
|---|---|---|
| `AUTH-1` — ch.6's cruelty line exceeded its own speech budget | **REWRITTEN.** 30 words in a single triple-clause → 20 words in two clipped sentences. ch.6 re-gated **PASS** | 2,101 → 2,089 |
| `AUTH-2` — restore Achird's shelf act, or leave it removed | **LEFT REMOVED**, and the reason upgraded from *unshown* to **geographically impossible** | — |

### Why the contract won, and it is not a matter of taste

Merope's `speech_budget.ch_6` says: *boastful, then **one short accurate line** delivered quietly;
sentences get LONGER before she gets cruel.* The drafted line was the **longest thing she said in the
whole chapter** — the exact inverse. The rewrite keeps both of its moves (the accusation, then the turn
on her for the consequence) and moves the length out of the dialogue and into the narration around it,
which is where the swelling already was and what Merope actually does: she explains herself *after* the
damage.

```
- "You have been standing beside me for years, and you have never once told me a single thing you
-  wanted, and now you are angry at me for not hearing it."
+ "You never once told me what you wanted. And now you are angry at me for not hearing it."
```

Epitaph for the entry: **this is the only finding in the entire project that a CONTRACT caught rather
than a reader.** The machine-readable speech budget is why.

### `AUTH-2`: investigating the fix produced a better answer than the finding

The original finding was that the clause was *unsupported*. Investigating whether to show it instead
proved it was **impossible**:

- the shelf is in the **camp** — *"out past the far edge of the growth"*, *"over a low rise and down
  into a place I had not seen"* (`chapter-04.md:5,15`);
- the departure happens in the **clearing**;
- and `chapter-06.md` holds Achird physically still for the entire confrontation (*"She stood there."*,
  *"She said nothing."*), so she never leaves and comes back.

So the act could not have happened when ch.7 said it did (*"she had **just** done the thing"*).
Showing it in ch.6 as first proposed would have required the shelf to be in the clearing. **Removal is
therefore the correct resolution, not the cautious one.** The beat, if wanted, belongs at Phase 2 as an
earlier scene — Achird going up to the camp alone — and is recorded so it is not lost with the clause.

### Changed files

`manuscript/chapters/chapter-06.md` · `dist/merope-book-one_WORKING-TITLE.epub` (rebuilt) ·
`ENTITY_STATE.yaml` · `CANON_LEDGER.yaml` (+`merope.cruelty_line`, geography evidence on
`chapter_07.departure_act`) · `PROJECT_STATE.yaml` · `continuity/manuscript-audit.md` (addendum) ·
`continuity/adversarial-audit.md` · `artifacts/05-barrier-note.md` · `artifacts/06-scorecard.md` ·
`artifacts/07-editorial-package.md` · `RUN_REPORT.md` · `../CANON_LEDGER.yaml` · `../README.md`

### Facts merged

`merope.cruelty_line` (with the superseded 30-word version preserved) · a second source added to
`chapter_07.departure_act` recording the geography.

### Conflicts

**None new. Zero open.** `PROBE-001` remains the only open conflict in the project and it belongs to
Book 2.

### Verification

All seven YAML files parse · all seven chapters PASS the gate · controls re-run green · EPUB rebuilt
and structurally verified (14 entries, mimetype first and stored, 12 XML files well-formed, the rewrite
present and the removed clause absent) · manuscript **15,531 words** · every stale 15,543 reference
reconciled.

### Still not true

No chapter has been read aloud. Phase 5 has never run. The cover-the-name exercise has not been done.
`AUTH-3`..`AUTH-6` remain open — including every title. The launch score is still 4.5.

### Next step

Unchanged: **Book 2**, and it is still blocked on the author's engine choice.

---

## 006 — 2026-09-22 — `AUTH-5` closed: both leads' appearance is author-decided canon

**Mode:** RESUME. Phase unchanged (7, completed). Book 1 remains closed.
**Trigger:** the author supplied physical descriptions for both leads.

### What was decided

| | Merope (`CHR-001`) | Achird (`CHR-002`) |
|---|---|---|
| Hair | white, in **twin tails** | **crimson**, scorpion-like |
| Clothing | a **celestial-themed Lolita dress** | a **hoodie designed after nuclear superbubbles** |
| Figure | not flat-chested | **flat-chested** |

Recorded at **series scope** (`start_book 1, end_book 99`) — appearance is stable across installments,
so Book 2 inherits it and does not get to redesign it.

### Checked against the prose BEFORE recording, and it is clean

Grepped all seven chapters for *hair, hoodie, dress, cloak, chest, tall, short, crimson, red hair*.
**The manuscript describes neither lead physically anywhere in 15,531 words.** The only hits are
incidental — *"moved it a hair to the left"*, *"not short of material"*, *"dress it up"*. So this is
new canon with **no conflict to reconcile**, and one small piece of support: ch.3's *"I sat on the
bench and did my hair without a mirror, which I can do"* is consistent with twin tails, which are a
style you can do by feel. The style is not stated in the prose.

### Four things deliberately NOT resolved

A guess in a design brief becomes a drawing, and a drawing becomes canon. So the gaps were left
visible, in `ENTITY_STATE.appearance.wording_flags` and `artifacts/character-design-brief.md`:

| # | Item | State |
|---|---|---|
| `APPEAR-1` | Merope's chest — the word given was **"boasty"** | **not guessed at.** Two plausible readings, either would be an invention. Recorded only as *not flat-chested*. |
| `APPEAR-2` | Achird's **"scorpia like"** hair | colour explicit; **shape undecided** — a scorpion-tail braid, a swept asymmetric cut, and a full scorpion silhouette are three designs |
| `APPEAR-3` | Achird's hair and **SCORPIUS** | **raised, not decided.** Ch.7 sends them out of Book 1 riding Scorpius. If her hair is scorpion-*shaped*, the constellation echoes the person who got them out — either the best detail in the series or a coincidence readers will over-read. **Nothing in the prose was changed on the strength of it.** |
| `APPEAR-4` | the hoodie's **"nuclear superbubbles"** | read as the real feature — nested limb-brightened shells blown by supernovae and stellar winds — and **labelled as this run's reading**, not an author statement |

### Consequences

1. **The cover brief's blocking constraint is lifted.** Section 4 of the editorial package is rewritten:
figure illustration is now legitimate, and the object cover is now a *choice* rather than a necessity.
The genre warning survives it — a figure cover pulls the horror-adjacent reader to the documented ch.3
abandonment.
2. **A new artifact:** `artifacts/character-design-brief.md`, the illustration-facing view of the canon.
3. **The prose position is now recorded.** With appearance canon, the manuscript's total silence about
both bodies becomes a position rather than an omission. Making the prose describe them is a change to
the narrator contract and needs its own decision.
4. **The EPUB was NOT rebuilt, and correctly so** — no prose changed. The appearance decision is
illustration and packaging canon; the manuscript is byte-identical to the build from session 005.

### Changed files

`ENTITY_STATE.yaml` (+`appearance` block) · `CANON_LEDGER.yaml` (**~`merope.appearance`,
~`achird.appearance` — see the correction below**, +1 registered document) · `PROJECT_STATE.yaml` (+2 decisions, +1 deliverable) ·
`artifacts/07-editorial-package.md` (cover brief §4) · `artifacts/06-scorecard.md` ·
`continuity/adversarial-audit.md` · `artifacts/character-design-brief.md` **(new)** ·
`../README.md` · `../book-2/ENTITY_STATE.yaml` · `../book-2/ASSUMPTIONS.md` · `../book-2/RUN_REPORT.md`

### Correction, same session — a defect this entry's own wording caused

This entry originally said `CANON_LEDGER.yaml` gained `merope.appearance` and `achird.appearance` as
**new** facts. It did not: **both already existed**, at `status: uncertain / authority: inference`,
recording appearance as *deferred*. Treating them as new meant writing **duplicate mapping keys**, and
the ledger stopped parsing:

```
YAMLException: duplicated mapping key (828:3)
  828 |   merope.appearance:
```

**Caught by the parser, not by rereading the edit** — which is the argument for running one. Fixed
properly: the two existing facts are now **updated in place** to `status: active / authority:
user_decision`, the old `UNESTABLISHED` value is preserved in their `supersedes` array, and the
duplicates are gone. Re-verified: ledger parses, exactly one `merope.appearance` and one
`achird.appearance`, 53 facts, 33 documents, 10 conflicts.

Recorded rather than smoothed, because it is the same failure the whole validation run exists to
catch: **adding a new record instead of reconciling an existing one.** A fact marked `uncertain` is
still a fact, and a second entry recording the same thing is not an update.

### Conflicts

**None new. Zero open** in Book 1. `PROBE-001` remains the only open conflict in the project, and it
belongs to Book 2.

### Gate and verification

All seven YAML files parse · 7/7 chapters PASS · controls green · manuscript 15,531 words, unchanged,
so the EPUB was **not** rebuilt and is current · every stale `AUTH-5` claim reconciled.

### Still not true

No chapter has been read aloud. Phase 5 has never run. `AUTH-3` (ch.5 reverse-frame wording; the two
straps), `AUTH-4` (every title) and `AUTH-6` (the *weeks* scale) remain open. `APPEAR-1`..`APPEAR-4`
are open by design. The launch score is still 4.5.

### Next step

Unchanged: **Book 2**, still blocked on the author's engine choice.

---

## 007 — 2026-09-22 — the appearance wording flags closed; AUTH-5 fully done

**Mode:** RESUME. No phase transition. Phase remains 7 (complete) for Book 1; Book 2 remains blocked
on the engine choice.

### Decisions

| # | Decision | Authority |
|---|---|---|
| 1 | `APPEAR-1`: the author's word "boasty" means **busty / full-figured**, and it is a stated deliberate contrast with Achird | author |
| 2 | `APPEAR-2`: Achird's hair is a **scorpion-tail braid** — one long crimson tail curving like a scorpion's tail | author |
| 3 | `APPEAR-3`: the braid and ch.7's **Scorpius** are a **coincidence, and the author likes it.** Not a designed resonance | author |

### Why decision 3 is recorded with three consequences rather than one sentence

"Coincidence" is not self-enforcing. Left as a bare note, it becomes three different things later,
and each one is a continuity defect waiting to happen. So it is written down as: **not seeded** into
Book 2's design language, **not remarked on** in either book by anyone, and **not changed** to avoid
the read. The ch.7 ending and the hair shape stay exactly as drafted. A reader who connects them is
over-reading, and that outcome is intended.

### Not done, on purpose

- **No prose changed.** The manuscript is 15,531 words before and after, so the EPUB is **not**
  rebuilt and the existing `dist/` build is still current. Verified, not assumed.
- `APPEAR-4` ("nuclear superbubbles") was **not** asked about again. The phrase is unambiguous in
  astronomy and was already recorded as a reading; it is re-labelled low-risk but still the **only**
  appearance item resting on this pipeline's inference instead of an author decision.

### Reconciled, not appended

The same trap as entry 006. `merope.appearance` and `achird.appearance` already existed in both
`ENTITY_STATE.yaml` and `CANON_LEDGER.yaml`, so the resolutions were written **into those records**
(losing the superseded wording to nothing — it stayed in the file) rather than pushed as new facts.
Asserted separately: `grep -c` for each fact key returning exactly 1 in the ledger.

### Files changed

`book-1/ENTITY_STATE.yaml`, `book-1/CANON_LEDGER.yaml`, `book-1/artifacts/character-design-brief.md`,
`book-1/artifacts/07-editorial-package.md`, `book-2/ASSUMPTIONS.md`, this file.

### Still not true

Unchanged from 006: no chapter read aloud; Phase 5 never activated; `AUTH-3`, `AUTH-4`, `AUTH-6` open;
launch score 4.5; `PROBE-001` still open in Book 2.

### Next step

Unchanged: **Book 2**, blocked on the author's engine choice.

---
