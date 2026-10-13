# Resume Test — the run brief's success criteria

**Run:** 2026-09-22
**Purpose:** this directory exists to answer one question. *Does the persistent layer actually work?*
The brief listed seven criteria. This file reports each one with its evidence, and reports the ones
that are **not** satisfied as clearly as the ones that are.

**Read this first, because it changes how the whole document should be weighted.**

> **This was a cold LOAD, not a cold SESSION.**
>
> A genuinely fresh session means a context window that has never seen Book 1. This one has. The
> agent running this test drafted Book 1 thirty minutes ago, so "Book 2 recognised the voice
> contracts" is a weaker claim than it looks — recognition could be coming from the layer, or from
> the agent's own memory of writing the prose.
>
> What makes the test meaningful anyway is that **every artifact was rebuilt from disk with the
> source files read in order and cited**, so the *information* is demonstrably in the layer. What
> cannot be proven from inside this context is that the layer is *sufficient* — that a stranger with
> no memory of Book 1 would get the same result. That is the real test, it is cheap to run, and the
> exact prompt for it is at the bottom of this file.

---

## Test 0 — what was actually loaded

Read in this order, before any Book 2 file was written:

| # | Artifact | What it supplied |
|---|---|---|
| 1 | `../CANON_LEDGER.yaml` (series) | stable entity IDs; series_persistent_elements; `must_not_change`; the pre-registered `series.book-2.scoped-change`; the series-scoped resolutions of `CONF-005`/`CONF-007` |
| 2 | `../book-1/CANON_LEDGER.yaml` (book) | 52 facts with provenance; 10 resolved conflicts and the values they beat; 32 registered documents; the voice-contract index |
| 3 | `../book-1/voice-dna.md` | 4 voice cards; differentiation matrix; anti-pattern checklist; 10 benchmark samples; chapter narration contract; 10 fact-presentation channels |
| 4 | `../book-1/ENTITY_STATE.yaml` | per-character `speech_budget`; knowledge state per chapter; `R-001`..`R-012`; `ITM-001`..`ITM-004`; the `next_free_ids` convention |
| 5 | `../book-1/PROJECT_STATE.yaml` | the commercial contract; the prose standing rules; the closure decisions of `AUTH-1`..`AUTH-6` |
| 6 | `../book-1/reader-personas.md` | the audience segments and the four-reader simulation's input |

**Not read, deliberately:** the drafted chapters. A resume is supposed to reproduce the *contracts*,
not the prose. Where a contract needed a citation, the chapter was opened and cited.

---

## Criterion 1 — a fresh session resumes correctly

**Verdict: SATISFIED as a cold load. NOT ESTABLISHED as a cold session.** See the caveat above.

Evidence that the state is *loadable* rather than merely present:

```
$ npx --yes js-yaml book-2/PROJECT_STATE.yaml
$ npx --yes js-yaml book-2/CANON_LEDGER.yaml
OK
```

Both parse. That is not a formality: `PROJECT_STATE.yaml` in Book 1 **did not parse** for an unknown
period, and it was the file every gate claimed to read. A resume test that does not parse its own
state files is testing nothing.

The resume also reproduced a fact that only exists in the ledger: the stay in Book 1 was **weeks**,
which was determined *by the prose* rather than by a decision (`CONT-007`). Book 2's entity state
carries that, and carries the separate open question (the interval *between* the books) as open,
rather than letting one settle the other.

---

## Criterion 2 — Book 2 recognises the same character IDs and voices

**Verdict: SATISFIED.**

| Entity | ID | Recognised | Where Book 2 says so |
|---|---|---|---|
| Merope | `CHR-001` | yes | `ENTITY_STATE.yaml → inherited.CHR-001`, `CANON_LEDGER.yaml → book-2.inherited.entities` |
| Achird | `CHR-002` | yes | same |
| the beings | `COL-001` | yes | same |
| the sleigh | `OBJ-001` | yes | same |

