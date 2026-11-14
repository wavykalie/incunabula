---
name: ductus-designer
description: Designs a book's ductus — the authorial voice contract — from what the voice should be in plain words and 2–5 passages of text that sound like it. Runs the corpus-fit check first, naming every dimension where the calibration corpus will fight the voice and which gate caps sit between them, then hands voice-matrix a target register. Use after the premise and before forme.
---

# Ductus-designer — building a voice from what the author wants

*Ductus* is the individual character of a writing hand. This skill designs one **for a
book**: what it sounds like, what it refuses, how it breaks under pressure, and the lines a
reader can blind-sort it by. It writes a contract. It never writes the book's prose.

The skill exists because nothing else in the pipeline chose a register. `voice-matrix`
realises a register from `foundation.md`; it does not select one. `register` polishes
dialogue and never touches narration, which is where a flat voice lives. `forme` builds
the foundation. A book could therefore be drafted under a contract nobody authored and
still pass every gate, because the gates measure distance from a corpus and the corpus was
never the register the book wanted.

## Position in the pipeline

**Phase 1.8** — after the premise exists, before `forme` opens Phase 2.

```
1.8    Ductus              ductus-designer
2      Foundation          forme
2.5    Voice matrix        voice-matrix      (consumes ductus.md as the target register)
```

The contract is **frozen before chapter one**. A change after drafting starts is a dated
decision in the voice's ledger, not a polish pass: a book half-written under one voice and
half under another is the cross-chapter drift `check-drift.py` was built to catch.

If the premise does not exist yet, stop. A ductus designed before the book knows what it
is becomes a costume the characters have to wear.

## Inputs

Gather four things. The first two are required.

1. **The want, in the author's own words.** Verbatim, not paraphrased. *"High-octane,
   moment-to-moment action, funny, American, sentences that move."* One or two sentences is
   enough, and the awkwardness is data: the want is the thing the corpus cannot measure.
2. **2–5 resonant excerpts, each with its source.** Passages the author points at and says
   *this*. See *Excerpts* below for how to store them and why they are untracked.
3. **An anti-voice** (optional): text the book must not sound like, or a named register it
   refuses. This is the cheapest input in the skill and the most under-used: a voice is
   defined as sharply by what it declines as by what it does.
4. **Book context** (optional): premise, genre, length, market lane, and the series it
   belongs to.

You also need the book's assignment. Resolve it before anything else:

```bash
python tools/ductus.py contract <book-root>
```

- **A contract prints** — that press voice is the *parent*. The book's `ductus.md` is
  written under it: its Register, Refusals and Breaking are binding, and this skill makes
  them specific to this book without contradicting them.
- **UNASSIGNED** — the book has no parent voice. Design the ductus from the inputs alone
  and record `parent: none` in Provenance. That is a legitimate state, not a gap.
- **REFUSED** — the assignment names a voice whose contract is a skeleton. Stop and report.
  Do not design a book contract on top of a voice nobody authored.
- **A series layer prints too, when the book belongs to one.** `series:` in `BOOKS.yaml`
  names it, and the contract resolves **book → series → voice**, naming every layer it
  used. The series contract (`<ductus dir>/<voice>/series/<series>.md`) binds this book the
  way the parent does: the book may tighten it and may never loosen it. A book that
  declares a series with no contract is REFUSED, not defaulted, because every volume after
  it inherits the layer.

## Excerpts

Store them with the book, one file each:

```
<book>/ductus/excerpts/01-killing-floor.txt
<book>/ductus/excerpts/02-the-blade-itself.txt
```

Each file starts with a source line, or the report cannot attribute anything:

```
---
source: Lee Child, Killing Floor (1997), ch. 1
---
Then the passage, as plain text.
```

**The excerpts are local-only, untracked, and never shipped** — same handling as the
calibration corpus (`tools/prose/calibration/.gitignore`). Quoting them into `ductus.md`
is fine because `test-books/` does not ship; the quoted samples never reach the packaged
book, the query letter, or a public repository. If the contract ever leaves the tree,
replace the quotes with paraphrases that preserve the rhythm.

Draw at least **500 words total** — a page or more per excerpt, 2–5 excerpts. The tool
refuses to judge fit below that, and it is right to: at 300 words a per-1,000-word rate is
one or two hits, and the report would be a verdict about type, not about voice.

