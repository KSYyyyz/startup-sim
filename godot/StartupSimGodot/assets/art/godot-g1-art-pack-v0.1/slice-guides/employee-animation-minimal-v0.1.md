# employee-animation-minimal-v0.1 Slice Guide

Export: `exports/employee-animation-minimal-v0.1.png`
Source: `sources/employee-animation-minimal-v0.1-source.png`
Grid: 8 columns x 6 rows
Image size: 1536 x 1024 px
Approx cell: 192.0 x 170.67 px

## Godot Notes
- Import the PNG as a normal Texture2D.
- Use AtlasTexture or Sprite2D region for individual cells.
- For animation sheets, create frame resources in the row/column order described by the asset notes.
- Keep text, numbers, and localized labels in Godot UI controls rather than baked into images.

## Content Notes
Six employee roles with two-frame loops for walk, work, tired, and rest states.
