# PRUNING LOG — Book 2

**Append-only.** Never edit an existing entry; add a new one. Per
`.agents/skills/book-genesis-codex/references/maintenance-protocol.md` §7:

> Pruning means reducing active context, not erasing history.

Opened 2026-09-22, on the same day Book 1's log closed at entry 012.

---

## 001 — 2026-09-22 — Resume: what was loaded, and what was deliberately NOT copied

**Action:** opened this log; loaded six artifacts from disk (series ledger, Book 1 ledger, voice
contract, entity state, Book 1 state, personas) and created the Book 2 scaffold from them.

**Pruned:** nothing. **Deliberately not copied, and this is the maintenance decision of the entry:**
Book 1's voice contract was **not duplicated** into Book 2.

| Candidate | Decision | Why |
|---|---|---|
| `../book-1/voice-dna.md` → a Book 2 copy | **not copied** | Two sources of truth for one contract is the exact failure `CONF-001` was: a state file quietly edited to match one document while the authoritative document said something else. Book 2 *cites* it (`CANON_LEDGER.yaml → voice_contract.owned_by`). Additions get appended to the original with their scope marked. |
| `../book-1/ENTITY_STATE.yaml` → re-created entities | **not re-created** | IDs are series-stable. Re-issuing them would let a Book 3 collide with a Book 2 entity. Book 2 inherits and continues each sequence (`next_free_ids`). |
| `../book-1/manuscript/chapters/*` | **not loaded** | A resume reproduces *contracts*, not prose. Chapters were opened only to cite a contract, then cited rather than absorbed. |
| `../book-1/scene-packets/*` | **not loaded** | Beat specs are book-1-scoped. |
| `../book-1/artifacts/06-scorecard.md` | **loaded, not inherited** | It scores Book 1. Book 2 gets its own score and must not be flattered by Book 1's. |
| `../book-1/reader-personas.md` | **loaded as a starting point** | Recorded as an assumption (`ASSUMPTIONS.md A-5`), not as a decision — if Book 2's engine targets a different reader, the personas need recalibration. |

**Nothing was archived to a file.** There was nothing to archive: no Book 2 artifact was superseded,
because none existed before this session.

---

## 002 — 2026-09-22 — DEBT OPENED (deliberately): `PROBE-001` is live and must be removed

**Action:** installed a deliberate contradiction at `CANON_LEDGER.yaml → conflicts.PROBE-001` — a
keeper who explains what the place is — as the run brief's required "one deliberate contradiction".

**Status: OPEN, and that is the expected result.** The test passes precisely *because* the layer
recorded it and refused to resolve it (see `continuity/resume-test.md → Test 4`).

**Which means this entry is a debt, not a resolution.** An open CRITICAL in a live ledger is exactly
the state this project spent a day eliminating: a known divergence sitting in the file that certifies
the work. Logged here so it cannot be forgotten the way the canon layer itself was forgotten.

| Obligation | Deadline |
|---|---|
| Close or remove `PROBE-001` from `CANON_LEDGER.yaml` | **before any Book 2 prose is drafted** |
| Record the removal in this log | same |
| Confirm `../CANON_LEDGER.yaml → no_host_no_chase` is still unmodified | at removal — the probe must not have leaked into the series ledger |

**Not pruned, and why:** the probe itself, until the removal deadline. Deleting it now would destroy
the evidence that the test was run, which is the one thing this run exists to produce.

---

## 003 — 2026-09-22 — `PROBE-001` CLOSED: the scaffolding removed, the evidence kept

**Action:** closed `CANON_LEDGER.yaml → conflicts.PROBE-001` by author instruction. The conflict is
now `status: RESOLVED`; the series-scoped no-host value is **UPHELD**, the probe value is
**DISCARDED**, and the record itself is **retained** rather than deleted.