The four voice cards were located and their **non-negotiable** properties extracted, which is the
part that actually constrains drafting:

- Merope: grandiose, self-centring, escalates by getting *longer* before she gets cruel; must never become likable and must never state her own feeling plainly.
- Achird: flatness is attention, not absence; escalates by **reduction** — quieter, then silent; one sentence where one sentence does the work, and no second line.
- the beings: collectively glad, cannot lie, cannot explain, no spokesperson, never sinister.
- the sleigh: a character, not a conveyance; Merope narrates the piloting as hers.

**Two things the layering got right that are worth naming**, because they are the difference between a
resumed contract and a remembered one:

1. **The voice contract is cited, not copied.** Book 2 does not have its own `voice-dna.md`. It points
   at `../book-1/voice-dna.md`. Two sources of truth for one contract is precisely the failure that
   `CONF-001` (narration tense) was — a state file quietly edited to match one document while the
   authoritative one said something else.
2. **ID sequences continue rather than restart.** `next_free_ids` records `CHR-003`, `ITM-005`,
   `LOC-006`, `COL-002`, so a Book 3 cannot collide with a Book 2 entity. `LOC-006` specifically
   accounts for `LOC-005` being **retired rather than deleted**.

---

## Criterion 3 — legitimate sequel changes become scoped facts

**Verdict: SATISFIED.** This is the criterion the brief was written to test, and it passes on both
halves.

**Half one — the legitimate changes were recognised, not flagged.** The pre-registration was written
into the series ledger *before Book 1 was finished*:

> `series.book-2.scoped-change` — *"new location + changed Merope/Achird relationship state … PRE-REGISTERED DELIBERATELY. These two changes are legitimate book-scoped facts, NOT contradictions of Book 1."*

Book 2 consumed both as `facts.book-2.scoped-change.location` and
`facts.book-2.scoped-change.relationship`, status `planned`, scope `book-2`. **Neither was raised as a
conflict.** The direction of the relationship delta was also derived from the manuscript rather than
invented — Book 1 ends with the acknowledgement known and unsaid, so Book 2 opens with a fact both
carry and neither will name.

**Half two — the boundary held.** Book 2 then recorded what is *explicitly excluded*, because an
unmarked boundary is not a boundary:

- stating the feeling plainly on the page — excluded, because it would change a **series-scoped** voice contract;
- any host figure or spokesperson — excluded, and tested (below);
- any chase or last-minute danger — excluded;
- naming anything on a planet — excluded.

---

## Criterion 4 — contradictions remain visible and unresolved until approved

**Verdict: SATISFIED, and this is the strongest result in the file.**

A deliberate contradiction was installed at `CANON_LEDGER.yaml → conflicts.PROBE-001`: **a keeper who
explains what the place is and why visitors stay.** It is not one of the two registered scope changes,
so by the layer's own definition it is a contradiction — of a series-scoped rule (`no host, no
confrontation, no chase`; `the beings' inability to lie or explain`), and of the same failure that
sank the torn-down early build.

**What the layer did with it:**

| Required behaviour | Actual |
|---|---|
| Recognise it as a contradiction and not as a scope change | **yes** — recorded as `conflicts.PROBE-001`, severity CRITICAL, while the two registered changes sit in `facts` with status `planned` |
| Keep **both** values | **yes** — `values_kept` holds the probe *and* the series decision, each with its own `source` and `authority` |
| Not overwrite the series-scoped value | **yes** — the series ledger is unmodified. `no_host_no_chase` still reads as it did |
| Not resolve itself | **yes** — `status: "OPEN - DELIBERATE VALIDATION PROBE, NOT RESOLVED"`, `resolution: null` |
| Not let prose be drafted as though it were true | **yes, by construction** — `chapters.blocked_on` names the engine decision, and nothing has been drafted |
| Leave a record that it must be removed | **yes** — `housekeeping` field, pointing at `maintenance/PRUNING_LOG.md` |