Before any excerpt, quoted line or benchmark leaves the book tree, run
`python tools/prose/check-excerpts.py <book-root>`. It fails on a missing source line, on
fewer than 500 pooled words, and on any git-tracked file that carries an 8-word run from
the excerpts — the threshold in `SOURCE_POLICY.md` for `local-copy` text.

## The step that matters: the corpus-fit check

**Run this before writing the contract.** It is the step that would have caught the failure
this skill was built for — a finished, gate-passing book whose voice was correct by the
corpus's measurements and flat to its reader.

```bash
python tools/prose/ductus-fit.py <book-root> --lane action-voice \
  > <book>/ductus/ductus-fit-report.md
```

The tool measures the excerpts and the lane's corpus with the same arithmetic, per
document, and reports each dimension three ways: the excerpt's value, the corpus's worst
single document, and the gate cap that sits between them. Every row lands in one of four
states:

| State | Meaning | What it means for the contract |
|---|---|---|
| **BLOCK** | The excerpt is at or past the gate cap. | Prose written in this register fails the gate as it stands. Name it. |
| **FIGHT** | Inside the cap, but outside anything the corpus does. | The cap is 1.5× the corpus's worst document, so this register lives in the headroom. The corpus has no evidence for it. |
| **SUPPORTED** | Inside the corpus's own range. | The corpus can measure this book. |
| **NOT RUN** | Corpus absent, too small, or excerpts too short. | The fit is unmeasured. Say so; never record it as supported. |

**BLOCK and FIGHT are findings, not refusals.** The skill does not fix them. It writes them
into `## Corpus fit` with the row, the excerpt's number, the corpus's worst, the cap, the
headroom, and one sentence on what the fight costs the book. Recommending corpus additions
is a **separate action** — see *Guardrails*.

Read the whole report, not only the fights. A dimension the excerpt and the corpus agree on
is evidence the corpus can measure this voice; a dimension where they disagree is the
reason the contract needs numbers rather than adjectives.

Two artifacts in the report are always checked by hand, because they can be formatting
rather than style:

- **Dashes spelled `--`.** A plain-text excerpt with no em dashes reports D1 0.00 for
  typography, not voice. The tool says so; do not read it as restraint.
- **One excerpt carrying a whole dimension.** If a single excerpt produces every BLOCK,
  the excerpt is a scene and not a register. Say which excerpt, and treat that dimension as
  a per-scene choice until the author confirms it is book-wide.

## The contract

Write `<book>/ductus.md`, beside `foundation.md`. The first five sections are exactly the
five `tools/ductus.py` already reads — Identity, Register, Refusals, Breaking, Benchmarks —
so the engine, `voice-matrix`, `register` and `ductus.py audit` treat this file the way
they treat a press contract. Sections after those are this skill's own record.

