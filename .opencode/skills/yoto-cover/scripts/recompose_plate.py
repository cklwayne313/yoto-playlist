#!/usr/bin/env python3
"""Move the painted character's head to a fixed fraction of the card height.

The title band is fixed, so a plate whose character sits low leaves a dead band
under the title, and one whose character reaches too high crowds the type. This
keeps the width untouched and either crops the empty top (head too low) or
mirrors a strip of empty background above it (head too high).

    python3 recompose_plate.py --plate assets/x-plate.jpg --head 0.50 \
        --target 0.40 --out /tmp/x-plate.jpg

`--head` is where the character's head is now, measured on the plate as a
fraction of its height (eyes/hat/ears, whichever is highest).
"""
import argparse
import os

from PIL import Image

W, H = 638, 1011


def recompose(im, head, target):
    iw, ih = im.size
    if head > target:                      # head too low: crop the empty top
        d = (head - target) / (1 - target)
        cut = int(round(ih * d))
        im = im.crop((0, cut, iw, ih))
        # height governs: no vertical crop, so the head stays at target
        scale = H / im.height
        out = im.resize((max(W, round(iw * scale)), H), Image.LANCZOS)
        left = (out.width - W) // 2
        return out.crop((left, 0, left + W, H))

    # head too high: add a mirrored strip of background above it
    q = (target - head) / (1 - target)
    pad = max(1, int(round(ih * q)))
    canvas = Image.new("RGB", (iw, ih + pad))
    top = im.crop((0, 0, iw, pad)).transpose(Image.FLIP_TOP_BOTTOM)
    canvas.paste(top, (0, 0))
    canvas.paste(im, (0, pad))
    # width governs: crop the bottom, so the head stays at target
    scale = W / iw
    out = canvas.resize((W, round(canvas.height * scale)), Image.LANCZOS)
    return out.crop((0, 0, W, H))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", required=True)
    ap.add_argument("--head", type=float, required=True)
    ap.add_argument("--target", type=float, default=0.40)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    im = Image.open(args.plate).convert("RGB")
    out = recompose(im, args.head, args.target)
    out.save(args.out, dpi=(300, 300), quality=95)
    print(f"{args.out}  {im.size} -> {out.size}  head {args.head:.2f} -> {args.target:.2f}")


if __name__ == "__main__":
    main()
