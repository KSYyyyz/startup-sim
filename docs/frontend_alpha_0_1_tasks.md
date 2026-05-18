# Frontend Alpha 0.1 Task Plan

Status: active execution plan
Date: 2026-05-18

## M1 Repo Baseline

- Keep existing Python turn engine as the rules source.
- Add the frontend PRD and API contract to `docs/`.
- Add Node and frontend build artifacts to `.gitignore`.

Verification:

- `python scripts/check_docs_consistency.py`
- `pytest tests/test_docs_and_demo.py`

## M2 Backend API

- Add a small local API module under `src/api/`.
- Expose `/api/health`, `/api/sessions`, `/api/sessions/{id}`, `/api/sessions/{id}/turns`, and `/api/sessions/{id}/suggestions`.
- Map existing `CompanyState`, board feedback, competitor moves, conflict, and insight into `GameStateView`.
- Ensure API output uses "现金流可支撑时间" and never legacy cash-coverage wording.

Verification:

- Add failing tests in `tests/test_frontend_api.py`.
- Run `pytest tests/test_frontend_api.py`.

## M3 Frontend App

- Create `frontend/` with React, Vite, TypeScript, Tailwind, Zustand, and Vitest.
- Build the game command center as the first screen.
- Use a static office stage background and React overlays for Alpha 0.1.
- Add HUD, left panel, right tabs, action bar, command input, loading, error, and ending states.
- Keep advice collapsed by default.

Verification:

- `npm test -- --run`
- `npm run build`

## M4 Local Integration

- Document local startup commands.
- Configure the frontend API base URL through environment variables.
- Verify a local browser can create a session and submit a turn.

Verification:

- Backend health endpoint returns OK.
- Frontend renders at localhost.
- Playwright/browser smoke test passes for start session and submit turn.

## M5 Final Acceptance

- Run all Python tests.
- Run all frontend tests and build.
- Run docs consistency checks.
- Capture desktop and mobile screenshots.
- Review UI text for legacy cash-coverage wording.

Verification:

- `pytest tests/`
- `python scripts/check_docs_consistency.py`
- `npm test -- --run`
- `npm run build`
- Browser screenshots at desktop and mobile widths.
