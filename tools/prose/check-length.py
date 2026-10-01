#!/usr/bin/env python3
"""Does the book deliver the length it declared?

WHY THIS EXISTS, AND WHY IT IS NOT A CORPUS ROW
-----------------------------------------------
`U1` (chapter-length variance) is a CV, so it is scale-invariant: truncating every
chapter proportionally leaves it unchanged, and cutting the two longest chapters
by 40% *raises* it. Measured on `sons-of-heaven-v2`:

    current                          17,872 words, CV 30.3%
    cut two longest chapters by 40%   15,980 words (-1,892), CV 22.5%  -> still passes

So the cheapest way to pass the one chapter-shape row the system enforces is to
delete prose. Five skill instructions push variation ("vary chapter length",
"break the book's uniform shape") and the only word-count figure anywhere in the
pipeline is `target_range_words: [0, 0]`. A distributional rule with no floor
beneath it constrains a book's shape without constraining its size.

This row is the other half of that pair, and it is deliberately NOT another corpus
measurement. It makes no claim about human prose at all. It compares a book to the
length *that book declared for itself* in PROJECT_STATE.yaml. That distinction is
the whole reason it is safe to enforce:

  - `U1` needed a published corpus and still had to be made advisory for
    non-fiction, because six published volumes disagree about the floor.
  - This row needs no corpus. There is no population it can false-fail, because
    it is not measuring a population. A book either delivered its declared
    length or it did not.

Which means it can be enforced everywhere, including on the books whose convention
declaration switched `U1` off. That is the point: `U1` was made advisory precisely
because it could not see non-fiction, and that blindness is where a book half its
intended length went unnoticed.

EXIT CODES
    0  within the declared range
    1  outside the declared range - a real failure
    2  no target declared, or nothing checkable - NOT RUN, never means pass
    3  no PROJECT_STATE.yaml at the book root - UNGOVERNED, not a pass, not a fail
    4  the book declares status: in_progress - recorded, never a delivery failure

A gate that reads nothing proves nothing, and this directory has three separate
bugs that all pointed the same way: the gate reporting itself more capable than it
was.
"""

import os
import re
import statistics as st
import sys

MIN_CHAPTERS = 4
CHAPTER = re.compile(r"chapter[-_ ]?\d+", re.I)


def resolve(arg):
    """Accept a book dir, a manuscript dir, or a chapter dir."""
    for candidate in (arg,
                      os.path.join(arg, "manuscript"),
                      os.path.join(arg, "manuscript", "chapters")):
        if os.path.isdir(candidate):
            if any(CHAPTER.search(n) for n in os.listdir(candidate)):
                return candidate
    return None


def load(directory):
    out = []
    for name in sorted(os.listdir(directory)):
        if CHAPTER.search(name):
            path = os.path.join(directory, name)
            with open(path, encoding="utf-8", errors="ignore") as fh:
                out.append((name, len(fh.read().split())))
    return out


def state_file(book_root):
    """Does this book have a PROJECT_STATE.yaml at all?

    Separate from declared_target() because the two absences mean opposite things and
    used to print the same sentence. A book that HAS the file and declares no target has
    made a decision - DRAFTING_FRAMEWORK.md now says numbers survive only in the
    book-level contract, so that is a legitimate state and the row is simply not
    applicable. A book with NO FILE may have had its state archived, renamed or never
    created, and in that case the row is not "not applicable", it is UNGOVERNED: nothing
    can say what length the book owes, and every downstream report that treats the skip
    as "no target declared" is reading an absence as a decision.

    That is not hypothetical. Both validation-series Merope books have their
    PROJECT_STATE.yaml in _archive/validation-series-meta/, so this gate exited 2 for a
    reason that had nothing to do with the drafting framework, and that exit 2 was read
    in-session as evidence that the framework had removed their length targets. It had
    not. The targets were still there, carrying `average_words_per_chapter_planned:
    2450` and `chapter_count_planned: 7` against books that have eleven chapters.

    The rule this produces is the standing one: *an absence is not a decision, and a
    gate that cannot tell them apart must not be the one reporting.*
    """
    return os.path.join(book_root, "PROJECT_STATE.yaml")


