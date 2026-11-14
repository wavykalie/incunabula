#!/usr/bin/env python3
"""monotony-units.py - calibrate check-monotony.py against published English fiction.

`check-monotony.py` shipped with thresholds set just above one book's post-pass
baseline, labelled provisional, and a TODO to calibrate against the same six volumes
`check-uniformity.py` uses. This is that calibration, done by running the SHIPPED gate
rather than by re-implementing its arithmetic: a threshold derived from a second
implementation measures the second implementation.

Method (same as the rest of this directory): stage each volume into a throwaway
`manuscript/chapters/chapter-NN.md` tree, run `check-monotony.py` on it, read the four
M lines back, and report per-volume figures. A volume is only measurable if it has the
gate's minimum word count.

usage: python monotony-units.py [--corpus DIR] [--all]
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
GATE = os.path.join(ROOT, "tools", "prose", "check-monotony.py")
DEFAULT_CORPUS = os.path.join(HERE, "corpus", "multivolume")

# The six volumes check-uniformity.py's floors were derived from.
SIX = ["austen-pride", "bronte-jane-eyre", "bronte-wuthering",
       "eliot-middlemarch", "hardy-tess", "stoker-dracula"]

NAME = re.compile(r"^(?P<stem>.+?)-v\d+__chapter-(?P<num>\d+)\.txt$")


def volumes(corpus, want_all):
    vols = {}
    for p in sorted(glob.glob(os.path.join(corpus, "*.txt"))):
        m = NAME.match(os.path.basename(p))
        if not m:
            continue
        vols.setdefault(m.group("stem"), []).append((int(m.group("num")), p))
    if not want_all:
        vols = {k: v for k, v in vols.items() if k in SIX}
    return {k: sorted(v) for k, v in vols.items()}


def measure(stem, files):
    tmp = tempfile.mkdtemp(prefix="monotony-%s-" % stem)
    try:
        d = os.path.join(tmp, "manuscript", "chapters")
        os.makedirs(d)
        for num, src in files:
            shutil.copyfile(src, os.path.join(d, "chapter-%02d.md" % num))
        r = subprocess.run([sys.executable, GATE, tmp], capture_output=True, text=True)
        out = r.stdout
        def num_from(pattern, cast=float):
            m = re.search(pattern, out, re.M)
            return cast(m.group(1)) if m else None
        return {
            "chapters": len(files),
            "words": num_from(r"^\s+(\d+) words,", int),
            "M1_found": num_from(r"M1 .*?: (\d+) found", int),
            "M1_worst": num_from(r"worst (\d+)$", int),
            "M2": num_from(r"M2 subject openings: ([\d.]+)%"),
            "M3": num_from(r"M3 'did not': ([\d.]+) per 10k"),
            "M4": num_from(r"M4 texture words: ([\d.]+) per 10k"),
            "exit": r.returncode,
            "err": r.stderr[-400:],
            "raw": out,
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    corpus = DEFAULT_CORPUS
    if "--corpus" in sys.argv:
        corpus = sys.argv[sys.argv.index("--corpus") + 1]
    if not os.path.isdir(corpus):
        print("monotony-units: no corpus at %s - nothing measured, nothing calibrated." % corpus)
        return 2
    vols = volumes(corpus, "--all" in sys.argv)
    if not vols:
        print("monotony-units: no <stem>-vNN__chapter-NN.txt files in %s." % corpus)
        return 2
    rows = []
    for stem, files in vols.items():
        r = measure(stem, files)
        rows.append((stem, r))
        print("%-22s %2d ch %7s words   M1 %s/%s   M2 %5.1f%%   M3 %5.1f   M4 %5.1f   exit %d" % (
            stem, r["chapters"], r["words"], r["M1_found"], r["M1_worst"],
            r["M2"] or -1, r["M3"] or -1, r["M4"] or -1, r["exit"]))
    ok = [(s, r) for s, r in rows if r["M2"] is not None]
    if not ok:
        print("monotony-units: no volume cleared the gate's minimum size.")
        return 2
    print("")
    print("published worst across %d volume(s):" % len(ok))
    for k, label in (("M2", "M2 subject openings %"), ("M3", "M3 did-not /10k   "),
                     ("M4", "M4 texture /10k   ")):
        worst = max(r[k] for _, r in ok)
        who = [s for s, r in ok if r[k] == worst][0]
        print("  %s worst %6.1f  (%s)   1.5x would be %6.1f - printed, not enforced"
              % (label, worst, who, worst * 1.5))
    worst1 = max((r["M1_worst"] or 0) for _, r in ok)
    found = sum(1 for _, r in ok if (r["M1_found"] or 0) > 0)
    print("  M1 repeated runs   worst %d use(s) in one volume; %d of %d volumes trip the row"
          % (worst1, found, len(ok)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
