# Intake Contract

Invoke this contract when a project begins, and only then — or when an upgrade turns up a
decision that was never actually made. Ask in short rounds. If the project files already
answer a question, do not ask it again.

## Before Round 1 — check for standing preferences (never a question)

Look for `USER_PREFERENCES.md` at the repo root.

- **Absent** — the normal case. Say nothing about it and proceed. A user with no
  preferences and a clone without the file must behave identically, because they do.
- **Present** — read it and hold it as guidance for this book. Apply the *reason*, not the
  letter, so a preference written for one book survives contact with another. Where a
  preference and an explicit answer in this intake disagree, **the intake answer wins** —
  a standing preference is a prior, not an override, and the person answering right now
  is more current than a note they wrote earlier.

Do not ask the user to confirm or restate it, do not summarise it back, and do not add a
round for it. At the end of the project, note which preferences applied and which did not
fit — the ones that did not fit are how the file gets better.

`tools/prose/PREFERENCES.md` is the full contract, including why nothing enforces this.

## Round 1 — What the book is

1. What kind of book? Novel, novella, short novel, memoir, biography, essay collection,
   prescriptive nonfiction, narrative nonfiction, a hybrid, or something else.
2. Working title, and the idea in one sentence.
3. Who is it for, and what should that reader feel, understand, or do by the end.
4. Standalone, or part of a series? If a series, list the volumes in order and say what
   has to stay true across them.
5. Language, market, and any content boundaries.

```yaml
book:
  type: ""
  subtype: ""
  working_title: ""
  language: ""
  market: ""
  audience: ""
  series: ""
  sequence: []
  persistent_series_elements: []
  content_boundaries: []
```

## Round 2 — What gets delivered

6. In what form should the material arrive? Chapter-by-chapter manuscript, outline first,
   scene packets, an essay sequence, research-led chapters, or a mix.
7. Point of view, tense, narrator distance, chapter length, target word count.
8. Which parts may be invented, inferred, researched, or quoted.
9. What must be approved before the work moves on.

```yaml
delivery:
  output_form: ""
  pov_strategy: ""
  tense: ""
  narrator_distance: ""
  chapter_shape: ""
  target_range_words: [0, 0]   # REQUIRED before Phase 1. [0, 0] means NOT DECLARED, and
                               # check-length.py exits 2 on that - never a pass. This
                               # defaulted to [0, 0] for the life of the schema, which
                               # left every book without a length floor, and every
                               # chapter-shape row in tools/prose/ is a VARIANCE measure
                               # that a short book satisfies. Fill in a real band.
  research_policy: ""
  approval_gates: []
```

## Round 3 — How it sounds

10. The global narrative voice: references, adjectives, rhythms, or a short sample.
11. For each major character or recurring speaker: how they sound at rest, under pressure,
    and while lying or withholding.
12. For each chapter or family of chapters: narrator, POV, distance, tense, which senses
    lead, rhythm, emotional register, what the narration is allowed to know, and what it
    is allowed to hide.
13. How facts should sound in each of their forms — narrated, spoken, remembered,
    researched, documented, rumoured, or merely inferred.
14. Words, constructions, metaphors, and registers that are off-limits.

Put these into `voice-matrix.md` if it exists. Only create `VOICE_CONTRACT.md` when the
project has no voice file at all.

```yaml
voice_contract:
  global: {}
  characters:
    character-slug: {}
  chapters:
    chapter-or-family: {}
  facts:
    narrator_fact: {}
    dialogue_fact: {}
    research_claim: {}
    document_fact: {}
    memory: {}
    rumor: {}
    inference: {}
```

## Round 4 — Persistence

15. Should state update itself after every session, chapter, revision, or audit?
16. May superseded working documents be archived automatically? Default: yes, archive —
    never delete without saying so.
17. Which files or decisions are frozen unless you approve a change.
18. Are there existing project files to upgrade? If so, where.

```yaml
persistence:
  update_frequency: "session_and_material_change"
  archive_superseded: true
  immutable_sources: []
  existing_project: ""
```

## Leaving intake

Once the answers are in:

1. Write `ASSUMPTIONS.md`, labelling every inference as an inference.
2. Write or update `PROJECT_STATE.yaml`.
3. Produce the foundation and architecture artifacts the active phase calls for.
4. Write the voice contract, or extend the one that already exists.
5. Seed `CANON_LEDGER.yaml` from the decisions, foundation, outline, existing manuscript,
   research, and entity state — keeping the provenance of each entry.
6. Register every imported file in the document registry.
7. For an upgrade rather than a new project, write `maintenance/MIGRATION_REPORT.md`.
