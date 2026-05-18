# Frontend Alpha 0.3 AI Command Layer Plan

Status: active execution plan
Date: 2026-05-18

## 1. Goal

Alpha 0.3 makes AI-style command interpretation part of the gameplay loop without letting AI own the game state.

The player should be able to type a free-form CEO instruction, ask the system to explain how it will be interpreted, then decide whether to execute it. The preview can be AI-like in presentation, but all numeric state changes remain controlled by the existing backend parser, StateGuard, and TurnEngine.

## 2. First Slice

Implemented first:

- `POST /api/sessions/{session_id}/command-preview`
- Frontend API client and Zustand store support for command preview.
- A compact `AI 指令解释` panel beside the bottom command input.
- Demo fallback support for Vercel when no live backend is configured.

The preview is intentionally read-only. It does not advance the month, mutate session state, or bypass validation.

## 3. Player Experience

When a player enters a command such as:

```text
花10万研发产品，花5万做营销
```

The UI explains:

- Which executable actions were detected.
- The action category, budget, risk label, and tradeoffs.
- That final settlement still happens through `TurnEngine`.

If no executable action is detected, the preview asks the player to clarify the instruction with a concrete direction and budget.

## 4. Acceptance Criteria

- Free-form command preview works before execution.
- Previewed actions use player-facing labels such as `产品研发` and `市场营销`.
- Preview text uses `现金流可支撑时间`, never `跑道` or `Runway`.
- Preview does not advance the turn or mutate saved state.
- Executing a command still uses the existing turn submission endpoint and backend rules.
- Vercel demo fallback can still show a useful preview without a live backend.

## 5. Next Alpha 0.3 Tasks

- Add lightweight role memory facts for CFO/CTO/COO based on previous player behavior.
- Feed command preview and turn history into board/competitor narrative surfaces.
- Add a monthly narrative layer that cites executed actions and result facts without inventing state changes.
- Keep LLM integration optional; deterministic fallback remains required for offline and Vercel demo play.

## 6. Verification

Run before commit:

- `pytest tests/ -q`
- `python scripts/check_docs_consistency.py`
- `cd frontend && npm test -- --run`
- `cd frontend && npm run build`
- `cd frontend && npm run test:e2e`
