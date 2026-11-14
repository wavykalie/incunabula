#!/usr/bin/env python3
"""check-excerpts.py - the excerpt directory is usable, attributed, and has not leaked.

WHY THIS EXISTS
  A ductus's excerpts are passages from books the author holds: local-copy text under
  `study/corpus/SOURCE_POLICY.md`. They may be measured where they sit and must never be
  shipped. The book tree is untracked, so the directory is already outside git - this tool
  checks the two ways that quietly stops being true: an excerpt pasted into a tracked file,
  and an excerpt file nobody can attribute.

  It also answers the question `ductus-fit.py` refuses to guess at: is there enough text
  here to measure, and does every file carry the source line the report needs?

WHAT IT CHECKS
  source     every excerpt starts with a `---` block holding a `source:` line
  size       2-5 files, 500 words pooled (the fit's own floor; below it, a per-1k rate is
             one or two hits and the report would be a verdict about type)
  leak       no git-tracked file reproduces an 8-word run from an excerpt. Eight words is
             SOURCE_POLICY.md's threshold: shorter runs survive ordinary quotation.

WHAT IT DOES NOT DO
  It does not run the fit (`ductus-fit.py` does), it does not judge the passages, and it
  does not compare them to a lane.

usage:  python tools/prose/check-excerpts.py <book-root> [--excerpts DIR]
        python tools/prose/check-excerpts.py --self-test

exit
  0  every excerpt is attributed, the size is usable, and nothing tracked reproduces it
  1  a missing source line, too little text, or a leak
  2  NOT RUN - no excerpt directory, or no excerpt files in it
"""
import glob
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NGRAM = 8
FILES = (2, 5)
WORDS = 500
TEXT_EXT = (".md", ".txt", ".csv", ".json", ".tsv", ".jsonl", ".yaml", ".yml")
HEADER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
WORD = re.compile(r"[a-z0-9']+")


def shingles(text, n=NGRAM):
    seq = WORD.findall(text.lower())
    return {" ".join(seq[i:i + n]) for i in range(len(seq) - n + 1)}


def excerpt_files(directory):
    out = []
    for path in sorted(glob.glob(os.path.join(directory, "*.txt")) +
                       glob.glob(os.path.join(directory, "*.md"))):
        if os.path.basename(path).lower().startswith(("readme", "manifest")):
            continue
        out.append(path)
    return out


def source_of(text):
    """(source, body) - the declared source line, or (None, text)."""
    m = HEADER.match(text)
    if not m:
        return None, text
    for line in m.group(1).splitlines():
        if line.strip().lower().startswith("source:"):
            return line.split(":", 1)[1].strip(), text[m.end():]
    return None, text[m.end():]


def tracked(root=ROOT):
    """Every git-tracked text file under the repository root."""
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True,
                             capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return [os.path.join(root, rel) for rel in out.split("\0")
            if rel and rel.lower().endswith(TEXT_EXT)]


def find_leaks(artifacts, marks):
    """[(artifact, excerpt, span)] for every tracked file reproducing a run."""
    found = []
    for path in artifacts:
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                seq = WORD.findall(fh.read().lower())
        except OSError:
            continue
        for i in range(len(seq) - NGRAM + 1):
            span = " ".join(seq[i:i + NGRAM])
            for name, markset in marks.items():
                if span in markset:
                    found.append((path, name, span))
                    break
    return found