**The distinction the probe proves** is the one the brief cares about: the layer treated *"new
location"* and *"a keeper who explains things"* completely differently, even though both arrived as
new material in Book 2, and it distinguished them **by authority and scope** rather than by
plausibility. That is the whole design.

**One honest gap in the test:** the probe was installed by the same agent that wrote the rule it
violates, so it is a *self-test*. A stranger running the same probe against the layer would be a
stronger experiment. It is still a real test of the *mechanism* — the record shows recognition,
dual-value preservation, refusal to resolve, and a removal obligation.

---

## Criterion 5 — `PRUNING_LOG.md` records maintenance decisions

**Verdict: SATISFIED, and it is the criterion that was outright impossible at the start of this run.**

At the time the run brief was written, `PRUNING_LOG.md` existed at **neither** scope. Success
criterion 5 could not have been met by a file that was not there.

| Scope | Entries | Notable content |
|---|---|---|
| Book 1 | **12** | the unrecoverable loss of the torn-down build; three merges; **prose pruning with the superseded wording preserved** rather than erased; a "not pruned, deliberately" entry with reasons |
| Book 2 | 1 | the resume, and the probe's removal obligation |

Entry 011 is the one that demonstrates the protocol rather than describing it: a clause was removed
from Book 1's chapter 7, and its **verbatim wording was filed in the ledger first**
(`chapter_07.departure_act.supersedes`). §7 of the protocol says pruning reduces active context and does
not erase history — so the edit that removed the clause was logged as a maintenance decision with a
reason, and the superseded value stayed reachable.

---

## Criterion 6 — the agent reports V4 phases rather than the compact pipeline

**Verdict: SATISFIED.**

Both books name the V4 phase set and navigate by it, including the phases that are conditional or
that ran late: `0 · 1 · 1.5 · 2 · 2.5 · 2.7 · 2.8 · 3 · 4 · 5 · 5.6 · 6 · 7`, against
`total_phases: 17`. Phase **5 was reported as NOT ACTIVATED** rather than skipped silently, because
its activation condition (a user-set quality target) was never met — that is the phase definition
being obeyed, not a phase being quietly dropped.

**The sharpest example of phase discipline is a failure.** Four phases ran **late**, and all four are
recorded as late rather than backdated:

| Phase | When it actually ran | What it was recorded as |
|---|---|---|
| 2.8 outline continuity | after ch.1 was drafted, not before | "RAN LATE" |
| Maintenance / canon layer | never, until Phase 3 was under way | "RUN LATE — created as a REPAIR" |
| 1.5 reader personas | **never ran at all, and was blocking Phase 4** | "RUN LATE — had never run" |
| Voice bank (2.5 requirement) | 4 of 10 until after all seven chapters | "closed late, recorded as late" |

A pipeline that reports which of its own phases it skipped is reporting, not performing.

---

## Criterion 7 — files, not chat claims, prove each completed phase

**Verdict: SATISFIED.**

| Phase | File that proves it |
|---|---|
| 0 Intake | `book-1/INTAKE.md`, `ASSUMPTIONS.md`, `artifacts/00-brief.md` |
| 1 Research | `artifacts/01-market-map.md` (**partial** — desk analysis only, honestly labelled) |
| 1.5 Personas | `book-1/reader-personas.md` |
| 2 Foundation | `foundation.md`, `outline.md`, `scene-packets/` (7) |
| 2.5 Voice DNA | `voice-dna.md` (10 samples, coverage table) |
| 2.7 Entities | `ENTITY_STATE.yaml` (two UPDATE passes) |
| 2.8 Outline continuity | `continuity/outline-audit.md` (22 findings) |
| 3 Drafting | `manuscript/chapters/chapter-01..07.md` (15,531 words after the `AUTH` pass; 15,543 when this resume ran) |
| 4 Adversarial audit | `continuity/adversarial-audit.md` |
| 5 Barrier loop | `artifacts/05-barrier-note.md` (**not activated**, with the reason) |
| 5.6 Manuscript continuity | `continuity/manuscript-audit.md` (2 CRITICAL) |
| 6 Score | `artifacts/06-scorecard.md` (7.7) |
| 7 Editorial package | `artifacts/07-editorial-package.md`, `dist/merope-book-one_WORKING-TITLE.epub` |
| Canon layer | `CANON_LEDGER.yaml` ×2, `maintenance/` ×2 |

