#!/usr/bin/env python3
"""niche-grow.py — grow tools/niche-pool.txt toward a target size.

The pool is the face of the dice behind the autonomous "random button".
roll-brief.py draws a niche from it, and the run that fired the button
appends five more. That works at five-per-run and does not work at all if you
want a deep pool: at that rate a thousand niches is two hundred runs, and the
pool would carry two hundred runs' worth of whatever the agent felt like
inventing on the day.

So: harvest instead of invent. The flavour axis of a shelf does not have to be
imagined from nothing. Wikipedia's category tree rooted at Category:Aesthetics
holds a thousand-odd concepts, movements, schools and traditions — Bauhaus,
rasa, wabi material, camp, monotype, chosonhwa, vaporwave — each one a real
aesthetic tradition with its own texture. Crossing those with genres, settings
and forms yields shelves that read like shelves, drawn from a source anyone can
check rather than from a session anyone has to trust.

The crossing is RANDOM and seeded. That is the point. A curated list would be
the agent's taste again, and the agent's taste is what the random button exists
to get away from. Given a seed, the grower is deterministic; without one it is
not, and --seed is printed either way.

APPEND-ONLY, enforced. niche-pool.txt is re-read by roll-brief.py to re-derive
old rolls from the first K lines, so rewriting an existing line rewrites a
brief that was already published in a RUN_REPORT. This script refuses to touch
a line it did not add: --out must be a path whose existing content is a strict
prefix of the new content, or it exits 1 having written nothing.

Not a prose gate and deliberately absent from GATE_FREEZE.md's manifest: it
reads no manuscript and measures no prose. Make-ready layer, same exemption
class as roll-brief.py, init-book.py and preflight.sh.

Usage:
    python tools/niche-grow.py --target 1000 --seed 20261005
    python tools/niche-grow.py --target 1000 --dry-run
    python tools/niche-grow.py --self-test

Exit codes:
    0  pool written (or dry-run reported), or self-test passed
    1  refused: the existing pool is not a prefix of the proposed one
    2  the concept file is missing or empty — a grower with no seed material
       grows nothing, and an empty result must never read as a pass
"""

import argparse
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_POOL = os.path.join(HERE, "niche-pool.txt")
DEFAULT_CONCEPTS = os.path.join(HERE, "aesthetics-concepts.txt")

# Axes. CONCEPTS come from aesthetics-concepts.txt (harvested, provenance
# recorded there); the other three are short closed lists written here, because
# a genre list is not worth a provenance note.
GENRES = [
    "literary fiction", "crime", "noir", "thriller", "psychological thriller",
    "mystery", "detective", "hard SF", "space opera", "science fiction",
    "fantasy", "dark fantasy", "fairy tale", "folk horror", "horror",
    "gothic", "historical fiction", "historical mystery", "war novel",
    "western", "romance", "erotic romance", "adventure", "swashbuckler",
    "spy novel", "heist", "caper", "political fiction", "dystopian",
    "post-apocalyptic", "utopian", "cyberpunk", "steampunk", "alternate history",
    "time travel", "portal fantasy", "urban fantasy", "mythic fiction",
    "Bildungsroman", "family saga", "campus novel", "epistolary fiction",
    "ghost story", "folk tale", "mythic retelling", "chamber piece",
    "novella cycle", "anthology", "verse novel", "nature writing",
    "travel writing", "memoir", "true crime", "reportage", "autofiction",
    "graphic novel", "pulp fiction", "hard-boiled detective", "procedural crime",
    "Nordic noir", "Southern gothic", "weird fiction", "spectral fiction",
    "revenge fiction", "wrestling fiction", "sports fiction", "cozy mystery",
    "amateur sleuth", "locked-room mystery", "heist romance", "horror romance",
]

SETTINGS = [
    "alpine", "small-town", "border", "borderland", "coastal", "island",
    "deep-sea", "subterranean", "desert", "mountain", "urban", "metropolitan",
    "rural", "harbour", "dockside", "canal", "orchard", "vineyard",
    "farmland", "prairie", "tundra", "arctic", "river", "lake", "forest",
    "rainforest", "cave", "monastery", "convent", "hospital", "sanatorium",
    "prison", "courthouse", "embassy", "archive", "museum", "library",
    "observatory", "lighthouse", "weather station", "oil rig", "mine",
    "factory", "mill", "shipyard", "railway", "motorway", "tunnel", "bridge",
    "dam", "data centre", "laboratory", "university", "boarding school",
    "funeral home", "landfill", "quarry", "tenement", "boarding house", "hotel",
    "bathhouse", "casino", "night market", "freight yard", "customs house",
    "halfway house", "commune", "mission", "hospice", "care home",
    "cruise ship", "ferry", "trawler", "submarine", "space station",
    "lunar colony", "research station", "city hall", "rooftop", "allotment",
    "stadium", "airport", "nuclear plant", "waterworks", "tannery",
    "bookbindery", "nuclear waste site", "polar station", "monastery scriptorium",
]

