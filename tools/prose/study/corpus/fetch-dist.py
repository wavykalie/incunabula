#!/usr/bin/env python3
"""fetch-dist.py - build Arm C's distribution corpus (C-dist), >=100 public-domain novels.

WHY THIS IS NOT ARM C
  Design §5's Arm C is ten books, and REDTEAM.md B1 shows why ten cannot set a threshold:
  an IQR from ten books is the gap between the 3rd and 8th book, and §10's whole deliverable
  is a threshold. So the study splits the human arm by job:

      C-deep    10 books, chosen for excerpt rating and close reading (§5, §8.6)
      C-dist   ~120 books, the distribution every IQR, threshold and false-positive rate
                in §9 and §10 is measured on

  This script builds C-dist. It is the amendment REDTEAM.md lists first, because it must be
  settled before anything is derived from it.

SELECTION IS A RULE, NOT A TASTE
  §5 rules 1-4 are enforced here rather than eyeballed:
    1. public domain        - Project Gutenberg only, hence pre-1929 US publication
    2. novel-length prose   - subject must carry "Fiction"; poetry, drama, essays and
                              short-story collections are excluded by heading
    3. spread of genre/era  - stratified across era and genre buckets, one cell at a time
    4. one work per author  - the author's surname is a key; a second book by the same
                              author is dropped, so no single voice can masquerade as
                              "human prose in general"
  Selection is deterministic: the same catalogue yields the same list in the same order, so
  the file in `dist-source.tsv` can be checked against a re-run.

ERA IS A PROXY AND SAYS SO
  Gutenberg's catalogue has no publication year. Rather than invent one, era comes from the
  author's birth year, parsed from the catalogue's own "Surname, Forename, 1789-1851" field,
  and is named `era_proxy` everywhere it appears. It tracks the generation whose prose this
  is; it is not the year of publication, and the report must not call it that.

WHAT IT DOES NOT DO
  It does not select Arm C's ten, does not rate anything, and does not redistribute the
  texts: it fetches them into a git-ignored `books/` tree for measurement only. The
  committed artifact is `dist-source.tsv` (ids, authors, strata, hashes), not the prose.

usage:
    python corpus/fetch-dist.py --select [--target 120]
    python corpus/fetch-dist.py --fetch [--limit N]
    python corpus/fetch-dist.py --check

A second stratum is built beside the baseline, never over it: `--out-source`, `--source`,
`--log` and `--slot-prefix` keep C-dist's files and slots untouched. The selection is the same
deterministic list, optionally with the books already fetched removed by gutenberg id:

    python corpus/fetch-dist.py --select --target 300 \
        --skip-log corpus/dist-fetch-log.tsv \
        --out-source corpus/dist-source-2.tsv --slot-prefix C-dist2-
    python corpus/fetch-dist.py --fetch \
        --source corpus/dist-source-2.tsv --log corpus/dist-fetch-log-2.tsv
"""

import argparse
import csv
import hashlib
import os
import re
import sys
import urllib.request
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
STUDY = os.path.dirname(HERE)
CATALOG = os.path.join(HERE, "pg_catalog.csv")
SOURCE = os.path.join(HERE, "dist-source.tsv")
BOOKS = os.path.join(STUDY, "books")
LOG = os.path.join(HERE, "dist-fetch-log.tsv")
REJECTS = os.path.join(HERE, "dist-rejects.tsv")

CATALOG_URL = "https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv"
TEXT_URL = "https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"

# Era buckets on the author's birth year. Buckets are the author generation, which is what
# makes the prose era; they are not publication decades and are labelled era_proxy.
ERA_BUCKETS = (
    ("born <1800", None, 1799),
    ("born 1800-1829", 1800, 1829),
    ("born 1830-1859", 1830, 1859),
    ("born 1860-1889", 1860, 1889),
    ("born >=1890", 1890, 3000),
)

# First match wins. Gutenberg subjects are Library-of-Congress-shaped headings, so these are
# the headings that actually occur rather than a genre taxonomy invented for the study.
GENRE_RULES = (
    ("science fiction", (r"science fiction", r"space flight", r"time travel")),
    ("detective", (r"detective", r"mystery", r"murder -- investigation", r"\bpolice\b")),
    ("gothic/horror", (r"horror", r"ghost stories", r"gothic", r"supernatural",
                       r"vampires", r"monsters")),
    ("romance", (r"love stories", r"\bromance\b", r"courtship", r"man-woman relationships")),
    ("historical", (r"historical fiction", r"-- history -- fiction", r"-- fiction\b.*history")),
    ("adventure", (r"adventure", r"sea stories", r"voyages and travels", r"western stories",
                   r"treasure")),
    ("comedy", (r"humor", r"humour", r"comic", r"satire", r"wit and humor")),
    ("juvenile", (r"juvenile fiction", r"children's fiction", r"conduct of life -- fiction")),
)

