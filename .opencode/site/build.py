#!/usr/bin/env python3
"""Build the static site in docs/ for GitHub Pages.

Run from the project root:

    python3 .opencode/site/build.py

It reads RANKING.md for the order, every playlists/*/reference.md for the pages,
and copies the covers into docs/covers/.
"""

import html
import os
import re
import shutil

import markdown
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOCS = os.path.join(ROOT, "docs")

STYLE = """
:root{
  --cream:#FFFDF3; --paper:#FFFFE8; --ink:#20303a; --muted:#6b7a83;
  --blue:#0392D4; --line:#e7e2cf;
}
*{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--ink);
  font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:28px 20px 80px}
header.top{display:flex;align-items:baseline;justify-content:space-between;gap:16px;flex-wrap:wrap}
h1{font-size:clamp(26px,4vw,38px);line-height:1.15;margin:0 0 6px}
h2{margin-top:38px}
a{color:#036f9f}
.sub{color:var(--muted);margin:0 0 18px}
nav a{margin-left:16px;font-weight:600;text-decoration:none}
nav a:first-child{margin-left:0}
.filters{display:flex;flex-direction:column;gap:10px;margin:20px 0 6px}
.search{width:100%;max-width:380px;padding:10px 14px;border:1px solid var(--line);
  border-radius:999px;background:#fff;font-size:15px}
.chips{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.chip{border:1px solid var(--line);background:#fff;color:var(--ink);font:inherit;font-size:13px;
  padding:6px 12px;border-radius:999px;cursor:pointer;line-height:1}
.chip:hover{border-color:#cfd8dd}
.chip.active{background:var(--blue);border-color:var(--blue);color:#fff}
.chip-group-label{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin-right:2px}
.count{font-size:13px;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px;margin-top:18px}
.card{display:flex;gap:14px;background:#fff;border:1px solid var(--line);border-radius:16px;
  padding:12px;text-decoration:none;color:inherit;position:relative}
.card:hover{border-color:#cfd8dd;box-shadow:0 3px 14px rgba(0,0,0,.05)}
.card img{width:88px;height:140px;object-fit:cover;border-radius:8px;flex:0 0 auto;background:#f2efe2}
.rank{position:absolute;top:-8px;left:-8px;background:var(--blue);color:#fff;font-weight:700;
  font-size:13px;border-radius:999px;min-width:28px;height:28px;display:grid;place-items:center;padding:0 7px}
.body{min-width:0}
.name{font-weight:700;margin:2px 0 4px;font-size:16px}
.why{margin:6px 0 0;color:var(--muted);font-size:13.5px;line-height:1.45}
.stars{font-size:13px;letter-spacing:.5px;color:#b98b00}
.pill{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.06em;
  padding:2px 8px;border-radius:999px;margin-left:6px;vertical-align:1px}
.pill.CORE{background:#e3f4fd;color:#036f9f}
.pill.GOOD{background:#e9f5e9;color:#2c6b34}
.pill.FUN{background:#fdf0e3;color:#8a5a1c}
.pill.LATER{background:#f1eef7;color:#5b4b85}
.kicker{font-size:10.5px;text-transform:uppercase;letter-spacing:.09em;color:var(--muted);margin:0 0 2px}
.page{display:grid;grid-template-columns:220px 1fr;gap:28px;align-items:start}
@media(max-width:720px){.page{grid-template-columns:1fr}.card img{width:72px;height:115px}}
.cover{width:100%;border-radius:14px;border:1px solid var(--line)}
article h1{margin-top:0}
article table{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px}
article th,article td{border-bottom:1px solid var(--line);padding:7px 8px;text-align:left;vertical-align:top}
article th{background:var(--paper);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
article tr:hover td{background:#fffdf6}
article ul,article ol{padding-left:22px}
article code{background:#f3f0e2;padding:1px 5px;border-radius:5px;font-size:13px}
article pre{background:#243038;color:#f3f5f6;padding:14px;border-radius:10px;overflow:auto;font-size:13px}
article pre code{background:none;padding:0;color:inherit}
article blockquote{margin:16px 0;padding:10px 16px;border-left:3px solid var(--blue);
  background:var(--paper);border-radius:0 8px 8px 0;color:#43535c}
.meta{color:var(--muted);font-size:14px;margin:0 0 14px}
footer{margin-top:50px;color:var(--muted);font-size:13px}
"""


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def title_of(text, fallback):
    first = text.strip().splitlines()[0]
    return first.lstrip("# ").strip() or fallback


def pretty(folder):
    return folder.replace("-", " ")


