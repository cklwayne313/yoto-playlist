---
name: Yoto Card Cover
description: Build a custom 1200x1902 cover for a Yoto Make Your Own card — check whether a real card exists, get the official character art, flatten its background, set the title in Yoto's blue on cream, and check the result against the existing covers. Use when a playlist has no matching Yoto card or the user asks for custom cover art.
---

# Yoto Card Cover

Custom cover art for a Make Your Own card, in the same visual language as the
real Yoto cards in `playlists/*/cover.jpg`.

## When to use this

Use it only after confirming **no real card matches** the playlist. A borrowed
Yoto cover is always better than custom art — search the product page first
(see `playlists/*/reference.md` for how each existing cover was sourced).

If a card exists, stop. This skill is for the gap: a playlist built from a
YouTube list, or a language/theme Yoto doesn't sell.

## House style — measured, not guessed

| Property | Value |
|---|---|
| Canvas | **638 × 1011 px at 300 DPI** = 54 × 85.6 mm, the card itself. One file per card: app upload and print sheet use the same image |
| Side margin | **7%** of width — a title never runs into the card edge |
| Mark | `HimHim`, centred above the title, 38 px tall, in the house two-tone: ink `#26323A` + coral `#C9552F`; cream `#FBF3DE` + coral on a dark card |
| Title | chunky rounded, hand-lettered, two lines with `SONGS` on the second, tight leading (~0.03 em between lines). Sized to the band between the mark and the character, never overlapping either |
| Background | a simple painted scene, generated per card — sky, hills, waves, bunting, stars. Not a flat fill: flat is what makes a custom card look homemade |
| Character top | **just under the title**, not at a fixed percentage. The title ink is centred between the mark and the character, so the gap below the mark and the gap above the head are equal. One CJK line puts the head at **~33%**; two Latin lines at **~35%** — the head follows the title, so every card has the same two gaps however tall the type is |
| Character scale, painted-into-scene cards | **60–65% of card height**: head or hat top under the title, feet/contact at the bottom edge, body running off it. A character whose head sits at 45–55% leaves a dead band of empty wall under the title and the card looks bottom-heavy. Say "head just below the title, feet at the bottom edge, filling the frame" in the prompt |
| Props | one scene idea per card, painted into the background. Not a collage of objects around the character. Bubbles, bunting and other scene props may fill the title-to-character space on purpose (see `speech-therapy-cantonese`) |
| Shadow | none, or a barely visible one |

Read several real cards, not one. `happy-songs` is the plainest card in the
set; `silly-songs` has a hill and bugs, `bedtime-songs` a starfield,
`underwater-songs` a sea. Match that range, not a YouTube thumbnail — thumbnails
are far busier and more saturated.

## Workflow

### 1. Find the official art

Never redraw a licensed character from scratch — it never lands and it wastes
rounds. Find the publisher's own asset:

- Character/landing pages on the brand's site (`supersimple.com/noodle-and-pals/`).
- Their WordPress uploads: `.../wp-content/uploads/<year>/<month>/<name>.png`.
  Full-size originals are usually the URL with the `-1024x1024` suffix removed.
- Largest available: prefer 800px+ on the short side. Flat, plain-background
  art keys cleanly; sunbursts and gradients do not.
- Never use another parent's fan art, a watermarked stock image, or a
  screenshot cropped out of a video with UI in it.

### 2. Flatten the background

If the art sits on a flat colour, the script can key it (`--key auto`).

If the background is a gradient or sunburst, ask the image model to swap **only**
the background and keep the drawing untouched:

```
Edit this image. Keep the character EXACTLY identical: same face, same eyes,
same nose, same cheeks, same hair, same arms, same clothes, same colours, same
texture, same pose, same size and position. Do not redraw, restyle, move or
resize the character.

Change only the background: replace everything around the character with a flat,
even, warm cream paper colour (#FFFFE8) with a very subtle fine grain.

No text, no letters, no shapes, no shadows, no outline, no extra objects.
```

Verify the result before composing: the character must be unchanged.

### 2b. Paint the background

Generate the scene separately, with no character and no text, so it can be
composited behind clean type later:

```
Portrait 2:3 children's book background painting, flat 2D gouache with fine
paper grain, no characters, no text, no letters, no logos.
Scene: <one idea — meadow, sunburst, kitchen table, morning sky, bunting,
concentric rings, underwater, night sky>. Keep the top third calm and open for
a title.
```

Then pass it in with `--background`. Keep the character on its own layer: the
model paints, the script sets the character and the type.

If the character art was flattened onto cream and its body is cream/white, keying
will chew the silhouette. Either flatten onto chroma green (`#00B140`) instead,
or sit the character on a cream panel so the edge is invisible.

### 3. Compose

Each card keeps its two source assets beside the skill, so a re-typeset never
depends on temp files:

```
assets/<card>-plate.jpg       painted background, no character, no text
assets/<card>-character.png   official art, transparent, cropped to the character
```

```bash
python3 scripts/build_cover.py \
  --bg   assets/<card>-plate.jpg \
  --char assets/<card>-character.png \
  --char-width 0.84 \
  --title ANIMAL SONGS \
  --colour '#A63352' \
  --max-size 128 \
  --out playlists/<card>/cover.jpg
```