# A subject heading that means "this is not a novel". Short-story collections are excluded
# deliberately: §5 asks for novel-length prose, and a 5,000-word book cannot be compared on
# per-book rows without becoming a length finding (REDTEAM.md B6).
REJECT_SUBJECT = re.compile(
    r"poetry|poems|drama|plays|essays|short stories|letters|diaries|correspondence|"
    r"criticism|biography|autobiograph|speeches|philosophy|religion|science|"
    r"history, modern|politics|description and travel|guidebooks|cookery",
    re.I)
REJECT_TITLE = re.compile(
    r"\b(collected works|complete works|works of|selections|anthology|omnibus|"
    r"vol(ume)?\.?\s*(i{1,3}|iv|v|\d+)\b)", re.I)

MIN_WORDS, MAX_WORDS = 20000, 400000
CHAPTER = re.compile(
    r"^[ \t]*(?:CHAPTER|Chapter)[ \t]+"
    r"(?:[IVXLCDM]{1,7}|\d{1,3}|ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|"
    r"ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|"
    r"TWENTY|FIRST|SECOND|THIRD)\b[^\n]{0,60}$", re.M)
PG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\n",
                      re.I)
PG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*", re.I)
YEAR = re.compile(r"\b(1[5-9]\d\d)\b")


def words(text):
    return len(text.split())


# ------------------------------------------------------------------ selection


def birth_year(authors):
    """First birth year in the catalogue's author field, or None."""
    m = re.search(r"\b(\d{4})-\d{0,4}\b", authors or "")
    if m:
        return int(m.group(1))
    return None


def era_bucket(year):
    if year is None:
        return "unknown"
    for name, lo, hi in ERA_BUCKETS:
        if (lo is None or year >= lo) and (hi is None or year <= hi):
            return name
    return "unknown"


def genre_bucket(subjects):
    s = (subjects or "").lower()
    for name, pats in GENRE_RULES:
        if any(re.search(p, s) for p in pats):
            return name
    return "general"


def surname(authors):
    first = (authors or "").split(";")[0]
    return first.split(",")[0].strip().lower()


def key_title(title):
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def candidates(rows):
    """Every catalogue row that satisfies §5's rules, deduplicated to one work per author."""
    kept, seen_author, seen_title = [], set(), set()
    for r in rows:
        if (r.get("Type") or "").strip() != "Text":
            continue
        if "en" not in [x.strip() for x in (r.get("Language") or "").split(";")]:
            continue
        subj = r.get("Subjects") or ""
        title = (r.get("Title") or "").strip()
        authors = (r.get("Authors") or "").strip()
        if not authors or not title:
            continue
        if "fiction" not in subj.lower():
            continue
        if REJECT_SUBJECT.search(subj) or REJECT_TITLE.search(title):
            continue
        # One work per author (§5 rule 4). Keeping the first (lowest) catalogue id.
        au, tt = surname(authors), key_title(title)
        if not au or au in seen_author or tt in seen_title:
            continue
        seen_author.add(au)
        seen_title.add(tt)
        by = birth_year(authors)
        kept.append({
            "gutenberg_id": r.get("Text#", "").strip(),
            "author": authors,
            "title": title,
            "era_proxy": era_bucket(by),
            "birth_year": "" if by is None else by,
            "genre_bucket": genre_bucket(subj),
            "subjects": subj.replace("\n", " ")[:300],
        })
    kept.sort(key=lambda d: int(d["gutenberg_id"]))
    return kept


def select(cands, target):
    """Round-robin over (era, genre) cells, so no single cell can dominate the corpus.

    Each pass takes the next unused candidate from every cell that still has one, cells
    ordered by how few they have contributed so far. That keeps the cheapest available
    thing to be breadth, not the largest pool.
    """
    cells = defaultdict(list)
    for c in cands:
        cells[(c["era_proxy"], c["genre_bucket"])].append(c)
    for v in cells.values():
        v.sort(key=lambda d: int(d["gutenberg_id"]))
    taken, given = [], Counter()
    order = sorted(cells)
    while len(taken) < target:
        progressed = False
        for cell in sorted(order, key=lambda k: (given[k], k)):
            if not cells[cell]:
                continue
            taken.append(cells[cell].pop(0))
            given[cell] += 1
            progressed = True
            if len(taken) >= target:
                break
        if not progressed:
            break
    return taken


def write_source(chosen, path=SOURCE, prefix="C-dist-"):
    cols = ("slots", "gutenberg_id", "author", "title", "era_proxy", "birth_year",
            "genre_bucket", "subjects", "url")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, cols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for i, c in enumerate(chosen, 1):
            row = dict(c, slots=f"{prefix}{i:03d}",
                       url=TEXT_URL.format(id=c["gutenberg_id"]))
            w.writerow(row)
    return path


