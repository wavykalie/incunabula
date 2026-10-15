# Incunabula

A book-production pipeline for AI-assisted writing. It turns a one-line idea into a
manuscript. It keeps a plan, a continuity ledger, calibrated quality checks, and an
editorial package.

**An empty result is not a good result.** Every tool in this repository reports *not run*
as *not run*. No tool reports a pass for a check that did not run.

## The names

The tool names come from the letterpress shop that printed the first books: the platen,
the quoin, the forme, the case, the pull, the colophon. An *incunabulum* is a book printed
before 1501.

Each name has one meaning. The dictionary is
[`INCUNABULA_LEXICON.md`](INCUNABULA_LEXICON.md). It gives the plain meaning of every
term and of every row ID that a run can print (`U1`, `A1`, `N4`, and others).

## What you need

- Python 3.
- bash.
- Git.

Note: on Windows, "bash" means Git Bash. Git supplies it. Every tool here is a POSIX shell
script. There is no PowerShell version and no `.cmd` version.

Note: on Windows, set `PYTHONUTF8=1` before a session. Use the command
`export PYTHONUTF8=1`. Without it, Python writes its output in the code page of the
machine. One em dash then goes out as one `0x97` byte, and the terminal shows it as
junk. The checks measure the same data either way. The setting changes only the way you
read the output.

`pyyaml` is optional. Its absence is a known blind spot, and the tools report it. Without
`pyyaml`, the YAML-parse rows read
`SKIP - no YAML parser on this machine, parse NOT CHECKED`. They do not read as a pass.
`tools/ductus.py check` also exits 3. To make those rows real checks, install it:

```bash
pip install pyyaml
```

## Install

The skills are the instructions. The checks are what enforces them. You need both. The
skills name the checks by path in every quality check that they run.

1. Copy the skills into the skills directory of your agent:

```bash
# global
mkdir -p ~/.agents/skills && cp -r skills/* ~/.agents/skills/

# or in this project only
mkdir -p .agents/skills && cp -r skills/* .agents/skills/
```

2. Keep the checks in `tools/prose/` inside the clone. Do not copy them. The skills name
   those paths relative to the clone.

3. Run every command in this document from the root of the clone.

If the clone is not in your working directory, use the absolute path in the check
commands. That is the only change you must make.

4. Invoke the `incunabula` skill. The engine reads the contract layer in
   `incunabula-codex` during the run. Do not invoke `incunabula-codex` separately. The
   engine stops before phase one if the contracts do not exist.

## Check your install

Run these three commands in this order.

1. Check the checks. The freeze makes every published result traceable to a known
   instrument:

```bash
bash tools/prose/verify-freeze.sh
```

`FREEZE HOLDS` means that the checks are present and byte-identical to the checks that
measured every published result in this repository. Run this command first. An edited
check is the most dangerous event for this harness, and this command finds it.

2. Check that the scanner is not blind:

```bash
bash tools/prose/deslop-check.sh tools/prose/calibration/slop-fixture.md   # must FAIL
```

If this command does not fail, the scanner cannot see slop. Repair the scanner before you
use any other check.

3. Check the static state of the record:

```bash
bash tools/preflight.sh
```

`preflight.sh` prints one row for each known failure class. Each row carries its own
state, including the states where it could not look.

## Make your first book

This repository ships no books. A book is somebody's manuscript. What the framework ships
is the scaffold that makes one.

```bash
python tools/init-book.py --path test-books/my-book --title "My Book"   # scaffold and register
python tools/roll-brief.py --seed 7                                     # optional: roll a premise
bash tools/run-gates.sh test-books/my-book                              # exit 2 until it has chapters
```

`init-book.py` needs `--path` and `--title`. A `test-books/` prefix on the path is
understood, not duplicated.

`run-gates.sh` exits **2** on a book with no chapters. Exit 2 means *not run*. It never
means *pass*. The first run shows this rule: an empty book is not a passed book.

Two conditions follow from shipping no books:

- `python tools/check-registry.py` exits **2** and prints
  `registry exists but lists no books` until you register your own book. Not run is not a
  pass.
- `bash tools/prose/validate-controls.sh` exits **2** (PARTIAL) with no calibration
  corpus. Its own summary says this. You supply the reference prose. The limits are
  verified only after you do. See *Supply a calibration corpus* below.

## The two main skills

The two skills are not alternatives. The intended production setup uses both.

