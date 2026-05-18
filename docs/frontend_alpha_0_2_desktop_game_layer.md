# Frontend Alpha 0.2 Desktop Game Layer Plan

Status: active execution plan
Date: 2026-05-18

## 1. Execution Principle

Alpha 0.2 is desktop-first.

The main product target is a playable desktop web game layer, not a mobile-first dashboard. Mobile should remain accessible enough for smoke tests, but detailed layout, control density, and interaction polish will be handled after the desktop loop is convincing.

Primary desktop viewports:

- 1366 x 768
- 1440 x 900
- 1920 x 1080

Secondary mobile scope:

- Page loads.
- A session can start.
- A simple turn can be submitted.
- No legacy wording such as "跑道" or "Runway" appears.

## 2. Alpha 0.2 Goal

Turn the current frontend from a status interface into the first playable office-management game layer.

The player should be able to:

- Observe the company through a central office scene.
- Click rooms to discover context-specific actions.
- Choose an action card that prepares a natural-language command.
- Submit the turn and see board, competitor, insight, and result feedback update.
- Understand the tradeoff without reading formulas.

## 3. Desktop Acceptance Criteria

The desktop version is acceptable when:

- The office scene is the main visual focus, not a decorative image.
- Room hotspots are clickable and visually clear.
- At least five room groups exist: product, team, sales, board, and servers.
- Each room has at least one action card.
- Selecting an action fills the existing turn command input.
- Submitting the prepared action advances one turn through the existing API.
- The right-side board, competitors, advice entry, and log remain visible and usable.
- The left-side company state and core tension remain readable.
- No panel text overlaps at the target desktop viewports.
- Suggestions remain collapsed by default.
- Player-facing cash coverage wording uses "现金流可支撑时间".

## 4. Current Alpha 0.2 Slice

Implemented first:

- `frontend/src/game/officeRooms.ts`
- `frontend/src/game/OfficeStage.tsx`
- PixiJS dependency for the office canvas layer.
- React room hotspots over the image-2 office asset.
- Action cards that prepare commands.
- Vitest and Playwright coverage for the room-to-command path.

This is intentionally a thin vertical slice. It proves the control loop before adding animations, employees, room upgrades, or richer AI characters.

## 4.1 Desktop Iteration Progress

Completed in the first ten desktop-first implementation rounds:

- Selected office room is explicit through visual state, "当前房间", and `aria-pressed`.
- Prepared actions can be cancelled without manually editing the command input.
- Action cards show compact tradeoff tags such as "产品 +" and "现金 -".
- Empty command state explains that the player can choose an office action or type a CEO instruction.
- The execute button is disabled until a command exists.
- Monthly result feedback is structured as "月度战报" with changes, reasons, and next-month pressure.
- Board rows show role stances such as "现金纪律" and "产品护城河".
- Board feedback rows can now turn role pressure into a prepared CEO command through a compact response button.
- Competitor rows and the competitor glance include readable trend labels such as "持平" and "上升".
- Competitor pressure can now be converted into an executable CEO command from the competitor panel.
- Board and competitor response commands show a bottom-dock explanation so the player knows which pressure generated the command.
- Generated pressure commands now show compact tradeoff tags such as "用户 +" and "现金 -" before execution.
- The office scene has a non-blocking "办公室提示" bubble for the current focus.
- Office dynamic feedback signals are clickable: board signals open the board panel, and competitor signals open the competitor panel.
- After submitting a turn, the office scene shows a compact "办公室月末变化" pulse strip for cash, product, users, and recurring revenue changes.
- Room and action definitions now have a UI-independent data layer in `frontend/src/game/gameplayContent.ts`, with `officeRooms.ts` only binding those definitions to React/lucide presentation.
- Board and competitor pressure response templates now live in the same gameplay data layer, so `App.tsx` no longer owns those command-selection rules.
- Bottom-dock quick actions now also come from gameplay data and prepare the same action preview used by room actions.
- Office pulse routing now uses gameplay data rules, so room pressure signals can evolve with future scenario/content packs.
- Room actions, quick actions, board responses, and competitor responses now share a single prepared-action preview path.
- Room operating states now resolve from gameplay data and render labels such as "运转中" and "产品改善" on the office scene.
- Office event bubbles now resolve from board, competitor, and operating insight facts, with clickable board and competitor bubbles opening the matching side panel.
- Monthly reports now resolve from gameplay data into a headline, highlight cards, review lines, next pressure, and one executable recovery action.
- `frontend/src/game/scenarios.ts` now defines the built-in AI SaaS seed scenario metadata, keeping scenario content separate from backend settlement rules.
- PixiJS canvas setup now lives behind `frontend/src/game/pixiOverlay.ts`, keeping `OfficeStage.tsx` focused on React interactions and preserving a lazy optional rendering boundary.
- Desktop office interaction now presents the selected room as an "办公室操作台", uses a stronger active-room highlight, and keeps office event bubbles compact to reduce scene clutter.
- Board feedback now renders NPC-style profiles with stable stances, trust trends, and pressure tags generated by the gameplay data layer.
- Competitor feedback now renders move types, reasons, and response commands from gameplay data instead of showing raw status text only.
- Turn results now include a compact "回合结算" timeline for command execution, month-end changes, and report review.
- Playwright now checks the main flow at 1366 x 768, 1440 x 900, and 1920 x 1080 desktop viewports, plus a basic mobile smoke path.

