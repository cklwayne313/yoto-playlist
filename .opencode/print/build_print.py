#!/usr/bin/env python3
"""Build print-ready Yoto card label sheets from the one cover per playlist.

    python3 .opencode/print/build_print.py            # PDFs only
    python3 .opencode/print/build_print.py --normalise # also rewrite covers to 638x1011 @300dpi

There is one image per card: `playlists/<name>/cover.jpg`, at 638 x 1011 px
(54 x 85.6 mm at 300 DPI). That same file is what the Yoto app accepts and what
these PDFs embed.

Print at 100% / "Actual size" — never "fit to page".
"""

import argparse
import glob
import os

from PIL import Image
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "print")

CARD_W, CARD_H = 54.0 * mm, 85.6 * mm
PX_W, PX_H = 638, 1011
GAP = 8 * mm
MARK = 3 * mm
MARK_OFF = 2 * mm


def covers():
    items = []
    for path in sorted(glob.glob(os.path.join(ROOT, "playlists", "*", "cover.jpg"))):
        items.append((os.path.basename(os.path.dirname(path)), path))
    return items


def normalise(path):
    im = Image.open(path).convert("RGB")
    if im.size == (PX_W, PX_H):
        im.save(path, dpi=(300, 300), quality=92, optimize=True)
        return
    target = PX_W / PX_H
    w, h = im.size
    if w / h > target:
        nw = int(round(h * target))
        im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(round(w / target))
        im = im.crop((0, (h - nh) // 2, w, (h + nh) // 2))
    im = im.resize((PX_W, PX_H), Image.LANCZOS)
    im.save(path, dpi=(300, 300), quality=92, optimize=True)


def crop_marks(c, x, y):
    c.setLineWidth(0.3)
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        cx = x if dx < 0 else x + CARD_W
        cy = y if dy < 0 else y + CARD_H
        c.line(cx, cy + dy * MARK_OFF, cx, cy + dy * (MARK_OFF + MARK))
        c.line(cx + dx * MARK_OFF, cy, cx + dx * (MARK_OFF + MARK), cy)


def make_pdf(items, page_size, name):
    pw, ph = page_size
    cols, rows = 3, 3
    grid_w = cols * CARD_W + (cols - 1) * GAP
    grid_h = rows * CARD_H + (rows - 1) * GAP
    x0 = (pw - grid_w) / 2
    y0 = (ph - grid_h) / 2

    path = os.path.join(OUT, name)
    c = canvas.Canvas(path, pagesize=page_size)
    c.setTitle("Yoto card labels")

    per_page = cols * rows
    for i, (folder, cover) in enumerate(items):
        if i and i % per_page == 0:
            c.showPage()
        slot = i % per_page
        col, row = slot % cols, slot // cols
        x = x0 + col * (CARD_W + GAP)
        y = y0 + (rows - 1 - row) * (CARD_H + GAP)
        c.drawImage(cover, x, y, CARD_W, CARD_H, preserveAspectRatio=False)
        crop_marks(c, x, y)

    c.showPage()
    c.save()
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--normalise", action="store_true",
                    help="rewrite every cover to 638x1011 px with 300 DPI metadata")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    items = covers()
    if args.normalise:
        for _, cover in items:
            normalise(cover)
    a = make_pdf(items, A4, "cards-a4.pdf")
    l = make_pdf(items, letter, "cards-letter.pdf")
    print(f"{len(items)} labels -> {a}, {l}")


if __name__ == "__main__":
    main()
