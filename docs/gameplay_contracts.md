# Startup Sim Gameplay Contracts

Status: Alpha 0.4 contract baseline
Date: 2026-05-18

This document defines the shared contract layer between the frontend/art agent, backend/rules agent, and future desktop or Unity prototype.

## Principle

The backend rules layer owns facts. The frontend owns presentation. The contract layer describes the data that can move between them.

## Contracts

| Contract | Owner | Purpose |
| --- | --- | --- |
| `ActionPlan` | Shared | A prepared player action before deterministic settlement. |
| `TurnFacts` | Backend/rules Agent | What actually happened after TurnEngine settlement. |
| `RoleMemory` | Backend/rules Agent | Role memory derived from historical facts. |
| `OfficeSignal` | Shared | Room-level signals that Web, Tauri, or Unity can render differently. |
| `ScenarioDefinition` | Shared | Scenario rooms, roles, competitors, and market framing. |
| `AssetManifest` | Frontend/art Agent | image-2 visual assets and stable references. |

### ActionPlan

`ActionPlan` describes a command before settlement. It can come from a room, quick action, board response, competitor response, or monthly recovery.

Required fields:

- `id`
- `source`
- `sourceLabel`
- `title`
- `command`
- `readableIntent`
- `tradeoffs`
- `authority`

The `authority` field must be `backend-turn-engine`. A frontend ActionPlan can explain intent and tradeoffs, but it cannot settle numeric state.

### TurnFacts

`TurnFacts` describes what actually happened after settlement.

Required fields:

- `month`
- `command`
- `changes`
- `replayBasis`
- `nextPressure`
- `authority`

`changes` should contain player-facing labels and values that already came from settled state. `replayBasis` should cite backend reasons or deterministic replay facts. Frontend narrative can summarize these facts, but cannot add new outcomes.

## Version

The current compatible contract family is `alpha-0.4-contracts.x`.

Breaking contract changes must:

1. Update `frontend/src/game/contracts.ts`.
2. Update this document.
3. Update frontend and backend tests before implementation.
4. Keep TurnEngine as the numeric authority.
