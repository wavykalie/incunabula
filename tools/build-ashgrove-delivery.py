#!/usr/bin/env python3
"""Build the Ashgrove Inventory delivery files from the chapter sources.

No external dependencies. The EPUB is a valid, simple EPUB 3 container; the
print HTML is a 6 x 9 in document intended for Chrome's --print-to-pdf.
"""

from pathlib import Path
import html
import re
import uuid
import zipfile

BOOK = Path(__file__).resolve().parents[1] / "test-books" / "ashgrove-inventory"
DELIVERY = BOOK / "delivery"
CHAPTERS = sorted((BOOK / "manuscript" / "chapters").glob("chapter-*.md"))
TITLE = "The Ashgrove Inventory"
SUBTITLE = "A novel in six documents"
AUTHOR = "Bastorius Quinn"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "ashgrove-inventory"))

NARROW = (
    "I stood within the opening, with one foot at the room edge\n"
    "of the reveal and the other against the brick jamb.\n\n"
    "The reveal extended from my heel to the\n"
    "edge of the brickwork ahead of me.\n\n"
    "My toe remained on\n"
    "the brick of the\n"
    "threshold."
)
NARROW_HTML = (
    '<div class="narrow">'
    '<p class="n1">I stood within the opening, with one foot at the room edge of the reveal and the other against the brick jamb.</p>'
    '<p class="n2">The reveal extended from my heel to the edge of the brickwork ahead of me.</p>'
    '<p class="n3">My toe remained on the brick of the threshold.</p>'
    '</div>'
)


def clean(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("<!-- layer:") or stripped == "<!-- /layer -->":
            continue
        lines.append(line.rstrip())
    text = "\n".join(lines).strip() + "\n"
    return text.replace("--", "—")


def chapter_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = text.replace("`", "")
    return text


def film_block(lines):
    return '<pre class="film">' + html.escape("\n".join(lines), quote=False) + "</pre>"


def md_to_html(text: str) -> str:
    text = text.replace(NARROW, "[[NARROW]]")
    out = []
    para = []
    i = 0
    lines = text.splitlines()

    def flush():
        nonlocal para
        if not para:
            return
        joined = " ".join(s.strip() for s in para).strip()
        if joined:
            if joined == "[[NARROW]]":
                out.append(NARROW_HTML)
            else:
                out.append("<p>" + inline(joined) + "</p>")
        para = []

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            flush()
            i += 1
            continue
        if line.startswith("# "):
            flush()
            out.append("<h1>" + inline(line[2:].strip()) + "</h1>")
            i += 1
            continue
        if line.startswith("## "):
            flush()
            out.append("<h2>" + inline(line[3:].strip()) + "</h2>")
            i += 1
            continue
        if line.startswith("REEL "):
            flush()
            block = [line]
            i += 1
            while i < len(lines) and lines[i].strip():
                block.append(lines[i])
                i += 1
            out.append(film_block(block))
            continue
        para.append(line)
        i += 1
    flush()
    return "\n".join(out)


def xhtml(title: str, body: str) -> str:
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n'
        '<head><meta charset="utf-8"/><title>' + html.escape(title) + '</title>'
        '<link rel="stylesheet" type="text/css" href="../style.css"/></head>\n'
        '<body>\n' + body + '\n</body></html>\n'
    )


def build_manuscript(chapters):
    parts = [
        "# THE ASHGROVE INVENTORY",
        "### " + SUBTITLE,
        "",
        "by " + AUTHOR,
        "",
        "---",
        "",
        "**Test-book delivery.** Author: Bastorius Quinn. No ISBN or rights are assigned. "
        "This edition exists to test the delivery path, not for sale.",
        "",
        "---",
        "",
        "## Contents",
        "",
    ]
    for n, (path, text) in enumerate(chapters, 1):
        parts.append(f"{n}. {chapter_title(text)}")
    parts += ["", "---", ""]
    for path, text in chapters:
        parts += [text.strip(), "", "---", ""]
    parts += [
        "## A note on the text",
        "",
        "The survey is set in roman; the film logs are monospaced; the annotations are "
        "first-person and present. The print edition sets the noun *house* in a second "
        "colour in the survey layer, and the chapter-four threshold passage uses a "
        "three-step narrowing block. No page-numbering trick is used.",
        "",
        "The Ashgrove Inventory is a test-book delivery of 8,807 words in six document "
        "clusters. It is not a market submission.",
        "",
    ]
    (DELIVERY / "manuscript.md").write_text("\n".join(parts), encoding="utf-8")