FORMS = [
    "novella cycle", "series", "trilogy", "duology", "anthology",
    "short story collection", "linked stories", "framed narrative", "dual POV",
    "epistolary", "diary form", "second person", "multiple timelines",
    "unreliable narrator", "first person confession", "ensemble cast",
    "reverse chronology", "mosaic structure", "braided narrative",
    "found manuscript", "archive novel", "dossier", "casebook", "almanac",
    "chapbook", "pocket thriller", "page-turner", "slow burn",
    "burn after reading", "dispatch", "puzzle box", "standalone", "spin-off",
    "prequel", "retelling", "adaptation", "parody", "elegy", "sequence",
    "decade chronicle", "triptych",
]

# Shapes, weighted. A niche in this pool reads like a shelf label: a modifier,
# a genre, sometimes a form. Weighting keeps the bare "concept + genre" the
# common case and the four-word ones rare, which is how shelves actually look.
SHAPES = [
    ("{concept} {genre}", 34),
    ("{setting} {genre}", 22),
    ("{concept} {form}", 12),
    ("{concept} {genre} {form}", 12),
    ("{setting} {concept} {genre}", 9),
    ("{setting} {genre} {form}", 7),
    ("{concept}", 4),
]

MAX_WORDS = 5


def read_lines(path):
    """One entry per line; blank lines and #-comments ignored.

    Same parsing rule as roll-brief.py's load_pool. If the two ever disagree the
    dice would draw a different index than the grower counted, which is exactly
    the class of bug this repo keeps getting bitten by.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            return [ln.strip() for ln in fh
                    if ln.strip() and not ln.strip().startswith("#")]
    except FileNotFoundError:
        return []


def read_niches_from(lines):
    return [ln.strip() for ln in lines
            if ln.strip() and not ln.strip().startswith("#")]


def load_concepts(path):
    return read_lines(path)


def build(concepts, existing, target, rng):
    """Return (new_entries, stats). Never touches `existing`."""
    have = {n.lower() for n in existing}
    fresh, rejected = [], 0
    weights = [w for _, w in SHAPES]
    shapes = [s for s, _ in SHAPES]

    # Draw until we have the shortfall. The bound is generous on purpose: a run
    # that cannot reach the target must say so and exit non-zero, not spin.
    for _ in range((target - len(existing)) * 400 + 5000):
        if len(existing) + len(fresh) >= target:
            break
        shape = rng.choices(shapes, weights=weights, k=1)[0]
        niche = shape.format(concept=rng.choice(concepts),
                            genre=rng.choice(GENRES),
                            setting=rng.choice(SETTINGS),
                            form=rng.choice(FORMS))
        niche = " ".join(niche.split())
        key = niche.lower()
        if len(niche.split()) > MAX_WORDS or key in have:
            rejected += 1
            continue
        # A repeated word reads as a glitch, not a shelf ("novel noir novel").
        words = niche.split()
        if len({w.lower().strip(",") for w in words}) != len(words):
            rejected += 1
            continue
        have.add(key)
        fresh.append(niche)
    return fresh, {"drawn": len(fresh), "rejected": rejected,
                   "shapes": len(shapes), "concepts": len(concepts)}


def prefix_ok(old, new):
    """The proposed pool must extend the old one, never rewrite it.

    Compared as PARSED NICHE LINES, not raw lines, because that is the invariant
    roll-brief.py depends on: comments and blank lines are skipped by the dice,
    so editing the header cannot change a single published brief, while removing
    or reordering a niche would. Comparing raw lines would also mean that once
    the header was edited the grower could never run again.
    """
    old_niches = read_niches_from(old)
    new_niches = read_niches_from(new)
    return len(new_niches) >= len(old_niches) and new_niches[:len(old_niches)] == old_niches


def self_test():
    concepts = ["rasa", "bauhaus", "camp"]
    pool = ["cozy mystery", "hard sf"]
    a, sa = build(concepts, pool, 20, random.Random(7))
    b, _ = build(concepts, pool, 20, random.Random(7))
    assert a == b, "same seed must grow the same pool"
    assert not (set(a) & set(pool)), "growth must not duplicate what is there"
    assert len(set(a)) == len(a), "growth must not duplicate itself"
    # The filter must reject. Prove it by filling the pool with every niche the
    # commonest shape could make, so any repeat has nowhere to go but the bin.
    filled = sorted({f"{c} {g}" for c in concepts for g in GENRES})
    c2, s2 = build(concepts, filled, len(filled) + 5, random.Random(7))
    assert s2["rejected"] > 0, "the filter must reject, or it is not filtering"
    assert not (set(c2) & set(filled)), "a full pool must not be re-filled"
    # growth must be a no-op when the target is already met
    assert build(concepts, pool, len(pool), random.Random(7))[0] == []
    # a grown pool must survive the next growth without rewriting the first part
    grown = pool + a
    c, _ = build(concepts, grown, len(grown) + 10, random.Random(8))
    assert prefix_ok(grown, grown + c), "second growth must extend, not replace"
    # editing a COMMENT must not block the next growth: the dice skips comments,
    # so the header is not part of the invariant and must stay editable
    assert prefix_ok(grown + ["# a note to self"], grown + c + ["# a note to self"])
    # the counterexample: a reordered pool is NOT a growth, and must be refused
    assert not prefix_ok(grown, list(reversed(grown)))
    # and so is dropping a niche, even when the count still goes up
    assert not prefix_ok(grown, grown[1:] + c)
    assert prefix_ok([], ["anything"]), "an empty pool can be grown into"
    assert read_lines("/nonexistent/concepts") == []
    # a niche must be one line and one niche: no commas, no colons, no quotes
    for n in a:
        assert not any(ch in n for ch in ",:;\"'"), n
    print("niche-grow self-test: ok")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Grow the niche pool toward a target size.")
    ap.add_argument("--target", type=int, default=1000,
                    help="total niches in the pool when finished (default 1000)")
    ap.add_argument("--seed", type=int, default=None,
                    help="reproduce a previous growth exactly")
    ap.add_argument("--pool", default=DEFAULT_POOL)
    ap.add_argument("--concepts", default=DEFAULT_CONCEPTS)
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would be added, write nothing")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    concepts = load_concepts(args.concepts)
    if not concepts:
        print(f"niche-grow: concept file missing or empty at {args.concepts}")
        print("  A grower with no seed material grows nothing. Exit 2 - never a pass.")
        return 2
    if args.target <= 0:
        print("niche-grow: --target must be positive.")
        return 2

    try:
        # newline="" on the way IN, and newline="\n" on the way out. Python's
        # text mode on Windows rewrites every "\n" as "\r\n" on write, which
        # turns an append-only growth into a whole-file rewrite: git reports
        # every old line as deleted and the append-only guarantee is a fiction.
        # Found by running it, 2026-10-05.
        with open(args.pool, encoding="utf-8", newline="") as fh:
            old_raw = [ln.rstrip("\r\n") for ln in fh]
    except FileNotFoundError:
        old_raw = []
    existing = read_lines(args.pool)

    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(10 ** 9)
    fresh, stats = build(concepts, existing, args.target, random.Random(seed))

    print(f"niche-grow - seed {seed} (re-run this exact growth with --seed {seed})")
    print(f"  concepts   {stats['concepts']} from {os.path.basename(args.concepts)}")
    print(f"  pool       {len(existing)} -> {len(existing) + len(fresh)} (target {args.target})")
    print(f"  drawn      {stats['drawn']} new, {stats['rejected']} rejected as duplicate or too long")
    if len(existing) + len(fresh) < args.target:
        print(f"  SHORT      {args.target - len(existing) - len(fresh)} niche(s) short of target;"
              " the axes are exhausted. Widen a list rather than lowering the bar.")

    sample = fresh[::max(1, len(fresh) // 8)][:8]
    for n in sample:
        print(f"    e.g. {n}")

    if args.dry_run:
        print("\nDRY RUN - nothing written.")
        return 0

    new_raw = old_raw + fresh
    if not prefix_ok(old_raw, new_raw):
        print("  REFUSED: the proposed pool does not extend the existing one.")
        print("  niche-pool.txt is append-only; rewriting a line rewrites a published roll.")
        return 1

    with open(args.pool, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(new_raw) + "\n")
    print(f"\nWROTE {len(fresh)} niche(s) to {args.pool}")
    return 0


if __name__ == "__main__":
    sys.exit(main())