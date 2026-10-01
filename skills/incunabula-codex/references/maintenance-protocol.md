# Maintenance and Upgrade Protocol

Runs on both sides of every meaningful unit of work: a session, a chapter, a revision, an
audit, a decision. Its purpose is to keep the project coherent without ever rewriting canon
behind the author's back.

## 1. Work out which mode you are in

- **NEW** — no project state, no manuscript.
- **RESUME** — Incunabula state exists and the user wants to keep going.
- **UPGRADE** — a project exists but predates the canon ledger or the voice contracts.
- **REPAIR** — the state or the ledger is malformed, contradictory, or out of step with the
  files. Stop before overwriting anything and report the boundary of the damage.

Look for `STATE.yaml`, `PROJECT_STATE.yaml`, `ASSUMPTIONS.md`, `foundation.md`,
`outline.md`, `voice-matrix.md`, `ENTITY_STATE.yaml`, chapter files, evaluations, and
delivery files.

## 2. Bringing an existing project up to date, in place

1. Read `STATE.yaml` and `PROJECT_STATE.yaml` if both are present.
2. Choose the primary one — explicit user decisions first, then completeness, then how far
   each has progressed, then last-modified evidence. Never delete or overwrite the other.
3. Register the non-primary state file in the ledger as historical, planned, or
   `needs_review`.
4. Import facts that can be verified, from foundation, outline, Voice Matrix, entity state,
   manuscript, research, and decisions.
5. Facts that live only in planning documents come in as `planned`. Facts established in
   approved prose come in as `active`.
6. If `voice-matrix.md` exists, extend it with the chapter and fact-presentation contracts.
   Create `VOICE_CONTRACT.md` only when extending the existing file would make it less
   coherent than a fresh one.
7. Write `maintenance/MIGRATION_REPORT.md` listing what was imported, which state file was
   chosen as primary, which conflicts remain open, and which assumptions were inferred.
8. Do not rewrite existing chapters and do not quietly settle a contradiction during
   migration.

## 3. Check-in

1. Open the primary state file, `CANON_LEDGER.yaml`, the recent session entries, the prompt
   for the current phase, and anything that changed.
2. Reconcile chapter status and word counts against the chapter files themselves.
3. Run a fact scan over what changed:
   - names, dates, places, objects, rules, relationships, knowledge transfers
   - character traits and voice markers
   - a chapter's narrator, tense, register, or limits on what it knows
   - research claims and factual assertions
4. Merge exact and rephrased duplicates into the fact IDs that already exist.
5. Attach source citations and refresh `last_verified`.
6. Where a new value contradicts an authoritative one, open a conflict. Do not overwrite.
7. Flag any fact whose source was edited away, whose chapter scope has ended, or whose
   planning document has been superseded.

## 4. Check-out

1. Write the primary state file.
2. Write `CANON_LEDGER.yaml` and the human-readable voice contract.
3. Append a session entry: decisions, files changed, facts merged, conflicts, next step.
4. Append to `maintenance/PRUNING_LOG.md`.
5. Register new documents with their authority and status.
6. Re-run the gate for the active phase before claiming any progress.

## 5. Duplicate detection

Two facts are duplicates when their normalized subject, predicate, value, and chapter scope
all match — even when the wording differs. Merge them into one record and keep every source.

Two documents are redundant when the newer canonical file carries the same purpose and the
same information. Mark redundant first. Archive only once no active phase still reads it.

## 6. Facts that are stale

- Replaced by an approved revision? Mark the old fact `superseded` and link `superseded_by`.
- Both statements still standing in the manuscript? Mark the ledger `conflicted` and raise a
  review item with the evidence attached.
- Planned, then removed before drafting? Mark `retired` — never delete.
- Cannot be verified? Mark `uncertain`, and do not let it drift into canon by default.
- Resolved by a decision from the user or an editor? Keep both values and both provenances,
  mark the conflict record resolved, set the fact to `active` or to whatever scoped status is
  now correct, record who resolved it, and move the ID from `flagged_conflicts` to
  `resolved_conflicts`.
- A trait that legitimately changes over time is not a contradiction. Keep both values with
  chapter scope.

## 7. Pruning and archival

Pruning reduces what has to be in context. It does not erase history.

- Canonical source documents are never deleted automatically.
- Clearly superseded working documents move to `archive/superseded/` only when automatic
  archival is enabled or the user approves it.
- The ledger keeps the original path, the archive path, the reason, the replacement
  document, and the date.
- A new subdirectory under `_archive/` gets an entry in `_archive/README.md` in the same
  commit that creates it.
- `maintenance/PRUNING_LOG.md` is append-only.
- Anything referenced by the active phase, by a pending handoff, by an unresolved conflict,
  or by a user decision does not get archived.
- Do not collapse facts that are distinct merely because they share a subject. In a series,
  the entity stays the same entity while role, age, location, knowledge, and relationships
  move between books.

### 7a. Archiving must not disarm a gate

The rules above govern *files*. They do not govern the gates' view of where those files
live, and that gap has already cost a manuscript.

- A file may be archived **out of a book's own directory** only if no gate in
  `GATE_FREEZE.md` reads that path. Otherwise the archive location is still the book root,
  or a stub is left behind pointing at the archive.
- A rewrite that re-chapters a book archives **the manuscript it replaces**, in the book,
  before writing the new one — not just the metadata. The 7 → 11 re-chapter of
  `validation-series` archived its outline, ledgers and audits correctly and overwrote seven
  chapter files in place; those chapters survived only inside an already-built EPUB.
- Confirm the pre-rewrite manuscript is readable **outside the live book directory** before
  treating the rewrite as done.
- **An archive needs an index, written in the same commit that creates it.** `_archive/`
  had none until 2026-09-29, and for that time a complete checkout of the framework's
  previous version — `hollow-bridge/book-genesis-v4/`, 19 skills, its own git history — sat
  there unread. An unindexed archive is not an archive; it is a directory nobody is
  allowed to delete. The index is `_archive/README.md`.
- **Do not assume an archived subtree is old manuscript.** Some of it is prior
  *framework*. Check the index before writing a provenance line that calls something
  superseded.

Nothing will report a violation of this. Every gate stays green while a book version is being
erased, because the gates read the *current* manuscript and that one is complete. A frozen
gate over missing inputs passes.

## 8. What each downstream phase should read

| Phase | Reads |
|---|---|
| Drafting | primary state, ledger, foundation, outline, voice contract, relevant entities |
| Editing | all of the above, plus conflicts, supersession links, and the pruning log |
| Continuity audit | entity state first, then ledger conflicts, knowledge flow, timeline, manuscript evidence |
| Scoring | the current manuscript and state; the ledger only to check intended contracts, never to inflate a score |
| Packaging | current state, approved manuscript, live editorial files; archived working documents only when tracing provenance |

## 9. Where the agent has to stop and ask

Merging, linking, classifying, and archiving may be done under this protocol. Stop when:

- two user decisions contradict each other
- the primary state file cannot be identified
- archiving something would destroy the only copy of a fact
- the change would alter content boundaries, how ambiguous the ending is, or a character's
  core identity
- a YAML parse error would have to be fixed by overwriting existing state
