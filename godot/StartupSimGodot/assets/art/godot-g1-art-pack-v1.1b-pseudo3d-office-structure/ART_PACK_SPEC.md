# Godot G1 Art Pack v1.1b - Pseudo 3D Office Structure

Status: production candidate  
Date: 2026-05-19  
Owner: Codex art-resource session

## Purpose

This pack adds modular 2.5D floor, wall, door, window, glass, and architectural connector assets so the renderer can build an office space instead of drawing a flat debug board.

## Assets

| Asset | Export | Size | Grid | Role |
| --- | --- | --- | --- | --- |
| pseudo3d-office-structure-atlas-v1.1b | `exports/pseudo3d-office-structure-atlas-v1.1b.png` | 1776 x 888 | 8 x 4, 222px cells | Startup Sim Godot 2.5D office floor, wall, and connector reinforcement |
| individual PNGs | `exports/tiles/*.png` | 222 x 222 each | 32 files | Direct Godot Sprite2D/TextureRect usage |
| transparent preview | `previews/pseudo3d-office-structure-atlas-v1.1b-transparent-contact-sheet.png` | 1776 x 888 | 8 x 4 | Checkerboard QA preview |

## Integration Notes

- Keep gameplay occupancy in grid/data logic.
- Use `textures` metadata from `asset-index.json` instead of guessing atlas coordinates.
- Honor `intended_layer`, `anchor`, `footprint_cells`, and `visual_size_cells` during Godot integration.
- Render all labels and numeric values with Godot UI nodes, not baked images.
