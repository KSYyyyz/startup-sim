# Godot G1 Art Pack v0.8 - Business Feedback FX

Status: production candidate
Date: 2026-05-19
Owner: Codex art-resource session

## Purpose

This pack adds small business feedback FX for the office simulation layer. It is meant to make resolved business signals visible in the office without baking numbers, Chinese text, or rule logic into images.

## Asset

| Asset | Export | Grid | Cell | Role |
| --- | --- | --- | --- | --- |
| business-feedback-fx-atlas-v0.8 | `exports/business-feedback-fx-atlas-v0.8.png` | 8 x 4 | 224 x 224 | Office-space feedback effects |

## Columns

1. Product progress
2. Sales lead
3. Cash pressure
4. Customer feedback
5. Morale shift
6. Server stability
7. Upgrade complete
8. Training growth

## Rows

1. Small pop marker
2. Rising float marker
3. Pulse ring marker
4. Burst/trail marker

## Design Notes

- Transparent RGBA PNG for layering above the office scene.
- Icon-like FX only; no text, numbers, or UI panels.
- Designed for short office-space feedback after a calculated business event or state change.
- Godot should provide localized labels, numeric deltas, and detailed explanations separately.
