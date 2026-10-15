# PROGRAM MAP — how Incunabula works

*Written in plain English on purpose. Every term here is defined again in
[`INCUNABULA_LEXICON.md`](INCUNABULA_LEXICON.md); this file is the map, that one is the
dictionary. If the two ever disagree, the lexicon wins on meaning and this file wins on
layout.*

---

## 1. What this program is, in one paragraph

Incunabula turns **one line — an idea for a book — into a finished manuscript and an
editorial package**. It is not the writer. It is the production line around the writing: it
plans the book, dispatches specialist steps (each a separate "skill"), measures every
chapter with automatic checks, refuses to advance when a check fails, and keeps a written
record of every fact, decision, and score so the project can be resumed weeks later by
anyone — human or machine.

---

## 2. The funnel: one prompt → one book

```
  "a literary novel about a physicist losing her memory"          ← the single prompt
                        │
                        ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 0. ENTRANCE                                             │
  │    incunabula-auto "<idea>"     (one command, one book)  │
  │    or: incunabula → start <idea>   (interactive)         │
  │    or: incunabula-auto random      (no idea: roll one)   │
  │    Gate: preflight.sh must be all PASS before anything.  │
  └─────────────────────────────────────────────────────────┘
                        │
                        ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 1. THE PAPERWORK (created before any writing)           │
  │    state file · canon ledger · voice contracts ·         │
  │    assumptions · pruning log · project registry entry    │
  │    A file that is missing here is a failure, not a TODO. │
  └─────────────────────────────────────────────────────────┘
                        │
                        ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 2. PLANNING  (phases 1 → 2.8)                           │
  │    1    Research      — the market, comps, niche         │
  │    1.5  Readership    — who reads it (incl. a hostile)   │
  │    2    Foundation    — characters, outline, theme       │
  │    2.5  Voice matrix  — how each voice sounds/breaks     │
  │    2.7  Case tracking — the book's fact inventory        │
  │    2.8  Collation     — is the plan self-consistent?     │
  │                                                         │
  │    ★ CHECKPOINT 1 — a human (or critic vote) approves    │
  └─────────────────────────────────────────────────────────┘
                        │
                        ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 3. THE CHAPTER LOOP  (phases 3 → 5.6, once per chapter) │
  │                                                         │
  │    write chapter ──► polish its dialogue                 │
  │         │          ──► score its opening & ending        │
  │         │          ──► break its predictable patterns    │
  │         │          ──► mechanical cleanup (dashes, etc.) │
  │         │          ──► evaluate it (a fresh evaluator)   │
  │         │          ──► fix its worst weakness (≤3 tries) │
  │         │          ──► revise it                         │
  │         │                                               │
  │         └─── every step leaves a file as proof ───┐      │
  │                                                   │      │
  │    THE GATE RUNNER (tools/run-gates.sh) ◄─────────┘      │
  │    17 automatic checks on the book so far.               │
  │    Verdict: CLEAR (0) · FAIL (1) · NOT CLEAR (2).        │
  │    FAIL or NOT CLEAR blocks the next phase. Period.      │
  │                                                         │
  │    ★ CHECKPOINT 2 — the manuscript is approved            │
  └─────────────────────────────────────────────────────────┘
                        │
                        ▼
  ┌─────────────────────────────────────────────────────────┐
  │ 4. DELIVERY  (phase 6)                                  │
  │    whole-book continuity audit · final score ·           │
  │    editorial package (logline, synopsis, query, cover) · │
  │    proofread and formatting                              │
  │                                                         │
  │    ★ CHECKPOINT 3 — the book is delivered                │
  └─────────────────────────────────────────────────────────┘
                        │
                        ▼
  out/  manuscript/ · delivery/ · evaluations/ · full record  ← the book
```

**The loop-backs (this is where books actually get made):**
- A revision that does not raise the floor after three rounds → back to planning (phase 2).
- A character who grows away from the plan → pause, fix the plan, resume.
- The gate runner failing anywhere → fix and re-run before any phase claim.
- The passing reader who would not keep reading → overrides every score, fixed first.

---

## 3. The three ways in

| You have | You run | What happens |
|---|---|---|
| An idea and no patience | `incunabula-auto "<idea>"` | The whole pipeline, autonomous, stopping only at the 3 checkpoints above |
| Nothing at all | `incunabula-auto random` | The niche and brief are rolled by dice (`tools/roll-brief.py`); critic subagents vote at the checkpoints |
| A desire to steer | `incunabula`, then `start`, `write`, `evaluate`, `revise`, `score`, `deliver` | You drive; every command still runs the same gates |

A fourth entrance exists for **small projects**: the 8-phase compact pipeline in
`incunabula-codex` (intake → foundation → architecture → drafting → devil's audit → fine
press loop → final score → colophon). It is opt-in only and never substitutes itself for
the full engine silently.

