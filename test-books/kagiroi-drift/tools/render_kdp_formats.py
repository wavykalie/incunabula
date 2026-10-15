#!/usr/bin/env python3
"""
render_kdp_formats.py - Generate Amazon KDP-optimized DOCX and EPUB for 'Kagiroi Drift'.

Produces:
  1. delivery/formatted/kagiroi-drift.docx (6x9 Trade Paperback & Kindle-ready Word document)
  2. delivery/formatted/kagiroi-drift.epub (EPUB 3 / EPUB 2 Dual-compatible Kindle eBook)
  3. Mirror copy in C:/Users/screa/incunabula/test-books/epubs/kagiroi-drift.epub

Features:
  - Clean text-only presentation: no cover image, no internal pipeline or engine metadata.
  - Smart typography: curly quotes, proper apostrophes, em-dashes, ellipses.
  - Full front matter: Half Title, Title Page, Copyright/Colophon, Table of Contents.
  - Accurate body styling: unindented first paragraphs, 0.25in indented body paragraphs,
    proper scene break ornaments (* * *), preserved italics and bold.
  - Full back matter: Story notes and thematic nomenclature glossary.
  - Strict Amazon KDP standards for Kindle eBook conversion and KDP Print-on-Demand.
"""
# --- paths derived from this file, not from the machine that ran it ----------------
# The run happened at C:/Users/screa/incunabula; a clone is somewhere else, so walk up
# until the repository root (the directory holding tools/prose/) is found.
import os


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isdir(os.path.join(d, "tools", "prose")):
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return d


REPO = _repo_root()

import os
import re
import html
import uuid
import datetime
import zipfile
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BOOK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.dirname(BOOK_DIR)
DELIVERY_DIR = os.path.join(BOOK_DIR, "delivery", "formatted")

TITLE = "Kagiroi Drift"
KANJI_TITLE = "陽炎ドリフト"
SUBTITLE = "A Yuri Space-Salvage Novel"
LANG = "en"
BOOK_UUID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "kdp/kagiroi-drift/2026"))

CHAPTER_METADATA = [
    ("chapter-01", "Chapter 1", "The Cold Weld"),
    ("chapter-02", "Chapter 2", "Acoustic Shunt"),
    ("chapter-03", "Chapter 3", "The Ghost Skiff"),
    ("chapter-04", "Chapter 4", "Thermal Breach"),
    ("chapter-05", "Chapter 5", "The Unburied"),
    ("chapter-06", "Chapter 6", "The Inertial Burn"),
    ("chapter-07", "Chapter 7", "The Trap in the Quiet"),
    ("chapter-08", "Chapter 8", "Kagiroi Dawn"),
]

def smartify(text):
    """Typographic polish: straight to curly quotes, apostrophes, ellipses, em-dashes."""
    text = text.replace("...", "\u2026")
    text = text.replace(" -- ", " \u2014 ").replace("--", "\u2014")
    # Apostrophes in contractions/possessives
    text = re.sub(r"(\w)'(\w)", "\\1\u2019\\2", text)
    # Slang leading apostrophes
    text = re.sub(r"(^|[\s\(\[\{])'(em|cause|til|bout|round|gainst)\b", "\\1\u2019\\2", text, flags=re.I)
    # Double quotes: opening
    text = re.sub(r'(^|[\s\(\[\{\u2014\u2013])"', "\\1\u201c", text)
    # Double quotes: closing
    text = text.replace('"', '\u201d')
    # Single quotes: opening
    text = re.sub(r'(^|[\s\(\[\{\u2014\u2013])\'', "\\1\u2018", text)
    # Single quotes: closing
    text = text.replace("'", '\u2019')
    return text

def parse_inlines(text):
    """Tokenize markdown inlines: bold, italic, code, normal."""
    pattern = re.compile(r'(\*\*\*[^*\n]+\*\*\*|\*\*[^*\n]+\*\*|\*[^*\n]+\*|`[^`\n]+`)')
    parts = pattern.split(text)
    result = []
    for p in parts:
        if not p:
            continue
        if p.startswith("***") and p.endswith("***"):
            result.append(("bold_italic", p[3:-3]))
        elif p.startswith("**") and p.endswith("**"):
            result.append(("bold", p[2:-2]))
        elif p.startswith("*") and p.endswith("*"):
            result.append(("italic", p[1:-1]))
        elif p.startswith("`") and p.endswith("`"):
            result.append(("code", p[1:-1]))
        else:
            result.append(("normal", p))
    return result

