# Yoto playlists

One folder per card: a `reference.md` with the link it was inspired by, a
numbered track list, and a YouTube link for every song — plus the card's own
`cover.jpg` when it mirrors a real Yoto card.

No scripts, no audio files. Links and art only.

**→ See [RANKING.md](RANKING.md)** for which playlists are actually good for a
2-year-old with a speech delay — rated, with verdicts and the cards that were
rejected.

## Current playlists

| Playlist | Tracks | Runtime | Notes |
|---|---|---|---|
| `sing-with-raffi` | 10 | 21:28 | official audio, exact durations — best speech input |
| `cantonese-nursery-rhymes` | 12 | 21:49 | Hong Kong recordings only |
| `pre-school-songs` | 15 | 33:11 | Old MacDonald card, recordings differ |
| `farm-songs` | 15 | ~40 min | Super Simple Farm Songs |
| `happy-songs` | 14 | 40:59 | 13 of 14 durations match exactly |
| `little-bo-peep` | 15 | 34:30 | 15 sung, 15 instrumentals dropped |
| `row-your-boat` | 15 | 38:12 | 15 sung, 15 instrumentals dropped |
| `best-of-the-wiggles` | 20 | 38:05 | movement songs, official audio |
| `blippi-vehicles` | 12 | 32:30 | 12/12 official, vehicle vocabulary |
| `doggyland` | 17 | 31:43 | 17/17 official, affirmations + social scripts |
| `sesame-street` | 10 | 19:01 | 10/10 official, ABC/number songs |
| `sing-and-dance-with-raffi` | 10 | 17:44 | 10/10 official, exact durations |
| `super-simple-christmas` | 15 | 39:11 | 15/15 official, seasonal |
| `super-simple-favourites` | 16 | 37:58 | your six + routines/actions, official; custom cover art |
| `bedtime-songs` | 15 | 37:51 | Super Simple Bedtime Songs, real card art |
| `silly-songs` | 15 | 40:31 | Super Simple Silly Songs, real card art |
| `underwater-songs` | 14 | 36:17 | Super Simple Underwater Songs, real card art |
| `speech-therapy-english` | 12 | 28:16 | SLP-sourced set, a target per track |
| `speech-therapy-cantonese` | 12 | 24:54 | HK therapy channels, no Mandarin |
| `speech-therapy-animals` | 10 | 28:02 | animal names + sounds |
| `speech-therapy-actions` | 10 | 21:49 | verbs, all Noodle & Pals |
| `speech-therapy-food` | 10 | 23:56 | mealtime words + choosing |
| `speech-therapy-routines` | 10 | 20:56 | shoes → teeth → bath → bed |
| `speech-therapy-social` | 10 | 21:48 | greet, ask, share, thank |
| `speech-therapy-feelings` | 10 | 24:00 | name a feeling, then settle |
| `speech-therapy-cantonese-animals` | 10 | 23:02 | 動物名 + 動物聲 |
| `speech-therapy-cantonese-routines` | 10 | 21:15 | 早晨到睡覺的程序 |
| `caspar-traditional` | 20 | 46:34 | acoustic, official, best of the new batch for age 2 |
| `caspar-singalong` | 16 | 40:19 | acoustic originals, call-and-response |
| `sesame-elmo` | 10 | 17:19 | Elmo's World songs, official |
| `moana` | 13 | 28:39 | Disney soundtrack |
| `moana-2` | 16 | 32:41 | Disney, cleanest Disney match |
| `frozen-2` | 11 | 31:15 | Disney soundtrack |
| `encanto` | 9 | 31:55 | Disney soundtrack |
| `tangled` | 9 | 21:04 | Disney soundtrack |
| `lion-king` | 12 | 46:29 | Disney, film score included |
| `kidz-bop-party` | 10 | 33:08 | exact durations, but 5–8 material |

## Covers

Playlists that mirror a real Yoto card keep that card's artwork as `cover.jpg`,
pulled from the product page. Upload it as the playlist image when you create
the Make Your Own card, and it looks the same on the player.

