# Godot G1 Art Pack v1.1 - Pseudo 3D Office Foundation

Status: production candidate
Date: 2026-05-19
Owner: Codex art-resource session

## Purpose

This pack adds the first pseudo-3D office foundation assets for the Godot office-management prototype.
It is designed to make the current rectangular `OfficeGridView` read more like a slanted, light-pixel,
office tycoon game surface without requiring a gameplay-coordinate rewrite.

## Assets

| Asset | Export | Size | Grid | Role |
| --- | --- | --- | --- | --- |
| pseudo3d-office-foundation-atlas-v1.1 | `exports/pseudo3d-office-foundation-atlas-v1.1.png` | 1776 x 888 | 8 x 4, 222px cells | Office shell, floor overlays, build markers, small props |
| individual props | `exports/props/*.png` | 222 x 222 each | 32 files | Direct Godot Sprite2D/TextureRect usage |
| transparent preview | `previews/pseudo3d-office-foundation-atlas-v1.1-transparent-contact-sheet.png` | 1776 x 888 | 8 x 4 | Checkerboard QA preview |

## Row Map

1. Office shell and boundary: wall corner, window wall, glass divider, entrance, column, threshold, buildable edge, blocked edge.
2. Floor and light overlays: floor patch, carpet patch, cable strip, window light, workstation shadow, large facility shadow, hover marker, selected marker.
3. Build and zone markers: placement valid, placement invalid, zone start, zone end, upgrade ring, capacity warning, traffic arrow, department boundary corner.
4. Small office props: plant, printer, water cooler, coffee machine, trash bin, sticky-note board, cable/router box, desk accessory cluster.

## Design Notes

- Original pseudo-3D light pixel art.
- Upper-left light and lower-right depth cues.
- Transparent PNG outputs for Godot layering.
- No baked text, numbers, logos, or localized labels.
- Intended to layer above the v0.7.1 background and below v0.8-v1.0 interactive feedback assets.

## Integration Notes

- Keep the current rectangular gameplay grid for now.
- Align larger shell/prop sprites by their lower visual footprint rather than by center point.
- Use the floor, carpet, shadow, hover, selected, and placement markers as overlays in `OfficeGridView` or future `OfficeWorld` layers.
- Use Godot `Label` / `RichTextLabel` for any user-facing text.