def load_chapter_blocks(cid):
    chap_path = os.path.join(BOOK_DIR, "manuscript", "chapters", f"{cid}.md")
    with open(chap_path, "r", encoding="utf-8") as f:
        raw = f.read()
    raw_paras = [p.strip() for p in raw.split("\n\n") if p.strip()]
    blocks = []
    for p in raw_paras:
        if p.startswith("#"):
            continue  # chapter title handled separately
        elif p in ("***", "* * *", "---", "___"):
            blocks.append(("break", "*   *   *"))
        else:
            clean = " ".join(line.strip() for line in p.splitlines())
            blocks.append(("para", clean))
    return blocks

# ==============================================================================
# 1. DOCX GENERATION (Amazon KDP 6"x9" Trade Format)
# ==============================================================================

def add_bookmark(paragraph, bookmark_id, bookmark_name):
    bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{bookmark_id}" w:name="{bookmark_name}"/>')
    bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{bookmark_id}"/>')
    paragraph._p.insert(0, bm_start)
    paragraph._p.append(bm_end)

def add_toc_hyperlink(paragraph, text, target_bookmark):
    hyperlink = parse_xml(f'<w:hyperlink {nsdecls("w")} w:anchor="{target_bookmark}"/>')
    r = parse_xml(
        f'<w:r {nsdecls("w")}><w:rPr><w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/><w:sz w:val="22"/>'
        f'<w:color w:val="1a1a1a"/></w:rPr><w:t xml:space="preserve">{html.escape(text)}</w:t></w:r>'
    )
    hyperlink.append(r)
    paragraph._p.append(hyperlink)

def add_page_number_field(run):
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)

