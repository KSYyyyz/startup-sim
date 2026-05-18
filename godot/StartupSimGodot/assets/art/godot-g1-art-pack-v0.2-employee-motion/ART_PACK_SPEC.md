# Startup Sim Godot G1 Art Pack v0.2 - Employee Motion

Storage policy: tracked Godot art pack. Keep active Godot gameplay assets under `godot/StartupSimGodot/assets/art/` with prompts, sources, exports, previews, slice guides, and an asset index. The external `D:\美术资源\startup-sim\godot-g1-art-pack-v0.2-employee-motion` copy is a backup.

## Goal

Provide a Godot-ready employee motion atlas for the playable office-management prototype. This pack prioritizes usable top-down employee movement and status states over large portraits.

## Asset Groups

1. `employee-motion-atlas-v0.2`
   - Six distinct employee rows.
   - Twelve action columns per row.
   - Four facing directions with two walk slots each.
   - Additional idle, work, tired, and rest state cells.

## Visual Direction

- Polished 2D management-game art with light pixel-art influence.
- Readable at small Godot sprite sizes.
- Top-down / slight isometric office-worker silhouettes.
- Characters vary by age, face shape, hair, outfit, accessories, expression, and role.
- No baked UI text.

## Production Notes

- Generated through built-in image generation on a chroma-key source.
- Source was reorganized into an equal-spaced 12 x 6 atlas for reliable Godot slicing.
- Transparent export was produced by local chroma-key removal.
- Column `right_walk_b_placeholder` duplicates `right_walk_a` because the generated pass missed one side-walk frame. This is documented so the integration session can wire it deliberately or skip the duplicate.

## Godot Import Intent

- Import `exports/employee-motion-atlas-v0.2.png` as `Texture2D`.
- Use `AtlasTexture`, `Sprite2D.region_rect`, or `AnimatedSprite2D` frames.
- Cell size is 192 x 192 px.
- Suggested first animation loops:
  - `front_walk`: columns 0-1
  - `back_walk`: columns 2-3
  - `left_walk`: columns 4-5
  - `right_walk`: columns 6-7
  - `idle`: column 8
  - `work`: column 9
  - `tired`: column 10
  - `rest`: column 11
