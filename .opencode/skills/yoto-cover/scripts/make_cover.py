#!/usr/bin/env python3
"""Compose a 1200x1902 Yoto-style cover from character art plus a title.

Keys a flat background, pastes the character on cream, and sets a chunky blue
title above it. See ../SKILL.md for the house style.

    python3 make_cover.py --art art.jpg --title MY FAVOURITES --out cover.jpg
"""

import argparse
import os
import random
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/baloo2/Baloo2%5Bwght%5D.ttf"
FONT_CACHE = os.path.expanduser("~/.cache/yoto-cover/Baloo2.ttf")


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def load_font(path, size):
    font = ImageFont.truetype(path, size)
    try:
        font.set_variation_by_name("ExtraBold")
    except Exception:
        pass
    return font


def ensure_font(path):
    if path and os.path.exists(path):
        return path
    if os.path.exists(FONT_CACHE):
        return FONT_CACHE
    os.makedirs(os.path.dirname(FONT_CACHE), exist_ok=True)
    print(f"downloading Baloo 2 to {FONT_CACHE}", file=sys.stderr)
    urllib.request.urlretrieve(FONT_URL, FONT_CACHE)
    return FONT_CACHE


def background_colour(rgb):
    h, w, _ = rgb.shape
    corners = np.array([
        rgb[2, 2], rgb[2, w - 3], rgb[h - 3, 2], rgb[h - 3, w - 3],
    ], dtype=np.float32)
    return np.median(corners, axis=0)


def cut_out(img, key, tol, erode):
    rgb = np.asarray(img.convert("RGB")).astype(np.float32)
    if key == "none":
        return img.convert("RGBA")

    if key == "auto":
        key = background_colour(rgb)
    else:
        key = np.array(hex_rgb(key), dtype=np.float32)

    dist = np.sqrt(((rgb - key) ** 2).sum(axis=2))
    near = dist < tol

    labels, _ = ndimage.label(near)
    edge = set(labels[0, :]) | set(labels[-1, :]) | set(labels[:, 0]) | set(labels[:, -1])
    edge.discard(0)
    bg = np.isin(labels, list(edge))
    bg = ndimage.binary_closing(bg, np.ones((5, 5)))

    solid = ~bg
    if erode > 0:
        solid = ndimage.binary_erosion(solid, np.ones((erode, erode)))
    alpha = Image.fromarray((solid * 255).astype(np.uint8), "L")
    alpha = alpha.filter(ImageFilter.GaussianBlur(1.2))

    out = img.convert("RGB").convert("RGBA")
    out.putalpha(alpha)
    return out.crop(out.getbbox())


def fit_size(text, font_path, max_w, max_h, start=420):
    probe = start
    while probe > 24:
        font = load_font(font_path, probe)
        bb = font.getbbox(text)
        if bb[2] - bb[0] <= max_w and bb[3] - bb[1] <= max_h:
            return probe
        probe -= 6
    return 24


