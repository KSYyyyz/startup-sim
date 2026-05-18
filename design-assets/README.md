# Startup Sim Design Asset Library

Status: active asset source of truth
Owner: Codex
Updated: 2026-05-18

## Purpose

This directory is the reusable design asset library for the Godot version of Startup Sim. All generated visual assets must be planned here first, registered in `manifest.json`, and exported into the Godot project only after they are ready for use.

The rule is simple:

> Generated visual assets use image-2 as the generation model. Godot references registered asset exports, not loose one-off files.

## Asset Types

- `image-2/prompts/`: final prompts used for generated bitmap assets.
- `image-2/exports/`: reusable generated image exports, grouped by asset type.
- `image-2/references/`: approved reference images used to guide future generation.
- `model-specs/`: written specs for future character, office, object, and scene model assets.
- `ui-specs/`: written specs for UI textures, panels, badges, action-card art, and icon-like generated assets.

## Godot Usage

Godot-ready copies live under:

```text
godot/StartupSimGodot/assets/
```

Every referenced Godot asset must have a matching entry in:

```text
design-assets/manifest.json
```

Do not add generated images directly to the Godot project without a manifest entry and prompt record.

Every image-2 asset that is exported for Godot use must also declare where it is used:

- `used_by` is required for each active image-2 asset.
- Every `used_by` path must point to an existing Godot scene, script, or resource file.
- If a Godot reference moves, update `used_by` in the same change that moves the reference.

## Generation Policy

- Required model: `image-2`.
- Keep final prompts in English unless Chinese text is part of the image itself.
- Avoid baked-in UI text where possible; render important labels in Godot UI so localization and layout remain controllable.
- Save reusable assets with stable semantic names, for example `office-command-center-v0.2.jpg`.
- Never overwrite an existing asset in place. Create a new versioned file and update the manifest.

## Acceptance Checklist

Before a new visual asset is used by Godot:

- The prompt is saved under `image-2/prompts/`.
- The exported asset is saved under `image-2/exports/`.
- A Godot copy exists under `godot/StartupSimGodot/assets/`.
- `manifest.json` records the asset id, type, model, prompt path, library path, Godot path, and usage.
- `used_by` lists every Godot file that references the asset or owns its import/display contract.
- The Godot C# project still builds.
