# Incunabula

A book-production pipeline for AI-assisted writing. It turns a one-line idea into a
manuscript with a foundation, a continuity ledger, calibrated quality gates, and an
editorial package.

The system takes its vocabulary from the letterpress shop that made the first printed
books — the platen, the quoin, the forme, the case, the pull, the colophon. An
*incunabulum* is a book printed before 1501. The names are not decoration: every term
below maps to a specific artifact or gate, and the full mapping lives in
[`INCUNABULA_LEXICON.md`](INCUNABULA_LEXICON.md).

---

## The two skills

**These are not alternatives. The intended production setup is both together.**

| Skill | What it is | Role |
|---|---|---|
| **`incunabula`** | The production engine. 17 phases, a self-contained 32 KB entrypoint that dispatches every specialist skill and enforces every gate. Never writes prose itself. | the machine that does the work |
| **`incunabula-codex`** | The contract layer. Almost no prose of its own — 19 reference files: intake schema, canon ledger schema, maintenance protocol, evaluator protocol, and a prompt per phase. Plus an optional 8-phase compact pipeline. | the durability around the work |

`incunabula-codex` supplies what has to survive between sessions and between agents:
guided intake, voice contracts, canon tracking with provenance, safe pruning, and
migration of projects that already exist. It runs in three modes — **NEW**,
**RESUME**, and **UPGRADE** (bring an existing book project into the system in place,
without erasing the files it finds).

The full engine then runs inside that layer, reading the same contracts. This is why the
two are shipped as a pair and why `incunabula`'s entrypoint tells you to read codex's
schemas before phase one.

**When to use the compact pipeline instead:** only when a project deliberately selects it.
It runs the same gates in 8 phases rather than 17, and drops the specialist-skill
dispatch. Reach for it on a small project or a quick run, not by default — and never as a
silent substitution for the full engine, which the pipeline explicitly forbids.

### About the name

`incunabula-codex` is **not** tied to OpenAI Codex or any particular host. The name is
kept for compatibility with existing installs and shortcuts; the workflow runs anywhere
that can read project files and write artifacts. If you came here looking for something
that requires Codex, nothing in this repository does.

---

## Install

Every skill lives under `skills/`. The gates live under `tools/prose/`. **You need
both** — the skills are the instructions, the gates are what enforces them, and the
skills refer to the gates by path in every quality check they run.

```bash
# global (Claude Code, Codex, and other file-aware agents)
mkdir -p ~/.agents/skills && cp -r skills/* ~/.agents/skills/

# or project-local
mkdir -p .agents/skills && cp -r skills/* .agents/skills/
```

The gates stay where they are, in the clone's `tools/prose/`, and every command below is
run from the repository root. You do not copy `tools/` anywhere — the skills name those
paths relative to where you cloned, and that is how they are meant to be called.

If you keep the clone somewhere other than your working directory, use the absolute path
in the gate commands. That is the only thing that needs to change.

Then invoke `incunabula`. The contract layer in `incunabula-codex` is read by the engine
during the run — you do not have to invoke it separately, and the full engine will not
run phase one until those contracts exist.
No dependencies, no build step, no packages to fetch. The skills are plain Markdown and
YAML; the gates are Python 3 and bash, using only the standard library.

```
skills/incunabula/            the full 17-phase engine (SKILL.md + the lexicon)
skills/incunabula-codex/      the contract layer: schemas, protocols, phase prompts
                              (and the optional 8-phase compact pipeline)
skills/deslopify/             the anti-AI style guide the scanner is built on
tools/prose/                  the gates every skill calls
INCUNABULA_LEXICON.md         the term map used across every skill and artifact
```

### Supplying a calibration corpus (the one setup step with a decision in it)

The thresholds in `tools/prose/` were measured against published prose that is
**deliberately not shipped** — it is somebody else's copyright. Until you supply your
own reference corpus, the gates still run and still catch synthetic slop, but the caps
are **unverified against human prose**: `validate-controls.sh` exits 2 and says so in
those words. It never pretends otherwise.

