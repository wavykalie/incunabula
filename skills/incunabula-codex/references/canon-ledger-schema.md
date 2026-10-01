# Canon Ledger Schema

`CANON_LEDGER.yaml` is the deduplicated memory layer. It replaces nothing — not the
manuscript, not the foundation, not the outline, not the Voice Matrix, not the entity
tracker. What it does is answer, for every phase, which version of a fact or a contract
currently holds and where that version came from.

## Schema

```yaml
meta:
  schema_version: "1.0"
  project_id: ""
  updated: ""
  primary_state_file: ""        # STATE.yaml or PROJECT_STATE.yaml
  maintenance_run: 0

facts:
  stable-fact-id:
    subject: ""                 # an entity, a chapter, a world element, or the project
    predicate: ""               # has_age, lives_in, knows, occurs_on, sounds_like
    value: ""
    kind: "character"           # character|world|timeline|plot|research|style|formatting
    status: "active"            # active|planned|superseded|conflicted|uncertain|retired
    authority: "user_decision"  # user_decision|manuscript|foundation|outline|research|inference
    scope:
      series_id: ""
      book_id: ""
      start_book: null
      end_book: null
      start_chapter: null
      end_chapter: null
      applies_to: ""
    sources:
      - file: ""
        anchor: ""              # heading, paragraph, line, or YAML path
        evidence: ""
        observed: ""
    supersedes: []
    superseded_by: []
    conflicts:
      - fact_id: ""
        reason: ""
        status: "unresolved"
    duplicate_of: null
    last_verified: ""
    notes: ""

documents:
  relative/path.md:
    role: "foundation"          # state|assumptions|foundation|outline|voice|entity|manuscript|research|evaluation|delivery|working
    status: "active"            # active|redundant|superseded|archived|needs_review
    authority: "foundation"
    canonical_for: []
    last_reviewed: ""
    superseded_by: null
    archive_path: null
    reason: ""

voice_contract:
  global: {}
  characters: {}
  chapters: {}
  facts: {}

maintenance:
  last_run: ""
  last_run_by: ""
  changed_files: []
  merged_facts: []
  flagged_conflicts: []
  resolved_conflicts: []
  archived_documents: []
  unresolved_reviews: []
```

## Which source wins

When two values disagree, this is the order, unless the project has written down a
different rule of its own:

1. a decision the user made explicitly
2. approved manuscript text, read only as far as the chapter it actually appears in
3. an accepted revision or an editor's decision
4. `foundation.md` and `outline.md`, treated as intended canon rather than achieved canon
5. research with a citation
6. model inference, or a note nobody has approved

Newness is not authority. A statement written later does not outrank one written earlier.
Where two authoritative sources can both be true inside different chapter scopes, keep
both and record the scopes. Where they genuinely cannot both be true, keep the earlier
value, record the later one as a conflict, and ask for a decision.

## Stable IDs

Derive the ID from the normalized subject, predicate, and the value that distinguishes it:

- `mara-calloway.voice-under-pressure`
- `hollow-bridge.founding-year`
- `chapter-08.narration-register`
- `station-ledger.status`

In a series, the series-level entity ID stays fixed; facts that evolve between volumes get
`book_id` and chapter scope attached. Never open a second fact because a fact was reworded.
Merge the new source into the one that already exists and keep both citations.

## Status values

| Status | Meaning |
|---|---|
| `active` | current and in force |
| `planned` | accepted in planning, not yet true in prose |
| `superseded` | replaced by an approved fact; the old value and its replacement link stay |
| `conflicted` | two incompatible values are both still on the record |
| `uncertain` | plausible, unverified, and never to be treated as settled |
| `retired` | no longer applies because the plan changed |

Resolving a conflict keeps both values and both provenances. Record the decision, who or
what resolved it, and the date. Deleting the losing evidence is not a resolution.
`archived` is a document status, not a fact status.

## The voice contract block

The `voice_contract` section is the machine-readable index; the readable rules stay in
`voice-matrix.md` or `VOICE_CONTRACT.md`. A fact-presentation profile must distinguish at
minimum:

- narrated facts
- spoken facts
- research or factual claims
- documentary or epistolary facts
- memory
- rumour
- inference, or knowledge held with less than certainty

Each profile records register, how certain the statement is, what cues its source, how much
hedging is allowed, sentence rhythm, and any explanatory habit the voice must not fall into.
