# Godot G1 Art Pack v0.7.1 - Company Main Scene Background

Status: production candidate
Date: 2026-05-19
Owner: Codex art-resource session

## Purpose

This pack adds the first full company main-scene background for the Godot office-management prototype.
It is intended to sit under the office grid, zone overlays, facilities, employees, feedback FX, and HUD.

## Asset

| Asset | Export | Size | Role |
| --- | --- | --- | --- |
| company-main-scene-background-v0.7.1 | `exports/company-main-scene-background-v0.7.1.png` | 1920 x 1080 | Opaque main office background |

## Design Notes

- Top-down / slightly isometric office view.
- Central office floor is intentionally open for buildable gameplay.
- Walls, windows, entrance, sidewalk, and exterior green space provide scene context.
- No baked UI text, logo text, people, or fixed furniture in the main buildable area.
- Right and bottom edges are calm enough for future UI panels.

## Integration Notes

- Use as a background layer, not as an interactive tile atlas.
- Keep interactive collision/buildability from data and grid logic, not from image pixels.
- Overlay existing tile, zone, facility, employee, status, and FX resources on top.
- The PNG is RGBA but intentionally opaque; transparent corners are not expected for this asset.