| Skill | What it is | What it does |
|---|---|---|
| `incunabula` | The production engine. 17 phases. One 32 KB entrypoint that calls every specialist skill and enforces every quality check. | It does the work. It never writes prose itself. |
| `incunabula-codex` | The contract layer. 19 reference files: the intake schema, the canon-ledger schema, the maintenance protocol, the evaluator protocol, and one prompt for each phase. It also holds an optional 8-phase compact pipeline. | It keeps the work durable. |

`incunabula-codex` holds the data that must survive between sessions and between agents:

- guided intake,
- voice contracts,
- canon tracking with recorded sources,
- safe pruning, and
- migration of projects that already exist.

It has three modes: **NEW**, **RESUME**, and **UPGRADE**. UPGRADE brings an existing
book project into the system in place. It does not erase the files that it finds.

The engine runs inside that layer and reads the same contracts. The two skills therefore
ship as a pair. The entrypoint of `incunabula` tells you to read the codex schemas before
phase one.

**The compact pipeline.** Use the 8-phase pipeline only when a project selects it. It
runs the same checks in 8 phases and does not call the specialist skills. Use it for a
small project or a short run. Do not use it by default, and never as a silent substitute
for the full engine. The pipeline explicitly forbids that.

### About the name `incunabula-codex`

The name is not related to OpenAI Codex, and it is not tied to any host. The name is kept
for compatibility with existing installs and shortcuts. The workflow runs on any host that
can read project files and write artifacts. Nothing in this repository needs Codex.

## The specialist skills

The engine never writes prose. It calls specialist skills. Each skill does exactly one
job.

| Job | Skill |
|---|---|
| Market research | `scout` |
| Reader personas | `readership` |
| Foundation document | `forme` |
| Voice specification for each character | `voice-matrix` |
| Entity-state tracking | `case-keeper` |
| Continuity audit | `collator` |
| Drafting (prose) | `setting` |
| Dialogue alignment | `register` |
| Opening and closing hooks | `catchword` |
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
| Reader swarm (crowd panels; `--light` = the four-voice market panel) | `reader-swarm` |
| Re-derivation under changed rules | `rewrite` |

Utility skills that are not part of book production keep their own names: `copy-editing`,
`deslopify`. The `skills/` directory holds 26 skills; retired skills are kept under
`skills/_archive/` with a `MOVED.md` shim naming their successor. One tool sits outside
the suite entirely: `bundles/good-idea/`, a video-idea validator kept as its own bundle.

## The gates

A **gate** is an automatic check that can fail the book. Two gates are required at every
phase. A third gate, the narrative gate, is required at evaluation and at delivery. No
gate is optional. No gate is satisfied by work that did not run.

### The prose gate

Four tools check the prose. They live in `tools/prose/` and ship with the pipeline. They
run before a chapter counts as drafted, before anybody reports a score, and before
anybody builds a package. All four tools run at every phase boundary. No tool replaces
another.

| Tool | Unit | What it fails |
|---|---|---|
| `deslop-check.sh` | one chapter | slop: per-1k rules, anaphora, duplication, fragment runs, and the closing coda as a *position* |
| `check-uniformity.py` | the whole book | monotony: chapter-length variance, rhythm spread, coda distribution, signature-frame spread, paragraph layout |
| `check-drift.py` | the whole book | a voice shift: a measurable change in sentence habits between the first chapters and the last |
| `check-arc.py` | the whole book | a flat emotional arc: a book whose direction never reverses |

Uniformity and drift fail on opposite problems, and you need both. `deslop-check.sh`
reads one chapter at a time, so it cannot see the shape of a book. A book can pass every
per-chapter limit and still be two different books joined together. The arc check asks a
third question: does the emotional direction of the story change at all?

While you draft a chapter, `tools/lint-chapter.py` shows the rule hits of the scanner at
drafting speed. It prints every hit as a `line:col` span in the chapter that you just
wrote. You can then repair the leverage trap and the participle run before assembly. The
tool reads the rules from `deslop-check.sh` at run time and holds no rules of its own.
Where the two disagree, the scanner is right. The tool is a drafting aid. It gates
nothing.

The rules of the instrument:

- **A limit is measured, never chosen.** A rule gets zero tolerance only if published
  prose never breaks it: zero occurrences in the calibration corpus. Every other rule
  gets a density limit. The measurements are in
  `tools/prose/calibration/CALIBRATION.md`. That file also records what was tested and
  rejected, so that nobody re-derives a metric and finds noise.