```markdown
# <Title> — ductus

*A ductus* — the individual character of this book's writing hand.

**Status: WISH, unfalsified as of <date>.** A ductus is a hypothesis about how the book
sounds until prose drafted under it either holds or breaks it. Two things falsify it: the
blind sort fails, or a drafted chapter cannot pass the gates without breaking a Refusal.

**Parent:** <press ductus slug, or none>

## Identity

Who this voice is when it writes: not a biography, a temperament. What it is drawn to,
what it refuses to be impressed by, what it assumes about the reader. Written in the
present tense and specific enough to lose an argument with.

## Register

The book-level narrative register: point of view and what the voice can know; sentence
architecture with a target mean and a range; rhythm — how paragraphs open and close, what a
paragraph may not close on; diction with its roots and jobs; metaphor sources and the ones
refused; humour and heat (does the book have them, where, and when humour leaves); what the
narrator sees first and never notices; description density on the Balzac–Chekhov line.

### Anti-pattern budgets

Voice-matrix's format, tightened to this book. Two kinds:

**Failures (zero tolerance) —** the constructions this voice cannot use at all, each with
one line of why. Every character sharing one rhythm, literary metaphors in an
unschooled mouth, voice under pressure identical to voice at rest, narrator register
bleeding into thought, simile extension, dialogue that reads like therapy.

**Budgets (per chapter, max) —** a table: forced symmetry, empty poetic vocabulary,
automatic rule-of-three, em-dash pile-ups, metaphors that could apply to anything, dramatic
*And* openings, pseudo-philosophical closings, named emotions ("a wave of"), binary
negation openers, fake-precise numbers, thematic saturation, orderly turn-taking dialogue.
Where the corpus-fit report measured a row, the budget cites the number; where it did not,
the budget is a judgement and is marked as one. **No budget may sit above a gate cap that
the report shows the register already trips** — that is a budget written to pass the gate,
not to serve the voice.

## Refusals

The moves it declines even when they would work. A voice with no refusals is a house style.
Each one names the alternative it prefers, so a writer under pressure has somewhere to go.

## Breaking

What happens to the sentences under pressure: what it stops doing, what it does badly, and
what survives last. Where the voice has a measurable failure mode, state its invariants in
the form `tools/ductus.py` can read —

```
no higher than 38 per 10,000
```

— so the same contract can be measured against a drafted book. A failure mode with no
number is a description; a number with no failure mode is a gate.

## Benchmarks

Three to five lines in this voice, **quoted from the resonant excerpts with their sources**,
long enough to blind-sort. Each carries the one technique it demonstrates, so a writer
re-reads it as a target rather than as admiration.

> "<line>" — <source>. Carries: <the technique>.

## Corpus fit

Paste the tool's table and fights verbatim, then one paragraph: which lane governs this
book, whether the corpus can measure this register, and what the fight costs. If the run
was NOT RUN, say that and why — a fit report that reads as a pass it did not earn is worse
than no report.

## Provenance

- **Want, as stated:** the author's words, verbatim, in a block quote.
- **Excerpts:** path, source, and word count for each.
- **Lane:** which corpus governs, and the date its profile was measured.
- **Fit report:** `ductus/ductus-fit-report.md`, sha256:<12 hex>.
- **Blind sort:** pass/fail, who ran it, and the material it was run on.
- **Designed:** <date>, by <who>.
- **Conflicts:** any place the stated want and the resonant text disagree. See below.

### Conflict, when there is one

The want and the excerpts will sometimes pull apart — the author asks for kinetic and
submits reflective pages. **State it; never average it.** The house failure is a contract
standing halfway between two voices, which is no voice and which no gate can see.

> **Conflict —** the want says *moment-to-moment action*; the excerpts are reflective
> (mean sentence 21 words, 0.4 em dashes per 1,000). The contract follows the excerpts on
> rhythm and the want on incident, because the author's own pages are the evidence and the
> want is the intention. If that is wrong, the fix is different excerpts, not a softer
> contract.

## Open questions

Anything this design could not settle, carried forward in the author's words with the
default taken and what changes if it is overruled.
```

## Validation

Two checks, and the contract is not finished until both have run.

**1. The corpus-fit report is present.** Not summarised, not remembered — present in
`## Corpus fit`, with its digest in Provenance. A contract whose fit was never measured is
a WISH with no evidence, and must say so.

**2. The blind sort, against the corpus.** The question is not "is this good prose". It is:
*can a reader tell this voice apart from the register the corpus governs?*

Take five benchmark lines from the contract and five passages from the governing corpus.
Strip the sources, shuffle them, hand them over unlabelled, and ask the reader to mark each
one **this book** or **the corpus**.

- **Pass** — the reader sorts them, or hesitates on at most one pair.
- **Fail** — the contract's lines read as more of the corpus.

A fail means the ductus is the corpus wearing the author's adjectives, which is exactly the
state that produced a good world in a flat voice. Do not repair it by making the benchmarks
stranger. Repair the Register section until the voice does something the corpus cannot, and
re-run the sort.

Record the result in Provenance. **A blind sort run by the agent that wrote the contract is
weak evidence**, and saying who ran it is part of the record.

## Guardrails

- **It does not edit frozen gates.** No change to `deslop-check.sh`, `check-uniformity.py`,
  `check-arc.py`, or the caps they carry.
- **It does not move caps.** A cap moves only by re-derivation on a named corpus plus a
  freeze record in `CALIBRATION.md` — never because a contract would read better under a
  different number.
- **It reports the fight; it does not resolve it.** "The action lane needs 5–10 books in
  its own register" is a recommendation with its evidence attached. Adding corpus is a
  separate action, run separately, recorded separately.
- **One ductus per book, written under a series ductus.** The contract is the book's voice,
  not the series'. The series layer (`<ductus dir>/<voice>/series/<series>.md`, resolved
  from `series:` in `BOOKS.yaml`) holds what must survive every volume; each volume's
  contract is written under it, may tighten it and may not loosen it. Two books in one
  series share a series and must not share a contract.
