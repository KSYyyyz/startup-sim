# Godot Import Notes - v1.1 Pseudo 3D Office Foundation

## Files

- Atlas: `exports/pseudo3d-office-foundation-atlas-v1.1.png`
- Props: `exports/props/*.png`
- Preview: `previews/pseudo3d-office-foundation-atlas-v1.1-transparent-contact-sheet.png`

## Recommended Godot Usage

Use this pack as layered 2D art, not as gameplay data.

Suggested short-term layering:

```text
OfficeBackdrop
OfficeGridView
  floor detail overlays
  zone overlays
  shadow overlays
  shell / boundary props
  facility sprites
  employee sprites
  build markers
  feedback FX
G2OperationsPanel
```

## Atlas Settings

- Resource type: `Texture2D`
- Atlas grid: 8 columns x 4 rows
- Region size: 222 x 222 px
- Import alpha: enabled
- Filter: nearest or nearest-with-mipmaps depending on final scaling tests

## Notes for Current Prototype

- The current `OfficeGridView` can consume this atlas without changing the logical 12 x 8 grid.
- Floor, carpet, shadow, hover, selected, valid, and invalid cells can be drawn as `DrawTextureRectRegion` overlays.
- Props can be drawn from the atlas or instanced from individual PNGs.
- Office shell pieces should not define collisions; buildability remains in grid/data logic.

## Text Policy

Do not use any image from this pack for localized text. All Chinese labels, metrics, months, and report text should be rendered by Godot UI nodes.
