# Godot Import Notes - v0.8 Business Feedback FX

## Recommended Import

- Import as `Texture2D`.
- Use `224 x 224` regions.
- Suggested usage: `Sprite2D`, `AnimatedSprite2D`, or a lightweight pooled feedback node above office cells, facilities, employees, and zone overlays.
- Keep filtering consistent with the current office camera scale. Avoid blurry mipmaps if the FX is shown at small size.

## Suggested Mapping

- Columns map to business signal family.
- Rows map to presentation role.
- For example, a product gain can use `product_progress/small_pop`; a server warning can use `server_stability/pulse_ring`.

## Boundaries

- These FX do not decide business results.
- They should only render signals already produced by C# Core, Godot data, or settled office state.
- Use Godot text rendering for any localized messages or numeric values.
