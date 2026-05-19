# Prompt - Pseudo 3D Office Foundation Atlas v1.1

Tooling: built-in imagegen / image-2 route
Generated: 2026-05-19
Purpose: source sheet for Godot transparent office-foundation sprites

```text
Use case: stylized-concept / game asset source atlas.
Asset type: source image for Startup Sim Godot v1.1 pseudo-3D office foundation atlas, later background removal and slicing.

Primary request: Create a single clean 8 columns x 4 rows asset atlas contact sheet for a top-down/slanted pseudo-3D light pixel art office-management game. The atlas must contain 32 separate modular office foundation assets, each centered in its own implied cell with generous padding, intended to be converted into transparent PNG sprites for Godot. Use an absolutely flat solid #ff00ff chroma-key background across the entire image, no shadows or gradients on the background, no texture on the background, no floor plane. Do not use #ff00ff anywhere in the assets.

Style: original pseudo-3D light pixel art, crisp readable silhouettes, moderate dark outlines, subtle pixel detail, warm modern startup office materials, unified upper-left light, soft object shadows included as part of each asset but not touching the image border, readable at small game scale. Camera shows asset tops plus front and right side faces. No copyrighted game style copying, no logos, no text, no labels, no numbers, no watermark.

Atlas layout: exactly 8 columns and 4 rows, evenly spaced. Each asset should be visually isolated and not overlap neighboring cells. No drawn grid lines, no row/column labels.

Row 1: office shell and boundary assets: 1 wall corner L piece, 2 straight wall segment with window, 3 glass divider segment, 4 entrance door segment, 5 square column/pillar, 6 exterior threshold strip, 7 buildable floor edge trim, 8 blocked floor edge trim.

Row 2: floor and light overlays: 1 office floor tile patch, 2 subtle carpet/rug zone patch, 3 cable run strip, 4 window light strip, 5 soft workstation shadow, 6 large facility shadow, 7 transparent hover highlight marker, 8 transparent selected-cell marker.

Row 3: build and zone markers: 1 placement valid marker, 2 placement invalid marker, 3 zone start marker, 4 zone end marker, 5 upgrade progress ring, 6 capacity warning marker, 7 path/traffic arrow marker, 8 department boundary corner marker.

Row 4: small office props: 1 potted plant, 2 printer/copier, 3 water cooler, 4 coffee machine, 5 small trash bin, 6 sticky note board with no readable text, 7 cable hub/router box, 8 desk accessory cluster.

Important transparency preparation: all assets are opaque or semi-opaque subjects on the flat #ff00ff background. Keep asset edges crisp and separated from the background. Do not include any text in the image. Do not use full-scene composition; this must look like a reusable sprite atlas source sheet, not a screenshot.
```

Post-processing:

- Copied generated source into this pack.
- Resized from 1774 x 887 to 1776 x 888 to form 8 x 4 square cells.
- Removed #ff00ff chroma-key background into alpha.
- Preserved the two shadow cells with neutral translucent shadow alpha.
- Sliced 32 individual PNG props from the transparent atlas.
