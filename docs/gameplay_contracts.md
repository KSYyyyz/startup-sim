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
| `StoryEvent` | Backend/rules Agent | Short replayable events derived from rule events, competitors, and insight facts. |
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
- `replay_basis`
- `next_pressure`
- `authority`

`changes` should contain metric facts, short labels, and values that already came from settled state. `replay_basis` should cite backend reasons or deterministic replay facts. `next_pressure` should come from post-settlement rule outputs, such as the settled conflict summary. Frontend narrative can summarize these facts, but cannot add new outcomes.

### RoleMemory

`RoleMemory` describes what a character remembers from settled facts.

Required fields:

- `role_id`
- `role_name`
- `month`
- `fact`
- `implication`
- `source`

The `source` field must be `settled-turn-facts`. Role memory cannot be generated from UI hover state, unsent commands, or speculative previews. Persisted history lives in SQLite `role_memory_history`; the turn response exposes the current turn as `role_memory` and recent persisted rows as `memory_history` / `recent_role_memory`.

### OfficeSignal

`OfficeSignal` describes a room-level signal that can be rendered by Web, Tauri, or Unity.

Required fields:

- `id`
- `room_id`
- `title`
- `description`
- `severity`
- `source`
- `visual_intent`

`visual_intent` is currently `surface-in-office`. React may render it as a badge or bubble; Unity may render it as room animation, character speech, or icon. Neither renderer should infer business rules from raw text.

### StoryEvent

`StoryEvent` describes one compact event for monthly reports and future post-game replay.

Required fields:

- `id`
- `title`
- `description`
- `tone`
- `source`

The `source` field must be one of `rule-event`, `competitor-fact`, or `business-insight`. Story events are narrative surfaces over settled facts. They cannot change metrics, advance turns, or introduce outcomes that are not already present in `TurnResult`.

## Backend Migration Notes

Current backend coverage:

- `ActionPlan` already exists as `src.core.models.ActionPlan`. The HTTP command preview exposes a read-only action explanation, while TurnEngine remains the only numeric settlement authority.
- `TurnFacts` first slice is exposed through `POST /api/sessions/{session_id}/turns` as `turn.turn_facts`. It is serialized from `src.core.models.TurnResult`, especially `month`, `action_plan.raw_input`, `delta`, `delta.reasons`, post-turn `CompanyState`, and `conflict_summary.next_focus`.
- `RoleMemory` is persisted in `role_memory_history` after each settled turn. The same turn response exposes `turn.role_memory` for current memories and `turn.memory_history` / `turn.recent_role_memory` for recent persisted memories; it must not derive from hover state, unsent commands, or command previews.
- `OfficeSignal` first slice is exposed through the same turn response as `turn.office_signals`. It is serialized from settled state, `conflict_summary`, and `insight`, with short fact text plus renderer-neutral room and visual intent fields.
- `StoryEvent` first slice is exposed through the same turn response as `turn.story_events`. It is serialized from settled rule events, competitor moves, or business insight fallback, then rendered by the frontend as a compact monthly event list.
- A read-only `GET /api/sessions/{session_id}/review` endpoint wraps existing `ReviewEngine` and `AchievementEngine` outputs without mutating state or changing TurnEngine settlement.

Migration sequence:

1. Keep the `TurnResult` to `TurnFacts` serializer thin; it must not change TurnEngine settlement behavior.
2. Broaden `TurnFacts` only with fields that can be proven from settled state, `delta.reasons`, events, or deterministic replay facts.
3. Keep `RoleMemory` persistence append-only and derived from settled turn facts; do not backfill from frontend text.
4. Broaden `OfficeSignal` only with fields derived from settled state, conflict, and insight facts; keep it renderer-neutral and limited to facts plus short display text.
5. Use `StoryEvent` for replay and monthly reporting only; it must remain downstream from settled events, competitor facts, and insight facts.
6. Extend `docs/frontend_api_contract.md` only when additional fields are actually exposed through HTTP.

## Version

The current compatible contract family is `alpha-0.4-contracts.x`.

Breaking contract changes must:

1. Update `frontend/src/game/contracts.ts`.
2. Update this document.
3. Update frontend and backend tests before implementation.
4. Keep TurnEngine as the numeric authority.
