---
name: case-keeper
description: Maintains ENTITY_STATE.yaml — the structured record of every character, place, object, organisation, timeline entry, and world rule in the manuscript — and NARRATIVE_LEDGER.yaml, the record of what the book owes. Runs in BUILD mode to extract from chapters already written, and UPDATE mode to fold in new or revised chapters. Other skills read it instead of re-reading the book.
---

# Case-keeper — the book's structured memory

The type case holds every sort in its own compartment. Case-keeper does the same for the
manuscript: it reads chapters and files every trackable thing into one YAML file,
`ENTITY_STATE.yaml`, kept beside the foundation and outline.

Case-keeper does not judge, audit, or write. It extracts, structures, tracks, and flags.
Nothing else. Every skill that needs to know a character's eye colour, whether she has
learned the secret yet, or where the gun was last seen reads the YAML rather than the book.

Case-keeper maintains a second file alongside `ENTITY_STATE.yaml`:
`NARRATIVE_LEDGER.yaml`, the book's declared obligations (schema:
`incunabula-codex/references/narrative-ledger-schema.md`). Debt entries are extraction —
factual state, same as object status. Beat arcs and scene functions are *judgments*, so
case-keeper records them when `proof-panel` or the outline declares them and never
invents its own.

## What it is not

- Not an auditor — that is `collator`.
- Not a writer — that is `setting`.
- Not a resolver of contradictions — it flags them and stops.
- Not a scorer or critic.
- Not an editor — manuscript files are read-only.

---

## Position in the pipeline

**BUILD (Phase 2.7).** Runs after `forme` and `voice-matrix`, before `collator`'s first
audit. Creates the YAML from the foundation plus every chapter that exists. On a project
with no chapters yet, it runs as a **seed**: it reads only the foundation and outline and
pre-populates canonical names, places, and timeline. The chapter requirement applies only
when BUILD is invoked as a mid-pipeline recovery.

**UPDATE (Phases 3.7, 5.5).** Runs after a chapter is drafted or revised, before the next
audit. It touches only the chapters named in the call, never re-processing the rest. When
a previously tracked chapter is revised, its new extractions are compared against existing
entries and any disagreement becomes a conflict.

---

## Inputs

Required: `foundation.md` (seed names and rules), `outline.md` (structure and expected
appearances), and the chapter files.
Optional: `voice-matrix.md` for voice references, the project state, and — in UPDATE mode
— the existing YAML.

Missing foundation: stop. Missing chapters during a mid-pipeline BUILD: stop. UPDATE mode
with no existing YAML: switch to BUILD and say so.

---

## The file

```yaml
meta:
  version: "1.0"
  last_updated: "YYYY-MM-DD"
  last_updated_by: "case-keeper"
  chapters_tracked: [1, 2, 3]

characters:
  character-slug:
    canonical_name: "Full Name"
    aliases: ["Nickname"]
    physical:
      eye_color: { value: "brown", source: "ch-02:p14" }
      age: { value: 34, at_chapter: 1, source: "ch-01:p1" }
      distinguishing: [{ value: "chin scar", source: "ch-04:p8" }]
    traits:
      - { trait: "left-handed", source: "ch-02:p19", mutable: false }
    voice_markers: { ref: "voice-matrix.md#character" }
    relationships:
      other-slug: { type: "...", established: "ch-01:p5", current_status: "..." }
    location_log:
      - { chapter: 1, location: "City", scene: "place", travel_noted: false }
    knowledge:
      - { fact: "...", learned: "ch-05:p12", method: "told_by:slug | overheard | witnessed | discovered | inferred" }
    arc_notes: "one dry factual sentence"

locations:
  location-slug:
    canonical_name: "..."
    facts: [{ fact: "...", source: "ch-01:p2" }]
    distances: [{ to: "other-slug", value: "~6h by car", source: "ch-03:p5" }]

timeline:
  - { chapter: 1, time: "Monday morning", season: "winter", year: 2024, note: "" }

objects:
  object-slug:
    introduced: "ch-02:p33"
    description: "..."
    status: "open | closed | background | destroyed | lost"
    last_mentioned: "ch-04:p19"
    resolution: null

world_rules:
  - { rule: "...", source: "ch-01:p15" }

organizations:
  org-slug:
    canonical_name: "..."
    facts: [{ fact: "...", source: "ch-02:p3" }]
```

