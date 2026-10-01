---
name: incunabula-codex
description: The contract layer for Incunabula — guided intake, voice contracts for character, chapter, and fact, durable canon tracking, safe pruning, and an upgrade path for projects that already exist. Read by the incunabula engine during a normal run; also hosts an optional 8-phase compact pipeline for small projects. Not tied to any particular agent or host despite the legacy folder name.
---

# Incunabula Universal Core — the portable pipeline

This is the portable upgrade and compatibility layer for file-aware agents: any tool that
can read project files and write artifacts. It runs anywhere that does.

The folder keeps the name `incunabula-codex` for compatibility with existing installs and
shortcuts, but the workflow is not tied to any one host. The default production route is
the full `incunabula` engine plus this layer; the compact eight-phase pipeline here is the
lightweight option, used when a project or an agent selects it deliberately.

Use it for fiction, memoir, nonfiction, or hybrid work; for turning a rough idea into a
structured book; for drafting chapter by chapter; for auditing machine-written prose and
structure; for producing a scored evaluation; and for synopses, cover briefs, launch
packages, and formatting handoff.

Do not quietly swap the compact pipeline in where the full engine was chosen.

## The one rule

Persist decisions to files. A run leaves a durable project tree, not chat.

## The layer

The full engine owns the phases. This folder supplies the contracts that wrap it — intake,
state selection, voice contracts, the canon ledger, contradiction handling, persistence,
migration, deduplication, and safe pruning — and it runs in three modes:

- **NEW** — run the intake contract before any foundation work.
- **RESUME** — load the primary state, the canon ledger, the voice contract, and the current phase prompt before acting.
- **UPGRADE** — migrate an existing project in place: keep its files, register their authority, import verified facts, and write a migration report. Where two state files exist, choose a primary by explicit decision, completeness, progress, and update evidence, and never erase the other.

Contracts live in `references/`: the intake schema, the canon ledger schema, the maintenance
protocol, the host contract, and the evaluator protocol.

The durable layers kept in step with each other:

- the state file (`STATE.yaml` or `PROJECT_STATE.yaml`)
- `ASSUMPTIONS.md` — explicit inferences
- `foundation.md` — premise, theme, characters, world
- `outline.md` — chapter architecture
- `voice-matrix.md` — global, character, chapter, and fact-presentation voice
- `ENTITY_STATE.yaml` — entity and knowledge tracking
- `CANON_LEDGER.yaml` — deduplicated facts with provenance, conflicts, supersession, and a document registry
- `maintenance/PRUNING_LOG.md` — append-only maintenance history
- `maintenance/SESSION_LOG.md` — append-only session entries

The first four are prerequisites of phase zero rather than things assembled later, and the
maintenance gate enforces that: a mandated artifact that was never created is a failure
reported as a failure, and a layer built late is recorded as a repair rather than backdated.

Before drafting, editing, auditing, or packaging, read the active canon entries and voice
contracts. Superseded material is not active canon.

Project layout:

```text
<project>/
  PROJECT_STATE.yaml
  ASSUMPTIONS.md
  RUN_REPORT.md
  premise.md              # optional, from the premise forge
  CANON_LEDGER.yaml
  maintenance/
    PRUNING_LOG.md
    SESSION_LOG.md
  artifacts/
  manuscript/chapters/
  evaluations/
  work/
  delivery/
```

## The compact pipeline

Load the phase manifest before starting or advancing.

1. Phase 0 — Intake
2. Phase 1 — Foundation
3. Phase 2 — Architecture
4. Phase 3 — Drafting
5. Phase 4 — Devil's audit
6. Phase 5 — Fine press loop
7. Phase 6 — Final score
8. Phase 7 — Colophon

Read only the prompt for the current phase: intake, foundation, architecture, drafting,
devil's audit, fine press loop, the scoring reference for the final score, and the
editorial-package prompt for the colophon. The orchestrator prompt carries the portable
orchestration rules, and the phases overview summarises the sequence.

## Operating loop

1. Read the host contract at start and on resume.
2. Locate the project directory, or create it.
3. Read the state, the assumptions, and the actual saved outputs. If the project is new, initialise from the project-state template.
4. Confirm the length contract before architecture or drafting; short-form positioning must be explicit.
5. Load the current phase prompt and produce only what that phase requires.
6. Update the state after every phase, chapter block, audit, or score, with real word counts and the length-gate status.
7. Do not skip the devil's audit; it comes before the fine press loop and before any final score.
8. Before any independent or final score, read the evaluator protocol and record the independence grade.
9. Draft into chapter files under the manuscript folder, keeping the state synchronised.
10. When feedback changes direction, record it in the project files before continuing.

## Quality policy

Prefer fewer constraints while drafting and repair afterwards. Keep drafting, audit,
scoring, and editorial judgment in separate hands. Apply the platen principle: the book is
only as strong as its weakest dimension. And check uniformity across chapters, not just
quality within them — chapters that are all the same length, all the same rhythm, or all
closing on the same rhetorical move are the clearest mechanical signature a finished book
carries, and no per-chapter check can see it. Sustained consistency is itself the tell. Write artifacts and prose in the project's language
unless told otherwise. And when the task is only editing, scoring, or packaging something
that already exists, enter at the matching phase rather than forcing a full restart.

## Complementary skills

Reach for these when they are available and relevant: `copy-editing` for prose cleanup,
`humanizer` for phrasing that has gone synthetic, a launch or content skill for go-to-market
material, and an image workflow for cover ideas.
