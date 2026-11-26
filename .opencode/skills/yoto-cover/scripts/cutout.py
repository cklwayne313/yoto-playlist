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
    ap.add_argument("--erode", type=int, default=2)
    ap.add_argument("--feather", type=float, default=55.0,
                    help="width of the soft alpha ramp, in colour distance")
    args = ap.parse_args()

    im = Image.open(args.src).convert("RGB")
    rgb = np.asarray(im).astype(np.float32)

    dist = np.sqrt(((rgb - KEY) ** 2).sum(axis=2))

    # soft edge: a ramp between two thresholds, not a hard cut, so the
    # silhouette stays smooth at card size
    t0 = args.tol
    t1 = args.tol + args.feather
    alpha = np.clip((dist - t0) / max(1.0, t1 - t0), 0, 1)

    if args.erode:
        alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8), "L")
                           .filter(ImageFilter.MinFilter(args.erode * 2 + 1))).astype(np.float32) / 255

    out = im.convert("RGBA")
    out.putalpha(Image.fromarray((alpha * 255).astype(np.uint8), "L"))

    # despill: pull green out of the fringe
    arr = np.asarray(out).astype(np.float32)
    a = arr[:, :, 3]
    edge = (a > 6) & (a < 250)
    g = arr[:, :, 1]
    spike = edge & (g > arr[:, :, 0] + 14) & (g > arr[:, :, 2] + 14)
    arr[:, :, 1] = np.where(spike, (arr[:, :, 0] + arr[:, :, 2]) / 2, arr[:, :, 1])
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

    out = out.crop(out.getbbox())
    out.save(args.out, optimize=True)
    print(f"{args.out}  {out.size}")


if __name__ == "__main__":
    main()