def generate_kdp_docx(out_path):
    doc = Document()
    
    # 6" x 9" Trim Size - Amazon KDP Standard Trade
    section = doc.sections[0]
    section.page_width = Inches(6.0)
    section.page_height = Inches(9.0)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)   # Gutter
    section.right_margin = Inches(0.60)  # Outside
    section.different_first_page_header_footer = True

    # Base Normal Style
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Georgia'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = RGBColor(0x1a, 0x1a, 0x1a)
    style_normal.paragraph_format.line_spacing = 1.18
    style_normal.paragraph_format.space_before = Pt(0)
    style_normal.paragraph_format.space_after = Pt(0)

    # Footer with Page Number
    footer = section.footer
    footer_p = footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_run = footer_p.add_run()
    footer_run.font.name = 'Georgia'
    footer_run.font.size = Pt(9.5)
    footer_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    add_page_number_field(footer_run)

    # -------------------------------------------------------------
    # FRONT MATTER: Half Title
    # -------------------------------------------------------------
    p_half = doc.add_paragraph()
    p_half.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_half.paragraph_format.space_before = Pt(140)
    run_half = p_half.add_run(TITLE.upper())
    run_half.font.name = 'Georgia'
    run_half.font.size = Pt(20)
    run_half.font.bold = True
    run_half.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    doc.add_page_break()

    # -------------------------------------------------------------
    # FRONT MATTER: Full Title Page
    # -------------------------------------------------------------
    p_t1 = doc.add_paragraph()
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1.paragraph_format.space_before = Pt(120)
    p_t1.paragraph_format.space_after = Pt(10)
    run_t1 = p_t1.add_run(TITLE.upper())
    run_t1.font.name = 'Georgia'
    run_t1.font.size = Pt(26)
    run_t1.font.bold = True

    p_t2 = doc.add_paragraph()
    p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t2.paragraph_format.space_before = Pt(0)
    p_t2.paragraph_format.space_after = Pt(22)
    run_t2 = p_t2.add_run(KANJI_TITLE)
    run_t2.font.name = 'Georgia'
    run_t2.font.size = Pt(15)
    run_t2.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(0)
    run_sub = p_sub.add_run(SUBTITLE)
    run_sub.font.name = 'Georgia'
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    doc.add_page_break()

    # -------------------------------------------------------------
    # FRONT MATTER: Copyright & Legal
    # -------------------------------------------------------------
    p_c1 = doc.add_paragraph()
    p_c1.paragraph_format.space_before = Pt(180)
    p_c1.paragraph_format.space_after = Pt(10)
    r_c1 = p_c1.add_run(f"{TITLE} ({KANJI_TITLE})\n{SUBTITLE}")
    r_c1.font.size = Pt(9.5)
    r_c1.font.bold = True

    p_c2 = doc.add_paragraph()
    p_c2.paragraph_format.space_after = Pt(10)
    r_c2 = p_c2.add_run(
        "Copyright © 2026. All rights reserved worldwide.\n"
        "No part of this publication may be reproduced, stored in a retrieval system, "
        "or transmitted in any form or by any means without prior written permission, "
        "except for brief quotations embodied in critical reviews or articles."
    )
    r_c2.font.size = Pt(8.5)
    r_c2.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    p_c3 = doc.add_paragraph()
    r_c3 = p_c3.add_run(
        "This is a work of fiction. Names, characters, places, and incidents are either the "
        "product of the author's imagination or are used fictitiously. Any resemblance to actual "
        "persons, living or dead, events, or locales is entirely coincidental."
    )
    r_c3.font.size = Pt(8.0)
    r_c3.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    doc.add_page_break()

    # -------------------------------------------------------------
    # FRONT MATTER: Table of Contents
    # -------------------------------------------------------------
    p_toch = doc.add_paragraph()
    p_toch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toch.paragraph_format.space_before = Pt(60)
    p_toch.paragraph_format.space_after = Pt(28)
    r_toch = p_toch.add_run("CONTENTS")
    r_toch.font.name = 'Georgia'
    r_toch.font.size = Pt(16)
    r_toch.font.bold = True
    r_toch.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    for i, (cid, num_label, title_label) in enumerate(CHAPTER_METADATA):
        p_row = doc.add_paragraph()
        p_row.paragraph_format.first_line_indent = Inches(0)
        p_row.paragraph_format.line_spacing = 1.35
        p_row.paragraph_format.space_before = Pt(3)
        p_row.paragraph_format.space_after = Pt(3)
        add_toc_hyperlink(p_row, f"{num_label}  —  {title_label}", f"_toc_{cid}")

    # Add Story Notes link to TOC
    p_row_col = doc.add_paragraph()
    p_row_col.paragraph_format.first_line_indent = Inches(0)
    p_row_col.paragraph_format.line_spacing = 1.35
    p_row_col.paragraph_format.space_before = Pt(3)
    p_row_col.paragraph_format.space_after = Pt(3)
    add_toc_hyperlink(p_row_col, "Story Notes & Glossary", "_toc_afterword")

    doc.add_page_break()

    # -------------------------------------------------------------
    # BODY MATTER: Chapters 1 to 6
    # -------------------------------------------------------------
    for i, (cid, num_label, title_label) in enumerate(CHAPTER_METADATA):
        # Heading 1: Chapter Number
        p_h1 = doc.add_paragraph(style='Heading 1')
        p_h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_h1.paragraph_format.space_before = Pt(65)
        p_h1.paragraph_format.space_after = Pt(6)
        p_h1.paragraph_format.keep_with_next = True
        run_h1 = p_h1.add_run(num_label.upper())
        run_h1.font.name = 'Georgia'
        run_h1.font.size = Pt(18)
        run_h1.font.bold = True
        run_h1.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
        add_bookmark(p_h1, str(i + 1), f"_toc_{cid}")

        # Heading 2: Chapter Title
        p_h2 = doc.add_paragraph(style='Heading 2')
        p_h2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_h2.paragraph_format.space_before = Pt(0)
        p_h2.paragraph_format.space_after = Pt(34)
        p_h2.paragraph_format.keep_with_next = True
        run_h2 = p_h2.add_run(title_label)
        run_h2.font.name = 'Georgia'
        run_h2.font.size = Pt(13)
        run_h2.font.italic = True
        run_h2.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

        blocks = load_chapter_blocks(cid)
        is_first_after_break = True

        for btype, btext in blocks:
            if btype == "break":
                p_brk = doc.add_paragraph()
                p_brk.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_brk.paragraph_format.first_line_indent = Inches(0)
                p_brk.paragraph_format.space_before = Pt(16)
                p_brk.paragraph_format.space_after = Pt(16)
                r_brk = p_brk.add_run(btext)
                r_brk.font.name = 'Georgia'
                r_brk.font.size = Pt(10)
                r_brk.font.color.rgb = RGBColor(0x77, 0x77, 0x77)
                is_first_after_break = True
            else:
                p_body = doc.add_paragraph()
                p_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p_body.paragraph_format.line_spacing = 1.18
                p_body.paragraph_format.space_before = Pt(0)
                p_body.paragraph_format.space_after = Pt(0)
                if is_first_after_break:
                    p_body.paragraph_format.first_line_indent = Inches(0)
                    is_first_after_break = False
                else:
                    p_body.paragraph_format.first_line_indent = Inches(0.25)

                smart_text = smartify(btext)
                inlines = parse_inlines(smart_text)
                for kind, chunk in inlines:
                    r = p_body.add_run(chunk)
                    r.font.name = 'Georgia'
                    r.font.size = Pt(11)
                    if kind == "bold":
                        r.bold = True
                    elif kind == "italic":
                        r.italic = True
                    elif kind == "bold_italic":
                        r.bold = True
                        r.italic = True
                    elif kind == "code":
                        r.font.name = "Consolas"
                        r.font.size = Pt(10)

        doc.add_page_break()

    # -------------------------------------------------------------
    # BACK MATTER: Story Notes & Glossary
    # -------------------------------------------------------------
    p_afth1 = doc.add_paragraph(style='Heading 1')
    p_afth1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_afth1.paragraph_format.space_before = Pt(65)
    p_afth1.paragraph_format.space_after = Pt(24)
    r_afth1 = p_afth1.add_run("STORY NOTES & GLOSSARY")
    r_afth1.font.name = 'Georgia'
    r_afth1.font.size = Pt(18)
    r_afth1.font.bold = True
    add_bookmark(p_afth1, "99", "_toc_afterword")

    p_aft1 = doc.add_paragraph()
    p_aft1.paragraph_format.first_line_indent = Inches(0)
    p_aft1.paragraph_format.space_after = Pt(8)
    r_aft1 = p_aft1.add_run("About Kagiroi Drift")
    r_aft1.font.bold = True
    r_aft1.font.size = Pt(12)

    p_aft2 = doc.add_paragraph()
    p_aft2.paragraph_format.first_line_indent = Inches(0)
    p_aft2.paragraph_format.space_after = Pt(12)
    p_aft2.add_run(
        smartify(
            "Between the howling storms of gas-giant Geryon-7 and the freezing silence of vacuum, "
            "the only warmth left in Shin-Murakumo Station belongs to Hotarubi Kaname and Kurotsuyu Sakuya. "
            "Kagiroi Drift is a story of tactile zero-g survival, sensory trauma, acoustic telemetry, and intense "
            "deep-space devotion."
        )
    )

    p_aft3 = doc.add_paragraph()
    p_aft3.paragraph_format.first_line_indent = Inches(0)
    p_aft3.paragraph_format.space_after = Pt(8)
    r_aft3 = p_aft3.add_run("Thematic Nomenclature")
    r_aft3.font.bold = True
    r_aft3.font.size = Pt(12)

    notes = [
        ("Hotarubi Kaname (蛍火 要)", "Lead EVA hull-cutter. Hotarubi ('cold firefly luminescence') captures the quiet chemiluminescent spark surviving in deep vacuum. Kaname ('keystone' or 'pivot') represents the physical grounding center anchoring Sakuya to reality."),
        ("Kurotsuyu Sakuya (玄露 朔夜)", "Deep-telemetry acoustician. Kurotsuyu ('black dew / condensation') evokes moisture clinging to cold sensor copper. Sakuya ('new moon / dark night') represents the shadow realm of acoustic micro-strain."),
        ("Shinonome Kagari (東雲 篝)", "Station salvage officer. Shinonome ('dawn fissure') and Kagari ('watchfire beacon') symbolize orbital warning telemetry."),
        ("Yoiduki Mizore (宵月 霙)", "Freelance runner. Yoiduki ('twilight moon') and Mizore ('freezing sleet') evoke low-albedo stealth transit and volatile cryo-coolant leaks."),
        ("The Kagiroi Effect (陽炎)", "The optical phenomenon of thermal shimmering and solar coronal plasma ribbons dancing across the gas-giant's atmosphere."),
    ]
    for name, desc in notes:
        p_n = doc.add_paragraph()
        p_n.paragraph_format.first_line_indent = Inches(0)
        p_n.paragraph_format.space_after = Pt(6)
        r_nh = p_n.add_run(f"• {name}: ")
        r_nh.font.bold = True
        p_n.add_run(smartify(desc))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc.save(out_path)
    print(f"Successfully generated clean KDP DOCX: {out_path} ({os.path.getsize(out_path):,} bytes)")


