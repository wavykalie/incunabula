# Phase 1 — Foundation

## Goal

Take what intake produced and turn it into a foundation solid enough to carry a whole
manuscript. If the foundation is soft, everything drafted on top of it will be soft in the
same places.

## Outputs

- `world.md` at the book root — it comes first, and the foundation is built on it
- `artifacts/03-characters.md`
- `artifacts/04-theme.md`
- `artifacts/06-emotional-curve.md`
- `PROJECT_STATE.yaml`

## Rules

- State the theme as a question. The moment it becomes a slogan, the book starts arguing
  with itself instead of asking.
- Every main character gets a wound, a want they can name, a need they cannot, and the lie
  they believe that keeps the two apart.
- Contradiction is not decoration. Put two incompatible things in the same person and make
  the plot test which one wins.
- Build relationships as pressure between people, not as fondness between them.
- The emotional curve needs real valleys. A curve that only rises has no shape and the
  reader stops feeling it by the midpoint.

## The world comes first

`world.md` is not one of the artifacts and it is not optional. It holds the physical fact
that makes the story possible — the thing that puts these people where they are and the
thing their labour produces that the world cannot do without. Write it in this shape,
because the Phase 2 gate reads the headings:

```markdown
# THE WORLD — <title>

## Engines considered

### 1. <name>
### 2. <name>
### 3. <name>

## Chosen engine

## Discarded
```

- **The first candidate is the genre's own engine.** For a LitRPG that is a progression
  system: levels, stats, classes, and what each one costs. For a mystery it is an
  information asymmetry; for a romance, a social obstacle.
- **The administrative candidate is written down and marked as the one that lost** — a
  contract, a debt, a charter, a court, a permit. Naming it is what stops the next run from
  reaching for it, because that file is where the pipeline's own vocabulary goes when a
  pilot has no worldbuilding step.
- **`python tools/blind-packet.py <book-root> --gate` must return PASS before this phase is
  dispatched.** W1 three candidates, W2 a chosen engine, W3 that engine is not
  administrative, W4 the attractor named among the discards. A world that fails W3 is a
  filing cabinet with weather in it, and everything built on top of it inherits the shape.

If the premise was written by this pipeline, do not build `world.md` from `premise.md`. Run
the packet (`--write`), get three worlds from a context that has not read the pipeline, and
file the winner in this shape. See `skills/incunabula/references/fresh-eyes.md`.

## What goes in each file

`artifacts/03-characters.md` — main characters, core wound, conscious desire, unconscious
need, the lie, contradictions, and notes on how each one sounds.

`artifacts/04-theme.md` — the central theme, the theme restated as a question, subthemes,
and the recurring symbols that carry it.

`artifacts/06-emotional-curve.md` — the progression block by block, the emotion it opens on,
the emotion it closes on, the points where a reader is most likely to put the book down, and
the beats that will hit hardest.

## Before you finish

Maintenance gate: check out to state, canon, and the pruning log. Re-run the foundation gate.
Record the world gate's verdict (`python tools/blind-packet.py <book-root> --gate`) beside
it: a foundation cannot be re-run as repaired while the world under it is still contested.
