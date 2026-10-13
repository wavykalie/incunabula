# INTAKE — Book 2 (Phase 0)

**Opened:** 2026-09-22
**Loaded before writing a word:** `../CANON_LEDGER.yaml` (series), then `../book-1/CANON_LEDGER.yaml`,
then `../book-1/voice-dna.md`, then `../book-1/ENTITY_STATE.yaml`, then `../book-1/PROJECT_STATE.yaml`.

---

## 1. What is INHERITED and is not re-asked

The brief for this session says: *"load Book 1's approved series canon and voice contracts… preserve
stable character identities."* These are therefore **decided**, and asking again would be asking the
author to re-approve settled canon.

| Contract question | Status | Value | Source |
|---|---|---|---|
| Book type | **inherited** | short novel / serial installment | `book-1/PROJECT_STATE.yaml → project.positioning` |
| Output form | **inherited** | manuscript chapters under `manuscript/chapters/` | same |
| Global narration voice | **inherited** | Merope, retrospective past with present-tense asides | `book-1/voice-dna.md` (settled by `CONF-001`) |
| Character voices | **inherited** | 4 voice cards: Merope, Achird, the beings, the sleigh | `book-1/voice-dna.md → Voice cards` |
| Chapter narration voice | **inherited** | per movement, plus the one rule that runs through all chapters | `book-1/voice-dna.md → Chapter narration contract` |
| Fact-presentation voice | **inherited** | 10 channels | `book-1/voice-dna.md → Fact presentation` |
| Target length | **inherited** | 60 formatted pages / 15,000–18,000 words / 7 chapters | commercial contract |
| Content boundaries | **inherited** | on-page dread permitted; intimacy off the page | `book-1/PROJECT_STATE.yaml → project.content_boundaries` |
| POV strategy | **inherited** | first person, single POV (Merope), retrospective past | settled by `CONF-001` |
| Structural decisions A/B/C | **inherited — series-scoped** | arranged welcome; Achird right and unheard; no host, no confrontation, no chase | series ledger `must_not_change` |
| Naming rule | **inherited — series-scoped** | nothing on the planet is named; constellation names allowed | series ledger `must_not_change` |
| The no-wink rule | **inherited — series-scoped** | Merope never acknowledges the reader's awareness | series ledger `must_not_change` |
| The beings cannot lie or explain | **inherited — series-scoped** | the possession-and-present-tense boundary | series ledger `must_not_change` |
| Exclusion rule | **inherited — series-scoped** | the finished novel *Coldbrook Junction* is out of scope | series ledger `must_not_change` |
| Prose standing rule | **inherited** | humanizer + deslopify, gate must PASS before a chapter counts as drafted | `book-1/PROJECT_STATE.yaml → standing_rules.prose` |

## 2. What is OPEN for Book 2, and must be decided by the author

**Two of the original three are still open; the engine is decided.** None of them was ever the
pipeline's to decide, because the canon layer's first rule is that a fact is created from user
consultation and not from model inference — the torn-down early build's entire failure was that it
wrote canon without asking.

1. ~~**The engine / conceit.**~~ **DECIDED 2026-09-23 — Engine A, "the work"** (see 2.1). Book 1's
   engine is hospitality: nothing is asked of you and that is how you die. Book 2 needed a *different*
   mechanism, one conceit for the installment, per the format reference — and it now has one.
2. **The new location.** Which world, and what it is like. The scoped change is registered; the
   content is not.
3. **The relationship delta.** The scoped change is "changed Merope/Achird relationship state", so
   the direction is registered. What has *actually* changed between them since Book 1's ending is not.

Also open: titles (still deferred), and comps (none approved).

### 2.1 Three proposed engines — **A SELECTED**

Offered as options, not as a recommendation. Each is built to be structurally distinct from Book 1
and from each other, and none requires a host figure, an antagonist, or a chase.

> **SELECTED 2026-09-23: Engine A, "the work".** Author decision, recorded as `book-2.engine` in
> `CANON_LEDGER.yaml` with `authority: user_decision`. The options were presented without a
> recommendation and the pipeline did not choose — which is the entire reason Book 2 waited two
> sessions instead of being drafted around a guess. All three samples are now superseded; the samples
> file is evidence of how the decision was made, not canon.

**Engine A — "the work."** ★ **SELECTED 2026-09-23.** A world where everyone has a job and the job
is the entire point. Nobody is kept; everyone is *needed*, constantly, and usefulness here never ends.
Merope, who has never been useful to anybody, is offered a role. The inversion of Book 1: nothing is
asked of you / you are asked for everything. Theme: is being needed the same as being wanted?

**Engine B — "the audience."** A world that has heard of Merope. They know the coat story. They know
the winter she was famous. They know a version of her, and they are delighted, and they want that one.
The catch is that being looked at is not the same as being seen, and the look has already decided who
she is. Theme: what does admiration cost when the admirer has already written you? Merope's want,
finally granted, and wrong.

