#!/usr/bin/env python3
"""Compose a 1200x1902 Yoto-style cover from character art plus a title.

Keys a flat background, pastes the character on cream, and sets a chunky blue
title above it. See ../SKILL.md for the house style.

    python3 make_cover.py --art art.jpg --title MY FAVOURITES --out cover.jpg
"""

import argparse
import math
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


def tint(c, f):
    c = tuple(c)
    if f <= 1:
        return tuple(max(0, int(v * f)) for v in c)
    return tuple(min(255, int(v + (255 - v) * (f - 1))) for v in c)


def vgrad(W, H, top, bottom):
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / max(1, H - 1)
        arr[y, :] = [int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)]
    return Image.fromarray(arr)


def draw_scene(canvas, kind, base, accent, W, H, seed):
    """A simple painted scene behind the character. Yoto cards each have one;
    a flat fill is what makes a custom card look homemade."""
    if kind in (None, "none"):
        return
    b, a = tuple(base), tuple(accent)
    rnd = random.Random(seed)
    if kind == "meadow":
        canvas.paste(vgrad(W, H, tint(b, 1.03), b))
        d = ImageDraw.Draw(canvas)
        d.ellipse([-W * 0.45, H * 0.80, W * 0.85, H * 1.2], fill=tint(a, 1.0))
        d.ellipse([W * 0.25, H * 0.85, W * 1.45, H * 1.25], fill=tint(a, 0.93))
        for _ in range(20):
            x, y = rnd.uniform(0, W), rnd.uniform(H * 0.82, H * 0.99)
            r = rnd.uniform(4, 8)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))
            r2 = r * 0.38
            d.ellipse([x - r2, y - r2, x + r2, y + r2], fill=(238, 186, 86))
    elif kind == "rays":
        cx, cy, R = W / 2, H * 0.18, W * 1.5
        for i in range(18):
            a0 = math.pi * 2 * i / 18
            a1 = a0 + math.pi / 18
            p1 = (cx + math.cos(a0) * R, cy + math.sin(a0) * R)
            p2 = (cx + math.cos(a1) * R, cy + math.sin(a1) * R)
            d = ImageDraw.Draw(canvas)
            d.polygon([(cx, cy), p1, p2], fill=tint(a, 1.0) if i % 2 else tint(b, 0.96))
    elif kind == "table":
        d = ImageDraw.Draw(canvas)
        top = H * 0.70
        d.rectangle([0, top, W, H], fill=a)
        cell = W / 8
        for row in range(4):
            for col in range(8):
                if (row + col) % 2 == 0:
                    d.rectangle([col * cell, top + row * cell, (col + 1) * cell, top + (row + 1) * cell],
                                fill=(255, 255, 255))
        for _ in range(16):
            x, y = rnd.uniform(0, W), rnd.uniform(H * 0.34, H * 0.68)
            r = rnd.uniform(3, 7)
            d.ellipse([x - r, y - r, x + r, y + r], fill=tint(a, 0.9))
    elif kind == "sky":
        canvas.paste(vgrad(W, H, tint(b, 1.05), tint(b, 0.97)))
        d = ImageDraw.Draw(canvas)
        d.ellipse([W * 0.74, H * 0.05, W * 0.97, H * 0.19], fill=(255, 224, 130))
        for cx, cy, s in [(0.18, 0.10, 1.0), (0.55, 0.06, 0.8), (0.30, 0.20, 0.7)]:
            for dx, dy, r in [(-0.06, 0, 0.045), (0, -0.02, 0.055), (0.06, 0, 0.045), (0.02, 0.01, 0.05)]:
                d.ellipse([W * (cx + dx - r), H * (cy + dy - r * 1.8),
                           W * (cx + dx + r), H * (cy + dy + r * 1.8)], fill=(255, 255, 255))
    elif kind == "bunting":
        d = ImageDraw.Draw(canvas)
        for row, y in enumerate((H * 0.035, H * 0.085)):
            d.line([(0, y), (W, y + H * 0.01)], fill=tint(a, 0.75), width=3)
            n = 9
            for i in range(n):
                x = (i + 0.5) * W / n
                w = W / n * 0.34
                colour = a if (i + row) % 2 == 0 else (255, 255, 255)
                d.polygon([(x - w, y), (x + w, y), (x, y + H * 0.045)], fill=colour)
        for _ in range(12):
            x, y = rnd.uniform(0, W), rnd.uniform(H * 0.45, H * 0.75)
            r = rnd.uniform(5, 11)
            d.ellipse([x - r, y - r, x + r, y + r], fill=tint(a, 1.0))
    elif kind == "calm":
        d = ImageDraw.Draw(canvas)
        for i, f in enumerate((0.35, 0.55, 0.75)):
            r = W * f
            d.ellipse([W / 2 - r, H * 0.66 - r, W / 2 + r, H * 0.66 + r],
                      outline=tint(a, 1.0), width=max(6, int(W * 0.012)))
    elif kind == "sea":
        canvas.paste(vgrad(W, H, tint(b, 1.08), tint(b, 0.82)))
        d = ImageDraw.Draw(canvas)
        for i, y in enumerate((0.86, 0.92, 0.97)):
            d.arc([-W * 0.3 + i * W * 0.25, H * y - H * 0.05,
                   W * 0.6 + i * W * 0.25, H * y + H * 0.05], 180, 360,
                  fill=tint(a, 0.9), width=max(5, int(W * 0.008)))
        for _ in range(16):
            x, y = rnd.uniform(0, W), rnd.uniform(H * 0.35, H * 0.85)
            r = rnd.uniform(5, 14)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255), width=3)
    elif kind == "night":
        canvas.paste(vgrad(W, H, (28, 44, 92), (12, 20, 48)))
        d = ImageDraw.Draw(canvas)
        for _ in range(70):
            x, y = rnd.uniform(0, W), rnd.uniform(0, H)
            r = rnd.uniform(1.2, 3.2)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 249, 214))
        d.ellipse([W * 0.72, H * 0.07, W * 0.93, H * 0.23], fill=(255, 236, 160))
        d.ellipse([W * 0.77, H * 0.05, W * 0.98, H * 0.21], fill=(16, 26, 58))


