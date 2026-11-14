#!/usr/bin/env python3
"""corpus-report.py - which corpus can answer which question, measured.

WHY THIS EXISTS
  CORPUS_MAP.md makes an argument: one corpus cannot serve every genre, and the eight caps
  in deslop-check.sh were derived from a single series. An argument in prose is an opinion
  with better manners. This walks the registry, measures every lane on disk with the same
  arithmetic `ductus-fit.py` uses (imported, never re-implemented), and prints - per lane,
  per capped row - the lane's worst document beside the cap that governs it.

WHAT THE NUMBERS MEAN
  worst doc   the highest rate any single document in this lane produces. The unit every
              cap in this project was derived on.
  headroom    gate cap minus the worst document. NEGATIVE IS THE FINDING: published prose
              from a lane the cap was not derived from is already failing it.
  new cap     what the cap would be if it were derived on THIS lane - 1.5x the worst for
              the density rows (CALIBRATION.md s11), worst+1 for P3, which is a run length
              and was set that way (worst 6, fail at 7). The basis is printed.
  that would  RAISE / LOWER / AGREE against the gate's cap. Evidence, not a decision.

  A cap that sits inside a row's cross-lane spread depends on which corpus was asked. That
  is the case for separate lanes. It is not permission to move a number.

WHAT IT DOES NOT DO
  It moves no cap and edits nothing. deslop-check.sh and CALIBRATION.md are read only.
  Per-lane caps need a scanner change and the author's signature (CORPUS_MAP.md section 6).

EXIT
  0  at least one lane measured
  2  NOT RUN - no lane has text at its registered path, or the registry cannot be read

usage: python tools/prose/corpus-report.py [--lane NAME] [--registry FILE]
       python tools/prose/corpus-report.py --self-test
"""
import importlib.util
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FIT_PATH = os.path.join(HERE, "ductus-fit.py")
LANES = os.path.join(HERE, "calibration", "LANES.tsv")
LANE_BOOKS = (5, 10)
LANE_WORDS = (500_000, 1_000_000)
# A declared word count is typed into a registry by hand and the corpus is re-staged by
# scripts; 0.5% is the difference between a stale annotation and a corpus that is not the
# corpus. Anything larger is reported as DRIFT rather than silently believed.
DRIFT_TOLERANCE = 0.005


