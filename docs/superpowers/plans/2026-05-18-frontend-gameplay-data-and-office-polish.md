# Frontend Gameplay Data And Office Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish six small Alpha 0.2 rounds that make the frontend office layer more data-driven, more game-like, and easier to extend toward scenario packs and desktop distribution.

**Architecture:** Keep deterministic state changes in the existing API/TurnEngine. Move player-facing action, pressure, room-status, office-event, scenario, and presentation metadata into focused frontend gameplay data modules. React components consume those definitions and render consistent controls, previews, and feedback.

**Tech Stack:** React, TypeScript, Vite, Vitest, Playwright, FastAPI wrapper, existing Python TurnEngine.

---

### Task 1: Unified Prepared Action

**Files:**
- Modify: `frontend/src/game/gameplayContent.ts`
- Modify: `frontend/src/App.tsx`
- Test: `frontend/src/game/gameplayContent.test.ts`
- Test: `frontend/src/App.test.tsx`
- Docs: `docs/frontend_alpha_0_2_desktop_game_layer.md`, `REPORTS.md`

- [ ] Add a `PreparedAction` data shape that can represent room actions, quick actions, board responses, and competitor responses.
- [ ] Replace split `preparedAction` and `pressureResponse` UI state with one prepared-action preview path.
- [ ] Verify all action sources still fill the command input and display title, description, command, and tradeoff tags.

### Task 2: Data-Driven Room Status

**Files:**
- Modify: `frontend/src/game/gameplayContent.ts`
- Modify: `frontend/src/game/OfficeStage.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/game/gameplayContent.test.ts`
- Test: `frontend/src/App.test.tsx`

- [ ] Add room status rules for `normal`, `warning`, `improving`, `blocked`, and `opportunity`.
- [ ] Render room status labels and classes from resolved data.
- [ ] Keep room hotspots readable and stable on desktop viewports.

### Task 3: Office Event Bubbles

**Files:**
- Modify: `frontend/src/game/gameplayContent.ts`
- Modify: `frontend/src/game/OfficeStage.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/game/gameplayContent.test.ts`
- Test: `frontend/src/App.test.tsx`

- [ ] Convert board, competitor, and insight facts into a small set of visible office event bubbles.
- [ ] Make event bubbles non-blocking and clickable when they map to an existing side panel.
- [ ] Preserve current board/competitor signal buttons.

### Task 4: Game-Like Monthly Report

**Files:**
- Modify: `frontend/src/game/gameplayContent.ts`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/game/gameplayContent.test.ts`
- Test: `frontend/src/App.test.tsx`

- [ ] Build monthly result cards for changes, reasons, next pressure, and recovery action.
- [ ] Keep detailed numbers readable but avoid formula-heavy presentation.
- [ ] Preserve existing `lastTurn.delta_reasons` behavior.

### Task 5: Scenario Metadata Seed

**Files:**
- Create: `frontend/src/game/scenarios.ts`
- Modify: `frontend/src/game/gameplayContent.ts`
- Test: `frontend/src/game/scenarios.test.ts`
- Docs: `docs/frontend_alpha_0_2_desktop_game_layer.md`, `docs/reference_game_analysis.md`, `REPORTS.md`

- [ ] Add an original `ai-saas-seed` scenario with starting company, rooms, competitors, board roles, market tags, and content-pack metadata.
- [ ] Keep the scenario metadata descriptive only; no numeric settlement bypass.
- [ ] Document it as the first step toward scenario/content packs.

### Task 6: PixiJS Lazy Load Boundary

**Files:**
- Create: `frontend/src/game/pixiOverlay.ts`
- Modify: `frontend/src/game/OfficeStage.tsx`
- Test: `frontend/src/game/OfficeStage.test.tsx` or existing frontend tests
- Docs: `docs/frontend_alpha_0_2_desktop_game_layer.md`, `REPORTS.md`

- [ ] Move Pixi overlay import and drawing code into a lazy-loaded module.
- [ ] Keep test mode free of Pixi initialization.
- [ ] Verify build still works; if chunk warning remains, document what remains and why.

### Verification Per Round

- [ ] Red-green the focused Vitest case.
- [ ] Run `npm test -- --run`.
- [ ] Run `npm run build`.
- [ ] Run `npm run test:e2e` for UI-affecting rounds.
- [ ] Run `pytest tests/ -q`.
- [ ] Run `python scripts/check_docs_consistency.py`.
- [ ] Run `python -m ruff check .`, `python -m black --check .`, `python -m isort --check-only .`.
- [ ] Commit and push after each round.
