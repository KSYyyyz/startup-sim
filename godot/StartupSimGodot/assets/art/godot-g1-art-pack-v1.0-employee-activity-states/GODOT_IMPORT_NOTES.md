# Godot Import Notes - v1.0 Employee Activity States

## Recommended Import

- Import as `Texture2D`.
- Use `192 x 192` atlas regions.
- Use `exports/icons/` for direct PNG references when region slicing is inconvenient.

## Suggested Mapping

- Row = employee visual archetype.
- Column = `EmployeeState.current_activity` visual.
- Example: `ops_engineer_variant/sick_leave` can show an operations employee in a sick state.

## Boundaries

- These sprites do not decide employee needs, fatigue, mood, health, or output.
- They should only render settled state from Godot/C# data.
- Use Godot text rendering for localized details.