---

## 4. The feature inventory

### The specialist skills (who does the work)

| Phase | Skill | Job |
|---|---|---|
| 1 | `scout` | market research, comps, positioning |
| 1.5 | `readership` | 3–5 reader personas, including a hostile one |
| 2 | `forme` | foundation: characters with inner contradictions, outline, theme as a question |
| 2.5 | `voice-matrix` | per-character voice specs, including how each voice breaks under pressure |
| 2.7 / 3.7 / 5.5 | `case-keeper` | the book's fact inventory (build / update / update) |
| 2.8 / 5.6 | `collator` | continuity audit of the plan, then of the whole manuscript |
| 3 | `setting` | drafts one chapter at a time |
| 3.1 | `register` | dialogue only: is each voice distinguishable? |
| 3.2 | `catchword` | opening hook and closing pull of each chapter |
| 3.5 | `quoin` | deliberately breaks the draft's predictable patterns |
| 3.8 | `composing` | mechanical cleanup (em dashes, adverbs, filter words) |
| 4 | `proof-panel` | independent evaluation — never the agent that wrote the chapter |
| 4.5 | `proof-pull` | fix-the-top-weakness loop, at most three rounds |
| 5 | `corrector` | surgical revision (structure → connective → prose → factual) |
| 6 | `colophon` + `presswork` | editorial package, proofread, formatting |

Supporting skills: `series-binder` (multi-book scope), `press-ledger` (session ledger),
`bestseller-studio`, `reader-swarm` (panels and market simulation — `--light` runs the
four-voice market panel), and the
generic craft utilities `copy-editing`, `deslopify`. (`bundles/good-idea/` is a
separate bundle, not part of this suite.)

### The gates (what can fail the book)

| Gate | Runs on | Question it answers |
|---|---|---|
| **Prose gate** | every prose phase | `deslop-check.sh` (per-chapter machine tells) · `check-uniformity.py` (are the chapters suspiciously alike?) · `check-drift.py` (does the voice shift mid-book?) · `check-arc.py` (does the emotional direction ever reverse?) |
| **Narrative gate** | evaluation + delivery | `check-narrative.py` against `NARRATIVE_LEDGER.yaml`: every set-up paid off or explicitly deferred; no beat/scene monotony |
| **Maintenance gate** | every phase | state, canon, and pruning log exist and reconcile; nothing resolved silently |
| **The gate runner** | checkpoints + on demand | `tools/run-gates.sh` — all of the above in one command, 17 rows, one verdict |

Report-only companions (`check-surplus`, `check-recoverable`, `check-figurative`,
`check-dialogue-tags`, `check-quantities`) inform but can never fail anything: no measured
corpus stands behind them yet.

**Two rules the gates enforce on themselves:**
1. **Not-run is never a pass.** An empty scan fails; a skipped gate blocks like a failure.
2. **The freeze.** The checking tools are fingerprinted (`GATE_FREEZE.md`,
   `tools/prose/verify-freeze.sh`). Every score in this repository can be traced to the
   exact tool version that produced it. Edit a checker without recording it and
   `verify-freeze` says `CHANGED` — stop immediately.

### Scoring

- **Incunabula Score** = the *floor* of seven dimensions (originality, theme, characters,
  prose/voice, pacing/coherence, emotion, one configurable). Six 9s and one 7 is a 7.
- **First Impression** — predicts first-year sales (gate: ≥ 7.0 before delivery).
- **Standing Type** — predicts twenty-year sales.
- The two indices are allowed to disagree; a 2-point divergence is reported, not fixed.
- Anti-inflation rules apply throughout: every score cites a passage; self-scores are
  assumed inflated by 0.5–1.0.

### The author's voice (who is writing, as distinct from what the book says)

| Piece | What it is |
|---|---|
| `ductus.yaml` | the imprint and where the voices live — no roster; a voice exists because a creator made one |
| `ductus/<name>/ductus.md` | the voice contract an agent pilots: identity, register, refusals, how it breaks under pressure, benchmark lines |
| `ductus/<name>/COMMONPLACE.md` | that voice's own taste ledger, with the root ledger's ceremony |
| `ductus/PROMOTIONS.md` | the only channel between voices — a dated, deliberate merge; nothing else crosses |
| `tools/ductus.py` | `new` · `check` · `contract` · `cross` · `list` — and `contract` is what a phase calls |

Isolation here is the same rule the channels obey (`SELF_IMPROVEMENT.md` §2): a preference
earned by one voice is not evidence for another, `cross` reports an entry two ledgers both
hold, and no voice may move a threshold.

### The record layer (what survives between sessions)

