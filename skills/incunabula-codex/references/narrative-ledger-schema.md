# NARRATIVE_LEDGER.yaml — the book's declared obligations

**What it is.** One file at the book root, beside `CANON_LEDGER.yaml` and
`ENTITY_STATE.yaml`, recording three things a manuscript never states about itself:
what it promised (debt), what shape each chapter is (beats), and what each extended
scene is *for* (scenes). It is the structural layer's answer to a gap the prose gates
cannot close: `deslop-check.sh` measures sentences, `check-uniformity.py` measures
chapter shape, `check-drift.py` measures voice — and none of them can see a wound
introduced in chapter one and never mentioned again, or four chapters running the same
emotional circuit.

**Who writes it.** `case-keeper`, in extraction pass 6 (debt) and at UPDATE (folding in
declarations). Beat arcs and scene functions are *judgments*, so they are declared by
`proof-panel` at Phase 4 and by the outline at Phase 2 respectively, and case-keeper
records them without altering them. `collator` audits the ledger against the manuscript
at every batch and full pass. `check-narrative.py` (rows N1–N4) validates it.

**Who reads it.** `collator` (unpaid-setup audit against declared debt), `corrector`
(revision planning from open debt), `catchword` (hooks from open obligations),
`series-binder` (deferrals that seed the next volume), `colophon`/`presswork` (the
delivery gate: no OPEN debt ships).

---

## Shape

```yaml
meta:
  version: "1.0"
  last_updated: "YYYY-MM-DD"
  last_updated_by: "case-keeper"
  chapters_tracked: [1, 2, 3]

beats:
  - { chapter: 1, arc: "overload -> anchored by touch -> release -> calm", source: "proof-panel" }

scenes:
  - { chapter: 2, scene: "the bath", function: "theme payoff", words: 1400, source: "outline" }

debt:
  - { id: D-001, kind: trauma, description: "the Minato pod - forty hours, three corpses",
      opened: "ch-01:p22", status: OPEN, resolution: null, resolved_at: null,
      deferred_reason: null }
```

**The parser is strict and stdlib-only** (`check-narrative.py` ships with no
dependencies, like every tool in `tools/prose/`), so the accepted subset is exactly
this: top-level sections; `key: value` maps; lists of **one-line flow maps** or scalars;
quoted strings, `null`, booleans, integers, and `[a, b]` lists. Full-line comments only.
Anything else fails the parse loudly (N4, exit 1) rather than being half-read — a
ledger whose rows are silently dropped hides the very debts it exists to show.

## The closed vocabularies

Closed lists are what make the checks mechanical. A declaration outside a list is a
conformance failure (N4).

| field | allowed values |
|---|---|
| `debt.kind` | `mystery` `trauma` `character` `clock` `promise` `threat` `object` `skill` |
| `debt.status` | `OPEN` `RESOLVED` `DEFERRED` |
| `scenes.function` | `relationship shift` `theme payoff` `plot turn` `character revelation` `pure texture` |

## Status discipline (this is the whole point)

- **OPEN** — introduced with emphasis, not yet paid off. Every OPEN entry at delivery
  is an N1 **failure**. An unexamined setup is a failure, not a loose end: this is the
  structural analogue of "not-run is never pass".
- **RESOLVED** — the payoff is on the page. Requires `resolution` (what happened) and
  `resolved_at` (`ch-XX:pYY`). Recorded by case-keeper when extraction pass 4/6 sees
  the payoff fire — the gun goes off, the letter is read, the promise is kept.
- **DEFERRED** — deliberately carried forward (series hooks, intentional ambiguity).
  Requires `deferred_reason`. **Deferral is legitimate; silent abandonment is not.**
  The tool checks that a reason was written down. It cannot check that the reason is
  good — that is the author's ruling, and a deferral the author has not ruled on
  should say so in its own reason text.

## What counts as debt

Anything introduced **with emphasis** that creates an expectation: mysteries, traumas
(core wounds), named secondary characters given weight, ticking clocks, promises,
threats, loaded objects, taught skills. Not every detail pays off — a meaningful share
of any book is pure texture — so the bar is *emphasis*, the same bar `collator`'s
unpaid-setup audit already uses. When unsure, record it with the uncertainty in the
description; a false entry costs one line, a missing one costs a plot.

## Beats and scenes

- **beats** — one row per chapter: a one-line emotional arc in `->` form. This is a
  summary a reader could disagree with, which is fine: N2's repetition check is
  report-only and a repeated circuit is sometimes deliberate. What the row buys is
  durability — the arc is on record across sessions, so the *same* circuit appearing
  four times becomes visible instead of living in one evaluator's memory.
- **scenes** — one row per extended scene (a scene carrying narrative weight at length,
  roughly 800+ words), with `function` from the closed list. `words` is optional but
  makes the pure-texture share computable. Two scenes declaring the same function is
  reported (N3), never failed: duplication of function is a judgment call, and
  "pure texture" is a budget the author sets, not a cap this directory invents.

## Staleness

`meta.chapters_tracked` must cover every chapter file on disk. A chapter the ledger has
never seen cannot be shown to owe nothing, so a stale ledger **fails at delivery** and
is merely noted while the book declares `status: in_progress` (mid-draft staleness is
normal — chapters arrive between case-keeper UPDATEs).

## Absences, spelled out (the check-length rule)

| condition | meaning | N1 verdict |
|---|---|---|
| no `NARRATIVE_LEDGER.yaml` | the book is **ungoverned** (exit 3) | not a pass, not a fail |
| ledger present, all sections empty, `chapters_tracked` empty | **not run** (exit 2) | never a pass |
| book declares `status: in_progress` | **recorded** (exit 4) | enforced the moment the status is gone |
| ledger parses, covers the book, no OPEN debt | **clean** (exit 0) | pass |

An absence is not a decision. A book with no ledger has not declared no obligations —
nothing has been able to ask it what it owes.

## Why this gates with no corpus

`check-narrative.py` reads no prose and measures no population: it compares a book to
the obligations *that book declared for itself*, exactly as `check-length.py` (L1)
compares a book to its declared length. "There is no population it can false-fail."
Every prose-reading companion in the narrative class (`check-figurative.py`,
`check-dialogue-tags.py`, `check-quantities.py`) is **report-only** for as long as no
measured corpus exists behind it — the same line this directory has always drawn.

## What this file is not

It is not a plot outline (`outline.md` plans; this records what the plan became), not
entity state (`ENTITY_STATE.yaml` says what is true; this says what is owed), and not a
scoring input on its own. A book can owe nothing and still be bad; a book can carry a
deferred thread and still be complete. The ledger closes one question — *did the book
pay what it promised* — and leaves every other question where it was.