def analyse(book, excerpts_dir=None):
    """(exit code, report lines). The only place the arguments are interpreted."""
    directory = excerpts_dir or os.path.join(book or "", "ductus", "excerpts")
    if not os.path.isdir(directory):
        alt = os.path.join(book or "", "excerpts")
        if os.path.isdir(alt):
            directory = alt
        else:
            return 2, ["check-excerpts: NOT RUN - no excerpt directory at %s." % directory,
                       "  Expected <book>/ductus/excerpts/*.txt, each with a source line."]
    files = excerpt_files(directory)
    if not files:
        return 2, ["check-excerpts: NOT RUN - %s holds no excerpt .txt files."
                   % os.path.relpath(directory, ROOT).replace(os.sep, "/"),
                   "  Zero excerpts is NOT RUN, never a pass. See the directory's README."]

    problems, marks, total = [], {}, 0
    out = ["check-excerpts - %s" % os.path.relpath(directory, ROOT).replace(os.sep, "/"),
           "  %-28s %6s  %s" % ("excerpt", "words", "source")]
    for path in files:
        text = open(path, encoding="utf-8", errors="replace").read()
        source, body = source_of(text)
        words = len(body.split())
        total += words
        marks[os.path.basename(path)] = shingles(body)
        out.append("  %-28s %6d  %s" % (os.path.basename(path)[:28], words,
                                        source or "** MISSING **"))
        if not source:
            problems.append("%s has no `source:` line - the fit cannot attribute it"
                            % os.path.basename(path))
    out.append("  %-28s %6d  across %d file(s)" % ("pooled", total, len(files)))

    if not FILES[0] <= len(files) <= FILES[1]:
        problems.append("%d excerpt(s); the ductus asks for %d-%d"
                        % (len(files), FILES[0], FILES[1]))
    if total < WORDS:
        problems.append("%d pooled words, below the %d-word floor - the fit will refuse"
                        % (total, WORDS))

    artifacts = tracked()
    if artifacts is None:
        out.append("  leak      NOT CHECKED - git is not available here")
    else:
        out.append("  leak      %d tracked text file(s) scanned for %d-word runs"
                   % (len(artifacts), NGRAM))
        for path, name, span in find_leaks(artifacts, marks):
            problems.append("%s reproduces %d words of %s: \"%s...\""
                            % (os.path.relpath(path, ROOT).replace(os.sep, "/"),
                               NGRAM, name, span[:50]))

    if problems:
        out.append("")
        for p in problems:
            out.append("  FAIL  %s" % p)
        return 1, out
    out.append("")
    out.append("OK - attributed, %d words, and no tracked file carries an 8-word run from"
               " any of it." % total)
    return 0, out


def self_test():
    """The checker must fail on a missing source, on thin text, and on a leak."""
    ok = True
    tmp = tempfile.mkdtemp(prefix="excerpts-")
    try:
        good = "He ran. " + " ".join(["the door was shut and the man was already gone."] * 40)
        with open(os.path.join(tmp, "01-good.txt"), "w", encoding="utf-8") as fh:
            fh.write("---\nsource: a work\n---\n" + good)
        with open(os.path.join(tmp, "02-good.txt"), "w", encoding="utf-8") as fh:
            fh.write("---\nsource: another work\n---\n" + good.replace("door", "stair"))
        code, text = analyse(None, tmp)
        if code != 0:
            print("self-test: a clean, attributed directory failed:\n" + "\n".join(text))
            ok = False

        with open(os.path.join(tmp, "03-nosource.txt"), "w", encoding="utf-8") as fh:
            fh.write(good)
        code, text = analyse(None, tmp)
        if code != 1 or "MISSING" not in "\n".join(text):
            print("self-test: a file with no source line was accepted")
            ok = False
        os.remove(os.path.join(tmp, "03-nosource.txt"))

        thin = os.path.join(tmp, "thin")
        os.makedirs(thin)
        with open(os.path.join(thin, "01-a.txt"), "w", encoding="utf-8") as fh:
            fh.write("---\nsource: a work\n---\nHe ran. The door was shut.\n")
        with open(os.path.join(thin, "02-b.txt"), "w", encoding="utf-8") as fh:
            fh.write("---\nsource: another work\n---\nShe walked in and sat down.\n")
        code, text = analyse(None, thin)
        if code != 1 or "below the" not in "\n".join(text):
            print("self-test: a two-sentence directory passed the size floor")
            ok = False

        marks = {"excerpt": shingles(good)}
        art = os.path.join(tmp, "tracked.md")
        with open(art, "w", encoding="utf-8") as fh:
            fh.write("A report quoting: " + good[8:120] + "\n")
        found = find_leaks([art], marks)
        if not found:
            print("self-test: a tracked file reproducing 8+ words was not caught")
            ok = False
        avoided = os.path.join(tmp, "clean.md")
        with open(avoided, "w", encoding="utf-8") as fh:
            fh.write("He ran, and the door was shut, but the man had already gone.\n")
        if find_leaks([avoided], marks):
            print("self-test: ordinary prose was reported as a leak")
            ok = False
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    if not ok:
        return 1
    print("check-excerpts: PASS - a clean directory passes, a missing source line and a "
          "thin directory both fail, an 8-word copy in a tracked file is caught, and "
          "ordinary prose is not.")
    return 0


def main(argv):
    args = list(argv[1:])
    if "--self-test" in args:
        return self_test()
    excerpts = None
    if "--excerpts" in args:
        i = args.index("--excerpts")
        excerpts = args[i + 1] if i + 1 < len(args) else None
        del args[i:i + 2]
    book = args[0] if args else None
    if not book and not excerpts:
        print("usage: python tools/prose/check-excerpts.py <book-root> [--excerpts DIR]")
        return 2
    code, text = analyse(book, excerpts)
    print("\n".join(text))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