def declared_target(book_root):
    """Read the book's own word-count target. Returns (floor, ceiling, source) or None.

    Reads the same keys the intake schema already writes, so nothing new has to be
    added to a book for this row to work. `target_range_words: [0, 0]` is the
    schema default and means *not declared* - it is treated as absent rather than
    as a book that wants to be zero words long.
    """
    path = state_file(book_root)
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8", errors="ignore") as fh:
        head = fh.read(8000)

    def num(*keys):
        for key in keys:
            m = re.search(rf"^\s*{key}\s*:\s*[\"']?([0-9][0-9,_]*)", head, re.I | re.M)
            if m:
                v = int(m.group(1).replace(",", "").replace("_", ""))
                if v:            # 0 is the "not declared" default everywhere
                    return v
        return None

    # Three naming schemes are in live use and this row has to read all of them, because
    # a book created from the pipeline's own template used `word_floor`/`word_ceiling`
    # while real books use `target_floor_words`/`target_ceiling_words`, and the intake
    # schema uses `target_range_words`. Reading only one of them meant a book built from
    # the template exited 2 while carrying a comment that promised a length gate.
    floor = num("target_floor_words", "word_floor", "min_words")
    ceiling = num("target_ceiling_words", "word_ceiling", "max_words")

    if not (floor or ceiling):
        # Fall back to the list form, `target_range_words: [28000, 32000]`.
        m = re.search(r"^\s*target_range_words\s*:\s*\[\s*([0-9][0-9,_]*)\s*,\s*([0-9][0-9,_]*)",
                      head, re.I | re.M)
        if m:
            a, b = m.group(1), m.group(2)
            floor, ceiling = int(a.replace(",", "")), int(b.replace(",", ""))
            if floor == 0 and ceiling == 0:
                return None  # the schema default. Not a declaration.

    if not floor and not ceiling:
        # A single `word_count_target` is a FIGURE, not a range. Failing against it
        # would require inventing a tolerance, and this project does not set a
        # threshold from an unmeasured number - so the row reports and warns, and
        # says plainly that it is not enforced. A book gets an enforced length row
        # by declaring `target_floor_words` and `target_ceiling_words`, which the
        # intake schema already carries.
        single = num("word_count_target", "word_target")
        if single:
            return single, single, os.path.basename(path) + " (single figure - advisory)"
        return None
    if not floor:
        floor = int(ceiling * 0.9)
    if not ceiling:
        ceiling = int(floor * 1.15)
    return floor, ceiling, os.path.basename(path)


def book_status(book_root):
    """The book's own declared state, or None.

    Reads the first `status:` key in the same 8,000-character head the length
    contract comes from. Only the literal value `in_progress` reclassifies the
    book; every other value (complete, drafting-as-decided, absent) leaves the
    row exactly as it was, because a finished book short of its floor is the
    finding L1 exists to report.
    """
    path = state_file(book_root)
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            head = fh.read(8000)
    except OSError:
        return None
    m = re.search(r"^\s*status\s*:\s*[\"']?([A-Za-z_. -]+)", head, re.I | re.M)
    if not m:
        return None
    value = m.group(1).strip().lower()
    return value if value == "in_progress" else None


def check_in_progress(label, chapters, target):
    """Report a drafting book's progress without ever calling it a failure."""
    floor, ceiling, source = target
    words = [n for _, n in chapters]
    total = sum(words)
    print("=" * 67)
    print(f"## {label}   {len(chapters)} chapters, {total:,} words")
    print("=" * 67)
    declared = f"{floor:,}" if floor == ceiling else f"{floor:,} - {ceiling:,}"
    print(f"declared target ({source}): {declared} words")
    print()
    print("   --    L1  declared length   IN PROGRESS, recorded not judged.")
    if total < floor:
        pct = 100.0 * total / floor
        print(f"          {total:,} of {floor:,} floor words ({pct:.0f}%). The book is")
        print("          still being drafted; this row does not read a draft as a")
        print("          delivery failure. It will enforce the contract again the")
        print("          moment the book stops declaring status: in_progress.")
    else:
        print(f"          {total:,} words, at or above the floor ({floor:,}). Drafting")
        print("          continues; the ceiling will be judged at delivery.")
    return 0


def check(label, chapters, target):
    floor, ceiling, source = target
    words = [n for _, n in chapters]
    total = sum(words)
    cv = 100 * st.pstdev(words) / st.mean(words) if st.mean(words) else 0.0

    print("=" * 67)
    print(f"## {label}   {len(chapters)} chapters, {total:,} words")
    print("=" * 67)
    advisory = "advisory" in source
    declared = f"{floor:,}" if floor == ceiling else f"{floor:,} - {ceiling:,}"
    print(f"declared target ({source}): {declared} words")
    print(f"  shortest chapter {min(words):,}   longest {max(words):,}   CV {cv:.1f}%")
    print()

    if total < floor:
        short = floor - total
        pct = 100.0 * short / floor
        status = "warn" if advisory else "FAIL"
        verdict = (f"{short:,} words SHORT of the floor ({pct:.0f}% under). "
                   f"Declared {floor:,}, delivered {total:,}.")
    elif total > ceiling:
        over = total - ceiling
        status = "warn" if advisory else "FAIL"
        verdict = (f"{over:,} words OVER the ceiling ({100.0 * over / ceiling:.0f}% over). "
                   f"Declared at most {ceiling:,}, delivered {total:,}.")
    else:
        status = "ok"
        verdict = (f"within the declared range, {total - floor:,} above the floor and "
                   f"{ceiling - total:,} below the ceiling.")

    print(f"   {status:<5} L1  declared length   {verdict}")
    if advisory:
        print("          ^ ADVISORY: the book declared a single figure, not a range.")
        print("            Failing it would mean inventing a tolerance. Declare")
        print("            target_floor_words and target_ceiling_words to enforce it.")
    print()

    # The pairing, stated explicitly. U1 and this row move in opposite directions,
    # which is the entire reason both exist.
    print("   Note: `U1` (chapter-length variance) is scale-invariant and can be")
    print("   satisfied by DELETING from the long chapters. This row is the only check")
    print("   in the directory that moves the other way. A book that cuts to raise its")
    print("   CV will fail here, and that is the design working.")
    print()

    if status == "FAIL":
        print("The book did not deliver the length it declared for itself.")
        print("Every other row in tools/prose/ is satisfied by a book that is shorter")
        print("than intended, because they are all rates. This one is not a rate.")
        return 1
    if status == "warn":
        print("Reported, not failed. The book declared one figure rather than a range,")
        print("and this row will not invent the tolerance that a failure would need.")
        return 0
    return 0


