# Authoritative failure locator.
# The regexes and the P1 tokenizer here are transcribed from
# incunabula/tools/prose/deslop-check.sh and must stay byte-equal to it.
# The earlier _find.py was an approximation: it used {0,60} where the gate uses
# {0,50}, allowed (had|has) where the gate allows only (was|were|is|are), and it
# counted P1 openers with a different tokenizer than the gate's awk. Patching
# against it would have been patching against a different instrument.
#
# P1 fails on EITHER  count*1000 > 6*words  OR  share > 15% of sentences.
# The gate prints only the single most frequent two-word opener, so a chapter can
# fail on a key that is not the one you were hunting.

# --- paths derived from this file, not from the machine that ran it ----------------
# The run happened at C:/Users/screa/incunabula; a clone is somewhere else, so walk up
# until the repository root (the directory holding tools/prose/) is found.
import os


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isdir(os.path.join(d, "tools", "prose")):
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return d


REPO = _repo_root()
import io, os, re, sys, glob
from collections import Counter

A25 = re.compile(
    r"(was|were|is|are) not[^.!?]{0,50}[.!?] +(It|That|This|He|She|They) (was|were|is|are)"
)
A6 = re.compile(r"(^|[^a-z])Not [a-z][^.!?]{0,30}\. Not [a-z]", re.I)
OPEN_PER_N, OPEN_PER_W, OPEN_SHARE_PCT = 6, 1000, 15.0

# The gate compares n*allow_w > allow_n*words, and the two caps have DIFFERENT
# denominators: A25 is 3/2000 and A6 is 2/1000. Both were first written as n*1000,
# which is right for A6 and wrong for A25 - it understated the failure by a factor of
# two and hid book-2/chapter-10, where 4 hits in 1391 words is 2.88/1k and a clear FAIL.
A25_ALLOW_N, A25_ALLOW_W = 3, 2000
A6_ALLOW_N, A6_ALLOW_W = 2, 1000

SENT_SPLIT = re.compile(r"[.!?] ")


def load(path):
    """Read a chapter the way the gate reads it.

    The gate now strips CR in its read path, and it reads in text mode, so the model
    to match is: every CR removed, every line ending a bare LF. Reading with
    newline="" (no translation) and dropping "\\r" reproduces that exactly. Reading with
    the default universal newlines does NOT, because \\r\\r\\n becomes \\n\\n and the
    doubled blank line changes what awk's "$0" looks like. Getting this wrong is what
    made the first version of this script disagree with the gate on all 22 chapters.
    """
    return io.open(path, encoding="utf-8", newline="").read().replace("\r", "")
WORD = re.compile(r"[A-Za-z]")
TWO_LETTERS = re.compile(r"[a-z]+")


def words(t):
    return max(1, len(re.findall(r"[A-Za-z']+", t)))


def sentences(text):
    """Mirror of the gate's awk tokenizer, in order.

    The gate counts nsent over EVERY sentence containing any word, but only builds
    an opener key for sentences of two words or more. Those are two different
    denominators and the P1 share row depends on the first one, so both are kept.
    """
    buf = text.replace("\n", " ") + " "
    out = []
    for part in SENT_SPLIT.split(buf):
        line = re.sub(r"^[^A-Za-z]+", "", part)          # gsub(/^[^A-Za-z]+/,"",line)
        w = [x for x in re.split(r"[ \t]+", line) if x]
        wc = sum(1 for x in w if WORD.search(x))
        if wc == 0:
            continue
        key = None
        if wc >= 2:
            a, b = w[0].lower(), w[1].lower()
            if TWO_LETTERS.fullmatch(a) and TWO_LETTERS.fullmatch(b):
                key = a + " " + b
        out.append({"key": key, "wc": wc, "text": part.strip(), "line": line})
    return out


def top_opener(t):
    sents = sentences(t)
    cnt = Counter(s["key"] for s in sents if s["key"])
    if not cnt:
        return ("-", 0, len(sents))
    # the gate breaks ties on the alphabetically smaller key
    mk = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    return (mk[0], mk[1], len(sents))


def locate(t):
    """(key, char_offset, sentence_text) for every sentence, in order."""
    out = []
    buf = t.replace("\n", " ") + " "
    pos = 0
    for part in SENT_SPLIT.split(buf):
        start = buf.find(part, pos) if part else pos
        pos = start + len(part)
        for s in sentences(part):
            out.append((s["key"], start, s["text"]))
            break
    return out


def show(entries, t):
    for m in entries:
        ln = t[:m.start()].count("\n") + 1
        print("    L%-4d %s" % (ln, t[max(0, m.start() - 90):m.end() + 60]
                               .replace("\n", " ").strip()))


def main():
    only = sys.argv[1:] or ["book-1", "book-2"]
    for book in only:
        B = REPO + "/test-books/validation-series/%s/manuscript/chapters/" % book
        print("#" * 12, book)
        for f in sorted(glob.glob(B + "chapter-*.md")):
            t = load(f)
            name = os.path.basename(f)
            nw = words(t)
            a25 = list(A25.finditer(t))
            a6 = list(A6.finditer(t))
            key, n, nsent = top_opener(t)
            share = 100.0 * n / max(1, nsent)
            f25 = len(a25) * A25_ALLOW_W > A25_ALLOW_N * nw
            f6 = len(a6) * A6_ALLOW_W > A6_ALLOW_N * nw
            f1 = n * OPEN_PER_W > OPEN_PER_N * nw or share > OPEN_SHARE_PCT
            if not (f25 or f6 or f1):
                continue
            print("\n%s  (%d words, %d sentences)" % (name, nw, nsent))
            if f25:
                print("  A25  %d hits, cap 3/2000 -> %d allowed, rate %.2f/1k"
                      % (len(a25), A25_ALLOW_N * nw // A25_ALLOW_W, 1000.0 * len(a25) / nw))
                show(a25, t)
            if f6:
                print("  A6   %d hits, cap 2/1000 -> %d allowed, rate %.2f/1k"
                      % (len(a6), A6_ALLOW_N * nw // A6_ALLOW_W, 1000.0 * len(a6) / nw))
                show(a6, t)
            if f1:
                why = []
                if n * OPEN_PER_W > OPEN_PER_N * nw:
                    why.append("rate %d*1000 > 6*%d" % (n, nw))
                if share > OPEN_SHARE_PCT:
                    why.append("share %.1f%% > 15%%" % share)
                print('  P1   "%s" x%d of %d sentences (%s)'
                      % (key, n, nsent, " AND ".join(why)))
                for k, at, part in locate(t):
                    if k == key:
                        ln = t[:at].count("\n") + 1
                        print("    L%-4d %s" % (ln, part[:170]))
                allc = Counter(k for k, _, _ in locate(t) if k)
                print("    run-up: %s" % ", ".join("%s x%d" % (k, v)
                                                  for k, v in allc.most_common(6)))



if __name__ == "__main__":
    main()
