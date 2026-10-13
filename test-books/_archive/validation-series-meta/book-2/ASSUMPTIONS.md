# ASSUMPTIONS — Book 2

Every assumption that Book 2 is running on, including the ones that make this validation weaker than
it looks. An assumption that is not written down is a fact waiting to happen.

---

## A. Inherited assumptions (taken from Book 1's canon, not re-verified here)

| # | Assumption | Source | If wrong |
|---|---|---|---|
| A-1 | Book 2 is the same series, same protagonist, same core world, same voice contracts | run brief | the whole directory is mis-scoped |
| A-2 | The length contract carries forward: 7 chapters, 15,000–18,000 words as the **aim**, ~60 formatted pages, with the ceiling **raised 20,000 → 22,000 words** on 2026-09-23 | `PROJECT_STATE.yaml → commercial_contract` (re-confirmed by the author) | if Engine A overruns 22,000 the shape needs re-cutting, not the ceiling raising again |
| A-3 | ~~Book 2's copy of the contract is not re-confirmed~~ — **RESOLVED 2026-09-23:** the author re-confirmed it together with the engine choice, so this is no longer an assumption but a decision | `PROJECT_STATE.yaml → commercial_contract.confirmed_by_user: true` | — (closed) |
| A-4 | The prose standing rule carries forward, including the calibrated scanner and its controls | `../book-1/PROJECT_STATE.yaml → standing_rules.prose` | a gate with no calibration is not a gate |
| A-5 | Book 1's four reader personas are the starting audience for Book 2 | `../book-1/reader-personas.md` | Book 2's packaging would target the wrong reader |

## B. Validation-specific assumptions — the honest ones

| # | Assumption | Risk | Recorded where |
|---|---|---|---|
| B-1 | **The resume was a cold LOAD, not a cold SESSION.** The agent performing the test drafted Book 1 minutes earlier, so "Book 2 recognised the voices" may be coming from the layer *or* from the agent's own memory of writing them. | **The test is weaker than it reads.** What is proven is that the information is *in the layer* and is loadable with citations. What is *not* proven is sufficiency: that a stranger with no memory of Book 1 gets the same result. | `continuity/resume-test.md`, opening caveat, and again in the scorecard |
| B-2 | The contradiction probe (`PROBE-001`) was installed by the same agent that wrote the rule it violates. | It is a **self-test**, and a self-test can pass for the wrong reason. | `continuity/resume-test.md → Test 4` |
| B-3 | The scores in `../book-1/artifacts/06-scorecard.md` were assigned by the agent that drafted the prose. | Least independent evidence in the project. | stated at the top of that file |
| B-4 | Phase 1 (Research) for Book 1 was **desk analysis only** — no live research was run — and Book 2 has no research at all yet. | Market claims rest on reasoning, not data. | `../book-1/RUN_REPORT.md` |

## C. Open decisions — assumptions Book 2 is deliberately NOT making

| # | Open | Why it is not inferred |
|---|---|---|
| C-1 | ~~**The engine**~~ — **DECIDED 2026-09-23: Engine A, "the work"** | Was held open on the no-inference rule, which is the whole reason to be able to point at this row and say it is closed by an author decision rather than by a guess. Three options were offered (`INTAKE.md 2.1`), none was recommended, and the author chose. → `CANON_LEDGER.yaml → facts.book-2.engine` |
| C-2 | ~~The new location's content~~ — **DECIDED 2026-09-23: Location 3, "the unfinished thing"** | Closed. `CANON_LEDGER.yaml → facts.book-2.location`. |
| C-3 | ~~The relationship delta's content~~ — **DECIDED 2026-09-24: Merope notices, and tests Achird in subtle ways** | Closed by author instruction. An earlier prohibition on directness was struck the same day as pipeline inference (`CONF-011`) — see the standing caution below. |
| C-4 | ~~The interval between the books~~ — **DECIDED 2026-09-24: not load-bearing, not specified** | Closed. Book 1's *weeks* remains book-1-scoped and is not reused to imply a gap. |
| C-5 | Book and chapter titles, comps | Deferred by the author since Book 1 Phase 2. Book 1 shipped with a working title; Book 2 does the same. |
| C-6 | ~~Whether the beings appear in Book 2~~ — **DECIDED 2026-09-24: they do not.** The population is something new | Closed. `COL-001` stays book-1-scoped and is **not** repurposed as a local population. Its rules (cannot lie, cannot explain, never sinister, no spokesperson) are not inherited by a new collective. |

