#!/usr/bin/env bash
# Re-typeset every custom cover from its stored plate.
#
#   bash .opencode/skills/yoto-cover/scripts/rebuild_custom_covers.sh
#
# Plates are finished paintings with the character already in the scene. Nine of
# them were re-composed with recompose_plate.py so the head sits just under the
# title (see the "character top" note in SKILL.md); the plate in assets/ is the
# composed one, so this script only sets the mark and the title.
#
# After a re-typeset:
#   python3 .opencode/print/build_print.py
#   python3 .opencode/print/build_vendor.py
set -euo pipefail

cd "$(dirname "$0")/../../../.."

S=.opencode/skills/yoto-cover/scripts
A=.opencode/skills/yoto-cover/assets
P=playlists
CJK="/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc#2"

# The title ink is centred between the mark and the head, so the obvious gap
# under the mark and the gap above the character stay equal. The title band
# stops where the character starts: 34% for one CJK line, 36% for two Latin.
build_en() { # card colour max-size WORD...
  local card=$1 colour=$2 cap=$3; shift 3
  python3 "$S/build_cover.py" \
    --bg "$A/$card-plate.jpg" \
    --title-bottom 0.36 --max-size "$cap" \
    --title "$@" --colour "$colour" --out "$P/$card/cover.jpg"
}

build_cjk() { # card colour WORD
  local card=$1 colour=$2; shift 2
  python3 "$S/build_cover.py" \
    --bg "$A/$card-plate.jpg" --font "$CJK" --jitter 0.35 \
    --title-bottom 0.34 --max-size 140 \
    --title "$@" --colour "$colour" --out "$P/$card/cover.jpg"
}

# --- speech therapy, English -------------------------------------------------
build_en speech-therapy-animals   '#A63352' 128 ANIMAL  SONGS
build_en speech-therapy-actions   '#C25E1E' 120 ACTION  SONGS
build_en speech-therapy-food      '#056158' 128 FOOD    SONGS
build_en speech-therapy-routines  '#134574' 120 ROUTINE SONGS
build_en speech-therapy-social    '#902D65' 124 SOCIAL  SONGS
build_en speech-therapy-feelings  '#74380F' 120 FEELING SONGS
build_en super-simple-favourites  '#0B6FA8' 118 MY PICKS

# --- Cantonese ---------------------------------------------------------------
build_cjk speech-therapy-cantonese     '#165462' 說話歌
build_cjk cantonese-animal-songs      '#216347' 動物朋友
build_cjk cantonese-christmas-songs    '#FDFCEA' 聖誕歌
build_cjk cantonese-community-songs    '#863C23' 社區英雄
build_cjk cantonese-concept-songs      '#2A455F' 認知歌
build_cjk cantonese-faith-songs        '#3F3F7A' 跟隨歌
build_cjk cantonese-happy-songs        '#B4401C' 開心歌
build_cjk cantonese-life-songs         '#0D534D' 生活歌
build_cjk cantonese-movement-songs     '#7F2644' 動作歌
build_cjk cantonese-play-songs         '#12544F' 遊戲歌
build_cjk cantonese-rhymes-active      '#A93E23' 跳跳歌
build_cjk cantonese-rhymes-calm        '#312F5F' 慢慢歌
build_cjk cantonese-singles            '#603562' 精選歌
build_cjk cantonese-transport-songs    '#234462' 交通工具
build_cjk speech-therapy-cantonese-animals   '#235325' 動物歌
build_cjk speech-therapy-cantonese-routines  '#FDF1B9' 日常歌
# cantonese-nursery-rhymes (童謠) is not rebuilt: its white title is part of the
# blue brush in the borrowed Yoto art, not typeset over a plate.
