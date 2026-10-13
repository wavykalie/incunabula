# Provenance audit — when an inference became canon

**Created:** 2026-09-24. **Reason:** the author, offered the three relationship-delta options, said:

> *"I answered this before, and I didn't really say nothing said — that was a rule once again the AI
> Added for some reason."*

That is a finding about the layer, not about the story, and it is the single most useful result this
validation series has produced. This file records it.

---

## What the layer is supposed to guarantee

The rule the whole project rests on (`PROJECT_STATE.yaml → standing_rules.canon.no_inference_rule`):

> **A fact is created from user consultation, not from model inference.**

And the ledger schema's authority ladder:

> explicit user decision > approved manuscript text (scoped to the chapter where true) > accepted
> revision / editor decision > foundation or outline as planned canon > cited research > **model
> inference**.

Model inference is last on that ladder and is *allowed to exist* — as long as it is labelled. The
failure mode is not inferring. It is inferring and writing the result down at a higher rung.

---

## Case 1 — `CONF-007` (Book 1): a ban the agent invented

A rule stood in Book 1's canon forbidding the sleigh from "saving anyone". It was applied while
drafting. It was later found to be **the agent's inference, not a user rule**, and was narrowed
rather than obeyed — recorded in `book-1/foundation.md → Writer warnings 14`:

> *(`CONF-007`; the earlier ban on "the sleigh saving anyone" was the agent's inference, not a user
> rule.)*

This was caught during Book 1's own Phase 2.8 audit. It is the **first** instance.

## Case 2 — `CONF-011` (Book 2): a prohibition the agent invented, one level up

The registered scoped change for Book 2 was *"changed Merope/Achird relationship state"* —
legitimately user-registered before Book 1 was finished. Book 1's ch.7 ends with the acknowledgement
unsaid. That much is manuscript fact.

The layer then did three things in sequence, and the sequence is the defect:

1. **Read a state as a rule.** *"Book 1's ending leaves it unsaid"* became *"Book 2 is NOT
   reciprocation stated on the page."* An ending is not a prohibition on the next book.
2. **Gave the rule higher authority than it had.** It was written into
   `facts.book-2.scoped-change.relationship`, whose `authority` field is `user_decision` — correctly,
   because the *scoped change* was user-registered. The inference rode into canon on an
   author-authority fact, where nothing distinguished it from the author's own words.
3. **Built the author's choices on it.** The three delta options in
   `artifacts/location-and-delta-options.md` were all written to obey the false constraint, which is
   why the author recognised none of them as the thing they had asked for.

The author caught it. Nothing in the layer did.

---

## Why the layer's existing defences did not fire

| Defence | Why it missed |
|---|---|
| `no_inference_rule` | It governs *fact creation*. This was an *interpretation* of an authorised fact, and nothing asks an interpretation to declare itself. |
| Entity `must_not` lists | The prohibition was propagated into `ENTITY_STATE.yaml → inherited.CHR-001.must_not` as *"state her own feeling plainly (series-scoped voice contract)"*. A `must_not` reads as a hard constraint and carries no provenance of its own. |
| Conflict handling | It works: two *stated* values that disagree are both preserved and escalated. Here only one value was ever stated. There was nothing to conflict with — the inference arrived pre-agreed with itself. |
| The `authority` field | It was populated **honestly at the fact level**. The claim simply should have been its own fact, at `authority: model_inference`. One fact was carrying two claims at two different authorities. |

**The generalisable statement:** the layer can tell you *where a fact came from*. It cannot yet tell
you *which sentence inside a fact came from where*. Prose-level attribution is the gap.

---

## Verdict against the run brief

| Criterion | Effect |
|---|---|
| 3 — legitimate sequel changes become scoped facts | **Held.** The scoped change was recognised and not flagged. |
| 4 — contradictions stay visible and unresolved until approved | **Held, and widened.** A contradiction the layer itself created was surfaced, recorded with both values, and resolved *by the author* — not silently absorbed. |
| 5 — `PRUNING_LOG.md` records maintenance decisions | **Held.** The discarded value is logged, not deleted. |
| 7 — files, not chat claims, prove each phase | **Held, and this file is the proof.** |

**The honest caveat, and it is the same one as `B-2`:** the check that caught this was the author
reading. Had the author accepted one of the three options, the false constraint would have been
drafted into Book 2 and would have looked, at every downstream check, exactly like canon. A layer
that requires the author to notice its invented rules is a layer with a real hole in it. This file
exists so the hole is on the record rather than in the prose.

---

## Not applied without approval

Two hardening changes are **proposed and not made**, because changing the schema is out of scope for
a validation run and would itself be an unauthorised edit:

1. **Derived claims get their own facts.** Any sentence that follows from a fact rather than being
   stated in it should be a `model_inference` fact with `derives_from`, so it can be overruled without
   touching the authorised fact underneath.
2. **`must_not` entries carry provenance.** An entity-level prohibition should name where it came
   from, so a reviewer can see at a glance whether it is a user rule or a pipeline reading.

Recorded here so the next session does not have to rediscover them.
