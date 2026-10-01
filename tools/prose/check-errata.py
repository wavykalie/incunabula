#!/usr/bin/env python3
"""check-errata.py - the guard on the system's own guidance.

WHY THIS EXISTS
  PRINTERS_COPY.md and ERRATA.md make this system self-improving: rules that survive a
  corpus are recorded, rules that do not are recorded as rejected, and a book that trips
  something three times escalates it. That is a good design with one failure mode, and the
  failure mode is quiet.

  A layer that accumulates entries without checking them is not learning. It is collecting
  confident opinions, and the confidence is indistinguishable from the rigour at reading
  time. VERMILLION's warning is the general case: a framework built without a theory of what
  it is measuring will, over time, optimise against the wrong target. Applied here, a ledger
  without a validator optimises against *whatever was easiest to write down*.

  So the protocol is checked, the same way every other rule in this directory is checked.
  This is the one tool here that reads no prose and gates no manuscript.

WHAT IT CHECKS

  ERRATA.md, every entry
    - the heading carries an ISO date
    - all seven fields are present
    - `motive` is exactly `aesthetic` or `privacy`      (never blank, never invented)
    - `state` is exactly observed | proposed | adopted
    - anything past `observed` names an `n`             (one book is an observation)
    - a `privacy` motive states what the rule is a substitute for

  PRINTERS_COPY.md
    - all four registries are present
    - the Confirmed registry contains no `privacy` row  (a privacy rule may not stand in
      for quality; §1's test is that they do not, and this enforces it)
    - the §1 test and the §7 protocol are still in the file
    - the tier names in §7 match the modes this tool implements
    - **the Rejected registry has not shrunk**           (see below)

  Modes
    `errata.mode` in PROJECT_STATE.yaml selects promotion behaviour. This tool **never
    mutates anything**. It reports what the current mode would permit, so the difference
    between `hand` and `auto` is visible at the moment it matters rather than in a diff
    nobody read.

THE SHRINKING-REGISTRY CHECK, AND WHY IT IS THE ODD ONE OUT

  PRINTERS_COPY.md §7 names the tell that the guidance has ossified: *a `Rejected` registry
  that stops growing*. That is a claim about a system over time, and a claim about time is
  the one thing a tool can actually hold you to. So this file records the count of rejected
  entries and **fails if the number has gone down**.

  A registry cannot lose an entry without someone deleting one, and deleting a rejected
  measure is how a project quietly reinvents a rule it already paid to disprove. The floor
  moves only by hand, in the same place, for the same reason a threshold does.

WHAT IT DOES NOT DO
  It cannot tell a good motive from a bad one, and it does not try. `motive: aesthetic` on
  an entry that is really a privacy measure passes this tool. The field exists to force the
  question to be written down where somebody has to answer it; the answer is still a human's.

  It cannot check that the corpus named in an `evidence` line exists, because that line is
  prose. It checks that the files the entry *claims to have changed* exist and contain the
  claim, which catches the common case of a fix that was reverted.

  usage:  tools/check-errata.py [PROJECT_DIR ...]
          (no argument = the incunabula root, found from this file)
          exit 0 = protocol intact   exit 1 = protocol violated
"""

import os
import re
import sys

# Rejected-registry floor. Hand-maintained, in one place, on purpose: it moves when a
# measure is genuinely retired, and moving it is a decision someone has to make on the
# record. At the time of writing: 21 rejected measures - set to 16 on the first attempt at
# that update and caught by the check itself, which is the intended way to find out.
#
# Raise it whenever a row is added. A floor left below the live count is slack the
# guard cannot see through, and the next deletion lands inside it.
REJECTED_FLOOR = 30

MODES = ("hand", "bulk", "auto")

ERRATA_FIELDS = ("row", "observed", "n", "evidence", "motive", "state", "proposes")
VALID_MOTIVES = ("aesthetic", "privacy")
VALID_STATES = ("observed", "proposed", "adopted")

# The files an adopted entry is allowed to claim it changed. All relative to the
# incunabula root.
KNOWN_TARGETS = (
    "PRINTERS_COPY.md", "ERRATA.md",
    "tools/prose/calibration/CALIBRATION.md", "tools/prose/README.md",
    "skills/composing/SKILL.md", "skills/setting/SKILL.md", "skills/forme/SKILL.md",
    "skills/quoin/SKILL.md", "skills/catchword/SKILL.md", "skills/corrector/SKILL.md",
    "skills/deslopify/SKILL.md", "skills/deslopify/references/style_guide.md",
    "tools/prose/check-uniformity.py", "tools/prose/check-arc.py",
    "tools/prose/check-surplus.py", "tools/prose/check-recoverable.py",
    "tools/prose/calibration/measure-pd-corpus.py",
    "tools/prose/calibration/proto-recoverable.py",
    "skills/incunabula-codex/references/pipeline/project-state.yaml",
)