def display_title(title):
    """Trim the repeated 'Speech therapy —' / '言語治療：' prefixes on cards."""
    for prefix in ("Speech therapy — ", "言語治療："):
        if title.startswith(prefix):
            return title[len(prefix):]
    return title


def prep_markdown(text):
    """Make the reference files render well: drop the leading H1 (the page has
    one), split the metadata block into real paragraphs, and turn bare YouTube
    links into compact ▶ links."""
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    text = "\n".join(lines)
    text = re.sub(r"\n(\*\*(?:Cover|Tracks|Inspired by):\*\*)", r"\n\n\1", text)
    text = re.sub(r"(?<!\()(https://youtu\.be/[A-Za-z0-9_-]+)", r"[▶](\1)", text)
    return text


def md_to_html(text):
    return markdown.Markdown(extensions=["tables", "sane_lists"]).convert(text)


CUSTOM_COVERS = {
    "speech-therapy-animals", "speech-therapy-actions", "speech-therapy-food",
    "speech-therapy-routines", "speech-therapy-social", "speech-therapy-feelings",
    "speech-therapy-cantonese-animals", "speech-therapy-cantonese-routines",
    "super-simple-favourites",
    "cantonese-life-songs",
    "cantonese-happy-songs",
    "cantonese-play-songs",
    "cantonese-faith-songs",
    "cantonese-christmas-songs",
    "cantonese-rhymes-active",
    "cantonese-rhymes-calm",
}


