---
name: incunabula-auto
description: One command, one book. Give it an idea and it dispatches the orchestrator to run the whole pipeline autonomously, stopping only at three human checkpoints. Or hit the random button: no idea, no author — a rolled niche and subagent-approved checkpoints.
---

# incunabula-auto — one command, one book

An idea goes in. A book comes out.

## The random button — autonomous mode

`incunabula-auto random` runs the pipeline with **no author and no idea**. The
brief is rolled, not given:

1. `python tools/roll-brief.py` — rolls language, niche, tone, and length from
   `tools/niche-pool.txt`, plus two premise seeds. The dice choose the shelf,
   not the story: the run invents the premise from the seeds. `--seed N
   --pool-size K` reproduces any earlier roll exactly (the pool grows, so the
   brief records K and draws from the pool as it was; the pool is
   append-only). Record the seed and pool size in the book's PROJECT_STATE.yaml
   so the run can be re-derived.
2. **The pool grows.** After rolling, the run appends **five new niches** to
   `tools/niche-pool.txt` — invented, because a script can draw a niche but
   never invent one. A pool that never grows is a button that gives the same
   answers forever.
3. Scaffold and register: `python tools/init-book.py --path <slug> --title
   "<working title>" --status autonomous --floor <rolled> --ceiling <rolled>`.
   `status: autonomous` in BOOKS.yaml means a run in flight: the registry
   checks skip the manuscript-shape rows for it, and the book is judged at its
   own gates instead.
4. Run the pipeline as below, with one change: **the three checkpoints are
   decided by subagent vote, not by the author.** At each checkpoint, dispatch
   a critic subagent (a fresh one each round — never the agent that produced
   the material) with the checkpoint's deliverables and the rubric for that
   gate. It returns **APPROVE** or **DENY** with reasons. On DENY: revise to
   answer every reason, then dispatch a fresh critic. **Loop until APPROVE.**
   Record every verdict — date, verdict, reasons — in PROJECT_STATE.yaml. A
   denied round that vanishes from the record is a round nobody learns from.
5. Deliver as usual. The book sits in the registry as `status: autonomous`;
   the author can promote it (edit the status by hand) or archive it.

Safety valve: if the same checkpoint is denied three times with materially the
same reasons, stop and leave the book at that phase with the record intact.
Three identical denials mean the rubric and the run disagree, and no critic
vote resolves that — a human does.

The skill dispatches the orchestrator agent, which runs the full pipeline with no
interruption except three approval points:

1. Market research
2. Readership
3. Foundation — characters, outline, theme
4. Voice matrix
5. **Checkpoint one: the foundation is approved**
6. Entity state built from the foundation
7. Outline collation
8. Every chapter: drafting, register, catchword, quoin, entity updates per batch, mechanical cleanup, evaluation, and the proof pull — all automatic
9. Full-manuscript evaluation
10. Revisions
11. Entity state updated to match the revisions
12. Full-manuscript continuity audit
13. **Checkpoint two: the manuscript is approved**
14. Editorial package — logline, synopsis, query, cover brief
15. Proofread and formatting
16. **Checkpoint three: the book is delivered**

## Usage

```
incunabula-auto [language] [idea]   |   incunabula-auto random
```

For example, a language-tagged idea in any supported language, a literary novel about a
physicist losing her memory, a memoir about burnout, or a thriller about a former officer
avenging a murdered family. Language and idea travel together.

## Execution

Before dispatching, run `bash tools/preflight.sh` at the pipeline root and confirm every
row is PASS or a named SKIP. A FAIL is fixed or reported before the run starts — a book
drafted against a stale instrument is not a book.

On invocation, dispatch the orchestrator immediately with the user's full input and the
instruction to run the entire pipeline autonomously, pausing only at the three checkpoints.

Do not add commentary and do not ask clarifying questions first. Dispatch.

The orchestrator runs for as long as it takes and returns to the user at each checkpoint.
In `random` mode it returns to nobody: the checkpoint subagent vote stands in for the
author, and the run reports once, at delivery.

## Where projects live

Each book is created in its own project folder, named with a slug generated from the title —
lowercase, hyphenated, no accents. If the user has a preferred root directory, use it; the
folder is created there.
