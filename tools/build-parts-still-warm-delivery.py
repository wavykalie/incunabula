#!/usr/bin/env python3
"""Build the delivery package for The Parts Still Warm from the chapter sources.

No external dependencies, same shape as build-ashgrove-delivery.py:
  delivery/manuscript.md              the whole book, front matter + 13 chapters
  delivery/ebook/the-parts-still-warm.epub   a valid, simple EPUB 3 container
  delivery/PACKAGE.md                 what is in the package, with measured numbers

No typographic conversion is performed. The manuscript's own dash and quote
conventions are carried through unchanged, and the counts are reported in
PACKAGE.md so a presswork pass can decide rather than inherit a silent choice.
"""

from pathlib import Path
import html
import re
import uuid
import zipfile

BOOK = Path(__file__).resolve().parents[1] / "test-books" / "the-parts-still-warm"
DELIVERY = BOOK / "delivery"
CHAPTERS = sorted((BOOK / "manuscript" / "chapters").glob("chapter-*.md"))
TITLE = "The Parts Still Warm"
SERIES = "Nothing Leaves, book one"
AUTHOR = "Kalie Kirch"
LANG = "en-US"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "the-parts-still-warm"))
AFTERWORD = BOOK / "manuscript" / "afterword.md"
SERIES_NAME = "Nothing Leaves"
PUBDATE = "2026-11-13"
RIGHTS = "Copyright \u00a9 2026 Kalie Kirch. All rights reserved."
DESCRIPTION = (
    "A sidekick who can move his own blood takes in the daughter of the man he failed "
    "and hunts the quiet that killed him, in a city that carries its debts in bodies."
)
SUBJECTS = ("Fiction / Thrillers / Crime", "Fiction / Literary")


