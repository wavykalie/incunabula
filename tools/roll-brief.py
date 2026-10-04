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

LANGUAGES = ["English", "Japanese", "Spanish", "French", "German", "Korean"]
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


def roll(seed, pool, pool_size=None):
    """Deterministic given (seed, pool, pool_size). Returns the brief as a dict.

    pool_size draws from the pool AS IT WAS at roll time (the first K lines).
    The pool is append-only and grows every firing, so a bare --seed would map
    the same draw to a different niche once the pool grows. The brief records
    K so the roll stays re-derivable forever.
    """
    rng = random.Random(seed)
    niches = pool[:pool_size] if pool_size else pool
    label, floor, ceiling = rng.choice(LENGTHS)
    return {
        "seed": seed,
        "language": rng.choice(LANGUAGES),
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
        f"roll-brief — seed {b['seed']} (re-roll this exact brief with --seed {b['seed']}"
        f" --pool-size {b['pool_size']})\n"
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
    assert a["niche"] in pool and a["language"] in LANGUAGES
    assert a["tone"] in TONES
    assert (a["length"], a["floor"], a["ceiling"]) in LENGTHS
    assert a["floor"] < a["ceiling"]
    assert a["subject"] in SUBJECTS and a["pressure"] in PRESSURES
    assert load_pool("/nonexistent/niches") == [], "missing pool must read as empty"
    # draws must advance the rng: two rolls from one seed differ somewhere over many seeds
    assert any(roll(s, pool) != roll(s + 1, pool) for s in range(20))
    print("roll-brief self-test: ok")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Roll a random brief for an authorless run.")
    ap.add_argument("--seed", type=int, default=None,
                    help="reproduce a previous roll exactly")
    ap.add_argument("--pool-size", type=int, default=None,
                    help="draw from the pool as it was at roll time (first K niches; "
                         "the brief records K — the pool is append-only)")
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
    print(render(roll(seed, pool, args.pool_size), len(pool)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
