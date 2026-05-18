# Godot Import Notes - Startup Sim G1 Art Pack v0.1

This folder is tracked in the project repository so Godot import checks and future art updates can use the same atlas files, prompts, and slice guides.

## Recommended Import Flow

1. Choose an export from `exports/` and inspect its matching guide in `slice-guides/`.
2. In Godot, import as `Texture2D`.
3. For office tiles, create a TileSet atlas source and align to the grid in the guide.
4. For employees and facilities, use `Sprite2D` region or `AtlasTexture` resources first; later convert repeated state frames into `AnimatedSprite2D` if the animation pipeline needs it.
5. For UI icons and recruitment portraits, keep labels in Godot UI text, not baked into the image.

## Preferred Assets

- Use `recruitment-portrait-sheet-v0.2-angle-balanced.png` over v0.1 for hiring UI because face angles are less repetitive.
- Use `employee-direction-variants-v0.1.png` when implementing movement-facing states.
- Use `employee-sprite-atlas-v0.1.png` when implementing work/rest/tired state feedback.

## Storage Rule

Keep generated digital assets for the active Godot game under `godot/StartupSimGodot/assets/art/`. New art packs should include `asset-index.json`, prompts, source images, export images, and slice guides before being committed.


## G1 Additions

- `ui-core-atlas-v0.1.png`: use for HUD, metric cards, employee/recruitment panels, build menu, monthly report modal, progress bars, and time controls. Keep readable text in Godot controls.
- `employee-animation-minimal-v0.1.png`: rows are roles; columns are paired walk/work/tired/rest frames. Start with simple two-frame `AnimatedSprite2D` loops.
- `feedback-fx-atlas-v0.1.png`: use cells as one-shot Sprite2D/VFX overlays for upgrade, warning, growth, incident, recovery, and achievement feedback.
