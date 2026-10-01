---
name: press-ledger
description: The project's state engine. Records chapters, scores, decisions, and open handoffs between sessions so a long book keeps its memory. Run at the start and end of every working session.
---

# Press-ledger — the state engine

A book is a long project: dozens of sessions, thousands of small decisions, several skills
each holding part of the picture. The only reason that stays coherent is persistent state.
Press-ledger is that state. It writes nothing creative; it records.

Without it, every session starts from nothing. With it, fifty sessions build one book.

---

## PROJECT_STATE.yaml

The source of truth, at the project root:

```yaml
project:
  title: ""
  author: ""
  genre: ""
  word_count_target: 0
  word_count_current: 0
  started: ""
  last_session: ""

phase: ""            # research | foundation | writing | evaluation | revision | delivery

chapters:
  - number: 1
    title: ""
    status: ""       # planned | drafted | revised | polished | final
    word_count: 0
    score: {}        # per-dimension scores if evaluated alone
    notes: ""

incunabula_score:
  version: ""
  last_evaluated: ""
  dimensions:
    originality:   { score: 0, evidence: "", citations: [], history: [] }
    theme:         { score: 0, evidence: "", citations: [], history: [] }
    characters:    { score: 0, evidence: "", citations: [], history: [] }
    prose_voice:   { score: 0, evidence: "", citations: [], history: [] }
    pacing:        { score: 0, evidence: "", citations: [], history: [] }
    emotion:       { score: 0, evidence: "", citations: [], history: [] }
    configurable:  { name: "", score: 0, evidence: "", citations: [], history: [] }
  # citations are { chapter: "Ch 5", excerpt: "...", partial: 0, reason: "" } —
  # a score with no excerpt attached is not a score.
  floor: 0

stylistic_device:
  type: ""           # surreal | marketplace | worldbuilding | epistolary | humour | other | none
  description: ""

decisions:
  - date: ""
    decision: ""
    rationale: ""
    reversible: true

open_handoffs:
  - skill: ""
    task: ""
    priority: ""     # high | medium | low
    created: ""

sessions:
  - number: 1
    date: ""
    duration: ""
    done: []
    decided: []
    problems: []
    next_step: ""
```

---

## Check-in (session start)

Run whenever work begins.

0. Run `bash tools/preflight.sh <project root>` and read `COMMONPLACE.md` at the pipeline
   root. The preflight says whether the instruments are the ones the results will be
   attributed to; the commonplace book says what has already been chosen and declined.
   A session that starts without both is working from memory, which is the failure this
   layer exists to end.
1. Read the state file.
2. Report: current phase, what the last session finished, open handoffs, the planned next step, and the current score if one exists.
3. Verify the file against reality: does the word count match the actual files, do chapter statuses match what exists, and did last session's decisions change today's work?
4. Ask whether to continue from the last stopping point or do something else today.

## Check-out (session end)

Run whenever work stops.

1. Update the state file: chapter statuses, word count, score if re-evaluated, decisions taken with their rationale, handoffs opened or closed, and the session record.
2. **Append this session's observations to `ERRATA.md`.** See below — this is the step that
   makes the pipeline improve across books instead of only within one.
3. **Append this session's `decision` and `outcome` entries to `COMMONPLACE.md`** at the
   pipeline root — every real fork where another road was visible, with the reason. This
   is the taste channel; `ERRATA.md` is the measurement channel, and evidence does not
   cross between them (`SELF_IMPROVEMENT.md` §2). Distill an `emergent` preference only
   at three agreeing decisions.
4. Tell the user what got done, what is still open, and what the logical next step is.
5. Warn about any handoff that has been open more than two sessions.

---

## Errata — the step that compounds

The pipeline is meant to get better as more books go through it, and the mechanism is two
files at the pipeline root: `PRINTERS_COPY.md` holds what the system believes, `ERRATA.md` is
the append-only ledger of what it has seen. `tools/prose/check-errata.py` validates both.

**Append an entry whenever a book produces evidence about the guidance itself.** Not only for
a book that broke — also for one that surprised you. The cases that matter:

- a gate fired on a book you believe is fine (**this is the most valuable entry you can write**,
  and the one most often skipped: a false accusation cost a rewrite and nothing else records it)
