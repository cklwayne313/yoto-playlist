#!/usr/bin/env python3
"""Stamp the HimHim wordmark onto a finished custom cover.

    python3 add_brand.py playlists/speech-therapy-food/cover.jpg
    python3 add_brand.py --all
    python3 add_brand.py --all --dry-run

House rule: the mark is the same on every custom card — same word, lettering,
size and corner. Only one thing changes with the artwork: ink on a pale card,
cream on a dark one, which is an ordinary logo reversal.

    Him  Him      first half ink (or cream), second half coral

It stamps in place, so only run it on a cover that has no mark yet. To redo one,
restore the plain cover first (`git checkout -- <plain> -- playlists/<name>/cover.jpg`)
and run it again.
"""

import argparse
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_cover import ensure_font, finish_hand, load_font  # noqa: E402

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
INK = "#26323A"
CREAM = "#FBF3DE"
CORAL = "#C9552F"
RAINBOW = ["#C9552F", "#C9862B", "#4E8C57", "#3D7FB5", "#7C5AA6", "#C9552F"]
TRIO = ["#C9552F", "#C9862B", "#4E8C57"]


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def is_dark(im):
    w, h = im.size
    band = np.asarray(im.crop((0, int(h * 0.10), w, int(h * 0.30)))).astype(np.float32)
    lum = band[:, :, 0] * 0.299 + band[:, :, 1] * 0.587 + band[:, :, 2] * 0.114
    return bool(np.median(lum) < 128)


def title_colour(im):
    """Only for the 'title' style: the card's own lettering colour."""
    w, h = im.size
    band = np.asarray(im.crop((0, int(h * 0.10), w, int(h * 0.30)))).astype(np.float32)
    lum = band[:, :, 0] * 0.299 + band[:, :, 1] * 0.587 + band[:, :, 2] * 0.114
    dark = np.median(lum) > 128
    mask = lum < np.percentile(lum, 4) if dark else lum > np.percentile(lum, 96)
    return tuple(int(v) for v in band[mask].mean(axis=0))


def colours_for(style, im, text=TEXT):
    dark = is_dark(im)
    if style == "two-tone":
        base = hex_rgb(CREAM if dark else INK)
        half = len(text) // 2
        return [base] * half + [hex_rgb(CORAL)] * (len(text) - half)
    if style == "ink":
        return [hex_rgb(CREAM if dark else INK)]
    if style == "trio":
        return [hex_rgb(c) for c in (TRIO * 2)][:len(text)]
    if style == "rainbow":
        return [hex_rgb(c) for c in RAINBOW][:len(text)]
    if style == "title":
        return [title_colour(im)]
    raise SystemExit(f"unknown style {style}")


def render_mark(text, font_path, size, colours, seed=11, jitter=0.55):
    """Hand-lettered line at small sizes: glyphs are cropped tight and set on a
    shared baseline, so nothing clips the way the cover-size renderer can."""
    rnd = random.Random(seed)
    glyphs = []
    for i, ch in enumerate(text):
        font = load_font(font_path, int(size * rnd.uniform(0.95, 1.05)))
        x0, y0, x1, y1 = font.getbbox(ch)
        tmp = Image.new("RGBA", (x1 - x0 + 8, y1 - y0 + 8), (0, 0, 0, 0))
        colour = colours[i % len(colours)]
        ImageDraw.Draw(tmp).text((4 - x0, 4 - y0), ch,
                                 font=font, fill=colour if len(colour) == 4 else colour + (255,))
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


def stamp(path, text=TEXT, style="two-tone", size_factor=0.064, jitter=0.55,
          seed=11, out=None):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    size = max(18, int(round(w * size_factor)))

    line = render_mark(text, ensure_font(None), size, colours_for(style, im, text),
                       seed, jitter)
    mark = finish_hand(line, seed, grain_amount=6, blur=3, offset=3, shadow_alpha=42)

    x = int(round(w * 0.058))
    y = int(round(h * 0.020))
    canvas = im.convert("RGBA")
    canvas.alpha_composite(mark, (x, y))
    canvas = canvas.convert("RGB")
    canvas.save(out or path, dpi=(300, 300), quality=92, optimize=True)
    return size, mark.size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("covers", nargs="*", help="cover.jpg paths")
    ap.add_argument("--all", action="store_true", help="every custom cover in playlists/")
    ap.add_argument("--text", default=TEXT)
    ap.add_argument("--style", default="two-tone",
                    choices=["two-tone", "ink", "trio", "rainbow", "title"])
    ap.add_argument("--size-factor", type=float, default=0.064)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    paths = list(args.covers)
    if args.all:
        paths += [os.path.join(ROOT, "playlists", c, "cover.jpg") for c in CUSTOM]

    for path in paths:
        out = "/tmp/opencode/brand-" + os.path.basename(os.path.dirname(path)) + ".jpg" if args.dry_run else None
        size, box = stamp(path, text=args.text, style=args.style,
                          size_factor=args.size_factor, seed=args.seed, out=out)
        print(f"{os.path.dirname(path).split('/')[-1]:34} {args.style:9} {size}px"
              f"  mark {box[0]}x{box[1]}  -> {out or path}")


if __name__ == "__main__":
    main()
