# Startup Sim Godot G1 Art Pack v0.1

Storage policy: tracked Godot art pack. Keep active Godot gameplay assets under `godot/StartupSimGodot/assets/art/` with prompts, sources, exports, slice guides, and an asset index.

## Goal

Create the first Godot-facing art pack for the G1 playable vertical slice. This pack prioritizes operable office-management assets over presentation-only portraits.

## Asset Groups

1. `office-tile-atlas-v0.1`
   - Top-down / slight isometric office construction tiles.
   - Floors, walls, glass partitions, doors, windows, grid highlights, valid and invalid placement overlays.

2. `zone-state-overlay-atlas-v0.1`
   - Zone color overlays and status badges.
   - Research, sales, server, meeting, recruiting, market, rest.
   - Normal, risk, opportunity, blocked, improving.

3. `facility-upgrade-atlas-v0.1`
   - Six facility families with three visible upgrade tiers.
   - Office desk, product whiteboard, sales phone booth, server rack, meeting table, coffee/rest facility.

4. `employee-sprite-atlas-v0.1`
   - Six employee role sprites with five states.
   - Roles: developer, sales, operations, server engineer, HR/recruiter, manager.
   - States: idle, working, walking, tired, resting.

5. `employee-direction-variants-v0.1`
   - Six employee roles with four facing directions.
   - Directions: front, left, right, back.
   - Intended for movement-facing logic and future walk-cycle expansion.

6. `status-icon-atlas-v0.1`
   - HUD, employee need, trait, zone state, facility, and monthly report icons.
   - Text must be rendered by Godot, not baked into icons.

7. `recruitment-portrait-sheet-v0.1`
   - Twelve diverse candidate portraits for employee hiring UI.
   - Age, face shape, gender presentation, clothing, expression, and gaze direction must vary.

8. `recruitment-portrait-sheet-v0.2-angle-balanced`
   - Preferred recruitment portrait sheet.
   - Adds stricter front/left/right/profile/downward gaze balance to avoid repeated right-facing characters.

## Visual Direction

- Polished 2D management-game art with light pixel-art influence.
- Readable at small sizes.
- Top-down or slight isometric for world sprites.
- Portraits can be stylized upper-body busts, but must not repeat the same face.
- Important labels and numbers must not be baked into images.

## Godot Import Intent

- Atlas exports should be imported as `Texture2D`.
- Sprite sheets can be sliced into `AtlasTexture` resources or used through region-enabled `Sprite2D`.
- Transparent PNGs are preferred for sprites, icons, facilities, employees, overlays, and portraits.
- Source chroma-key PNGs are kept in `sources/`.

9. `ui-core-atlas-v0.1`
   - G1 HUD, panel, card, modal, toast, progress, and time-control UI frames.
   - Intended as raster UI frame pieces; all text remains in Godot.

10. `employee-animation-minimal-v0.1`
   - Six employee roles with two-frame loops for walk, work, tired, and rest.
   - Intended for the first AnimatedSprite2D prototype, not final animation polish.

11. `feedback-fx-atlas-v0.1`
   - One-shot gameplay feedback effects for upgrade, cash pressure, growth, incidents, blocks, training, recovery, achievement, and placement feedback.
