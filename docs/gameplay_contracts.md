# Startup Sim Gameplay Contracts

Status: Godot contract baseline
Date: 2026-05-18

This document defines the shared contract layer between the Godot presentation layer and the backend/rules layer.

## Principle

The rules layer owns facts. Godot owns presentation. The contract layer describes data that can move between them.

## Contracts

| Contract | Owner | Purpose |
| --- | --- | --- |
| `ActionPlan` | Shared | A prepared player action before deterministic settlement. |
| `TurnFacts` | Rules | What actually happened after deterministic settlement. |
| `RoleMemory` | Rules | Role memory derived from historical facts. |
| `OfficeSignal` | Shared | Room-level signals that Godot can render as room animation, character speech, or icons. |
| `StoryEvent` | Rules | Short replayable events derived from rule events, competitors, and insight facts. |
| `PhaseGoal` | Rules | Current stage objectives, direction tags, and risk hints. |
| `ObjectiveUpdate` | Rules | Post-settlement progress against stage objectives. |
| `ScenarioDefinition` | Shared | Scenario rooms, roles, competitors, and market framing. |
| `AssetManifest` | Godot/art | image-2 visual assets and stable references. |

## Required Boundaries

- Godot may prepare actions, display previews, and submit commands.
- Godot must not settle cash, users, product score, valuation, equity, board state, competitor state, or endings.
- C# Core remains pure rules code and must not depend on Godot APIs.
- Python remains the complete reference implementation until C# Core parity gates are complete.
- New contract fields must be added to tests and docs before Godot UI depends on them.

## ActionPlan

`ActionPlan` describes a command before settlement.

Required fields:

- `id`
- `source`
- `sourceLabel`
- `title`
- `command`
- `readableIntent`
- `tradeoffs`
- `authority`

The `authority` field must be `backend-turn-engine` or `csharp-core`. A presentation ActionPlan can explain intent and tradeoffs, but it cannot settle numeric state.

## TurnFacts

`TurnFacts` describes what actually happened after settlement.

Required fields:

- `month`
- `command`
- `changes`
- `replay_basis`
- `next_pressure`
- `authority`

`changes` should contain metric facts, short labels, and values that already came from settled state. `replay_basis` should cite deterministic replay facts. `next_pressure` should come from post-settlement rule outputs.

## RoleMemory

`RoleMemory` describes what a character remembers from settled facts.

Required fields:

- `role_id`
- `role_name`
- `month`
- `fact`
- `implication`
- `source`

The `source` field must be `settled-turn-facts`. Role memory cannot be generated from hover state, unsent commands, or speculative previews.

## OfficeSignal

`OfficeSignal` describes a room-level signal that Godot can render.

Required fields:

- `id`
- `room_id`
- `title`
- `description`
- `severity`
- `source`
- `visual_intent`

`visual_intent` is currently `surface-in-office`. Godot may render it as room animation, character speech, or icon. Godot should not infer business rules from raw text.

## StoryEvent

`StoryEvent` describes one compact event for monthly reports and future post-game replay.

Required fields:

- `id`
- `title`
- `description`
- `tone`
- `source`

The `source` field must be one of `rule-event`, `competitor-fact`, or `business-insight`. Story events cannot change metrics, advance turns, or introduce outcomes that are not already present in settled facts.

## PhaseGoal

`PhaseGoal` describes stage objectives and player-facing directions.

Required fields:

- `phase_label`
- `title`
- `summary`
- `objectives`

Each objective may include `id`, `title`, `status`, `progress_label`, `action_directions`, and `risk_hint`. It must not include one-click execution metadata. The goal system can guide player thinking, but the player must still compose or choose the CEO command.

## ObjectiveUpdate

`ObjectiveUpdate` describes how settled turn results affected stage objectives.

Required fields:

- `id`
- `title`
- `status`
- `summary`

It is derived only after settlement from turn result facts and post-turn state. It must not recommend or execute the next action.

## Version

The current compatible contract family is `godot-contracts.g1`.
