#!/usr/bin/env python
"""Extract an epub's spine documents to plain text, one file per document.

Used only to build the calibration corpus. Not part of the book pipeline.
"""
import os
import posixpath
import re
import sys
import zipfile
import html
import xml.etree.ElementTree as ET


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
                # zip entry names are always POSIX-separated, even on Windows
                order.append(posixpath.join(base, href) if base else href)
    return z, order


def to_text(raw):
    s = raw.decode("utf-8", "replace")
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


def main(epub, outdir, tag):
    os.makedirs(outdir, exist_ok=True)
    z, order = spine_docs(epub)
    n = 0
    for i, doc in enumerate(order):
        if doc not in z.namelist():
            continue
        txt = to_text(z.read(doc))
        words = len(txt.split())
        if words < 400:          # front matter, colophons, part dividers
            continue
        n += 1
        stem = os.path.splitext(os.path.basename(doc))[0]
        stem = re.sub(r"[^A-Za-z0-9._-]", "_", stem)
        out = os.path.join(outdir, "%s__%02d__%s.txt" % (tag, i, stem))
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(txt)
        print("%s  %6d words  %s" % (tag, words, os.path.basename(out)))
    print("-- %s: %d docs kept" % (tag, n))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
