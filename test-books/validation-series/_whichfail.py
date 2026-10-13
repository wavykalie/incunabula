import io, os, subprocess, glob

INC = "C:/Users/screa/incunabula/tools/prose/deslop-check.sh"
for book in ("book-1", "book-2"):
    B = "C:/Users/screa/incunabula/test-books/validation-series/%s/manuscript/chapters" % book
    print("##########", book)
    for f in sorted(glob.glob(B + "/chapter-*.md")):
        out = subprocess.run(["bash", INC, f], capture_output=True, text=True).stdout
        fails = [l.strip() for l in out.splitlines() if "FAIL" in l]
        if fails:
            print("  %-14s %s" % (os.path.basename(f), " | ".join(
                x.split(None, 1)[1][:70] for x in fails)))
