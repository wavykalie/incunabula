"""Verify the pilot book's cast declarations parse the way ENTITY_STATE.yaml claims.

The whole point of the declared `canonical_name:` convention is that the frozen
gate reads it correctly. This checks that against the real parser, not an
assumption, before a single chapter is drafted against it.
"""
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_names", Path("C:/Users/screa/incunabula/tools/prose/check-names.py")
)
cn = importlib.util.module_from_spec(_spec)
sys.modules["check_names"] = cn
_spec.loader.exec_module(cn)

BOOK = Path("C:/Users/screa/incunabula/test-books/muzzle-and-marrow")
LEDGER = BOOK / "ENTITY_STATE.yaml"

EXPECTED_FIRST = {"Mittens", "Rocky", "Hester", "Patches", "Tuppence", "Void"}
EXPECTED_SUR = {"Brisk", "Cavaltone", "Pye", "Quill", "Small", "Nighthollow"}


def main():
    full, firsts, surs = cn.harvest(str(LEDGER))

    print("parsed full names :")
    for n in sorted(full):
        print("   ", n)
    print()
    print("parsed first names:", sorted(firsts))
    print("parsed surnames   :", sorted(surs))
    print()

    problems = []

    # 1. No title may land in a name slot.
    titles = {"Duke", "Dame", "Sergeant", "Baroness", "Captain", "Madame", "Sir"}
    for t in titles & (firsts | surs):
        problems.append("title %r parsed as a name" % t)

    # 2. Every character must be visible to the gate.
    missing = EXPECTED_FIRST - firsts
    if missing:
        problems.append("characters invisible to the gate: %s" % sorted(missing))

    # 3. No entry may be a connector ("the", "of", "von").
    connectors = {"the", "of", "von", "de", "van"}
    for c in connectors & (firsts | surs):
        problems.append("connector %r parsed as a name" % c)

    # 4. First names must be unique, or the gate will flag a first-name collision.
    if len(firsts) != 6:
        problems.append("expected 6 first names, got %d" % len(firsts))
    if len(surs) != 6:
        problems.append("expected 6 surnames, got %d" % len(surs))

    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  -", p)
        return 1

    print("PASS - 6 characters visible, no titles, no connectors, no collisions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
