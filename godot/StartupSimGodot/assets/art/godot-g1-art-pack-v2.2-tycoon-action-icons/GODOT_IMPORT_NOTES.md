# Godot Import Notes - tycoon-action-icon-atlas-v2.2

- Atlas: `exports/tycoon-action-icon-atlas-v2.2.png`
- Atlas grid: 8 columns x 3 rows, 224 x 224 px cells.
- 64px HUD icons: `exports/icons_64/`
- 48px compact icons: `exports/icons_48/`
- 224px source cell icons: `exports/icons_224/`
- Use `asset-index.json` as the source of truth for semantic ids, row/column regions, categories, button sizes, and state tags.
- Render all Chinese labels and values with Godot Label/RichTextLabel; icon PNGs contain no baked text.
- For the cash status label, use “现金流可支撑时间” as the single approved UI wording.
- The external `D:/美术资源/startup-sim` copy is backup only; Godot should import the in-project copy.
