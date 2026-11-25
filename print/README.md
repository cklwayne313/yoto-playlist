# Print files

Everything here is true size. The only thing that can go wrong is the printer
scaling the page, so read the two rules below.

## What's here

| File | What it is |
|---|---|
| `png/<playlist>.png` | 638 × 1011 px at 300 DPI = **54 × 85.6 mm**, one label per file |
| `cards-a4.pdf` | 9 labels per A4 sheet, true size, with crop marks (5 pages) |
| `cards-letter.pdf` | 9 labels per US Letter sheet, true size, with crop marks |

Rebuild after changing a cover:

```bash
python3 .opencode/print/build_print.py
```

## Print rules

1. **Scale 100% / “Actual size”.** Turn off “Fit to page”, “Shrink to fit” and
   “Scale to printable area”. This is the mistake that makes labels come out
   small.
2. **Do a plain-paper test first.** Print one sheet and measure a card outline
   with a ruler. It must be 54 mm across. If it isn't, the scale is wrong — not
   the file.

## Size notes

- A Yoto card is **54 × 85.6 mm**, the same as a bank card (ISO ID-1). Native
  cover art is **638 × 1011 px at 300 DPI**.
- A label slightly smaller is easier to place: **50 × 82 mm** leaves a thin card
  border and hides a wonky cut. Trim inside the crop marks for that.
- Paper: matte vinyl sticker paper survives small hands; glossy shows every
  fingerprint. Plain paper is fine for a first try.
- The NFC chip reads through paper and vinyl. Thickness is the limit — peel the
  old label off before adding a new one.

## Not 43 × 85.5 mm

43 × 85.5 mm is not a Yoto dimension. It is a 0.503 ratio, against the card's
0.631, so an image printed at 43 × 85.5 would either be squeezed or lose about
20% of its width. If a specific label sheet really is 43 × 85.5, the covers need
to be **recomposed** at that ratio, not cropped — ask and it can be generated.
