# Godot G1 Art Pack v1.2 - Zone Carpets and Build Markers

Status: production candidate  
Date: 2026-05-19  
Owner: Codex art-resource session

## Purpose

This pack replaces debug-colored regions with 2.5D department carpets, projected-cell highlights, construction markers, and zone status overlays.

## Assets

| Asset | Export | Size | Grid | Role |
| --- | --- | --- | --- | --- |
| zone-carpet-build-marker-atlas-v1.2 | `exports/zone-carpet-build-marker-atlas-v1.2.png` | 1776 x 888 | 8 x 4, 222px cells | Startup Sim Godot 2.5D department carpets and projected build markers |
| individual PNGs | `exports/overlays/*.png` | 222 x 222 each | 32 files | Direct Godot Sprite2D/TextureRect usage |
| transparent preview | `previews/zone-carpet-build-marker-atlas-v1.2-transparent-contact-sheet.png` | 1776 x 888 | 8 x 4 | Checkerboard QA preview |

## Integration Notes

- Keep gameplay occupancy in grid/data logic.
- Use `textures` metadata from `asset-index.json` instead of guessing atlas coordinates.
- Honor `intended_layer`, `anchor`, `footprint_cells`, and `visual_size_cells` during Godot integration.
- Render all labels and numeric values with Godot UI nodes, not baked images.
