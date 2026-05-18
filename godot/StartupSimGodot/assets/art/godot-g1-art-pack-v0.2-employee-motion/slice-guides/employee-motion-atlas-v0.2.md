# employee-motion-atlas-v0.2 Slice Guide

Export: `exports/employee-motion-atlas-v0.2.png`
Source: `sources/employee-motion-atlas-v0.2-source.png`
Raw generated source: `sources/employee-motion-atlas-v0.2-raw-generated.png`

## Grid

- Columns: 12
- Rows: 6
- Cell size: 192 x 192 px
- Export size: 2304 x 1152 px
- Godot region hint: use `AtlasTexture` or region-enabled `Sprite2D` with 192 px cell width and 192 px cell height.

## Rows

| Row | Role / visual identity |
| --- | --- |
| 0 | Young developer, blue hoodie, youthful face |
| 1 | Senior architect, grey hair, glasses, brown jacket |
| 2 | Energetic sales lead, red suit, ponytail |
| 3 | Operations coordinator, grey blazer, tied hair |
| 4 | Server engineer, dark tech outfit, glasses |
| 5 | HR / recruiter, cream cardigan, long dark hair |

## Columns

| Column | State / frame |
| --- | --- |
| 0 | front_walk_a |
| 1 | front_walk_b |
| 2 | back_walk_a |
| 3 | back_walk_b |
| 4 | left_walk_a |
| 5 | left_walk_b |
| 6 | right_walk_a |
| 7 | right_walk_b_placeholder |
| 8 | idle |
| 9 | work |
| 10 | tired |
| 11 | rest |

## Notes

- Column 7 duplicates column 6 because the generated pass missed one consistent second right-facing walk frame. Treat this as acceptable v0.2 placeholder timing, not final animation polish.
- The sheet is intended for first playable-prototype motion and status feedback, not final character animation.
- Text, names, stats, and UI labels must remain Godot-rendered text.
