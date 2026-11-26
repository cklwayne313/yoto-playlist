#!/usr/bin/env bash
# Rebuild the nine custom covers from their stored plates and character cut-outs.
#
#   bash .opencode/skills/yoto-cover/scripts/rebuild_custom_covers.sh
#
# Assets live in .opencode/skills/yoto-cover/assets/ — one painted plate and one
# transparent character per card — so a re-typeset never depends on temp files.
# Then rebuild the print sets:
#
#   python3 .opencode/print/build_print.py
#   python3 .opencode/print/build_vendor.py
set -euo pipefail

cd "$(dirname "$0")/../../../.."

S=.opencode/skills/yoto-cover/scripts/build_cover.py
A=.opencode/skills/yoto-cover/assets
P=playlists
CJK="/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc#2"

build() { # card  colour  char-width  max-size  [--font CJK]  title...
  local card=$1 colour=$2 width=$3 cap=$4; shift 4
  local font=()
  [ "$1" = "--cjk" ] && { font=(--font "$CJK" --jitter 0.35); shift; }
  [ "$1" = "--no-tint" ] && { font+=(--no-tint); shift; }
  python3 "$S" \
    --bg "$A/$card-plate.jpg" \
    --char "$A/$card-character.png" \
    --char-width "$width" \
    --char-top "${CHAR_TOP:-0.40}" \
    --char-x "${CHAR_X:-0}" \
    --max-size "$cap" \
    "${font[@]}" \
    --title "$@" \
    --colour "$colour" \
    --out "$P/$card/cover.jpg"
}

build speech-therapy-animals             '#A63352' 0.84 128 ANIMAL  SONGS
build speech-therapy-actions             '#C25E1E' 0.78 120 ACTION  SONGS
build speech-therapy-food                '#056158' 1.00 128 FOOD    SONGS
build speech-therapy-routines            '#134574' 0.52 120 ROUTINE SONGS
build speech-therapy-social              '#902D65' 0.84 124 SOCIAL  SONGS
build speech-therapy-feelings            '#74380F' 0.92 120 FEELING SONGS
CHAR_X=-0.04 build speech-therapy-cantonese-animals '#235325' 0.72 140 --cjk 動物歌
build speech-therapy-cantonese-routines  '#FDF1B9' 0.74 140 --cjk 日常歌
build super-simple-favourites            '#0B6FA8' 0.84 118 MY PICKS
