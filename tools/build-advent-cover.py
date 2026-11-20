#!/usr/bin/env python3
"""Build the Advent Horror cover at KDP geometry, 300 dpi.

  delivery/print/cover-front.jpg    5.5 x 8.5 in front panel, the ebook cover
  delivery/print/cover-wrap.jpg     full wrap at the MEASURED extent
  delivery/print/cover-wrap.pdf     the same wrap as one PDF page, exact trim + bleed
  delivery/print/cover-wrap-comp.jpg  full wrap at the ESTIMATED extent, only if no
                                      interior has been built yet (a comp, not an upload file)

The spine is not a constant here. It is read from delivery/print/interior-meta.json,
which tools/build-advent-interior.py writes beside the interior PDF:

    pages x 0.002252 in/page (white paper) = spine

So run the interior first. A spine built from an estimate is the failure that uploads
cleanly and proves wrong, which is why the estimated path writes a file with "comp"
in its name and the measured path does not.

CMYK is not produced: no colour-managed converter is installed on this machine. KDP
prints these digitally from RGB, and the wrap PDF here is RGB with no transparency.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import json
import os
import sys

import numpy as np

BOOK = Path(__file__).resolve().parents[1] / "test-books" / "advent-horror"
OUT = BOOK / "delivery" / "print"
META = OUT / "interior-meta.json"
FONTS = Path("C:/Windows/Fonts")
ART_FONTS = Path(__file__).resolve().parent / "fonts" / "creepster"

# The title face matches the interior's title page (Creepster, SIL OFL, vendored with the
# build). Subtitle and author stay in Georgia: the subtitle is the KDP-mandated string and
# has to stay legible at thumbnail size, and a display face at 20 px reads as a smudge.

TITLE_LINES = ("TERROR BEFORE", "CHRISTMAS")
TITLE_ONE_LINE = "TERROR BEFORE CHRISTMAS"
SUBTITLE = ("A HORROR ADVENT CALENDAR FOR ADULTS",
            "24 TERRIFYING TALES, ONE FOR EACH NIGHT BEFORE CHRISTMAS")
AUTHOR = "KALIE KIRCH"
ART = OUT / "cover-art.jpg"          # the author's painting; never resampled below 1200 px
# The author's finished front: painting, title, subtitle and byline already composed at
# 1800 x 2700 (2:3, the front panel's own aspect). When it is present the cover is set
# from it verbatim and no type is drawn again, because setting type over a finished cover
# doubles the title.
FINAL_ART = OUT / "cover-art-final.png"

DPI = 300
TRIM_W, TRIM_H = 5.5, 8.5
BLEED = 0.125
CALIPER = 0.002252          # white paper, inches per page (KDP figure, verified 2026-08-12)

# Only used when no interior has been typeset: 46,359 words at ~230 wpp + doors + matter.
PAGES_EST = 236

BG = (10, 10, 11)
DOOR = (18, 18, 20)
FRAME = (44, 44, 48)
NUM = (86, 86, 92)
CREAM = (236, 228, 213)
DIM = (150, 143, 130)
RED = (150, 28, 18)
CREAM_FIELD = (242, 234, 219)       # the plate layout's paper
INK = (30, 22, 20)                  # type on that paper, and on snow
GREEN = (25, 74, 44)                # the full-bleed layout's type: dark forest on snow
LIME = (124, 236, 20)               # the supplied front's own title green
PLATES = BOOK / "art" / "illustrations" / "print"   # 24 untitled plates, 1 per night
BACK_DOORS = (8, 3)                 # 24 windows on the back, as a calendar reads


TITLE_FONT = "Creepster-Regular.ttf"


def font(name, size):
    """Resolve a face from the vendored display fonts first, then from Windows."""
    local = ART_FONTS / name
    return ImageFont.truetype(str(local if local.is_file() else FONTS / name), size)


def tracked(draw, xy, text, f, fill, tracking=0.0, center_on=None):
    widths = [f.getlength(ch) + tracking for ch in text]
    total = sum(widths) - tracking
    x, y = xy
    if center_on is not None:
        x = center_on - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += w
    return total


def tracked_center(draw, cx, cy, text, f, fill, tracking=0.0):
    """Draw tracked text centred on a point, using the glyph box, not the line box."""
    widths = [f.getlength(ch) + tracking for ch in text]
    total = sum(widths) - tracking
    bb = f.getbbox(text)
    x, y = cx - total / 2, cy - (bb[1] + bb[3]) / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += w


def fit_font(word, max_width, start=300, face=TITLE_FONT):
    size = start
    while size > 20:
        f = font(face, size)
        if sum(f.getlength(c) for c in word) + 0.10 * size * (len(word) - 1) <= max_width:
            return f
        size -= 2
    return font(face, 20)


def tracked_width(f, text, tracking):
    return sum(f.getlength(ch) for ch in text) + tracking * (len(text) - 1)


def load_art(path, w, h):
    """Cover-fit the supplied painting to the front panel, centre-cropped.

    Nothing is stretched: the panel takes the largest centre crop whose aspect is the
    panel's, so the composition survives and only the edges give way. The image is
    then sharpened once, because upscaling 1000 px to a 1650 px panel with LANCZOS
    alone looks soft under ink.
    """
    art = Image.open(path).convert("RGB")
    scale = max(w / art.width, h / art.height)
    art = art.resize((max(w, int(round(art.width * scale))),
                      max(h, int(round(art.height * scale)))), Image.LANCZOS)
    left = (art.width - w) // 2
    top = (art.height - h) // 2
    return art.crop((left, top, left + w, top + h)).filter(
        ImageFilter.UnsharpMask(radius=1.3, percent=55, threshold=2))


def scrim(w, h, top=232, top_end=0.315, foot=165, foot_start=0.845):
    """A vertical veil, heaviest at the head and the foot, so type has a ground.

    Returned as (colour, mask) for Image.composite: black where the mask is high.
    A straight rectangle would read as a bar; the exponent makes it fall away.
    """
    column = Image.new("L", (1, h))
    put = column.load()
    for y in range(h):
        a = 0.0
        if y < top_end * h:
            a = top * (1 - y / (top_end * h)) ** 1.6
        if y > foot_start * h:
            a = max(a, foot * ((y - foot_start * h) / (h - foot_start * h)) ** 1.3)
        put[0, y] = int(a)
    return Image.new("RGB", (w, h), (6, 9, 18)), column.resize((w, h))


# Four ways to put type on the painting. The art is fully composed - star and ribbons
# own the head, the pole runs the centre, the child stands at the foot - so the choice is
# a real one, not a preference: "plate" keeps type off the art entirely, "snowline" puts
# one line of type on the empty snow above the child, "overlay" runs the title across the
# sky and therefore across the cracked star, and "full" gives the painting the whole
# panel with all the type in one dark green on the snow.


def overlay_panel(art, w, h):
    veil, mask = scrim(w, h)
    img = Image.composite(veil, art, mask)

    # Everything is drawn on its own RGBA layer so the type can cast one soft shadow:
    # the sky behind the title is not uniformly dark, and the star is gold.
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # title: every line is set to the same measure, so the block spans the panel.
    # Cap heights differ between lines because the words differ in length - that is the
    # point of the setting, and it is why CHRISTMAS can stand a third larger than
    # TERROR BEFORE while both still reach the same edges.
    max_w = int(w * 0.90)
    y = int(h * 0.045)
    for line in TITLE_LINES:
        f = fit_font(line, max_w, start=300)
        while tracked_width(f, line, 0.02 * f.size) > max_w and f.size > 24:
            f = font(TITLE_FONT, f.size - 2)
        tracked_center(draw, w / 2, y + f.size * 0.46, line, f, CREAM,
                       tracking=0.02 * f.size)
        y += int(f.size * 0.84)

    # subtitle, two quiet lines under a hairline
    y += int(h * 0.012)
    draw.line([w / 2 - int(w * 0.11), y, w / 2 + int(w * 0.11), y],
              fill=(196, 74, 52, 210), width=3)
    y += int(h * 0.026)
    for line, maxsize, track in ((SUBTITLE[0], 46, 11), (SUBTITLE[1], 34, 7)):
        f = font("georgia.ttf", maxsize)
        while tracked_width(f, line, track) > w * 0.82 and f.size > 12:
            f = font("georgia.ttf", f.size - 1)
        tracked_center(draw, w / 2, y + f.size * 0.5, line, f, (232, 216, 194),
                       tracking=track)
        y += int(f.size * 1.55)

    # author at the foot, clear of the trim edge
    af = font("georgia.ttf", 64)
    while tracked_width(af, AUTHOR, 17) > w * 0.66 and af.size > 20:
        af = font("georgia.ttf", af.size - 1)
    tracked_center(draw, w / 2, h - 0.46 * DPI, AUTHOR, af, CREAM, tracking=17)

    return with_shadow(img, layer)


def with_shadow(img, layer, strength=0.62):
    """One soft shadow under all type on a layer, so it survives a light background."""
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(7)))
    shadow = Image.composite(Image.new("RGBA", img.size, (0, 0, 0, int(255 * strength))),
                             Image.new("RGBA", img.size, (0, 0, 0, 0)),
                             shadow.getchannel("A"))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def plate_panel(art, w, h):
    """The painting as a plate on cream paper, every word in the margins.

    Nothing in the picture is covered, so the star, the drips, the hand in the gift and
    the child all stay readable; the cost is that the art gives up the full bleed.
    """
    field = Image.new("RGB", (w, h), CREAM_FIELD)
    draw = ImageDraw.Draw(field)

    band_top = int(1.52 * DPI)     # room for a title that spans the panel, not a caption
    band_foot = int(0.85 * DPI)
    art_h = h - band_top - band_foot - int(0.18 * DPI)
    art_w = int(art_h * art.width / art.height)
    x = (w - art_w) // 2
    y = band_top + int(0.09 * DPI)
    field.paste(art.resize((art_w, art_h), Image.LANCZOS), (x, y))
    draw.rectangle([x - 7, y - 7, x + art_w + 6, y + art_h + 6],
                   outline=(146, 36, 28), width=3)

    # title above the plate, fitted to the band rather than to the panel
    size = int(0.44 * DPI)
    while size > 20 and any(tracked_width(font(TITLE_FONT, size), line, 0.02 * size)
                           > w * 0.86 for line in TITLE_LINES):
        size -= 2
    ty = int(0.10 * DPI)
    for line in TITLE_LINES:
        f = font(TITLE_FONT, size)
        tracked_center(draw, w / 2, ty + size * 0.46, line, f, INK, tracking=0.02 * size)
        ty += int(size * 0.80)

    ty += int(0.03 * DPI)
    draw.line([w / 2 - int(w * 0.10), ty, w / 2 + int(w * 0.10), ty],
              fill=(146, 36, 28), width=3)
    ty += int(0.09 * DPI)
    for line, maxsize, track in ((SUBTITLE[0], 30, 6), (SUBTITLE[1], 23, 4)):
        f = font("georgia.ttf", maxsize)
        while tracked_width(f, line, track) > w * 0.84 and f.size > 12:
            f = font("georgia.ttf", f.size - 1)
        tracked_center(draw, w / 2, ty, line, f, (74, 32, 26), tracking=track)
        ty += int(f.size * 1.6)

    af = font("georgia.ttf", 50)
    tracked_center(draw, w / 2, h - int(0.46 * DPI), AUTHOR, af, INK, tracking=15)
    return field


def snowline_panel(art, w, h):
    """Full bleed; one line of title on the snow between the hooves and the child."""
    img = art.copy()
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    af = font("georgia.ttf", 36)
    tracked_center(draw, w / 2, int(0.760 * h), AUTHOR, af, INK, tracking=13)

    size = int(0.44 * DPI)
    while size > 24 and tracked_width(font(TITLE_FONT, size), TITLE_ONE_LINE,
                                      0.03 * size) > w * 0.86:
        size -= 2
    f = font(TITLE_FONT, size)
    cy = int(0.818 * h)
    tracked_center(draw, w / 2, cy, TITLE_ONE_LINE, f, INK, tracking=0.03 * size)
    draw.line([w / 2 - int(w * 0.16), cy + size * 0.72, w / 2 + int(w * 0.16),
               cy + size * 0.72], fill=(146, 36, 28, 220), width=3)
    return with_shadow(img, layer, strength=0.22)


def full_panel(art, w, h):
    """Full bleed: the painting owns the panel, and every word is one dark green.

    The colour is geometry, not taste. Measured in this art: the sky runs at 56 luma and
    the snow at the foot at 211, so green type only survives on the light ground. The
    title therefore sits on the snow above the child rather than through her, the author
    is set small at the left, and the subtitle takes the last clean strip under her feet,
    held 0.25 in inside the trim edge.

    One soft shadow, not a panel: it separates the letters from the blood pools and the
    deer without putting a layer between the reader and the painting.
    """
    img = art.copy()
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    size = int(0.62 * DPI)
    while size > 24 and any(tracked_width(font(TITLE_FONT, size), line, 0.02 * size)
                            > w * 0.86 for line in TITLE_LINES):
        size -= 2
    ty = int(0.700 * h)
    for line in TITLE_LINES:
        f = font(TITLE_FONT, size)
        tracked_center(draw, w / 2, ty + size * 0.46, line, f, GREEN, tracking=0.02 * size)
        ty += int(size * 0.80)

    for line, maxsize, track, at in ((SUBTITLE[0], 30, 6, 0.928),
                                     (SUBTITLE[1], 24, 4, 0.958)):
        f = font("georgia.ttf", maxsize)
        while tracked_width(f, line, track) > w * 0.84 and f.size > 12:
            f = font("georgia.ttf", f.size - 1)
        tracked_center(draw, w / 2, int(at * h), line, f, GREEN, tracking=track)

    # 0.22, not 0.17: at 0.17 the author's first letter measured 0.243 in from the trim
    # edge, seven thousandths inside KDP's 0.25 in safe area.
    tracked_center(draw, int(w * 0.22), int(0.880 * h), AUTHOR,
                   font("georgia.ttf", 44), GREEN, tracking=13)
    return with_shadow(img, layer, strength=0.35)


def supplied_panel(path, w, h):
    """The author's finished front at trim, nothing added over the design.

    The supplied file is a full-bleed 6 x 9 in design (1800 x 2700, 2:3) and this panel is
    5.5 x 8.5 in (0.647), so 3% of the aspect has to go somewhere. Cropping it takes
    0.083 in off each side and the subtitle already sits 0.103 in from the right trim, so
    a crop eats the type. Filling the bleed box instead squeezes the art's own 0.097 in
    head margin into the bleed, which cuts 0.033 in off the top of the title at trim.

    So the art is placed at trim at her composition and the aspect difference is taken as
    a 3% horizontal compression - the same one the ebook cover gets, so the two fronts
    match - and the bleed around it is built by extending the edge pixels, never by
    mirroring. The design's outer inch is dark in every direction, so the extension is a
    dark band in the bleed: no seam, no reversed title, no invented content, and nothing
    cut at the trim line.
    """
    art = Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)
    return art.filter(ImageFilter.UnsharpMask(radius=1.0, percent=32, threshold=2))


def edge_pad(img, left, top, right, bottom):
    """Grow a panel into the bleed from its own edges: exact at the trim, soft outside.

    Not a mirror, and not a repeated line. A mirror pastes reversed art into the bleed,
    which on this front put a flipped copy of the green title at the head and of the gold
    byline at the foot, with a hard seam where the reflection began. A repeated line has
    no seam but drags any patch on the edge - the foot's cream and blue-grey - straight
    down the band as stripes.

    So each band starts as the panel's outermost line, which is continuous with the trim
    at the fold, and fades to a heavy blur of that same line by the page edge. Nothing is
    invented and nothing reverses: the band only ever carries colours already on the
    edge, and it is trimmed away, so it is never printed.
    """
    w, h = img.size
    out = Image.new("RGB", (w + left + right, h + top + bottom))
    out.paste(img, (left, top))
    if left:
        out.paste(img.crop((0, 0, 1, h)).resize((left, h)), (0, top))
    if right:
        out.paste(img.crop((w - 1, 0, w, h)).resize((right, h)), (left + w, top))
    if top:
        out.paste(img.crop((0, 0, w, 1)).resize((w, top)), (left, 0))
    if bottom:
        out.paste(img.crop((0, h - 1, w, h)).resize((w, bottom)), (left, top + h))
    for x0, y0 in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        bw = left if x0 == 0 else right
        bh = top if y0 == 0 else bottom
        if bw and bh:
            out.paste(img.crop((x0, y0, x0 + 1, y0 + 1)).resize((bw, bh)),
                      (0 if x0 == 0 else left + w, 0 if y0 == 0 else top + h))
    return feather_bleed(out, left, top, right, bottom)


def feather_bleed(img, left, top, right, bottom):
    """Soften each bleed band away from the trim, leaving its inner edge untouched.

    The band's inner edge keeps the panel's own outermost line, so the join is invisible;
    at the page edge the band is a wide blur of that line, so an edge patch reads as paper
    going soft rather than as a stripe. Blur is horizontal along the band, which is where
    the stripes were: the band is uniform down its depth by construction.
    """
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    H, W = a.shape[:2]
    blk = a.copy()

    def band(line, depth, lean_out):
        soft = np.asarray(Image.fromarray(line[None].astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(max(4.0, len(line) / 14.0))), dtype=np.float32)[0]
        t = np.linspace(0.0, 1.0, depth)[:, None, None]
        if lean_out:
            t = t[::-1]
        return line[None] * (1 - t) + soft[None] * t

    if top:
        blk[:top] = band(a[0], top, True)
    if bottom:
        blk[H - bottom:] = band(a[H - 1], bottom, False)
    if left:
        blk[:, :left] = np.transpose(band(a[:, 0], left, True), (1, 0, 2))
    if right:
        blk[:, W - right:] = np.transpose(band(a[:, W - 1], right, False), (1, 0, 2))
    return Image.fromarray(np.clip(blk, 0, 255).astype(np.uint8))


def front_panel(art, w, h, variant="full"):
    return {"overlay": overlay_panel, "plate": plate_panel, "full": full_panel,
            "snowline": snowline_panel}[variant](art, w, h)


def bleed_extend(img, bleed):
    """Grow the front panel into the bleed along its three outer edges.

    Left is the spine fold, where the art has to stop dead; the other three edges are
    trimmed, so they must carry art past the trim line or a pale sliver can survive a
    trim that drifts by a sixty-fourth. The mirrored strip is cut off, never seen.
    """
    w, h = img.size
    out = Image.new("RGB", (w + bleed, h + 2 * bleed))
    out.paste(img, (0, bleed))
    out.paste(img.crop((w - bleed, 0, w, h)).transpose(Image.FLIP_LEFT_RIGHT), (w, bleed))
    strip = out.crop((0, bleed, out.width, bleed + bleed)).transpose(Image.FLIP_TOP_BOTTOM)
    out.paste(strip, (0, 0))
    strip = out.crop((0, out.height - 2 * bleed, out.width, out.height - bleed))
    out.paste(strip.transpose(Image.FLIP_TOP_BOTTOM), (0, out.height - bleed))
    return out


def back_panel(w, h, bleed, trim_px, spine_px):
    """The back cover: the painting at night, the title, the blurb, 24 windows.

    The panel is built here rather than left as flat black because a 7.2 pt paragraph on
    six inches of empty ink is the one thing a proofreader sees first. The painting is
    carried across the back at 30% so the back and front read as one object around the
    spine; the 24 untitled plates sit under the copy as the calendar the book is.

    Text lives between 0.40 in and the trim edge minus 0.40 in, and the bottom-right
    2.0 x 1.2 in is left clear in paper cream for the barcode KDP prints there.
    """
    art = Image.open(ART).convert("RGB")
    scale = max(w / art.width, h / art.height)
    art = art.resize((max(w, int(round(art.width * scale))),
                      max(h, int(round(art.height * scale)))), Image.LANCZOS)
    left, top = (art.width - w) // 2, (art.height - h) // 2
    art = art.crop((left, top, left + w, top + h)).filter(ImageFilter.GaussianBlur(3))
    art = Image.blend(Image.new("RGB", (w, h), BG), art, 0.30)
    veil, mask = scrim(w, h, top=120, top_end=0.42, foot=90, foot_start=0.92)
    img = Image.composite(veil, art, mask)

    # a soft ground under the copy: the pole, the deer and the reindeer legs run straight
    # through the middle of the panel, and 9 pt on 30% art needs a darker bed than that
    ground = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(ground).rectangle(
        [bleed + int(0.22 * DPI), int(0.30 * DPI),
         bleed + trim_px - int(0.22 * DPI), int(5.45 * DPI)], fill=(6, 8, 14, 128))
    img = Image.alpha_composite(img.convert("RGBA"),
                                ground.filter(ImageFilter.GaussianBlur(26))).convert("RGB")

    inner = int(0.40 * DPI)
    x0, x1 = bleed + inner, bleed + trim_px - inner
    cx, max_w = (x0 + x1) / 2, x1 - x0

    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # title: each line fitted to the same measure, as on the front
    y = int(0.42 * DPI)
    for line in TITLE_LINES:
        f = fit_font(line, max_w, start=260)
        tracked_center(d, cx, y + f.size * 0.46, line, f, LIME, tracking=0.02 * f.size)
        y += int(f.size * 0.84)

    d.line([cx - max_w * 0.16, y + int(0.06 * DPI), cx + max_w * 0.16,
            y + int(0.06 * DPI)], fill=(196, 74, 52, 220), width=3)
    y += int(0.16 * DPI)
    af = font("georgia.ttf", 52)
    tracked_center(d, cx, y, AUTHOR, af, CREAM, tracking=16)
    y += int(0.22 * DPI)

    # blurb: 38 px is 9.1 pt, readable at arm's length on paper; the panel runs to
    # y > H before the windows start
    bf = font("georgia.ttf", 38)
    y += int(0.10 * DPI)
    for para in (OUT / "back-cover.txt").read_text(encoding="utf-8").strip().split("\n\n"):
        for line in wrap_text(d, " ".join(para.split()), bf, max_w):
            d.text((x0, y), line, font=bf, fill=CREAM)
            y += 56
        y += 26

    img = with_shadow(img, layer, strength=0.55)

    # 24 windows, 8 across and 3 down, in the lower third
    cols, rows = BACK_DOORS
    cell, gap = 150, 12
    gw = cols * cell + (cols - 1) * gap
    gh = rows * cell + (rows - 1) * gap
    gx = bleed + (trim_px - gw) // 2
    gy = int(0.720 * h) - gh // 2
    d2 = ImageDraw.Draw(img)
    for i in range(cols * rows):
        cx_i = gx + (i % cols) * (cell + gap)
        cy_i = gy + (i // cols) * (cell + gap)
        plate = Image.open(PLATES / ("%02d.jpg" % (i + 1))).convert("RGB")
        s = max(cell / plate.width, cell / plate.height)
        plate = plate.resize((max(cell, int(plate.width * s)),
                              max(cell, int(plate.height * s))), Image.LANCZOS)
        l2 = (plate.width - cell) // 2
        t2 = (plate.height - cell) // 2
        img.paste(plate.crop((l2, t2, l2 + cell, t2 + cell)), (cx_i, cy_i))
        d2.rectangle([cx_i, cy_i, cx_i + cell - 1, cy_i + cell - 1],
                     outline=(146, 36, 28), width=2)

    # barcode: KDP prints it bottom-right; the ground there stays paper cream
    bw, bh = int(2.0 * DPI), int(1.2 * DPI)
    bx = bleed + trim_px - int(0.30 * DPI) - bw
    by = h - int(0.30 * DPI) - bh
    d2.rectangle([bx, by, bx + bw, by + bh], fill=CREAM_FIELD)
    print("back       title y %.2f in, blurb to %.2f in, windows %.2f-%.2f in, barcode %.2f-%.2f in"
          % (0.42, y / DPI, gy / DPI, (gy + gh) / DPI, by / DPI, (by + bh) / DPI))
    return img


def wrap_text(draw, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def build_wrap(front, spine_in, extend=False, supplied=False):
    """Assemble back, spine and front on a page measured in whole pixels.

    The page is 2*bleed + 2*trim + spine pixels wide and 2*bleed + trim tall, and the
    typst page is that pixel count over 300 dpi. So one image pixel is one page pixel: the
    PDF and the JPG are the same picture, and nothing is stretched by the 100% x 100%
    image box or clipped at an edge that does not divide evenly by 300.
    """
    bleed = int(round(BLEED * DPI))
    spine_px = int(round(spine_in * DPI))
    trim_px = int(round(TRIM_W * DPI))
    trim_h_px = int(round(TRIM_H * DPI))
    W = 2 * bleed + 2 * trim_px + spine_px
    H = 2 * bleed + trim_h_px
    w_in, h_in = W / DPI, H / DPI
    front_x = bleed + trim_px + spine_px

    img = Image.new("RGB", (W, H), BG)
    img.paste(back_panel(bleed + trim_px, H, bleed, trim_px, spine_px), (0, 0))
    draw = ImageDraw.Draw(img)

    if supplied:
        # the author's finished front: art at trim, edges continued into the bleed
        img.paste(edge_pad(front, 0, bleed, bleed, bleed), (front_x, 0))
    elif extend:
        # full bleed: art runs over the three trimmed edges, but stops at the spine fold
        img.paste(bleed_extend(front, bleed).resize((trim_px + bleed, H), Image.LANCZOS),
                  (front_x, 0))
    else:
        img.paste(front.resize((trim_px, trim_h_px), Image.LANCZOS), (front_x, bleed))

    # spine: author set in the usable band, rotated to read bottom-to-top
    band = spine_in - 2 * 0.0625
    if band > 0.14:
        sf = font("georgia.ttf", int(min(40, band * DPI * 0.55)))
        layer = Image.new("RGBA", (int(TRIM_H * DPI), spine_px), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(layer)
        tracked_center(sdraw, layer.width / 2, spine_px / 2, AUTHOR, sf, CREAM, tracking=6)
        layer = layer.rotate(90, expand=True)
        img.paste(layer, (bleed + trim_px + (spine_px - layer.width) // 2,
                          bleed + (int(TRIM_H * DPI) - layer.height) // 2), layer)

    return img, w_in, h_in, spine_px, bleed, trim_px


def ink_box(img, box):
    """Bounding box of bright ink inside a crop, or None."""
    strip = img.crop(box).convert("L")
    return strip.point(lambda v: 255 if v > 110 else 0).getbbox()


def wrap_pdf(jpg_name, w_px, h_px, stem="cover-wrap"):
    """One page, sized from the JPG's pixel count in points, so it maps 1:1.

    Inches rounded to four places left the page 0.004 pt shorter than the image, which
    typst then had to absorb by scaling the picture by 0.00007 in. Points divide evenly
    (3500 px = 840 pt, 2626 px = 630.24 pt at 300 dpi), so the image is placed at its own
    size and the PDF and the JPG are the same picture.
    """
    import typst
    src = (
        "#set page(width: %.4fpt, height: %.4fpt, margin: 0pt, fill: white)\n"
        "#image(\"%s\", width: 100%%, height: 100%%)\n" % (w_px / DPI * 72, h_px / DPI * 72,
                                                          jpg_name)
    )
    (OUT / (stem + ".typ")).write_text(src, encoding="utf-8")
    typst.compile(str(OUT / (stem + ".typ")), output=str(OUT / (stem + ".pdf")))
    return OUT / (stem + ".pdf")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    measured = META.is_file()
    pages = int(json.loads(META.read_text(encoding="utf-8"))["pages"]) if measured else PAGES_EST

    variant = sys.argv[1] if len(sys.argv) > 1 else (
        "supplied" if FINAL_ART.is_file() else "full")
    if variant not in ("overlay", "plate", "snowline", "full", "supplied"):
        raise SystemExit("layout must be overlay, plate, snowline, full or supplied")

    if variant == "supplied":
        if not FINAL_ART.is_file():
            raise SystemExit("finished front missing: put it at %s" % FINAL_ART)
        W, H = int(TRIM_W * DPI), int(TRIM_H * DPI)
        source = Image.open(FINAL_ART)
        front = supplied_panel(FINAL_ART, W, H)
        print("layout     supplied (author's finished front, no type drawn here)")
        print("art        %s  %dx%d px -> %dx%d at trim (%.2fx)"
              % (FINAL_ART.name, source.width, source.height, W, H, W / source.width))
    else:
        if not ART.is_file():
            raise SystemExit("cover art missing: put the painting at %s" % ART)
        W, H = int(TRIM_W * DPI), int(TRIM_H * DPI)
        source = Image.open(ART)
        front = front_panel(load_art(ART, W, H), W, H, variant)
        print("layout     %s" % variant)
        print("art        %s  %dx%d px -> %d dpi at trim (upscaled %.2fx)"
              % (ART.name, source.width, source.height,
                 round(source.width / TRIM_W), W / source.width))

    front.save(OUT / "cover-front.jpg", quality=95, dpi=(DPI, DPI))

    spine_in = pages * CALIPER
    wrap, w_in, h_in, spine_px, bleed, trim_px = build_wrap(
        front, spine_in, extend=(variant == "full"),
        supplied=(variant == "supplied"))

    # ADVENT_COVER_PREVIEW=1 writes cover-wrap-preview.* and leaves the upload files
    # alone, so a new back can be looked at before it replaces anything.
    preview = os.environ.get("ADVENT_COVER_PREVIEW") == "1"
    stem = ("cover-wrap-preview" if preview else
            ("cover-wrap" if measured else "cover-wrap-comp"))
    jpg = OUT / (stem + ".jpg")
    wrap.save(jpg, quality=95, dpi=(DPI, DPI))

    # the spine band must hold its type: ink inside it, clear of both folds
    bbox = ink_box(wrap, (bleed + trim_px, bleed, bleed + trim_px + spine_px,
                          bleed + int(TRIM_H * DPI)))
    if bbox:
        left_clear = bbox[0] / DPI
        right_clear = (spine_px - bbox[2]) / DPI
        spine_note = ("ink %.3f in from the back fold, %.3f in from the front fold"
                      % (left_clear, right_clear))
    else:
        spine_note = "no spine ink"

    print("front      %s  %dx%d px (%.2f x %.2f in)" % (OUT / "cover-front.jpg", W, H,
                                                        TRIM_W, TRIM_H))
    print("wrap       %s  %dx%d px (%.4f x %.4f in)" % (jpg, wrap.width, wrap.height,
                                                       w_in, h_in))
    print("extent     %d pages (%s)" % (pages, "measured" if measured else "ESTIMATED"))
    print("spine      %.4f in (%.2f mm)   usable band %.3f in" % (spine_px / DPI,
                                                                  spine_px / DPI * 25.4,
                                                                  spine_px / DPI - 0.125))
    print("spine ink  %s" % spine_note)
    print("folds      %.4f in and %.4f in from the left edge" % ((bleed + trim_px) / DPI,
                                                                 (bleed + trim_px + spine_px) / DPI))
    if measured:
        pdf = wrap_pdf(jpg.name, wrap.width, wrap.height, stem)
        import pypdf
        r = pypdf.PdfReader(str(pdf))
        box = r.pages[0].mediabox
        print("wrap pdf   %s  %d page, %.4f x %.4f in" % (pdf, len(r.pages),
                                                          float(box.width) / 72,
                                                          float(box.height) / 72))
        stale = OUT / "cover-wrap-comp.jpg"
        if stale.is_file() and not preview:
            stale.unlink()
            print("removed    %s (superseded by the measured wrap)" % stale.name)


if __name__ == "__main__":
    main()
