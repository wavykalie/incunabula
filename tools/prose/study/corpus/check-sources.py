#!/usr/bin/env python3
"""check-sources.py - the provenance gate for any work added to Arm C beyond Gutenberg.

WHY THIS EXISTS
  `fetch-dist.py` rule 1 is "public domain - Project Gutenberg only". That is a licensing
  rule, and it leaves the human baseline entirely pre-1930. Broadening it to modern prose is
  the point of C-dist v2 - but the registry has to say *how* each work was obtained, because
  that is the part that can be checked.

  The study is non-consumptive: it counts features and never republishes a text. A text the
  researcher lawfully holds (bought, gifted, or downloaded through the platform's own export)
  may be analysed on that basis and recorded as `local-copy`, which forces
  `redistributable=no`. Pirated and DRM-stripped copies are refused, because there the wrong
  is in the acquisition, not in the analysis.

usage:
    python corpus/check-sources.py [corpus/sources-v2.tsv]

exit
    0  every row has a permitted provenance, evidence and a redistribution flag
    1  at least one row is unusable
    2  missing registry, missing columns, or zero rows - NOT RUN, never a pass
"""

import argparse
import csv
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "sources-v2.tsv")

COLUMNS = ("slots", "source", "source_id", "author", "title", "license",
           "license_evidence", "url", "stratum", "genre_bucket", "words",
           "redistributable", "notes")
REQUIRED = COLUMNS[:-1]

ALLOWED = {
    "public-domain": "copyright expired, or a public-domain edition",
    "cc0": "CC0 dedication",
    "cc-by": "Creative Commons Attribution",
    "cc-by-sa": "Creative Commons Attribution-ShareAlike",
    "author-permission": "the author granted corpus use in writing",
    "publisher-permission": "the rights holder granted corpus use in writing",
    "local-copy": "lawfully acquired copy, analysed locally and never redistributed",
}
REFUSED = {
    "pirated": "an unlawfully obtained copy is not cleared by being useful",
    "drm-stripped": "circumventing DRM is a separate wrong from copyright (DMCA 1201)",
    "all-rights-reserved": "all rights reserved is not a licence to copy",
    "fair-use": "fair use is a defence, not a permission - record provenance, not a defence",
    "unknown": "an unknown provenance cannot be cleared",
}
STRATA = {"public-domain", "licensed-web", "permissioned", "local-modern"}
REDIST = {"yes", "no"}
SLOT = re.compile(r"^C-(dist|mod)-\d{3}$")
URL = re.compile(r"^https?://", re.I)
DATE = re.compile(r"\b(19|20)\d{2}-\d{2}-\d{2}\b")
MIN_WORDS = 20000


def read(path):
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        rows = list(reader)
        return rows, (reader.fieldnames or [])


def evidence_exists(value, base):
    if URL.match(value):
        return True
    return os.path.exists(value if os.path.isabs(value) else os.path.join(base, value))