def build_print(chapters):
    pieces = []
    for n, (path, text) in enumerate(chapters, 1):
        pieces.append(f'<section class="chapter" id="ch{n}">')
        pieces.append(md_to_html(clean(text)))
        pieces.append("</section>")
    title_page = (
        '<section class="titlepage">'
        f'<h1>{html.escape(TITLE)}</h1>'
        f'<p class="subtitle">{html.escape(SUBTITLE)}</p>'
        f'<p class="author">{html.escape(AUTHOR)}</p>'
        '<p class="testnotice">Test-book delivery. Not for sale.</p>'
        '</section>'
    )
    body = title_page + "\n" + "\n".join(pieces)
    css = """
@page { size: 6in 9in; margin: 0.85in 0.70in 0.85in 0.80in; }
html, body { margin: 0; padding: 0; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 10.5pt; line-height: 1.45; color: #111; }
h1 { font-size: 18pt; text-align: center; font-weight: normal; margin: 0 0 1.4em; page-break-before: always; }
h2 { font-size: 12pt; text-align: center; font-weight: normal; }
p { margin: 0; text-indent: 1.25em; text-align: justify; }
h1 + p { text-indent: 0; }
.film { font-family: 'Courier New', monospace; font-size: 9pt; line-height: 1.35; white-space: pre-wrap; margin: 1em 0; text-align: left; }
.narrow { width: 60%; margin: 1.4em auto; }
.narrow p { text-indent: 0; text-align: left; }
.narrow .n1 { width: 100%; }
.narrow .n2 { width: 66%; }
.narrow .n3 { width: 33%; }
section.chapter { page-break-after: always; }
.titlepage { text-align: center; padding-top: 2.4in; }
.titlepage h1 { page-break-before: avoid; font-size: 26pt; margin-bottom: 0.4em; }
.titlepage .subtitle { text-indent: 0; text-align: center; font-size: 12pt; margin-bottom: 2em; }
.titlepage .author { text-indent: 0; text-align: center; font-size: 14pt; letter-spacing: 0.08em; }
.titlepage .testnotice { text-indent: 0; text-align: center; font-size: 9pt; margin-top: 3em; }
"""
    doc = (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>'
        f'<meta name="author" content="{html.escape(AUTHOR)}"/>'
        f"<title>{html.escape(TITLE)}</title><style>{css}</style></head><body>\n"
        + body
        + "\n</body></html>\n"
    )
    (DELIVERY / "print").mkdir(exist_ok=True)
    (DELIVERY / "print" / "ashgrove-inventory.html").write_text(doc, encoding="utf-8")