- **Validation has seven sides.** Published prose must pass three controls (the scanner,
  the uniformity check, the drift check). A synthetic slop fixture must fail the scanner.
  Machine-written prose must not all pass. A uniform manuscript must fail the uniformity
  check. A book whose voice changes must fail the drift check.
  `tools/prose/validate-controls.sh` runs all seven again and exits nonzero if one
  misbehaves.
- **Not run is never pass.** An empty scan is a failure. When the calibration corpus is
  absent, the control runner exits **2** (not run). It does not report success.
- **Planning documents are exempt.** Outlines, scene packets, and state files need
  precision. Their register is above the prose limits by design.

Passing the gate is necessary, and it is never enough. The gate cannot see voice, rhythm,
a dead metaphor, or one argument that the book states ten times. The read-aloud pass stays
in force.

### The narrative gate

The prose gate measures the surface of sentences. The narrative gate measures the shape of
the story. It reads one declared file, `NARRATIVE_LEDGER.yaml` at the root of the book,
with `tools/prose/check-narrative.py`. That tool reads no prose.

| Row | What it asks | Tier |
|---|---|---|
| `N1` narrative debt | Does every obligation that the book introduced with emphasis end as RESOLVED (payoff recorded) or DEFERRED (reason recorded)? OPEN at delivery is a failure. | **gates** |
| `N2` beat repetition | Do the declared per-chapter emotional arcs repeat? The same circuit four times is one scene four times. | reports |
| `N3` scene function | Do extended scenes declare the same function? `pure texture` is a budget that the author sets. | reports |
| `N4` ledger conformance | Schema, status discipline (RESOLVED without a resolution is a defect), staleness. A chapter that the ledger never saw cannot be shown to owe nothing. | **gates** |

An unexamined set-up is a failure, not a loose end. This is the story-level form of the
rule *not run is never pass*.

Three tools feed the ledger. `case-keeper` records debt at extraction pass 6.
`proof-panel` declares the beat arc of each chapter and the function of each extended
scene at Phase 4. `collator` audits the ledger against the text in both directions.

Three companions read prose and report only: `check-figurative.py`,
`check-dialogue-tags.py`, and `check-quantities.py`. No measured corpus stands behind
them, so they can report and cannot fail anything.

The narrative gate gates without a corpus for the same reason as `check-length.py`: it
compares a book with the obligations that the book declared for itself. No population can
produce a false failure. The gate also states what it cannot see: an unrecorded set-up
passes this gate perfectly.

Schema: `skills/incunabula-codex/references/narrative-ledger-schema.md`.

### The maintenance gate

The system reconciles state, canon, and the pruning log before it dispatches the work of
a phase, and again after the work finishes.

- The layer exists before the first phase. It is not built up later. `CANON_LEDGER.yaml`
  (series scope and book scope), the active voice contracts, and
  `maintenance/PRUNING_LOG.md` are prerequisites of Phase 0.
- **Never resolve a contradiction without a record.** Keep both values. Keep their
  recorded sources. Attach a conflict record. Escalate anything that touches content
  boundaries, the end of an ambiguity, or the core identity of a character.
- **Record a skipped step as skipped.** An absent artifact is a failure. Report it as a
  failure, not as a to-do item.
- **Verify each claim of the state against the files.** Read a state file with a real
  parser, not with an eyeball. A state file that does not parse is a FAIL.
- **The pruning log records restraint.** A decision *not* to prune, and a decision *not*
  to overrule a source, are entries.

## Supply a calibration corpus

The limits in `tools/prose/` were measured against published prose. That prose is
deliberately not shipped: it is somebody else's copyright.

Until you supply your own reference corpus, the checks still run and still catch
machine-written slop. The limits are then **unverified against human prose**: nobody has
measured them against published prose in this clone. `validate-controls.sh` exits 2, which
means *not run*, and it says so in those words. It never pretends otherwise.

To supply a corpus and fully validate the instrument:

1. Put reference prose in `calibration/corpus/<name>/`. Use one `.txt` file for each
   chapter. Name the files so that `check-drift.py` can sort them.

   Public-domain prose is a good choice and costs nothing.
   `tools/prose/calibration/fetch-multivolume.py` builds a multi-volume set. Controls 4-7
   need multi-volume prose, divided into volumes and chapters. The `--set` option selects
   the set: `fiction`, `nonfiction`, or `prescriptive`. Control 10 needs the non-fiction
   volumes.

