# The Parts Still Warm — series ductus

*A ductus* — the individual character of this series' writing hand, and the layer between
the persona and the volumes.

**Status: WISH, unfalsified as of 2026-11-12.**

**Parent:** kalie-kirch (re-authored 2026-11-12)

**Volumes:** ten planned (author, 2026-11-12). One drafted; nine not.

**Why this file exists.** A persona is a hand; a book contract is that hand on this
material; neither of them holds a series. Book one's contract states a pace band derived
from its own best chapters, and without this layer that band is book one's private
property — volume two would start from the persona, which is a horror hand that never
selected pace, and the throttle book one spent 129,992 words learning would be learned
again. `ductus-designer`'s open question 4 has said since the skill was written that each
volume is written "under a series parent". Until 2026-11-12 no such parent existed and no
tool could read one, so the sentence had no file behind it.

## Identity

One man, ten volumes, one continuity. The series is not ten books about a vigilante; it is
one book about a bill, told in parts. What holds across all ten is the arithmetic: every
volume adds to what he owes and subtracts from what he can still be.

Each volume must be satisfiable on its own — a reader who buys volume four reads a whole
story — and must leave the series' question open. Trade a volume's ending for the hook and
the reader is gone before the next one exists.

## Register

The series carries the persona's register and lets each volume set its own pace inside a
band this layer will not let it leave. What is fixed here:

- **The instrument does not change.** Close third, past tense, one body, the count. A volume
  may change the city, the cast and the antagonist; it may not change what the prose is for.
- **The series does not decelerate, and it does not flatten.** Volume one's register is a
  **fold**, not a band: a count end near nine to twelve words, an open end near fifteen to
  seventeen, a book mean of 16 or under, and every volume required to travel the range —
  chapter means at least eight words apart across a volume, action opening before it pays.
  The numbers live in `test-books/the-parts-still-warm/ductus.md` and this file cites them
  by reference, so there is still one copy. A volume may tighten them or move its own mean
  inside the fold. None may loosen the fold, and none may sit at one end of it for a whole
  volume — that is the flatness the 2026-11-12 second revision exists to stop.
- **Each volume names its own incident.** No volume may be the one where the arithmetic
  pauses and the book becomes the aftermath of the previous volume.

## Refusals

- **No volume resolves the series.** A volume may close a debt; it may not close the
  question the series opened.
- **No genre drift between volumes.** A vigilante thriller with a body count does not become
  a procedural in volume three, a heist in volume five, or a cape book at any point, however
  well the material would take it.
- **No reset.** Nothing that cost him in an earlier volume is restored because a later
  volume would be easier to write from the earlier state.
- **No volume that requires the last one to be interesting.** Each carries its own threat
  and its own cost.

## Breaking

Under pressure a volume does what its own contract says: sentences shorten to the count and
the bill is reported in the same breath as the action.

The series' own failure mode is slower and worse: **the same book ten times.** No
volume-level row can see it, because a volume may pass every gate while volume four is
volume one with new names. Two existing measures watch it, and neither needs a new number:

- `tools/prose/check-drift.py`, applied **across volumes** rather than within one — the
  point where a series starts rewriting itself;
- `check-uniformity.py` rows U1–U3, because a series of ten volumes has ten chances to
  flatten into one shape.

No `ductus-invariants` block is declared here. The persona's block (negation 20, subject
openings 20, texture 90) binds, and each volume declares its own, because the failure mode
is measured per volume. Restating the parent's numbers in this file would put a second copy
of a number in the tree, which is the thing this project has been bitten by most.

## Benchmarks

**Pending, and not invented (2026-11-12).** No excerpts exist on disk, so this section
carries a specification and no lines, for the same reason volume one's does: a benchmark
written by the agent would be the agent's imitation of the target, and the blind sort would
then test that imitation against the corpus.

Volume one's four technique slots stand. This layer adds a fifth, which is a series
question rather than a volume one: **a line that closes a volume's debt while opening the
next volume's**, with nobody standing outside the room to summarise it.

## What each volume may vary

Free: city, cast, antagonist, the specific count the book runs on, chapter count, and the
shape of its climax. Binding: the register above, the refusals, the arithmetic of the toll,
and the tightening-only rule from the persona's ledger (2026-11-12).

## Corpus fit

**Installed at volume one, not run here (2026-11-12).** The facts are volume one's, and they
matter more here: `action-voice` is now installed (five works, 837,388 words), the fit was
run on seeded excerpts and returned 18 supported / 0 fight, and the global caps are still
derived from one light-novel series. A ten-volume series is the strongest case in this project for
building that lane before volume two drafts, because every volume after this one inherits
whatever this layer gets wrong — and unlike a single book, the error compounds nine times.

## Provenance

- **Volumes planned:** ten (author, 2026-11-12). Volume one's intake still records the
  series as "volume count open"; that line is superseded here, not edited there.
- **Parent:** `ductus/kalie-kirch/ductus.md`.
- **Child:** `test-books/the-parts-still-warm/ductus.md` (volume one).
- **Designed:** 2026-11-12, the day the author stated the series is ten books and the
  hierarchy was extended from two layers to three.
- **Conflicts:** none new. Volume one's recorded conflict — action set-piece against drafted
  aftermath — is inherited unrepaired.

## Open questions

1. **Is the pace band a series rule or volume one's?** Default: series, tightening-only,
   because nine unwritten volumes have no evidence of their own. If volume two's material
   needs a slower instrument, that is a dated decision here — not a quiet loosening in
   volume two's file.
2. **Does the series carry a shared opening convention?** Not stated, so: none. Each volume
   opens inside motion per the persona, with no series-wide device.
3. **Where does the series bible live?** `series-binder` builds one and names no path. This
   file is the voice layer only; the canon layer is still homeless.
