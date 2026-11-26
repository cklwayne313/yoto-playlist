#!/usr/bin/env python3
"""Build a custom card cover from a background plate, an official character
cut-out, the HimHim mark and a hand-lettered title.

    python3 build_cover.py --bg plate.png --char char.png \
        --title ACTION SONGS --colour '#814202' --out cover.jpg

Layout, at 638 x 1011 (54 x 85.6 mm at 300 DPI):
  * 7% side margins, so the title never runs into the card edge.
  * The mark sits in its own band at the top, flush left with the title block.
  * The title block is top-aligned and stops 3% above the character's head.
  * Type is sized to the space that is actually free, not to a fixed scale.
  * The character is pasted at its original position, never resampled.
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_brand import colours_for, render_mark  # noqa: E402
from make_cover import ensure_font, render_hand_line  # noqa: E402

W, H = 638, 1011
MARGIN = 0.07
MARK_TOP = 0.050
MARK_SIZE = 38
MARK_GAP = 0.016
BOTTOM_GAP = 0.040


def hand(layer, seed, size):
    """Grain plus a soft shadow sized to the type, so a small line does not
    carry the padding of a poster headline."""
    import numpy as np
    from PIL import ImageFilter

    rng = np.random.default_rng(seed)
    arr = np.asarray(layer).astype(np.int16)
    noise = rng.normal(0, 6, (arr.shape[0], arr.shape[1], 1))
    visible = arr[:, :, 3:4] > 0
    arr[:, :, :3] = np.where(visible, np.clip(arr[:, :, :3] + noise, 0, 255), arr[:, :, :3])
    layer = Image.fromarray(arr.astype(np.uint8))

    pad = max(2, int(size * 0.06))
    offset = max(1, int(size * 0.03))
    blur = max(1, int(size * 0.03))
    base = Image.new("RGBA", (layer.width + pad * 2, layer.height + pad * 2), (0, 0, 0, 0))
    mask = layer.split()[3].point(lambda v: int(v * 0.23))
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow.paste((25, 45, 70, 255), (pad, pad + offset), mask)
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(layer, (pad, pad))
    return base


def plate(path):
    im = Image.open(path).convert("RGB")
    scale = max(W / im.width, H / im.height)
    im = im.resize((max(W, int(im.width * scale) + 1), max(H, int(im.height * scale) + 1)),
                   Image.LANCZOS)
    left, top = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((left, top, left + W, top + H))


def character_top(char):
    alpha = np.asarray(char.split()[3])
    rows = np.where((alpha > 12).sum(axis=1) > 2)[0]
    return int(rows[0]) if len(rows) else int(H * .5)


def place_char(char, width_f, bottom_f, x_f=0.0, top_f=None):
    """Scale the cut-out to a fraction of the card width and sit it on the
    bottom edge, so a cropped body never shows a cut line. Given `top_f`, size
    it instead so its top lands at that fraction of the card height — that is
    what keeps every card's character at the same eye line."""
    if top_f is not None:
        h = max(40, int(H * (1 - bottom_f - top_f)))
        w = max(40, int(h * char.width / char.height))
    else:
        w = max(40, int(W * width_f))
    h = max(40, int(char.height * w / char.width))
    char = char.resize((w, h), Image.LANCZOS)
    x = int((W - w) / 2 + x_f * W)
    y = H - h - int(H * bottom_f)
    return char, x, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", required=True)
    ap.add_argument("--char", default=None,
                    help="character cut-out; omit for a collection card with no character")
    ap.add_argument("--title", nargs="+", required=True)
    ap.add_argument("--colour", default="#26323A")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--mark-size", type=int, default=MARK_SIZE)
    ap.add_argument("--no-mark", action="store_true")
    ap.add_argument("--mark-style", default="two-tone")
    ap.add_argument("--font", default=None, help="typeface for the title, e.g. a CJK face")
    ap.add_argument("--jitter", type=float, default=1.0)
    ap.add_argument("--max-size", type=int, default=0, help="cap the title size, in px")
    ap.add_argument("--colour2", default=None,
                    help="colour for the second title line; default is a lighter tint")
    ap.add_argument("--no-tint", action="store_true",
                    help="keep the second line the same colour as the first")
    ap.add_argument("--tint", type=float, default=0.28,
                    help="how far the second line is blended to white, 0-1")
    ap.add_argument("--char-width", type=float, default=1.0,
                    help="character width as a fraction of the card width")
    ap.add_argument("--char-bottom", type=float, default=0.0,
                    help="gap under the character, as a fraction of card height")
    ap.add_argument("--char-x", type=float, default=0.0,
                    help="horizontal nudge, as a fraction of card width")
    ap.add_argument("--char-top", type=float, default=None,
                    help="place the top of the character at this fraction of the card height")
    args = ap.parse_args()

    canvas = plate(args.bg).convert("RGBA")
    if args.char:
        char, char_x, char_y = place_char(Image.open(args.char).convert("RGBA"),
                                          args.char_width, args.char_bottom, args.char_x,
                                          args.char_top)
    else:
        char = None
        char_x = char_y = 0

    colour = tuple(int(args.colour.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    if args.no_tint:
        colour2 = colour
    elif args.colour2:
        colour2 = tuple(int(args.colour2.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    else:
        # the second line is always a lighter tint of the first, so the
        # hierarchy never inverts; step the tint down until it reads
        def lum(c):
            def ch(v):
                v /= 255
                return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
            r, g, b = (ch(v) for v in c)
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        def ratio(a, b):
            la, lb = sorted((lum(a), lum(b)), reverse=True)
            return (la + 0.05) / (lb + 0.05)

        band = np.asarray(canvas.convert("RGB").crop((0, int(H * .12), W, int(H * .32)))).astype(np.float32)
        bg = tuple(int(v) for v in np.median(band.reshape(-1, 3), axis=0))
        colour2 = colour
        for tint in (args.tint, 0.22, 0.15, 0.08):
            cand = tuple(int(c + (255 - c) * tint) for c in colour)
            if cand != colour and ratio(cand, bg) >= 2.0:
                colour2 = cand
                break

    font_path = ensure_font(args.font)
    max_w = W * (1 - 2 * MARGIN)
    top_of_art = char_y if char else int(H * 0.62)

    mark = None
    if not args.no_mark:
        line = render_mark("HimHim", font_path, args.mark_size,
                           colours_for(args.mark_style, canvas))
        mark = hand(line, args.seed, args.mark_size)

    mark_top = int(H * MARK_TOP)
    title_top = mark_top + (mark.height + int(H * MARK_GAP) if mark else 0)
    avail = top_of_art - title_top - int(H * 0.02)

    def render(text, size, ink=colour):
        seed = (args.seed * 131 + len(text)) & 0xFFFFFFFF
        return hand(render_hand_line(text, font_path, size, ink, seed, args.jitter), seed, size)

    size = args.max_size or 220
    while size > 24:
        lines = [render(t, size, colour if i == 0 else colour2)
                 for i, t in enumerate(args.title)]
        gap = int(size * 0.03)
        block_w = max(l.width for l in lines)
        total = sum(l.height for l in lines) + gap * (len(lines) - 1)
        if block_w <= max_w and total <= avail:
            break
        size = int(size * 0.94)

    lines = [render(t, size, colour if i == 0 else colour2)
             for i, t in enumerate(args.title)]
    gap = int(size * 0.03)
    block_w = max([l.width for l in lines] + ([mark.width] if mark else [0]))
    left = int((W - block_w) / 2)

    if mark:
        canvas.alpha_composite(mark, (int((W - mark.width) / 2), mark_top))

    # compose the block, then centre its *ink*, not its line boxes, so the gap
    # under the mark and the gap above the character are equal
    block_h = sum(l.height for l in lines) + gap * (len(lines) - 1)
    block = Image.new("RGBA", (W, block_h), (0, 0, 0, 0))
    y = 0
    for line in lines:
        block.alpha_composite(line, (int((W - line.width) / 2), y))
        y += line.height + gap

    ink = block.getbbox()
    ink_h = ink[3] - ink[1]
    band_top = mark_top + (mark.getbbox()[3] if mark else 0)
    space = top_of_art - int(H * 0.015) - band_top
    gap_top = max(0, (space - ink_h) // 2)
    y = band_top + gap_top - ink[1]
    canvas.alpha_composite(block, (0, y))

    if char:
        canvas.alpha_composite(char, (char_x, char_y))
    out = canvas.convert("RGB")
    out.save(args.out, dpi=(300, 300), quality=92, optimize=True)
    print(f"{args.out}  art_top {top_of_art}  band {band_top}  ink_gap {gap_top}  "
          f"size {size}  block {block_w}/{int(max_w)}")


if __name__ == "__main__":
    main()