```bash
# usage: fetch-multivolume.py <out-dir> [--set fiction|nonfiction|prescriptive] [--limit N]
python tools/prose/calibration/fetch-multivolume.py \
  tools/prose/calibration/corpus/multivolume --set fiction
```

Note: the script takes the output directory as its first argument. It is not a `--help`
style tool, and it downloads files when you run it.

2. Run every control:

```bash
HUMAN_CORPUS="calibration/corpus/<name>" \
VOLUME_CORPUS="calibration/corpus/<name>" \
  bash tools/prose/validate-controls.sh
```

   Exit 0 means ALL CONTROLS PASS, with the corpus named.

3. On a partial run (exit 2), read what the run proved and what it did not. The summary
   separates the two.

Note: do not treat a green partial run as full validation. Freeze 10 records that exact
failure.

Which limits need a corpus: every threshold in `deslop-check.sh`, `check-uniformity.py`,
and `check-drift.py`. `check-length.py` needs no corpus, because it compares a book with
what that book declared. The registry checks also need none.

## Reading guide

This repository holds two kinds of truth: the **framework** (works for any author) and
the **record** (the decisions, taste, and history of this installation). The record is
context. It is not an obligation. The files state which kind they are.

| Order | File | Kind | Why read it |
|---|---|---|---|
| 1 | `README.md` (this file) | framework | what the system is |
| 2 | `INCUNABULA_LEXICON.md` | framework | the dictionary: every term in plain words |
| 3 | `tools/prose/`, `tools/check-registry.py` | framework | the instrument; every skill calls these by path |
| 4 | `BOOKS.yaml` | framework (your copy will differ) | the registry that the suite reads; `init-book.py` maintains it |
| 5 | `DRAFTING_FRAMEWORK.md` | framework and rulings | the production rules, with the reasoning |
| 6 | `GATE_FREEZE.md` | framework, append-only | why results are traceable; the protocol for a change to any check |
| 7 | `ERRATA.md`, `PRINTERS_COPY.md`, `KNOWN_FINDINGS.md` | record | how limits earn changes; what was tried and rejected; what was left alone |
| 8 | `COMMONPLACE.md`, `SELF_IMPROVEMENT.md` | framework and record | the taste channel; what may promote itself without a person |

**The rule of thumb:** if a file records a decision that somebody made, the file is
evidence of the way this installation thinks. It is not a rule that you inherit.
`USER_PREFERENCES.md` is the clearest example: it is untracked on purpose. The framework
proper is the tools, the schemas in `incunabula-codex`, and the protocols. Everything
else is the log.

## What is in this repository, and what is not

Everything above is the book-production system. Three classes of file are not part of it:

- **Your books are not here.** Git ignores `test-books/` and `demo-books/`. The
  books that you write go there, stay on your disk, and never leave it because of a
  `git push`. Every path in every document still refers to those directories, because
  that is where the books live.
- **The record of this installation is not here.** The author's errata ledger, commonplace
  book, known findings, freeze history, registry, and books are kept beside the framework
  and are not tracked. The repository carries a template at each canonical path, so that
  the tools keep working on a fresh clone.
- **A separate project is not here.** A video pipeline once lived in this clone. No tool
  in this repository reads it, and a clone should not download it. It is now ignored by
  git and stays only on the machine that made it.

The same division runs through the records. The **framework** works for any author. The
**record** is what this installation decided.

## Scoring

The **Incunabula Score** is the *floor* across seven dimensions. It is not an average.

1. Originality
2. Theme
3. Characters
4. Prose and Voice
5. Pacing and Coherence
6. Emotion
7. Configurable (market, worldbuilding, epistolary, humour, or custom)

**The Platen** is the principle behind the score: the weakest link rule. The lowest
dimension presses the whole score down, because a book is only as strong as its weakest
impression. Six dimensions at 9.0 and one at 7.0 give a score of 7.0.

Two commercial indices sit on top of the score:

- **First Impression** predicts first-year sales. It uses commercial pacing, the Keepsake
  Test, the Passing Reader verdict, shareability, the concept pitch, and human closeness.
- **Standing Type** predicts twenty-year sales. It uses the craft dimensions directly,
  weighted by engagement type.

The two indices measure different things, and they may differ. When they differ by 2.0 or
more, the difference *is* the finding. A literary work can be commercially invisible. A
page-turner can be thin on craft.