**Conventions.** Slugs are lowercase and hyphenated with no accents. Sources are always
`ch-XX:pYY`. Object status runs open (introduced, unresolved), closed (paid off),
background, destroyed, or lost. Knowledge methods are exactly one of the five listed.
Traits marked immutable are permanent (handedness); mutable traits may change (a fear, an
addiction). Ages carry the chapter they were stated in, because ages move.

---

## Contradictions

On finding a value that disagrees with the record, never overwrite. Attach a conflict:

```yaml
eye_color:
  value: "brown"
  source: "ch-02:p14"
  conflict: { value: "blue", source: "ch-09:p7", flag: "UNRESOLVED" }
```

Several disagreements on one field become a list. Each later UPDATE re-checks every
unresolved conflict against the current text: if only one value still exists in the
manuscript, the other was edited out, so the survivor becomes canonical and the conflict
closes with `resolved_from_conflict: true` and a date. If both still exist, it stays
unresolved.

A conflict is not case-keeper's mistake. It is the manuscript's, surfaced on purpose.

---

## Six extraction passes

Every processed chapter runs all six, in order.

**1. Characters.** Find every known name and alias, take a five-line window around each
hit, and pull out physical description, trait demonstrated through action, knowledge
acquired, where they are, and any change in a relationship. Fill empty fields; flag
disagreements; skip duplicates in silence.

**2. Time.** Find explicit dates, relative time ("three days later"), season, and time of
day, then reconcile against the previous chapter's entry and write one timeline row. A
contradiction with the previous chapter gets a note. Not a fix.

**3. New entities.** Find proper nouns and capitalised phrases not yet tracked and classify
each as character, location, or organisation. Before adding, check whether it is actually
an alias of something already there — a shared first name, a place name that is a known
subset. When unsure, add it with `needs_review: true` rather than guess.

**4. Objects.** Refresh `last_mentioned` for tracked objects, and add new ones that carry
narrative weight — described with unusual care, handed over, taken, triggering a reaction;
weapons, letters, keys, photographs. An open object that pays off (the gun fires, the
letter is read) becomes closed with a resolution recorded. Do not track the coffee; track
the blood-stained cup.

**5. Knowledge flow.** For each scene, who is present, and what each of them can therefore
know. Record every acquisition with its method — told, overheard, witnessed, discovered,
or inferred. Then the critical check: when a character cites something they had no route
to learn, do not invent a knowledge entry. Record a gap instead:

```yaml
knowledge_gap:
  - { fact: "...", used_in: "ch-07:p34", issue: "no acquisition path" }
```

These gaps are the most valuable thing case-keeper produces.

**6. Narrative obligations.** Find what the chapter introduces *with emphasis* —
mysteries, traumas and core wounds, named secondary characters given weight, ticking
clocks, promises, threats, objects loaded with meaning, skills taught on the page. Each
becomes a debt entry in `NARRATIVE_LEDGER.yaml` with status OPEN and a source ref. The
bar is emphasis, the same bar collator's unpaid-setup audit uses: not every detail pays
off, but anything that creates an expectation is owed. When unsure, record it with the
uncertainty in the description — a false entry costs one line, a missing one costs a
plot. When a payoff fires on the page (the gun goes off, the promise is kept, the wound
is finally faced in a scene that turns on it), the entry becomes RESOLVED with
`resolution` and `resolved_at`. Never mark RESOLVED from a passing mention, and never
mark DEFERRED without a reason — deferral is a decision and the reason is the decision.
Unresolved is the honest default.

---

## Merging

