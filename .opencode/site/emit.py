#!/usr/bin/env python3
"""Emit the data the React app eats.

    python3 .opencode/site/emit.py

Writes, all generated:

    web/src/data/playlists.json     one record per card, ranked
    web/public/covers/<folder>.jpg  400 px thumbnails for the grid
    web/public/covers/full/<folder>.jpg   638 x 1011 originals for the detail view
    web/public/covers-sheet.jpg     every cover on one page
    web/public/icons/*.png          home-screen icons

Parsing is not duplicated: RANKING.md and playlists/*/reference.md are read by
build.py, so the ranking and the prose stay single-sourced.
"""

import json
import os
import re
import shutil
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

import build  # noqa: E402  (same directory)

WEB = os.path.join(ROOT, "web")
PUB = os.path.join(WEB, "public")
DATA = os.path.join(WEB, "src", "data")


def annotate_tables(html):
    """Add data-label="<header>" to every cell, so a table can stack into a
    card per row on a phone without losing which column each value came from."""
    cell_i = 0

    def fix_table(m):
        table = m.group(0)
        heads = [re.sub(r"<[^>]+>", "", h).strip()
                 for h in re.findall(r"<th[^>]*>(.*?)</th>", table, re.S)]
        if not heads:
            return table

        def fix_row(row_m):
            row = row_m.group(0)
            idx = [0]

            def fix_cell(cm):
                label = heads[idx[0]] if idx[0] < len(heads) else ""
                idx[0] += 1
                return f'{cm.group(1)} data-label="{label}"{cm.group(2)}'

            return re.sub(r"(<td)([^>]*>)", fix_cell, row)

        return re.sub(r"<tr>.*?</tr>", fix_row, table, flags=re.S)

    return re.sub(r"<table>.*?</table>", fix_table, html, flags=re.S)


def stars(text):
    return text.count("★")


def minutes(runtime):
    if not runtime:
        return 0
    parts = [int(x) for x in runtime.split(":")]
    return parts[0] * 60 + parts[1] if len(parts) == 3 else parts[0]


def hhmm(total):
    return f"{total // 60}h {total % 60:02d}m"


def icons():
    """Home-screen icons drawn from shapes only, so the build needs no CJK font."""
    from PIL import ImageDraw

    out = os.path.join(PUB, "icons")
    os.makedirs(out, exist_ok=True)
    cream, blue, coral = (251, 246, 232), (11, 106, 151), (180, 71, 43)

    def card(size, pad_f, label):
        im = Image.new("RGB", (size, size), cream)
        d = ImageDraw.Draw(im)
        pad = int(size * pad_f)
        left, top, right, bottom = pad, pad, size - pad, size - pad
        radius = int(size * 0.09)
        d.rounded_rectangle((left, top, right, bottom), radius=radius, fill=blue)
        # a cream disc with a coral play mark, centred on the card
        cx, cy = size / 2, size / 2
        r = size * 0.17
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=cream)
        tri = size * 0.075
        d.polygon([(cx - tri * 0.6, cy - tri), (cx - tri * 0.6, cy + tri), (cx + tri, cy)], fill=coral)
        im.save(os.path.join(out, label))

    card(192, 0.10, "icon-192.png")
    card(512, 0.10, "icon-512.png")
    card(192, 0.22, "maskable-192.png")
    card(512, 0.22, "maskable-512.png")
    shutil.copy(os.path.join(out, "icon-192.png"), os.path.join(out, "apple-touch-icon.png"))


def main():
    os.makedirs(DATA, exist_ok=True)
    for sub in ("covers", "covers/full"):
        d = os.path.join(PUB, sub)
        os.makedirs(d, exist_ok=True)
        for name in os.listdir(d):
            if name.endswith(".jpg"):
                os.remove(os.path.join(d, name))

    ranking = build.parse_ranking()
    playlists = []
    total_min = 0

    for r in ranking:
        folder = r["folder"]
        src = os.path.join(ROOT, "playlists", folder, "reference.md")
        if not os.path.exists(src):
            continue
        text = build.read(src)
        raw = build.title_of(text, build.pretty(folder))
        name = build.display_title(raw)
        label, group = build.series_of(folder)
        rt = build.runtime_of(folder)
        total_min += minutes(rt)
        body = build.md_to_html(build.prep_markdown(text))

        cover_src = os.path.join(ROOT, "playlists", folder, "cover.jpg")
        if os.path.exists(cover_src):
            im = Image.open(cover_src).convert("RGB")
            thumb = im.copy()
            thumb.thumbnail((400, 634), Image.LANCZOS)
            thumb.save(os.path.join(PUB, "covers", f"{folder}.jpg"), quality=82, optimize=True)
            im.resize((638, 1011), Image.LANCZOS).save(
                os.path.join(PUB, "covers", "full", f"{folder}.jpg"), quality=88, optimize=True)

        playlists.append({
            "rank": r["rank"],
            "folder": folder,
            "name": name,
            "title": raw,
            "kicker": label,
            "series": group,
            "lang": "cantonese" if "cantonese" in folder else "english",
            "cover": "custom" if folder in build.CUSTOM_COVERS else "official",
            "tracks": int(r["tracks"]),
            "runtime": rt,
            "speech": stars(r["speech"]),
            "age": stars(r["age"]),
            "verdict": r["verdict"],
            "why": r["why"],
            "body": annotate_tables(body),
        })

    stats = {
        "count": len(playlists),
        "songs": sum(p["tracks"] for p in playlists),
        "runtime": hhmm(total_min),
        "minutes": total_min,
    }
    with open(os.path.join(DATA, "playlists.json"), "w", encoding="utf-8") as fh:
        json.dump({"stats": stats, "playlists": playlists}, fh, ensure_ascii=False)

    # contact sheet, written straight into the app's public folder
    build.DOCS = PUB
    build.build_sheet(ranking)
    icons()

    print(f"data  -> {os.path.join(DATA, 'playlists.json')}")
    print(f"covers-> {os.path.join(PUB, 'covers')} (+ full/)")
    print(f"{stats['count']} playlists · {stats['songs']} songs · {stats['runtime']}")


if __name__ == "__main__":
    main()
