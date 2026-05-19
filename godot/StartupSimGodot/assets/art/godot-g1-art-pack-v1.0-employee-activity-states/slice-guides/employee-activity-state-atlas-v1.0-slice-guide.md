# Slice Guide - employee-activity-state-atlas-v1.0

## Atlas

- Export: `exports/employee-activity-state-atlas-v1.0.png`
- Size: `1536 x 768`
- Grid: `8 columns x 4 rows`
- Cell: `192 x 192`
- Alpha: transparent RGBA
- Individual icons: `exports/icons/{row_label}-{column_label}.png`

## Godot Region Formula

```text
x = column * 192
y = row * 192
w = 192
h = 192
```

## Rows

| Row | Label |
| --- | --- |
| 0 | `product_engineer_variant` |
| 1 | `sales_specialist_variant` |
| 2 | `ops_engineer_variant` |
| 3 | `office_generalist_variant` |

## Columns

| Column | Label |
| --- | --- |
| 0 | `working_focus` |
| 1 | `rest_break` |
| 2 | `entertainment` |
| 3 | `restroom_need_away` |
| 4 | `sick_leave` |
| 5 | `training` |
| 6 | `emotional_pressure` |
| 7 | `idle_walk` |
