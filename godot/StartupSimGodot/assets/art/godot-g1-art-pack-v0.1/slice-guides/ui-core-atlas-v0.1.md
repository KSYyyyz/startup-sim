# ui-core-atlas-v0.1 Slice Guide

Export: `exports/ui-core-atlas-v0.1.png`
Source: `sources/ui-core-atlas-v0.1-source.png`
Grid: 6 columns x 4 rows
Image size: 1536 x 1024 px
Approx cell: 256.0 x 256.0 px

## Godot Notes
- Import the PNG as a normal Texture2D.
- Use AtlasTexture or Sprite2D region for individual cells.
- For animation sheets, create frame resources in the row/column order described by the asset notes.
- Keep text, numbers, and localized labels in Godot UI controls rather than baked into images.

## Content Notes
HUD, metric cards, employee/recruitment panels, build menu, monthly report modal, toast frames, progress bars, and time controls.