- a gate did not fire on something that was clearly wrong
- a rule was waived, and a **second** book waived it too
- a panel or reader verdict contradicts something a gate is enforcing
- a book needed a workaround that no skill describes

**Three states, and the middle one is the trap.** Write `observed` and stop. `proposed`
requires an `n` naming independent books. In `hand` mode only a person may write
`adopted` — which means applying the change to `PRINTERS_COPY.md` as a diff. In
`improvement.mode: auto` (`SELF_IMPROVEMENT.md`), the verifier stack writes `adopted`:
the person is replaced by falsification, never by silence, and a promotion with any
SKIPPED verifier is held rather than adopted. **A book never moves a threshold.** One
book is an observation; three agreeing books are a proposal; in `hand` mode the decision
is still a human's, and in `auto` it is the stack's — which is the human's rules read
strictly. That rule is the whole point of the layer: a threshold re-derived from a handful
of books somebody liked has baked a period confound into a permanent constant.

**The motive field is yours and cannot be generated.** If a change would only make a score go
down and would not make the book better, it is `privacy`, not `aesthetic`, and it has to say
what it is a substitute for. There are currently no `privacy` rules in the confirmed
registry, and the validator enforces that. This is the distinction the whole layer exists to
protect: advice that reduces a synthetic feel is not the same as writing a novel, and a system
that cannot tell them apart optimises against the wrong target.

Read `errata.mode` from `PROJECT_STATE.yaml` to see what the current promotion mode permits,
and run `python tools/prose/check-errata.py` after writing. The entry format is documented at
the top of `ERRATA.md`; a malformed entry fails the validator rather than sitting there
looking like evidence.

---

## Decisions

Record anything that affects structure, character, theme, or direction.

```yaml
- date: "2026-03-02"
  decision: "Moved part two from parallel structure to linear"
  rationale: "Chapters arguing the same thesis independently stalled. A causal chain restores momentum."
  reversible: true
```

The log exists so decisions are not remade, so the reasoning survives the person who made
it, so a reversal is possible, and so a fresh agent inherits the context.

## Handoffs

When one skill needs another's output, record it:

```yaml
open_handoffs:
  - skill: "setting"
    task: "Rework chapter three dialogue — subtext is weak"
    priority: "high"
    created: "2026-03-02"
```

Remove it when done. Anything open past two sessions gets surfaced at check-in.

## Recovery

When context is lost — a crash, a limit, a new conversation:

1. Read the state file; it holds everything.
2. Read the last three session records for recent context.
3. Check open handoffs for what was in flight.
4. Check recent decisions for what was settled.
5. Summarise it back to the user and confirm before continuing.

As long as the file exists and is current, nothing is permanently lost.

---

## Errata, not waivers

A waived rule is a *local* decision and lives in `RUN_REPORT.md`. A repeated waiver is an
*observation about the system* and belongs in `ERRATA.md`. The record in
`tools/check-uniformity.py` already says why this distinction matters: “reproducing the same
exemption across books is itself the pattern this check exists to catch.” A second waiver is
not a coincidence to be re-noted in the next book; it is the first data point in a pattern
that nobody will otherwise assemble.

The same applies in reverse. If you catch yourself writing the same justification into
`RUN_REPORT.md` for the third time, the justification is not book-specific, and the honest
thing is to escalate it to the errata ledger where it can be counted.

---

## File conventions

```
manuscript/
├── PROJECT_STATE.yaml        # source of truth (this skill)
├── foundation/               # characters, emotional curve, theme, voice guide, outline
├── chapters/                 # ch-01.md, ch-02.md ...
├── research/                 # comp titles, per-chapter data, market notes
├── evaluations/              # versioned scores and proof-panel reads
├── editorial/                # logline, blurbs, query letter, cover brief
└── export/                   # assembled manuscript
```

Filename rules: kebab-case, no accents or spaces; chapters always zero-padded; evaluations
always versioned. Paths in the state file are relative to this structure. If a project does
not follow it, check-in creates the missing folders.

## Commands

`/state` current phase, scores, and open items · `/checkin` run check-in · `/checkout` run
check-out · `/decisions` list the decision log · `/handoffs` list open handoffs ·
`/history [chapter]` show one chapter's change history.