def draw_motif(canvas, kind, accent, W, H, char_top, seed):
    """A single quiet shape behind the character, so two cards in the same
    series do not read as the same template."""
    if kind in (None, "none"):
        return
    draw = ImageDraw.Draw(canvas)
    if kind == "circle":
        r = W * 0.63
        cy = char_top + r * 0.72
        draw.ellipse([W / 2 - r, cy - r, W / 2 + r, cy + r], fill=accent)
    elif kind == "hill":
        draw.ellipse([-W * 0.35, H * 0.68, W * 1.35, H * 1.40], fill=accent)
    elif kind == "dots":
        rnd = random.Random(seed)
        for _ in range(26):
            x = rnd.uniform(0, W)
            y = rnd.uniform(H * 0.32, H * 0.95)
            r = rnd.uniform(6, 16)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=accent)


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
               jitter=1.0, seed_base=0, scale=1.0):
    region_h = region_bottom - region_top
    n = len(lines)
    max_w = width * 0.95
    sizes = [max(24, int(fit_size(t, font_path, max_w, region_h * 0.62) * scale)) for t in lines]

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
    p.add_argument("--background", default=None, help="painted background image to use instead of a flat canvas")
    p.add_argument("--scene", default="none", help="none, meadow, rays, table, sky, bunting, calm, sea or night")
    p.add_argument("--motif", default="none", help="none, circle, hill or dots")
    p.add_argument("--accent", default="#EFE9D6", help="colour of the background motif")
    p.add_argument("--title-scale", type=float, default=1.0, help="shrink the title for a lighter look")
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
    if args.background:
        bg = Image.open(args.background).convert("RGB")
        scale = max(W / bg.width, H / bg.height)
        bg = bg.resize((int(bg.width * scale) + 1, int(bg.height * scale) + 1), Image.LANCZOS)
        left, top = (bg.width - W) // 2, (bg.height - H) // 2
        canvas = bg.crop((left, top, left + W, top + H))
    else:
        canvas = Image.new("RGB", (W, H), hex_rgb(args.bg))
        if not args.no_grain:
            noise = np.random.default_rng(args.seed).normal(0, 2.6, (H, W, 1))
            canvas = Image.fromarray(np.clip(np.asarray(canvas).astype(np.float32) + noise, 0, 255).astype(np.uint8))

    font_path = ensure_font(args.font)
    top = H - cut.height + 15 if args.anchor_bottom else args.char_top
    if not args.background:
        if args.scene != "none":
            draw_scene(canvas, args.scene, hex_rgb(args.bg), hex_rgb(args.accent), W, H, args.seed)
        draw_motif(canvas, args.motif, hex_rgb(args.accent), W, H, top, args.seed)
    draw_title(canvas, args.title, font_path, hex_rgb(args.blue),
               int(H * 0.085), top - int(H * 0.02), W,
               jitter=args.jitter, seed_base=args.seed, scale=args.title_scale)
    canvas.paste(cut, ((W - args.char_width) // 2, top), cut)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    canvas.save(args.out, quality=95)
    print(f"{args.out}  {W}x{H}  character {cut.size[0]}x{cut.size[1]}")


if __name__ == "__main__":
    main()