def read_source(path=SOURCE):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# ------------------------------------------------------------------ fetch


def strip_pg(text):
    m = PG_START.search(text)
    if m:
        text = text[m.end():]
    m = PG_END.search(text)
    if m:
        text = text[:m.start()]
    return text.strip()


def split_chapters(text, target=2500):
    """The book's own chapters when it has them, else fixed word-count slices.

    Chapter structure is an outcome, not an analysis unit (REDTEAM.md B3), so the fallback
    is not a defect: it keeps a book with no recoverable chapter headings measurable on
    every segment-level row instead of dropping it.
    """
    marks = [m.start() for m in CHAPTER.finditer(text)]
    parts = []
    if len(marks) >= 4:
        for i, start in enumerate(marks):
            end = marks[i + 1] if i + 1 < len(marks) else len(text)
            parts.append(text[start:end].strip())
        parts = [p for p in parts if words(p) >= 300]
    if len(parts) < 4:
        parts, buf = [], []
        for para in re.split(r"\n\s*\n", text):
            buf.append(para)
            if words(" ".join(buf)) >= target:
                parts.append("\n\n".join(buf))
                buf = []
        if buf and words(" ".join(buf)) >= 200:
            parts.append("\n\n".join(buf))
    return [p for p in parts if p]


def fetch_one(row, quiet=False):
    bid = row["gutenberg_id"]
    url = TEXT_URL.format(id=bid)
    with urllib.request.urlopen(url, timeout=120) as r:
        raw = r.read()
    text = strip_pg(raw.decode("utf-8", errors="ignore"))
    n_raw = words(text)
    if not (MIN_WORDS <= n_raw <= MAX_WORDS):
        return None, f"length {n_raw}w outside {MIN_WORDS}-{MAX_WORDS}"
    parts = split_chapters(text)
    if len(parts) < 4:
        return None, f"only {len(parts)} segment(s)"
    slot = row["slots"]
    d = os.path.join(BOOKS, slot, "manuscript", "chapters")
    os.makedirs(d, exist_ok=True)
    for i, p in enumerate(parts, 1):
        with open(os.path.join(d, f"chapter-{i:02d}.md"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(p.rstrip() + "\n")
    rec = {
        "slots": slot, "gutenberg_id": bid, "author": row["author"],
        "title": row["title"],        "era_proxy": row["era_proxy"],
        "genre_bucket": row["genre_bucket"], "raw_words": n_raw,
        # Everything before the first chapter heading - title page, dedication, preface -
        # is deliberately not filed, so the analysable count is a separate column. The
        # difference between the two is front matter, not damage.
        "chapters_words": sum(words(p) for p in parts),
        "chapters": len(parts), "sha256": hashlib.sha256(raw).hexdigest(),
        "url": url,
    }
    return rec, None


def append_log(rec, path=LOG):
    exists = os.path.exists(path)
    cols = ("slots", "gutenberg_id", "author", "title", "era_proxy", "genre_bucket",
            "raw_words", "chapters_words", "chapters", "sha256", "url")
    with open(path, "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, cols, delimiter="\t", extrasaction="ignore")
        if not exists:
            w.writeheader()
        w.writerow(rec)


def known_rejects(path=REJECTS):
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8", newline="") as fh:
        return {(r["slots"], r["reason"]) for r in csv.DictReader(fh, delimiter="\t")}


def append_reject(row, why, path=REJECTS):
    """A dropped book is data (design §3), so the reason is filed, not just printed."""
    exists = os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, ("slots", "gutenberg_id", "author", "title", "reason"),
                           delimiter="\t", extrasaction="ignore")
        if not exists:
            w.writeheader()
        w.writerow(dict(row, reason=why))


def check(bookdir=BOOKS, log=LOG):
    """A run that read zero books is a failure, never a pass (README, repo defect log)."""
    if not os.path.exists(log):
        print(f"no {log}. Nothing fetched.")
        return 1
    with open(log, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    bad = 0
    for r in rows:
        d = os.path.join(bookdir, r["slots"], "manuscript", "chapters")
        files = sorted(os.listdir(d)) if os.path.isdir(d) else []
        if len(files) != int(r["chapters"]):
            print(f"  {r['slots']}: {len(files)} chapter file(s), log says {r['chapters']}")
            bad += 1
            continue
        got = sum(words(open(os.path.join(d, f), encoding="utf-8", errors="ignore").read())
                  for f in files)
        # Compare against the SEGMENTED count, not the whole downloaded file. Front matter
        # before the first chapter heading is not filed on purpose, so measuring the check
        # against raw words flags a correctly split book as damaged.
        want = (r.get("chapters_words") or "").strip()
        if not want:
            print(f"  {r['slots']}: log has no chapters_words; re-fetch to record it")
            bad += 1
            continue
        if got != int(want):
            print(f"  {r['slots']}: {got}w on disk vs {want}w segmented in log")
            bad += 1
    if not rows:
        print("log is empty: a corpus of zero books is a failure, not a pass")
        return 1
    eras = Counter(r["era_proxy"] for r in rows)
    genres = Counter(r["genre_bucket"] for r in rows)
    dropped = sum(int(r["raw_words"]) - int(r["chapters_words"]) for r in rows)
    print(f"{len(rows)} book(s) filed, {bad} problem(s), "
          f"{dropped:,}w of front matter not filed")
    print("  era:   " + ", ".join(f"{k} {v}" for k, v in sorted(eras.items())))
    print("  genre: " + ", ".join(f"{k} {v}" for k, v in sorted(genres.items())))
    longest = max(eras.values()) if eras else 0
    if longest > 0.5 * len(rows):
        print(f"  WARN one era holds {longest}/{len(rows)} books: era is not stratified")
    return 1 if bad else 0


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--select", action="store_true", help="write the source list")
    ap.add_argument("--target", type=int, default=120)
    ap.add_argument("--fetch", action="store_true", help="download and file the corpus")
    ap.add_argument("--limit", type=int, default=0, help="fetch at most N (smoke test)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--out-source", default=SOURCE, help="where --select writes (default: %(default)s)")
    ap.add_argument("--source", default=SOURCE, help="which list --fetch reads")
    ap.add_argument("--log", default=LOG, help="fetch log (default: %(default)s)")
    ap.add_argument("--skip-log", default=None,
                    help="a fetch log whose gutenberg ids --select must leave out")
    ap.add_argument("--skip-rejects", default=None,
                    help="a reject log whose gutenberg ids --select must leave out")
    ap.add_argument("--slot-prefix", default="C-dist-",
                    help="slot id prefix, e.g. C-dist2- for a second stratum")
    args = ap.parse_args(argv)

    if args.check:
        return check(log=args.log)

    if args.select:
        if not os.path.exists(CATALOG):
            print(f"missing {CATALOG}; download {CATALOG_URL} there first")
            return 2
        with open(CATALOG, encoding="utf-8", errors="replace", newline="") as fh:
            rows = list(csv.DictReader(fh))
        cands = candidates(rows)
        # Excluded before selection, not after: a book already fetched, or already rejected
        # on length, must not consume a slot and leave the stratum one book short.
        for path, label in ((args.skip_log, "already fetched"),
                            (args.skip_rejects, "known-rejected")):
            if path and os.path.exists(path):
                skip = {r["gutenberg_id"] for r in read_source(path)}
                before = len(cands)
                cands = [c for c in cands if c["gutenberg_id"] not in skip]
                print(f"{before - len(cands)} {label} id(s) left out")
        chosen = select(cands, args.target)
        if len(chosen) < args.target:
            print(f"WARN only {len(chosen)} of {args.target} slots could be filled")
        path = write_source(chosen, args.out_source, args.slot_prefix)
        eras = Counter(c["era_proxy"] for c in chosen)
        genres = Counter(c["genre_bucket"] for c in chosen)
        print(f"{len(rows)} catalogue row(s) -> {len(cands)} eligible -> "
              f"{len(chosen)} selected")
        print("  era:   " + ", ".join(f"{k}={v}" for k, v in sorted(eras.items())))
        print("  genre: " + ", ".join(f"{k}={v}" for k, v in sorted(genres.items())))
        print(f"-> {path}")
        return 0

    if args.fetch:
        rows = read_source(args.source)
        if args.limit:
            rows = rows[:args.limit]
        done = {r["slots"] for r in (read_source(args.log) if os.path.exists(args.log) else [])}
        ok = skip = fail = 0
        for row in rows:
            if row["slots"] in done:
                skip += 1
                continue
            try:
                rec, why = fetch_one(row)
            except Exception as e:            # noqa: BLE001 - report, never crash the run
                rec, why = None, f"{type(e).__name__}: {e}"
            if not rec:
                print(f"  {row['slots']:<12} {row['gutenberg_id']:>6}  REJECT  {why}")
                if (row["slots"], why) not in known_rejects():
                    append_reject(row, why)
                fail += 1
                continue
            append_log(rec, args.log)
            ok += 1
            print(f"  {rec['slots']:<12} {rec['gutenberg_id']:>6}  "
                  f"{rec['raw_words']:>7}w {rec['chapters']:>3}ch  {rec['title'][:52]}")
        print(f"\nfetched {ok}, already present {skip}, rejected {fail}")
        return 0 if ok or skip else 1

    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main())
