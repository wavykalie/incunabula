#!/usr/bin/env python3
"""Typeset the Advent Horror print interior with Typst and measure it.

  delivery/print/interior.typ                 the generated typesetting source
  delivery/print/advent-horror-interior.pdf   5.5 x 8.5 in, no bleed, fonts embedded
  delivery/print/interior-meta.json           the measured extent, read by the cover build

Typst is reached through the `typst` Python package (pip install typst), so no
binary has to be on PATH; page count and trim are read back from the PDF with
pypdf. Both are pip dependencies of this script and of `tools/build-advent-cover.py`.

The extent written to interior-meta.json is the extent of the PDF written beside it.
The cover build reads that file, so the spine is never a guess about a book that
was not typeset.

One source of prose: the 24 chapter files and manuscript/front-matter.md, the same
files the EPUB is built from. Nothing here retypes a word of the book.

The title page sets the title in Creepster from tools/fonts (SIL OFL, licence beside the
font). Typst embeds every face it uses, and `measure()` below refuses to report a PDF whose
faces are not embedded, so the display face travels in the file KDP receives.
"""

from pathlib import Path
import json
import os
import re
import sys

import typst
import pypdf

BOOK = Path(__file__).resolve().parents[1] / "test-books" / "advent-horror"
OUT = BOOK / "delivery" / "print"
# The colour edition is the default and keeps its file names. The black-ink edition is
# typeset beside it from a graded plate set, with its own PDF and meta file, so neither
# artifact can overwrite the other:
#
#   ADVENT_PLATES=mono/print ADVENT_SUFFIX=-mono python tools/build-advent-interior.py
#
# Same prose, same plate dimensions, so the extent and the spine come out identical.
SUFFIX = os.environ.get("ADVENT_SUFFIX", "")
PLATES = os.environ.get("ADVENT_PLATES", "titled/print")
PDF = OUT / ("advent-horror-interior%s.pdf" % SUFFIX)
TYP = OUT / ("interior%s.typ" % SUFFIX)
META = OUT / ("interior-meta%s.json" % SUFFIX)
CHAPTERS = sorted((BOOK / "manuscript" / "chapters").glob("chapter-*.md"))
ILLUS = BOOK / "art" / "illustrations" / "titled" / "print"
FRONT = BOOK / "manuscript" / "front-matter.md"
AFTER = BOOK / "manuscript" / "afterword.md"
BIO = BOOK / "manuscript" / "about-the-author.md"
BRIEFS = BOOK / "manuscript" / "BRIEFS" / "ADVENT-BRIEFS.md"

TITLE = "Terror Before Christmas"
AUTHOR = "Kalie Kirch"
FONT = "Libertinus Serif"

# The title page carries a display face, not the body serif: a paperback's first page is
# allowed to shout, and the brief for this book is a Goosebumps-style logo. Creepster
# (SIL OFL, vendored with its licence under tools/fonts) is the closest open face to that
# hand-lettered, dripping lettering. Nosifer was rendered beside it and rejected: its
# ascenders and drips collide when three lines are stacked at book-page width.
DISPLAY = "Creepster"
FONTS = Path(__file__).resolve().parent / "fonts"
TITLE_W = 4.6      # display width in inches; 0.45in clear of each trim edge, inside KDP's 0.25in safe area

# 5.5 x 8.5 in, no bleed (text-only book; bleed would tell KDP to cut 0.125 in off nothing).
TRIM_W, TRIM_H = 5.5, 8.5
INSIDE, OUTSIDE, TOP, BOTTOM = 0.75, 0.5, 0.72, 0.8   # KDP gutter floor, 151-300 pp, is 0.5
FRONT_PAGES = 4                                       # title, copyright, contents, epigraph

TYPO_ESCAPE = set("\\#$*_`<>@~[]")


def fill(template, **tokens):
    for key, value in tokens.items():
        template = template.replace("@@%s@@" % key.upper(), str(value))
    return template


