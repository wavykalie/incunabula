#!/usr/bin/env python3
"""check-fp.py - how often the two filing checks fire on 109 unrelated human novels.

WHY THIS EXISTS
  `run/dispatch.py` refuses a filing when a new book opens on a shared sentence or shares
  an 8-word passage with a book already filed in its arm. A gate that refuses real books is
  worse than no gate: at 52 filings, one refusal per twenty books means an operator who
  learns to pass `--deviation` reflexively, which is a check turned into paperwork.

  So the gate is measured on prose that is known not to be a leak. C-dist is exactly that:
  109 public-domain novels, one work per author (fetch-dist.py enforces it), every pair
  therefore unrelated. Any pair the checks flag here is, by construction, a false positive.
  The reused `dispatch` functions are imported rather than copied - a copy of a gate is
  free to drift from the gate, and this repo has already paid for that mistake.

WHAT IS MEASURED
  * openings: every pair compared with the shipped `opening_matches` (exact, or token-set
    overlap >= OPENING_MIN_OVERLAP on openers of >= OPENING_MIN_TOKENS words).
  * passages: every pair compared for a shared PHRASE_N-word run carrying
    PHRASE_MIN_CONTENT content words. Exact via packed 32-bit gram hashes over all books:
    9.3M grams, sorted once, runs of equal hash grouped by book. No sampling.
  * boilerplate: grams appearing in ten or more books. If the corpus still carried
    Project Gutenberg's header, every book would collide with every other and the passage
    numbers would be a fact about the fetch step, not about the prose. Measured so that
    possibility is excluded rather than assumed away.

THE NUMBER THAT MATTERS
  Per-pair rate is not the operating quantity. A filing is refused if it collides with any
  book already filed, so the exposure of an arm is its pair count: n(n-1)/2. The report
  carries the extrapolation to the primary arm (20 books, 190 pairs) and to the full run
  (52 books, 1326 pairs), and says plainly that a 19th-century corpus is more formulaic
  than a generated novel, so these are if anything conservative.

usage:
    python analysis/check-fp.py                      measure, print the table
    python analysis/check-fp.py --out FILE           also write the markdown report
    python analysis/check-fp.py --selftest           prove the machinery on known collisions
"""

import argparse
import csv
import importlib.util
import itertools
import json
import os
import re
import sys
import zlib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.abspath(os.path.join(HERE, ".."))
SHIFT = 7            # 109 books < 128; the low bits carry the book index
MASK = (1 << SHIFT) - 1
BOILERPLATE_BOOKS = 10


