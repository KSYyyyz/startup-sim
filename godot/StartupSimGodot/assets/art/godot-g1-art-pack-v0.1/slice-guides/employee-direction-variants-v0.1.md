# employee-direction-variants-v0.1 Slice Guide

Export: `exports/employee-direction-variants-v0.1.png`
Source: `sources/employee-direction-variants-v0.1-source.png`
Grid: 6 columns x 4 rows
Image size: 1536 x 1024 px
Approx cell: 256.0 x 256.0 px

## Godot Notes
- Import the PNG as a normal Texture2D.
- Use AtlasTexture, Sprite2D region, or TileSet atlas source depending on the consuming scene.
- Keep filtering consistent with the final art direction. For small sprites, test nearest vs linear in Godot before locking it.
- Trim transparent padding only after confirming grid-region alignment in the target scene.

## Content Notes
Front, left, right, and back directions for the same six role silhouettes.
