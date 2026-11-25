# Vendor files — 54 × 85.5 mm

Two complete sets, 37 cards each. Send the one your printer asks for.

| Folder | Size | Bleed | Use when |
|---|---|---|---|
| `vendor/trim/` | **638 × 1010 px** = 54 × 85.5 mm at 300 DPI | none | the vendor's template is exactly the finished size |
| `vendor/bleed/` | **708 × 1080 px** = 60 × 91.5 mm | **3 mm** on every side | the vendor prints with bleed and trims to 54 × 85.5 |

The bleed set is made by extending the edge pixels outward, not by scaling the
art. The central 54 × 85.5 mm is identical to the trim file, so nothing inside
the cut line moves or shrinks.

All files: JPEG, quality 95, sRGB, 300 DPI, portrait. Filenames match the
playlist folders.

## Ask the vendor these three questions

1. **Bleed?** If yes, send `vendor/bleed/`. If they say "no bleed", send
   `vendor/trim/`. Sending trim art to a bleed workflow gives white edges.
2. **CMYK or RGB?** These are sRGB. Most sticker shops accept RGB and convert;
   if they insist on CMYK, ask for their profile and the colours can be converted.
3. **PDF or images?** Individual JPEGs are fine for most. If they want one
   imposed sheet or a PDF, that can be generated.

The corners are square in these files. If the vendor dies them to the card's
rounded corners, that is done on their side — no change needed here.

Rebuild:

```bash
python3 .opencode/print/build_vendor.py
```
