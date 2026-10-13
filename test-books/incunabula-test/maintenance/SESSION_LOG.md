# Session Log

Append-only. One entry per session, with decisions, changed files, facts merged,
conflicts, and the next step. A phase that did not run is recorded as skipped rather
than omitted.

---

## 2026-09-25 — Session 1, Phase 0 (Intake)

**Phase:** 0. **Status:** completed, gate pending user direction.

**Check-in:** NEW project. No prior state to reconcile. Read the intake contract
(`references/prompts/intake.md`), the canon-ledger schema, the maintenance protocol, and
the prose gate before dispatching anything.

**Work done / files created:**
- `ASSUMPTIONS.md` — 15 labelled inferences.
- `artifacts/00-brief.md`, `artifacts/01-market-map.md`, `artifacts/02-story-engine.md`.
- `PROJECT_STATE.yaml` — primary state; parses (verified with a real parser).
- `CANON_LEDGER.yaml` — book scope; series scope declared `null` rather than omitted.
- `voice-matrix.md` — global narration contract active; per-figure cards deferred to 2.5.
- `maintenance/PRUNING_LOG.md` — opened with a restraint entry.
- `RUN_REPORT.md` — resume point.

**Facts merged:** none (first session). F-001 … F-007 recorded as `inference`, not canon.

**Conflicts raised:** `CONF-001` — first person vs third person in the narration. Open;
does not block drafting. Escalated to the author rather than decided.

**Skipped:** nothing mandated by this phase.

**Next step:** Phase 1 (Foundation) → `forme`. Phase 2 (Architecture) → `architecture`.
Phases 1.5 (`readership`) and 2.5 (`voice-matrix`) run between them.

**Gate:** the maintenance gate's preconditions exist before Phase 1 is dispatched
(ledger, voice contract, pruning log). Prose gate tools installed and controls green
(see RUN_REPORT.md).

---

## 2026-09-25 — Session 1 (continued), Phases 1–7

**Phases run:** 1, 1.5, 2, 2.5, 2.7, 2.8, 3, 3.1, 3.2, 3.5, 3.8, 4, 4.5, 5.5, 5.6, 6, 7.
**Phase recorded as SKIPPED:** 5 (revision) — see below.

**Check-in before dispatch:** primary state and ledger read; no prior chapters to
reconcile (NEW project); the phase prompts and the prose-gate and evaluator-protocol
references read before the phases that require them.

**Work done / files created:** foundation.md, readership.md, outline.md, voice-matrix.md
(17 figure cards), ENTITY_STATE.yaml, continuity/outline-audit.md,
manuscript/chapters/ (11 chapters + 11 writer reports), evaluations/ (11 quoin reports,
11 chapter evaluations, full-manuscript evaluation, register/catchword/composing logs,
revision-plan, fine-press-loop record), artifacts/08–10, continuity/manuscript-audit.md,
delivery/editorial/upstream-signals.md, research/01-market-notes.md, tools/build-epub.py,
manuscript/full-manuscript.md (generated), dist/*.epub.

**Facts merged:** none new at series scope. Facts F-001…F-007 remain `inference`.
ENTITY_STATE gained birth years for FIG-15, FIG-17 and FIG-18 (CONT-301).

**Conflicts:** `CONF-001` remains open (narrator person). No contradiction was resolved
silently. No new conflict was raised.

**Prose gate:** all 11 chapters PASS; 0 HARD-rule failures across the manuscript; six
chapters carry a D2 warning under the cap. Controls re-run green
(`tools/validate-controls.sh`).

**Skipped step, recorded as skipped:**
- **Phase 5 (revision).** A revision plan of 8 tickets was produced and **not executed**.
  The global floor is 7.0, which meets the prescriptive-NF threshold, and the outstanding
  tickets change the book's balance rather than fixing faults. Deferred to the author.
  `revision_cycles: 0`.
- **Phase 5 Fine Press overlay.** Not activated: the activation condition is an author-set
  quality target, and none was set. Recorded in `evaluations/fine-press-loop.md`.

**The finding that matters:** Phase 5.6 found **three CRITICAL arithmetic errors in prose
that had already passed the prose gate** (CONT-101, CONT-102, CONT-201). All three were
fixed and the manuscript re-scanned to PASS. The scanner cannot add; nothing else in the
pipeline can either. This is the same defect class the prior validation run recorded.

**Second finding:** the evaluation is **grade C** (same context as the writer) and is
**DEGRADED**. The scorecard says so and the Colophon cannot claim independent validation.

**Check-out:** primary state updated; ledger, entity state, voice contract and document
registry updated; this log appended; PRUNING_LOG appended; the active-phase gates re-run.

**Next step:** none required. The book is delivered to the author. Open items: `CONF-001`,
all titles, all comps, and the Phase 5 revision plan.