ENTRY = re.compile(r"^### (\d{4}-\d{2}-\d{2})\s+—\s*(.+)$", re.M)
FIELD = re.compile(r"^-\s+\*\*(\w+):\*\*\s+(.*)$", re.M)


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def split_entries(text):
    """[(date, title, body, fields_dict)] for every entry, in file order."""
    marks = list(ENTRY.finditer(text))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[m.end():end]
        fields = {k.lower(): v.strip() for k, v in FIELD.findall(body)}
        out.append((m.group(1), m.group(2).strip(), body, fields))
    return out


def check_errata(root, failures):
    path = os.path.join(root, "ERRATA.md")
    if not os.path.isfile(path):
        failures.append("ERRATA.md is missing - the layer has no ledger")
        return 0
    text = read(path)
    entries = split_entries(text)
    if not entries:
        failures.append("ERRATA.md has no entries in the required format")
        return 0

    for date, title, body, fields in entries:
        tag = f"ERRATA {date}"
        missing = [f for f in ERRATA_FIELDS if f not in fields]
        if missing:
            failures.append(f"{tag}: missing field(s) {', '.join(missing)}")

        # The motive field may carry a rationale after the token - "aesthetic - because
        # a false accusation here costs an author an injected one-line paragraph" is a
        # better entry than a bare "aesthetic". Only the first token is the field.
        motive = fields.get("motive", "").strip().lower()
        motive = motive.split()[0].strip(".,:;-") if motive else ""
        if motive and motive not in VALID_MOTIVES:
            failures.append(f"{tag}: motive is '{motive}', must be one of {VALID_MOTIVES}")

        state = fields.get("state", "").strip().lower().split()[0].strip(".,:;-") \
            if fields.get("state") else ""
        if state and state not in VALID_STATES:
            failures.append(f"{tag}: state is '{state}', must be one of {VALID_STATES}")

        if state in ("proposed", "adopted") and "n" not in fields:
            failures.append(f"{tag}: state '{state}' needs an n - one book is an observation")

        if motive == "privacy" and "substitute" not in body.lower():
            failures.append(f"{tag}: a privacy motive must say what the rule stands in for "
                            f"(PRINTERS_COPY.md §1)")

    # An adopted entry that names a file must name one that exists. Catches the common
    # case of a fix that was reverted while the entry stayed.
    #
    # Only when this is a real Incunabula install. Pointed at a project directory, or at a
    # pair of copied files, the check is meaningless and drowns the entries that matter -
    # which is exactly what happened the first time this ran on a copy.
    full_install = os.path.isdir(os.path.join(root, "tools", "prose"))
    if not full_install:
        return len(entries)

    for date, title, body, fields in entries:
        if fields.get("state", "").strip().lower().split()[0].strip(".,:;-") != "adopted":
            continue
        for target in KNOWN_TARGETS:
            stem = os.path.splitext(os.path.basename(target))[0]
            if stem.lower() in body.lower():
                if not os.path.isfile(os.path.join(root, target)):
                    failures.append(f"ERRATA {date}: adopted entry cites {target}, "
                                    f"which does not exist")
    return len(entries)


def rejected_count(text):
    """Rows in the Rejected registry table. Counts table lines, not prose."""
    m = re.search(r"^##\s*4\.\s*Rejected.*?^(?=^##\s)", text, re.M | re.S)
    if not m:
        return None
    block = m.group(0)
    return sum(1 for line in block.splitlines()
               if line.strip().startswith("|") and "---" not in line
               and not re.match(r"^\|\s*measure\s*\|", line.strip()))