# ==============================================================================
# 2. EPUB 3 / EPUB 2 DUAL GENERATION (Amazon KDP Kindle Ready)
# ==============================================================================

CSS_CONTENT = """@charset "utf-8";

/* Page and viewport geometry */
@page {
    margin: 1.0em 0.8em;
}

body {
    font-family: Georgia, "Iowan Old Style", "Palatino Linotype", "Book Antiqua", serif;
    font-size: 1.0em;
    line-height: 1.55;
    color: #1a1a1a;
    background-color: #ffffff;
    margin: 0 4%;
    padding: 0;
    text-align: justify;
}

/* Headings */
h1 {
    font-size: 1.85em;
    font-weight: bold;
    letter-spacing: 0.04em;
    text-align: center;
    margin: 2.5em 0 0.2em;
    page-break-before: always;
    break-before: page;
}

h2 {
    font-size: 1.25em;
    font-weight: normal;
    letter-spacing: 0.05em;
    text-align: center;
    margin: 2.2em 0 0.15em;
    page-break-before: always;
    break-before: page;
}

p.chap-sub {
    font-size: 1.05em;
    font-style: italic;
    text-align: center;
    color: #444444;
    margin: 0 0 2.4em;
    text-indent: 0;
}

/* Paragraph styling */
p {
    margin: 0;
    text-indent: 1.4em;
}

p.first {
    text-indent: 0;
}

p.ornament {
    text-align: center;
    text-indent: 0;
    margin: 1.8em 0;
    color: #777777;
    letter-spacing: 0.35em;
    font-size: 0.95em;
}

/* Title & Front Matter */
div.titlepage {
    text-align: center;
    padding-top: 25%;
    page-break-before: always;
    break-before: page;
}

h1.book-title {
    font-size: 2.3em;
    letter-spacing: 0.08em;
    margin-bottom: 0.1em;
}

p.kanji-title {
    font-size: 1.3em;
    color: #555555;
    margin: 0.2em 0 1.2em;
    text-indent: 0;
}

p.book-subtitle {
    font-size: 1.15em;
    font-style: italic;
    color: #444444;
    margin-bottom: 3.0em;
    text-indent: 0;
}

/* Copyright Page */
div.colophon {
    font-size: 0.85em;
    color: #444444;
    line-height: 1.5;
    margin-top: 30%;
    page-break-before: always;
    break-before: page;
}

div.colophon p {
    text-indent: 0;
    margin-bottom: 1.0em;
}

/* Table of Contents */
nav#toc ol, div.toc-list ol {
    list-style-type: none;
    padding-left: 0;
    margin: 2.0em 0;
}

nav#toc li, div.toc-list li {
    margin: 0.9em 0;
    text-indent: 0;
}

nav#toc a, div.toc-list a {
    text-decoration: none;
    color: #1a1a1a;
}
"""