def check(path):
    if not os.path.exists(path):
        print(f"no registry at {path}: nothing is cleared, so nothing may be fetched.")
        return 2
    rows, fields = read(path)
    missing = [c for c in REQUIRED if c not in fields]
    if missing:
        print(f"{path}: missing column(s): {', '.join(missing)}")
        print(f"  required: {', '.join(REQUIRED)}")
        return 2
    if not rows:
        print(f"{path}: zero rows. An empty registry is NOT RUN, never a pass - "
              f"a corpus of zero books is a failure.")
        return 2

    base = os.path.dirname(os.path.abspath(path))
    problems = []
    seen_slots, seen_authors = set(), {}
    for i, r in enumerate(rows, 2):
        slot = (r.get("slots") or "").strip()
        where = f"line {i} ({slot or 'no slot'})"

        if not SLOT.match(slot):
            problems.append(f"{where}: slot must look like C-dist-001 or C-mod-001")
        elif slot in seen_slots:
            problems.append(f"{where}: duplicate slot")
        seen_slots.add(slot)

        for col in ("source", "source_id", "author", "title"):
            if not (r.get(col) or "").strip():
                problems.append(f"{where}: {col} is empty")

        lic = (r.get("license") or "").strip().lower()
        if not lic:
            problems.append(f"{where}: no licence recorded")
        elif lic in REFUSED:
            problems.append(f"{where}: provenance {lic!r} is refused - {REFUSED[lic]}")
        elif lic not in ALLOWED:
            problems.append(f"{where}: provenance {lic!r} is not one of "
                            f"{', '.join(sorted(ALLOWED))}")

        ev = (r.get("license_evidence") or "").strip()
        if not ev:
            problems.append(f"{where}: no evidence (a licence or acquisition-record URL, "
                            f"or a path to the file on disk)")
        elif not evidence_exists(ev, base):
            problems.append(f"{where}: evidence {ev!r} is neither an http(s) URL "
                            f"nor a file that exists")

        url = (r.get("url") or "").strip()
        if not URL.match(url):
            problems.append(f"{where}: url must be http(s)")

        stratum = (r.get("stratum") or "").strip()
        if stratum not in STRATA:
            problems.append(f"{where}: stratum must be one of {', '.join(sorted(STRATA))}")

        redist = (r.get("redistributable") or "").strip().lower()
        if redist not in REDIST:
            problems.append(f"{where}: redistributable must be 'yes' or 'no'")
        elif redist == "yes" and lic in ("local-copy", "all-rights-reserved"):
            problems.append(f"{where}: {lic} cannot be redistributed - this study is "
                            f"non-consumptive, so mark it no")
        elif redist == "yes" and stratum == "local-modern":
            problems.append(f"{where}: a local-modern row is redistributable=no by "
                            f"definition")

        notes = (r.get("notes") or "").strip()
        if lic == "local-copy":
            if not DATE.search(notes):
                problems.append(f"{where}: local-copy needs the acquisition date "
                                f"(YYYY-MM-DD) in notes")
            if stratum != "local-modern":
                problems.append(f"{where}: a local-copy work belongs in stratum "
                                f"local-modern")

        words = (r.get("words") or "").strip()
        if words:
            try:
                if int(words) < MIN_WORDS:
                    problems.append(f"{where}: {words} words is below the {MIN_WORDS}-word "
                                    f"floor")
            except ValueError:
                problems.append(f"{where}: words {words!r} is not an integer")

        author = re.sub(r"[^a-z]+", " ", (r.get("author") or "").lower()).strip()
        if author:
            if author in seen_authors:
                problems.append(f"{where}: second work by the same author "
                                f"(also {seen_authors[author]}); one work per author")
            else:
                seen_authors[author] = slot

    print(f"check-sources: {len(rows)} row(s) in {path}")
    print("  provenance: " + ", ".join(
        f"{k}={v}" for k, v in
        sorted(Counter((r.get("license") or "none").strip().lower() for r in rows).items())))
    print("  stratum:    " + ", ".join(
        f"{k}={v}" for k, v in
        sorted(Counter((r.get("stratum") or "none").strip() for r in rows).items())))
    print("  source:     " + ", ".join(
        f"{k}={v}" for k, v in
        sorted(Counter((r.get("source") or "none").strip() for r in rows).items())))
    print("  redistributable: " + ", ".join(
        f"{k}={v}" for k, v in
        sorted(Counter((r.get("redistributable") or "none").strip().lower()
                       for r in rows).items())))
    if problems:
        for p in problems:
            print(f"  FAIL  {p}")
        print(f"\ncheck-sources: FAIL - {len(problems)} unusable row(s). Nothing here may "
              f"be loaded until they are fixed or removed.")
        return 1
    print("OK - every row carries a permitted provenance, evidence, a stratum and a "
          "redistribution flag consistent with it.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("registry", nargs="?", default=DEFAULT)
    args = ap.parse_args(argv)
    return check(args.registry)


if __name__ == "__main__":
    sys.exit(main())
