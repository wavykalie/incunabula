# RUN_REPORT — *La merienda*

Autonomous run, 2026-10-05. No author at the wheel. Three checkpoints, each
judged by a **critic-role pass in this same agent** — **this harness has no
subagent dispatcher**, and the votes below are recorded as
`critic-role-pass` rather than as subagent approvals, because claiming a
separation that did not happen is the one dishonest thing a run can do.

## The roll

```
python tools/roll-brief.py --seed 594517907 --pool-size 1000 --dice 1
```

| field | value |
|---|---|
| seed | 594517907 |
| pool_size | 1000 |
| dice | **1** — see *Dice* below |
| language | Spanish |
| niche | tea ceremony second person |
| tone | warm |
| length | novella (25,000–45,000 words) |
| premise seeds | a weather station / a letter arrives misaddressed |

**Dice.** The run was made before `roll-brief.py` gained dice 2, and dice 2
removed the language draw entirely. `--dice 1` is therefore required to
re-derive this brief; the seed alone no longer does. Recorded in
`PROJECT_STATE.yaml → autonomous.roll.dice`.

**The niche came out of the 1000-niche pool** built earlier the same day by
`tools/niche-grow.py`, so the button drew on harvested Wikipedia material
rather than on forty hand-written lines. The five new niches this run owed the
pool are appended: *weather station epistolary, pass-road tea house novel,
missed-the-train collection, second person orchard novel, high-altitude slow
burn.*

## Premise

> A weather observer is sent to close a mountain weather station for the winter
> and finds, in its mailbox, a letter that has been waiting since 1983. The old
> woman who kept the station before her comes up the pass every Thursday
> because she was told someone would be there.

The second person, the tea ceremony and the Spanish came off the rolled shelf.
The premise was invented here from the two seeds.

## Checkpoints

**Checkpoint 1 — foundation. DENY, then APPROVE.**
Round 1 denied it. Chapter 2 as first written was an inventory with no
irreversible act (reader R2's deal-breaker: *a book where nothing happens*), and
the ninth envelope was heading toward a twist — a second mystery, conspiracy by
mailbox — which `01-market.md` rules out and which would have converted a book
about attention into a book about plot. Round 2 rebuilt the engine: the ninth
envelope is Elvira's own letter to her dead husband, returned to sender and
posted back once a year for fourteen years, by a woman who never once opened
the mailbox herself.

**Checkpoint 2 — manuscript. Two real failures, both reported.**

- **L1 will fail at delivery.** 16,340 words against a rolled floor of 25,000.
  See ruling R-002.
- **U1 chapter-length variance CV 22.1%** against a fail line of 22.0%. Passing
  by one tenth of a point, which is not a margin.
- `check-narrative` failed on the ledger itself and **the gate was right**: its
  parser accepts sections, `key: value` maps and lists of one-line flow maps, and
  the file was written in block style. Rewritten to the shape the tool reads.
- A1 reversals per bin 0.481 (warn under 0.50).

**Checkpoint 3 — delivery. APPROVE, with the package marked provisional.**
`check-length` fails and that FAIL stands. The package names its own gaps.

## Rulings

**R-001 — the drafting pass emits characters from other scripts, and no prose
gate can see them.** Twelve contaminated lines in chapter 1 alone: CJK,
Cyrillic, and English words sitting inside Spanish sentences that read correctly
for twenty words either side. `check-length` counts a Cyrillic word happily.
`tools/check-manuscript-integrity.py` was written to catch them and promoted into
the harness. Across the ten chapters it caught and repaired **23 contaminated
lines**, more than one per chapter.

**R-002 — delivered short; L1 left to fail.** The run recommended expanding by
~8,700 words, per the pension-winter precedent. The author chose to deliver at
16,340 and let the gate report a fact about the book rather than a number the
run had moved. The contract reads 25,000–45,000 and was not amended.

## Final gate state

| gate | result |
|---|---|
| `check-manuscript-integrity` | **OK** — all ten chapters clean |
| `check-narrative` | **OK** — 6 resolved, 4 deferred, 0 open |
| `check-arc` | **warn** — A1 0.481 |
| `check-drift` | **OK** |
| `check-names` | **OK** |
| `check-comps` | **OK** — 4 comps verified against public sources |
| `check-premise-distinct` | **OK** |
| `check-uniformity` | **warn** — U1 CV 22.1%, fail line 22.0% |
| `deslop-check` | **PASS with notes** |
| **`check-length`** | **FAIL — by decision.** 16,340 / 25,000 |

One misattribution was caught by verification and recorded rather than shipped:
*El invierno en Lisboa* was first credited to Andrés Trapiello. It is Antonio
Muñoz Molina. Trapiello is a different author with a similarly-placed career.

## Known gaps — read before treating this as finished

1. **The book is 35% short of its own length contract.** Not a defect in the
   prose; a fact about the deliverable. Query copy must quote 16,000 words.
2. **No subagent dispatcher exists in this harness.** The three checkpoint
   approvals are one agent reviewing itself, recorded as such.
3. **No EPUB or DOCX render.** No pandoc here and no per-book renderer, as with
   Pension Winter.
4. **No sales data.** No BookScan, no panel, no retailer contact. The comp set
   is an argument from four books.
5. **Two debts are deliberately unresolved.** D-007 (Tomás could not read,
   Fermín could — said once, unconfirmed) and D-008 (two of the nine envelopes
   stamped Zaragoza, opened and never entered). Both recorded with reasons. D-008
   is the one a reviewer may fairly call a cheat.
6. **The Spanish drafting pass is unreliable.** Twenty-three contaminated lines
   in ten chapters is a rate, not an accident. The repair loop works, but a
   human pass over the prose is not optional before submission.
7. **U1 passes by 0.1% of CV.** Any edit to a single chapter can tip it.