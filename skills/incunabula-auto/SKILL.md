---
name: incunabula-auto
description: One command, one book. Give it an idea and it dispatches the orchestrator to run the whole pipeline autonomously, stopping only at three human checkpoints.
---

# incunabula-auto — one command, one book

An idea goes in. A book comes out.

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
incunabula-auto [language] [idea]
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

## Where projects live

Each book is created in its own project folder, named with a slug generated from the title —
lowercase, hyphenated, no accents. If the user has a preferred root directory, use it; the
folder is created there.
