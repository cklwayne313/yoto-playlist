#!/usr/bin/env python3
"""Key a chroma-green character render down to a transparent PNG.

    python3 cutout.py /tmp/opencode/iso-food.png assets/speech-therapy-food-character.png

Characters are isolated on flat #00B140 by the image model, then keyed here.
The result is cropped to the character, so the composer places it by width and
distance from the bottom of the card rather than by canvas position.
"""

import argparse

import numpy as np
from PIL import Image, ImageFilter

KEY = np.array([0, 177, 64], dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--tol", type=float, default=70.0)
    ap.add_argument("--erode", type=int, default=3)
    args = ap.parse_args()

    im = Image.open(args.src).convert("RGB")
    rgb = np.asarray(im).astype(np.float32)

    dist = np.sqrt(((rgb - KEY) ** 2).sum(axis=2))
    solid = (dist > args.tol).astype(np.uint8) * 255

    if args.erode:
        solid = np.asarray(Image.fromarray(solid, "L").filter(
            ImageFilter.MinFilter(args.erode * 2 + 1)))

    alpha = Image.fromarray(solid, "L").filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA")
    out.putalpha(alpha)

    # despill: pull green out of the fringe
    arr = np.asarray(out).astype(np.float32)
    edge = (np.asarray(alpha) > 0) & (np.asarray(alpha) < 250)
    g = arr[:, :, 1]
    spike = edge & (g > arr[:, :, 0] + 18) & (g > arr[:, :, 2] + 18)
    arr[:, :, 1] = np.where(spike, (arr[:, :, 0] + arr[:, :, 2]) / 2, arr[:, :, 1])
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    out = out.crop(out.getbbox())
    out.save(args.out, optimize=True)
    print(f"{args.out}  {out.size}")


if __name__ == "__main__":
    main()