CONTAINER_XML = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

def to_xhtml_doc(body_content, page_title):
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" '
        f'xml:lang="{LANG}" lang="{LANG}">\n'
        '<head>\n'
        '<meta charset="utf-8"/>\n'
        f'<title>{html.escape(page_title)}</title>\n'
        '<link rel="stylesheet" type="text/css" href="style.css"/>\n'
        '</head>\n'
        '<body>\n'
        f'{body_content}\n'
        '</body>\n'
        '</html>\n'
    )

def render_title_xhtml():
    body = (
        '<div class="titlepage">\n'
        f'  <h1 class="book-title">{html.escape(TITLE.upper())}</h1>\n'
        f'  <p class="kanji-title">{html.escape(KANJI_TITLE)}</p>\n'
        f'  <p class="book-subtitle">{html.escape(SUBTITLE)}</p>\n'
        '</div>'
    )
    return to_xhtml_doc(body, TITLE)

def render_colophon_xhtml():
    body = (
        '<div class="colophon">\n'
        f'  <p><strong>{html.escape(TITLE)} ({html.escape(KANJI_TITLE)})</strong><br/>{html.escape(SUBTITLE)}</p>\n'
        '  <p>Copyright &#169; 2026. All rights reserved worldwide.</p>\n'
        '  <p>No part of this publication may be reproduced, stored in a retrieval system, or transmitted '
        'in any form or by any means without prior written permission, except for brief quotations in critical reviews.</p>\n'
        '  <p>This is a work of fiction. Names, characters, places, and incidents are either the product of the author&#8217;s '
        'imagination or used fictitiously. Any resemblance to actual persons, living or dead, events, or locales is entirely coincidental.</p>\n'
        '</div>'
    )
    return to_xhtml_doc(body, "Copyright")

