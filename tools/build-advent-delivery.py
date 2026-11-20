#!/usr/bin/env python3
"""Build the ebook delivery package for Advent Horror from the chapter sources.

Each door document carries its story's plate above the day number. The plates are the
same paintings the print interior uses, at 800 px wide for the ebook (the print set is
1024), so the file a reader downloads does not carry the press-resolution copy.


Same shape as build-parts-still-warm-delivery.py: no external dependencies, one
source of prose, an EPUB 3 container and a single-file manuscript.

  delivery/manuscript.md                    front matter + 24 doors + 24 stories
  delivery/ebook/advent-horror.epub          EPUB 3, cover, nav with 24 entries

Front matter is read from manuscript/front-matter.md, split on `<!-- pagebreak -->`
so there is one editable copy of the title and copyright pages. Theme lines are read
from the briefs, not retyped, so a door cannot disagree with the brief it came from.
"""

from pathlib import Path
import html
import re
import uuid
import zipfile
from datetime import datetime, timezone

BOOK = Path(__file__).resolve().parents[1] / "test-books" / "advent-horror"
DELIVERY = BOOK / "delivery"
CHAPTERS = sorted((BOOK / "manuscript" / "chapters").glob("chapter-*.md"))
FRONT = BOOK / "manuscript" / "front-matter.md"
AFTER = BOOK / "manuscript" / "afterword.md"
BIO = BOOK / "manuscript" / "about-the-author.md"
BRIEFS = BOOK / "manuscript" / "BRIEFS" / "ADVENT-BRIEFS.md"
COVER = DELIVERY / "print" / "cover-front.jpg"
ILLUS = BOOK / "art" / "illustrations" / "titled" / "ebook"

TITLE = "Terror Before Christmas"
SUBTITLE = ("A Horror Advent Calendar for Adults: 24 Terrifying Tales, "
            "One for Each Night Before Christmas")
AUTHOR = "Kalie Kirch"
LANG = "en-US"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "advent-horror"))
ON_SALE = "2026-12-01"
RIGHTS = "Copyright \u00a9 2026 Kalie Kirch. All rights reserved."
DESCRIPTION = ("Twenty-four standalone horror stories, one for every night from December 1 to "
               "Christmas Eve, in a book built as an advent calendar.")
