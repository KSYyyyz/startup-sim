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

### RoleMemory

`RoleMemory` describes what a character remembers from settled facts.

Required fields:

- `roleId`
- `roleName`
- `fact`
- `implication`
- `source`

The `source` field must be `settled-turn-facts`. Role memory cannot be generated from UI hover state, unsent commands, or speculative previews.

### OfficeSignal

`OfficeSignal` describes a room-level signal that can be rendered by Web, Tauri, or Unity.

Required fields:

- `id`
- `roomId`
- `title`
- `description`
- `severity`
- `source`
- `visualIntent`

`visualIntent` is currently `surface-in-office`. React may render it as a badge or bubble; Unity may render it as room animation, character speech, or icon. Neither renderer should infer business rules from raw text.

## Backend Migration Notes

Current backend coverage:

- `ActionPlan` already exists as `src.core.models.ActionPlan`. The HTTP command preview exposes a read-only action explanation, while TurnEngine remains the only numeric settlement authority.
- `TurnFacts` is not a separate backend model yet. The current source of truth is `src.core.models.TurnResult`, especially `month`, `action_plan`, `delta.reasons`, `events`, `customer_response`, `competitor_moves`, and the post-turn `CompanyState`.
- `RoleMemory` is not persisted yet. It should be derived only from settled turn records, future `TurnFacts`, and saved role feedback; it must not derive from hover state, unsent commands, or command previews.
- `OfficeSignal` is not persisted yet. The current semantic inputs are settled state plus rule outputs such as `ConflictEngine.identify(...)` and post-turn business insight. Future API fields should expose short facts like title, description, severity, source, and visualIntent, leaving layout and animation to the frontend or Unity layer.

Migration sequence:

1. Add backend serializers that convert `TurnResult` into `TurnFacts` without changing TurnEngine settlement behavior.
2. Add focused tests that prove `TurnFacts` values come from settled state and `delta.reasons`, not frontend text.
3. Derive `RoleMemory` from saved `TurnFacts` history after the `TurnFacts` serializer is stable.
4. Derive `OfficeSignal` from settled state, conflict, and insight facts; keep it renderer-neutral and limited to facts plus short display text.
5. Extend `docs/frontend_api_contract.md` only when these fields are actually exposed through HTTP.

## Version

The current compatible contract family is `alpha-0.4-contracts.x`.

Breaking contract changes must:

1. Update `frontend/src/game/contracts.ts`.
2. Update this document.
3. Update frontend and backend tests before implementation.
4. Keep TurnEngine as the numeric authority.
