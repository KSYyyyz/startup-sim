# Slice Guide - business-feedback-fx-atlas-v0.8

## Atlas

- Export: `exports/business-feedback-fx-atlas-v0.8.png`
- Size: `1792 x 896`
- Grid: `8 columns x 4 rows`
- Cell: `224 x 224`
- Alpha: transparent RGBA
- Individual icons: `exports/icons/{column_label}-{row_label}-v0.8.png`

## Columns

| Column | Label | Intended Signal |
| --- | --- | --- |
| 0 | `product_progress` | Product capacity, quality, feature progress |
| 1 | `sales_lead` | Leads, customer growth, sales conversion |
| 2 | `cash_pressure` | Cash burn, budget stress, runway pressure |
| 3 | `customer_feedback` | Customer sentiment or customer response |
| 4 | `morale_shift` | Morale and team mood changes |
| 5 | `server_stability` | Stability, delivery capacity, incident pressure |
| 6 | `upgrade_complete` | Facility upgrade or improvement result |
| 7 | `training_growth` | Training, growth, learning progress |

## Rows

| Row | Label | Suggested Use |
| --- | --- | --- |
| 0 | `small_pop` | Quick one-shot marker |
| 1 | `rising_float` | Marker that floats upward |
| 2 | `pulse_ring` | Repeating attention pulse |
| 3 | `burst_trail` | Completion or consequence burst |

## Godot Region Formula

```text
x = column * 224
y = row * 224
w = 224
h = 224
```

Use the labels in `asset-index.json` for stable mapping instead of relying only on visible icon shape.

## Individual Transparent Icons

The atlas has been sliced into 32 standalone transparent PNG files in `exports/icons/`.
Each sliced icon keeps the full `224 x 224` cell canvas so Godot placement pivots remain consistent.
