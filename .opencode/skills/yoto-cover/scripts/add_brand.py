#!/usr/bin/env python3
"""Stamp the HimHim wordmark onto a finished custom cover.

    python3 add_brand.py playlists/speech-therapy-food/cover.jpg
    python3 add_brand.py --all
    python3 add_brand.py --all --dry-run

The mark is hand-lettered in the same face as the card title, in that card's
own title colour (sampled from the top band), so it never adds a new colour to
the palette. It sits top-left, small — the card title still does the work.

Only run this on a cover that has no mark yet: it stamps in place. To redo one,
restore the plain cover first (`git checkout -- playlists/<name>/cover.jpg`).
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_cover import ensure_font, finish_hand, render_hand_line  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

CUSTOM = [
    "speech-therapy-animals",
    "speech-therapy-actions",
    "speech-therapy-food",
    "speech-therapy-routines",
    "speech-therapy-social",
    "speech-therapy-feelings",
    "speech-therapy-cantonese-animals",
    "speech-therapy-cantonese-routines",
    "super-simple-favourites",
]

TEXT = "HimHim"


def render_mark(text, font_path, size, colour, seed, jitter=0.55):
    """Hand-lettered line at small sizes: glyphs are cropped tight and set on a
    shared baseline, so nothing clips the way the cover-size renderer can."""
    import random

    from PIL import ImageDraw

    from make_cover import load_font

    rnd = random.Random(seed)
    glyphs = []
    for ch in text:
        font = load_font(font_path, int(size * rnd.uniform(0.95, 1.05)))
        x0, y0, x1, y1 = font.getbbox(ch)
        tmp = Image.new("RGBA", (x1 - x0 + 8, y1 - y0 + 8), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((4 - x0, 4 - y0), ch, font=font, fill=colour)
        tmp = tmp.rotate(rnd.uniform(-2.6, 2.6) * jitter, resample=Image.BICUBIC, expand=True)
        tmp = tmp.crop(tmp.getbbox())
        glyphs.append((tmp, y1))

    gap = max(1, int(size * 0.02))
    width = sum(g[0].width for g in glyphs) + gap * (len(glyphs) - 1)
    layer = Image.new("RGBA", (width, int(size * 1.6)), (0, 0, 0, 0))
    baseline = int(size * 1.22)
    x = 0
    for tmp, drop in glyphs:
        y = baseline - drop + int(rnd.uniform(-0.03, 0.03) * size)
        layer.alpha_composite(tmp, (x, y))
        x += tmp.width + gap
    return layer.crop(layer.getbbox())


def title_colour(im):
    """The card's own title colour: the darkest cluster on a pale card, the
    lightest on a dark one. Same colour as the hand-lettered title, so the mark
    is always legible on that card's background."""
    w, h = im.size
    band = np.asarray(im.crop((0, int(h * 0.10), w, int(h * 0.30)))).astype(np.float32)
    lum = band[:, :, 0] * 0.299 + band[:, :, 1] * 0.587 + band[:, :, 2] * 0.114
    dark = np.median(lum) > 128
    mask = lum < np.percentile(lum, 4) if dark else lum > np.percentile(lum, 96)
    rgb = band[mask].mean(axis=0)
    return tuple(int(v) for v in rgb)


def stamp(path, text=TEXT, size_factor=0.064, jitter=0.55, seed=11, out=None):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    colour = title_colour(im)
    size = max(18, int(round(w * size_factor)))

    line = render_mark(text, ensure_font(None), size, colour, seed, jitter)
    mark = finish_hand(line, seed, grain_amount=6, blur=3, offset=3, shadow_alpha=42)

    x = int(round(w * 0.058))
    y = int(round(h * 0.020))
    canvas = im.convert("RGBA")
    canvas.alpha_composite(mark, (x, y))
    canvas = canvas.convert("RGB")
    canvas.save(out or path, dpi=(300, 300), quality=92, optimize=True)
    return colour, size, mark.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("covers", nargs="*", help="cover.jpg paths")
    ap.add_argument("--all", action="store_true", help="every custom cover in playlists/")
    ap.add_argument("--text", default=TEXT)
    ap.add_argument("--size-factor", type=float, default=0.064)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    paths = list(args.covers)
    if args.all:
        paths += [os.path.join(ROOT, "playlists", c, "cover.jpg") for c in CUSTOM]

    for path in paths:
        out = "/tmp/opencode/brand-" + os.path.basename(os.path.dirname(path)) + ".jpg" if args.dry_run else None
        colour, size, box = stamp(path, text=args.text, size_factor=args.size_factor,
                                  seed=args.seed, out=out)
        print(f"{os.path.dirname(path).split('/')[-1]:34} #{colour[0]:02X}{colour[1]:02X}{colour[2]:02X}"
              f"  {size}px  mark {box[0]}x{box[1]}  -> {out or path}")


if __name__ == "__main__":
    main()