def typq(s):
    """A typst string literal."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ---------------------------------------------------------------- text conversion

def smart(text):
    """Straight quotes to curly.

    Double quotes toggle within a paragraph, which is what dialogue does. Reading only
    the preceding character gets interrupted speech backwards: in `"It's not \u2014"` the
    quote after the em dash closes, and a preceding-character rule calls it open. Six
    paragraphs in this manuscript do that, so the toggle is the rule that survives the
    text. Apostrophes read their own context.
    """
    out, opening = [], True
    for i, ch in enumerate(text):
        prev = text[i - 1] if i else " "
        nxt = text[i + 1] if i + 1 < len(text) else " "
        if ch == '"':
            out.append("\u201c" if opening else "\u201d")
            opening = not opening
        elif ch == "'":
            if prev.isalnum():
                out.append("\u2019")                   # don't, Ellen's, girls'
            elif nxt.isdigit():
                out.append("\u2019")                   # '90s
            elif nxt.isalnum():
                out.append("\u2018")                   # opening single quote
            else:
                out.append("\u2019")
        else:
            out.append(ch)
    return "".join(out)


def escape(text):
    return "".join("\\" + c if c in TYPO_ESCAPE else c for c in text)


def inline(text):
    """Markdown emphasis and typst escaping for one paragraph."""
    parts, pos = [], 0
    for m in re.finditer(r"\*\*(.+?)\*\*|\*(.+?)\*", text, flags=re.S):
        parts.append(escape(text[pos:m.start()]))
        if m.group(1) is not None:
            parts.append("#strong[" + escape(m.group(1)) + "]")
        else:
            parts.append("#emph[" + escape(m.group(2)) + "]")
        pos = m.end()
    parts.append(escape(text[pos:]))
    return "".join(parts)


def paragraphs(raw):
    """Split markdown prose into blocks, keeping scene breaks as @@@BREAK@@@."""
    blocks, cur = [], []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            if cur:
                blocks.append(" ".join(cur))
                cur = []
            continue
        if re.fullmatch(r"[*\u2014\u2013_\-]+", stripped) and len(stripped) >= 3:
            if cur:
                blocks.append(" ".join(cur))
                cur = []
            blocks.append("@@@BREAK@@@")
            continue
        if stripped.startswith("#"):
            continue
        cur.append(stripped)
    if cur:
        blocks.append(" ".join(cur))
    return blocks


def story_body(raw):
    out, first = [], True
    for block in paragraphs(raw):
        if block == "@@@BREAK@@@":
            out.append("#v(0.55em)#align(center)[#text(tracking: 0.9em)[\\* \\* \\*]]#v(0.55em)")
            first = True
            continue
        text = inline(smart(block))
        if first:
            out.append("#set par(first-line-indent: 0em)\n" + text
                       + "\n#set par(first-line-indent: 1.2em)")
            first = False
        else:
            out.append(text)
    return "\n\n".join(out)


def flat_body(raw):
    """Back matter: paragraphs with no first-line indent, and a right-aligned sign-off.

    A line beginning `>> ` is set flush right - that is how the afterword is signed, and
    the marker keeps the signature out of the prose without a second source file.
    """
    out = []
    for block in paragraphs(raw):
        if block == "@@@BREAK@@@":
            out.append("#v(0.6em)")
            continue
        if block.startswith(">> "):
            out.append("#align(right)[" + inline(smart(block[3:])) + "]")
            continue
        out.append(inline(smart(block)))
    return "\n\n".join(out)


def themes():
    found = re.findall(r'\*\*Theme:\*\*\s*"(.+?)"', BRIEFS.read_text(encoding="utf-8"))
    if len(found) != 24:
        raise SystemExit("expected 24 theme lines in the briefs, found %d" % len(found))
    return {i: t for i, t in enumerate(found, start=1)}


def split_heading(h):
    m = re.match(r"^(\d+)\s*[-\u2013\u2014]\s*(.+)$", h)
    if not m:
        raise SystemExit("chapter heading has no day number: %r" % h)
    return m.group(1), m.group(2)


# ---------------------------------------------------------------- typst templates

PREAMBLE = """
#set document(title: @@TITLE@@, author: @@AUTHOR@@)
#set text(font: @@FONT@@, size: 11pt, lang: "en", region: "us", hyphenate: true)
#set par(justify: true, leading: 0.66em, spacing: 0.9em, first-line-indent: 1.2em)

