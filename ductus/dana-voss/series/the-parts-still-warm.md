# The Parts Still Warm - series ductus

*A ductus* - the individual character of this series' writing hand, and the layer between
the persona and the volumes.

**Status: WISH, unfalsified as of 2026-11-12.**

**Parent:** dana-voss (authored 2026-11-12 for the thriller line)

**Volumes:** ten planned (author, 2026-11-12). None drafted under this layer.

**Why this file exists.** A persona is a hand; a book contract is that hand on this
material; neither of them holds a series. The previous version of this file sat under the
literary-horror persona and inherited its stillness, so volume one was drafted as a horror
book and then argued with. Nine unwritten volumes have no evidence of their own, so the
series carries the ponytail - the pace band - and each volume may tighten it, never loosen
it.

## Identity

One man, ten volumes, one continuity. The series is not ten books about a vigilante; it is
one book about a bill, told in parts. What holds across all ten is the arithmetic: every
volume adds to what he owes and subtracts from what he can still be.

Each volume must be satisfiable on its own - a reader who buys volume four reads a whole
story - and must leave the series' question open.

## Register

- **The instrument does not change.** Close third, past tense, one body, the count.
- **The series does not decelerate and does not flatten.** Volume one's contract runs
  mean sentence <= 13, short sentences >= 40%, paragraph <= 32, chapter means 9-14, with
  the fastest and slowest chapters at least six words apart and no two consecutive
  chapters within one word. The numbers live in `test-books/the-parts-still-warm/ductus.md`
  and this file cites them by reference: one copy of a number.
- **Each volume names its own incident.** No volume may be the one where the arithmetic
  pauses and the book becomes the aftermath of the previous volume.
- **Measurement is pounds and paces**, in every volume, in narration and in quoted
  documents.

## Refusals

- **No volume resolves the series.** A volume may close a debt; it may not close the
  question the series opened.
- **No genre drift between volumes.** A vigilante thriller with a body count does not
  become a procedural in volume three, a heist in volume five, or a cape book at any point.
- **No reset.** Nothing that cost him earlier is restored because a later volume would be
  easier to write.
- **No volume that requires the last one to be interesting.**

## Breaking

Under pressure a volume does what its own contract says: sentences shorten to the count and
the bill is reported in the same breath as the action.

The series' own failure mode is **the same book ten times**. No volume-level row can see
it. Two existing measures watch it, and neither needs a new number:

- `tools/prose/check-drift.py`, applied **across volumes** rather than within one;
- `check-uniformity.py` rows U1-U3, because ten volumes have ten chances to flatten.

No `ductus-invariants` block is declared here; the persona's block binds, and each volume
declares its own, because the failure mode is measured per volume.

## Benchmarks

**Pending, and not invented.** Volume one's four benchmark lines are in its own contract.
This layer adds a fifth: **a line that closes a volume's debt while opening the next
volume's**, with nobody standing outside the room to summarise it.

## What each volume may vary

Free: city, cast, antagonist, the specific count the book runs on, chapter count, and the
shape of its climax. Binding: the register above, the refusals, the arithmetic of the toll,
and the tightening-only rule from the persona's ledger.

## Corpus fit

The lane is `action-voice` (five works, 837,388 words, installed 2026-11-12). Volume one's
contract was derived from it. No fit has been run on prose written under the new voice,
because none exists yet; the first one is a report on a drafted chapter, not on the lane's
own pages.

## Provenance

- **Volumes planned:** ten (author, 2026-11-12).
- **Parent:** `ductus/dana-voss/ductus.md`.
- **Child:** `test-books/the-parts-still-warm/ductus.md`.
- **Designed:** 2026-11-12, at the restart. Supersedes the kalie-kirch series contract,
  which is retained in the repository as the record of the retired hand.
- **Conflicts:** the retired series contract required volume one to keep the horror
  persona's refusals. This layer replaces that requirement with the action register, by the
  author's restart instruction.

## Open questions

1. **Does the series carry a shared opening convention?** Not stated, so: none. Each volume
   opens inside motion.
2. **Where does the series bible live?** `series-binder` builds one and names no path. This
   file is the voice layer only; the canon layer is still homeless.
