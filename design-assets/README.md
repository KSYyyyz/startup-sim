# Startup Sim Design Asset Library

Status: active asset source of truth
Owner: Codex
Updated: 2026-05-18

## Purpose

This directory is the reusable design asset library for the web frontend. All generated frontend visual assets must be planned here first, registered in `manifest.json`, and exported into `frontend/public/assets/` only after they are ready for use.

The rule is simple:

> Generated frontend assets use image-2 as the generation model. The game references registered asset exports, not loose one-off files.

## Asset Types

- `image-2/prompts/`: final prompts used for generated bitmap assets.
- `image-2/exports/`: reusable generated image exports, grouped by asset type.
- `image-2/references/`: approved reference images used to guide future generation.
- `model-specs/`: written specs for future character, office, object, and scene model assets.
- `ui-specs/`: written specs for UI textures, panels, badges, action-card art, and icon-like generated assets.

## Frontend Usage

Frontend-ready copies live under:

```text
frontend/public/assets/
```

Every referenced frontend asset must have a matching entry in:

```text
design-assets/manifest.json
```

Do not add generated images directly to `frontend/public/` without a manifest entry and prompt record.

## Generation Policy

- Required model: `image-2`.
- Keep final prompts in English unless Chinese text is part of the image itself.
- Avoid baked-in UI text where possible; render important labels in React/CSS so localization and layout remain controllable.
- Save reusable assets with stable semantic names, for example `office-command-center-v0.2.jpg`.
- Never overwrite an existing asset in place. Create a new versioned file and update the manifest.
- If an asset is replaced, keep the older version until no frontend code references it.

## Acceptance Checklist

Before a new visual asset is used by the frontend:

- The prompt is saved under `image-2/prompts/`.
- The exported asset is saved under `image-2/exports/`.
- A frontend copy exists under `frontend/public/assets/`.
- `manifest.json` records the asset id, type, model, prompt path, library path, frontend path, and usage.
- The frontend still passes local tests, build, and Vercel smoke checks.
