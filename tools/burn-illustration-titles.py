"""Burn each day's title into its plate as a white title card.

Every plate leaves its top band dark and empty, so the title is set there, in Creepster,
the book's display face: the same voice as the title page, sitting inside the painting
rather than printed underneath it. A faint darkening over the band and a blurred shadow
under the letters keep the white readable where the sky is not quite black.

Reads the clean plates from art/illustrations/{print,ebook} and writes titled copies to
art/illustrations/titled/{print,ebook}; the originals are never touched, so the pass can be
re-run after a title or type-size change. Titles come from the chapter headings, which are
the single source of truth the two builders also read.
"""

import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BOOK = Path(__file__).resolve().parent.parent / "test-books" / "advent-horror"
CHAPTERS = sorted((BOOK / "manuscript" / "chapters").glob("chapter-*.md"))
ART = BOOK / "art" / "illustrations"
SIZES = ("print", "ebook")

# The title page's display face, shipped with the project. The rest are fallbacks so the pass
# still runs on a machine where the font folder is missing.
DISPLAY = Path(__file__).resolve().parent / "fonts" / "creepster" / "Creepster-Regular.ttf"
FALLBACK = ("C:/Windows/Fonts/constan.ttf", "C:/Windows/Fonts/pala.ttf",
            "C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/times.ttf")

MAX_LINES = 3
BOX_W = 0.82          # of image width
TOP = 0.072           # of image height, from the trim to the top of the title block
TRACK = 0.055         # letterspacing, in em
LEAD = 1.12


def split_heading(h):
    m = re.match(r"^(\d+)\s*[-\u2013\u2014]\s*(.+)$", h)
    if not m:
        raise SystemExit("chapter heading has no day number: %r" % h)
    return m.group(1), m.group(2).strip()


def titles():
    out = {}
    for path in CHAPTERS:
        day, title = split_heading(path.read_text(encoding="utf-8").splitlines()[0][2:].strip())
        out[int(day)] = title
    if sorted(out) != list(range(1, 25)):
        raise SystemExit("days on disk are not 1..24: %s" % sorted(out))
    return out


def load_font(size):
    for path in (DISPLAY,) + tuple(Path(p) for p in FALLBACK):
        if Path(path).is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size)


def width(draw, text, font, track):
    if not text:
        return 0.0
    total = sum(draw.textlength(ch, font=font) + track for ch in text)
    return total - track


def wrap(draw, text, font, track, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if not cur or width(draw, trial, font, track) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, title, w):
    """Largest size that sets the title in at most three lines inside the box."""
    start = int(round(w * 0.082))
    for size in range(start, int(w * 0.026), -2):
        font = load_font(size)
        track = size * TRACK
        lines = wrap(draw, title, font, track, w * BOX_W)
        if len(lines) <= MAX_LINES and max(width(draw, l, font, track) for l in lines) <= w * BOX_W:
            return font, track, lines
    raise SystemExit("could not fit title at any size: %r" % title)


def veil(size, end, alpha_max=80):
    """Faint darkening across the title band so white type holds even on a lit sky."""
    w, h = size
    layer = Image.new("L", (1, h), 0)
    end = max(1, min(end, h))
    for y in range(end):
        t = 1 - y / end
        layer.putpixel((0, y), int(alpha_max * t * t))
    black = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    black.putalpha(layer.resize((w, h)))
    return black


def card(src, title, dst):
    img = Image.open(src).convert("RGBA")
    w, h = img.size
    draw = ImageDraw.Draw(img)
    font, track, lines = fit(draw, title, w)
    lh = int(round(font.size * LEAD))
    block = lh * len(lines)
    top = int(round(h * TOP))

    img = Image.alpha_composite(img, veil((w, h), top + block + int(h * 0.10)))
    draw = ImageDraw.Draw(img)

    # One layer for the type, blurred once for the shadow, drawn once sharp on top: a single
    # shadow offset is invisible on a bright ground, a blur reads as depth under white.
    text_layer = Image.new("L", (w, h), 0)
    tdraw = ImageDraw.Draw(text_layer)
    for i, line in enumerate(lines):
        x = (w - width(draw, line, font, track)) / 2
        y = top + i * lh
        for ch in line:
            tdraw.text((x, y), ch, font=font, fill=255)
            x += draw.textlength(ch, font=font) + track

    shadow = text_layer.filter(ImageFilter.GaussianBlur(max(2, font.size // 12)))
    img = Image.alpha_composite(img, Image.merge(
        "RGBA", (Image.new("L", (w, h), 0),) * 3 + (shadow.point(lambda v: v * 0.85),)))
    img = Image.alpha_composite(img, Image.merge(
        "RGBA", (Image.new("L", (w, h), 255),) * 3 + (text_layer,)))

    exif = img.getexif()
    desc = "Day %s - %s. Terror Before Christmas, Kalie Kirch." % (dst.stem, title)
    exif[0x010E] = desc                      # ImageDescription
    exif[0x9C9B] = desc.encode("utf-16-le")   # XPTitle (Windows)
    img.convert("RGB").save(dst, "JPEG", quality=92, optimize=True, exif=exif)
    return len(lines), font.size


def main():
    names = titles()
    for size in SIZES:
        out = ART / "titled" / size
        out.mkdir(parents=True, exist_ok=True)
        for day in range(1, 25):
            src = ART / size / ("%02d.jpg" % day)
            if not src.is_file():
                raise SystemExit("clean plate missing: %s" % src)
            n, px = card(src, names[day], out / ("%02d.jpg" % day))
            if day in (1, 24):
                print("%-5s day %02d  %d line(s), %d px  %s"
                      % (size, day, n, px, names[day]))
        print("%-5s wrote 24 titled plates to %s" % (size, out.relative_to(BOOK)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