def render_chapter_xhtml(cid, num_label, title_label):
    blocks = load_chapter_blocks(cid)
    lines = [
        f'<h2>{html.escape(num_label)}</h2>',
        f'<p class="chap-sub">{html.escape(title_label)}</p>'
    ]
    is_first_after_break = True
    for btype, btext in blocks:
        if btype == "break":
            lines.append('<p class="ornament">&#9671; &#160; &#9671; &#160; &#9671;</p>')
            is_first_after_break = True
        else:
            smart_text = smartify(btext)
            inlines = parse_inlines(smart_text)
            html_parts = []
            for kind, chunk in inlines:
                esc = html.escape(chunk)
                if kind == "italic":
                    html_parts.append(f'<em>{esc}</em>')
                elif kind == "bold":
                    html_parts.append(f'<strong>{esc}</strong>')
                elif kind == "bold_italic":
                    html_parts.append(f'<strong><em>{esc}</em></strong>')
                elif kind == "code":
                    html_parts.append(f'<code>{esc}</code>')
                else:
                    html_parts.append(esc)
            para_content = "".join(html_parts)
            if is_first_after_break:
                lines.append(f'<p class="first">{para_content}</p>')
                is_first_after_break = False
            else:
                lines.append(f'<p>{para_content}</p>')
    body = "\n".join(lines)
    return to_xhtml_doc(body, f"{num_label}: {title_label}")

def render_afterword_xhtml():
    body = (
        '<h2>Story Notes &amp; Glossary</h2>\n'
        '<p class="chap-sub">Thematic Nomenclature</p>\n'
        '<p class="first"><strong>Between the howling storm of Geryon-7 and the freezing silence of vacuum, '
        'the only heat left is between them.</strong></p>\n'
        '<p>Every character name and motif in <em>Kagiroi Drift</em> is drawn from vacuum optical phenomena, orbital kinetics, and acoustic physics:</p>\n'
        '<p>&#8226; <strong>Hotarubi Kaname (&#34541;&#28779; &#35201;)</strong>: Lead EVA hull-cutter. '
        '<em>Hotarubi</em> (&#8220;cold firefly bioluminescence&#8221;) embodies the kinetic heat dissipating against silent hull plating. '
        '<em>Kaname</em> (&#8220;keystone / pivot&#8221;) is the somatic center keeping the station and Sakuya grounded.</p>\n'
        '<p>&#8226; <strong>Kurotsuyu Sakuya (&#29572;&#38706; &#26388;&#22812;)</strong>: Station acoustician. '
        '<em>Kurotsuyu</em> (&#8220;dark condensation&#8221;) represents moisture clinging to cold sensor well copper. '
        '<em>Sakuya</em> (&#8220;new moon night&#8221;) reflects the unilluminated shadow where telemetry listens for micro-fractures.</p>\n'
        '<p>&#8226; <strong>Shinonome Kagari (&#26481;&#38642; &#31741;)</strong>: Dawn fissure and watchfire beacon.</p>\n'
        '<p>&#8226; <strong>Yoiduki Mizore (&#23477;&#26376; &#38681;)</strong>: Twilight moon and freezing cryo-sleet.</p>\n'
        '<p>&#8226; <strong>The Kagiroi Effect (&#38525;&#28814;)</strong>: Thermal shimmering and solar coronal plasma ribbons dancing across the dawn horizon.</p>'
    )
    return to_xhtml_doc(body, "Story Notes & Glossary")