def load_fit():
    spec = importlib.util.spec_from_file_location("ductus_fit", FIT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FIT = load_fit()

WORK = re.compile(r"(?:-v\d+)?__.*$")


def work_stem(path):
    """The work a document belongs to. `austen-pride-v01__chapter-01.txt` -> austen-pride."""
    return WORK.sub("", os.path.splitext(os.path.basename(path))[0])


def measure_lane(lane, root):
    """docs, words, works, metrics for one lane. Empty metrics means nothing to measure."""
    rel = (lane.get("path") or "").strip()
    directory = os.path.join(root, rel) if rel else None
    empty = {"docs": 0, "words": 0, "works": 0, "metrics": [], "path": directory}
    if not directory or not os.path.isdir(directory):
        return empty
    docs = FIT.corpus_docs(directory)
    metrics = [m for m in (FIT.metrics(FIT.read_text(p)) for p in docs) if m]
    if not metrics:
        return empty
    return {"docs": len(metrics),
            "words": sum(m["words"] for m in metrics),
            "works": len({work_stem(p) for p in docs}),
            "metrics": metrics,
            "path": directory}


def new_cap(rid, worst):
    """(value, basis) - what this lane's worst document implies for the cap.

    Two derivations, because this project used two and pretending otherwise would put a
    wrong number beside a real one: the density rows are re-derived at 1.5x the worst
    published document, and P3 is a run length capped at worst+1.
    """
    if rid == "P3":
        return worst + 1.0, "worst+1"
    return worst * 1.5, "1.5x"


def direction(value, cap):
    if cap is None:
        return "CAP NOT READ"
    if value > cap + 0.05:
        return "RAISE"
    if value < cap - 0.05:
        return "LOWER"
    return "AGREE"


def _num(value, unit):
    if unit == "sentences":
        return "%d" % round(value)
    return "%.1f" % value


def _declared(lane, key):
    raw = (lane.get(key) or "").strip()
    try:
        return int(raw)
    except ValueError:
        return None


def analyse(lanes_path=LANES, root=ROOT, only=None):
    """(exit code, report text). The only place the arguments are interpreted."""
    lanes, problem = FIT.read_lanes(lanes_path)
    if problem:
        return 2, "corpus-report: NOT RUN - %s" % problem
    if not lanes:
        return 2, "corpus-report: NOT RUN - the registry holds no lanes."
    if only:
        lanes = [l for l in lanes if l["lane"] == only]
        if not lanes:
            return 2, "corpus-report: no lane %r in the registry." % only

    caps, _tiers, caps_problem = FIT.read_gate()
    try:
        shown = os.path.relpath(lanes_path, root).replace(os.sep, "/")
    except ValueError:
        shown = os.path.basename(lanes_path)

    out = ["corpus-report - %d lane(s) in %s" % (len(lanes), shown)]
    if caps_problem:
        out.append("  CAPS NOT READ: %s" % caps_problem)
    else:
        out.append("  gate caps  " + "  ".join(
            "%s %s" % (rid, _num(caps[rid], unit))
            for rid, _label, _key, unit in FIT.CAP_ROWS if rid in caps))

    spread, measured, breaches, compared = {}, 0, 0, 0
    for lane in lanes:
        books = _declared(lane, "books")
        words = _declared(lane, "words")
        out.append("")
        out.append("%s  [%s]" % (lane["lane"], lane.get("role", "?")))
        out.append("  register  %s" % lane.get("register", ""))
        out.append("  era       %s   status %s" % (lane.get("era", "unrecorded"),
                                                   lane.get("status", "")))
        out.append("  declared  %s work(s), %s words" % (
            lane.get("books", "?"), lane.get("words", "?")))
        m = measure_lane(lane, root)
        if not m["metrics"]:
            out.append("  measured  NOT INSTALLED at %s" % lane.get("path", ""))
            if (books or 0) > 0 or (words or 0) > 0:
                out.append("  DRIFT     the registry declares text at a path that holds "
                           "none - this lane cannot be re-measured here")
            out.append("  size      cannot be judged - no text at the registered path")
            out.append("  can       %s" % lane.get("answers", ""))
            out.append("  cannot    %s" % lane.get("cannot", ""))
            continue

        measured += 1
        drift = []
        if words is None or abs(words - m["words"]) > max(1, DRIFT_TOLERANCE * m["words"]):
            drift.append("words %+d" % (m["words"] - (words or 0)))
        # `works` when declared, `books` otherwise: a study lane may hold seven works cut
        # into four hundred documents, and comparing its `books: 0` to the measured work
        # count reported every such lane as drift.
        declared_works = _declared(lane, "works")
        if declared_works is None:
            declared_works = books
        if declared_works is not None and declared_works != m["works"]:
            drift.append("works %+d" % (m["works"] - declared_works))
        out.append("  measured  %d document(s), %d words, %d work(s)   %s" % (
            m["docs"], m["words"], m["works"],
            "MATCH" if not drift else "DRIFT in " + ", ".join(drift)))
        within = (LANE_BOOKS[0] <= m["works"] <= LANE_BOOKS[1]
                  and LANE_WORDS[0] <= m["words"] <= LANE_WORDS[1])
        out.append("  size      %s the rule (%d-%d works, %dk-%dk words)" % (
            "within" if within else "outside", LANE_BOOKS[0], LANE_BOOKS[1],
            LANE_WORDS[0] // 1000, LANE_WORDS[1] // 1000))
        out.append("  can       %s" % lane.get("answers", ""))
        out.append("  cannot    %s" % lane.get("cannot", ""))
        out.append("")
        out.append("  %-24s %10s %9s %10s %13s   %s" % (
            "row", "worst doc", "gate cap", "headroom", "new cap", "that would"))
        for rid, label, key, unit in FIT.CAP_ROWS:
            worst = max(x[key] for x in m["metrics"])
            value, basis = new_cap(rid, worst)
            cap = caps.get(rid)
            headroom = "" if cap is None else "%+0.1f" % (cap - worst)
            say = direction(value, cap)
            if cap is not None:
                compared += 1
                if worst > cap:
                    breaches += 1
            out.append("  %-24s %10s %9s %10s %13s   %s" % (
                "%s %s" % (rid, label), _num(worst, unit),
                _num(cap, unit) if cap is not None else "-", headroom,
                "%s %s" % (_num(value, unit), basis), say))
            spread.setdefault(rid, []).append((lane["lane"], worst, cap))

    if not measured:
        out.append("")
        out.append("corpus-report: NOT RUN - not one lane has text at its registered path.")
        return 2, "\n".join(out)

    out.append("")
    out.append("row spread across the %d measured lane(s)" % measured)
    out.append("  %-26s %7s %8s %8s %9s %13s   %s" % (
        "row", "lanes", "min", "max", "gate cap", "cap inside?", "widest lane"))
    inside = 0
    for rid, label, _key, unit in FIT.CAP_ROWS:
        cells = spread.get(rid, [])
        if not cells:
            continue
        worst_lane = max(cells, key=lambda c: c[1])
        cap = cells[0][2]
        lo = min(c[1] for c in cells)
        hi = worst_lane[1]
        straddles = cap is not None and lo < cap < hi
        if straddles:
            inside += 1
        out.append("  %-26s %7d %8s %8s %9s %13s   %s" % (
            "%s %s" % (rid, label), len(cells), _num(lo, unit), _num(hi, unit),
            _num(cap, unit) if cap is not None else "-",
            "YES" if straddles else ("no" if cap is not None else "-"), worst_lane[0]))
    out.append("")
    out.append("  %d of %d rows have the gate's cap inside the cross-lane range: the same"
               % (inside, len(spread)))
    out.append("  number is defensible for one register and wrong for another. %d of %d"
               % (breaches, compared))
    out.append("  lane-rows are published prose already past a cap it was not derived on.")
    out.append("  No cap was moved. Per-lane caps are a freeze event (CORPUS_MAP.md s6).")
    return 0, "\n".join(out)


def self_test():
    """The report must fire, read extra columns, and refuse an unmeasurable registry."""
    ok = True
    tmp = tempfile.mkdtemp(prefix="corpus-report-")
    try:
        caps, _t, problem = FIT.read_gate()
        if problem or abs(caps.get("D1", -1) - 10.0) > 1e-9:
            print("self-test: the gate caps are not readable; nothing below proves anything")
            return 1

        plain = " ".join(["He walked to the door and put the key in it."] * 60)
        dashed = plain.replace(". ", " \u2014and then\u2014 ", 30)
        lanes = []

        def lane(name, body, path, books="1", words=None, status="INSTALLED"):
            d = os.path.join(tmp, name)
            os.makedirs(d)
            with open(os.path.join(d, "doc-01.txt"), "w", encoding="utf-8") as fh:
                fh.write(body)
            lanes.append("\t".join([name, "control", "test register", books,
                                    words or str(len(body.split())), path, "synthetic",
                                    books, "now", status, "nothing", "nothing"]))

        lane("plain", plain, "plain")
        lane("dashed", dashed, "dashed")
        # Declares text at a path that holds none: the registry-drift case.
        lanes.append("\t".join(["ghost", "planned", "no text", "3", "175144",
                                "does-not-exist", "synthetic", "3", "now",
                                "INSTALLED ELSEWHERE", "nothing", "everything"]))
        registry = os.path.join(tmp, "LANES.tsv")
        header = ("lane\trole\tregister\tbooks\twords\tpath\tnote\tworks\tera\tstatus"
                  "\tanswers\tcannot")
        with open(registry, "w", encoding="utf-8") as fh:
            fh.write(header + "\n" + "\n".join(lanes) + "\n")

        rows, problem = FIT.read_lanes(registry)
        if problem or len(rows) != 3:
            print("self-test: the registry did not parse (%s)" % (problem or len(rows)))
            return 1
        if rows[0].get("status") != "INSTALLED" or rows[0].get("answers") != "nothing":
            print("self-test: extra columns are not mapped by header name")
            ok = False

        code, text = analyse(registry, tmp)
        if code != 0:
            print("self-test: a measurable registry exited %d\n%s" % (code, text))
            return 1
        if "RAISE" not in text:
            print("self-test: a dash-heavy lane did not raise the em-dash cap")
            ok = False
        if "NOT INSTALLED at" not in text:
            print("self-test: a lane with no text was not reported as NOT INSTALLED")
            ok = False
        if "DRIFT" not in text:
            print("self-test: declared text at an empty path was not reported as DRIFT")
            ok = False
        if "inside the cross-lane range" not in text:
            print("self-test: the spread summary is missing")
            ok = False

        # A registry missing a required column must be a problem, not a shifted read.
        short = os.path.join(tmp, "short.tsv")
        with open(short, "w", encoding="utf-8") as fh:
            fh.write("lane\trole\tbooks\nx\tcontrol\t1\n")
        rows2, problem2 = FIT.read_lanes(short)
        if not problem2 or rows2:
            print("self-test: a header missing required columns was accepted")
            ok = False
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    if not ok:
        return 1
    print("corpus-report: PASS - header-mapped registry, extra columns read, a dashed lane "
          "would RAISE D1, an empty path with declared text is DRIFT, a short header is "
          "refused, and the cross-lane spread is reported.")
    return 0


def main(argv):
    args = list(argv[1:])
    if "--self-test" in args:
        return self_test()
    only = None
    if "--lane" in args:
        i = args.index("--lane")
        only = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
        if not only:
            print("corpus-report: --lane needs a lane slug.")
            return 2
    registry = LANES
    if "--registry" in args:
        i = args.index("--registry")
        registry = args[i + 1]
        del args[i:i + 2]
    code, text = analyse(registry, ROOT, only)
    print(text)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
