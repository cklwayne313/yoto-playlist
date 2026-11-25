#!/usr/bin/env python3
"""Build print-ready Yoto card labels.

    python3 .opencode/print/build_print.py

Outputs:
  print/png/<folder>.png      638x1011 px, 300 DPI (54 x 85.6 mm)
  print/cards-a4.pdf          nine labels per A4 page, true size, crop marks
  print/cards-letter.pdf      nine labels per US Letter page

Print at 100% / "Actual size" — never "fit to page".
"""

import glob
import os

from PIL import Image
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "print")
PNG_DIR = os.path.join(OUT, "png")

CARD_W, CARD_H = 54.0 * mm, 85.6 * mm
PX_W, PX_H = 638, 1011  # 300 DPI at card size
GAP = 8 * mm
MARK = 3 * mm
MARK_OFF = 2 * mm


def card_images():
    items = []
    for path in sorted(glob.glob(os.path.join(ROOT, "playlists", "*", "cover.jpg"))):
        folder = os.path.basename(os.path.dirname(path))
        items.append((folder, path))
    return items


def make_pngs(items):
    os.makedirs(PNG_DIR, exist_ok=True)
    for folder, path in items:
        im = Image.open(path).convert("RGB")
        # exact trim ratio: crop the 0.1px difference rather than stretch
        target_ratio = PX_W / PX_H
        w, h = im.size
        if w / h > target_ratio:
            new_w = int(round(h * target_ratio))
            im = im.crop(((w - new_w) // 2, 0, (w + new_w) // 2, h))
        else:
            new_h = int(round(w / target_ratio))
            im = im.crop((0, (h - new_h) // 2, w, (h + new_h) // 2))
        im = im.resize((PX_W, PX_H), Image.LANCZOS)
        im.save(os.path.join(PNG_DIR, f"{folder}.png"), dpi=(300, 300), optimize=True)


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
    for i, (folder, _) in enumerate(items):
        if i and i % per_page == 0:
            c.showPage()
        slot = i % per_page
        col, row = slot % cols, slot // cols
        x = x0 + col * (CARD_W + GAP)
        y = y0 + (rows - 1 - row) * (CARD_H + GAP)
        c.drawImage(os.path.join(PNG_DIR, f"{folder}.png"), x, y, CARD_W, CARD_H,
                    preserveAspectRatio=False, mask=None)
        crop_marks(c, x, y)

    c.showPage()
    c.save()
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    items = card_images()
    make_pngs(items)
    a = make_pdf(items, A4, "cards-a4.pdf")
    l = make_pdf(items, letter, "cards-letter.pdf")
    print(f"{len(items)} labels -> {a}, {l}, {PNG_DIR}")


if __name__ == "__main__":
    main()
