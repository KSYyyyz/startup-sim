# Art Asset Metadata Standard

Status: required for new Godot art packs
Date: 2026-05-19
Scope: `godot/StartupSimGodot/assets/art/godot-g1-art-pack-v1.1+`

This standard exists so the Godot integration agent can consume art packs without guessing what an atlas cell means.
Every new formal art pack must include machine-readable metadata, human-readable slice guidance, and descriptive filenames.

## Required Pack Files

Each pack must include:

- `asset-index.json`
- `ART_PACK_SPEC.md`
- `GODOT_IMPORT_NOTES.md`
- `prompts/`
- `sources/`
- `exports/`
- `slice-guides/`
- `previews/`

Transparent, interactive, or sprite-like assets must also include individual PNG exports, usually under `exports/props/`, `exports/icons/`, or `exports/sprites/`.

## Required Texture Metadata

For every atlas cell or individual texture, `asset-index.json` must include a `textures` entry with:

| Field | Purpose |
| --- | --- |
| `id` | Stable texture identifier used by integration code. |
| `semantic_name` | English machine-readable meaning. |
| `zh_name` | Chinese human-readable meaning. |
| `category` | Semantic group such as `office_shell`, `zone_overlay`, `facility`, `employee`, `hud_icon`. |
| `file` | Individual transparent PNG path. |
| `atlas` | Atlas PNG path when the texture comes from an atlas. |
| `atlas_region` | Pixel region `{ x, y, w, h }` inside the atlas. |
| `grid_position` | Zero-based atlas `{ row, column }`. |
| `intended_layer` | Recommended Godot render layer. |
| `anchor` | Placement/sorting anchor such as `center`, `bottom_center`, `feet_center`. |
| `footprint_cells` | Logical gameplay occupancy in grid cells. |
| `visual_size_cells` | Approximate rendered footprint; can be larger than logic occupancy. |
| `usage` | Short integration purpose. |
| `state_tags` | Filterable tags for behavior, state, or tooling. |
| `godot_hint` | Rendering, sorting, or text-policy hints. |

## Naming Rules

Individual files must be self-describing. Do not use names like `icon_01.png`.

Recommended patterns:

```text
office_shell-wall_corner_inner_ne.png
zone_overlay-product_carpet_center.png
build_marker-placement_valid.png
facility-desk_group_2x1-active.png
employee-product_engineer-walk_down-01.png
hud-kpi_cash.png
```

## 2.5D Fields

2.5D office assets must explicitly declare:

- `anchor`: usually `bottom_center` for walls, props, facilities, and employees.
- `footprint_cells`: what the gameplay grid reserves.
- `visual_size_cells`: how large the sprite appears visually.
- `intended_layer`: where it should draw relative to floors, zones, facilities, employees, feedback FX, and HUD.

This prevents large sprites from breaking placement, click targets, and y-sorting.

## Human-Readable Slice Guides

Each slice guide must include a table with:

```text
row / col / region / id / 中文说明 / 推荐层级 / 锚点 / 逻辑占格 / 视觉尺寸 / 用途
```

The slice guide should not be the only source of truth. It mirrors the machine-readable `textures` entries.

## Text Policy

Art assets must not bake in localized labels, numbers, months, company metrics, or user-facing report text. Godot renders those with `Label`, `RichTextLabel`, or other UI nodes.

## Validation Expectations

New art packs should be validated for:

- export PNG files exist
- RGBA mode
- transparent corners for transparent assets
- atlas size matches index
- individual PNG count matches index
- individual PNG dimensions match cell size
- `textures` count matches expected atlas cells
- required metadata fields are present
- backup hash matches `D:\美术资源\startup-sim\...`