### Anti-inflation

Self-evaluation has maximum bias, so the protocol is explicit:

- No score may jump by more than +0.5 in one revision cycle without textual evidence.
- Every score cites a specific passage. A number without a citation is invalid.
- A floor above 8.0 without extraordinary evidence gets a challenge.
- The benchmark difference between self-scored and calibrated evaluation is assumed to be
  −0.5 to −1.0.

## Engines of engagement

Every project declares a primary engagement type in Phase 2. That declaration changes the
behaviour of every downstream skill.

**Empathy** (feel what they feel) · **Fascination** (cannot look away) ·
**Self-Insertion** (I am the protagonist) · **Intellectual** (I am learning) ·
**Aspiration** (I feel special).

When the primary type and the secondary type conflict, that tension is the identity of
the book. The system does not resolve it.

## Project layout

A run produces a self-contained project directory:

```
{project}/
  STATE.yaml / PROJECT_STATE.yaml   the source of truth (parsed, never eyeballed)
  ASSUMPTIONS.md                    every inference labelled as an inference
  RUN_REPORT.md                     the exact unfinished task and resume step
  CANON_LEDGER.yaml                 facts with recorded sources and conflict records
  NARRATIVE_LEDGER.yaml             what the book owes: debt, beat arcs, scene functions
  foundation.md  outline.md  voice-matrix.md  readership.md
  manuscript/chapters/              one file per chapter
  evaluations/  continuity/  research/  delivery/
  maintenance/                      SESSION_LOG.md, PRUNING_LOG.md
  tools/                            prose/: the scanner, the two cross-chapter gates,
                                    the control runner, and the calibration record
```

## What the system will not do

- It will not report a check as passed when the check did not run.
- It will not resolve a contradiction by quietly picking one side.
- It will not let the agent that wrote a chapter also score that chapter.
- It will not accept a chat message as proof that a phase finished.

Files prove phases. Any person with a terminal can check the files again.

The last point is the whole design. The judgments in a run are judgments, and the system
labels them as judgments. The evidence, which is word counts, grep hits, parser exit
codes, and archive integrity, is not a judgment.

## How the system improves

The system adapts without a person in the loop, and it states the exact point where that
stops. [`SELF_IMPROVEMENT.md`](SELF_IMPROVEMENT.md) is the protocol. The system proposes a
change as a diff and adopts it only when the verifier stack falsifies the change: freeze
attribution, the controls, a closed-catalogue regression, and a held-out comparison. The
system reverts a change when a monitor regresses. `tools/preflight.sh` runs the static half
of the stack before a session starts.

### Taste, one layer down: the ductus

A **ductus** (`ductus.yaml`, `ductus/<slug>/`) is an authorial persona that an agent
pilots. `ductus.md` is the contract that the persona drafts under. `COMMONPLACE.md` is the
ledger of that voice. A voice exists because a person made one with
`python tools/ductus.py new <slug>`. It does not exist because the configuration file
lists it.

The system holds voices apart the same way that it holds channels apart. `ductus.py cross`
reports an entry that two voices both hold. Nothing crosses except a dated merge in
`ductus/PROMOTIONS.md`.

The layer is optional. With no voices declared, every book drafts under the root ledger.

### The three channels

Three channels exist: measurement, craft, and taste. A firewall separates them. Evidence
from one channel may never move another channel. A limit still needs a named corpus.
Declared preferences in `USER_PREFERENCES.md` are immutable to the loop. The only external
signals of the loop are the controls, the corpus, and reader outcomes. Prediction error is
the fitness signal, because a system with no outcome channel becomes more confident, not
better.

## Source of the checks

The freeze makes a result traceable. To see the same trace from the other side, read the
record of what each check was measured against:

```bash
bash tools/prose/verify-freeze.sh          # are the checks the recorded ones?
python tools/prose/check-errata.py         # is the ledger of corrections well formed?
python tools/prune-stale.py                # do the standing claims match the program?
python tools/errata-store.py check         # is the store behind ERRATA.md consistent?
python tools/check-registry.py             # does the registry agree with the disk?
python tools/ductus.py check               # do the voice contracts hold?
```

## Provenance

Incunabula is an original work, written and maintained by Kalie Kirch. The text of every
skill, contract, prompt, and reference file here was written for this system.

## Licence

MIT. See [`LICENSE`](LICENSE).