def build_epub(chapters):
    epub_dir = DELIVERY / "ebook"
    epub_dir.mkdir(exist_ok=True)
    files = {}
    files["META-INF/container.xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
        "</rootfiles></container>\n"
    )
    files["OEBPS/style.css"] = (
        "body { font-family: Georgia, serif; line-height: 1.5; margin: 1em; }\n"
        "h1 { text-align: center; font-size: 1.5em; font-weight: normal; margin: 2em 0 1.2em; }\n"
        "p { margin: 0; text-indent: 1.25em; text-align: justify; }\n"
        "h1 + p { text-indent: 0; }\n"
        ".film { font-family: monospace; white-space: pre-wrap; font-size: 0.9em; }\n"
        ".narrow { width: 70%; margin: 1.4em auto; }\n"
        ".narrow p { text-indent: 0; text-align: left; }\n"
        ".narrow .n1 { width: 100%; } .narrow .n2 { width: 70%; } .narrow .n3 { width: 38%; }\n"
        ".title { text-align: center; margin-top: 25%; }\n"
        ".title h1 { font-size: 2em; margin-bottom: 0.3em; }\n"
        ".title p { text-indent: 0; text-align: center; }\n"
        ".copyright { font-size: 0.9em; }\n"
    )
    title_body = (
        '<div class="title"><h1>' + html.escape(TITLE) + "</h1>"
        "<p>" + html.escape(SUBTITLE) + "</p><p>by " + html.escape(AUTHOR) + "</p></div>"
        '<div class="copyright"><p>Test-book delivery. Author: Bastorius Quinn. No ISBN or rights are assigned. '
        "This edition exists to test the delivery path, not for sale.</p></div>"
    )
    files["OEBPS/text/title.xhtml"] = xhtml(TITLE, title_body)

    nav_items = []
    spine = ['<itemref idref="title"/>']
    manifest = [
        '<item id="title" href="text/title.xhtml" media-type="application/xhtml+xml"/>',
        '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '<item id="css" href="style.css" media-type="text/css"/>',
    ]
    for n, (path, text) in enumerate(chapters, 1):
        cid = f"ch{n:02d}"
        files[f"OEBPS/text/{cid}.xhtml"] = xhtml(chapter_title(text), md_to_html(clean(text)))
        manifest.append(f'<item id="{cid}" href="text/{cid}.xhtml" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{cid}"/>')
        nav_items.append(f'<li><a href="text/{cid}.xhtml">{html.escape(chapter_title(text))}</a></li>')
    back_body = (
        "<h1>A note on the text</h1>"
        "<p>The survey is set in roman; the film logs are monospaced; the annotations are "
        "first-person and present. The print edition sets the noun <em>house</em> in a second "
        "colour in the survey layer, and the chapter-four threshold passage uses a three-step "
        "narrowing block. No page-numbering trick is used.</p>"
        "<p>This is a test-book delivery of 8,807 words in six document clusters. It is not a "
        "market submission.</p>"
    )
    files["OEBPS/text/back.xhtml"] = xhtml("A note on the text", back_body)
    manifest.append('<item id="back" href="text/back.xhtml" media-type="application/xhtml+xml"/>')
    spine.append('<itemref idref="back"/>')

    nav_body = (
        '<nav epub:type="toc" id="toc" xmlns:epub="http://www.idpf.org/2007/ops">'
        "<h1>Contents</h1><ol>" + "".join(nav_items) + "</ol></nav>"
    )
    files["OEBPS/nav.xhtml"] = xhtml("Contents", nav_body)
    files["OEBPS/content.opf"] = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        f'<dc:identifier id="bookid">{BOOK_ID}</dc:identifier>'
        f"<dc:title>{html.escape(TITLE)}</dc:title>"
        f"<dc:creator>{html.escape(AUTHOR)}</dc:creator>"
        "<dc:language>en</dc:language>"
        "<dc:description>A novel in six documents.</dc:description>"
        '<meta property="dcterms:modified">2026-11-07T00:00:00Z</meta>'
        "</metadata><manifest>" + "".join(manifest) + "</manifest><spine>" + "".join(spine) + "</spine></package>\n"
    )
    files["OEBPS/toc.ncx"] = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
        f'<head><meta name="dtb:uid" content="{BOOK_ID}"/></head>'
        f"<docTitle><text>{html.escape(TITLE)}</text></docTitle><navMap>"
        + "".join(
            f'<navPoint id="np{n}" playOrder="{n}"><navLabel><text>{html.escape(chapter_title(text))}</text></navLabel>'
            f'<content src="text/ch{n:02d}.xhtml"/></navPoint>'
            for n, (path, text) in enumerate(chapters, 1)
        )
        + "</navMap></ncx>\n"
    )

    out = epub_dir / "ashgrove-inventory.epub"
    with zipfile.ZipFile(out, "w") as z:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        z.writestr(info, "application/epub+zip")
        for name, data in files.items():
            z.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)


def main():
    DELIVERY.mkdir(exist_ok=True)
    chapters = [(path, clean(path.read_text(encoding="utf-8"))) for path in CHAPTERS]
    build_manuscript(chapters)
    build_print(chapters)
    build_epub(chapters)
    print(f"built {len(chapters)} chapters")
    print(DELIVERY / "manuscript.md")
    print(DELIVERY / "print" / "ashgrove-inventory.html")
    print(DELIVERY / "ebook" / "ashgrove-inventory.epub")


if __name__ == "__main__":
    main()
