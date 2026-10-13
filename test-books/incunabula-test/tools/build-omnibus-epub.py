#!/usr/bin/env python3
"""
build-omnibus-epub.py - build ONE EPUB 3 containing both books of the validation series.

Reads the markdown manuscripts of book-1/ and book-2/ and emits a single file with a
two-level table of contents (book -> chapter). Standard library only, same conventions as
the per-book builders in book-1/tools and book-2/tools.

Usage:
    python tools/build-omnibus-epub.py [--out dist]

Design notes
------------
* The `mimetype` entry is written FIRST and STORED (uncompressed); the OCF spec requires it.
  Everything else is DEFLATE.
* Both an EPUB 3 `nav.xhtml` and an EPUB 2 `toc.ncx` are emitted, with nested entries so the
  two books appear as distinct sections.
* No `dc:creator` is emitted. The author has not been named for this build.
* Titles are DEFERRED by the author. This script must not invent one; the working title and
  the provisional chapter labels are carried through from the per-book builders.
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
SUBTITLE = "Books One and Two"
LANG = "en"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "codebuff/validation-series/omnibus"))

# (book dir, spine id, part subtitle, production note, [(chapter file, working label), ...])
#
# The production note is a RECORD, not copy: it states which titles are still working
# titles. It is deliberately never printed. It was printed once, on the title page and
# again on every part page, which is how one pipeline shipped the same front matter on
# books in different genres. Working-title status belongs in RUN_REPORT.md.
BOOKS = [
    (
        "book-1",
        "book1",
        "Book One",
        "Working title. The series name, the book title and the chapter titles have not been set.",
        [
            ("chapter-01", "arrival"),
            ("chapter-02", "the welcome, from two sides"),
            ("chapter-03", "she is happy here"),
            ("chapter-04", "the belongings"),
            ("chapter-05", "what the beings are"),
            ("chapter-06", "the refusal"),
            ("chapter-07", "leaving, and the acknowledgement"),
        ],
    ),
    (
        "book-2",
        "book2",
        "Book Two",
        "Working title. The series name, the book title and the chapter titles have not been set. "
        "Book two of two; the first book is not required, but it is the other half of the argument.",
        [
            ("chapter-01", "the handover"),
            ("chapter-02", "every part of it"),
            ("chapter-03", "what everyone calls it"),
            ("chapter-04", "someone leaves"),
            ("chapter-05", "why everyone came"),
            ("chapter-06", "the test, and the answer"),
            ("chapter-07", "giving it back"),
        ],
    ),
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
    text = re.sub(r"(?<=\w)'(?=\w)", "\u2019", text)  # don't -> don’t
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


def chapter_xhtml(md_path, book_subtitle, number, label):
    paras = paragraphs(md_path)
    out = [
        '<h2>%s &#183; Chapter %d</h2>' % (html.escape(book_subtitle), number),
        '<p class="label">%s</p>' % html.escape(label),
    ]
    for i, block in enumerate(paras):
        cls = ' class="first"' if i == 0 else ""
        out.append("<p%s>%s</p>" % (cls, html.escape(smartify(block))))
    return to_xhtml("\n".join(out), "%s Chapter %d" % (book_subtitle, number))


def title_xhtml():
    # The reader sees the book, not the pipeline. Production facts - which titles are
    # settled, which edition this is - belong in the project's own files, not on a title
    # page. See the design notes at the top of this file for the status of these titles.
    body = (
        "<h1>%s</h1>\n<p class=\"sub\">%s</p>\n"
        % (html.escape(TITLE), html.escape(SUBTITLE))
    )
    return to_xhtml(body, TITLE)


def part_xhtml(book_subtitle):
    body = (
        "<h1>%s</h1>\n<p class=\"sub\">%s</p>\n"
        % (html.escape(TITLE), html.escape(book_subtitle))
    )
    return to_xhtml(body, (TITLE + " \u2014 " + book_subtitle).strip())


def book_entries():
    """Yield (spine_id, filename, display_title, label) for every chapter, plus book headers."""
    entries = []
    for book_dir, spine, subtitle, _note, chapters in BOOKS:
        for i, (cid, label) in enumerate(chapters):
            sid = "%s-%s" % (spine, cid)
            entries.append(
                {
                    "book_dir": book_dir,
                    "spine": spine,
                    "subtitle": subtitle,
                    "sid": sid,
                    "file": "%s.xhtml" % sid,
                    "number": i + 1,
                    "cid": cid,
                    "label": label,
                }
            )
    return entries


def nav_xhtml(entries):
    by_book = {}
    for e in entries:
        by_book.setdefault(e["spine"], []).append(e)

    sections = []
    for book_dir, spine, subtitle, _note, _chapters in BOOKS:
        items = "\n".join(
            '      <li><a href="%s">Chapter %d &#8212; %s</a></li>'
            % (e["file"], e["number"], html.escape(e["label"]))
            for e in by_book[spine]
        )
        sections.append(
            '    <li><a href="%s.xhtml">%s</a>\n      <ol>\n%s\n      </ol>\n    </li>'
            % (spine + "-title", html.escape(subtitle), items)
        )
    body = (
        '<nav epub:type="toc" id="toc">\n<h1>Contents</h1>\n<ol>\n%s\n</ol>\n</nav>\n'
        '<nav epub:type="landmarks" id="landmarks" hidden="hidden">\n<h1>Landmarks</h1>\n<ol>\n'
        '<li><a epub:type="bodymatter" href="%s">Start</a></li>\n</ol>\n</nav>'
        % ("\n".join(sections), entries[0]["file"])
    )
    return to_xhtml(body, "Contents")


def ncx_xhtml(entries):
    by_book = {}
    for e in entries:
        by_book.setdefault(e["spine"], []).append(e)

    order = 0
    points = []
    for book_dir, spine, subtitle, _note, _chapters in BOOKS:
        order += 1
        children = []
        for e in by_book[spine]:
            order += 1
            children.append(
                '        <navPoint id="%s" playOrder="%d"><navLabel><text>Chapter %d &#8212; %s'
                '</text></navLabel><content src="%s"/></navPoint>'
                % (e["sid"], order, e["number"], html.escape(e["label"]), e["file"])
            )
        points.append(
            '    <navPoint id="%s" playOrder="%d"><navLabel><text>%s</text></navLabel>'
            '<content src="%s-title.xhtml"/>\n%s\n    </navPoint>'
            % (spine, order - len(children), html.escape(subtitle), spine, "\n".join(children))
        )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="%s">\n'
        '  <head><meta name="dtb:uid" content="%s"/><meta name="dtb:depth" content="2"/>'
        '<meta name="dtb:totalPageCount" content="0"/>'
        '<meta name="dtb:maxPageNumber" content="0"/></head>\n'
        '  <docTitle><text>%s</text></docTitle>\n  <navMap>\n%s\n  </navMap>\n</ncx>\n'
        % (LANG, BOOK_ID, html.escape(TITLE), "\n".join(points))
    )


def content_opf(entries, modified):
    manifest = [
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '<item id="css" href="style.css" media-type="text/css"/>',
        '<item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>',
    ]
    spine = ['<itemref idref="title"/>', '<itemref idref="nav" linear="no"/>']
    for book_dir, s, _sub, _note, _ch in BOOKS:
        manifest.append(
            '<item id="%s-title" href="%s-title.xhtml" media-type="application/xhtml+xml"/>' % (s, s)
        )
        spine.append('<itemref idref="%s-title"/>' % s)
    for e in entries:
        manifest.append(
            '<item id="%s" href="%s" media-type="application/xhtml+xml"/>' % (e["sid"], e["file"])
        )
        spine.append('<itemref idref="%s"/>' % e["sid"])
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
            html.escape("%s: %s" % (TITLE, SUBTITLE)),
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
    entries = book_entries()
    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, "merope-validation-series_omnibus_WORKING-TITLE.epub")

    files = {"OEBPS/style.css": CSS}
    files["OEBPS/title.xhtml"] = title_xhtml()
    files["OEBPS/nav.xhtml"] = nav_xhtml(entries)
    files["OEBPS/toc.ncx"] = ncx_xhtml(entries)
    files["OEBPS/content.opf"] = content_opf(entries, modified)
    for book_dir, spine, subtitle, _note, _chapters in BOOKS:
        files["OEBPS/%s-title.xhtml" % spine] = part_xhtml(subtitle)
    for e in entries:
        md = os.path.join(ROOT, e["book_dir"], "manuscript", "chapters", e["cid"] + ".md")
        if not os.path.exists(md):
            raise SystemExit("missing chapter source: %s" % md)
        files["OEBPS/%s" % e["file"]] = chapter_xhtml(
            md, e["subtitle"], e["number"], e["label"]
        )

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