SUBJECTS = ("Fiction / Horror", "Fiction / Short Stories (single author)", "Fiction / Holidays")

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
h1 { font-size: 1.5em; font-weight: normal; text-align: center; margin: 2em 0 0.2em; }
.chnum { text-align: center; letter-spacing: 0.3em; font-size: 0.8em; color: #555; margin: 0 0 2em; }
h2 { font-size: 1.05em; font-weight: normal; font-style: italic; margin: 1.6em 0 0.6em; }
p { margin: 0; text-indent: 1.4em; text-align: justify; }
hr { border: 0; border-top: 1px solid #bbb; margin: 2em 20%; }
.title { text-align: center; text-indent: 0; font-size: 2.1em; letter-spacing: 0.12em;
         margin: 3.2em 0 0.6em; }
.series, .author, .rule { text-align: center; text-indent: 0; margin: 0.5em 0; }
.series { font-style: italic; color: #444; }
.author { letter-spacing: 0.18em; margin-top: 2.4em; }
.copyright p { text-indent: 0; text-align: left; font-size: 0.85em; margin: 0 0 0.9em; }
.toc { list-style: none; padding: 0; }
.toc li { margin: 0 0 0.45em; text-indent: 0; }
.toc a { color: inherit; text-decoration: none; }
.toc .day { display: inline-block; width: 2.4em; color: #666; letter-spacing: 0.12em; }
.signoff { text-align: right; text-indent: 0; margin-top: 1.6em; }
.door { text-align: center; margin: 3em 0; }
.door .day { display: block; font-size: 2.6em;
             letter-spacing: 0.3em; color: #7a1b12; margin: 0 0 0.6em; }
.door .theme { display: block; font-style: italic; color: #333; margin: 1.4em auto 0;
               max-width: 22em; }
/* The plate carries the title as a title card, so the visible heading would print it twice.
   It stays in the document for screen readers, search and the table of contents. */
.door h1 { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0;
           overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
.plate { text-align: center; text-indent: 0; margin: 0 0 1.6em; }
.plate img { max-width: 100%; height: auto; }
.cover { margin: 0; padding: 0; text-align: center; }
.cover img { max-width: 100%; height: auto; }
"""


def clean(text):
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return "\n".join(l.rstrip() for l in text.splitlines()).strip() + "\n"


def smart(text):
    """Straight quotes from the sources become typographic ones.

    Typst does this for the print interior on its own, so without this the ebook would set
    "Thank you," with inch marks while the paperback sets curly ones.
    """
    out = []
    for i, ch in enumerate(text):
        prev = text[i - 1] if i else ""
        nxt = text[i + 1] if i + 1 < len(text) else ""
        # A quote after a dash is a closing one: the book interrupts dialogue with an em
        # dash ("It's not -") more often than it opens speech after one.
        if ch == '"':
            opening = not prev or prev.isspace() or prev in "([{"
            out.append("\u201c" if opening else "\u201d")
        elif ch == "'":
            if prev.isalnum() and nxt.isalnum():
                out.append("\u2019")
            elif not prev or prev.isspace() or prev in "([{":
                out.append("\u2018" if nxt.isalpha() else "\u2019")
            else:
                out.append("\u2019")
        else:
            out.append(ch)
    return "".join(out)


def inline(text):
    text = smart(html.escape(text, quote=False))
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)


def md_body(text, skip_h1=True):
    out, para = [], []

    def flush():
        if para:
            joined = " ".join(p.strip() for p in para).strip()
            if joined:
                out.append("<p>" + inline(joined) + "</p>")
            para.clear()

    for line in text.splitlines():
        if not line.strip():
            flush()
            continue
        if line.startswith("# "):
            flush()
            if not skip_h1:
                out.append("<h1>" + inline(line[2:].strip()) + "</h1>")
            continue
        if line.startswith("## "):
            flush()
            out.append("<h2>" + inline(line[3:].strip()) + "</h2>")
            continue
        if line.startswith("### "):
            flush()
            out.append("<p><strong>" + inline(line[4:].strip()) + "</strong></p>")
            continue
        if line.strip() in ("---", "***"):
            flush()
            out.append("<hr/>")
            continue
        if line.startswith(">> "):                 # right-aligned sign-off
            flush()
            out.append('<p class="signoff">' + inline(line[3:].strip()) + "</p>")
            continue
        para.append(line)
    flush()
    return "\n".join(out)


def heading(text):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def split_heading(h):
    m = re.match(r"^(\d+)\s*[-\u2013\u2014]\s*(.+)$", h)
    return (m.group(1), m.group(2)) if m else ("", h)


def themes():
    found = re.findall(r'\*\*Theme:\*\*\s*"(.+?)"', BRIEFS.read_text(encoding="utf-8"))
    if len(found) != 24:
        raise SystemExit("expected 24 theme lines in the briefs, found %d" % len(found))
    return {i: t for i, t in enumerate(found, start=1)}


def front_pages(contents_html):
    raw = FRONT.read_text(encoding="utf-8")
    blocks = [b.strip("\n") for b in raw.split("<!-- pagebreak -->")]
    if len(blocks) != 3:
        raise SystemExit("front-matter.md should have 3 pages, found %d" % len(blocks))
    title, copyright, contents = blocks
    # The contents block is HTML, not prose: inserting it before md_body escaped the tags and
    # printed the markup on the page. Keep the generated list raw, render the text around it.
    head, _, tail = contents.partition("<!-- contents -->")
    contents = (md_body(head) + "\n" + contents_html + "\n" + md_body(tail)).strip()
    return [
        ("Title Page", title_doc(title)),
        ("Copyright", '<section class="copyright" epub:type="copyright-page">\n'
                      + md_body(copyright) + "\n</section>"),
        ("Contents",
         '<nav epub:type="toc" id="toc">\n' + contents + "\n</nav>"),
    ]


def title_doc(block):
    paras = [p for p in block.splitlines() if p.strip()]
    out = ['<section epub:type="titlepage">']
    for line in paras:
        if line.startswith("# "):
            out.append('<p class="title">' + html.escape(line[2:].strip()) + "</p>")
        elif line.startswith("## "):
            out.append('<p class="series">' + html.escape(line[3:].strip()) + "</p>")
        elif line.startswith("### "):
            out.append('<p class="author">' + html.escape(line[4:].strip()) + "</p>")
        else:
            out.append('<p class="rule">' + inline(line) + "</p>")
    out.append("</section>")
    return "\n".join(out)


def build_epub(docs, nav_items, plates):
    out = DELIVERY / "ebook" / "advent-horror.epub"
    out.parent.mkdir(parents=True, exist_ok=True)

    has_cover = COVER.is_file()
    manifest = "\n".join(
        '    <item id="%s" href="%s" media-type="application/xhtml+xml"/>' % (i, fn)
        for i, fn, _, _ in docs)
    if plates:
        manifest = "\n".join(
            '    <item id="%s" href="%s" media-type="image/jpeg"/>' % (i, fn)
            for i, fn, _ in plates) + "\n" + manifest
    spine = "\n".join('    <itemref idref="%s"/>' % i for i, _, _, _ in docs)
    if has_cover:
        manifest = ('    <item id="cover_img" href="images/cover.jpg" '
                    'media-type="image/jpeg" properties="cover-image"/>\n'
                    '    <item id="cover_page" href="cover.xhtml" '
                    'media-type="application/xhtml+xml"/>\n') + manifest
        spine = '    <itemref idref="cover_page" linear="yes"/>\n' + spine

    subjects = "\n".join("    <dc:subject>%s</dc:subject>" % html.escape(s) for s in SUBJECTS)
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cover_meta = ('    <meta name="cover" content="cover_img"/>\n' if has_cover else "")

    opf = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{lang}" dir="ltr">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">{bookid}</dc:identifier>
    <dc:title id="t-main">{title}</dc:title>
    <dc:title id="t-sub">{subtitle}</dc:title>
    <meta refines="#t-main" property="title-type">main</meta>
    <meta refines="#t-sub" property="title-type">subtitle</meta>
    <dc:creator>{author}</dc:creator>
    <dc:language>{lang}</dc:language>
    <dc:date>{onsale}</dc:date>
    <dc:rights>{rights}</dc:rights>
    <dc:description>{desc}</dc:description>
{subjects}
{cover_meta}    <meta property="dcterms:modified">{modified}</meta>
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
""".format(lang=LANG, bookid=BOOK_ID, title=html.escape(TITLE),
           subtitle=html.escape(SUBTITLE), author=html.escape(AUTHOR),
           onsale=ON_SALE, rights=html.escape(RIGHTS), desc=html.escape(DESCRIPTION),
           subjects=subjects, cover_meta=cover_meta, modified=modified,
           manifest=manifest, spine=spine)

    nav_ol = "\n".join('      <li><a href="%s">%s</a></li>' % (fn, html.escape(label))
                       for fn, label in nav_items)
    nav = XHTML.format(lang=LANG, title="Contents", body=(
        '<nav epub:type="toc" id="toc">\n  <h1>Contents</h1>\n  <ol class="toc">\n'
        + nav_ol + "\n  </ol>\n</nav>"))

    container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

    cover_page = ('<section class="cover" epub:type="cover">\n'
                  '<img src="images/cover.jpg" alt="%s"/>\n</section>' % html.escape(TITLE))

    with zipfile.ZipFile(out, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/nav.xhtml", nav, zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, zipfile.ZIP_DEFLATED)
        if has_cover:
            z.write(COVER, "OEBPS/images/cover.jpg", zipfile.ZIP_DEFLATED)
            z.writestr("OEBPS/cover.xhtml",
                       XHTML.format(lang=LANG, title=html.escape(TITLE), body=cover_page),
                       zipfile.ZIP_DEFLATED)
        for _, fn, path in plates:
            z.write(path, "OEBPS/" + fn, zipfile.ZIP_DEFLATED)
        for i, fn, body, label in docs:
            z.writestr("OEBPS/" + fn,
                       XHTML.format(lang=LANG, title=html.escape(label), body=body),
                       zipfile.ZIP_DEFLATED)
    return out


def main():
    day_theme = themes()
    parts, manuscript = [], []
    words = em = spaced = 0
    for path in CHAPTERS:
        raw = clean(path.read_text(encoding="utf-8"))
        words += len(raw.split())
        em += raw.count("\u2014")
        spaced += raw.count(" - ")
        day, name = split_heading(heading(raw))
        if not day.isdigit():
            raise SystemExit("%s has no day number in its heading" % path.name)
        d = int(day)
        theme = day_theme[d]
        body = md_body(raw)
        chnum = '<p class="chnum">%s</p>\n' % html.escape(day)
        chapter = ('<section epub:type="chapter">\n<h1>%s</h1>\n%s%s\n</section>'
                   % (html.escape(name), chnum, body))
        plate = ('<div class="plate"><img src="images/ill-%02d.jpg" alt="%s"/>\n</div>\n'
                 % (d, html.escape("Illustration for Day %s: %s" % (day, name))))
        door = ('<section epub:type="part" class="door">\n' + plate
                + '<span class="day">%s</span>\n<h1 class="card-title">%s</h1>\n'
                '<span class="theme">%s</span>\n</section>'
                % (html.escape(day), html.escape(name), html.escape(theme)))
        parts.append((day, name, theme, door, chapter))
        manuscript.append("---\n\n## December %s\n\n*%s*\n\n%s" % (d, theme, raw.strip()))

    days = [int(p[0]) for p in parts]
    if days != list(range(1, 25)):
        raise SystemExit("days on disk are not 1..24: %s" % days)

    contents_html = '<ol class="toc">\n' + "\n".join(
        '<li><a href="door-%02d.xhtml"><span class="day">%s</span>%s</a></li>'
        % (n, html.escape(p[0]), html.escape(p[1]))
        for n, p in enumerate(parts, start=1)) + "\n</ol>"

    fm = front_pages(contents_html)
    docs = [("fm1", "frontmatter.xhtml", fm[0][1], "Title Page"),
            ("fm2", "copyright.xhtml", fm[1][1], "Copyright"),
            ("fm3", "contents.xhtml", fm[2][1], "Contents")]
    nav_items = [("frontmatter.xhtml", "Title Page"), ("contents.xhtml", "Contents")]
    for n, (day, name, theme, door, chapter) in enumerate(parts, start=1):
        docs.append(("d%02d" % n, "door-%02d.xhtml" % n, door, "Day %s. %s" % (day, name)))
        docs.append(("c%02d" % n, "ch-%02d.xhtml" % n, chapter, name))
        nav_items.append(("door-%02d.xhtml" % n, "Day %s. %s" % (day, name)))

    after_raw = ""
    if AFTER.is_file():
        after_raw = clean(AFTER.read_text(encoding="utf-8"))
        words += len(after_raw.split())
        docs.append(("aw", "afterword.xhtml",
                     '<section epub:type="afterword">\n<h1>Afterword</h1>\n'
                     + md_body(after_raw) + "\n</section>", "Afterword"))
        nav_items.append(("afterword.xhtml", "Afterword"))

    about_raw = ""
    if BIO.is_file():
        about_raw = clean(BIO.read_text(encoding="utf-8"))
        words += len(about_raw.split())
        docs.append(("ab", "about.xhtml",
                     '<section epub:type="biography">\n<h1>About the Author</h1>\n'
                     + md_body(about_raw) + "\n</section>", "About the Author"))
        nav_items.append(("about.xhtml", "About the Author"))

    plates = []
    for n, (day, name, theme, door, chapter) in enumerate(parts, start=1):
        path = ILLUS / ("%02d.jpg" % int(day))
        if path.is_file():
            plates.append(("ill%02d" % n, "images/ill-%02d.jpg" % n, path))
        else:
            raise SystemExit("plate missing for day %s: %s" % (day, path))

    epub = build_epub(docs, nav_items, plates)

    DELIVERY.mkdir(parents=True, exist_ok=True)
    front_raw = FRONT.read_text(encoding="utf-8").replace("<!-- contents -->", contents_html)
    front_raw = "\n\n---\n\n".join(b.strip() for b in front_raw.split("<!-- pagebreak -->"))
    (DELIVERY / "manuscript.md").write_text(
        re.sub(r"<a [^>]*>|</a>", "", front_raw)
        .replace("<ol class=\"toc\">", "").replace("</ol>", "")
        .replace("<li>", "- ").replace("</li>", "").replace('<span class="day">', "**")
        .replace("</span>", "** ")
        + "\n\n" + "\n\n".join(manuscript)
        + (("\n\n---\n\n## Afterword\n\n" + after_raw.strip()) if after_raw else "")
        + (("\n\n---\n\n## About the Author\n\n" + about_raw.strip()) if about_raw else "")
        + "\n", encoding="utf-8")

    size = epub.stat().st_size
    print("manuscript.md  %d words of chapters, 24 doors" % words)
    print("epub           %s  (%d bytes, %d documents)" % (epub, size, len(docs)))
    print("dashes         %d em, %d spaced hyphens" % (em, spaced))
    print("cover          %s" % ("included" if COVER.is_file() else "NOT INCLUDED"))
    print("plates         %d (%.1f MB of images)"
          % (len(plates), sum(p.stat().st_size for _, _, p in plates) / 1e6))


if __name__ == "__main__":
    main()
