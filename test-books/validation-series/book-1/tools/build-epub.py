#!/usr/bin/env python3
"""
build-epub.py - build an EPUB 3 for Book 1 from the markdown manuscript.

Standard library only (zipfile, re, html, uuid, datetime). No Calibre, no pandoc, no dependencies.

Usage:
    python tools/build-epub.py [--out dist]

Design notes
------------
* The `mimetype` entry is written FIRST and STORED (uncompressed) because the OCF spec requires it.
  Everything else is DEFLATE.
* Both an EPUB 3 `nav.xhtml` and an EPUB 2 `toc.ncx` are emitted, because Kindle/KDP pipelines and
  older readers vary in which they honour.
* No `dc:creator` is emitted. The author has not been named for this build and inventing one would be
  worse than omitting it. Add it here when a name exists.
* The title is the working title. Titles are DEFERRED by the author; this script must not invent one.
"""

import argparse
import datetime
import html
import os
import re
import uuid
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TITLE = "Merope"
SUBTITLE = "Book One"
LANG = "en"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "codebuff/validation-series/book-1"))

# chapter file -> label. Eleven chapters, not seven: four of the seven were cut at a
# natural seam when the manuscript was re-chaptered to break its uniform lengths.
CHAPTERS = [
    ("chapter-01", "arrival"),
    ("chapter-02", "the welcome, from two sides"),
    ("chapter-03", "she is happy here"),
    ("chapter-04", "the same morning twice"),
    ("chapter-05", "things that did not grow"),
    ("chapter-06", "the belongings"),
    ("chapter-07", "what the beings are"),
    ("chapter-08", "everyone who came here died here"),
    ("chapter-09", "the refusal"),
    ("chapter-10", "leaving"),
    ("chapter-11", "the acknowledgement"),
]

CSS = """@charset "utf-8";
body { font-family: Georgia, "Iowan Old Style", "Palatino Linotype", serif;
       line-height: 1.5; margin: 0 5%; text-align: left; }
h1 { font-size: 2em; font-weight: normal; letter-spacing: 0.06em;
     margin: 3em 0 0.2em; text-align: center; }
h2 { font-size: 1.2em; font-weight: normal; letter-spacing: 0.08em;
     margin: 2.5em 0 0.1em; text-align: center; }
p.label { font-size: 0.85em; font-style: italic; text-align: center;
          color: #666; margin: 0 0 2.5em; }
p.sub { text-align: center; font-size: 1.1em; margin: 0 0 3em; }
p.note { font-size: 0.8em; color: #666; text-align: center; margin: 4em 1em 0; }
p { margin: 0; text-indent: 1.4em; }
p.first { text-indent: 0; }
hr { border: 0; border-top: 1px solid #ccc; width: 30%; margin: 3em auto; }
"""


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def smartify(text):
    """Straight quotes to typographic quotes. Conservative and per-paragraph."""
    text = text.replace("...", "\u2026")
    text = re.sub(r"(?<=\w)'(?=\w)", "\u2019", text)  # don't -> don't
    out, opening = [], True
    for ch in text:
        if ch == '"':
            out.append("\u201c" if opening else "\u201d")
            opening = not opening
        else:
            out.append(ch)
    return "".join(out)


def paragraphs(md_path):
    raw = strip_comments(open(md_path, encoding="utf-8").read())
    blocks = [b.strip() for b in re.split(r"\n\s*\n", raw)]
    return [b for b in blocks if b]


def to_xhtml(body, title, extra_head=""):
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
        'xml:lang="%s" lang="%s">\n<head>\n<meta charset="utf-8"/>\n<title>%s</title>\n'
        '<link rel="stylesheet" type="text/css" href="style.css"/>\n%s</head>\n<body>\n%s\n</body>\n</html>\n'
        % (LANG, LANG, html.escape(title), extra_head, body)
    )


def chapter_xhtml(md_path, number, label):
    paras = paragraphs(md_path)
    out = ['<h2>Chapter %d</h2>' % number, '<p class="label">%s</p>' % html.escape(label)]
    for i, block in enumerate(paras):
        cls = ' class="first"' if i == 0 else ""
        out.append("<p%s>%s</p>" % (cls, html.escape(smartify(block))))
    return to_xhtml("\n".join(out), "Chapter %d" % number)