Useful flags: `--char-width` (fraction of card width), `--char-bottom`,
`--char-x`, `--max-size` (cap the type size so nine cards keep one scale),
`--no-mark`, `--jitter` (1.0 = hand-drawn, 0.35 for a CJK face).

CJK titles need a font with the glyphs — Baloo 2 has none:

```bash
--font "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc#2" --jitter 0.35
```

Rebuild every custom cover at once with `scripts/rebuild_custom_covers.sh`,
then `build_print.py` and `build_vendor.py`.

**When the character is painted into the plate, check the gap before typesetting.**
Measure where the top of the head/hat/ears sits as a fraction of the card. If it
is lower than the title needs (one CJK line wants ~33%, two Latin lines ~35%),
do not leave the dead band and do not float the title: raise the character by
cropping the empty top and letting the bottom run off the card.

```bash
python3 scripts/recompose_plate.py \
  --plate assets/<card>-plate.jpg --head 0.47 --target 0.335 \
  --out assets/<card>-plate.jpg
```

`--head` is the measured head top, before the crop. The script keeps the width,
crops the top, and scales by height, so the head lands exactly on `--target`;
the feet move to the bottom edge. Use it only on a plate whose gap is empty
wall or sky — if bubbles, bunting or props are filling the space, leave the
composition alone.

**Character extraction.** Cut the character onto flat chroma green (`#00B140`)
in the image model, then key it with `scripts/cutout.py`. `rembg` works only
where the character contrasts with its background: it eats cream characters on
pale skies and drags in props (moons, rings), so check every cut-out on magenta
before using it.

### 4. Check it

- Open the result next to `playlists/happy-songs/cover.jpg`. Cream tone, blue
  tone, title weight and character scale should look like siblings.
- Shrink it to **126px wide** (the Yoto app grid tile) and again to ~60px. The
  character must still be identifiable at 126 px — that is the size a child
  actually picks the card by. If it turns into a dot, generate it again larger
  rather than nudging the crop; the title may blur, the face may not.
- Look for a pale halo or green fringe at the character edge — increase
  `--erode` (default 7) if you see one.

### 5. The house mark

`build_cover.py` draws the `HimHim` mark itself, centred above the title, in
one fixed two-tone everywhere: `Him` in ink `#26323A`, `Him` in coral `#C9552F`,
and cream instead of ink on a dark card. Same word, lettering, size (38 px) and
position on every custom cover — that sameness is the brand.

The card's own title colour is deliberately **not** used: nine differently
coloured marks read as decoration, not a label. Never put a publisher's logo on
a card; `HimHim` is the family's mark, on cards we made only.

`scripts/add_brand.py` still exists for stamping the mark onto an already
finished image, but new covers get it from `build_cover.py`.

### 6. Record it

In the playlist's `reference.md`, say what the cover is and that it is **not
official artwork** — which art was used, that the background was replaced, and
that the title is a plain font, not the brand logo. Never imply a Yoto or brand
endorsement.

Keep the build reproducible. The plate and the character live in
`assets/<card>-plate.jpg` and `assets/<card>-character.png`, so a re-typeset
does not depend on temp files:

~~~~markdown
## Cover build

- **Character art:** <publisher> — <page or file URL>. Official art, background
  removed; kept as `.opencode/skills/yoto-cover/assets/<name>-character.png`.
- **Background:** painted for this card, no character and no text; kept as
  `.opencode/skills/yoto-cover/assets/<name>-plate.jpg`.
- **Composed** with the `yoto-cover` skill at **638 × 1011 px, 300 DPI**
  (54 × 85.6 mm) — one image per card, used for the app upload and the print
  sheet:

```bash
python3 .opencode/skills/yoto-cover/scripts/build_cover.py \
  --bg .opencode/skills/yoto-cover/assets/<name>-plate.jpg \
  --char .opencode/skills/yoto-cover/assets/<name>-character.png \
  --char-width 0.84 --max-size 128 \
  --title ANIMAL SONGS --colour '#A63352' \
  --out playlists/<name>/cover.jpg
```

- Not official Yoto art. Personal card only.
~~~~

Put the real `--char-width` and `--max-size` in that block — a recorded command
that no longer reproduces the image is worse than none.

## Pitfalls

- **Never put the publisher's logo on it** — Yoto's, Super Simple's, Ms.
  Rachel's. Use the family's own `HimHim` mark instead. A card that looks
  official is a problem; one that looks like the same *series* is the goal.
- **Don't trace over or filter a copyrighted image** to hide its origin. Use
  the publisher's own art, credit it in the reference file, and keep the card
  personal — no publishing, no selling.
- **One character, one idea.** A scene with six props reads as a YouTube
  thumbnail and will not match the shelf.
- **Title text must be exact.** If the model generates the lettering, check
  every letter. Prefer the script: fonts do not misspell.
- **Don't upscale small art.** A 200px character blown up to 1100px looks
  soft next to crisp type. Find a larger source instead.
