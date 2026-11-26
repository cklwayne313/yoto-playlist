#!/usr/bin/env python3
"""Set the mark and title onto a text-free card image.

    python3 typeset_cover.py --image /tmp/opencode/nt-fav.png \
        --colour-from playlists/super-simple-favourites/cover.jpg \
        --title MY FAVOURITES --out playlists/super-simple-favourites/cover.jpg

Layout rules (at 638 x 1011):
  * 7% side margins, so a title never runs into the card edge.
  * The HimHim mark sits directly above the title, flush with its left edge —
    one lockup, not a logo floating in the corner.
  * The title block is top-aligned, not floated mid-space, and stops 3% above
    the character's head.
  * Character pixels are never written to; only the band above them is drawn on.
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_brand import render_mark, colours_for  # noqa: E402
from make_cover import ensure_font, finish_hand, render_hand_line  # noqa: E402

W, H = 638, 1011
MARGIN = 0.07
MARK_TOP = 0.052
MARK_SIZE = 40
MARK_GAP = 0.022
BOTTOM_GAP = 0.030


def title_colour(im):
    w, h = im.size
    band = np.asarray(im.crop((0, int(h * .10), w, int(h * .30)))).astype(np.float32)
    lum = band[:, :, 0] * .299 + band[:, :, 1] * .587 + band[:, :, 2] * .114
    if np.median(lum) > 128:
        sel = lum < np.percentile(lum, 4)
    else:
        sel = lum > np.percentile(lum, 96)
    return tuple(int(v) for v in band[sel].mean(axis=0))


def character_top(im):
    """First row where the art departs from the background colour."""
    arr = np.asarray(im.convert("RGB")).astype(np.float32)
    h, w, _ = arr.shape
    corners = np.array([arr[3, 3], arr[3, w - 4], arr[3, w // 2]], dtype=np.float32)
    bg = np.median(corners, axis=0)
    dist = np.sqrt(((arr - bg) ** 2).sum(axis=2))
    rows = (dist > 40).sum(axis=1) > w * 0.02
    idx = np.argmax(rows)
    return int(idx) if rows.any() else int(h * .5)


def fit_line(text, font_path, max_w, max_h):
    size = 400
    while size > 20:
        font = __import__("make_cover").load_font(font_path, size)
        bb = font.getbbox(text)
        if bb[2] - bb[0] <= max_w and bb[3] - bb[1] <= max_h:
            return size
        size -= 4
    return 20


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="text-free card art")
    ap.add_argument("--title", nargs="+", required=True)
    ap.add_argument("--colour", default=None, help="#RRGGBB; default samples the old title")
    ap.add_argument("--colour-from", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--no-mark", action="store_true")
    args = ap.parse_args()

    im = Image.open(args.image).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)

    if args.colour:
        v = args.colour.lstrip("#")
        colour = tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))
    elif args.colour_from:
        colour = title_colour(Image.open(args.colour_from))
    else:
        colour = (38, 50, 58)

    font_path = ensure_font(None)
    char_top = character_top(im)
    max_w = W * (1 - 2 * MARGIN)

    mark = None
    if not args.no_mark:
        mark_line = render_mark("HimHim", font_path, MARK_SIZE, colours_for("two-tone", im))
        mark = finish_hand(mark_line, args.seed, grain_amount=6, blur=3, offset=3, shadow_alpha=42)

    mark_top = int(H * MARK_TOP)
    title_top = mark_top + (mark.height + int(H * MARK_GAP) if mark else 0)
    avail = char_top - int(H * BOTTOM_GAP) - title_top

    n = len(args.title)
    gap = int(avail * 0.06)
    per_line = (avail - gap * (n - 1)) / n
    size = min(fit_line(t, font_path, max_w, per_line) for t in args.title)

    lines = []
    for i, text in enumerate(args.title):
        seed = (args.seed * 131 + i * 17 + len(text)) & 0xFFFFFFFF
        line = render_hand_line(text, font_path, size, colour, seed, 1.0)
        lines.append(finish_hand(line, seed))

    block_w = max([l.width for l in lines] + ([mark.width] if mark else [0]))
    left = int((W - block_w) / 2)
    canvas = im.convert("RGBA")

    if mark:
        canvas.alpha_composite(mark, (left, mark_top))

    y = title_top
    for line in lines:
        canvas.alpha_composite(line, (int((W - line.width) / 2), y))
        y += line.height + gap

    out = canvas.convert("RGB")
    out.save(args.out, dpi=(300, 300), quality=92, optimize=True)
    print(f"{args.out}  {W}x{H}  char_top {char_top}  size {size}  block {block_w}  "
          f"title {title_top}..{y - gap}  colour #{colour[0]:02X}{colour[1]:02X}{colour[2]:02X}")


if __name__ == "__main__":
    main()