def main():
    args = sys.argv[1:]
    targets = []
    for arg in args:
        directory = resolve(arg)
        if not directory:
            print(f"check-length: no chapters found under {arg}")
            return 2
        targets.append((arg, directory))

    if not targets:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        found = glob_chapters(root)
        if not found:
            print("check-length: nothing checkable - a pass with no books read proves nothing.")
            return 2
        targets = found

    checked = failures = skipped = ungoverned = in_progress = 0
    for arg, directory in targets:
        chapters = load(directory)
        if len(chapters) < MIN_CHAPTERS:
            print(f"check-length: {arg} has {len(chapters)} chapters, fewer than "
                  f"{MIN_CHAPTERS} - cannot judge a book length, skipped")
            skipped += 1
            continue
        book_root = os.path.dirname(os.path.dirname(directory))
        if not os.path.isfile(state_file(book_root)):
            # Exit 3, not exit 2. The row did not decline to run; it had nothing to run
            # against, and that is the book's problem to fix, not the framework's.
            print(f"check-length: {arg} has NO {os.path.basename(state_file(book_root))} "
                  f"at its root ({book_root}) - the book is UNGOVERNED by this row.")
            print("          This is not the same as declaring no target length. It means")
            print("          nothing can say what length this book owes. Either the state")
            print("          file was archived, renamed or never created; find it and put it")
            print("          back, or say explicitly that this book has no length contract.")
            print("          Exit 3 means ungoverned. It is not a pass and not a fail.")
            ungoverned += 1
            continue
        target = declared_target(book_root)
        if not target:
            print(f"check-length: {arg} declares no target length "
                  f"(target_floor_words / target_ceiling_words, or a non-zero "
                  f"target_range_words) - NOT APPLICABLE, and not a pass")
            skipped += 1
            continue
        # Freeze 11: a book that says it is still being drafted is not a delivered
        # book, and reading it as LENGTH FAILURE trains the reader to ignore the
        # row that cannot lie at delivery time (ERRATA 2026-10-01, n=2 agreed).
        # The state comes from the book's own first status key in PROJECT_STATE.yaml
        # - the same 8k head this gate already reads - so no new input is needed.
        if book_status(book_root) == "in_progress":
            check_in_progress(os.path.basename(os.path.abspath(arg)),
                              chapters, target)
            print()
            in_progress += 1
            continue
        checked += 1
        failures += check(os.path.basename(os.path.abspath(arg)), chapters, target)
        print()

    if failures:
        print("=" * 67)
        print(f"LENGTH FAILURE - {failures} book(s) did not deliver their declared length.")
        print("Short chapters are not a style. This is the book being shorter than the")
        print("book that was asked for.")
        return 1

    if ungoverned:
        print("=" * 67)
        print(f"LENGTH UNGOVERNED - {ungoverned} book(s) have no PROJECT_STATE.yaml. "
              f"Exit 3, not 2.")
        if skipped:
            print(f"          ({skipped} other book(s) declared no target and were skipped; "
                  f"that is a different condition.)")
        print("An archive that removes a book's state file from its own directory")
        print("disarms this row silently. Say which of the two you meant.")
        return 3

    if in_progress:
        print("=" * 67)
        print(f"LENGTH IN PROGRESS - {in_progress} book(s) are still being drafted and "
              f"were recorded, not judged. Exit 4.")
        print("A book that declares status: in_progress owes nothing to this row yet.")
        print("The contract enforces again the moment the declaration is gone.")
        if checked:
            print(f"({checked} other book(s) were judged normally in the same run.)")
        return 4

    if checked == 0:
        print(f"check-length: nothing checkable ({skipped} book(s) skipped). "
              f"Exit 2 means not applicable; it never means pass.")
        return 2

    print(f"LENGTH OK - {checked} book(s) delivered their declared length.")
    return 0


def glob_chapters(root):
    import glob as _glob
    out = []
    for directory in sorted(_glob.glob(os.path.join(root, "*", "manuscript", "chapters"))):
        label = os.path.basename(os.path.dirname(os.path.dirname(directory)))
        out.append((label, directory))
    return out


if __name__ == "__main__":
    sys.exit(main())