def parse_ranking():
    text = read(os.path.join(ROOT, "RANKING.md"))
    rows = []
    for line in text.splitlines():
        if not line.startswith("| ") or not re.match(r"\|\s*\d+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            continue
        rows.append({
            "rank": int(cells[0]),
            "folder": cells[1].strip("`"),
            "tracks": cells[2],
            "speech": cells[3],
            "age": cells[4],
            "verdict": cells[6],
            "why": cells[7],
        })
    rows.sort(key=lambda r: r["rank"])
    return rows


def page_shell(title, body, rel="", extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{rel}style.css">
</head>
<body>
<div class="wrap">
<header class="top">
  <div><h1>{html.escape(title)}</h1>{extra}</div>
  <nav><a href="{rel}index.html">Shelf</a><a href="{rel}ranking.html">Ranking</a><a href="{rel}readme.html">Read me</a></nav>
</header>
{body}
<footer>Built from RANKING.md and playlists/*/reference.md. Personal project; card art belongs to its owners.</footer>
</div>
</body>
</html>
"""


def main():
    os.makedirs(DOCS, exist_ok=True)
    os.makedirs(os.path.join(DOCS, "pages"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "covers"), exist_ok=True)

    with open(os.path.join(DOCS, "style.css"), "w", encoding="utf-8") as fh:
        fh.write(STYLE)
    open(os.path.join(DOCS, ".nojekyll"), "w").close()

    ranking = parse_ranking()
    by_folder = {r["folder"]: r for r in ranking}

    folders = sorted(
        f for f in os.listdir(os.path.join(ROOT, "playlists"))
        if os.path.isdir(os.path.join(ROOT, "playlists", f))
    )

    for folder in folders:
        src = os.path.join(ROOT, "playlists", folder, "reference.md")
        if not os.path.exists(src):
            continue
        text = read(src)
        body = md_to_html(prep_markdown(text))
        rank = by_folder.get(folder)
        extra = ""
        if rank:
            extra = f'<p class="meta">Rank {rank["rank"]} of {len(ranking)} · Tracks {rank["tracks"]} · Speech {rank["speech"]} · Age 2 {rank["age"]}</p>'
        cover = f'<img class="cover" src="../covers/{folder}.jpg" alt="{html.escape(pretty(folder))} cover">'
        content = f'<div class="page">{cover}<article>{body}</article></div>'
        out = page_shell(title_of(text, pretty(folder)), content, rel="../", extra=extra)
        with open(os.path.join(DOCS, "pages", f"{folder}.html"), "w", encoding="utf-8") as fh:
            fh.write(out)

        cov_src = os.path.join(ROOT, "playlists", folder, "cover.jpg")
        if os.path.exists(cov_src):
            img = Image.open(cov_src).convert("RGB")
            img.thumbnail((400, 634), Image.LANCZOS)
            img.save(os.path.join(DOCS, "covers", f"{folder}.jpg"), quality=82, optimize=True)

    cards = []
    for r in ranking:
        folder = r["folder"]
        page = os.path.join(ROOT, "playlists", folder, "reference.md")
        raw = title_of(read(page), pretty(folder)) if os.path.exists(page) else pretty(folder)
        name = display_title(raw)
        kicker = ""
        if raw.startswith("Speech therapy — "):
            kicker = "Speech therapy"
        elif raw.startswith("言語治療"):
            kicker = "言語治療" 
        lang = "cantonese" if "cantonese" in folder else "english"
        cover = "custom" if folder in CUSTOM_COVERS else "official"
        speech = r["speech"].count("★")
        cards.append(f"""<a class="card" data-name="{html.escape(name.lower())}" data-verdict="{r['verdict']}" data-lang="{lang}" data-cover="{cover}" data-speech="{speech}" href="pages/{folder}.html">
  <span class="rank">{r['rank']}</span>
  <img src="covers/{folder}.jpg" alt="" loading="lazy">
  <div class="body">
    {f'<div class="kicker">{kicker}</div>' if kicker else ''}
    <div class="name">{html.escape(name)}</div>
    <div class="stars">Speech {r['speech']} · Age 2 {r['age']}<span class="pill {r['verdict']}">{r['verdict']}</span></div>
    <p class="why">{html.escape(r['why'])}</p>
  </div>
</a>""")

    index_body = f"""
<p class="sub">All {len(ranking)} playlists, ranked for a 2-year-old with a speech delay — speech value first, then age fit.</p>
<div class="filters">
  <input class="search" id="q" placeholder="Search by name…" aria-label="Search playlists">
  <div class="chips" data-group="verdict">
    <span class="chip-group-label">Show</span>
    <button class="chip active" data-value="all">All</button>
    <button class="chip" data-value="CORE">Core</button>
    <button class="chip" data-value="GOOD">Good</button>
    <button class="chip" data-value="FUN">Fun</button>
    <button class="chip" data-value="LATER">Later</button>
  </div>
  <div class="chips" data-group="lang">
    <span class="chip-group-label">Language</span>
    <button class="chip active" data-value="all">All</button>
    <button class="chip" data-value="cantonese">Cantonese</button>
    <button class="chip" data-value="english">English</button>
  </div>
  <div class="chips" data-group="cover">
    <span class="chip-group-label">Cover</span>
    <button class="chip active" data-value="all">All</button>
    <button class="chip" data-value="official">Official Yoto art</button>
    <button class="chip" data-value="custom">Custom art</button>
  </div>
  <div class="chips" data-group="speech">
    <span class="chip-group-label">Speech</span>
    <button class="chip active" data-value="all">All</button>
    <button class="chip" data-value="5">5 stars</button>
    <button class="chip" data-value="4">4+ stars</button>
  </div>
  <div class="count" id="count">{len(ranking)} shown</div>
</div>
<div class="grid" id="grid">
{''.join(cards)}
</div>
<script>
const state = {{ q: "", verdict: "all", lang: "all", cover: "all", speech: "all" }};
const cards = [...document.querySelectorAll("#grid .card")];
const count = document.getElementById("count");
const q = document.getElementById("q");

function apply() {{
  let shown = 0;
  for (const card of cards) {{
    const okName = !state.q || card.dataset.name.includes(state.q);
    const okVerdict = state.verdict === "all" || card.dataset.verdict === state.verdict;
    const okLang = state.lang === "all" || card.dataset.lang === state.lang;
    const okCover = state.cover === "all" || card.dataset.cover === state.cover;
    const okSpeech = state.speech === "all" ||
      (state.speech === "5" ? card.dataset.speech === "5" : Number(card.dataset.speech) >= 4);
    const ok = okName && okVerdict && okLang && okCover && okSpeech;
    card.style.display = ok ? "" : "none";
    if (ok) shown++;
  }}
  count.textContent = shown + " of " + cards.length + " shown";
}}

q.addEventListener("input", () => {{ state.q = q.value.trim().toLowerCase(); apply(); }});

document.querySelectorAll(".chips").forEach(group => {{
  const key = group.dataset.group;
  group.querySelectorAll(".chip").forEach(chip => {{
    chip.addEventListener("click", () => {{
      group.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      state[key] = chip.dataset.value;
      apply();
    }});
  }});
}});

apply();
</script>
"""
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page_shell("Yoto shelf", index_body))

    for src, name, label in [("RANKING.md", "ranking.html", "Playlist ranking"),
                             ("README.md", "readme.html", "Read me")]:
        body = f'<article>{md_to_html(prep_markdown(read(os.path.join(ROOT, src))))}</article>'
        with open(os.path.join(DOCS, name), "w", encoding="utf-8") as fh:
            fh.write(page_shell(label, body))

    print(f"built {len(folders)} playlist pages + index in {DOCS}")


if __name__ == "__main__":
    main()