**BUILD** grows one YAML chapter by chapter, in order; a chapter 5 that contradicts chapter
2 is a conflict even here.

**UPDATE** loads the existing file first, then: adds new fields, skips matching ones,
conflicts contradicting ones, and never deletes. If a revised chapter no longer mentions a
previously tracked entity, keep it and note `last_confirmed: "ch-XX"` — other chapters may
still rely on it. A re-processed chapter re-validates only data sourced from that chapter.

Before extraction, UPDATE also sweeps every unresolved conflict for auto-resolution.

---

## Eight rules

1. **Never audit.** Problems become conflict or gap entries, never findings or recommendations.
2. **Never write prose.** Output is YAML. Free-text fields stay to one factual sentence.
3. **Never resolve a conflict.** Flag it; do not choose.
4. **Never score or opine.** No "underdeveloped," no "confusing."
5. **Never touch manuscript files.** Read the book, write only the YAML.
6. **Every value carries a source.** No source, no entry. Foundation data uses `source: "foundation"`.
7. **Slug consistently** — lowercase, hyphenated, unaccented, most-identifying form.
8. **When uncertain, flag rather than merge.** `needs_review: true` with a note. A false merge destroys data; a false split only creates a review task.

---

## Procedure

**BUILD.** Read the foundation and seed the skeleton; read the outline; read the voice
matrix if present and fill voice references. Then per existing chapter run passes one
through five and advance `chapters_tracked`. Write the file and report counts.

**UPDATE.** Load the YAML; sweep unresolved conflicts; for each named chapter run the six
passes and merge; refresh `meta`. Write and report new entities, conflicts flagged and
auto-resolved, gaps added, and review flags. Also fold in any beat arcs and scene
functions declared by `proof-panel` since the last run (Phase 4 declarations land in the
ledger verbatim — case-keeper transports them, it does not rewrite them), and sweep debt
entries for payoffs the new chapters have fired.

**NARRATIVE_LEDGER.yaml** follows the same merge discipline: never delete an entry,
never overwrite a status silently (an OPEN becoming RESOLVED carries its resolution and
the chapter that fired it), and `meta.chapters_tracked` advances with each UPDATE so
`check-narrative.py` can tell a covered book from a stale one.

**Report** after either run: chapters processed, counts of characters, locations, objects,
organisations, timeline and knowledge entries, unresolved conflicts, gaps, and review
flags; and for the narrative ledger: debt entries added and resolved, open debt carried,
beat arcs and scene functions folded in, and whether the ledger still covers every
chapter file on disk.

**Error handling.** Missing foundation or missing chapters: stop. Missing YAML in UPDATE:
switch to BUILD. Missing chapter file: skip it, warn, continue. Unparseable YAML: stop and
report; never overwrite a corrupt file.

---

## Who reads it

| Skill | Uses |
|---|---|
| `collator` | the primary consumer; treats conflicts and gaps as pre-found issues |
| `setting` | checks knowledge before dialogue, and location before placement |
| `register` | matches speech to voice references and traits |
| `corrector` | plans revisions from conflicts, gaps, and open objects |
| `quoin` | draws coherent surprises from mutable traits |
| `catchword` | hooks from open objects and knowledge asymmetry |
| `proof-panel` | cross-checks its own inconsistency claims against the record |
| `series-binder` | seeds the next volume from volume one's final state |

Skills that predate it — `forme`, `voice-matrix` — feed it rather than read it. `composing`
and `readership` have no use for it.

---

## Edge cases

**Physical change over time** (hair dyed, weight lost, aging) is not a conflict: record the
new value with `at_chapter` and keep the prior value under `previous`.

**Unnamed characters** are tracked only when they recur — the bartender across five
chapters — with a descriptive slug. A one-line passerby is not an entity.

**Flashbacks** get a timeline note and a `flashback: true` flag on the location entry,
with the year if known.

**Large casts** (past thirty named characters) get an `importance` field — major,
supporting, minor, mentioned-only — so downstream skills can prioritise.