def load_dispatch():
    path = os.path.join(STUDY, "run", "dispatch.py")
    spec = importlib.util.spec_from_file_location("study_dispatch", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


D = load_dispatch()


# ------------------------------------------------------------------ the gate itself
def fingerprint(s):
    """64 bits of the string, in two independent halves.

    A single 32-bit crc32 is not enough here and that was worth learning the hard way:
    over 9.3M grams it collides about 10,000 times, which flagged 66% of human pairs at
    every n - a flat curve that is the signature of hash noise rather than of prose. Two
    32-bit halves make a chance collision about 1 in 400,000 runs of this measurement.
    """
    b = s.encode("utf-8")
    return (zlib.crc32(b) << 32) | zlib.adler32(b)


def packed_grams(text, idx, n=None, content=None):
    """Every distinctive n-gram in `text`, packed as (64-bit print << SHIFT) | book."""
    toks = D.phrase_tokens(text)
    out = []
    n = n or D.PHRASE_N
    content = content or D.PHRASE_MIN_CONTENT
    for i in range(len(toks) - n + 1):
        gram = toks[i:i + n]
        if sum(1 for t in gram if D.is_content(t)) < content:
            continue
        out.append((fingerprint(" ".join(gram)) << SHIFT) | idx)
    return out


def scan_packed(packed):
    """(pair counts, gram -> book count where the gram is suspiciously widespread)."""
    packed.sort()
    pairs = Counter()
    wide = Counter()
    i, n = 0, len(packed)
    while i < n:
        h = packed[i] >> SHIFT
        j = i
        books = set()
        while j < n and (packed[j] >> SHIFT) == h:
            books.add(packed[j] & MASK)
            j += 1
        if len(books) >= 2:
            for a, b in itertools.combinations(sorted(books), 2):
                pairs[(a, b)] += 1
            if len(books) >= BOILERPLATE_BOOKS:
                wide[h] = len(books)
        i = j
    return pairs, wide


def find(ids, texts, opening=True, passage=True, n=None, content=None):
    """Both gates over a list of texts. Returns pairs and per-book flags."""
    out = {"openings": {}, "passages": Counter(), "wide": Counter()}
    if opening:
        heads = {i: D.opening_sentence(t) for i, t in enumerate(texts)}
        for a, b in itertools.combinations(range(len(texts)), 2):
            if D.opening_matches(heads[a], heads[b]):
                out["openings"][(a, b)] = (heads[a], heads[b])
    if passage:
        packed = []
        for i, t in enumerate(texts):
            packed.extend(packed_grams(t, i, n=n, content=content))
        pairs, wide = scan_packed(packed)
        out["passages"] = pairs
        out["wide"] = wide
    flagged = set()
    for a, b in list(out["openings"]) + list(out["passages"]):
        flagged.add(a)
        flagged.add(b)
    out["flagged"] = flagged
    return out


# ------------------------------------------------------------------ readable evidence
def passages_between(ta, tb, limit=4):
    a = D.phrase_tokens(ta)
    b = D.phrase_tokens(tb)
    runs = D.shared_runs(a, D.distinctive_grams(b), " " + " ".join(b) + " ")
    return runs[:limit]


CHAPTER_START = re.compile(r"(?im)^\s*(chapter|part|book)\b")


def prose_start(text, within=800):
    """The text from its first chapter heading, if one arrives early enough to be a front
    matter boundary rather than a late section."""
    lines = text.splitlines()
    seen = 0
    for i, line in enumerate(lines):
        if CHAPTER_START.match(line) and seen <= within:
            return "\n".join(lines[i:])
        seen += len(line.split())
    return text


def rate(k, n):
    return f"{k} of {n:,}" + (f" ({k / n:.3%})" if n else "")


def expected(k, n_pairs, arm_pairs):
    return (k / n_pairs) * arm_pairs if n_pairs else 0.0


# ------------------------------------------------------------------ report
PREMISE_POOL = os.path.join(STUDY, "premises", "candidates.json")
FROZEN = (os.path.join(STUDY, "premises", "frozen", "premises-v1.json"),
          os.path.join(STUDY, "premises", "frozen", "premises-v2.json"))


def premise_corpus():
    """(id, genre, title, text) for the 40 pool premises, rendered by premise.py itself.

    Imported, not re-derived: the pool is stored as six labelled fields, and the text the
    arms receive is `render()`'s join of them. A second implementation of that join would
    measure a text no book was ever drafted from.
    """
    spec = importlib.util.spec_from_file_location(
        "study_premise", os.path.join(STUDY, "premises", "premise.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return [(p["id"], p.get("genre", ""), p.get("title_label", ""), mod.render(p))
            for p in mod.load()]


def targeted_premise_ids():
    ids = []
    for path in FROZEN:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                ids.extend(p["id"] for p in json.load(fh)["premises"])
    return ids


def measure_premises(out_path=None):
    """The gates on the premise texts: a pair that collides here is seeded, not leaked.

    The gate compares books, and books drafted from two premises that already share a long
    run of words have a legitimate reason to share it. The human corpus cannot see that
    channel - it has no premises - so it is measured separately, on the inputs themselves.
    """
    corpus = premise_corpus()
    ids = [c[0] for c in corpus]
    texts = [c[3] for c in corpus]
    words = [len(t.split()) for t in texts]
    npairs = len(corpus) * (len(corpus) - 1) // 2
    res = find(ids, texts)

    # A zero is only a result if the same loop can produce a one. Append a copy of the first
    # premise and require the gate to flag it; if this line ever reports no, every zero
    # below is a bug wearing a finding's clothes.
    probe = find(ids + ["probe-copy"], texts + [texts[0]])
    probe_hits = probe["passages"].get((0, len(texts)), 0)
    probe_caught = (0, len(texts)) in probe["passages"]

    target = set(targeted_premise_ids())
    idx = [k for k, c in enumerate(corpus) if c[0] in target]
    sub_texts = [texts[k] for k in idx]
    sub_ids = [ids[k] for k in idx]
    sub_res = find(sub_ids, sub_texts)
    sub_pairs = len(idx) * (len(idx) - 1) // 2

    def label(k):
        pid, genre, title, _ = corpus[k]
        return f"`{pid}` {genre} — *{title}*"

    lines = []
    w = lines.append
    w("# Do the filing checks fire on the premises themselves?")
    w("")
    w(f"The second false-positive channel, and one the human corpus cannot show: books from"
      f" two premises that already share wording have a legitimate reason to share it, and"
      f" the gate does not skip different-premise pairs. Measured on the premise texts"
      f" exactly as `premises/premise.py` renders them (fields joined in fixed order, no"
      f" labels), at the constants shipped in `run/dispatch.py`.")
    w("")
    w(f"Pool: **{len(corpus)}** premises, {min(words)}–{max(words)} words "
      f"(mean {sum(words) / len(words):.0f}), {npairs:,} pairs. "
      f"Targeted by the study: **{len(idx)}** premises, {sub_pairs:,} pairs "
      f"(the frozen sets, not a hand-picked subset).")
    w("")
    w(f"Machinery check: a copy of `{ids[0]}` appended as an extra premise is flagged in "
      f"{probe_hits} passages - "
      + ("the loop finds a seeded collision when there is one." if probe_caught else
         "**FAILED**, so the zeros below mean nothing."))
    w("")
    w("| corpus | pairs | opening collisions | shared " + str(D.PHRASE_N) +
      "-word passages |")
    w("|---|---|---|---|")
    w(f"| all 40 premises | {npairs:,} | {len(res['openings'])} | "
      f"{len(res['passages'])} |")
    w(f"| the {len(idx)} targeted premises | {sub_pairs:,} | "
      f"{len(sub_res['openings'])} | {len(sub_res['passages'])} |")
    w("")
    w("| run length | pool pairs flagged |")
    w("|---|---|")
    for n, pairs, _ in curve(texts):
        mark = " **shipped**" if n == D.PHRASE_N else ""
        w(f"| {n} words{mark} | {pairs} of {npairs:,} |")
    w("")
    if res["openings"] or res["passages"]:
        w("## Pairs that collide on their own inputs")
        w("")
        for (a, b), (ha, hb) in sorted(res["openings"].items())[:10]:
            w(f"- openings: {label(a)} / {label(b)}")
            w(f"  - `{ha[:100]}` / `{hb[:100]}`")
        for (a, b), k in sorted(res["passages"].items(), key=lambda kv: -kv[1])[:10]:
            w(f"- {label(a)} / {label(b)} — {k} shared grams")
            for s in passages_between(texts[a], texts[b]):
                w(f"  - `{D.clip(s, 40)}`")
        w("")
    else:
        w("## What this means for the run")
        w("")
        w("No two premises share an opening or a " + str(D.PHRASE_N) + "-word run, so no pair"
          " of books is seeded with text the gate would refuse. The seeded channel is closed"
          " at the premise layer for this pool, and the human-corpus figure is the whole"
          " false-positive budget.")
        w("")
    w("## Limits")
    w("")
    w("- Absence of a shared run is not absence of shared *wording*: two premises can both"
      " say \"a fishing town where everyone knows everyone\" without a 24-word verbatim"
      " overlap, and a model drafting from them may still reach for the same phrasing. The"
      " measurement bounds the seed, not the echo.")
    w("- The gates skip same-premise pairs by design, because the two books from one premise"
      " are *supposed* to be related. This table is about different-premise pairs, which the"
      " gates do not skip and which the skip does not protect.")
    w("- Premises are 64–91 words, so the 24-word bar is a large share of a premise: the"
      " measurement is plausible at these sizes rather than merely conservative.")
    text = "\n".join(lines) + "\n"
    print(text)
    if out_path:
        with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"report -> {out_path}")
    return 0


def curve(texts, ns=(8, 12, 16, 20, 24, 32)):
    """Pairs flagged at each candidate run length, on the same corpus."""
    rows = []
    for n in ns:
        pairs, _ = scan_packed([g for i, t in enumerate(texts)
                                for g in packed_grams(t, i, n=n)])
        rows.append((n, len(pairs), len({i for p in pairs for i in p})))
    return rows


def measure(books_root, source_tsv, out_path=None):
    books = sorted(os.listdir(books_root))
    books = [b for b in books if os.path.isdir(os.path.join(books_root, b,
                                                             "manuscript"))]
    if len(books) < 2:
        print(f"need at least two books under {books_root}; found {len(books)}")
        return 1
    if len(books) >= (1 << SHIFT):
        print(f"{len(books)} books exceeds the {MASK + 1}-book packing limit")
        return 2
    meta = {}
    if source_tsv and os.path.exists(source_tsv):
        with open(source_tsv, encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                meta[r["slots"]] = r
    texts, words = [], []
    for b in books:
        t, _ = D.manuscript_text({"book_id": b}, books_root)
        texts.append(t)
        words.append(len(t.split()))

    res = find(books, texts)
    # A generated book is filed as prose; a Gutenberg text begins with title-page matter, so
    # the gate as filed compares a title page on this corpus. Both numbers are reported:
    # "as filed" is the gate's literal behaviour, "prose opener" is the sentence it will
    # compare on a book that starts where the study's books start.
    prose = find(books, [prose_start(t) for t in texts], passage=False)
    n_books = len(books)
    n = len(books)
    npairs = n * (n - 1) // 2

    def label(i):
        m = meta.get(books[i], {})
        author = (m.get("author") or "").split(",")[0]
        title = (m.get("title") or "").strip()
        return f"`{books[i]}`" + (f" {author} — *{title}*" if author else "")

    lines = []
    w = lines.append
    w("# How often the two filing checks fire on unrelated human novels")
    w("")
    w(f"Corpus: **{n}** books, {sum(words):,} words "
      f"({min(words):,}–{max(words):,} per book), one work per author — every pair is "
      f"unrelated by construction, so every flag here is a false positive.")
    w(f"Gates measured exactly as shipped in `run/dispatch.py`, imported not copied: an "
      f"opening either equal after normalisation or at least "
      f"{D.OPENING_MIN_OVERLAP:.2f} token overlap with openers of "
      f">= {D.OPENING_MIN_TOKENS} words; a passage of `{D.PHRASE_N}` words carrying "
      f">= {D.PHRASE_MIN_CONTENT} content words. All {npairs:,} pairs compared, no "
      f"sampling.")
    w("")
    w("| gate | pairs flagged | books flagged | per-pair rate |")
    w("|---|---|---|---|")
    w(f"| opening sentence, as filed | {len(res['openings'])} of {npairs:,} | "
      f"{len({i for p in res['openings'] for i in p})} of {n} | "
      f"{rate(len(res['openings']), npairs).split('(')[-1].rstrip(')')} |")
    w(f"| opening sentence, from the first chapter heading (prose opener) | "
      f"{len(prose['openings'])} of {npairs:,} | "
      f"{len({i for p in prose['openings'] for i in p})} of {n} | "
      f"{rate(len(prose['openings']), npairs).split('(')[-1].rstrip(')')} |")
    w(f"| shared {D.PHRASE_N}-word passage | {len(res['passages'])} of {npairs:,} | "
      f"{len({i for p in res['passages'] for i in p})} of {n} | "
      f"{rate(len(res['passages']), npairs).split('(')[-1].rstrip(')')} |")
    w("")
    w("## How the passage length was chosen")
    w("")
    w("The same pass at each candidate length. A gate has to be quiet on unrelated books; a"
      " leaked context hands over paragraphs, so length costs almost no sensitivity.")
    w("")
    w("| run length | pairs flagged | books flagged | as a share of pairs |")
    w("|---|---|---|---|")
    for n, pairs, hit in curve(texts):
        mark = " **shipped**" if n == D.PHRASE_N else ""
        w(f"| {n} words{mark} | {pairs} of {npairs:,} | {hit} of {n_books} | "
          f"{pairs / npairs:.3%} |")
    w("")
    w("## What that means at this study's arm sizes")
    w("")
    w("A filing is refused if it collides with **any** book already filed, so the exposure "
      "is the pair count, not the pair rate.")
    w("")
    w("| arm | pairs | expected false refusals (openings) | expected (passages) |")
    w("|---|---|---|---|")
    for name, size in (("primary Arm A or B (20 books)", 20), ("voice arm (6)", 6),
                       ("full run (52 books)", 52)):
        p = size * (size - 1) // 2
        w(f"| {name} | {p:,} | {expected(len(res['openings']), npairs, p):.3f} | "
          f"{expected(len(res['passages']), npairs, p):.3f} |")
    w("")
    if res["wide"]:
        w(f"**Boilerplate diagnostic failed:** {len(res['wide'])} grams appear in "
          f"{BOILERPLATE_BOOKS}+ books. That is a fact about the fetch step, not the "
          f"prose; the passage numbers above cannot be read until it is fixed.")
    else:
        w(f"Boilerplate diagnostic: no gram appears in {BOILERPLATE_BOOKS}+ books, so the "
          f"corpus carries no shared header text and the passage numbers are about prose.")
    w("")
    if prose["openings"]:
        w("## Opening collisions on prose openers (the number that applies)")
        w("")
        for (a, b), (ha, hb) in sorted(prose["openings"].items())[:20]:
            w(f"- {label(a)} / {label(b)}")
            w(f"  - `{ha[:120]}`")
            w(f"  - `{hb[:120]}`")
        w("")
    if res["openings"]:
        w("## Opening collisions as filed (title-page matter included)")
        w("")
        for (a, b), (ha, hb) in sorted(res["openings"].items())[:20]:
            w(f"- {label(a)} / {label(b)}")
            w(f"  - `{ha[:120]}`")
            w(f"  - `{hb[:120]}`")
        w("")
    if res["passages"]:
        w("## Passage collisions")
        w("")
        worst = sorted(res["passages"].items(), key=lambda kv: -kv[1])[:10]
        for (a, b), k in worst:
            w(f"### {label(a)} / {label(b)} — {k} shared grams")
            w("")
            for s in passages_between(texts[a], texts[b]):
                w(f"- `{D.clip(s, 40)}`")
            w("")
    if not res["openings"] and not res["passages"]:
        w("## Collisions")
        w("")
        w("None. On this corpus the gates refuse nothing.")
        w("")
    w("## Limits of this measurement")
    w("")
    w("- Human novels are the honest control for *false* positives but not for the true "
      "positive rate: a leak produces many long shared passages, and nothing here says how "
      "many. The gate only has to be quiet on unrelated books and loud on a copy.")
    w("- C-dist is 19th- and early-20th-century public-domain prose: more formulaic, more "
      "shared idiom, longer chapters than a 2026 generated novel. If anything that "
      "overstates the false-positive rate, which is the safe direction for a gate.")
    w("- One work per author means a pair is never two books by one hand. An author "
      "repeating themselves is not a leak and is not measured here.")
    text = "\n".join(lines) + "\n"
    print(text)
    if out_path:
        with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"report -> {out_path}")
    return 0


# ------------------------------------------------------------------ selftest
def selftest():
    """Known answers on three synthetic books: the machinery, not the corpus."""
    assert fingerprint("a b c") != fingerprint("c b a"), "fingerprint is order-blind"
    body = ("The bus was already late when Oskar reached the stop. Rain had stopped an "
            "hour before. ")
    leak = ("The smell of the stairwell was still in her coat when she reached the street, "
            "and the rain had stopped an hour before she finally turned the key in the lock "
            "and went up the stairs without turning on the light. The landing was dark and "
            "the door to her flat stood open an inch, which was how she knew someone had "
            "been there, and had not been careful about it. ")
    clean = ("Nobody answered the door the first time, so I knocked again. The kettle was "
             "still warm when I came down. The dog barked once, decided against it, and "
             "lay down. ") * 25
    a = "The ledger was open on the table when the inspector came in. " + body * 40 + leak
    b = ("Inspector Rothe arrived without an appointment and waited in the hall. "
         + body * 40 + leak)
    swapped = ("Oskar took the long way round by the canal and said nothing. " + body * 40
               + leak.replace("her coat", "his coat"))

    checks = []
    res = find(["a", "b", "c"], [a, b, clean], opening=False)
    checks.append(("shared passage flags the leaked pair only",
                   set(res["passages"]) == {(0, 1)}, sorted(res["passages"])))
    res = find(["a", "b"], [a, swapped], opening=False)
    checks.append(("one substituted word inside the leak still flags",
                   set(res["passages"]) == {(0, 1)}, sorted(res["passages"])))
    res = find(["a", "c"], [a, clean], opening=False)
    checks.append(("unrelated prose flags nothing",
                   not res["passages"], sorted(res["passages"])))

    heads = ["She walked to the door and opened it without a word.",
             "Nobody answered the door the first time.",
             "she walked to the door and opened it without any word."]
    res = find(["a", "b", "c"], heads, passage=False)
    checks.append(("reworded opening flags its pair only",
                   set(res["openings"]) == {(0, 2)}, sorted(res["openings"])))

    for name, ok, detail in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if not ok else ""))
    return 0 if all(ok for _, ok, _ in checks) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--books", default=os.path.join(STUDY, "books"))
    ap.add_argument("--source", default=os.path.join(STUDY, "corpus", "dist-source.tsv"))
    ap.add_argument("--out")
    ap.add_argument("--premises", action="store_true",
                   help="measure the gates on the premise pool's own text")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.premises:
        return measure_premises(args.out or os.path.join(
            HERE, "filing-checks-premises.md"))
    return measure(args.books, args.source, args.out)


if __name__ == "__main__":
    sys.exit(main())
