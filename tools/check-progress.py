#!/usr/bin/env python3
"""check-progress.py — two bookkeeping rows: C1 contract-vs-plan, L2 running total.

Not a prose gate and deliberately absent from GATE_FREEZE.md's manifest: same
exemption class as init-book.py, check-registry.py, check-pass-evidence.py. It
reads declarations and counts words exactly the way check-pass-evidence.py
already does; a FAIL here means the book's records contradict each other, never
that the prose is bad. The prose verdicts stay with the frozen instruments.

C1 contract-vs-plan (the judgment row). The length contract the book declares
for itself must agree with the plan the outline records — the per-chapter word
targets in outline.md, or failing those the state's own plan keys
(`chapter_count_planned` x `average_words_per_chapter_planned`). A contract
checked against nothing is what the 2026-10-13 systems audit found being used
to disarm L1: `check-length.py` reads the band from the book's own
PROJECT_STATE.yaml, so a band rewritten after the output was visible made the
gate agree with itself and pass. This row pins the band to a second record.
A contract that contradicts the plan FAILS. A contract with no plan is not a
pass — it is NOT RUN, because an absence is never a decision (KF-004's rule,
one layer up).

Unlike L1, C1 is never deferred by `status: in_progress`. L1's "recorded, not
judged" exists because a draft is not a delivery (Freeze 11); the contract and
the plan, by contrast, are up-front declarations and nothing about drafting
changes them. Deferring C1 during drafting would hand the mid-run contract
rewrite exactly the cover the row exists to remove.

L2 running total (the report row, never fails). Running words against the
outline's plan: what has been written versus what the written chapters were
planned to carry, and the total against the plan's sum. This is the number the
maintenance gate's stop-the-line rule already names ("a waiver ... that leaves
the running total behind the outline's plan") — before this row it had no tool.

Word counting is `len(text.split())` over whole chapter files — the same
convention check-length.py and check-pass-evidence.py use, so the three rows
cannot disagree by double digits. The contract vocabulary is not re-implemented
here: `declared_target()` is imported from tools/prose/check-length.py, which is
frozen, so one reader defines what a contract is.

Usage:
    python tools/check-progress.py <book-root>

Exit codes (the L1 contract vocabulary):
    0  C1 agrees (or the contract is advisory) — L2 reported alongside
    1  C1 FAIL: the contract contradicts the plan
    2  cannot judge: no contract, or no plan to check it against
    3  UNGOVERNED: no PROJECT_STATE.yaml at the book root
"""

import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHAPTER = re.compile(r"chapter[-_ ]?0*(\d+)", re.I)   # the check-pass-evidence convention
NUMCELL = re.compile(r"\d[\d,]*")
PLANCOL = re.compile(r"word|target|length", re.I)