#let rt = state("rt", @@TITLE@@)

// A page carrying an <opener> marker gets no running head and no folio. Queried by
// label rather than read from a state, because a header is laid out before the page's
// own content and would never see a state the page itself updates.
#let is-opener-page(p) = query(selector(<opener>)).any(e => e.location().page() == p)

#set page(
  width: @@W@@in, height: @@H@@in,
  margin: (inside: @@INS@@in, outside: @@OUTS@@in, top: @@TOP@@in, bottom: @@BOT@@in),
  numbering: "i",
  header: context {
    let p = here().page()
    if p > @@FRONT@@ and not is-opener-page(p) {
      set text(size: 8.5pt, tracking: 0.14em, fill: luma(70))
      if calc.even(p) { align(center, upper(@@TITLE@@)) }
      else { align(center, upper(rt.get())) }
    }
  },
  footer: context {
    let p = here().page()
    if p > @@FRONT@@ and not is-opener-page(p) {
      set text(size: 9pt, fill: luma(55))
      align(center, counter(page).display())
    }
  },
)
"""

TITLE_PAGE = """
#page[
  #set par(justify: false, first-line-indent: 0em)
  #set text(hyphenate: false)   // a logo word must never be broken, whatever its width
  // The block spans 84% of the trim, so centring it on the text measure (0.75in inside,
  // 0.5in outside on this recto page) drifts it 0.125in right of optical centre and reads
  // as a misprint. The page is shifted back onto the trim centre instead.
  #move(dx: -0.125in)[
  #v(0.6in)
  // Each word is set at the size that makes the longest one span @@WIDTH@@in, so the block
  // is a solid slab of type that runs nearly edge to edge, the way a series logo does.
  // Every line is a box: unbreakable, so a word wider than the 4.25in text measure draws
  // into the margin instead of hyphenating. That is what keeps this one page on one page.
  // Spacing is slightly positive: the face fills its em box, and any tightening at all
  // overprints the ascenders of the line below.
  #context {
    let sz = 100pt * (@@WIDTH@@in / measure(text(font: @@DISPLAY@@, size: 100pt,
                                             tracking: 0.015em, @@LONGEST@@)).width)
    align(center, stack(dir: ttb, spacing: 0.02 * sz,
      ..(@@LINES@@).map(l => box(text(font: @@DISPLAY@@, size: sz, tracking: 0.015em, l)))))
  }
  #v(1.15in)
  #align(center, block(width: 86%, text(size: 10.5pt, style: "italic", fill: luma(60), @@SUB@@)))
  #v(0.6in)
  #align(center, text(size: 13pt, tracking: 0.22em, upper(@@AUTHOR@@)))
  ]
]
"""

COPYRIGHT = """
#page[
  #v(2.6in)
  #set text(size: 8.5pt, fill: luma(40))
  #set par(justify: false, first-line-indent: 0em, spacing: 0.65em)
  @@BODY@@
]
"""


def contents_page():
    """The contents is built from the <door> metadata, so it cannot drift from the book."""
    return """