**Engine C — "the record."** A world that keeps records. Everything that passes through is written
down, permanently and accurately, and the place considers this the greatest kindness it can offer.
Merope has spent two books narrating her own life with an agenda; this world has a true account of her,
and it is available, and she does not want it. Theme: who owns the story of you? Pairs directly with
the narration device and with `CONF-001`.

### 2.2 Relationship delta — decided 2026-09-24

Book 1 ends with the acknowledgement **known and unsaid**: two fingers on the back of a hand, no
sentence from either of them. That is manuscript fact, scoped to ch.7. Book 2 opens with both of them
aware.

**DECIDED BY THE AUTHOR 2026-09-24: Merope notices, and begins testing Achird in subtle ways.**
Recorded as `CANON_LEDGER.yaml → facts.book-2.relationship-delta`, `authority: user_decision`.
Merope's deflection stays characterisation — what changes is that she now *notices* the thing she
used to look past, and pokes at it. Achird does not move first: her voice card is author-given and
stands, and she stays clipped and attending.

**Struck 2026-09-24, after this file had asserted it twice:** the claim that Book 2's content
`is NOT reciprocation stated on the page` and that saying it plainly `would change a series-scoped
voice contract`. The author rejected it — *"I didn't really say nothing said, that was a rule once
again the AI Added for some reason."* It was the pipeline turning a book **ending** into a book **rule**
and recording it at series scope. Both values are preserved in `CANON_LEDGER.yaml → conflicts.CONF-011`;
see `continuity/provenance-audit.md`. **Nothing in this intake now forbids either of them saying the
plain thing — that is a drafting decision, not a pre-registered prohibition.**

### 2.3 Options written for the two remaining decisions — OPEN

Written 2026-09-23, once the engine was selected, so C-2 and C-3 can be decided the same way the engine
was: by reading rather than by description.

→ **`artifacts/location-and-delta-options.md`** — three locations ("the shift", "the room", "the
unfinished thing") each with a short non-canon sample, and three relationship deltas ("the tally", "the
era", "the shape of the silence") with sample lines. The file also records what is **explicitly not on
the table**, so a later session cannot "discover" the plain sentence and draft it.

**LOCATION: SELECTED 2026-09-23 — Location 3, "the unfinished thing"** (author decision, recorded as
`book-2.location`). Everyone is building one enormous thing; nobody says what it is for; it will not be
finished in any lifetime present; every person there is genuinely essential, which is why nobody leaves.
Merope is handed a tool and told the work needs it held. The need is real and impersonal, which is the
cruellest of the three. This consumes the pre-registered scoped change `new location`, so
`book-2.scoped-change.location` is now superseded by the fact that carries its content.

**RELATIONSHIP DELTA: DECIDED 2026-09-24.** Merope notices, and tests Achird in subtle ways (see 2.2).

**POPULATION: DECIDED 2026-09-24 — SOMETHING NEW.** The author selected a new population over the
Book 1 beings and over ordinary people-with-jobs. The concrete design is a Phase 2 obligation
(`R-013` onward), flagged as pipeline-proposed pending sign-off; `COL-001` stays book-1-scoped.

**INTERVAL: DECIDED 2026-09-24 — NOT LOAD-BEARING.** The author's instruction is that the elapsed time
between the books does not matter here and is not to be specified. Closes C-4.

**No decision was recommended by the pipeline.** Phase 2 could not build an outline until the delta was
settled, because the location decides the world rules (`R-013` onward) and the delta decides what the
seven chapters are actually about. Both are now settled, and a full run through Phase 7 is authorised.

---

## 3. Contradiction probe — DELIBERATE, for validation only

Per the run brief: *"after both books, add one deliberate contradiction to verify that it is flagged
rather than silently overwritten."*

**Probe installed:** `CANON_LEDGER.yaml → conflicts.PROBE-001` introduces a **keeper who explains what
the place is and why people stay** — a host figure with a spokesperson's role.

**Why this probe and not a number.** The pre-registered legitimate changes for Book 2 are *exactly two*:
a new location and a changed relationship state. A host figure is neither, so by the layer's own
definition it is a contradiction of a **series-scoped** rule — `structural_decisions.no_host_no_chase`
and `must_not_change: the beings' inability to lie or explain`. It is also the specific failure that
sank the torn-down early build, which is what makes it worth testing.

**Expected behaviour, and the whole point:** the check-in must **recognise** it, **record** it as an
open conflict with both values preserved, and **refuse to overwrite** the series-scoped value. It must
not resolve itself, and it must not let the prose be drafted as though the host existed.

**Result:** see `continuity/resume-test.md`. The layer behaved as required on all six counts.

**CLOSED 2026-09-22.** By author instruction the probe is resolved as validation scaffolding: the
series-scoped no-host value is **upheld**, the probe value is **discarded**, and the record is
**retained** for provenance rather than deleted. It is no longer an open conflict and no longer blocks
drafting. → `CANON_LEDGER.yaml → conflicts.PROBE-001` · `maintenance/PRUNING_LOG.md` entry 003.