### Standing caution, added 2026-09-24

**The pipeline's own readings must not be recorded at author authority.** `CONF-011` is the second
instance in this project of an inference being written into canon as though it were a user rule
(compare `CONF-007`). Both were caught by the author, late. Anything in this file or the ledgers that
reads as a *prohibition* should be checked against its `authority` field before it is obeyed. Comps
(C-5) remain unapproved and Book 1's market map remains desk analysis only.

## D. Hygiene obligations before Book 2 is drafted

These are debts the validation created. Each has an owner and a file.

Every row now carries a **status**, because a debt list that mixes "done" with "later" with "the
author's" is a list nobody can act on. Reclassified 2026-09-22.

| # | Obligation | Status | Where |
|---|---|---|---|
| D-1 | **Close or remove `PROBE-001`.** It was validation scaffolding, not canon. Leaving an open CRITICAL in a live ledger is exactly the "silently divergent" state this project spent a day eliminating. | **CLOSED 2026-09-22** — resolved by author instruction; series value upheld, probe value discarded, record retained for provenance | `CANON_LEDGER.yaml → conflicts.PROBE-001` |
| D-2 | Log the removal in the pruning log, per protocol §7. | **CLOSED 2026-09-22** — pruning log entry 003 | `maintenance/PRUNING_LOG.md` |
| D-3 | Re-confirm or re-set the commercial contract when the engine is chosen. | **CLOSED 2026-09-23** — re-confirmed by the author alongside the engine; shape unchanged, ceiling raised to 22,000 | `PROJECT_STATE.yaml → commercial_contract.confirmed_by_user: true` |
| D-4 | Carry Book 1's **remaining three** author items forward rather than losing them at the volume boundary. `AUTH-1`, `AUTH-2` and `AUTH-5` were **closed 2026-09-22** (the last of them made both leads' appearance canon); `AUTH-3` (two prose judgement calls), `AUTH-4` (titles) and `AUTH-6` (the weeks scale) remain. | **CARRIED** — registered, not lost; all three are the author's | `../book-1/PROJECT_STATE.yaml → notes` |
| D-7 | **Book 2 inherits the appearance canon and does not get to redesign it.** Series-scoped: Merope — white twin tails, celestial Lolita dress, busty/full-figured. Achird — flat-chested, crimson hair in a **scorpion-tail braid**, superbubble hoodie. `APPEAR-1`, `APPEAR-2` and `APPEAR-3` are **author-resolved** (the last as a coincidence the author likes, explicitly *not* a planted resonance — it must not be seeded into Book 2 and must never be remarked on in the prose). Only `APPEAR-4`, the superbubble hoodie reading, remains this pipeline's interpretation rather than an author statement. | **SATISFIED** — recorded in Book 2's own entity state | `ENTITY_STATE.yaml → inherited` · `../book-1/artifacts/character-design-brief.md` |
| D-5 | Do **not** duplicate the voice contract. Additions are appended to `../book-1/voice-dna.md` with their scope marked. | **SATISFIED** — still cited, not copied | `CANON_LEDGER.yaml → voice_contract.owned_by` |
| D-6 | The cover-the-name exercise still has not been performed, for either book. | **CARRIED** — deadline before Phase 7; not a drafting blocker | `../book-1/PROJECT_STATE.yaml → voice_dna.cover_the_name_pass` |