def title_xhtml():
    # The reader sees the book, not the pipeline. The working-title status is a
    # production fact and lives in RUN_REPORT.md; it does not belong on a title page.
    # This note used to be emitted on every book, in near-identical words.
    body = (
        "<h1>%s</h1>\n<p class=\"sub\">%s</p>\n"
        % (html.escape(TITLE), html.escape(SUBTITLE))
    )
    return to_xhtml(body, TITLE)


def nav_xhtml():
    items = "\n".join(
        '<li><a href="%s.xhtml">Chapter %d &#8212; %s</a></li>' % (cid, i + 1, html.escape(label))
        for i, (cid, label) in enumerate(CHAPTERS)
    )
    body = (
        '<nav epub:type="toc" id="toc">\n<h1>Contents</h1>\n<ol>\n%s\n</ol>\n</nav>\n'
        '<nav epub:type="landmarks" id="landmarks" hidden="hidden">\n<h1>Landmarks</h1>\n<ol>\n'
        '<li><a epub:type="bodymatter" href="chapter-01.xhtml">Start</a></li>\n</ol>\n</nav>'
        % items
    )
    return to_xhtml(body, "Contents")


def ncx_xhtml():
    points = "\n".join(
        '    <navPoint id="n%d" playOrder="%d"><navLabel><text>Chapter %d</text></navLabel>'
        '<content src="%s.xhtml"/></navPoint>' % (i + 1, i + 1, i + 1, cid)
        for i, (cid, _) in enumerate(CHAPTERS)
    )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="%s">\n'
        '  <head><meta name="dtb:uid" content="%s"/><meta name="dtb:depth" content="1"/>'
        '<meta name="dtb:totalPageCount" content="0"/>'
        '<meta name="dtb:maxPageNumber" content="0"/></head>\n'
        '  <docTitle><text>%s</text></docTitle>\n  <navMap>\n%s\n  </navMap>\n</ncx>\n'
        % (LANG, BOOK_ID, html.escape(TITLE), points)
    )


def content_opf(modified):
    manifest = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '<item id="css" href="style.css" media-type="text/css"/>',
        '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>',
    ]
    spine = ['<itemref idref="title"/>', '<itemref idref="nav" linear="no"/>']
    for i, (cid, _) in enumerate(CHAPTERS):
        manifest.append(
            '<item id="%s" href="%s.xhtml" media-type="application/xhtml+xml"/>' % (cid, cid)
        )
        spine.append('<itemref idref="%s"/>' % cid)
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" '
        'xml:lang="%s">\n'
        '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        '    <dc:identifier id="bookid">%s</dc:identifier>\n'
        '    <dc:title>%s</dc:title>\n'
        '    <dc:language>%s</dc:language>\n'
        '    <meta property="dcterms:modified">%s</meta>\n'
        '  </metadata>\n'
        '  <manifest>\n    %s\n  </manifest>\n'
        '  <spine toc="ncx">\n    %s\n  </spine>\n</package>\n'
        % (
            LANG,
            BOOK_ID,
            html.escape(TITLE),
            LANG,
            modified,
            "\n    ".join(manifest),
            "\n    ".join(spine),
        )
    )


CONTAINER = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
    '  <rootfiles>\n'
    '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
    "  </rootfiles>\n</container>\n"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    args = ap.parse_args()

    modified = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    chapdir = os.path.join(ROOT, "manuscript", "chapters")
    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, "merope-book-one_WORKING-TITLE.epub")

    files = {"OEBPS/style.css": CSS}
    files["OEBPS/title.xhtml"] = title_xhtml()
    files["OEBPS/nav.xhtml"] = nav_xhtml()
    files["OEBPS/toc.ncx"] = ncx_xhtml()
    files["OEBPS/content.opf"] = content_opf(modified)
    for i, (cid, label) in enumerate(CHAPTERS):
        md = os.path.join(chapdir, cid + ".md")
        if not os.path.exists(md):
            raise SystemExit("missing chapter source: %s" % md)
        files["OEBPS/%s.xhtml" % cid] = chapter_xhtml(md, i + 1, label)

    with zipfile.ZipFile(out_path, "w") as z:
        # mimetype MUST be first and stored.
        z.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", CONTAINER, zipfile.ZIP_DEFLATED)
        for name in sorted(files):
            z.writestr(name, files[name], zipfile.ZIP_DEFLATED)

    size = os.path.getsize(out_path)
    print("wrote %s (%d bytes, %d entries)" % (out_path, size, len(files) + 2))
    return out_path


if __name__ == "__main__":
    main()
