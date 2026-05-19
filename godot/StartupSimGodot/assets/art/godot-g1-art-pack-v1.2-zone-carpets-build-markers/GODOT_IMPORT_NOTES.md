# Godot Import Notes - 1.2

## Files

- Atlas: `exports/zone-carpet-build-marker-atlas-v1.2.png`
- Individual PNGs: `exports/overlays/*.png`
- Preview: `previews/zone-carpet-build-marker-atlas-v1.2-transparent-contact-sheet.png`

## Recommended Usage

Use `asset-index.json` `textures` entries as the source of truth. Do not hard-code row/column meanings from visual inspection.

## Atlas Settings

- Resource type: `Texture2D`
- Atlas grid: 8 columns x 4 rows
- Region size: 222 x 222 px
- Import alpha: enabled
- Filter: nearest or nearest-with-mipmaps depending on final scaling tests

## Text Policy

Do not use any image from this pack for localized text. Chinese labels, metrics, months, and report text should be rendered by Godot UI nodes.
