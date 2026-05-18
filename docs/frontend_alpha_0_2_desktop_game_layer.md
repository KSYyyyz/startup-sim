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