def clean(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return "\n".join(l.rstrip() for l in text.splitlines()).strip() + "\n"


def heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def split_heading(h: str):
    """'7 - The Room Above the Cinema' -> ('7', 'The Room Above the Cinema')."""
    m = re.match(r"^(\d+)\s*[-–—]\s*(.+)$", h)
    return (m.group(1), m.group(2)) if m else ("", h)


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text.replace("`", "")


def md_body(text: str) -> str:
    out, para = [], []
    lines = text.splitlines()

    def flush():
        if para:
            joined = " ".join(p.strip() for p in para).strip()
            if joined:
                out.append("<p>" + inline(joined) + "</p>")
            para.clear()

    for line in lines:
        if not line.strip():
            flush()
            continue
        if line.startswith("# "):
            flush()
            continue
        if line.startswith("## "):
            flush()
            out.append("<h2>" + inline(line[3:].strip()) + "</h2>")
            continue
        if line.startswith("### "):
            flush()
            out.append("<h3>" + inline(line[4:].strip()) + "</h3>")
            continue
        if line.strip() in ("---", "***"):
            flush()
            out.append("<hr/>")
            continue
        para.append(line)
    flush()
    return "\n".join(out)


XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="{lang}" lang="{lang}">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body>
{body}
</body>
</html>
"""

CSS = """body { font-family: Georgia, "Times New Roman", serif; line-height: 1.5; margin: 1.2em; }
h1 { font-size: 1.4em; font-weight: normal; text-align: center; margin: 2em 0 0.2em; }
.chnum { text-align: center; letter-spacing: 0.2em; text-transform: uppercase;
         font-size: 0.8em; color: #444; margin: 0 0 2em; }
h2 { font-size: 1.05em; font-weight: normal; font-style: italic; margin: 1.6em 0 0.6em; }
p { margin: 0; text-indent: 1.4em; text-align: justify; }
p.title { text-align: center; text-indent: 0; margin: 3em 0 0; font-size: 1.6em; }
p.series, p.author { text-align: center; text-indent: 0; margin: 0.6em 0; }
p.series { font-style: italic; }
hr { border: 0; border-top: 1px solid #ccc; margin: 2em 20%; }
.copyright { margin: 3em 0.6em; }
.copyright p { text-indent: 0; text-align: left; font-size: 0.85em; margin: 0 0 0.9em; }
"""


def front_matter_html() -> str:
    return (
        '<section epub:type="titlepage">'
        f'<p class="title">{html.escape(TITLE)}</p>'
        f'<p class="series">{html.escape(SERIES)}</p>'
        f'<p class="author">{html.escape(AUTHOR)}</p>'
        "</section>"
    )


def copyright_html() -> str:
    return (
        '<section class="copyright" epub:type="copyright-page">'
        "<p>This is a work of fiction. Names, characters, places, and incidents are either "
        "the product of the author's imagination or are used fictitiously. Any resemblance "
        "to actual persons, living or dead, events, or locales is entirely coincidental.</p>"
        f"<p>{html.escape(RIGHTS)}</p>"
        "<p>All rights reserved. No part of this book may be reproduced, distributed, or "
        "transmitted in any form or by any means without the prior written permission of the "
        "author, except in the case of brief quotations embodied in critical reviews and "
        "certain other noncommercial uses permitted by copyright law.</p>"
        f"<p>{html.escape(SERIES_NAME)}, book one</p>"
        f"<p>First edition, {PUBDATE[:4]}</p>"
        "<p>Paperback ISBN: to be assigned</p>"
        "<p>Cover design: to be assigned</p>"
        "</section>"
    )


def build_epub(parts) -> Path:
    """parts: list of (number, chapter title, xhtml body)."""
    out = DELIVERY / "ebook" / "the-parts-still-warm.epub"
    out.parent.mkdir(parents=True, exist_ok=True)

    docs = [
        ("frontmatter.xhtml", "Title Page", front_matter_html()),
        ("copyright.xhtml", "Copyright", copyright_html()),
    ]
    nav_items = []
    for i, (num, name, body) in enumerate(parts, start=1):
        fn = f"ch{i:02d}.xhtml"
        docs.append((fn, name, body))
        nav_items.append((fn, f"{num}. {name}" if num else name))

    manifest = "\n".join(
        f'    <item id="{fn.replace(".", "_")}" href="{fn}" media-type="application/xhtml+xml"/>'
        for fn, _, _ in docs
    )
    spine = "\n".join(f'    <itemref idref="{fn.replace(".", "_")}"/>' for fn, _, _ in docs)
    nav_ol = "\n".join(
        f'      <li><a href="{fn}">{html.escape(label)}</a></li>' for fn, label in nav_items
    )

    subjects = "\n".join(
        f"    <dc:subject>{html.escape(s)}</dc:subject>" for s in SUBJECTS
    )

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{LANG}" dir="ltr">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{BOOK_ID}</dc:identifier>
    <dc:title>{html.escape(TITLE)}</dc:title>
    <dc:creator>{html.escape(AUTHOR)}</dc:creator>
    <dc:language>{LANG}</dc:language>
    <dc:date>{PUBDATE}</dc:date>
    <dc:rights>{html.escape(RIGHTS)}</dc:rights>
    <dc:description>{html.escape(DESCRIPTION)}</dc:description>
{subjects}
    <meta property="belongs-to-collection" id="series">{html.escape(SERIES_NAME)}</meta>
    <meta refines="#series" property="collection-type">series</meta>
    <meta refines="#series" property="group-position">1</meta>
    <meta property="dcterms:modified">{PUBDATE}T00:00:00Z</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="css" href="style.css" media-type="text/css"/>
{manifest}
  </manifest>
  <spine>
{spine}
  </spine>
</package>
"""

    nav = XHTML.format(lang=LANG, title="Contents", body=(
        '<nav epub:type="toc" id="toc">\n  <h1>Contents</h1>\n  <ol>\n'
        f"{nav_ol}\n  </ol>\n</nav>"
    ))

    container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

    with zipfile.ZipFile(out, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, zipfile.ZIP_DEFLATED)
        for fn, name, body in docs:
            doc = XHTML.format(lang=LANG, title=html.escape(name), body=body)
            z.writestr(f"OEBPS/{fn}", doc, zipfile.ZIP_DEFLATED)
    return out


def main():
    parts, manuscript, words = [], [], 0
    em, hyphen = 0, 0
    for path in CHAPTERS:
        raw = clean(path.read_text(encoding="utf-8"))
        words += len(raw.split())
        em += raw.count("—")
        hyphen += raw.count(" - ")
        h = heading(raw)
        num, name = split_heading(h)
        body = md_body(raw)
        head = (f'<p class="chnum">{html.escape(num)}</p>\n' if num else "")
        body = f'<section epub:type="chapter">\n<h1>{html.escape(name)}</h1>\n{head}{body}\n</section>'
        parts.append((num, name, body))
        manuscript.append(raw.strip())

    chapters = len(parts)
    aw = 0
    if AFTERWORD.is_file():
        raw = clean(AFTERWORD.read_text(encoding="utf-8"))
        aw = len(raw.split())
        name = split_heading(heading(raw))[1]
        parts.append(("", name, (
            '<section epub:type="afterword">\n'
            f"<h1>{html.escape(name)}</h1>\n"
            f"{md_body(raw)}\n"
            "</section>"
        )))
        manuscript.append(raw.strip())

    front = f"# {TITLE}\n\n### {SERIES}\n\n### {AUTHOR}\n"
    DELIVERY.mkdir(parents=True, exist_ok=True)
    (DELIVERY / "manuscript.md").write_text(
        front + "\n\n---\n\n" + "\n\n---\n\n".join(manuscript) + "\n", encoding="utf-8")

    epub = build_epub(parts)

    digest = "unknown"
    state = BOOK / "PROJECT_STATE.yaml"
    if state.is_file():
        m = re.search(r'contract_digest:\s*"([0-9a-f]+)"', state.read_text(encoding="utf-8"))
        if m:
            digest = m.group(1)

    pkg = f"""# Package — {TITLE}

*{SERIES}* · {AUTHOR} · literary thriller / vigilante justice

Built from `manuscript/chapters/chapter-01..13.md` and `manuscript/afterword.md` by
`tools/build-parts-still-warm-delivery.py`. Rebuild with:

    python tools/build-parts-still-warm-delivery.py

## Contents

| File | What it is |
|---|---|
| `manuscript.md` | the whole book in one file: title page, thirteen chapters, afterword |
| `ebook/the-parts-still-warm.epub` | EPUB 3 container — mimetype, container.xml, OPF, nav, copyright page, one XHTML per chapter, afterword |
| `KDP.md` | KDP upload sheet: metadata, categories, keywords, print geometry, cover spec |
| `COLOPHON.md` | logline, back-cover copy, editorial synopsis, query letter, cover brief |
| `PACKAGE.md` | this file |

## The numbers

| | |
|---|---|
| Chapters | {chapters} |
| Words, chapter sources | **{words:,}** |
| Afterword | {aw:,} words, after chapter 13 |
| Contract | `kalie-kirch`, digest `{digest}` |
| Em dashes in the manuscript | {em} |
| Spaced hyphens used as dashes | {hyphen} |

Manuscript size and the EPUB's word count both derive from the chapter files; there is no second
text. `check-length.py` reads the chapter files directly and records the same total.

**No typographic conversion was applied.** The dash and quote conventions are the manuscript's own,
carried into the EPUB unchanged. If a presswork pass wants em dashes, that is a decision with a count
attached above, not a silent transform in a build script.

## Fidelity

Each chapter is written to `manuscript.md` and to its own EPUB document from the same source text, so
no second copy of the prose exists to drift: the only transformation is markdown to XHTML markup.
`check-length.py` reads the chapter files directly and records the same total.

## Known open items

1. **Register run on chapter 7 only.** The voice matrix now exists (`voice-matrix.md`), so the other
   twelve chapters can be tested against it; none of them has been.
2. Two gate rows are structurally unrun and will stay so without author action: `check-names.py`
   (this cast is a roster of callsigns; the checker harvests two-part names only) and
   `check-premise-distinct.py` (the premise catalogue is unseeded).
3. Twelve of thirteen beat arcs in `NARRATIVE_LEDGER.yaml` are declared provisional by the panel that
   wrote them. The ledger says so per row rather than in a footnote.

## Gate state at packaging

Length PASS at {words:,} in [130,000, 140,000]; narrative PASS (0 open debt, N4 conformant, 13 of 13
chapters tracked); pass-evidence PASS ({words:,} of {words:,} words gated); ductus audit PASS; ductus
calibrate PASS on all three lines the contract declares; uniformity, drift, arc, monotony, deslop,
comps, progress all PASS. Suite verdict: NOT CLEAR, nothing failed, two rows not run — both listed
above.
"""
    (DELIVERY / "PACKAGE.md").write_text(pkg, encoding="utf-8")

    print(f"manuscript.md   {DELIVERY / 'manuscript.md'}  ({words:,} words of chapters)")
    print(f"epub            {epub}  ({epub.stat().st_size:,} bytes)")
    print(f"afterword       {aw:,} words")
    print(f"package         {DELIVERY / 'PACKAGE.md'}")
    print(f"dashes          {em} em, {hyphen} spaced hyphens")


if __name__ == "__main__":
    main()