def render_nav_xhtml():
    li_items = []
    for cid, num_label, title_label in CHAPTER_METADATA:
        li_items.append(f'    <li><a href="{cid}.xhtml">{html.escape(num_label)} &#8212; {html.escape(title_label)}</a></li>')
    li_items.append('    <li><a href="afterword.xhtml">Story Notes &amp; Glossary</a></li>')
    items_markup = "\n".join(li_items)

    body = (
        '<nav epub:type="toc" id="toc">\n'
        '  <h1>Table of Contents</h1>\n'
        '  <ol>\n'
        f'{items_markup}\n'
        '  </ol>\n'
        '</nav>\n'
        '<nav epub:type="landmarks" id="landmarks" hidden="hidden">\n'
        '  <h1>Landmarks</h1>\n'
        '  <ol>\n'
        '    <li><a epub:type="titlepage" href="title.xhtml">Title Page</a></li>\n'
        '    <li><a epub:type="bodymatter" href="chapter-01.xhtml">Start of Story</a></li>\n'
        '    <li><a epub:type="toc" href="nav.xhtml">Table of Contents</a></li>\n'
        '  </ol>\n'
        '</nav>'
    )
    return to_xhtml_doc(body, "Contents")

def render_ncx():
    points = [
        '    <navPoint id="np-title" playOrder="1"><navLabel><text>Title Page</text></navLabel><content src="title.xhtml"/></navPoint>',
        '    <navPoint id="np-colophon" playOrder="2"><navLabel><text>Copyright</text></navLabel><content src="colophon.xhtml"/></navPoint>',
        '    <navPoint id="np-toc" playOrder="3"><navLabel><text>Table of Contents</text></navLabel><content src="nav.xhtml"/></navPoint>',
    ]
    order = 4
    for cid, num_label, title_label in CHAPTER_METADATA:
        points.append(
            f'    <navPoint id="np-{cid}" playOrder="{order}">'
            f'<navLabel><text>{html.escape(num_label)}: {html.escape(title_label)}</text></navLabel>'
            f'<content src="{cid}.xhtml"/></navPoint>'
        )
        order += 1
    points.append(
        f'    <navPoint id="np-afterword" playOrder="{order}">'
        f'<navLabel><text>Story Notes &amp; Glossary</text></navLabel>'
        f'<content src="afterword.xhtml"/></navPoint>'
    )
    nav_markup = "\n".join(points)

    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="en">\n'
        '  <head>\n'
        f'    <meta name="dtb:uid" content="{BOOK_UUID}"/>\n'
        '    <meta name="dtb:depth" content="1"/>\n'
        '    <meta name="dtb:totalPageCount" content="0"/>\n'
        '    <meta name="dtb:maxPageNumber" content="0"/>\n'
        '  </head>\n'
        f'  <docTitle><text>{html.escape(TITLE)} ({html.escape(KANJI_TITLE)})</text></docTitle>\n'
        '  <navMap>\n'
        f'{nav_markup}\n'
        '  </navMap>\n'
        '</ncx>\n'
    )