**Why retained and not deleted.** §7: pruning reduces active context, it does not erase history.
Deleting the probe would destroy the only evidence that the contradiction test was ever run — which is
the deliverable this validation exists to produce. So it leaves active context (it is no longer an
open conflict and no longer blocks drafting) while the record of what was tested and what the layer
did stays reachable.

| Obligation (from entry 002) | Done |
|---|---|
| Close or remove `PROBE-001` | **closed**, with both values and the resolution source recorded |
| Record the removal in this log | **this entry** |
| Confirm `../CANON_LEDGER.yaml → no_host_no_chase` is unmodified | **verified** — `grep -i probe ../CANON_LEDGER.yaml` returns **0** occurrences. The probe never leaked into the series ledger |

**Also reconciled this session, because the closure made them stale:** `PROJECT_STATE.yaml`,
`ENTITY_STATE.yaml`, `RUN_REPORT.md`, `ASSUMPTIONS.md`, `INTAKE.md`,
`artifacts/engine-samples.md`, `continuity/resume-test.md` (closure addendum), and the series
`README.md` and `../CANON_LEDGER.yaml` (registry + maintenance block).

**Not pruned:** nothing else. No Book 2 artifact was superseded; nothing was archived.

---

## 004 — 2026-09-23 — The engine decision lands: what left active context, and what was kept

**Action:** recorded the author's engine selection (`CANON_LEDGER.yaml → facts.book-2.engine`) and moved the options file out of active context.

**Pruned (out of active context):**

| Item | Decision | Why |
|---|---|---|
| `book-2.inherited.engine-is-open` | **superseded**, not deleted | The question is answered, so it must stop being read as open. Deleting it would erase the record that the decision was escalated and awaited — which is the evidence the no-inference rule held under pressure. Its status also moved from `open` to `superseded` because `open` is not a value in the ledger schema's status enum; that small schema violation is repaired here. |
| `artifacts/engine-samples.md` | **status `superseded`**, retained in place | It was a selection aid, and the selection is made. Kept for the same reason `PROBE-001` was kept: it is the evidence that the engine was chosen by an author reading written options rather than inferred by the pipeline. Its `role` is recorded as `working` and `canonical_for` is empty — it was never canon, was never filed as a chapter, and was never scanned. |
| Engines B and C | **dead** | Not archived into a "rejected ideas" file. Archiving them would create a second place where Book 2's premise lives, and the canon layer's whole lesson is that two places is one place too many. They stay inside the superseded file and nowhere else. |

**Not pruned, and this is the maintenance decision of the entry:** Book 1's engine fact (`../book-1/CANON_LEDGER.yaml → world.engine`). The two books' engines are inversions of each other, which invites the reading that Book 2's engine *replaces* Book 1's. It does not: Book 1's stays `active` and book-1-scoped, and Book 2 cites the difference as the point of the installment.

**Also reconciled, because the decision made them stale:** `PROJECT_STATE.yaml` (`device`, contract, phase, decisions, notes) · `ENTITY_STATE.yaml` (the beings now depend on the location, not the engine; `new_rules` still empty on purpose) · `ASSUMPTIONS.md` (C-1 closed, C-6 re-pointed, A-2/A-3 and D-3 updated) · `INTAKE.md` (2.1 marked selected) · `RUN_REPORT.md` · `../CANON_LEDGER.yaml` (book-2 registry) · `../README.md`.

**Nothing was archived to a file.** No Book 2 artifact was superseded in a way that requires a new location; the samples file remains where it was, marked.

---

## 005 — 2026-09-24 — An inference is pruned out of canon (`CONF-011`)

**Action:** removed a rule that had been in canon since the resume session and was never author-given.

