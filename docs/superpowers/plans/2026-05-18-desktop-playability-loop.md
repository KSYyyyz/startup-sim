# Desktop Playability Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move Alpha 0.2 from a stable office UI slice toward a more playable desktop-first startup management game loop.

**Architecture:** Keep backend TurnEngine as the only authority for state changes. Add focused frontend gameplay data helpers for board NPC roles, competitor events, scenario catalog presentation, and turn feedback rhythm. React components should render those data outputs without inventing numeric outcomes.

**Tech Stack:** React, TypeScript, Vite, Zustand, Vitest, Playwright, FastAPI wrapper, existing Python TurnEngine.

---

### Task 1: Desktop Office Visual Interaction

**Files:**
- Modify: `frontend/src/game/OfficeStage.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/App.test.tsx`
- Docs: `docs/frontend_alpha_0_2_desktop_game_layer.md`, `REPORTS.md`

- [ ] Write a failing frontend test that expects the selected room area to expose an office operation deck, a selected-room state label, and reduced event-bubble noise.
- [ ] Run `cd frontend && npm test -- --run src/App.test.tsx` and confirm the new assertion fails.
- [ ] Update `OfficeStage.tsx` markup so selected room details read as a game operation deck and event bubbles expose concise titles.
- [ ] Update CSS for stronger active room state, stable desktop operation deck dimensions, and compact event-bubble layout.
- [ ] Run `cd frontend && npm test -- --run`, `cd frontend && npm run build`, and `cd frontend && npm run test:e2e`.
- [ ] Update docs, run Python/document checks, commit as `Polish desktop office interaction`, and push.

### Task 2: Board NPC Role Surface

**Files:**
- Modify: `frontend/src/game/gameplayContent.ts`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/game/gameplayContent.test.ts`
- Test: `frontend/src/App.test.tsx`
- Docs: `docs/frontend_alpha_0_2_desktop_game_layer.md`, `REPORTS.md`

- [ ] Write a failing data-layer test for `buildBoardNpcProfiles()` that maps board members to stable role stance, trust trend, and pressure tags from current metrics.
- [ ] Run the focused Vitest test and confirm it fails because the helper is missing.
- [ ] Implement `buildBoardNpcProfiles()` without changing settlement rules or inventing new board members.
- [ ] Render role stance, trust trend, and pressure tags in the board side panel.
- [ ] Add an App test asserting the board panel shows role identity and trend text.
- [ ] Run frontend verification, Python/document checks, commit as `Add board NPC profile surface`, and push.

### Task 3: Competitor Dynamic System Surface

**Files:**
- Modify: `frontend/src/game/gameplayContent.ts`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/game/gameplayContent.test.ts`
- Test: `frontend/src/App.test.tsx`
- Docs: `docs/frontend_alpha_0_2_desktop_game_layer.md`, `REPORTS.md`

- [ ] Write a failing data-layer test for `buildCompetitorMoves()` that converts competitor status and trend into a visible move type such as 功能升级、渠道抢量、价格压力、客户绑定, or 暂无大动作.
- [ ] Confirm the focused test fails.
- [ ] Implement the helper as descriptive metadata only.
- [ ] Render move type, reason, and player-facing response command in the competitor panel.
- [ ] Add App coverage for at least one competitor move.
- [ ] Run verification, commit as `Add competitor move surface`, and push.

### Task 4: Turn Resolution Rhythm Feedback

**Files:**
- Modify: `frontend/src/game/gameplayContent.ts`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/game/gameplayContent.test.ts`
- Test: `frontend/src/App.test.tsx`
- Docs: `docs/frontend_alpha_0_2_desktop_game_layer.md`, `REPORTS.md`

- [ ] Write a failing test for `buildTurnResolutionSteps()` producing three steps: 执行指令, 月末变化, 战报复盘.
- [ ] Confirm the focused test fails.
- [ ] Implement the helper from `lastTurn`, metric highlights, and monthly report facts.
- [ ] Render a compact resolution timeline after submitting a turn.
- [ ] Add App test coverage that the timeline appears after a turn.
- [ ] Run verification, commit as `Add turn resolution timeline`, and push.

### Task 5: Scenario Selection Entry

**Files:**
- Modify: `frontend/src/game/scenarios.ts`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/game/scenarios.test.ts`
- Test: `frontend/src/App.test.tsx`
- Docs: `docs/frontend_alpha_0_2_desktop_game_layer.md`, `REPORTS.md`

- [ ] Write a failing scenario test that expects each built-in scenario to expose menu copy, difficulty, and feature tags.
- [ ] Confirm the focused test fails.
- [ ] Extend scenario metadata with menu presentation fields.
- [ ] Add a compact scenario entry panel using the current built-in scenario, without introducing alternate settlement rules yet.
- [ ] Add App coverage for the scenario entry panel.
- [ ] Run verification, commit as `Add scenario selection entry`, and push.

### Task 6: Production Acceptance Polish

**Files:**
- Modify: `frontend/e2e/startup-sim.spec.ts`
- Modify: `frontend/src/styles.css`
- Modify: `docs/vercel_frontend_deploy.md` or `docs/frontend_alpha_0_2_desktop_game_layer.md`
- Test: `frontend/e2e/startup-sim.spec.ts`
- Docs: `REPORTS.md`

- [ ] Add a failing Playwright assertion for production-facing desktop acceptance: no "跑道/Runway", office stage visible, scenario entry visible, and a room-to-command path works at 1366 x 768.
- [ ] Confirm e2e fails before the final polish if any acceptance signal is missing.
- [ ] Tighten CSS or text only where required by the acceptance test.
- [ ] Update docs with current production URL and acceptance checklist.
- [ ] Run full verification, commit as `Polish production desktop acceptance`, and push.
- [ ] Confirm GitHub CI passes and production URL returns HTTP 200.
