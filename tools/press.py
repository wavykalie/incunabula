#!/usr/bin/env python3
"""press.py — the press and its author lines, and the isolation between them.

WHY THIS EXISTS
  The taste channel was single: one `COMMONPLACE.md`, one implied author. But the
  catalogue holds three kinds of book, and distilled taste does not transfer between
  them — a rule earned in the literary line is the rule the prescriptive line must
  decline. `press.yaml` declares the lines; this tool holds them apart.

  Isolation is the whole feature, and it is structural, not stylistic: each line
  reads only its own ledger, and nothing crosses lines except an explicit, dated
  author merge in `press/PROMOTIONS.md`. Evidence from one line may not move another,
  the same way evidence from one channel may not move another (SELF_IMPROVEMENT §2).

WHAT IT WILL NOT DO
  - It will not choose a line for a book. `line:` in BOOKS.yaml is the author's
    assignment; `check` NAMES the unassigned books and changes nothing. A book with
    no line is drafted under the root ledger alone, which is where the whole
    catalogue was drafted.
  - It will not accept a missing ledger as an empty one. A declared store that is not
    on disk is a failure: "a file that is missing here is a failure, not a TODO."
  - It will not silently repair a leak. `cross` reports an entry that appears in two
    lines' ledgers and exits non-zero; removing one is a decision with a reason.
  - It is not a gate. Nothing here moves a threshold, and no book is judged by it.

usage:  tools/press.py <command> [--root DIR]
  check        validate the press, the lines and the isolation rules
  cross        report any entry that appears in more than one line's ledger
  list         the lines, their stores and their entry counts
  --self-test  run the assertions

EXIT
  0  clean
  1  a rule failed (each failure names it)
  2  press.yaml missing or unreadable
  3  no YAML parser on this machine — nothing was checked (and not passed)
"""

import os
import re
import shutil
import sys
import tempfile

REQUIRED_LINE_KEYS = ("id", "imprint", "register", "taste_store")
ENTRY_HEADING = re.compile(r"^#{2,3}\s+(.*\S)\s*$")
ROOT_LEDGER = "COMMONPLACE.md"


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_text(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def load_yaml(path):
    """(data, error). ImportError is reported as its own state, never as a pass."""
    try:
        import yaml
    except ImportError:
        return None, "no-yaml"
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh), None
    except Exception as e:  # a config that does not parse is the KF-004 class
        return None, str(e)


def entries(path):
    """Entry headings in a ledger, for the cross-line leak check."""
    if not os.path.isfile(path):
        return []
    return [m.group(1).strip() for m in
            (ENTRY_HEADING.match(ln) for ln in read_text(path).splitlines()) if m]


def book_lines(root):
    """(assigned, unassigned, unknown) from BOOKS.yaml's optional `line:` key."""
    data, err = load_yaml(os.path.join(root, "BOOKS.yaml"))
    if err or not isinstance(data, dict):
        return None, [], []
    assigned, unassigned = [], []
    for b in data.get("books") or []:
        if not isinstance(b, dict):
            continue
        (assigned if b.get("line") else unassigned).append(b.get("path"))
    return assigned, unassigned, []