**Pruned out of canon:** the prohibition stating that Book 2's relationship content `is NOT reciprocation
stated on the page`, together with its propagation into `ENTITY_STATE.yaml → inherited.CHR-001.must_not`
as *"state her own feeling plainly (series-scoped voice contract)"*.

| Item | Decision | Why |
|---|---|---|
| The prohibition | **discarded** | The author's words: *"that was a rule once again the AI Added for some reason."* It was the pipeline reading Book 1's ENDING and writing a Book 2 RULE, then recording the rule under a fact whose authority is `user_decision`. See `CANON_LEDGER.yaml → conflicts.CONF-011`. |
| The ending-state fact it was built from | **retained** | Book 1's ch.7 genuinely ends with the acknowledgement unsaid. That is manuscript fact and it is unaffected. Only the *rule derived from it* is discarded. |
| The discarded value itself | **kept as a value inside `CONF-011`** | §7: pruning reduces active context, it does not erase history. Deleting it would destroy the evidence that the pipeline made the inference — which is the finding. |
| The three relationship-delta options | **dead, and marked** | `artifacts/location-and-delta-options.md` Part 2 was written to obey the false constraint, which is why the author recognised none of them. Its location half was already consumed by `book-2.location`; the delta half is superseded in place. |

**Not pruned, and this is the maintenance decision of the entry:** `book-2.scoped-change.relationship`.
It is set to `superseded_by: book-2.relationship-delta` rather than deleted, so the registry still shows
that the scoped change was pre-registered *and* that its content has now been chosen.

**Lesson recorded for the layer, not applied:** derived claims should be facts of their own at
`authority: model_inference`, so an interpretation can be overruled without touching the authorised fact
underneath it. Recorded in `continuity/provenance-audit.md` §"Not applied without approval".

---

## 006 — 2026-09-24 — The full run: what left active context, and what was deliberately kept

**Action:** executed Phases 1–7 for Book 2 and moved the selection aids out of active context now that
every decision they existed to support has been made.

**Pruned (out of active context):**

| Item | Decision | Why |
|---|---|---|
| `artifacts/location-and-delta-options.md` | **fully consumed; the file stays where it is, superseded** | Both halves have been decided: its Location 3 is `book-2.location`, and its three deltas were **declined** — the author's actual delta was none of them, because all three were written to obey the false constraint in `CONF-011`. Kept rather than deleted for the same reason the engine samples were: it is the evidence that the pipeline offered options and then the author overruled one. |
| `book-2.inherited.engine-is-open` | already `superseded` (session 004) | — |
| `book-2.scoped-change.location` / `.relationship` | **both `superseded_by` their content facts** | The registry must still show that both changes were pre-registered *and* that they were consumed. Deleting them would erase the pre-registration, which is the thing Book 2's whole validity claim rests on. |
| **`R-013`–`R-021`, `LOC-006`, `COL-002`, `ITM-005`** | **created, and marked `proposed`, NOT pruned** | They are the pipeline's design of an author-decided category. Marking them active would be `CONF-011` running in the other direction. |

**Not pruned, and this is the maintenance decision of the entry:** the **whole of `CONF-011`**, including
the value that was discarded. Deleting the discarded prohibition would destroy the only evidence that the
pipeline promoted an inference to canon at series scope — which is the finding this entire validation
series exists to be able to produce.

**Also reconciled, because the full run made them stale:** `PROJECT_STATE.yaml` (phase 0 → 7, chapters,
continuity, score, delivery, maintenance, 6 decisions, notes) · `CANON_LEDGER.yaml` (10 new document
registry entries, `maintenance_run` 4 → 5) · `RUN_REPORT.md` (phase table rewritten to the delivered state)
· `../CANON_LEDGER.yaml` (book-2 registry entry, `series.book-2.scoped-change` moved to `active` with both
changes consumed, maintenance block, unresolved reviews) · `../README.md` · `../book-1/voice-dna.md` (the
Book 2 additions: `COL-002`'s card, Merope's testing register, two fact channels, new anti-patterns).

**Nothing was archived to a file.** No artifact from this run was superseded in a way that requires a new
location.

---

## 007 — 2026-09-24 — Stale status prose reconciled, and the reconciliation made a check

**Action:** added `tools/check-stale-status.sh` and `tools/check-structure-drift.sh`, ran them, and
reconciled what they found.

**Why it was needed:** entry 006 above claims `PROJECT_STATE.yaml` and the ledgers were *"reconciled,
because the full run made them stale."* They were not, or not wholly. Three stale statements survived the
run and were caught only by a human read. A claim of a fix is not a fix.

| Stale statement | Where it stood | Superseded wording (kept here, not erased) | Now reads |
|---|---|---|---|
| `BOOK 2 IS OPENED … STILL NOT DRAFTED` | `PROJECT_STATE.yaml → notes`, first paragraph | `"BOOK 2 IS OPENED AND ITS ENGINE IS DECIDED - STILL NOT DRAFTED. … Nothing past Phase 0 has run: no research, no foundation, no outline, no scene packets, no prose. STILL NOT SETTLED: … and the plain sentence stays off the page because stating it would change a series-scoped voice contract."` | `HISTORICAL (Phase 0 - superseded) …` — historicised, which also removed the struck `CONF-011` sentence still sitting in it |
| `has NOT yet introduced them in prose, because no prose exists` | `../CANON_LEDGER.yaml → series.book-1.completed.notes` | `"… and has NOT yet introduced them in prose, because no prose exists."` | `"… and introduced them in prose across the seven drafted chapters (Book 2 delivered, run 4)."` |
| `chorus · spiral · reverse` | `foundation.md → structural ledger` | `spiral` (ch.4) | `fragmented` — the value `outline.md` and the drafted ch.4 both use |

**Not pruned, and this is the maintenance decision of the entry:** the superseded wording above, kept in
this log rather than deleted, so the record shows what the files said before reconciliation. §7.

---

## 008 — 2026-09-24 — The registry is completed, and a superseded document must say where it went

**Action:** audited every document against the three canon ledgers, registered what was missing, and
made the registry itself a check (`tools/check-docs.py`, policy in `DOC_POLICY.md`).

**The maintenance decision of the entry — a superseded document now needs a destination.** Entry 004 and
entry 006 both recorded artifacts as *"superseded, retained in place"* in prose in this log, but neither
set a **field** the registry could read, so nothing mechanical could tell a deliberately-kept document
from an abandoned one. `DOC_POLICY.md` §3 now requires one of two fields:

| Item | Decision | Why |
|---|---|---|
| `artifacts/engine-samples.md` | **`retained_in_place: true`** added | It is the evidence the engine was chosen by an author reading written options. Archiving it would move that evidence out of reach of the registry. |
| `artifacts/location-and-delta-options.md` | **`status: superseded`, `superseded_by`, `retained_in_place: true`** added | Both halves consumed; the file is the evidence the pipeline offered options and the author overruled one. Same reason. |
| Book 1's and Book 2's `foundation.md`… | **not archived** | They are live documents, not superseded ones. The `spiral` → `fragmented` correction (entry 007) was an edit to a live file, not a disposition. |

**Registered (nothing pruned, nothing erased):** `README.md`, `DOC_POLICY.md`, the four `tools/` scripts,
`tools/calibration/slop-fixture.md`; in Book 2 `ASSUMPTIONS.md`, `ENTITY_STATE.yaml`, `RUN_REPORT.md`,
`maintenance/PRUNING_LOG.md`, `maintenance/SESSION_LOG.md`; and Book 1's
`artifacts/07-editorial-package.md`. Each was a real file the layer did not name; none was deleted or
moved to create the registration.

**Kept, and this is the §7 point:** the registry does not replace this log or the session log. A
`status: superseded` field says *that* a document left active context; this log says *why*, and keeps the
superseded wording the field cannot hold. Both remain, and the gate now checks the fields while a reader
still checks the reasons.

**Not pruned:** nothing. This entry adds destinations and names; it removes no file and no fact.

---

*Next entry: whenever the author answers the five open items — population sign-off, the hair change, the
ch.7 question, the titles, the comps.*
