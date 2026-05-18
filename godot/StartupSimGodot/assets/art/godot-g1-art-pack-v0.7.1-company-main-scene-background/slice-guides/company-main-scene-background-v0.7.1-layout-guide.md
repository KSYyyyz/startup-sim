# Layout Guide - company-main-scene-background-v0.7.1

This is a full-scene background, not a sliced atlas.

## Canvas

- Export size: `1920 x 1080`
- Aspect ratio: `16:9`
- Alpha policy: opaque RGBA

## Suggested Layer Order

1. Company main scene background
2. Godot office grid
3. Zone color overlays
4. Facilities
5. Employees
6. Employee status icons and feedback FX
7. HUD and panels

## Buildable Area Guidance

- The central tiled floor is the intended visual buildable region.
- Low walls, windows, entrance, sidewalk, grass, and exterior props are scene framing.
- Do not infer authoritative gameplay boundaries from the image. Use office map data and grid logic.

## UI Safe Areas

- Right edge and bottom edge are intentionally calmer than the center.
- Future HUD or operations panels can overlap these areas if needed.