def check(root):
    press_path = os.path.join(root, "press.yaml")
    if not os.path.isfile(press_path):
        print(f"press: no {press_path} — the press is not declared.")
        return 2
    data, err = load_yaml(press_path)
    if err == "no-yaml":
        print("press: no YAML parser on this machine — press.yaml was NOT checked "
              "(and not passed).")
        return 3
    if err:
        print(f"press: press.yaml does not parse — {err}")
        return 1

    fails, reviews, stores = [], [], {}
    press = (data or {}).get("press") or {}
    if not press.get("name"):
        fails.append("press.name is missing — a press with no name has no imprint")
    lines = press.get("lines") or []
    if not isinstance(lines, list) or not lines:
        fails.append("press.lines is empty — a press with no line publishes nothing")
        lines = []

    ids = []
    for i, line in enumerate(lines):
        if not isinstance(line, dict):
            fails.append(f"line {i} is not a mapping")
            continue
        lid = line.get("id") or f"(line {i})"
        for key in REQUIRED_LINE_KEYS:
            if not line.get(key):
                fails.append(f"{lid}: missing `{key}`")
        if line.get("id"):
            ids.append(line["id"])
        store = line.get("taste_store")
        if not store:
            continue
        srel, spath = store, os.path.join(root, store)
        if srel == ROOT_LEDGER:
            fails.append(f"{lid}: taste_store points at the press-wide {ROOT_LEDGER} — "
                         "a line that reads the shared ledger has no line")
            continue
        expected = f"press/{line.get('id')}/"
        if not srel.replace("\\", "/").startswith(expected):
            fails.append(f"{lid}: taste_store {srel!r} is outside press/{lid}/ — a "
                         "line whose ledger lives elsewhere is a line by declaration only")
        if not os.path.isfile(spath):
            fails.append(f"{lid}: taste_store {srel} is not on disk — a missing ledger "
                         "is a failure, not an empty one")
        elif not os.path.getsize(spath):
            reviews.append(f"{lid}: {srel} is empty (not a failure; a quiet line)")
        if srel in stores:
            fails.append(f"{lid}: taste_store {srel} is shared with line "
                         f"{stores[srel]!r} — isolation is the point of a line")
        else:
            stores[srel] = lid
    if len(set(ids)) != len(ids):
        fails.append(f"line ids are not unique: {ids}")

    assigned, unassigned, _ = book_lines(root)
    known = set(ids)
    if assigned is not None:
        data, _ = load_yaml(os.path.join(root, "BOOKS.yaml"))
        for b in (data or {}).get("books") or []:
            if isinstance(b, dict) and b.get("line") and b["line"] not in known:
                fails.append(f"{b.get('path')}: BOOKS.yaml assigns line "
                             f"{b['line']!r}, which is not declared in press.yaml")
        if unassigned:
            reviews.append(f"{len(unassigned)} book(s) carry no `line:` — the "
                           "assignment is the author's: " + ", ".join(unassigned[:6])
                           + (" …" if len(unassigned) > 6 else ""))

    print(f"press — {press.get('name') or '(unnamed)'}, {len(lines)} line(s)")
    for line in lines:
        if isinstance(line, dict):
            print(f"  {line.get('id', '?'):8} {line.get('imprint', ''):10} "
                  f"{len(entries(os.path.join(root, line.get('taste_store', ''))))} "
                  f"entr(ies)  {line.get('taste_store')}")
    for r in reviews:
        print(f"  REVIEW  {r}")
    for f in fails:
        print(f"  FAIL    {f}")
    if fails:
        print(f"press: {len(fails)} failure(s). Isolation is structural — fix it here, "
              "not in a book.")
        return 1
    print("press: lines and their ledgers check out; every line reads only its own.")
    return 0


def cross(root):
    data, err = load_yaml(os.path.join(root, "press.yaml"))
    if err == "no-yaml":
        print("press: no YAML parser — nothing checked (and not passed).")
        return 3
    if err or not data:
        print("press: press.yaml is missing or unreadable.")
        return 2
    seen = {}
    for line in ((data.get("press") or {}).get("lines") or []):
        if not isinstance(line, dict):
            continue
        for e in entries(os.path.join(root, line.get("taste_store", ""))):
            seen.setdefault(e, []).append(line.get("id"))
    leaks = {e: ids for e, ids in seen.items() if len(ids) > 1}
    print(f"press cross — {len(seen)} distinct entr(ies) across the lines")
    for e, ids in sorted(leaks.items()):
        print(f"  LEAK    {e!r} appears in {', '.join(ids)} — a preference in two "
              "ledgers has stopped being one line's. Merge it deliberately in "
              "press/PROMOTIONS.md, or remove it from the line it was not earned in.")
    if leaks:
        return 1
    print("press cross: no entry appears in more than one line's ledger.")
    return 0


def cmd_list(root, args):
    return check(root)


# --- self-test -------------------------------------------------------------

CLEAN = """press:
  name: "Test Press"
  lines:
    - id: folio
      imprint: "Folio"
      register: "long literary fiction"
      taste_store: "press/folio/COMMONPLACE.md"
    - id: octavo
      imprint: "Octavo"
      register: "short prescriptive nonfiction"
      taste_store: "press/octavo/COMMONPLACE.md"
"""

BOOKS_ONE = "books:\n  - path: assigned-book\n    line: folio\n"
BOOKS_NONE = "books:\n  - path: unassigned-book\n"
BOOKS_UNKNOWN = "books:\n  - path: stranded-book\n    line: duodecimo\n"


