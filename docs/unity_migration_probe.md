# Unity Migration Probe

Status: C# core preparation active
Date: 2026-05-18

Startup Sim will prepare for Unity by moving deterministic gameplay contracts toward a pure C# core. The Web frontend remains useful as a rule validation bench, but it is no longer the intended final presentation layer.

## Goal

Validate whether Unity can consume the same gameplay contracts while `StartupSim.Core` becomes the long-term portable rules layer.

## Minimum Probe

The first Unity probe should include only:

1. One office scene.
2. Five room hotspots matching `ScenarioDefinition.rooms`.
3. One visible board role.
4. One competitor signal.
5. Clicking a room creates an `ActionPlan`.
6. No numeric settlement inside Unity.

The first C# preparation slice now lives in:

- `csharp/StartupSim.Core/`
- `csharp/golden-cases/`
- `unity/StartupSimUnity/Assets/Scripts/StartupSim/`
- `docs/csharp_unity_migration_plan.md`

## Required Inputs

- `ActionPlan`
- `OfficeSignal`
- `ScenarioDefinition`
- `AssetManifest`

## Explicit Non-Goals

- No TurnEngine rewrite in Unity.
- No full game UI rebuild.
- No 3D office requirement.
- No Steam packaging until the web loop is validated.

## Decision Gate

Unity presentation work can advance after the C# preparation path has:

- Stable `StartupSim.Core` contracts.
- Golden cases generated from the Python reference engine.
- One Unity office-room vertical slice that does not settle numeric rules.
- A tested bridge from Unity input to either the current API or the C# core.

If Unity can produce the room-to-action loop without duplicating rules, it becomes the primary presentation path. If Unity scripts start owning settlement logic, stop and move that logic into `StartupSim.Core`.
