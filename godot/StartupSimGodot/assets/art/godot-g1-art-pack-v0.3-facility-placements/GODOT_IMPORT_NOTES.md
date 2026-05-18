# Godot Import Notes - Facility Placements v0.3

Use `exports/facility-placement-atlas-v0.3.png` as a `Texture2D`.

## Slice

- Columns: 6
- Rows: 3
- Cell: 256 x 342 px

## Mapping

Rows are upgrade levels. Columns are facility families:

1. Desk workstation
2. Product whiteboard / planning wall
3. Server rack
4. Sales phone workstation / call booth
5. Meeting table
6. Coffee / rest corner

Keep costs, names, and gameplay text in Godot UI. Do not bake labels into the atlas.