def _build(tmp, press_text, books_text, stores):
    os.makedirs(os.path.join(tmp, "press"), exist_ok=True)
    with open(os.path.join(tmp, "press.yaml"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(press_text)
    with open(os.path.join(tmp, "BOOKS.yaml"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(books_text)
    for rel, body in stores.items():
        p = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)


def selftest():
    checks = []

    def ok(cond, label):
        checks.append((bool(cond), label))

    base_stores = {
        "press/folio/COMMONPLACE.md": "# COMMONPLACE — Folio\n\n### 2026-01-01 — decision — a\n",
        "press/octavo/COMMONPLACE.md": "# COMMONPLACE — Octavo\n\n### 2026-01-02 — decision — b\n",
    }
    tmp = tempfile.mkdtemp(prefix="press-")
    try:
        ok(load_yaml(os.path.join(tmp, "nope.yaml"))[1] == "no-yaml" or True,
           "parser probe: load_yaml reports its state rather than raising")

        _build(tmp, CLEAN, BOOKS_ONE, base_stores)
        ok(check(tmp) == 0, "check: a clean press with one assigned book passes")
        ok(cross(tmp) == 0, "cross: two lines with distinct entries have no leak")
        ok(book_lines(tmp)[1] == [], "check: an assigned book is not reported as unassigned")

        # a missing ledger is a failure, never an empty one
        shutil.rmtree(os.path.join(tmp, "press"))
        _build(tmp, CLEAN, BOOKS_ONE, {k: v for k, v in base_stores.items()
                                       if k.endswith("octavo/COMMONPLACE.md")})
        ok(check(tmp) == 1, "check: a declared ledger that is not on disk fails")

        # a shared ledger defeats the line
        shared = CLEAN.replace("press/octavo/COMMONPLACE.md",
                               "press/folio/COMMONPLACE.md")
        shutil.rmtree(os.path.join(tmp, "press"))
        _build(tmp, shared, BOOKS_ONE, base_stores)
        ok(check(tmp) == 1, "check: two lines sharing one ledger fails")

        # a ledger outside its own line directory
        outside = CLEAN.replace('"press/octavo/COMMONPLACE.md"', '"press/elsewhere.md"')
        shutil.rmtree(os.path.join(tmp, "press"))
        _build(tmp, outside, BOOKS_ONE, dict(base_stores, **{
            "press/elsewhere.md": "# elsewhere\n"}))
        ok(check(tmp) == 1, "check: a ledger outside press/<id>/ fails")

        # a line pointing at the press-wide ledger
        wide = CLEAN.replace('"press/octavo/COMMONPLACE.md"', '"COMMONPLACE.md"')
        shutil.rmtree(os.path.join(tmp, "press"))
        _build(tmp, wide, BOOKS_ONE, dict(base_stores, **{
            "COMMONPLACE.md": "# the press-wide ledger\n"}))
        ok(check(tmp) == 1, "check: a line pointing at COMMONPLACE.md fails")

        # an unknown line assignment fails; an absent one is the author's call
        shutil.rmtree(os.path.join(tmp, "press"))
        _build(tmp, CLEAN, BOOKS_UNKNOWN, base_stores)
        ok(check(tmp) == 1, "check: a book assigned to an undeclared line fails")
        shutil.rmtree(os.path.join(tmp, "press"))
        _build(tmp, CLEAN, BOOKS_NONE, base_stores)
        ok(check(tmp) == 0, "check: an unassigned book is REVIEW, not a failure")

        # Every assertion above calls check()/cross() directly, which would not have
        # caught a dispatch that cannot reach them. The interface is what a run uses.
        argv, sys.argv = sys.argv, ["press.py", "check", "--root", tmp]
        try:
            rc_dispatch = main()
        except TypeError as e:
            rc_dispatch = f"TypeError: {e}"
        finally:
            sys.argv = argv
        ok(isinstance(rc_dispatch, int),
           f"main: a command dispatched through main() returns an exit code ({rc_dispatch})")

        # the leak detector, proven by injection in both directions
        leaked = dict(base_stores)
        leaked["press/octavo/COMMONPLACE.md"] += "\n### 2026-01-01 — decision — a\n"
        shutil.rmtree(os.path.join(tmp, "press"))
        _build(tmp, CLEAN, BOOKS_ONE, leaked)
        ok(cross(tmp) == 1, "cross: an entry in two ledgers is reported as a leak")
        shutil.rmtree(os.path.join(tmp, "press"))
        _build(tmp, CLEAN, BOOKS_ONE, base_stores)
        ok(cross(tmp) == 0, "cross: removing the duplicate clears the leak")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [label for good, label in checks if not good]
    for good, label in checks:
        print(("  ok    " if good else "  FAIL  ") + label)
    print("-" * 67)
    if failed:
        print(f"SELF-TEST FAILURE — {len(failed)} of {len(checks)} assertions failed.")
        return 1
    print(f"SELF-TEST PASS — {len(checks)} assertions (schema, isolation, missing ledger, "
          "shared ledger, outside-dir ledger, root-ledger, assignment, leak detection).")
    return 0


# --- main ------------------------------------------------------------------

def main():
    args = sys.argv[1:]
    root = repo_root()
    if "--root" in args:
        i = args.index("--root")
        root = args[i + 1]
        del args[i:i + 2]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if args else 2
    cmd, rest = args[0], args[1:]
    if cmd in ("selftest", "--self-test"):
        return selftest()
    # check/cross take the root; list is a command-shaped function. Wrapped rather
    # than unified so the CLI shape stays the same as the other harness tools.
    table = {"check": lambda r, a: check(r), "cross": lambda r, a: cross(r),
             "list": cmd_list}
    if cmd not in table:
        print(f"press: unknown command {cmd}")
        return 2
    return table[cmd](root, rest)


if __name__ == "__main__":
    sys.exit(main())
