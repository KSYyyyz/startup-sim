# Slice Guide - facility-state-variant-atlas-v0.9

## Atlas

- Export: `exports/facility-state-variant-atlas-v0.9.png`
- Size: `1792 x 672`
- Grid: `8 columns x 3 rows`
- Cell: `224 x 224`
- Alpha: transparent RGBA
- Individual icons: `exports/icons/{row_label}-{column_label}.png`

## Godot Region Formula

```text
x = column * 224
y = row * 224
w = 224
h = 224
```

## Rows

| Row | Label |
| --- | --- |
| 0 | `basic_desk` |
| 1 | `product_whiteboard` |
| 2 | `starter_server_rack` |

## Columns

| Column | Label |
| --- | --- |
| 0 | `idle` |
| 1 | `active` |
| 2 | `upgrading` |
| 3 | `blocked` |
| 4 | `inefficient` |
| 5 | `high_efficiency` |
| 6 | `placement_valid` |
| 7 | `placement_invalid` |