def render_hand_line(text, font_path, size, colour, seed, jitter=1.0):
    """One line of hand-lettered type: each glyph slightly rotated, scaled and
    dropped off the baseline, so it reads painted rather than typeset."""
    rnd = random.Random(seed)
    glyphs = []
    for ch in text:
        if ch.isspace():
            glyphs.append((None, int(size * 0.30)))
            continue
        s = max(8, int(size * rnd.uniform(0.94, 1.06)))
        font = load_font(font_path, s)
        bb = font.getbbox(ch)
        cw = max(1, bb[2] - bb[0])
        tmp = Image.new("RGBA", (cw + 120, s + 160), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((60 - bb[0], 60 - bb[1]), ch, font=font, fill=colour)
        tmp = tmp.rotate(rnd.uniform(-3.4, 3.4) * jitter, resample=Image.BICUBIC, expand=False)
        dy = rnd.uniform(-0.055, 0.055) * size * jitter
        glyphs.append((tmp, cw, dy))

    gap = size * 0.015
    total = sum(g[1] for g in glyphs) + gap * (len(glyphs) - 1)
    box_h = int(size * 1.9)
    layer = Image.new("RGBA", (int(total) + 160, box_h), (0, 0, 0, 0))
    x = 80
    for tmp, cw, dy in glyphs:
        if tmp is None:
            x += cw + gap
            continue
        layer.alpha_composite(tmp, (int(x - 60), int(box_h * 0.5 - size * 0.68 + dy)))
        x += cw + gap
    return layer.crop(layer.getbbox())


def finish_hand(layer, seed, grain_amount=10, blur=7, offset=8, shadow_alpha=58):
    """Print texture inside the letters plus a soft cast shadow."""
    rng = np.random.default_rng(seed)
    arr = np.asarray(layer).astype(np.int16)
    noise = rng.normal(0, grain_amount, (arr.shape[0], arr.shape[1], 1))
    visible = arr[:, :, 3:4] > 0
    arr[:, :, :3] = np.where(visible, np.clip(arr[:, :, :3] + noise, 0, 255), arr[:, :, :3])
    layer = Image.fromarray(arr.astype(np.uint8))

    pad = 40
    base = Image.new("RGBA", (layer.width + pad * 2, layer.height + pad * 2), (0, 0, 0, 0))
    mask = layer.split()[3].point(lambda v: int(v * shadow_alpha / 255))
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    shadow.paste((25, 45, 70, 255), (pad, pad + offset), mask)
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(layer, (pad, pad))
    return base


def draw_title(canvas, lines, font_path, blue, region_top, region_bottom, width,
               jitter=1.0, seed_base=0):
    region_h = region_bottom - region_top
    n = len(lines)
    max_w = width * 0.95
    sizes = [fit_size(t, font_path, max_w, region_h * 0.62) for t in lines]

    gap = int(region_h * 0.05)
    while True:
        heights = []
        for text, size in zip(lines, sizes):
            font = load_font(font_path, size)
            bb = font.getbbox(text)
            heights.append(bb[3] - bb[1])
        total = sum(heights) + gap * (n - 1)
        if total <= region_h or max(sizes) <= 24:
            break
        shrink = (region_h - gap * (n - 1)) / max(total - gap * (n - 1), 1)
        sizes = [max(24, int(s * shrink * 0.98)) for s in sizes]

    rendered = []
    for i, (text, size) in enumerate(zip(lines, sizes)):
        seed = (seed_base * 131 + i * 17 + len(text)) & 0xFFFFFFFF
        line = render_hand_line(text, font_path, size, blue, seed, jitter)
        rendered.append(finish_hand(line, seed))

    total = sum(r.height for r in rendered) + gap * (n - 1)
    y = region_top + (region_h - total) / 2
    rgba = canvas.convert("RGBA")
    for layer in rendered:
        rgba.alpha_composite(layer, ((width - layer.width) // 2, int(y)))
        y += layer.height + gap
    canvas.paste(rgba.convert("RGB"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--art", required=True)
    p.add_argument("--title", nargs="+", required=True, help='e.g. --title "MY" "FAVOURITES"')
    p.add_argument("--out", required=True)
    p.add_argument("--width", type=int, default=1200)
    p.add_argument("--height", type=int, default=1902)
    p.add_argument("--bg", default="#FFFFE8")
    p.add_argument("--blue", default="#0392D4")
    p.add_argument("--char-top", type=int, default=700, help="y of the top of the character")
    p.add_argument("--char-width", type=int, default=1120)
    p.add_argument("--key", default="auto", help="auto, none, or #RRGGBB")
    p.add_argument("--key-color", default=None, help="alias for --key #RRGGBB")
    p.add_argument("--tol", type=float, default=30.0)
    p.add_argument("--erode", type=int, default=7)
    p.add_argument("--font", default=None)
    p.add_argument("--no-grain", action="store_true")
    p.add_argument("--jitter", type=float, default=1.0, help="hand-lettered wobble, 0 disables")
    p.add_argument("--seed", type=int, default=7, help="change to re-roll the lettering")
    p.add_argument("--fade-bottom", type=int, default=0, help="soften a hard cut at the bottom of the art, in px")
    p.add_argument("--anchor-bottom", action="store_true", help="sit the art on the card edge, so a cropped source has no visible cut")
    args = p.parse_args()

    key = args.key_color or args.key
    art = Image.open(args.art)
    cut = cut_out(art, key, args.tol, args.erode)
    if args.fade_bottom > 0 and cut.height > args.fade_bottom:
        alpha = np.asarray(cut.split()[3]).astype(np.float32)
        ramp = np.linspace(1.0, 0.0, args.fade_bottom)
        alpha[-args.fade_bottom:, :] *= ramp[:, None]
        cut.putalpha(Image.fromarray(alpha.astype(np.uint8), "L"))

    scale = args.char_width / cut.size[0]
    cut = cut.resize((args.char_width, int(cut.size[1] * scale)), Image.LANCZOS)

    W, H = args.width, args.height
    canvas = Image.new("RGB", (W, H), hex_rgb(args.bg))
    if not args.no_grain:
        noise = np.random.default_rng(args.seed).normal(0, 2.6, (H, W, 1))
        canvas = Image.fromarray(np.clip(np.asarray(canvas).astype(np.float32) + noise, 0, 255).astype(np.uint8))

    font_path = ensure_font(args.font)
    top = H - cut.height + 15 if args.anchor_bottom else args.char_top
    draw_title(canvas, args.title, font_path, hex_rgb(args.blue),
               int(H * 0.085), top - int(H * 0.02), W,
               jitter=args.jitter, seed_base=args.seed)
    canvas.paste(cut, ((W - args.char_width) // 2, top), cut)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    canvas.save(args.out, quality=95)
    print(f"{args.out}  {W}x{H}  character {cut.size[0]}x{cut.size[1]}")


if __name__ == "__main__":
    main()