def check_printers_copy(root, failures):
    path = os.path.join(root, "PRINTERS_COPY.md")
    if not os.path.isfile(path):
        failures.append("PRINTERS_COPY.md is missing - the layer has no standing brief")
        return
    text = read(path)

    for registry in ("Confirmed", "Rejected", "Load-bearing but unmeasured", "Open"):
        if not re.search(rf"\*\*{re.escape(registry)}\*\*", text) and \
           not re.search(rf"^#+.*\b{re.escape(registry)}\b", text, re.M):
            failures.append(f"PRINTERS_COPY.md: registry '{registry}' is missing")

    for required in ("If this rule only lowers a score", "How this file changes",
                     "What no mode may do"):
        if required not in text:
            failures.append(f"PRINTERS_COPY.md: the section containing "
                            f"'{required}' has been removed")

    for mode in MODES:
        if f"`{mode}`" not in text:
            failures.append(f"PRINTERS_COPY.md: tier '{mode}' is not described in §7")

    confirmed = re.search(r"^##\s*3\.\s*Confirmed.*?^(?=^##\s)", text, re.M | re.S)
    if confirmed and "privacy" in confirmed.group(0).lower():
        failures.append("PRINTERS_COPY.md: a `privacy` rule has appeared in the Confirmed "
                        "registry - §1's test exists to prevent exactly this")

    n = rejected_count(text)
    if n is None:
        failures.append("PRINTERS_COPY.md: the Rejected registry table could not be found")
    elif n < REJECTED_FLOOR:
        failures.append(
            f"PRINTERS_COPY.md: the Rejected registry has shrunk - {n} entries, floor is "
            f"{REJECTED_FLOOR}. §7 calls a registry that stops growing the tell that this "
            f"system has ossified, and a registry that SHRINKS means a measure was quietly "
            f"re-invented after being disproven. If the deletion was deliberate, lower "
            f"REJECTED_FLOOR in check-errata.py and say why in ERRATA.md.")
    elif n > REJECTED_FLOOR:
        failures.append(
            f"PRINTERS_COPY.md: the Rejected registry has grown to {n} but REJECTED_FLOOR is "
            f"{REJECTED_FLOOR}. The floor is the only memory this system has that a measure "
            f"was disproven, so slack above it is a deletion nobody would notice. Raise the "
            f"floor to {n} in check-errata.py.")


def report_mode(root):
    print()
    print("  Promotion mode, and what it permits:")
    state = os.path.join(root, "PROJECT_STATE.yaml")
    mode = None
    if os.path.isfile(state):
        m = re.search(r"^\s*mode\s*:\s*\"?([\w-]+)", read(state)[:4000], re.M)
        if m:
            mode = m.group(1).strip()
    if mode is None:
        print("    hand (default, no PROJECT_STATE.yaml override)")
        print("      observations append; only a person edits PRINTERS_COPY.md")
    else:
        print(f"    {mode}")
        if mode == "hand":
            print("      observations append; only a person edits PRINTERS_COPY.md")
        elif mode == "bulk":
            print("      observations auto-promote to the PROJECT-LOCAL copy at 3 agreeing")
            print("      books. Never the shipped pipeline, never a threshold.")
        elif mode == "auto":
            print("      thresholds may re-derive from accumulated data, with a printed")
            print("      changelog and a dated re-check horizon on every rule. PRINTERS_COPY")
            print("      §7 argues against this mode. It is available, not endorsed.")
    if mode is not None and mode not in MODES:
        print(f"    WARNING: mode '{mode}' is not one of {MODES}. Unknown modes are treated")
        print("    as 'hand' by every reader, which is the safe default but is a typo.")


def main():
    args = sys.argv[1:]
    root = repo_root()
    if args:
        roots = [os.path.abspath(a) for a in args]
    else:
        roots = [root]

    failures = 0
    entries = 0
    for r in roots:
        print("=" * 67)
        print(f"## check-errata   {r}")
        print("=" * 67)
        local = []
        entries += check_errata(r, local)
        check_printers_copy(r, local)
        failures += len(local)
        if local:
            for f in local:
                # Normalised for a cp1252 console, which mangles the em dashes these
                # messages quote back from the files they are complaining about.
                print(f"   FAIL  {f}".encode("ascii", "replace").decode("ascii"))
        else:
            print("   ok    ERRATA.md entries carry a date, all seven fields, a valid")
            print("         motive and a valid state")
            print("   ok    PRINTERS_COPY.md carries all four registries, the section 1 test,")
            print("         the section 7 protocol and all three tiers")
            print(f"   ok    Rejected registry at its floor of {REJECTED_FLOOR}")
        report_mode(r)
        print()

    print("=" * 67)
    if failures == 0:
        print(f"ERRATA PROTOCOL OK - {entries} entries, nothing promoted without evidence.")
        return 0
    print(f"ERRATA PROTOCOL FAILURE - {failures} violation(s).")
    print("This gate reads no prose and judges no manuscript. It only asks that every claim")
    print("about how to write carries a date, a number, a motive, and a state - so that a")
    print("rule cannot enter the system because it was written down confidently.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
