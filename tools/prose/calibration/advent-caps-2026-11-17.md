# The Advent lane's cap re-derivation — measured, not applied

*2026-11-17. Lane `advent-horror`: 10 works, 106 documents, 774,011 words (LANES.tsv). The
brief of 2026-11-17 asks for the caps to be re-derived at 1.5× the worst document across the
full corpus and the result recorded. This is that record. **No cap was changed.***

## What the lane measures

`python tools/prose/corpus-report.py` prints, per lane, each cap row's worst single document,
the cap in force, and what 1.5× that worst document would imply:

| row | worst doc | cap in force | headroom | 1.5× would be | direction |
|---|---|---|---|---|---|
| D1 em dash /1k | 9.3 | 10.0 | +0.7 | 14.0 | RAISE |
| D2 rule of three /1k | 5.6 | 5.0 | −0.6 | 8.4 | RAISE |
| D3 -ly adverbs /1k | 25.6 | 26.0 | +0.4 | 38.4 | RAISE |
| A23 parenthetical dash /1k | 1.9 | 3.0 | +1.1 | 2.9 | LOWER |
| A24 explanatory coda /1k | 0.4 | 1.0 | +0.6 | 0.6 | LOWER |
| A25 antithesis formula /1k | 0.6 | 1.5 | +0.9 | 0.9 | LOWER |
| P1 repeated opener, top /1k | 6.1 | 6.0 | −0.1 | 9.2 | RAISE |
| P3 longest short-sentence run | 12 | 7 | −5.0 | 13 (worst+1) | RAISE |

Three findings, in order of how much they matter:

1. **The corpus breaches P3.** The worst single document in the lane runs 12 short sentences in
   a row against a gate cap of 7. The ghost-story control found 9; the fuller lane finds 12. A
   cap that the register's own published prose fails by 71% is not measuring slop, it is
   measuring a rhythm the register uses. This is the row to re-derive first, and it is a
   scanner change (P3's family), therefore a freeze event.
2. **D2 and P1 sit marginally over.** 5.6 against 5.0, and 6.1 against 6.0. Two published
   documents out of 106 exceed each cap. That is the expected cost of caps set on a 48-document
   light-novel corpus and then applied to a 106-document horror one.
3. **The rest pass with headroom** — D1, D3, A23, A24, A25 — and three of those would *tighten*
   at 1.5×, which is the opposite of what a lane-wide re-derivation is usually asked for.

## Why nothing moved

`LANES.tsv`'s header and `CORPUS_MAP.md` §6 state the rule this record obeys: the scanner's caps
are **global**, one set serves every lane, so re-deriving them on a second lane moves the first
lane's thresholds too. Per-lane caps need a scanner change and are a freeze event. And the
standing rule is that a single book, or a single lane, never moves a threshold: three
independent books make a proposal, and a person still decides.

So this is evidence, filed where the decision will be made. The Advent book is drafted against
the caps in force, and the three rows above are recorded as the reason it may trip them.

## What it means for the Advent drafts

- A story that fails **P3** at 8–12 in a row is doing something this register does. The waiver
  is recorded with that citation, not treated as a defect in the story.
- **D2** and **P1** failures at these margins are likewise lane-level, not book-level.
- **D1, D3, A23, A24, A25** are live: the lane passes them comfortably, so a draft that fails
  one is failing against its own register, and gets fixed.
