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
| Canvas | 1200 × 1902 (2:3 portrait) |
| Background | a simple painted scene, generated for that card — sky, hills, waves, bunting, stars. Not a flat fill: flat is what makes a custom card look homemade |
| Title | chunky rounded, hand-lettered (each glyph slightly rotated, scaled and dropped), fine grain and a soft shadow, top ~9–34%. Blue `#0392D4` on cream is the default; vary the colour with the background |
| Character | official brand art, chest-up, top of head ~37% down, body runs off the bottom edge |
| Props | one scene idea per card, painted in the background. Not a collage of objects around the character |
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

```bash
python3 scripts/make_cover.py \
  --art /tmp/opencode/noodle-cream.jpg \
  --background /tmp/opencode/bg-meadow.jpg \
  --title "MY" "FAVOURITES" \
  --out playlists/<name>/cover.jpg
```

Useful flags: `--char-top 700` (head position), `--char-width 1120`,
`--bg '#FFFFE8'`, `--blue '#0392D4'`, `--no-grain`, `--key auto|none`,
`--key-color '#RRGGBB'`, `--font path.ttf`.

Title control: `--jitter 1.0` sets how hand-drawn the lettering is (`0` gives
clean vector type), `--seed 7` re-rolls it. The lettering is deterministic for a
given seed, so a recorded command reproduces the file byte-for-byte.

Variation: a set of cards with identical cream and blue reads as one template.
Give each card its own `--bg`, `--blue` (title) and one `--motif` (`circle`,
`hill` or `dots`) with `--accent`, ideally sampled from the character. Real Yoto
cards each have their own scene; two cards in the same series should not look
interchangeable. `--title-scale 0.9` lightens a long word.

Art control: `--anchor-bottom` sits the character on the card's bottom edge.
Use it whenever the source art is cropped at the bottom — otherwise the cut
floats mid-card and looks like a mistake. `--fade-bottom N` is a softer fallback
but turns black characters grey, so prefer anchoring.

The script keys the flat background, erodes the matte to kill halos, pastes the
character on a grained cream canvas, and auto-sizes the title into the space
above it. It downloads Baloo 2 ExtraBold to `~/.cache/yoto-cover/` on first run
if no font is supplied.

### 4. Check it

- Open the result next to `playlists/happy-songs/cover.jpg`. Cream tone, blue
  tone, title weight and character scale should look like siblings.
- Shrink it to ~200px wide (the Yoto app tile size). The character must still
  read; the title may not, which is fine.
- Look for a pale halo or green fringe at the character edge — increase
  `--erode` (default 7) if you see one.

### 5. Record it

In the playlist's `reference.md`, say what the cover is and that it is **not
official artwork** — which art was used, that the background was replaced, and
that the title is a plain font, not the brand logo. Never imply a Yoto or brand
endorsement.

Keep the build reproducible. Save the flattened art beside the cover as
`cover-source.jpg` and copy the exact command into a `## Cover build` section:

~~~~markdown
## Cover build

- **Character art:** <publisher> — <page or file URL>
- **Background:** replaced with flat cream; drawing untouched. Flattened file
  kept as `cover-source.jpg`.
- **Composed** with the `yoto-cover` skill:

```bash
python3 .opencode/skills/yoto-cover/scripts/make_cover.py \
  --art playlists/<name>/cover-source.jpg \
  --title MY FAVOURITES \
  --out playlists/<name>/cover.jpg
```

- Composed at 1200×1902, then normalised to the card file: **638×1011 px at
  300 DPI** (54×85.6 mm) with
  `python3 .opencode/print/build_print.py --normalise`. One image per card —
  the app upload and the print sheet use the same file.
- Not official Yoto art. Personal card only.
~~~~

If you changed any default (`--char-top`, `--char-width`, `--erode`), put the
real values in that block — a recorded command that no longer reproduces the
image is worse than none.

## Pitfalls

- **Do not put the brand logo on it.** Use a plain word in the same shape
  language. A card that looks official is a problem; one that looks like the
  same *series* is the goal.
- **Don't trace over or filter a copyrighted image** to hide its origin. Use
  the publisher's own art, credit it in the reference file, and keep the card
  personal — no publishing, no selling.
- **One character, one idea.** A scene with six props reads as a YouTube
  thumbnail and will not match the shelf.
- **Title text must be exact.** If the model generates the lettering, check
  every letter. Prefer the script: fonts do not misspell.
- **Don't upscale small art.** A 200px character blown up to 1100px looks
  soft next to crisp type. Find a larger source instead.