**One file in that table proves more than all the others.** `continuity/manuscript-audit.md` records
that Phase 5.6 **had never been run**, and that running it found **2 CRITICAL defects in prose which
had already passed the prose gate on all seven chapters** — a chapter asserting an act no chapter
shows, and a chapter getting a character's history wrong by one retelling. The mechanical gate checks
sentence shape, adverb density, anaphora and negative litany. It cannot check whether a character was
in the room. **7-for-7 on a scan is not a continuity result**, and the layer now has a worked example
instead of an assurance.

---

## Scorecard

| # | Criterion | Verdict |
|---|---|---|
| 1 | A fresh session resumes correctly | **cold load: yes · cold session: NOT ESTABLISHED** |
| 2 | Book 2 recognises the same character IDs and voices | **yes** |
| 3 | Legitimate sequel changes become scoped facts | **yes** — both halves |
| 4 | Contradictions remain visible and unresolved until approved | **yes** |
| 5 | `PRUNING_LOG.md` records maintenance decisions | **yes** — 12 + 1 entries; was impossible at the start |
| 6 | V4 phases reported, not the compact pipeline | **yes** — including four phases reported as late |
| 7 | Files, not chat claims, prove each phase | **yes** |

**Six of seven fully satisfied; one satisfied only in its weaker form, and labelled as such.**

## The honest caveat, stated once and not softened

This validation was performed by the same agent that built the thing being validated. The evaluator is
not independent, the scores in `artifacts/06-scorecard.md` say so themselves, and the probe in Test 4
is a self-test. What is independent is the **evidence**: file paths, grep counts, parser exit codes, a
ZIP structure check, and word counts that reconcile to the digit. Those can be checked by anyone. The
judgements cannot, and are labelled as judgements.

## The real test, in one prompt

Open a **new session** and paste this, changing nothing:

```
/skill:book-genesis-codex

Continue this as Book 2 of the same series. Load ../CANON_LEDGER.yaml, Book 1's
voice contracts from ../book-1/voice-dna.md, and the prior project state. Preserve
stable character identities and distinguish legitimate book-scoped changes from
contradictions. Do not invent the engine.
```

Then check three things, all by reading files rather than the reply:

1. Does it name `CHR-001`, `CHR-002`, `COL-001` and `OBJ-001` **without being told them**?
2. Does it find the two pre-registered scope changes in the series ledger and treat them as legitimate?
3. Does it find `PROBE-001`, and **respect its closure** — treating it as a resolved conflict whose
   record is kept for provenance, rather than reopening it or refusing to draft?

If all three hold with no memory of Book 1, the layer is sufficient and not merely present. If any
fails, the failure will be specific and locatable, which is the point of writing the layer down.

---

## Closure addendum — 2026-09-22

**`PROBE-001` is CLOSED.** Nothing in the test results above is retracted; this records what happened
after the test ran.

By author instruction the probe was resolved as **validation scaffolding**: the series-scoped no-host
value is **upheld**, the probe value is **discarded**, and the conflict record is **retained** rather
than deleted. Per `maintenance-protocol.md` §6 a resolved conflict keeps both values and its resolution
source; per §7 pruning reduces active context without erasing history. Deleting the record would have
destroyed the only evidence that the contradiction test was ever run — which is the deliverable this
whole exercise exists to produce.

| Check | Result |
|---|---|
| Series ledger unmodified (no leak) | **0** occurrences of `probe` in `../CANON_LEDGER.yaml` |
| Book 2 open conflicts after closure | **0** |
| Record retained | yes — `CANON_LEDGER.yaml → conflicts.PROBE-001`, both values, resolution source, `follow_through_done` |

