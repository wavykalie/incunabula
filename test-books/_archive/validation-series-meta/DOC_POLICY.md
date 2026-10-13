# Document policy — the registry, the checks, and the reconciliation loop

This project's deliverable is not the books; it is the **persistent layer** that lets a later session
resume without re-deriving anything. That layer is a set of documents, and a document nobody verifies
will drift. It already did: a ledger said "no prose exists" about a delivered book, and
`foundation.md` and `outline.md` disagreed about ch.4's structure. Both escaped every gate. This file
is the policy those checks enforce.

## 1 · The registry

Every document is accounted for in a `documents:` block inside a cannon ledger:

- `CANON_LEDGER.yaml` — series scope, paths are repo-relative
- `book-1/CANON_LEDGER.yaml` — book scope, paths are book-relative
- `book-2/CANON_LEDGER.yaml` — book scope, paths are book-relative

Each entry carries `role`, `status`, `authority`, `canonical_for`, `last_reviewed`, `superseded_by`,
`archive_path`, and `reason`. A registered path resolves relative to the ledger that records it.

## 2 · Coverage

**Every `.md`, `.yaml` and `.yml` in the repo must be registered**, except:

- `manuscript/` — governed by the continuity audits, not the registry
- `dist/` — build output
- `archive/` — out of active context on purpose (its files are reached through `archive_path`)

Nothing may hide from the registry. If a file exists and no ledger names it, the check fails.

## 3 · Disposition of a superseded document

When a document stops being live, set `status: superseded` and a `superseded_by`, then choose one:

- **archive it** — set `archive_path` to its new home under an `archive/` directory; or
- **retain it in place** — set `retained_in_place: true` and give the reason. This is for documents
  that are themselves the evidence of a decision (the engine samples, the rejected delta options).
  Moving them would destroy what this project exists to prove.

A superseded document with neither is a failure.

## 4 · The checks

Run `tools/run-checks.sh` at every phase gate and at run close. It runs:

| Check | Enforces |
|---|---|
| `tools/check-structure-drift.sh` | the structural ledger agrees between `foundation.md` and `outline.md` |
| `tools/check-stale-status.sh` | a state/planning file does not contradict its own status fields |
| `tools/check-docs.py` | registry coverage, existence, supersession, archive policy, references, duplicate records |

Two tiers, deliberately:

- **ENFORCED** exits nonzero and blocks the gate: a registered-but-missing file, an unregistered
  file, a supersession or archive inconsistency, a broken file reference, a duplicate record.
- **REVIEW** is reported and never fails: a stale `last_reviewed`, a duplicate canon claim. `README.md`
  and the continuity reports are always REVIEW-only, because they narrate history and a past-tense
  sentence is normal there.

Dated records (`maintenance/SESSION_LOG.md`, `PRUNING_LOG.md`) and `artifacts/*` are **not scanned** by
the status check: they hold past and present together on purpose. References to `.agents/**` are not
broken links — those skills live with the harness, not the repo.

## 5 · The reconciliation loop

1. **Run** the checks.
2. **Reconcile** each ENFORCED finding: correct the stale prose, register the missing file, set the
   supersession or archive fields, fix the reference.
3. **Prune** by marking and archiving — never by deleting. Per the maintenance protocol §7, pruning
   reduces active context; it does not erase history.
4. **Log** the change in `maintenance/SESSION_LOG.md`, and keep the superseded wording in
   `maintenance/PRUNING_LOG.md`.
5. **Re-run** until the gate is green.

The check **verifies; it does not rewrite**. A scanner never silently edits canon — that would break
the project's own `no_inference_rule`. It flags, a human or agent reconciles, and the log records it.

## 6 · What this does not do

The checks are mechanical. They catch a bounded class: a file contradicting its own status fields, two
ledgers disagreeing, registry drift, dead references. A stale *narrative* sentence with no status field
beside it is still a read, not a scan. Reconciliation is a step in the run, not a replacement for
reading.
