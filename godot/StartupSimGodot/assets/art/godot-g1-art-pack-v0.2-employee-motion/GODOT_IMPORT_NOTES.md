# Godot Import Notes - Startup Sim Employee Motion v0.2

Use `exports/employee-motion-atlas-v0.2.png` for the first Godot employee motion prototype.

## Import Flow

1. Import as `Texture2D`.
2. Slice as 12 columns x 6 rows.
3. Use 192 x 192 px cells.
4. Keep role names, employee names, stats, tooltips, and UI labels in Godot text.

## Recommended Mapping

- Rows map to visual employee archetypes, not business-rule identities.
- Columns 0-7 are walk/facing slots.
- Columns 8-11 are state slots: idle, work, tired, rest.
- Column 7 is a documented placeholder duplicate for the missing second right-walk frame.

## Storage Rule

Keep this active pack under `godot/StartupSimGodot/assets/art/`. The external `D:\美术资源` copy is only a backup, not the primary Godot path.