Known follow-up:

- PixiJS now loads through an isolated optional overlay boundary. Its async production chunk is still large, so the next performance pass should choose between a lighter canvas renderer, deeper Pixi tree-shaking, or a release-oriented chunk budget.
- The mobile path is intentionally smoke-level only. Desktop layout remains the primary acceptance target until the office-management loop feels complete.

## 5. Next Desktop Tasks

### M1 Interaction Polish

- Make the selected room state more obvious.
- Add hover/focus states that feel game-like rather than dashboard-like.
- Add a compact "prepared action" preview near the command input.
- Keep keyboard and screen-reader access for room buttons.

### M2 Monthly Result Layer

- Replace the current text-heavy result area with a clearer monthly report panel.
- Show "what changed", "why it changed", and "what pressure comes next".
- Keep detailed numeric explanations behind an optional detail area.

### M3 AI Character Surface

- Give board members stronger identities and consistent roles.
- Add a lightweight role memory display only when it affects feedback.
- Ensure AI narrative consumes facts from the API and does not invent state changes.

### M4 Office Simulation Feel

- Add non-blocking room activity indicators.
- Add speech bubbles for important board, customer, or competitor moments.
- Add subtle turn-result animations for cash, product, users, and MRR changes.

### M5 Asset Pipeline

- Continue using `design-assets/` as the reusable image-2 asset library.
- Register every generated visual asset in `design-assets/manifest.json`.
- Prefer reusable room, UI, and character assets over one-off page decorations.

### M6 Gameplay Data Layer

- Keep frontend gameplay definitions UI-independent where possible.
- Move room metadata, action commands, tradeoff tags, pressure response templates, and later scenario metadata into data modules before adding more UI complexity.
- Keep the deterministic API/TurnEngine as the only authority for state changes; data definitions may prepare player commands but must not settle numeric outcomes.
- Scenario modules may describe rooms, board roles, competitors, market tags, and future content-pack affordances, but should continue to point numeric authority to the backend TurnEngine.

## 6. Verification

Run before commit:

- `python -m ruff check .`
- `python -m black --check .`
- `python -m isort --check-only .`
- `pytest tests/ -q`
- `python scripts/check_docs_consistency.py`
- `cd frontend && npm test -- --run`
- `cd frontend && npm run build`
- `cd frontend && npm run test:e2e`

After push:

- Confirm GitHub CI passes.
- Confirm Vercel deployment succeeds.
- Smoke the production frontend at `https://startup-sim-khaki.vercel.app` for the desktop room-to-command path.