Supply a corpus and the same command fully validates the instrument:

```bash
# 1. Put reference prose in calibration/corpus/<name>/ — one .txt file per chapter,
#    named so check-drift.py can sort it. Public-domain prose works well and is free:
#    calibration/fetch-multivolume.py builds a multi-volume set (controls 4-7 need
#    MULTI-VOLUME prose, split into volumes and chapters); the --nonfiction flag adds
#    the non-fiction volumes control 10 stages.
python calibration/fetch-multivolume.py --help

# 2. Run every control. Exit 0 = ALL CONTROLS PASS, with the corpus named.
HUMAN_CORPUS="calibration/corpus/<name>" \
VOLUME_CORPUS="calibration/corpus/<name>" \
  bash tools/prose/validate-controls.sh

# 3. On a partial run (exit 2), read what it proved and what it did not — the summary
#    separates them. Do not treat a green partial run as full validation; that exact
#    confusion is Freeze 10's recorded failure.
```

Which caps are affected: every threshold in `deslop-check.sh`, `check-uniformity.py`
and `check-drift.py`. `check-length.py` needs no corpus (it compares a book to what
that book declared); the registry checks need none.

### Demo books (runnable fixtures)

Three complete books produced by this pipeline ship under [`demo-books/`](demo-books/)
— manuscripts, state files, and the phase artifacts — so every gate can be run against
real books before you trust it on your own:

- **`demo-magician`** — *The Trick*, a 1930s conjuring mystery (34 chapters). The clean run: complete, swept, colophon built.
- **`muzzle-and-marrow`** — the from-scratch pilot. Its `U1`/`L1` failures are deliberately kept findings.
- **`marrow-light`** — 38 chapters; the book whose silent omission from a hand-typed suite list created the registry.

```bash
bash tools/prose/deslop-check.sh demo-books/demo-magician/manuscript/chapters
python tools/prose/check-uniformity.py demo-books/demo-magician
python tools/prose/check-length.py demo-books/muzzle-and-marrow   # kept L1 finding: exits 1
```

### Reading guide: what to read, in what order

This repository carries two kinds of truth: the **framework** (works for any author)
and **this author's record** (decisions, taste, history — context, not obligations).
The files tell you which they are:

| order | file | kind | why |
|---|---|---|---|
| 1 | `README.md` (this file) | framework | what the system is |
| 2 | `INCUNABULA_LEXICON.md` | framework | the vocabulary everything else uses |
| 3 | `tools/prose/` + `tools/check-registry.py` | framework | the instrument; every skill calls these by path |
| 4 | `BOOKS.yaml` | framework (your copy will differ) | the registry the suite reads; `init-book.py` maintains it |
| 5 | `DRAFTING_FRAMEWORK.md` | framework + rulings | the production rules, with the reasoning attached |
| 6 | `GATE_FREEZE.md` | framework, append-only | why results are attributable; the protocol for changing any gate |
| 7 | `ERRATA.md` / `PRINTERS_COPY.md` / `KNOWN_FINDINGS.md` | record | how thresholds earn changes; what was tried and rejected; what the author declined to fix |
| 8 | `COMMONPLACE.md`, `SELF_IMPROVEMENT.md` | framework + record | the taste channel and what may promote itself without a person |

**The rule of thumb:** if a file records a *decision someone made*, it is evidence of
how this installation thinks, not a rule you inherit. `USER_PREFERENCES.md` is the
clearest example — it is untracked on purpose. The framework proper is the tools, the
schemas in `incunabula-codex`, and the protocols; everything else is the log.

### Check your install in one command

```bash
bash tools/prose/verify-freeze.sh
```

`FREEZE HOLDS` means the gates are present and byte-identical to the ones every published
result in this repository was measured against. **Run this first.** A gate that has been
edited is the single most dangerous thing that can happen to this harness, and this is
the check that catches it.

