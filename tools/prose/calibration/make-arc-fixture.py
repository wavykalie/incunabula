#!/usr/bin/env python3
"""make-arc-fixture.py - build the monotone-arc fixture A1 must fail.

`CALIBRATION.md` records that a synthetic monotone-arc fixture was built to prove the
arc gate can fire, because a gate that never fires proves nothing. It was built ad hoc
and never kept, which is the same mistake as a threshold with no recorded derivation: the
next person has to rebuild it and cannot tell whether the rebuild still fails.

This writes it. The construction is the whole point, and it is easy to get wrong:

    the positive fraction must DECLINE with the bin, not sit at a constant

A fixed positive band is enough to make the curve reverse at every bin, which is exactly
what A1 measures - a fixture built that way scores 0.585 and PASSES, which is what the
first attempt at this file did before the band was made to fall. The bug was caught only
because the fixture is checked against the gate below, and that check is why it is a
script rather than a file of prose.

Seeded, so the output is byte-identical on every run and a failure is reproducible.

usage:  python make-arc-fixture.py <out-dir>   # then:  check-arc.py <out-dir>
"""

import os
import random
import sys

POSITIVE = "good happy love beautiful joy hope delight pleasure kind warm bright".split()
NEGATIVE = "sad hate terrible grief sorrow pain anger fear cruel dark cold worse".split()
NEUTRAL = ("the of and to a in that it was he she they as for with on not "
           "but which had been were there when what some more").split()

SEED = 7
CHAPTERS = 4
SENTENCES = 60
WORDS = 20

# Positive share at the first and last sentence. The fall is what makes the arc monotone.
POS_START, POS_END = 0.80, 0.02

# Why these numbers and not larger ones. `curve()` bins at WINDOW_WORDS = 200, so a
# "monotone" decline has to be monotone ACROSS A BIN, not across a sentence: the sign of
# each step is the difference between adjacent 200-word means. With 20-word sentences
# that is 10 sentences per bin, and a decline spread over hundreds of sentences moves
# each bin by a small fraction of the noise in it - so the steps change sign at random and
# the fixture reverses everywhere. A first attempt used 420 sentences of 16 words and
# scored 0.566, which PASSED a gate it was built to fail. The fix is a fall steep enough
# to clear the bin's own sampling noise, and that is what these constants encode.


def chapter(c):
    out = []
    for i in range(SENTENCES):
        t = i / (SENTENCES - 1)
        pos_share = POS_START * (1 - t) + POS_END * t
        neg_share = 1.0 - 0.10 - pos_share
        words = []
        for _ in range(WORDS):
            r = random.random()
            if r < neg_share:
                words.append(random.choice(NEGATIVE))
            elif r < neg_share + pos_share:
                words.append(random.choice(POSITIVE))
            else:
                words.append(random.choice(NEUTRAL))
        out.append(" ".join(words).capitalize() + ".")
    return "\n\n".join(out)


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 2
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    random.seed(SEED)
    for c in range(1, CHAPTERS + 1):
        with open(os.path.join(out, f"chapter-{c:02d}.md"), "w", encoding="utf-8") as fh:
            fh.write(chapter(c))
    print(f"wrote {CHAPTERS} chapters to {out}")
    print("Sentiment falls monotonically, so reversals per bin must be 0.")
    print("If this fixture PASSES, A1 is broken and the lexicon or the windowing is wrong.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
