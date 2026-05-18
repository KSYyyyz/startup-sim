# recruitment-portrait-sheet-v0.1 Slice Guide

Export: `exports/recruitment-portrait-sheet-v0.1.png`
Source: `sources/recruitment-portrait-sheet-v0.1-source.png`
Grid: 4 columns x 3 rows
Image size: 1536 x 1024 px
Approx cell: 384.0 x 341.33 px

## Godot Notes
- Import the PNG as a normal Texture2D.
- Use AtlasTexture, Sprite2D region, or TileSet atlas source depending on the consuming scene.
- Keep filtering consistent with the final art direction. For small sprites, test nearest vs linear in Godot before locking it.
- Trim transparent padding only after confirming grid-region alignment in the target scene.

## Content Notes
First portrait pass with strong role, age, clothing, and accessory variety.