def length_module():
    """tools/prose/check-length.py — the frozen reader of the contract.

    The naming schemes a contract may use live THERE (three of them are in live
    use; see its declared_target). If it cannot be loaded, this row reports
    NOT RUN rather than inventing a second vocabulary that can drift from the
    gate it is supposed to cross-check.
    """
    path = os.path.join(HERE, "prose", "check-length.py")
    if not os.path.isfile(path):
        return None
    try:
        spec = importlib.util.spec_from_file_location("check_length", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except (OSError, AttributeError, SyntaxError):
        return None
    return mod


def outline_plan(root):
    """The outline's plan: {chapter: target-words} from the outline's tables.

    Reads outline.md at the book root (or artifacts/outline.md) and takes the
    column the header calls words/target/length. A table without such a column
    is not a plan table — the clue ledger has chapter numbers too and must not
    be read as one. Returns {} when no plan table is found; that is a caller
    state (fall back to the state's plan keys), not an error.
    """
    for rel in ("outline.md", os.path.join("artifacts", "outline.md")):
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8", errors="ignore") as fh:
            lines = fh.read().splitlines()
        out = {}
        col = None  # None = the next row is a table header
        for line in lines:
            s = line.strip()
            if not s.startswith("|"):
                col = None
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                continue                      # separator row; header already seen
            if col is None:
                col = next((i for i, c in enumerate(cells)
                            if PLANCOL.search(c)), -1)
                continue
            if col < 0 or col >= len(cells) or not re.fullmatch(r"\d+", cells[0]):
                continue
            if NUMCELL.fullmatch(cells[col]):
                out[int(cells[0])] = int(cells[col].replace(",", ""))
        if out:
            return out
    return {}


def state_plan(root):
    """The state's own plan keys, as (chapters, words-per-chapter) or None.

    Tolerant of the naming schemes in live use, for the same reason
    check-length.py reads three contract schemes: the codex template says
    `chapters_planned` / `words_per_chapter_target`, real books say
    `chapter_count_planned` / `average_words_per_chapter_planned`. Zero means
    not declared, everywhere in this schema.
    """
    path = os.path.join(root, "PROJECT_STATE.yaml")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8", errors="ignore") as fh:
        head = fh.read(8000)

    def num(*keys):
        for key in keys:
            m = re.search(rf"^\s*{key}\s*:\s*[\"']?([0-9][0-9,_]*)", head, re.I | re.M)
            if m:
                v = int(m.group(1).replace(",", "").replace("_", ""))
                if v:
                    return v
        return None

    ch = num("chapter_count_planned", "chapters_planned", "total_planned")
    wpc = num("average_words_per_chapter_planned", "words_per_chapter_target")
    if ch and wpc:
        return ch, wpc
    return None


def chapters_on_disk(root):
    """[(number, name, words)] for every chapter file — counted the gate's way."""
    chdir = os.path.join(root, "manuscript", "chapters")
    out = []
    try:
        names = sorted(os.listdir(chdir))
    except FileNotFoundError:
        return out
    for n in names:
        m = CHAPTER.search(n)
        if not m:
            continue
        with open(os.path.join(chdir, n), encoding="utf-8", errors="ignore") as fh:
            words = len(fh.read().split())
        out.append((int(m.group(1)), n, words))
    return out


def main():
    if len(sys.argv) != 2:
        print("usage: python tools/check-progress.py <book-root>")
        return 2
    root = sys.argv[1]

    mod = length_module()
    if mod is None:
        print(f"check-progress: {os.path.join(HERE, 'prose', 'check-length.py')} could not be")
        print("          loaded - the contract vocabulary lives there and this row will not")
        print("          invent a second copy that can drift from the gate it cross-checks.")
        print("          NOT RUN. Not-run is never a pass.")
        return 2

    state = mod.state_file(root)
    if not os.path.isfile(state):
        print(f"check-progress: {root} has NO {os.path.basename(state)} at its root - the")
        print("          book is UNGOVERNED by these rows. Exit 3 is neither pass nor fail.")
        return 3

    chapters = chapters_on_disk(root)
    total = sum(w for _, _, w in chapters)

    outline = outline_plan(root)
    splan = state_plan(root)
    if outline:
        plan_sum = sum(outline.values())
        plan_desc = f"outline.md ({len(outline)} chapter targets)"
    elif splan:
        plan_sum = splan[0] * splan[1]
        plan_desc = (f"state plan keys ({splan[0]} chapters x "
                     f"{splan[1]:,} words)")
    else:
        plan_sum = None
        plan_desc = "no plan found"

    target = mod.declared_target(root)
    label = os.path.basename(os.path.abspath(root))

    print("=" * 67)
    print(f"## {label}   {len(chapters)} chapters, {total:,} words")
    print("=" * 67)

    # ---- C1: contract vs plan -------------------------------------------------
    if target is None:
        print(f"plan ({plan_desc}): "
              + (f"{plan_sum:,} planned words" if plan_sum else "none"))
        print("   --    C1  contract-vs-plan   NOT DECLARED - the book declares no length")
        print("          contract, so there is nothing for the plan to agree with.")
        print("          Cannot judge. Not-run is never a pass.")
        print()
        print("   --    L2  running total      ", end="")
        l2_report(outline, splan, chapters, total, plan_sum, plan_desc)
        return 2

    floor, ceiling, source = target
    advisory = "advisory" in source
    declared = f"{floor:,}" if floor == ceiling else f"{floor:,} - {ceiling:,}"
    src = os.path.basename(state)
    print(f"contract ({src}): {declared} words"
          + ("   [single figure - advisory]" if advisory else ""))
    print(f"plan ({plan_desc}): "
          + (f"{plan_sum:,} planned words" if plan_sum else "none"))
    print()

    if plan_sum is None:
        print("   --    C1  contract-vs-plan   NO PLAN - nothing outside the book's own")
        print(f"          {src} records what it owes. A contract checked against nothing")
        print("          is the self-declared contract the 2026-10-13 audit found disarming")
        print("          L1: the band is whatever the book says it is. Write the outline's")
        print("          per-chapter targets, or the state's chapter_count_planned and")
        print("          average_words_per_chapter_planned. Cannot judge; not a pass.")
        c1 = 2
    elif advisory:
        delta = plan_sum - floor
        print(f"   --    C1  contract-vs-plan   ADVISORY - the plan's {plan_sum:,} words against")
        print(f"          the declared figure {floor:,} ({delta:+,}). The book declared one")
        print("          figure, not a band, and this row will not invent the tolerance a")
        print("          failure would need - the same rule L1 follows.")
        c1 = 0
    elif plan_sum < floor:
        print(f"   FAIL  C1  contract-vs-plan   the plan's {plan_sum:,} words fall {floor - plan_sum:,}")
        print(f"          BELOW the contract's floor ({floor:,}). The outline plans a book")
        print("          shorter than the contract demands; the two declarations cannot both")
        print("          stand. Reconcile them at the source - outline or contract - rather")
        print("          than letting L1 judge against a number the outline does not support.")
        c1 = 1
    elif plan_sum > ceiling:
        print(f"   FAIL  C1  contract-vs-plan   the plan's {plan_sum:,} words run {plan_sum - ceiling:,}")
        print(f"          OVER the contract's ceiling ({ceiling:,}). The band has been set")
        print("          below what the outline plans - the shrink-the-band disarm, caught")
        print("          while it is still cheap. The contract owes the plan, not the other")
        print("          way round.")
        c1 = 1
    else:
        headroom_down = plan_sum - floor
        headroom_up = ceiling - plan_sum
        print(f"   ok    C1  contract-vs-plan   the plan's {plan_sum:,} words sit within the")
        print(f"          declared {floor:,} - {ceiling:,} ({headroom_down:,} above the floor,"
              f" {headroom_up:,} below the ceiling).")
        c1 = 0
        if headroom_down > plan_sum // 2:
            print(f"          NOTE: the floor sits {plan_sum - floor:,} under the plan. L1 would")
            print(f"          pass a {floor:,}-word book the outline does not plan. No threshold")
            print("          is invented here; the number is named so a person can judge.")
    if mod.book_status(root) == "in_progress":
        print("          status: in_progress does NOT defer this row (it defers L1, never C1):")
        print("          the contract and the plan are declarations, and drafting changes neither.")
    print()

    # ---- L2: running total (reports; never changes the exit) ------------------
    print("   --    L2  running total      ", end="")
    l2_report(outline, splan, chapters, total, plan_sum, plan_desc)
    return c1


def l2_report(outline, splan, chapters, total, plan_sum, plan_desc):
    """Running words against the plan. Prints; never decides."""
    if not chapters:
        print("nothing written yet - the running total starts at 0.")
        return
    if plan_sum is None:
        pct = 0
        print(f"{total:,} words written; no plan to run against ({plan_desc}).")
        return
    pct = 100.0 * total / plan_sum
    where = "BEHIND" if total < plan_sum else "at/over"
    print(f"{total:,} of {plan_sum:,} planned words ({pct:.0f}%) - {where}"
          + (f" by {plan_sum - total:,}." if total < plan_sum else "."))

    if outline:
        written_nums = {n for n, _, _ in chapters}
        expected = sum(t for n, t in outline.items() if n in written_nums)
        planned_mean = sum(outline.values()) / len(outline)
        if expected:
            delta = total - expected
            print(f"          expected by now (targets of the {len(written_nums)} written")
            print(f"          chapters): {expected:,} - running total is {delta:+,}.")
        under = [(n, w, outline[n]) for n, _, w in chapters
                 if n in outline and outline[n] and w < outline[n] * 0.5]
        if under:
            print(f"          {len(under)} chapter(s) under 50% of planned length - the")
            for n, w, t in under:
                print(f"            chapter-{n:02d}: {w:,} of {t:,} planned")
            print("          drafting floor - each needs a recorded waiver, per the gate.")
    else:
        planned_mean = splan[1]
        expected = len(chapters) * planned_mean
        print(f"          expected by now ({len(chapters)} chapters x {planned_mean:,}): "
              f"{expected:,} - running total is {total - expected:+,}.")
    actual_mean = total / len(chapters)
    print(f"          pace: {actual_mean:,.0f} words/chapter written vs "
          f"{planned_mean:,.0f} planned.")


if __name__ == "__main__":
    sys.exit(main())