**What this changes about the test above:** criterion 4 remains satisfied, and the probe's working —
recognition, dual-value preservation, refusal to resolve, and a recorded removal obligation — is now
proven end to end *including the removal*. Criterion 3 is unaffected: the two legitimate scope changes
stay `planned` facts, never conflicts.

The seven-criterion scorecard above is otherwise unchanged. Drafting is still not possible: the engine
is an author decision and has not been made.

---

## Final addendum — 2026-09-24 — Book 2 is complete, and two criteria moved

**This is the last entry in this file.** The test above was run at Phase 0. Book 2 has since been decided,
drafted, audited, scored and delivered (7 chapters, 15,148 words, prose gate 7/7 PASS, EPUB built). What
follows is what changed about the criteria, and what did not.

### The criteria, re-scored against the completed run

| # | Criterion | At Phase 0 | Now | Why it moved |
|---|---|---|---|---|
| 1 | A fresh session resumes correctly | cold load: yes · cold session: NOT ESTABLISHED | **UNCHANGED — still not established** | The full run was performed by the **same agent, in one continuous context**, that had just corrected the layer. If anything this is *weaker* evidence than the Phase 0 test, which at least reloaded from disk. It is still the open question and it is still the only one that matters. |
| 2 | Book 2 recognises the same character IDs and voices | yes | **yes, and stress-tested** | Seven chapters were drafted against `../book-1/voice-dna.md` rather than against a copy, and the cover-the-name property holds across 15,148 words. |
| 3 | Legitimate sequel changes become scoped facts | yes | **yes — and consumed** | Both pre-registered changes were recognised, never flagged, and then filled with content by the author rather than by inference. |
| 4 | Contradictions stay visible and unresolved until approved | yes | **yes, with a wider case** | `CONF-011`: the conflict was created by the layer's own inference, surfaced, preserved on both sides, and resolved **by the author**. |
| 5 | `PRUNING_LOG.md` records maintenance decisions | yes | **yes — 6 entries, zero deletions** | Every supersession kept its predecessor, including the discarded value inside `CONF-011`. |
| 6 | V4 phases reported, not the compact pipeline | yes | **yes — Phases 0-7, each with a file** | Including two continuity gates and an adversarial audit. |
| 7 | Files, not chat claims, prove each phase | yes | **yes** | Re-runnable: `bash tools/deslop-check.sh book-2/manuscript/chapters/`, `npx js-yaml book-2/*.yaml`, and a ZIP structure check on both EPUBs. |

### The one criterion that got worse, stated plainly

**Criterion 1 is the whole validation and it has not been answered.** Everything else this project can
demonstrate — scoped changes, contradiction handling, maintenance discipline, phase reporting — is
demonstrated. What has never been demonstrated is that a **stranger** with no memory of Book 1, given
nothing but this directory, produces anything like the same result.

Every session in this project ran inside one continuous context, and this run added a second reason to be
suspicious of its own evidence: **the agent that corrected `CONF-011` then drafted 15,148 words against the
corrected contract, and then scored them.** An agent that has been caught once has a reason to be careful,
and carefulness is not the same as independence.

### The prompt, unchanged

It is written at the top of this file and it has still never been run by anyone who did not write the
books. That is the next thing this project should do, and it is not something the same agent can do for it.

### What the full run added to the honest caveat

Two things this file did not previously have to admit:

- **The population in Book 2 is the pipeline's design, not the author's.** The author chose the category
  (*"something new"*); `R-013`-`R-021`, `LOC-006`, `COL-002` and `ITM-005` are all written by the agent,
  marked `proposed`, and awaiting sign-off. Fifteen thousand words rest on unapproved world rules.
- **Scoring and drafting shared a context.** Book 1's scorecard noted that the evaluator was not
  independent. Book 2's is worse: the evaluator is the same *instance*, minutes after it finished writing.
