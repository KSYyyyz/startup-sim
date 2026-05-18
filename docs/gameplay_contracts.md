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

## Version

The current compatible contract family is `alpha-0.4-contracts.x`.

Breaking contract changes must:

1. Update `frontend/src/game/contracts.ts`.
2. Update this document.
3. Update frontend and backend tests before implementation.
4. Keep TurnEngine as the numeric authority.
