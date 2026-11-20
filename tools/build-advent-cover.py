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
import sys

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
    """The author's finished front, fitted by width, never cropped across the type.

    The supplied file is 6 x 9 in (2:3); this panel is 5.5 x 8.5 in (0.647), so a
    crop-to-fill would take 3% off the sides - and the title in this cover reaches the
    sides. Fit by width instead: 1800 -> 1650 is 0.917x, which leaves 2475 px of image
    for a 2550 px panel. The 75 px difference is split top and bottom and filled with a
    mirrored sliver, so the composition is unchanged and the added band falls in the
    bleed, outside the trim. A side effect worth having: the title moves 0.125 in in
    from the head trim, back inside KDP's 0.25 in safe area.
    """
    art = Image.open(path).convert("RGB")
    art = art.resize((w, max(1, int(round(art.height * w / art.width)))), Image.LANCZOS)
    canvas = Image.new("RGB", (w, h))
    if art.height >= h:
        top = (art.height - h) // 2
        canvas.paste(art.crop((0, top, w, top + h)), (0, 0))
    else:
        top = (h - art.height) // 2
        canvas.paste(art, (0, top))
        band = h - art.height
        if top:
            canvas.paste(art.crop((0, 0, w, top)).transpose(Image.FLIP_TOP_BOTTOM), (0, 0))
        rest = band - top
        if rest:
            canvas.paste(art.crop((0, art.height - rest, w, art.height))
                         .transpose(Image.FLIP_TOP_BOTTOM), (0, h - rest))
    return canvas.filter(ImageFilter.UnsharpMask(radius=1.0, percent=32, threshold=2))


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


def build_wrap(front, spine_in, extend=False):
    w_in = BLEED + TRIM_W + spine_in + TRIM_W + BLEED
    h_in = TRIM_H + 2 * BLEED
    W, H = int(round(w_in * DPI)), int(round(h_in * DPI))
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    bleed = int(round(BLEED * DPI))
    spine_px = int(round(spine_in * DPI))
    trim_px = int(round(TRIM_W * DPI))
    front_x = bleed + trim_px + spine_px

    if extend:
        # full bleed: art runs over the three trimmed edges, but stops at the spine fold
        img.paste(bleed_extend(front, bleed).resize((trim_px + bleed, H), Image.LANCZOS),
                  (front_x, 0))
    else:
        img.paste(front.resize((trim_px, int(TRIM_H * DPI)), Image.LANCZOS), (front_x, bleed))

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

    # back panel: copy at the head, barcode corner kept clear
    copy = (OUT / "back-cover.txt").read_text(encoding="utf-8").strip().split("\n\n")
    bf = font("georgia.ttf", 30)
    x = bleed + 120
    max_w = trim_px - 240
    y = bleed + 150
    for para in copy:
        for line in wrap_text(draw, " ".join(para.split()), bf, max_w):
            draw.text((x, y), line, font=bf, fill=CREAM)
            y += int(bf.size * 1.55)
        y += int(bf.size * 0.75)
        if y > H - 700:
            break
    return img, w_in, h_in, spine_px, bleed, trim_px


def ink_box(img, box):
    """Bounding box of bright ink inside a crop, or None."""
    strip = img.crop(box).convert("L")
    return strip.point(lambda v: 255 if v > 110 else 0).getbbox()


def wrap_pdf(jpg_name, w_in, h_in):
    import typst
    src = (
        "#set page(width: %.4fin, height: %.4fin, margin: 0pt, fill: white)\n"
        "#image(\"%s\", width: 100%%, height: 100%%)\n" % (w_in, h_in, jpg_name)
    )
    (OUT / "cover-wrap.typ").write_text(src, encoding="utf-8")
    typst.compile(str(OUT / "cover-wrap.typ"), output=str(OUT / "cover-wrap.pdf"))
    return OUT / "cover-wrap.pdf"


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
        front, spine_in, extend=(variant in ("full", "supplied")))

    jpg = OUT / ("cover-wrap.jpg" if measured else "cover-wrap-comp.jpg")
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
    print("spine      %.4f in (%.2f mm)   usable band %.3f in" % (spine_in, spine_in * 25.4,
                                                                  spine_in - 0.125))
    print("spine ink  %s" % spine_note)
    print("folds      %.4f in and %.4f in from the left edge" % (BLEED + TRIM_W,
                                                                 BLEED + TRIM_W + spine_in))
    if measured:
        pdf = wrap_pdf(jpg.name, w_in, h_in)
        import pypdf
        r = pypdf.PdfReader(str(pdf))
        box = r.pages[0].mediabox
        print("wrap pdf   %s  %d page, %.4f x %.4f in" % (pdf, len(r.pages),
                                                          float(box.width) / 72,
                                                          float(box.height) / 72))
        stale = OUT / "cover-wrap-comp.jpg"
        if stale.is_file():
            stale.unlink()
            print("removed    %s (superseded by the measured wrap)" % stale.name)


if __name__ == "__main__":
    main()
