# Unity Migration Probe

Status: planning baseline
Date: 2026-05-18

Startup Sim should not switch to Unity before the web prototype proves the core loop. However, the project should keep a clear path for a future Unity or desktop build.

## Goal

Validate whether Unity can consume the same gameplay contracts without rewriting the simulation.

## Minimum Probe

The first Unity probe should include only:

1. One office scene.
2. Five room hotspots matching `ScenarioDefinition.rooms`.
3. One visible board role.
4. One competitor signal.
5. Clicking a room creates an `ActionPlan`.
6. No numeric settlement inside Unity.

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

Run this probe after Alpha 0.4 has:

- Stable ActionPlan and TurnFacts contracts.
- A playable 3-5 turn desktop web loop.
- Reusable image-2 asset naming and manifest discipline.
- One documented Vercel playtest pass.

If the probe can read the same contracts and produce a room-to-action loop, Unity remains viable. If it requires duplicating rules, keep Unity as a later presentation rewrite rather than a near-term platform switch.
