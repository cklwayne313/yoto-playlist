#!/usr/bin/env python3
"""Export vendor-ready files at 54 x 85.5 mm.

    python3 .opencode/print/build_vendor.py

Two sets:
  vendor/trim/<name>.jpg    638 x 1010 px @300dpi, exact 54 x 85.5 mm, no bleed
  vendor/bleed/<name>.jpg   709 x 1081 px @300dpi, 3 mm bleed, trim area unchanged

The bleed is made by extending the edge pixels outward, not by scaling the art,
so the part that gets trimmed off is identical to the trim file.
"""

import glob
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "vendor")

DPI = 300
W_MM, H_MM = 54.0, 85.5
BLEED_MM = 3.0

TRIM = (round(W_MM / 25.4 * DPI), round(H_MM / 25.4 * DPI))          # 638 x 1010
BL = round(BLEED_MM / 25.4 * DPI)                                    # 35 px
FULL = (TRIM[0] + BL * 2, TRIM[1] + BL * 2)                          # 708 x 1080


def trim_image(im):
    tw, th = TRIM
    target = tw / th
    w, h = im.size
    if w / h > target:
        nw = round(h * target)
        im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = round(w / target)
        im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
    return im.resize((tw, th), Image.LANCZOS)


def add_bleed(im):
    tw, th = im.size
    canvas = Image.new("RGB", FULL)
    canvas.paste(im, (BL, BL))

    left = im.crop((0, 0, 1, th)).resize((BL, th))
    right = im.crop((tw - 1, 0, tw, th)).resize((BL, th))
    top = im.crop((0, 0, tw, 1)).resize((tw, BL))
    bottom = im.crop((0, th - 1, tw, th)).resize((tw, BL))

    canvas.paste(left, (0, BL))
    canvas.paste(right, (BL + tw, BL))
    canvas.paste(top, (BL, 0))
    canvas.paste(bottom, (BL, BL + th))

    for sx, sy, dx, dy in ((0, 0, 0, 0), (tw - 1, 0, BL + tw, 0),
                           (0, th - 1, 0, BL + th), (tw - 1, th - 1, BL + tw, BL + th)):
        px = im.crop((sx, sy, sx + 1, sy + 1)).resize((BL, BL))
        canvas.paste(px, (dx, dy))
    return canvas


def main():
    os.makedirs(os.path.join(OUT, "trim"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "bleed"), exist_ok=True)

    covers = sorted(glob.glob(os.path.join(ROOT, "playlists", "*", "cover.jpg")))
    for path in covers:
        name = os.path.basename(os.path.dirname(path))
        im = trim_image(Image.open(path).convert("RGB"))
        im.save(os.path.join(OUT, "trim", f"{name}.jpg"), dpi=(DPI, DPI),
                quality=95, subsampling=0, optimize=True)
        add_bleed(im).save(os.path.join(OUT, "bleed", f"{name}.jpg"), dpi=(DPI, DPI),
                           quality=95, subsampling=0, optimize=True)

    print(f"{len(covers)} cards -> vendor/trim ({TRIM[0]}x{TRIM[1]}) "
          f"and vendor/bleed ({FULL[0]}x{FULL[1]})")


if __name__ == "__main__":
    main()
