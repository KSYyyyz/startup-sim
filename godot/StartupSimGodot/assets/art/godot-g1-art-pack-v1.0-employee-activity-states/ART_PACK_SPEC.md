# Godot G1 Art Pack v1.0 - Employee Activity States

Status: production candidate
Date: 2026-05-19
Owner: Codex art-resource session

## Purpose

This pack adds employee activity state sprites for autonomous office simulation. It helps Godot show what employees are doing without turning employee simulation into a text-only panel.

## Asset

| Asset | Export | Grid | Cell | Role |
| --- | --- | --- | --- | --- |
| employee-activity-state-atlas-v1.0 | `exports/employee-activity-state-atlas-v1.0.png` | 8 x 4 | 192 x 192 | Transparent employee activity atlas |
| sliced transparent icons | `exports/icons/*.png` | 32 files | 192 x 192 | Individual transparent employee activity PNGs |

## Rows

1. `product_engineer_variant`
2. `sales_specialist_variant`
3. `ops_engineer_variant`
4. `office_generalist_variant`

## Columns

1. `working_focus`
2. `rest_break`
3. `entertainment`
4. `restroom_need_away`
5. `sick_leave`
6. `training`
7. `emotional_pressure`
8. `idle_walk`

## Design Notes

- Transparent RGBA PNG for employee activity rendering.
- Characters are deliberately varied in age, face, hair, outfit, accessory, expression, skin tone, pose, and direction.
- No baked text, numbers, or UI panels.
- `restroom_need_away` uses a neutral stepping-away/door cue instead of explicit toilet imagery.
