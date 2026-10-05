#!/usr/bin/env python3
"""roll-brief.py — the dice behind the autonomous "random button".

An authorless run needs a brief nobody chose. This rolls language, niche, tone,
length, and premise seeds — and prints the seed that produced them, so any run
can be re-rolled exactly (`--seed N`).

The hybrid: the dice choose the shelf, not the story. The niche, genre, tone,
and length are rolled from tables; the premise is the agent's to invent from
the rolled seeds.

The pool grows. Every autonomous firing appends five new niches to
tools/niche-pool.txt — invented by the run, because a script cannot invent a
niche, only draw one.

Not a prose gate and deliberately absent from GATE_FREEZE.md's manifest: it
reads no manuscript and measures no prose. Make-ready layer, same exemption
class as init-book.py and preflight.sh.

Usage:
    python tools/roll-brief.py [--seed N] [--pool FILE] [--self-test]

Exit codes:
    0  brief rolled (or self-test passed)
    2  the niche pool is missing or empty — a dice with no faces rolls nothing
"""

import argparse
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_POOL = os.path.join(HERE, "niche-pool.txt")

# LANGUAGES and the draw are VERSIONED, and this is not fussiness.
#
# Dice 1 is the list this file shipped with, kept verbatim, because a published
# roll records the seed and pool size and nothing else. Change the list or the
# draw method and `--seed N --pool-size K` stops reproducing that roll, which
# breaks the one promise this tool makes. Dice 1 is how the pension-winter run
# (seed 779398044) still re-derives.
#
# Dice 2 is the current one. It is weighted toward English, because this is a
# book-production harness and not a localisation engine: the pipeline's gates,
# its voice contracts and its calibration corpus are English, and a run in
# another language is a run whose instruments are a guess. Languages that were
# never fired at are gone rather than down-weighted - Japanese, French and
# Korean had never been run, so their presence in the table was a claim about
# coverage the harness could not honour. German and Spanish stay because both
# have been delivered from this pool and are in BOOKS.yaml.
#
# A future run in a language this harness has never carried is a change to this
# table and a new dice version, not a new entry in a weights dict.
LANGUAGES = ["English", "Japanese", "Spanish", "French", "German", "Korean"]
LANGUAGES_V2 = ["English", "German", "Spanish"]
LANGUAGE_WEIGHTS = [80, 12, 8]
TONES = ["lyrical", "propulsive", "spare", "baroque", "comic",
         "elegiac", "noir", "warm", "unsettling", "satirical"]
# (label, floor words, ceiling words) — feeds init-book.py --floor/--ceiling.
LENGTHS = [
    ("short novella", 15000, 25000),
    ("novella", 25000, 45000),
    ("short novel", 50000, 70000),
    ("novel", 75000, 95000),
    ("long novel", 95000, 130000),
]
# Premise seeds: two draws that the run turns into a premise. The dice choose
# the shelf; the agent writes the story.
SUBJECTS = ["a lighthouse", "an archive", "an orchard", "a ferry", "a radio telescope",
            "a boarding house", "a seed bank", "a border crossing", "a theatre",
            "a weather station", "a family vineyard", "a decommissioned mine",
            "a night market", "a lending library", "a closed factory", "a lighthouse keeper's log"]
PRESSURES = ["a debt comes due", "a name resurfaces", "the supply line breaks",
             "an old promise is called in", "someone is declared dead",
             "the lease will not be renewed", "a witness recants",
             "the winter comes early", "a letter arrives misaddressed",
             "the company is sold"]


def load_pool(path):
    """One niche per line; blank lines and #-comments ignored."""
    try:
        with open(path, encoding="utf-8") as fh:
            return [ln.strip() for ln in fh
                    if ln.strip() and not ln.strip().startswith("#")]
    except FileNotFoundError:
        return []


def roll(seed, pool, pool_size=None, dice=2):
    """Deterministic given (seed, pool, pool_size, dice). Returns the brief.

    pool_size draws from the pool AS IT WAS at roll time (the first K lines).
    The pool is append-only and grows every firing, so a bare --seed would map
    the same draw to a different niche once the pool grows. The brief records
    K so the roll stays re-derivable forever.

    dice records which table and which draw method produced this brief, for the
    same reason: a re-roll command that omits it will stop working the day the
    table changes, and the day it stops working nobody will know why.
    """
    rng = random.Random(seed)
    niches = pool[:pool_size] if pool_size else pool
    label, floor, ceiling = rng.choice(LENGTHS)
    if dice == 1:
        language = rng.choice(LANGUAGES)
    elif dice == 2:
        language = rng.choices(LANGUAGES_V2, weights=LANGUAGE_WEIGHTS, k=1)[0]
    else:
        raise ValueError(f"unknown dice version {dice}; this tool ships dice 1 and 2")
    return {
        "seed": seed,
        "dice": dice,
        "language": language,
        "niche": rng.choice(niches),
        "tone": rng.choice(TONES),
        "length": label,
        "floor": floor,
        "ceiling": ceiling,
        "subject": rng.choice(SUBJECTS),
        "pressure": rng.choice(PRESSURES),
        "pool_size": len(niches),
    }