- It's the publisher's artwork, so it's for your own card — don't redistribute it.
- `cantonese-nursery-rhymes` uses Yoto's *Nursery Rhymes* art as a thematic
  stand-in; no Cantonese card exists.
- `speech-therapy-english` uses Ms. Rachel's *I'm So Happy* art — the closest
  Yoto card to the theme, since her show began as a speech-and-language resource.
- `speech-therapy-cantonese` uses Yoto's *Animal Sounds* art; animal sounds are
  the first thing a late talker imitates.
- The eight target cards use **eight different Super Simple characters**, one per
  card, so no two covers repeat: the Roundabouts pig (animals), the yellow
  Noodle & Pals friend (actions), a Bumble Num (food), Carl's Rescue Crew
  (routines), a Rhymington Square monster (social), Lulu the Owl (feelings), the
  Peekaboo cat (Cantonese animals) and a Roundabouts penguin (Cantonese
  routines). Each sits in its own painted scene — meadow, sunburst, kitchen,
  morning sky, party wall, sand rings, garden, night sky — with its own title
  colour, so no two read as the same template. The characters are Super
  Simple's; the backgrounds were painted for these cards.
- `super-simple-favourites` has a custom cover: Super Simple's own Noodle
  artwork, cream background, hand-lettered title.

Custom covers are built with the **`yoto-cover` skill** —
`.opencode/skills/yoto-cover/` holds the house style (1200×1902, cream
`#FFFFE8`, Yoto blue `#0392D4`, one character, no scenery) and
`scripts/make_cover.py`, which keys the art, composes the card and sets the
title. Ask for a cover and it runs automatically.

## Adding a playlist

Send a YouTube link — a playlist, a single video, or a card you've seen. I'll add
`playlists/<name>/reference.md` with the tracks pulled out, in order, each with
its link, and notes on anything swapped or missing.

## Printing the covers

Every card has **one** image: `playlists/<name>/cover.jpg` at **638 × 1011 px,
300 DPI** — 54 × 85.6 mm, the size of a Yoto card. That same file is what the app
accepts and what the print sheets embed. `print/` holds A4 / US Letter sheets
with nine labels each and crop marks. Print at **100% / Actual size** — never
"fit to page". Rebuild with:

```bash
python3 .opencode/print/build_print.py
```

See [print/README.md](print/README.md) for paper and trimming notes.

## Browsing it as a website

`docs/` is a generated static site: the ranked shelf, one page per playlist with
clickable links and covers, plus the ranking and this readme. Rebuild after
editing any markdown:

```bash
python3 .opencode/site/build.py
```

To publish on GitHub Pages: push the repo, then **Settings → Pages → Deploy from
a branch → `main` / `/docs`**. The site works from a subpath, so
`https://<user>.github.io/<repo>/` is fine.

## Using a playlist

1. Open its `reference.md` and listen through the links.
2. Put the audio on a Make Your Own playlist at
   [yotoplay.com](https://yotoplay.com) (Make Your Own → create playlist).
3. Link the blank card: Yoto app → *Players* → your player → *Link a card*, then
   hold the card flat on the player's NFC spot until it beeps.

## Format

```markdown
# Playlist name

**Inspired by:** <link>
**Cover:** `cover.jpg`
**Tracks:** 14 · **Runtime:** 40:59 · **Status:** verified

| # | Track | Length | Channel | Listen |
|---|-------|--------|---------|--------|
| 1 | Song name | 3:55 | Channel | https://youtu.be/xxxxxxxxxxx |
```

## Removed for being unbuildable

Three cards were dropped rather than half-mirrored:

- **Ms. Rachel — I'm So Happy** — her album isn't on YouTube; only hour-long
  compilations. Buy the card; it's the best speech content of the lot.
- **Brown Bear & Friends** — an audiobook, and the only YouTube copies are
  unauthorised read-alouds. Read the board book instead.
- **The Laurie Berkner Collection** — a 3-card pack of 20–40 minute albums, not
  a track list.

Nothing here is blocked from coming back — say the word if you want one rebuilt.
