# Fresh eyes — the blind packet

**Added 2026-11-23.** Two books in a row came back from this pipeline with a legal
instrument at the centre: a fulfilment contract with clauses, and a sentence that was a
debt. Both were well made. Both were about administration, and neither had a line anyone
would repeat.

The cause was measurable. Before Phase 2 this engine says *contract* thirty-two times,
*ledger* fifteen, *gate* sixty-one, and *world* four — and the four are all about checking
a world for contradictions, never inventing one. A model that reads all of that and is then
asked for a world builds a filing cabinet with weather in it. It is not choosing badly. It
is choosing from the only materials in the room.

This is the way out of the room.

## What a blind packet is

The book's premise, the genre, and the ask — and nothing else. No phases, no gates, no
names for anything. It is given to a context that has never seen this project: a different
model (Antigravity, Claude, ChatGPT, a local model), a fresh subagent, or a person.

The packet is not a prompt trick. It is the premise with the pipeline's vocabulary removed,
so whatever the reader invents comes from the story rather than from the tooling.

## What goes in, and what stays out

**In:** the author's own sentence about the book, in their words. The genre. Who reads it.
How long it is. Any constraint the author actually stated.

**Out:** every word of this system. Not because the words are secret, but because they are
contagious. `world.md`, `CANON_LEDGER.yaml`, `ductus.md`, the gates, the scores, the
previous books, the outline, the character sheets, the earlier drafts — none of it. A
reader who has seen the canon will produce a variation on the canon.

`premise.md` usually has to stay out too. By the time a premise exists it has been written
by the same pipeline, and it carries the diagnosis in its nouns. This book's premise says
*debt* twelve times and *writ* twelve times before it says what the dungeon is.

## How to run it

```bash
# the author's sentence, in their words, kept in maintenance/IDEA.md or passed directly
python tools/blind-packet.py test-books/<book>/book-1 --write

# paste-ready version for another model or a fresh context
python tools/blind-packet.py test-books/<book>/book-1 --prompt

# check any artifact for the pipeline's vocabulary
python tools/blind-packet.py test-books/<book>/book-1 --audit test-books/<book>/book-1/world.md
```

The tool refuses to ship a packet containing the system's vocabulary, and it prints the
words it found with line numbers. That refusal is the feature: a packet you had to clean is
a packet that was contaminated at the source, and the source is usually `premise.md`.

## The ask it puts

Three worlds, each under two hundred words, each carrying:

1. the physical fact that puts this family underground and keeps them there;
2. what their work produces that the surface cannot do without;
3. three scenes that could happen nowhere else;
4. one line a reader would repeat to a friend.

Then: which world is the most game-like, which is what this genre promises; the first
hundred and fifty words of chapter one in the author's voice; and a choice.

The fourth item is not decoration. A world that cannot produce three scenes and a line is a
world with no memorable moments in it, and that is the failure this whole mechanism exists
to catch. Memorability is not a quality that gets added at the prose stage. It is a
property of a world that puts people in situations worth quoting.

## What to do with the answer

- **File it, don't improve it.** The chosen engine goes into `world.md` as the author's
  decision. The pipeline's job is to make the rest of the book consistent with it, not to
  sand its edges into the house style.
- **Keep the discards.** The two worlds that lost, with the reason they lost, are the next
  pilot's guardrail.
- **Discard an administrative engine on sight.** If the returned centre is a contract, a
  debt, a court, a permit, or a title, the pass has failed even if it is beautifully
  argued: the pipeline got in through the premise. Rewrite the idea in physical terms and
  run it again.
- **A person counts.** The best blind pass is a reader who has never heard of this system
  being asked what the book is about. The tool only standardises the question.

## The gate

The packet is a way of finding a world. The gate is how a bad one is refused, and it belongs
to the 2 → 2.5 transition:

```bash
python tools/blind-packet.py test-books/<book>/book-1 --gate
```

It reads `world.md`, not the conversation that produced it, and it judges four things:

| rule | the file must show |
|---|---|
| **W1** | `## Engines considered` with at least three `###` candidates |
| **W2** | a non-empty `## Chosen engine` section |
| **W3** | the chosen engine carries no administrative vocabulary — no contract, debt, writ, charter, court, permit, or title |
| **W4** | `## Discarded` names at least one administrative engine that lost |

Exit 0 is the pass and its printed verdict goes into the phase record. Exit 1 blocks the
transition. Exit 2 means there is no `world.md`, which is not a verdict — a book before
Phase 2 is simply not judged by this row. `--allow "charter,debt"` records a deliberate use
of a flagged word, and the reason belongs in the file beside it.

W4 is the rule that looks like decoration and is not. A world that never names the filing
cabinet it refused will be handed to a pilot who reaches for it again, and the record is the
only thing that stops the second run.

## The honest limit

A blind reader does not know the canon, and will contradict it — a series with nine
established volumes will get a world that cannot hold them. That is not a defect to
suppress; it is the cost of fresh eyes, and the human decides what survives. The *pass* is
never recorded as a gate: no artifact filed, no phase advanced. What is gated is the world
the pass produced, and only that.
