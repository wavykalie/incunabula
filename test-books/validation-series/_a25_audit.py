# Audit every A25 hit: real antithesis, or the regex matching " not" inside a word?
#
# A25 is `(was|were|is|are) not[^.!?]{0,50}[.!?] +(It|That|This|He|She|They) (was|were|is|are)`.
# There is no word boundary after `not`, so "was NOTHING in it worth the walk. It was"
# matches: the regex takes "was not" and then "hing in it worth the walk" as the
# intervening clause. That is not an antithesis formula. It is a substring accident.
#
# This matters because the fix for a false positive is to change the GATE, not the prose.
# Editing a correct sentence to dodge a regex bug is the exact opposite of what a gate
# is for, and it would silently degrade the manuscript to satisfy the instrument.
#
# Classify every hit, then say how many of the 10 failing chapters fail for real.

import glob, io, os, re, sys

sys.path.insert(0, "C:/Users/screa/incunabula/test-books/validation-series")
import _locate as L

real = fake = 0
chapters_with_fake_only = []

for book in ("book-1", "book-2"):
    for f in sorted(glob.glob("C:/Users/screa/incunabula/test-books/validation-series/%s/manuscript/chapters/chapter-*.md" % book)):
        t = L.load(f)
        nw = L.words(t)
        ms = list(L.A25.finditer(t))
        if not ms:
            continue
        label = "%s/%s" % (book, os.path.basename(f)[:-3])
        print("\n%s  (%d words, %d A25 hits)" % (label, nw, len(ms)))
        for m in ms:
            # the word immediately after the matched " not"
            after = t[m.end() - len(" was") + 4 if False else m.start():]
            mm = re.match(r"(was|were|is|are) not", m.group(0))
            tail = t[m.start() + len(mm.group(0)):]
            word = re.match(r"[A-Za-z']+", tail)
            w = word.group(0) if word else ""
            # A genuine negation means "not" is a whole word: the next character
            # after the match must not be a letter. Testing the remainder against a
            # word list was wrong and marked "nothing" as real, because the remainder
            # is "hing".
            genuine = not tail[:1].isalpha()
            kind = "REAL" if genuine else "FALSE POSITIVE"
            if genuine:
                real += 1
            else:
                fake += 1
            print("  L%-4d %-14s %r" % (t[:m.start()].count("\n") + 1, kind,
                                        t[max(0, m.start() - 45):m.end() + 30]
                                        .replace("\n", " ")))

print("\n%d real, %d false positive" % (real, fake))