Then prove it works, which needs no corpus and no setup of any kind:

```bash
bash tools/prose/deslop-check.sh tools/prose/calibration/slop-fixture.md   # must FAIL
```

If that does not FAIL, your scanner is blind and nothing else matters until it does.

---

## The specialist skills

The orchestrator never writes prose. It dispatches specialised skills, each named from
the print shop, and each responsible for exactly one job.

| Job | Skill |
|---|---|
| Market research | `scout` |
| Reader personas | `readership` |
| Foundation document | `forme` |
| Per-character voice spec | `voice-matrix` |
| Entity-state tracking | `case-keeper` |
| Continuity audit | `collator` |
| Drafting (prose) | `setting` |
| Dialogue alignment | `register` |
| Opening/closing hooks | `catchword` |
| Predictability-breaking pass | `quoin` |
| Mechanical cleanup | `composing` |
| Evaluation | `proof-panel` |
| Chapter quality loop | `proof-pull` |
| Revision | `corrector` |
| Editorial package | `colophon` |
| Production preparation | `presswork` |
| Project ledger | `press-ledger` |
| Series scope | `series-binder` |
| One-command run | `incunabula-auto` |
| Bestseller profile | `bestseller-studio` |
| Reader swarm | `reader-swarm` |
| Agent panel | `agent-panel` |

Generic craft language stays generic (*scene*, *chapter*, *beat*, *voice under
pressure*, *anti-AI scan*), and utility skills unrelated to book production —
`humanizer`, `copy-editing`, `deslopify`, `good-idea` — keep their old names.

---

## The pipeline

The full engine runs 17 phases. The compact `incunabula-codex` pipeline runs the same
work as eight.

```
PHASE 1     RESEARCH            scout
PHASE 1.5   READERSHIP          readership
PHASE 2     FOUNDATION          forme
PHASE 2.5   VOICE MATRIX        voice-matrix
PHASE 2.7   CASE TRACKING       case-keeper (BUILD)
PHASE 2.8   COLLATION (outline) collator
PHASE 3     WRITING             setting            (one chapter at a time)
PHASE 3.1   REGISTER            register
PHASE 3.2   CATCHWORD           catchword
PHASE 3.5   QUOIN               quoin
PHASE 3.7   CASE UPDATE         case-keeper (UPDATE)
PHASE 3.8   COMPOSING           composing
PHASE 4     EVALUATION          proof-panel
PHASE 4.5   PROOF PULL          proof-pull          (auto-loop, max 3)
PHASE 5     REVISION            corrector
PHASE 5.5   CASE UPDATE         case-keeper (UPDATE)
PHASE 5.6   COLLATION (ms)      collator
PHASE 6     DELIVERY            colophon + presswork
```

Agents run in sequence and never score their own fresh output: `proof-panel` must not
share the context that wrote the chapter, or the evaluation is worthless.

---

## The gates

Two gates are **required at every phase**; a third — the narrative gate — is required at
evaluation and at delivery. None is skippable, and none is satisfied by work that was
never run.

### The prose gate

Manuscript prose is checked by three tools — `tools/prose/`, shipped with the pipeline —
before a chapter counts as drafted, before a score is reported, and before a package is
built. All three run at every phase boundary; none subsumes another.

| tool | unit | what it fails |
|---|---|---|
| `deslop-check.sh` | one chapter | slop: per-1k rules, anaphora, duplication, fragment runs, and the closing coda as a *position* |
| `check-uniformity.py` | the whole book | monotony: chapter-length variance, rhythm spread, coda distribution, signature-frame spread, paragraph layout |
| `check-drift.py` | the whole book | a voice shift: stylometric step and trend between the first chapters and the last |

The last two are opposite failures and both are needed. `deslop-check.sh` never holds two
chapters at once, so it cannot see a book's shape; and a book can pass every per-chapter
cap while being one of two different books.