def render_content_opf(modified_iso):
    manifest = [
        '    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
        '    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
        '    <item id="css" href="style.css" media-type="text/css"/>',
        '    <item id="title" href="title.xhtml" media-type="application/xhtml+xml"/>',
        '    <item id="colophon" href="colophon.xhtml" media-type="application/xhtml+xml"/>',
    ]
    for cid, _, _ in CHAPTER_METADATA:
        manifest.append(f'    <item id="{cid}" href="{cid}.xhtml" media-type="application/xhtml+xml"/>')
    manifest.append('    <item id="afterword" href="afterword.xhtml" media-type="application/xhtml+xml"/>')

    spine = [
        '    <itemref idref="title"/>',
        '    <itemref idref="colophon"/>',
        '    <itemref idref="nav"/>',
    ]
    for cid, _, _ in CHAPTER_METADATA:
        spine.append(f'    <itemref idref="{cid}"/>')
    spine.append('    <itemref idref="afterword"/>')

    manifest_markup = "\n".join(manifest)
    spine_markup = "\n".join(spine)

    desc = (
        "Between the howling storms of gas-giant Geryon-7 and the freezing silence of vacuum, "
        "the only heat left is between them. An adult yuri science fiction erotic novella of sensory "
        "grounding, zero-g salvage, and deep-space devotion."
    )

    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" '
        f'xml:lang="{LANG}">\n'
        '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        f'    <dc:identifier id="bookid">{BOOK_UUID}</dc:identifier>\n'
        f'    <dc:title>{html.escape(TITLE)} ({html.escape(KANJI_TITLE)})</dc:title>\n'
        f'    <dc:language>{LANG}</dc:language>\n'
        f'    <dc:description>{html.escape(desc)}</dc:description>\n'
        f'    <meta property="dcterms:modified">{modified_iso}</meta>\n'
        '  </metadata>\n'
        '  <manifest>\n'
        f'{manifest_markup}\n'
        '  </manifest>\n'
        '  <spine toc="ncx">\n'
        f'{spine_markup}\n'
        '  </spine>\n'
        '  <guide>\n'
        '    <reference type="toc" title="Table of Contents" href="nav.xhtml"/>\n'
        '    <reference type="text" title="Beginning" href="chapter-01.xhtml"/>\n'
        '  </guide>\n'
        '</package>\n'
    )

def generate_kdp_epub(out_path):
    modified = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    files = {
        "OEBPS/style.css": CSS_CONTENT.encode("utf-8"),
        "OEBPS/title.xhtml": render_title_xhtml().encode("utf-8"),
        "OEBPS/colophon.xhtml": render_colophon_xhtml().encode("utf-8"),
        "OEBPS/nav.xhtml": render_nav_xhtml().encode("utf-8"),
        "OEBPS/toc.ncx": render_ncx().encode("utf-8"),
        "OEBPS/content.opf": render_content_opf(modified).encode("utf-8"),
        "OEBPS/afterword.xhtml": render_afterword_xhtml().encode("utf-8"),
    }

    # Add chapter files
    for cid, num_label, title_label in CHAPTER_METADATA:
        xhtml = render_chapter_xhtml(cid, num_label, title_label)
        files[f"OEBPS/{cid}.xhtml"] = xhtml.encode("utf-8")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with zipfile.ZipFile(out_path, "w") as zf:
        # 1. mimetype MUST be uncompressed (STORED) and first in archive
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        # 2. META-INF/container.xml
        zf.writestr("META-INF/container.xml", CONTAINER_XML.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
        # 3. Everything else deflated
        for item_name in sorted(files):
            zf.writestr(item_name, files[item_name], compress_type=zipfile.ZIP_DEFLATED)

    print(f"Successfully generated clean KDP EPUB: {out_path} ({os.path.getsize(out_path):,} bytes, {len(files) + 2} entries)")


def main():
    docx_target = os.path.join(DELIVERY_DIR, "kagiroi-drift.docx")
    epub_target = os.path.join(DELIVERY_DIR, "kagiroi-drift.epub")

    print("=== Rendering Clean Amazon KDP Formats for Kagiroi Drift ===")
    generate_kdp_docx(docx_target)
    generate_kdp_epub(epub_target)

    # Mirror to workspace epubs/ catalog
    global_epubs_dir = os.path.join(WORKSPACE_DIR, "epubs")
    if os.path.exists(global_epubs_dir):
        global_epub_target = os.path.join(global_epubs_dir, "kagiroi-drift.epub")
        with open(epub_target, "rb") as src, open(global_epub_target, "wb") as dst:
            dst.write(src.read())
        print(f"Mirrored clean EPUB to catalog: {global_epub_target}")

    print("=== Render Complete ===")

if __name__ == "__main__":
    main()
