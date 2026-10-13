import io, re, glob, os, sys

A25 = re.compile(r"(?:was|were|is|are) not[^.!?]{0,60}[.!?] +(?:It|That|This|He|She|They|There) (?:was|were|is|are|had|has)", re.I)
A6  = re.compile(r"\bnot \w+ not \w+", re.I)

for book in ("book-1", "book-2"):
    B = "C:/Users/screa/incunabula/test-books/validation-series/%s/manuscript/chapters/" % book
    print("##########", book)
    for f in sorted(glob.glob(B + "chapter-*.md")):
        t = io.open(f, encoding="utf-8").read()
        name = os.path.basename(f)
        for rx, lab in ((A25, "A25"), (A6, "A6 ")):
            for x in rx.finditer(t):
                line = t[:x.start()].count("\n") + 1
                print("  %-8s %s L%-4d %s" % (name, lab, line,
                      t[max(0, x.start()-70):x.end()+30].strip().replace("\n", " ")))
        # anaphora: leading "I did" / "I told" / "I had" sentence openers
        for op in ("I did", "I told", "I had"):
            n = len(re.findall(r"(?:^|(?<=[.!?])\s+|\n)" + op + r"\b", t))
            if n >= 5:
                print("  %-8s P1  %r x%d" % (name, op, n))
