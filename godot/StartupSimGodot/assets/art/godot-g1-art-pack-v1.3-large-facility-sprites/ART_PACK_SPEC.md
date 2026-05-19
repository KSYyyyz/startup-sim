# Godot G1 Art Pack v1.3 - Large Facility Sprites

Status: production candidate  
Date: 2026-05-19  
Owner: Codex art-resource session

## Purpose

This pack provides larger 2.5D department facilities with visual states so office capability reads from the scene instead of from text alone.

## Assets

| Asset | Export | Size | Grid | Role |
| --- | --- | --- | --- | --- |
| large-facility-sprite-atlas-v1.3 | `exports/large-facility-sprite-atlas-v1.3.png` | 1776 x 888 | 8 x 4, 222px cells | Startup Sim Godot 2.5D large facility sprites and visual states |
| individual PNGs | `exports/facilities/*.png` | 222 x 222 each | 32 files | Direct Godot Sprite2D/TextureRect usage |
| transparent preview | `previews/large-facility-sprite-atlas-v1.3-transparent-contact-sheet.png` | 1776 x 888 | 8 x 4 | Checkerboard QA preview |

## Integration Notes

- Keep gameplay occupancy in grid/data logic.
- Use `textures` metadata from `asset-index.json` instead of guessing atlas coordinates.
- Honor `intended_layer`, `anchor`, `footprint_cells`, and `visual_size_cells` during Godot integration.
- Render all labels and numeric values with Godot UI nodes, not baked images.
