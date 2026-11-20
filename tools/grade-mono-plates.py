#!/usr/bin/env python3
"""Grade the 24 titled plates for the black-ink edition.

A plain desaturation is not good enough for this art: four plates use hue *as* their
light source (Day 13's lit rig, 19's beam, 22's star, 23's radiator glow) and collapse
to grey on grey when converted with Rec.709 luma. So the grade is:

  * a red-sensitive channel mix, the old panchromatic trick: warm accents (red door,
    red sofa, red canyon, porch light) stay light, blues and greens sink;
  * auto-levels taken from the art area only, so the near-black title band cannot drag
    the black point down;
  * a shadow lift plus a mild S-curve, which is what puts the light-source plates back
    into the mid-tones;
  * a rounded-shoulder pull-down over the top fifth, so the white Creepster cards keep
    at least 4.5:1 contrast whatever the grade does below them;
  * a small unsharp pass, because flat vector-ish art under one ink loses edge at 1024 px.

Writes art/illustrations/mono/print/NN.jpg at the same 1024 x 1536 as the colour plates,
so pagination is identical and the spine does not move.
"""

from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageFilter

BOOK = Path(__file__).resolve().parents[1] / "test-books" / "advent-horror"
SRC = BOOK / "art" / "illustrations" / "titled" / "print"
DST = BOOK / "art" / "illustrations" / "mono" / "print"

MIX = (0.45, 0.40, 0.15)   # red-sensitive mix
GAMMA = 0.80               # shadow lift
SCURVE = 1.10              # midtone contrast
FLOOR, CEIL = 0.055, 0.96  # print-safe black and paper white
BAND = 0.20                # the title card lives in the top fifth
BAND_MAX = 0.18            # mean under the card; white type on it keeps >= 4.5:1
MIN_CONTRAST = 4.5


def grade(img):
    a = np.asarray(img, dtype=np.float32)
    g = MIX[0] * a[..., 0] + MIX[1] * a[..., 1] + MIX[2] * a[..., 2]
    h = g.shape[0]

    art = g[int(h * 0.25):]                     # below the card: real tonal range
    lo, hi = np.percentile(art, 2.0), np.percentile(art, 99.5)
    g = np.clip((g - lo) / max(hi - lo, 8.0), 0.0, 1.0)
    g = g ** GAMMA
    g = np.clip(0.5 + (g - 0.5) * SCURVE, 0.0, 1.0)
    g = FLOOR + g * (CEIL - FLOOR)

    # Pull the card band down, easing out by BAND. Iterated, because the eased rows lower
    # the band mean less than a flat multiply would; one pass left Day 21 at 4.4:1.
    rows = np.arange(h, dtype=np.float32) / h
    k = (np.clip((BAND - rows) / BAND, 0.0, 1.0) ** 1.5)[:, None]
    for _ in range(6):
        band_mean = g[: int(h * BAND)].mean()
        if band_mean <= BAND_MAX:
            break
        g = g * (1.0 - k * (1.0 - BAND_MAX / band_mean))

    return np.clip(g * 255.0, 0, 255).astype(np.uint8)


def stats(im):
    a = np.asarray(im, dtype=np.float32)
    h = a.shape[0]
    band = a[: int(h * BAND)]
    art = a[int(h * 0.25):]
    return {
        "band": band.mean(),
        "art": art.mean(),
        "sd": art.std(),
        "contrast": (250.0 + 12.05) / (band.mean() + 12.05),
        "mid": float(((art > 60) & (art < 200)).mean() * 100),
    }


def main():
    DST.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob("*.jpg"))
    if len(files) != 24:
        raise SystemExit("expected 24 plates, found %d" % len(files))

    print("%-4s %-7s %-7s %-7s %-6s %s" % ("day", "band", "art", "mid%", "W:B", "moved >8"))
    bad = []
    for f in files:
        rgb = Image.open(f).convert("RGB")
        before = np.asarray(rgb.convert("L"), dtype=np.int16)
        graded = grade(rgb)
        im = Image.fromarray(graded, mode="L")
        im = im.filter(ImageFilter.UnsharpMask(radius=2.0, percent=55, threshold=3))
        im.save(DST / f.name, quality=92, subsampling=0)

        s = stats(im)
        moved = float((np.abs(im_arr := np.asarray(im, dtype=np.int16) - before) > 8).mean() * 100)
        print("%-4s %6.1f %7.1f %7.1f %6.1f %8.1f%%"
              % (f.stem, s["band"], s["art"], s["mid"], s["contrast"], moved))
        if s["contrast"] < MIN_CONTRAST:
            bad.append((f.stem, round(s["contrast"], 1)))

    print()
    print("plates written  %s" % DST)
    if bad:
        print("CARD CONTRAST BELOW 4.5:1  %s" % bad)
        return 1
    print("cards           all %d plates >= %.1f:1" % (len(files), MIN_CONTRAST))
    return 0


if __name__ == "__main__":
    sys.exit(main())