- **Studies use one shared neutral test ductus.** A study that gives each arm its own voice
  is measuring the voice, not the pipeline.
- **It never writes the book's prose.** No sample paragraphs invented for the benchmarks,
  no "for instance" lines in Register. The benchmarks are quoted from the excerpts or they
  are not benchmarks.
- **WISH until falsified.** Every contract ships as a hypothesis with a named falsifier.
  The alternative — a contract asserted as fact — is a house style with better paperwork.

## Consumers

| Skill | Uses |
|---|---|
| `voice-matrix` | Register, Refusals, Breaking and Benchmarks as the target for Section 1; the contract wins on book-level register |
| `setting` | the whole contract, read before every chapter |
| `register` | Refusals, binding on dialogue as well as narration |
| `quoin` | anti-pattern budgets, so disruption respects the voice |
| `corrector` | budgets, Refusals, and what the blind sort is testing |
| `presswork` | Provenance, for what the book is and the excerpts it may not quote |
| `ductus.py audit` | the contract digest, so a chapter's carryover is attributable |

## Rules

1. The premise is upstream. Do not design a voice before the book knows what it is.
2. The want is authoritative on intention; the excerpts are authoritative on sound. When
   they disagree, record the conflict; do not split the difference.
3. Run the corpus-fit check before writing a word of Register. A contract written first is
   a contract the fit will be read to confirm.
4. The corpus-fit report goes in the contract, unedited. Findings are the product.
5. The five contract sections are `ductus.py`'s, spelled the same way. Additional sections
   are this skill's and come after them.
6. A Refusal that costs nothing is decoration. Each one names what the voice does instead.
7. Breaking is mandatory and numeric where the voice has a measurable failure mode.
8. Benchmarks are quoted, never invented, and carry a source.
9. The blind sort is pass/fail and it is the document's purpose.
10. Freeze before chapter one. Change after that is a dated decision.
11. The skill designs the voice; the writer writes the prose. A contract that contains its
    own sample paragraphs has drafted the book in the wrong room.

## Open questions, awaiting the author's call

These are carried rather than decided. Each has the default this skill runs on today and
what changes if it is ruled the other way. None of them blocks a run.

1. **How many excerpts — 2 to 5, or is one strong excerpt ever enough?**
   Default: 2 minimum, because one passage is a scene and a register is a pattern, and the
   corpus-fit check cannot see a single passage's idiosyncrasy as anything but a fight.
   If one is ruled sufficient, the skill needs a second instrument for the dimensions a
   single excerpt cannot establish (paragraph shape, opener repetition, rhythm variance).
2. **Name corpus additions by title, or only name the dimensions?**
   Default: name the dimensions and quote the measured gap; name titles only when the
   author asks for candidates, because a recommended list becomes a canon nobody
   re-measures, and the borrow list for a lane is the author's call.
3. **Does this contract format match the voice-contract format the engine already holds?**
   Default: yes, for the five sections `tools/ductus.py` reads, with this skill's
   additional sections after them. If the engine's format is ruled the authority, Register,
   Refusals and Breaking need mapping, and the fit/provenance sections need a home.
4. **Resolved 2026-11-12 — one per book, written under a series parent.** The default was
   right and unimplemented: the hierarchy had two levels, so "under a series parent" named
   nothing. It is now a file the engine resolves (`series:` in `BOOKS.yaml` →
   `<ductus dir>/<voice>/series/<series>.md`, book → series → voice), with the tightening-only
   rule at each step. The reason it stays one contract per book is unchanged: the pipeline's
   evidence is that a book's register is specific to its material.
5. **Per-lane caps, or the single global set in `deslop-check.sh`?**
   Default: the global set, unchanged, because moving a cap is a freeze event and a scanner
   change is larger than this skill. The cost is that a second lane cannot derive its own
   thresholds without moving the first lane's: the action register's caps and the light
   novel's are currently the same numbers, derived from one corpus. If per-lane caps are
   ruled, the scanner needs a lane dimension and each lane re-derives on its own corpus
   against its own freeze record — a separate action, run before any lane drafts.

Ask the author once, in a batch, at the end of the first run. A question asked mid-design
gets answered by the design.
