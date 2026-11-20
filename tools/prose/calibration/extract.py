#!/usr/bin/env python
"""Extract an ebook's documents to plain text, one file per document.

Used only to build the calibration corpus. Not part of the book pipeline.

EPUB: one file per spine document, as the package declares it.
MOBI: the text records are one HTML stream, so the document boundaries come from the
`<mbp:pagebreak>` markers the format uses; a MOBI without them is written as one
(document count printed honestly, never padded). PalmDOC compression (type 2) and
uncompressed (type 1) are read here; HUFF/CDIC (17480) is refused by name rather than
extracted wrongly.
"""
import os
import posixpath
import re
import struct
import sys
import zipfile
import html
import xml.etree.ElementTree as ET
from urllib.parse import unquote


def spine_docs(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    container = [n for n in names if n.endswith("container.xml")][0]
    root = ET.fromstring(z.read(container))
    opf = None
    for el in root.iter():
        if el.tag.endswith("rootfile"):
            opf = el.attrib.get("full-path")
    opf = opf or [n for n in names if n.endswith(".opf")][0]
    base = posixpath.dirname(opf)
    tree = ET.fromstring(z.read(opf))
    manifest = {}
    for el in tree.iter():
        if el.tag.endswith("item") and "id" in el.attrib:
            manifest[el.attrib["id"]] = el.attrib.get("href", "")
    order = []
    for el in tree.iter():
        if el.tag.endswith("itemref") and "idref" in el.attrib:
            href = manifest.get(el.attrib["idref"], "")
            if href:
                # The OPF percent-encodes a filename it has to (%20 for a space); the zip
                # entry is stored under the decoded name. Without this, an epub whose
                # documents carry spaces in their names resolves to zero documents and is
                # reported as "0 docs kept" rather than as the filename bug it is.
                href = unquote(href)
                # zip entry names are always POSIX-separated, even on Windows
                order.append(posixpath.join(base, href) if base else href)
    return z, order


def to_text(raw):
    s = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|h[1-6]|li|blockquote|section)>", "\n\n", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    # keep typography (curly quotes, em dashes) - A20 measures it, so
    # normalising here would hide the very thing under calibration
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return "\n".join(ln.strip() for ln in s.split("\n")).strip()


def palmdoc(blob):
    """PalmDOC LZ77, the only compression a MOBI text record uses besides none."""
    out, i, n = bytearray(), 0, len(blob)
    while i < n:
        c = blob[i]
        i += 1
        if c == 0:
            out.append(0)
        elif c <= 8:
            out += blob[i:i + c]
            i += c
        elif c <= 0x7F:
            out.append(c)
        elif c <= 0xBF:
            if i >= n:
                break
            v = (c << 8) | blob[i]
            i += 1
            dist, length = (v >> 3) & 0x7FF, (v & 7) + 3
            for _ in range(length):
                out.append(out[-dist] if dist and len(out) >= dist else 0x20)
        else:
            out += b" "
            out.append(c ^ 0x80)
    return bytes(out)


def repair(raw):
    """UTF-8, with stray cp1252 bytes repaired one at a time.

    These MOBIs are mixed: an apostrophe written as cp1252 0x92 sitting beside an em
    dash written as UTF-8 E2 80 94. Decoding the whole record one way corrupts the
    other - cp1252 turns every em dash into three mojibake characters, and UTF-8 turns
    the apostrophes into U+FFFD. Valid UTF-8 sequences are kept; only the bytes that
    cannot be UTF-8 are mapped through cp1252.
    """
    out = []
    for ch in raw.decode("utf-8", "surrogateescape"):
        code = ord(ch)
        if 0xDC80 <= code <= 0xDCFF:
            out.append(bytes([code - 0xDC00]).decode("cp1252", "replace"))
        else:
            out.append(ch)
    return "".join(out)


def mobi_html(path):
    """The whole book as one HTML string. Header offsets are read, never guessed."""
    data = open(path, "rb").read()
    nrec = struct.unpack(">H", data[76:78])[0]
    # Record info entries are 8 bytes, not 4: the offset is followed by a 4-byte tail.
    offs = [struct.unpack(">I", data[78 + i * 8:82 + i * 8])[0] for i in range(nrec)]
    offs.append(len(data))
    rec0 = data[offs[0]:offs[1]]
    compression, _unused, textlen = struct.unpack(">HHI", rec0[:8])
    first = struct.unpack(">I", rec0[0x50:0x54])[0]
    if compression == 1:
        raw = b"".join(data[offs[i]:offs[i + 1]] for i in range(1, first))
    elif compression == 2:
        raw = b"".join(palmdoc(data[offs[i]:offs[i + 1]]) for i in range(1, first))
    else:
        raise SystemExit("extract: MOBI compression %d (HUFF/CDIC) is not read here"
                         % compression)
    return repair(raw[:textlen])


def mobi_docs(path):
    """[(stem, text)] split on the format's own page-break marker."""
    parts = re.split(r"(?i)<mbp:pagebreak[^>]*>", mobi_html(path))
    return [("part%02d" % i, to_text(p)) for i, p in enumerate(parts)]


def epub_docs(path):
    """[(stem, text)] in spine order, as the package declares it."""
    z, order = spine_docs(path)
    out = []
    for i, doc in enumerate(order):
        if doc not in z.namelist():
            continue
        stem = os.path.splitext(os.path.basename(doc))[0]
        out.append(("%02d__%s" % (i, re.sub(r"[^A-Za-z0-9._-]", "_", stem)),
                    to_text(z.read(doc))))
    return out


# A chapter heading the author wrote as a bare number on its own line: Lee Child's
# paperbacks do this, and their epubs keep whole runs of chapters in one spine document.
NUMBERED_HEADING = re.compile(r"(?m)^[ \t]*(\d{1,3})[ \t]*$")


def split_numbered(text):
    """[(label, text)] cut at bare-number headings, or [(None, text)] when there are none."""
    cuts = [m.start() for m in NUMBERED_HEADING.finditer(text)]
    if len(cuts) < 3:
        return [(None, text)]
    out, starts = [], [0] + cuts
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        body = text[start:end]
        m = NUMBERED_HEADING.match(body)
        out.append((m.group(1) if m else None, body))
    return out


def main(source, outdir, tag, split_chapters=False):
    os.makedirs(outdir, exist_ok=True)
    reader = mobi_docs if source.lower().endswith((".mobi", ".azw", ".azw3")) else epub_docs
    n = 0
    docs = []
    for i, (stem, txt) in enumerate(reader(source)):
        if split_chapters:
            docs.extend(("%s_c%s" % (stem, c) if c else stem + "_pre", part)
                        for c, part in split_numbered(txt))
        else:
            docs.append((stem, txt))
    for i, (stem, txt) in enumerate(docs):
        words = len(txt.split())
        if words < 400:          # front matter, colophons, part dividers
            continue
        n += 1
        out = os.path.join(outdir, "%s__%02d__%s.txt" % (tag, i, stem))
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(txt)
        print("%s  %6d words  %s" % (tag, words, os.path.basename(out)))
    print("-- %s: %d docs kept" % (tag, n))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], "--split-chapters" in sys.argv)