- **Thresholds are measured, never chosen.** A rule may be zero-tolerance only if
  published prose never does it — literally zero occurrences in the calibration corpus.
  Everything else gets a density cap. The measurements are in
  `tools/prose/calibration/CALIBRATION.md`, which also records what was **tested and
  rejected**, so nobody re-derives a metric expecting a rule and finds noise.
- **Validation is seven-sided.** Human prose must pass all three tools; a synthetic slop
  fixture must fail the scanner; a uniform manuscript must fail the uniformity gate; a
  book whose voice changes must fail the drift gate. `tools/prose/validate-controls.sh`
  re-runs all seven and exits nonzero if any misbehaves.
- **Not-run is never pass.** An empty scan is a failure, and when the calibration corpus
  is absent the control runner exits **2** rather than reporting success.
- **Planning documents are exempt.** Outlines, scene packets, and state files need
  precision; their register sits above the prose caps by design.

Passing the gate is necessary and never sufficient. It cannot see voice, rhythm, a dead
metaphor, or one argument restated ten ways. The read-aloud pass stays in force.

### The narrative gate

The prose gate measures the surface of sentences; the narrative gate measures the shape
of story. One declared file — `NARRATIVE_LEDGER.yaml` at the book root — checked by
`tools/prose/check-narrative.py`, which reads no prose at all:

| row | what it asks | tier |
|---|---|---|
| `N1` narrative debt | every obligation the book introduced with emphasis ends RESOLVED (payoff recorded) or DEFERRED (reason recorded); OPEN at delivery is a failure | **gates** |
| `N2` beat repetition | do declared per-chapter emotional arcs repeat — the same circuit four times is the book having one scene four times | reports |
| `N3` scene function | do extended scenes declare the same function; `pure texture` is a budget the author sets | reports |
| `N4` ledger conformance | schema, status discipline (RESOLVED without a resolution is a defect), staleness — a chapter the ledger never saw cannot be shown to owe nothing | **gates** |

An unexamined setup is a failure, not a loose end — the structural analogue of
"not-run is never pass". The ledger is fed by declarations: `case-keeper` extraction
pass 6 records debt, `proof-panel` declares each chapter's beat arc and each extended
scene's function at Phase 4, `collator` audits the ledger against the text in both
directions. Three prose-reading companions — `check-figurative.py`,
`check-dialogue-tags.py`, `check-quantities.py` — are report-only: no measured corpus
stands behind them, so they report and cannot fail anything. The narrative gate gates
with no corpus for the same reason `check-length.py` does: it compares a book to the
obligations that book declared for itself, and there is no population it can false-fail.
And it says what it cannot see: an unrecorded setup passes this gate perfectly.

Schema: `incunabula-codex/references/narrative-ledger-schema.md`. Provenance: Freeze 13
in `GATE_FREEZE.md`.

### The maintenance gate

State, canon, and the pruning log are reconciled **before** a phase's work is
dispatched and **after** it finishes.

- The layer exists before the first phase, not built up later. `CANON_LEDGER.yaml`
  (series and book scope), the active voice contracts, and
  `maintenance/PRUNING_LOG.md` are prerequisites of Phase 0.
- **Never resolve a contradiction silently.** Keep both values with their provenance,
  attach a conflict record, and escalate anything that touches content boundaries,
  ending ambiguity, or a character's core identity.
- **A skipped step is recorded as skipped.** An absent artifact is a failure reported
  as a failure, not a to-do item.
- **State claims are verified against files**, and a state file that will not parse is
  a FAIL — read it with a real parser, not an eyeball.
- **The pruning log records restraint too.** Decisions *not* to prune and *not* to
  overrule a source are entries.

---

## Scoring

The **Incunabula Score** is the *floor* across seven dimensions, not an average:

1. Originality
2. Theme
3. Characters
4. Prose & Voice
5. Pacing & Coherence
6. Emotion
7. Configurable (market, worldbuilding, epistolary, humor, or custom)