```
{project}/
  PROJECT_STATE.yaml        where the run is, what is done, what is next
  ASSUMPTIONS.md            every inference labelled as an inference
  RUN_REPORT.md             the exact unfinished task and resume step
  CANON_LEDGER.yaml         the book's facts, each with its source
  NARRATIVE_LEDGER.yaml     what the book owes: set-ups, beats, scene functions
  foundation.md  outline.md  voice-matrix.md  readership.md
  manuscript/chapters/      one file per chapter
  evaluations/  continuity/  research/  delivery/
  maintenance/              SESSION_LOG.md, PRUNING_LOG.md (append-only)
```

Nothing is decided in chat and forgotten: files prove phases, and anyone with a terminal
can re-check them.

### Self-improvement (the make-ready)

- `ERRATA.md` — append-only ledger of mistakes found in the measurements themselves.
- `PRINTERS_COPY.md` — what was tried and **rejected**, with reasons (the anti-regression
  registry).
- `SELF_IMPROVEMENT.md` — what may change without a person, and what may not.
- `COMMONPLACE.md` — the taste ledger: preferences distilled from three agreeing choices.
- `tools/preflight.sh` — runs the static half of this stack before every session.

Firewall: evidence from measurement, craft, and taste never moves the other's thresholds.
A single book never moves a threshold; three independent books make a proposal, and a
person still decides.

---

## 5. One chapter, up close (the loop everyone asks about)

0. **Resolve the voice** — `python tools/ductus.py contract <book-root>`. A book may be
   drafted *under a ductus*: one authorial voice, whose contract the writer reads before
   any line and whose refusals are binding (`ductus/<name>/ductus.md`). `UNASSIGNED` means
   no voice is declared and the root `COMMONPLACE.md` is the only taste ledger in play;
   `REFUSED` means the assignment names a voice nobody authored, and the phase stops there
   rather than drafting against a skeleton.
1. **Write** (`setting`) — given the outline entry, the voice bank, the previous chapter,
   and a structural approach that must differ from the previous chapter's.
2. **Dialogue pass** (`register`) — blind-sort every speaking character; fix voice bleeding.
3. **Openings/endings** (`catchword`) — score hook and pull; rewrite below threshold;
   never repeat the previous chapter's hook type.
4. **Disruption** (`quoin`) — at least five operations that break predictability while
   preserving the emotional anchor.
5. **Mechanical pass** (`composing`) — em dashes, overprints, adverbs, filter words; every
   diff reviewed by a human eye before it lands.
6. **Evaluate** (`proof-panel`) — a fresh evaluator, in a context that never wrote this:
   scores, weakness taxonomy, tic scan, reader simulation.
7. **Proof-pull** (`proof-pull`) — fix the single top weakness, re-evaluate, ≤ 3 rounds.
8. **Revise** (`corrector`) — top-down: structure first, sentence polish last.
9. **Gate** (`run-gates.sh`) — the whole book re-measured. CLEAR or nothing is claimed.
10. Every step above leaves its artifact (blind-sort table, hook scores, quoin log, diff
    review, verdicts, round log). `check-pass-evidence.py` verifies they exist; a claim
    without an artifact is a failure, not a pass.

---

## 6. Where everything lives in the repository

| Path | What it is |
|---|---|
| `skills/` | the 29 skills — instructions for the specialist steps |
| `skills/incunabula/` | the orchestrator: phases, gates, dispatch, scoring |
| `skills/incunabula-codex/` | the contract layer: intake schema, canon schema, phase prompts, compact pipeline |
| `tools/prose/` | the checkers (frozen instrument — fingerprinted in `GATE_FREEZE.md`) |
| `tools/` | the harness: `run-gates.sh`, `preflight.sh`, `init-book.py`, `roll-brief.py`, `prune-stale.py`, `ductus.py`, … |
| `ductus.yaml`, `ductus/` | the author voices: one contract an agent pilots plus one developing taste ledger per voice, created by `tools/ductus.py new` |
| `tools/prose/calibration/` | how the thresholds were measured; corpus supplied locally, never committed |
| `demo-books/`, `test-books/` | your books — gitignored, never published by a push. The framework ships no manuscripts; `tools/init-book.py` makes the first one |
| `GATE_FREEZE.md`, `ERRATA.md`, `PRINTERS_COPY.md`, `KNOWN_FINDINGS.md` | the evidence and history record |
| `INCUNABULA_LEXICON.md` | the dictionary of every term |

---

## 7. What the system will not do

- Report a check as passed when it was never run.
- Resolve a contradiction by quietly picking a side.
- Let the agent that wrote a chapter also score it.
- Claim a phase finished on the strength of a chat message.

That last one is the whole design: **judgments are labelled as judgments; evidence is
evidence.**
