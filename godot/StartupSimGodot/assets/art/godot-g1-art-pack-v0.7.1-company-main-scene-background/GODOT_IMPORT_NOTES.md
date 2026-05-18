# Godot Import Notes - v0.7.1 Company Main Scene Background

## Recommended Import

- Import as `Texture2D`.
- Use in a `Sprite2D` or `TextureRect` below the office grid and all gameplay sprites.
- Native export size is `1920 x 1080`.
- Treat the image as an opaque background even though it is encoded as RGBA.

## Scene Placement

- Anchor or center the background behind the buildable office plane.
- Let Godot's grid and data layer decide buildable cells.
- Keep this background visually static for G1/G3; later packs can add animated window-light, weather, or time-of-day overlays.

## Avoid

- Do not slice this as an object atlas.
- Do not use wall pixels as gameplay collision authority.
- Do not bake UI labels or gameplay numbers into derived background variants.