def render(b, pool_size):
    return (
        f"roll-brief — seed {b['seed']}, dice {b['dice']} (re-roll this exact brief with"
        f" --seed {b['seed']} --pool-size {b['pool_size']} --dice {b['dice']})\n"
        f"\n"
        f"  language : {b['language']}\n"
        f"  niche    : {b['niche']}\n"
        f"  tone     : {b['tone']}\n"
        f"  length   : {b['length']} ({b['floor']}-{b['ceiling']} words)\n"
        f"  seeds    : {b['subject']} / {b['pressure']}\n"
        f"\n"
        f"  The premise is yours to invent from the seeds.\n"
        f"\n"
        f"  pool: {pool_size} niche(s). The pool grows every firing:\n"
        f"  append 5 new niches to tools/niche-pool.txt before the next run.\n"
    )


def self_test():
    pool = ["cozy mystery", "hard sf"]
    a = roll(42, pool)
    b = roll(42, pool)
    assert a == b, "same seed must reproduce the same brief"
    # the pool grows every firing; re-derivation must survive the growth
    grown = pool + ["new niche one", "new niche two", "new niche three",
                    "new niche four", "new niche five"]
    assert roll(42, grown, pool_size=a["pool_size"]) == a, \
        "same seed + pool size must reproduce the brief after the pool grows"
    assert roll(42, grown)["niche"] != a["niche"] or True  # bare re-roll MAY differ; the flag is the contract
    assert a["niche"] in pool and a["language"] in LANGUAGES_V2
    assert a["tone"] in TONES
    assert (a["length"], a["floor"], a["ceiling"]) in LENGTHS
    assert a["floor"] < a["ceiling"]
    assert a["subject"] in SUBJECTS and a["pressure"] in PRESSURES
    assert load_pool("/nonexistent/niches") == [], "missing pool must read as empty"
    # draws must advance the rng: two rolls from one seed differ somewhere over many seeds
    assert any(roll(s, pool) != roll(s + 1, pool) for s in range(20))
    # THE CONTRACT THAT MATTERS: an old roll must survive a change to the dice.
    # Dice 1 is the table and draw method that produced every roll before dice 2,
    # so `--dice 1` has to keep reproducing it - the seed alone no longer does.
    old = roll(779398044, ["psychological thriller"], dice=1)
    assert old["language"] == "German", f"dice 1 must still roll German there, got {old['language']}"
    assert roll(779398044, ["psychological thriller"], dice=1) == old
    assert roll(779398044, ["psychological thriller"], dice=1)["dice"] == 1
    # and the two dices must be genuinely different draws, not the same table twice
    assert {roll(s, ["x"], dice=1)["language"] for s in range(50)} != \
           {roll(s, ["x"], dice=2)["language"] for s in range(50)}
    # dice 2 must never reach a language the harness has never carried
    assert all(roll(s, ["x"], dice=2)["language"] in LANGUAGES_V2 for s in range(300))
    # and it must be English-dominant, which is the point of the change
    tally = {}
    for s in range(2000):
        lang = roll(s, ["x"], dice=2)["language"]
        tally[lang] = tally.get(lang, 0) + 1
    assert tally.get("English", 0) > 3 * sum(v for k, v in tally.items() if k != "English"), \
        f"dice 2 must be English-dominant, got {tally}"
    try:
        roll(1, ["x"], dice=9)
        assert False, "an unknown dice version must not be silently accepted"
    except ValueError:
        pass
    print("roll-brief self-test: ok")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Roll a random brief for an authorless run.")
    ap.add_argument("--seed", type=int, default=None,
                    help="reproduce a previous roll exactly")
    ap.add_argument("--pool-size", type=int, default=None,
                    help="draw from the pool as it was at roll time (first K niches; "
                         "the brief records K — the pool is append-only)")
    ap.add_argument("--dice", type=int, default=2, choices=[1, 2],
                    help="which table and draw method (default 2). Use 1 to "
                         "re-derive a roll made before dice 2 existed.")
    ap.add_argument("--pool", default=DEFAULT_POOL,
                    help="niche pool file (one niche per line)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    pool = load_pool(args.pool)
    if not pool:
        print(f"roll-brief: niche pool missing or empty at {args.pool}")
        print("  A dice with no faces rolls nothing. Exit 2 — never a pass.")
        return 2

    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(10 ** 9)
    print(render(roll(seed, pool, args.pool_size, args.dice), len(pool)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
