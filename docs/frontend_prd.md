# Startup Sim Frontend Alpha 0.1 PRD

Status: execution baseline
Owner: Codex
Date: 2026-05-18

## Product Goal

Frontend Alpha 0.1 turns the existing text-first Startup Sim into a playable web experience without changing the simulation rules. The backend remains the source of truth for business logic. The frontend translates the current state into clear choices, conflict, and feedback.

Core principle:

> Real business logic stays under the hood. The player-facing layer must stay simple, visual, readable, and replayable.

## Scope

Alpha 0.1 includes:

- A browser-based game shell with HUD, office scene, side panels, and action bar.
- HTTP API endpoints for creating a session, reading current game state, submitting an action, and viewing suggestions.
- A single-player local demo flow backed by the existing Python turn engine.
- Compressed advice entry by default, with full advice behind an explicit panel.
- Human-facing copy that uses "现金流可支撑时间" instead of legacy cash-coverage wording.

Alpha 0.1 does not include:

- PixiJS or animated office simulation.
- Account login, cloud saves, multiplayer, payments, or production deployment.
- New financial systems such as bank loans, PMF scoring, or IPO board selection.

## Design Asset Library

The project keeps reusable generated visual assets under `design-assets/`. The frontend should reference only registered exports from `frontend/public/assets/`, and every generated image, model concept, UI texture, scene background, portrait, or reusable visual must be recorded in `design-assets/manifest.json`.

Generation policy:

- Required image generation model: image-2.
- Save final prompts under `design-assets/image-2/prompts/`.
- Save reusable exports under `design-assets/image-2/exports/`.
- Avoid baking important UI text into generated images; render player-facing labels in React/CSS.
- Version generated assets instead of overwriting them in place.

## Experience Principles

| Principle | Requirement |
| --- | --- |
| Game first | The first screen is the playable command center, not a landing page. |
| Complexity behind the scenes | Business mechanics appear as plain-language feedback and choices. |
| One-turn clarity | After each action, the player sees what changed, why it changed, and what pressure now matters. |
| Progressive detail | Advice, board details, competitor details, and logs live behind tabs or drawers. |
| Visual orientation | The office scene is the stage; panels explain the business state around it. |
| Reusable asset pipeline | Generated frontend visual assets are created with image-2, registered in `design-assets/manifest.json`, and exported through `frontend/public/assets/`. |

## Main Screen

The screen is organized into five areas:

- Top HUD: month, cash, cash change, cash coverage, MRR, users, product score, reputation, founder equity, valuation.
- Center stage: isometric office background with simple room labels and state badges.
- Left panel: this month, core tension, and operating insight.
- Right panel: board, competitors, advice, and log tabs.
- Bottom action bar: Build, Hire, Fundraise, Marketing, Sales, Control Cost, plus a command input.

## Required Player Flow

1. Player opens the web app and starts a local session.
2. The app shows current company state, core tension, board members, competitors, and an advice entry.
3. Player chooses an action from the bottom action bar or enters a natural-language command.
4. The frontend sends the action to the backend.
5. Backend processes one turn through the existing TurnEngine.
6. The UI refreshes with post-turn state, board feedback, competitor movement, insight, risk, and ending state if any.
7. If the game ends, a review/ending panel explains why and what the player can learn.

## Content Rules

- Never show legacy cash-coverage wording in the frontend.
- Use "现金流可支撑时间" for cash coverage.
- Advice is collapsed by default: "输入「建议」查看详情" in text channels, and an Advice tab/button in the web UI.
- Board feedback must not invent investors when there is no financing event or prior outside investment.
- Competitor information should be visible every turn, even if only as "no major move".
- If cash cannot cover fixed costs, the backend must end the game or return an ending state that the frontend can display.

## Acceptance Criteria

- The app starts locally with one backend command and one frontend command.
- The first browser screen is the playable command center.
- A new session can be created from the web UI.
- Submitting a turn updates HUD metrics, board feedback, competitor information, and operating insight.
- Suggestions are accessible but not dumped into the default layout.
- The UI uses "现金流可支撑时间" and does not show legacy cash-coverage wording.
- Desktop layout has no obvious overlap at 1440px width.
- Mobile layout degrades into a readable vertical flow at 390px width.
- API contract tests and frontend tests pass.
- A browser smoke test confirms the local page renders and a turn can be submitted.
