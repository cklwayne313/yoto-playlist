#!/usr/bin/env bash
# Rebuild the nine non-Cantonese custom covers from their stored plates.
#
#   bash .opencode/skills/yoto-cover/scripts/rebuild_custom_covers.sh
#
# Each plate in .opencode/skills/yoto-cover/assets/ is now a finished painting:
# the background and the character are one image, so a re-typeset only needs the
# plate, the mark and the title. Nothing is composited any more.
#
#   python3 .opencode/print/build_print.py
#   python3 .opencode/print/build_vendor.py
set -euo pipefail

cd "$(dirname "$0")/../../../.."

S=.opencode/skills/yoto-cover/scripts/build_cover.py
A=.opencode/skills/yoto-cover/assets
P=playlists
CJK="/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc#2"

build() { # card  colour  max-size  [--cjk]  WORD...
  local card=$1 colour=$2 cap=$3; shift 3
  local font=(--title-top 0.12 --title-bottom 0.36)
  [ "$1" = "--cjk" ] && { font=(--font "$CJK" --jitter 0.35 --title-top 0.12 --title-bottom 0.34); shift; }
  python3 "$S" \
    --bg "$A/$card-plate.jpg" \
    --max-size "$cap" \
    "${font[@]}" \
    --title "$@" \
    --colour "$colour" \
    --out "$P/$card/cover.jpg"
}

build speech-therapy-animals   '#A63352' 128 ANIMAL  SONGS
build speech-therapy-actions   '#C25E1E' 120 ACTION  SONGS
build speech-therapy-food      '#056158' 128 FOOD    SONGS
build speech-therapy-routines  '#134574' 120 ROUTINE SONGS
build speech-therapy-social    '#902D65' 124 SOCIAL  SONGS
build speech-therapy-feelings  '#74380F' 120 FEELING SONGS
build speech-therapy-cantonese-animals '#235325' 140 --cjk 動物歌
build speech-therapy-cantonese-routines '#FDF1B9' 140 --cjk 日常歌
build super-simple-favourites  '#0B6FA8' 118 MY PICKS
