# Do the filing checks fire on the premises themselves?

The second false-positive channel, and one the human corpus cannot show: books from two premises that already share wording have a legitimate reason to share it, and the gate does not skip different-premise pairs. Measured on the premise texts exactly as `premises/premise.py` renders them (fields joined in fixed order, no labels), at the constants shipped in `run/dispatch.py`.

Pool: **40** premises, 64–91 words (mean 74), 780 pairs. Targeted by the study: **23** premises, 253 pairs (the frozen sets, not a hand-picked subset).

Machinery check: a copy of `lit-01` appended as an extra premise is flagged in 71 passages - the loop finds a seeded collision when there is one.

| corpus | pairs | opening collisions | shared 24-word passages |
|---|---|---|---|
| all 40 premises | 780 | 0 | 0 |
| the 23 targeted premises | 253 | 0 | 0 |

| run length | pool pairs flagged |
|---|---|
| 8 words | 0 of 780 |
| 12 words | 0 of 780 |
| 16 words | 0 of 780 |
| 20 words | 0 of 780 |
| 24 words **shipped** | 0 of 780 |
| 32 words | 0 of 780 |

## What this means for the run

No two premises share an opening or a 24-word run, so no pair of books is seeded with text the gate would refuse. The seeded channel is closed at the premise layer for this pool, and the human-corpus figure is the whole false-positive budget.

## Limits

- Absence of a shared run is not absence of shared *wording*: two premises can both say "a fishing town where everyone knows everyone" without a 24-word verbatim overlap, and a model drafting from them may still reach for the same phrasing. The measurement bounds the seed, not the echo.
- The gates skip same-premise pairs by design, because the two books from one premise are *supposed* to be related. This table is about different-premise pairs, which the gates do not skip and which the skip does not protect.
- Premises are 64–91 words, so the 24-word bar is a large share of a premise: the measurement is plausible at these sizes rather than merely conservative.
