#!/usr/bin/env python3
"""
build-epub.py - build the EPUB 3 for the manuscript in this project.

Standard library only (zipfile, re, html, uuid, datetime). No Calibre, no pandoc.

Usage:
    python tools/build-epub.py [--out dist]

Design notes
------------
* `mimetype` is written FIRST and STORED (uncompressed) - the OCF spec requires it.
  Everything else is DEFLATE.
* Both an EPUB 3 `nav.xhtml` and an EPUB 2 `toc.ncx` are emitted, because reader
  pipelines differ in which they honour.
* TITLE and the chapter labels are WORKING TITLES. The author has deferred the real
  titles, so this script must not invent one. No dc:creator is emitted for the same
  reason: inventing an author would be worse than omitting one.
* The prose-gate scan is NOT run here. It is run by tools/deslop-check.sh and its result
  is recorded in RUN_REPORT.md. This builder does not decide whether the book is fit to
  ship; it only packages it.

It also writes manuscript/full-manuscript.md, which is a GENERATED concatenation of the
chapter files. Do not edit that file by hand; edit the chapters.
"""

import argparse
import datetime
import html
import os
import re
import uuid
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TITLE = "Sons of Heaven, Students of Dust"
SUBTITLE = "Eleven Rulers and the Philosophers Who Explained Them"
LANG = "en"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "codebuff/incunabula-test/sons-of-heaven"))

# chapter file -> title. Fifteen chapters, not eleven: the two chapters carrying the
# most material (the Qin and the Tang collapse) were each cut into three at a natural
# seam when the manuscript was re-chaptered to break its uniform chapter lengths.
CHAPTERS = [
    ("chapter-01", "One Axle-Width"),
    ("chapter-02", "The Book Burn"),
    ("chapter-03", "What He Left Standing"),
    ("chapter-04", "Two Men at the Edge of a Ravine"),
    ("chapter-05", "The Historian's Silence"),
    ("chapter-06", "The Usurper Who Read the Classics"),
    ("chapter-07", "A Poet Among Warlords"),
    ("chapter-08", "The Emperor Who Fed the Monks"),
    ("chapter-09", "The Canal and the Gate of Examinations"),
    ("chapter-10", "The Mirror and the Minister"),
    ("chapter-11", "The Woman Who Became Son of Heaven"),
    ("chapter-12", "Interlude: A Man Drinking on a Mountain"),
    ("chapter-13", "The Golden Age and the General Who Ended It"),
    ("chapter-14", "The Poem with the Child in the Middle"),
    ("chapter-15", "The Age of the Literati"),
]

CSS = """@charset "utf-8";
body { font-family: Georgia, "Iowan Old Style", "Palatino Linotype", serif;
       line-height: 1.55; margin: 0 5%; text-align: left; }
h1 { font-size: 1.9em; font-weight: normal; letter-spacing: 0.04em;
     margin: 3em 0 0.2em; text-align: center; }
h2 { font-size: 1.15em; font-weight: normal; letter-spacing: 0.06em;
     margin: 2.5em 0 0.1em; text-align: center; }
p.label { font-size: 0.85em; font-style: italic; text-align: center;
          color: #666; margin: 0 0 2.5em; }
p.sub { text-align: center; font-size: 1.05em; margin: 0 0 2.5em; }
p.note { font-size: 0.8em; color: #666; text-align: center; margin: 3em 1em 0; }
p { margin: 0; text-indent: 1.4em; }
p.first { text-indent: 0; }
blockquote { margin: 1.4em 2em; font-style: italic; }
hr { border: 0; border-top: 1px solid #ccc; width: 30%; margin: 3em auto; }
"""


def strip_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def smartify(text):
    """Straight quotes to typographic quotes. Conservative and per-block."""
    text = text.replace("...", "\u2026")
    text = re.sub(r"(?<=\w)'(?=\w)", "\u2019", text)
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


def inline(text):
    """Escape, then re-apply the manuscript's two inline conventions: *italic* and `code`."""
    text = html.escape(smartify(text))
    text = re.sub(r"\*([^*\n]+)\*", r"<em>\1</em>", text)
    text = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", text)
    return text


def block_html(block):
    if block.startswith(">"):
        inner = " ".join(l.lstrip("> ").strip() for l in block.splitlines())
        return "<blockquote><p>%s</p></blockquote>" % inline(inner)
    return "<p>%s</p>" % inline(block.replace("\n", " "))


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
        rendered = block_html(block)
        if i == 0:
            rendered = rendered.replace("<p>", '<p class="first">', 1)
        out.append(rendered)
    return to_xhtml("\n".join(out), "Chapter %d" % number)


def title_xhtml():
    # The reader sees the book, not the pipeline.
    #
    # This used to emit a note explaining that the titles were provisional. It emitted
    # that note on every book this pipeline produced, in near-identical words, which is
    # how two unrelated genres ended up carrying the same front matter. A production
    # fact belongs in the project's own files (RUN_REPORT.md), where the working-title
    # status is now recorded; it does not belong on a title page.
    #
    # The absence of an author name is deliberate and is still enforced by simply not
    # emitting dc:creator. Inventing one would be worse than omitting it.
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
    for cid, _ in CHAPTERS:
        manifest.append('<item id="%s" href="%s.xhtml" media-type="application/xhtml+xml"/>' % (cid, cid))
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
        % (LANG, BOOK_ID, html.escape(TITLE), LANG, modified,
           "\n    ".join(manifest), "\n    ".join(spine))
    )


CONTAINER = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
    '  <rootfiles>\n'
    '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
    "  </rootfiles>\n</container>\n"
)


def write_full_manuscript(chapdir):
    """Generate the concatenated manuscript. GENERATED - do not edit by hand."""
    out = [
        "# %s" % TITLE,
        "*%s*" % SUBTITLE,
        "> GENERATED FILE. Concatenated from `manuscript/chapters/` by "
        "`tools/build-epub.py`. Edit the chapter files, not this one.",
        "---",
    ]
    for cid, label in CHAPTERS:
        out.append("## Chapter %s — %s" % (cid.split("-")[1], label))
        out.append(open(os.path.join(chapdir, cid + ".md"), encoding="utf-8").read().strip())
        out.append("---")
    path = os.path.join(ROOT, "manuscript", "full-manuscript.md")
    open(path, "w", encoding="utf-8").write("\n\n".join(out) + "\n")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    args = ap.parse_args()

    modified = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    chapdir = os.path.join(ROOT, "manuscript", "chapters")
    os.makedirs(args.out, exist_ok=True)
    slug = "sons-of-heaven-students-of-dust_WORKING-TITLE.epub"
    out_path = os.path.join(args.out, slug)

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

    fm = write_full_manuscript(chapdir)
    size = os.path.getsize(out_path)
    print("wrote %s (%d bytes, %d entries)" % (out_path, size, len(files) + 2))
    print("wrote %s" % fm)
    return out_path


if __name__ == "__main__":
    main()
