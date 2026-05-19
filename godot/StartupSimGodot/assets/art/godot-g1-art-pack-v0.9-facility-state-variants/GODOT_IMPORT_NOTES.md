# Godot Import Notes - v0.9 Facility State Variants

## Recommended Import

- Import as `Texture2D`.
- Use `224 x 224` atlas regions.
- Use `exports/icons/` for direct PNG references when region slicing is inconvenient.

## Suggested Mapping

- Row = facility id.
- Column = visual state.
- Example: `starter_server_rack/high_efficiency` can render a server rack with a blue performance glow.

## Boundaries

- This pack does not define facility costs, legal placement, effects, or upgrade rules.
- Facility rules stay in Godot data and C# Core.
- Do not infer placement validity from the image alone.