#page[
  #v(0.9in)
  #align(center, text(size: 14pt, tracking: 0.24em, upper("Contents")))
  #v(0.55in)
  #set text(size: 9.5pt)
  #set par(first-line-indent: 0em, justify: false, spacing: 0.42em)
  #context {
    for e in query(selector(<door>)) {
      let dest = e.location()
      block(width: 100%,
        link(dest, text(fill: luma(110), size: 8.5pt)[#e.value.day])
        + h(0.9em) + link(dest, e.value.title)
        + h(1fr) + link(dest, text(fill: luma(70))[#counter(page).at(dest).first()]))
    }
  }
]
"""


EPIGRAPH = """
#page[
  #v(3in)
  #align(center, block(width: 84%,
    text(size: 10.5pt, style: "italic", fill: luma(45), @@TEXT@@)))
]
"""

# The afterword and the author bio are the back matter. Each opens on its own page, sets a little smaller than
# the stories, and takes the running head "Afterword", so a reader who turns to the end is not
# told they are still inside Day 24.
AFTERWORD = """
#rt.update("Afterword")
#page(header: none, footer: none)[
  #v(0.85in)
  #align(center, text(size: 14pt, tracking: 0.24em, upper("Afterword")))
  #v(0.5in)
  #set text(size: 10.5pt)
  #set par(first-line-indent: 0em, justify: true, leading: 0.72em, spacing: 0.85em)
  @@BODY@@
]
"""

# The bio closes the book: same setting as the afterword, its own page and its own running head,
# so the signature page cannot end up underneath a biography heading.
ABOUT = """
#rt.update("About the Author")
#page(header: none, footer: none)[
  #v(0.85in)
  #align(center, text(size: 14pt, tracking: 0.24em, upper("About the Author")))
  #v(0.5in)
  #set text(size: 10.5pt)
  #set par(first-line-indent: 0em, justify: true, leading: 0.72em, spacing: 0.85em)
  @@BODY@@
]
"""

DOOR = """
#page(header: none, footer: none)[
  #metadata((day: @@DAY@@, title: @@TITLE@@))<door>
  // The plate gets exactly the height the caption does not use, measured here rather than
  // estimated: a fixed reserve overflowed by a few points, which pushed the words of each
  // door onto a second page, took the extent from 172 to 196, and would have silently
  // respined the cover from the page count it reads.
  #v(0.18in)
  // Fixed, not measured: `measure` of a block that contains `set align` reports the whole
  // text area, not the caption, which collapsed the plate to a thumbnail. The title is set
  // into the plate itself (tools/burn-illustration-titles.py), so the caption is only
  // December, the day numeral and the theme; 0.18 + 4.25 + 0.26 + 1.40 = 6.09in against a
  // 6.98in text area, so no door can overflow into a second page. `verify()` below counts
  // 24 door pages, so a change to this number is caught rather than shipped.
  #align(center, image(@@IMAGE@@, height: 4.25in))
  #v(0.26in)
  #set align(center)
  #text(size: 8.5pt, tracking: 0.3em, fill: luma(90))[#upper("December")]
  #v(0.04in)
  // The day is a function argument, not a content block: in a content block the straight
  // quotes around it survive as typographic quotes and print as “‘01’”.
  #text(size: 30pt, fill: luma(25), @@DAY@@)
  #v(0.16in)
  #block(width: 80%, text(size: 9pt, style: "italic", fill: luma(60), @@THEME@@))
]
"""


def build_source(stories, front, extra_blank, afterword="", about=""):
    title_block, copyright_block, contents_block = front
    sub = re.search(r"^## (.+)$", title_block, flags=re.M)
    body = "\n\n".join(inline(smart(p)) for p in
                       re.split(r"\n\s*\n", copyright_block.strip()) if p.strip())
    note = [b for b in contents_block.split("---") if b.strip() and "<!-- contents -->" not in b]

    out = [fill(PREAMBLE, title=typq(TITLE), author=typq(AUTHOR), font=typq(FONT),
                w=TRIM_W, h=TRIM_H, ins=INSIDE, outs=OUTSIDE, top=TOP, bot=BOTTOM,
                front=FRONT_PAGES)]
    words = [w.upper() for w in TITLE.split()]
    out.append(fill(TITLE_PAGE, author=typq(AUTHOR), display=typq(DISPLAY),
                    width=TITLE_W, lines=", ".join(typq(w) for w in words),
                    longest=typq(max(words, key=len)),
                    sub=typq(smart(sub.group(1)) if sub else "")))
    out.append(fill(COPYRIGHT, body=body))
    out.append(contents_page())
    if note:
        out.append(fill(EPIGRAPH,
                        text=typq(" ".join(note[-1].replace("*", "").split()))))
    out.append('#set page(numbering: "1")\n#counter(page).update(1)')

    for day, title, theme, text in stories:
        # Relative to interior.typ (delivery/print), not to root: a "C:/..." path is a
        # path component Typst refuses. root=BOOK keeps the plate inside the sandbox.
        plate = "../../art/illustrations/%s/%s.jpg" % (PLATES, day)
        out.append(fill(DOOR, day=typq(day), title=typq(title), image=typq(plate),
                        theme=typq(" ".join(theme.split()))))
        out.append("#rt.update(%s)\n#metadata(none)<opener>\n\n%s" % (typq(title), text))

    if afterword:
        out.append(afterword)
    if about:
        out.append(about)
    if extra_blank:
        out.append("#page(header: none, footer: none)[]")
    return "\n".join(out)


# ---------------------------------------------------------------- measure

def measure(pdf_path):
    reader = pypdf.PdfReader(str(pdf_path))
    pages = len(reader.pages)
    box = reader.pages[0].mediabox
    trim = (round(float(box.width) / 72, 4), round(float(box.height) / 72, 4))

    fonts, embedded = {}, {}
    for page in reader.pages:
        res = page.get("/Resources")
        if not res or "/Font" not in res:
            continue
        for key in res["/Font"]:
            fo = res["/Font"][key].get_object()
            base = re.sub(r"^/[A-Z]{6}\+", "", str(fo.get("/BaseFont")))
            base = re.sub(r"-(Identity-H|Bold|Italic|Regular)$", "", base)
            fonts[base] = fonts.get(base, 0) + 1
            files = set()
            for holder in [fo] + [d.get_object() for d in fo.get("/DescendantFonts", [])]:
                desc = holder.get("/FontDescriptor")
                if desc:
                    desc = desc.get_object()
                    files |= {k for k in ("/FontFile", "/FontFile2", "/FontFile3") if k in desc}
            embedded[base] = embedded.get(base, False) or bool(files)
    return pages, trim, fonts, embedded


def verify(reader, titles):
    """Structural checks on the built PDF, so a silent layout regression cannot ship."""
    def page_text(n):
        return reader.pages[n - 1].extract_text() or ""

    toc = " ".join(page_text(3).split())
    missing = [t for t in titles if t not in toc]
    full = " ".join(page_text(i) for i in range(1, len(reader.pages) + 1))
    doors = sorted(i for i in range(1, len(reader.pages) + 1)
                   if "DECEMBER" in page_text(i).replace(" ", "").replace("\n", "")
                   and len(page_text(i)) < 300)
    return [
        ("contents lists 24 titles", not missing,
         "24/24" if not missing else "%d missing, first: %r" % (len(missing), missing[0])),
        ("24 door pages", len(doors) == 24, "%d found" % len(doors)),
        # The title is set one word per line in the display face; pypdf extracts the three
        # stacked runs with no separators, so the title is compared whitespace-stripped.
        ("title page", "TERRORBEFORECHRISTMAS" in re.sub(r"\s+", "", page_text(1).upper()),
         page_text(1).split("\n")[0][:30]),
        ("epigraph on page 4", page_text(4).strip().startswith("Every story is a door"),
         page_text(4).split("\n")[0][:30]),
        ("day 1 door on page 5", "DECEMBER" in page_text(5).replace(" ", "")[:60],
         page_text(5).split("\n")[1][:12] if len(page_text(5).split("\n")) > 1 else ""),
        ("first door follows front matter", doors[:1] == [5], str(doors[:1])),
        ("quotes balanced", full.count("\u201c") == full.count("\u201d"),
         "%d open / %d close" % (full.count("\u201c"), full.count("\u201d"))),
        # The sign-off proves the afterword survived pagination rather than being clipped by a
        # page template; the bio is checked for its own opening line for the same reason.
        ("afterword signed", any("November 2026" in " ".join(page_text(i).split())
                                 for i in range(1, len(reader.pages) + 1)),
         "found" if any("November 2026" in " ".join(page_text(i).split())
                       for i in range(1, len(reader.pages) + 1)) else "MISSING"),
        ("author bio", "second published book" in full,
         "found" if "second published book" in full else "MISSING"),
    ]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw_front = FRONT.read_text(encoding="utf-8")
    front = [b.strip("\n") for b in raw_front.split("<!-- pagebreak -->")]
    if len(front) != 3:
        raise SystemExit("front-matter.md should have 3 pages, found %d" % len(front))

    day_theme = themes()
    stories = []
    for path in CHAPTERS:
        raw = path.read_text(encoding="utf-8")
        first = raw.splitlines()[0]
        if not first.startswith("# "):
            raise SystemExit("%s has no heading" % path.name)
        day, title = split_heading(first[2:].strip())
        stories.append((day, title, day_theme[int(day)], story_body(raw)))
    if [int(s[0]) for s in stories] != list(range(1, 25)):
        raise SystemExit("days on disk are not 1..24")

    afterword = ""
    if AFTER.is_file():
        afterword = fill(AFTERWORD, body=flat_body(AFTER.read_text(encoding="utf-8")))
    about = ""
    if BIO.is_file():
        about = fill(ABOUT, body=flat_body(BIO.read_text(encoding="utf-8")))

    extra_blank = False
    for _ in range(2):
        TYP.write_text(build_source(stories, front, extra_blank, afterword, about),
                       encoding="utf-8")
        # root=BOOK: the plates live in ../../art, outside the .typ file's own folder.
        typst.compile(str(TYP), output=str(PDF), font_paths=[str(FONTS)], root=str(BOOK))
        pages, trim, fonts, embedded = measure(PDF)
        if pages % 2 == 0:
            break
        extra_blank = True          # KDP prints sheet counts in even numbers; match it

    checks = verify(pypdf.PdfReader(str(PDF)), [s[1] for s in stories])
    for label, ok, detail in checks:
        print("%-26s %s  %s" % (label, "PASS" if ok else "FAIL", detail))

    words = sum(len(p.read_text(encoding="utf-8").split()) for p in CHAPTERS)
    for back in (AFTER, BIO):                 # the book's count includes the back matter
        if back.is_file():
            words += len(back.read_text(encoding="utf-8").split())
    meta = {
        "pdf": PDF.name,
        "pages": pages,
        "trim_in": list(trim),
        "margins_in": {"inside": INSIDE, "outside": OUTSIDE, "top": TOP, "bottom": BOTTOM},
        "words": words,
        "words_per_page": round(words / pages, 1),
        "fonts": sorted(fonts),
        "fonts_embedded": all(embedded.values()),
        "final_blank_page": extra_blank,
        "typesetter": "typst %s" % getattr(typst, "__version__", "?"),
        "checks": {label: ok for label, ok, _ in checks},
    }
    META.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    print("interior   %s" % PDF)
    print("pages      %d  %s" % (pages, "even" if pages % 2 == 0 else "ODD"))
    print("trim       %.3f x %.3f in (no bleed)" % trim)
    print("words      %d  (%.1f per page)" % (words, words / pages))
    print("fonts      %s" % ", ".join(sorted(fonts)))
    print("embedded   %s" % ("all" if all(embedded.values()) else
                             "MISSING: " + ", ".join(k for k, v in embedded.items() if not v)))
    print("spine      %d x 0.002252 = %.4f in (%.2f mm) white paper"
          % (pages, pages * 0.002252, pages * 0.002252 * 25.4))
    return 0 if all(embedded.values()) and all(ok for _, ok, _ in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