**The Platen** is the principle behind it: the lowest dimension presses the whole score
down, because a book is only as strong as its weakest impression. Six dimensions at 9.0
and one at 7.0 is a 7.0.

Two commercial indices sit on top:

- **First Impression** — predicts first-year sales. Commercial pacing, Keepsake Test,
  Passing Reader verdict, shareability, concept pitch, and human closeness.
- **Standing Type** — predicts twenty-year sales. Uses the craft dimensions directly,
  weighted by engagement type.

They measure different things and are allowed to diverge. When they diverge by 2.0 or
more, the divergence *is* the finding: a literary masterpiece can be commercially
invisible, and a page-turner can be craft-thin.

### Anti-inflation

Self-evaluation runs on maximum bias, so the protocol is explicit:

- No score jump above +0.5 per revision cycle without textual evidence.
- Every score cites a specific passage. A number without a citation is invalid.
- A floor above 8.0 without extraordinary evidence gets challenged.
- The benchmark delta between self-scored and calibrated evaluation is assumed to be
  −0.5 to −1.0.

---

## Engines of engagement

Every project declares a primary engagement type in Phase 2, because it changes how
every downstream skill behaves:

**Empathy** (feel what they feel) · **Fascination** (can't look away) ·
**Self-Insertion** (I am the protagonist) · **Intellectual** (I'm learning) ·
**Aspiration** (I feel special).

When the primary and secondary conflict, that tension is the book's identity. The
system does not resolve it.

---

## Project layout

A run produces a self-contained project directory:

```
{project}/
  STATE.yaml / PROJECT_STATE.yaml   the source of truth (parsed, never eyeballed)
  ASSUMPTIONS.md                    every inference labelled as an inference
  RUN_REPORT.md                     the exact unfinished task and resume step
  CANON_LEDGER.yaml                 facts with provenance and conflict records
  NARRATIVE_LEDGER.yaml             what the book owes: debt, beat arcs, scene functions
  foundation.md  outline.md  voice-matrix.md  readership.md
  manuscript/chapters/              one file per chapter
  evaluations/  continuity/  research/  delivery/
  maintenance/                      SESSION_LOG.md, PRUNING_LOG.md
  tools/                            prose/ — the scanner, the two cross-chapter gates,
                                    the control runner, and the calibration record
```

---

## What the system will not do

- It will not report a gate as passed when the gate was never run.
- It will not resolve a contradiction by quietly picking a side.
- It will not let the agent that wrote a chapter also score it.
- It will not claim a phase finished on the strength of a chat message. Files prove
  phases, and the files can be re-checked by anyone with a terminal.

That last point is the whole design. The judgments in a run are judgments and are
labelled as such. The evidence — word counts, grep hits, parser exit codes, archive
integrity — is not.

---

## The make-ready — how the system improves

The system adapts without a person in the loop, and says exactly where that stops.
[`SELF_IMPROVEMENT.md`](SELF_IMPROVEMENT.md) is the protocol: changes are proposed as
diffs, adopted only when the verifier stack falsifies them (freeze attribution, controls,
closed-catalogue regression, held-out comparison), and reverted when a monitor regresses.
[`COMMONPLACE.md`](COMMONPLACE.md) is the taste ledger — decisions, reader outcomes, and
emergent preferences distilled from three agreeing choices. `tools/preflight.sh` runs the
stack's static half before a session starts.

Three channels — measurement, craft, taste — with a firewall: evidence from one may never
move another. Thresholds still need a named corpus. Declared preferences in
`USER_PREFERENCES.md` are immutable to the loop. And the loop's only external signals are
the controls, the corpus, and reader outcomes; prediction error is the fitness, because a
system with no outcome channel becomes more confident, not better.

---

## Provenance

Incunabula is an original work, written and maintained by Kalie Kirch. The text of every
skill, contract, prompt, and reference file here was authored for this system.

## Licence

MIT. See [`LICENSE`](LICENSE).
