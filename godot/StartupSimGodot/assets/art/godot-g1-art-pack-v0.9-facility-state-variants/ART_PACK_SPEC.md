# Godot G1 Art Pack v0.9 - Facility State Variants

Status: production candidate
Date: 2026-05-19
Owner: Codex art-resource session

## Purpose

This pack adds state variants for the current G1 core facilities. It supports placement previews, facility upgrades, blocked/inefficient feedback, and visible active/high-efficiency states.

## Asset

| Asset | Export | Grid | Cell | Role |
| --- | --- | --- | --- | --- |
| facility-state-variant-atlas-v0.9 | `exports/facility-state-variant-atlas-v0.9.png` | 8 x 3 | 224 x 224 | Transparent facility state atlas |
| sliced transparent icons | `exports/icons/*.png` | 24 files | 224 x 224 | Individual transparent facility state PNGs |

## Rows

1. `basic_desk`
2. `product_whiteboard`
3. `starter_server_rack`

## Columns

1. `idle`
2. `active`
3. `upgrading`
4. `blocked`
5. `inefficient`
6. `high_efficiency`
7. `placement_valid`
8. `placement_invalid`

## Design Notes

- Transparent RGBA PNG for layering in the office scene.
- Covers the current data-layer facilities instead of adding new content scope.
- Placement states are visual previews only; Godot/data validation remains authoritative.
- No baked text, numbers, or business rules.
