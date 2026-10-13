#!/usr/bin/env python3
# CORRECTION to _fix_eol.py (both runs are the record).
#
# Run 1 misread the evidence: it treated the 10 seam-affected files as CRLF-drafted
# because `file` reported "CRLF, LF" for them, but the counts in its own output
# (crlf 2 + bare-lf 163 ...) show those files were LF-DRAFTED and the edit passes'
# "\r\n\r\n" seam had introduced the only CRLF bytes in them. Only chapter-31.md was
# genuinely CRLF-drafted (296 CRLF + 9 LF from a textwrap.fill insertion).
#
# This run restores each file to its drafting convention, at internal consistency:
#   LF-drafted   -> pure LF   (the seam CRLF bytes are removed too)
#   CRLF-drafted -> pure CRLF (run 1 already did 31 correctly)
# PROSE IS NOT TOUCHED in either run: only line-ending bytes.
import io, os

CH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "manuscript", "chapters")
LF_FILES = ["chapter-02.md", "chapter-04.md", "chapter-05.md", "chapter-06.md",
            "chapter-07.md", "chapter-08.md", "chapter-12.md", "chapter-15.md",
            "chapter-16.md", "chapter-21.md", "chapter-25.md", "chapter-26.md",
            "chapter-28.md", "chapter-30.md", "chapter-32.md", "chapter-34.md"]

for name in LF_FILES:
    path = os.path.join(CH, name)
    with io.open(path, encoding="utf-8", newline="") as fh:
        t = fh.read()
    t = t.replace("\r\n", "\n")
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(t)
    print("%s -> LF (%d lines)" % (name, t.count("\n")))
print("done")
