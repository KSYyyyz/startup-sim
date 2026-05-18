# Reference Game Analysis

Status: reference baseline
Date: 2026-05-18
Scope: local read-only directory scan

## 1. Boundary

This document records what Startup Sim can learn from the locally installed reference games without copying proprietary content.

Allowed:

- Study folder organization, public-facing mod/localization structures, save/config/log conventions, and high-level interaction patterns.
- Use the findings to shape Startup Sim's own original systems, UI flow, documentation, asset pipeline, and desktop distribution roadmap.
- Reference the existence of files and systems when they are visible from normal installation folders.

Not allowed:

- Do not copy art, audio, text, code, databases, compiled assets, or game-specific names into Startup Sim.
- Do not decompile, unpack, bypass DRM, or reverse engineer closed implementation.
- Do not reproduce proprietary mechanics one-to-one. Translate observations into original design principles.

## 2. Local Reference Scan

### 2.1 Mad Games Tycoon 2

Local path: `D:\XDWork\Game\Mad.Games.Tycoon.2.Build.20855306`

Observed structure:

- Unity runtime layout: `Mad Games Tycoon 2_Data`, `MonoBleedingEdge`, `UnityPlayer.dll`.
- External asset folders under `Mad Games Tycoon 2_Data\Extern`, including company logos, feature icons, genre icons, platform icons, screenshots, and text.
- Large Unity asset bundles and scene/resource files under the data folder.

Usefulness for Startup Sim:

- Strong reference for an office/company-management game where the workspace itself becomes the primary gameplay surface.
- Reinforces the direction that rooms, facilities, employees, projects, and market feedback should be visible, clickable, and progressive.
- Useful as a product-shape reference for how a business simulation can grow from a small company to a larger operating machine.

Safe takeaway:

Startup Sim should build its own office layer where every room represents a business capability: product, sales, team, board, infrastructure, market, and later finance/compliance. The reference is the interaction pattern, not the assets or exact rules.

### 2.2 STONKS-9800

Local path: `D:\XDWork\Game\STONKS9800`

Observed structure:

- GameMaker-style package with `data.win`, executable, options/config files, backgrounds, music, palette, names, localization files, and mod folders.
- Public modding surface exists: `modding_guide.txt`, `mods\test_mod.meow`, `make your own localization`, and `mod_uploader`.
- Public data-like folders are clearly separated from compiled game content.

Usefulness for Startup Sim:

- Best local reference for mod/localization/data extensibility.
- Shows the value of a visible, player-friendly customization surface: mods, localization, names, palettes, and uploader tooling.
- Provides a useful pattern for keeping user-editable content outside the compiled core.

Safe takeaway:

Startup Sim should gradually separate original game data from the runtime code:

- `frontend/src/game` for runtime gameplay UI.
- `frontend/src/assets` for generated visual assets.
- `data/gameplay` or equivalent for original room, action, event, investor, competitor, and character definitions.
- `data/locales` for localization when the text surface stabilizes.
- Later: a documented mod or scenario format for custom startup sectors, investors, competitors, and events.

### 2.3 历史模拟器：崇祯

Local path: `D:\Steam\steamapps\common\历史模拟器：崇祯`

Observed structure:

- Electron/Chromium desktop distribution: executable, Chromium runtime files, locale packs, `resources.pak`, and `resources\app.asar`.
- Steamworks integration appears in `resources\app.asar.unpacked\node_modules\steamworks.js`.
- The install folder is a useful desktop-packaging reference, but the application source package should not be unpacked or inspected for implementation details.

Usefulness for Startup Sim:

- Strong reference for a web-tech game distributed as a desktop app.
- Supports the current plan: keep the web frontend playable first, then reserve Electron or Tauri packaging for desktop distribution.
- Reinforces that AI-native strategy games can ship with a conventional desktop shell while keeping game logic and UI in web technologies.

Safe takeaway:

Startup Sim should keep the current Vite/React frontend deployable to Vercel, but also preserve a future desktop packaging path:

- Browser demo remains the public playtest channel.
- Desktop-first UI density remains the design target.
- Later packaging can use Tauri or Electron without rewriting the game layer.
- Steam-specific integration should be deferred until the core office loop is compelling.

## 3. Product Implications

### 3.1 Office Layer Is The Main Game Board

The current Alpha 0.2 office layer should keep moving away from dashboard composition and toward a playable management space.

Required next direction:

- Rooms are not decorative zones. Each room is a system entry.
- Room state should communicate pressure: busy, blocked, improving, risky, or ready for a decision.
- Staff and room events should become visible feedback for business state changes.
- Monthly changes should be shown both in panels and in the office scene.

### 3.2 Data-Driven Content Should Start Early

STONKS-9800's public mod/localization structure is the most useful engineering lesson. Startup Sim should not hard-code every room, action, investor, competitor, event, and role forever.

Recommended direction:

- Move room/action definitions toward structured data.
- Keep deterministic rules in the core engine.
- Let the frontend read stable definitions for labels, descriptions, tradeoff tags, and room metadata.
- Prepare for original scenario packs without committing to public modding too early.

### 3.3 Desktop Distribution Should Remain Open

The reference games show three viable packaging shapes:

- Unity-heavy desktop game.
- GameMaker-style executable with visible data/mod folders.
- Electron desktop game using web technology.

Startup Sim should not switch to Unity now. The current project benefits from fast web iteration, existing Vercel deployment, and reusable Python simulation logic. The right path is:

1. Make the desktop web version feel like a game.
2. Keep frontend and backend boundaries clean.
3. Add a local save/export path.
4. Evaluate Tauri/Electron packaging after the office loop, AI command loop, and monthly result loop are strong.

## 4. Concrete Roadmap Adjustments

### 4.1 Near Term

- Keep Alpha 0.2 desktop-first.
- Improve the office scene as an interactive board, not a static illustration.
- Add visible room states and activity pulses.
- Make board, competitor, and office feedback feel like game events.
- Keep suggestions folded by default.
- Continue using "现金流可支撑时间" in player-facing text.

### 4.2 Next Game-Data Step

Introduce a small original data layer for frontend gameplay definitions:

- Rooms.
- Room actions.
- Action tradeoff tags.
- Board pressure response templates.
- Competitor pressure response templates.
- Office feedback signal types.

This should be data-driven, but still executed through the existing API/TurnEngine. The frontend can propose commands; the deterministic engine still owns state changes.

### 4.3 Later Desktop Game Step

Prepare for a distributable independent game without committing to a final wrapper:

- Keep save data serializable.
- Avoid browser-only assumptions where possible.
- Document required environment variables and offline fallback behavior.
- Keep generated image-2 assets inside the project design asset library.
- Defer Steamworks, achievements, cloud saves, and mod uploader until after a playable Alpha loop.

## 5. What Not To Do

- Do not copy the reference games' images, audio, text, logos, character names, or exact event scripts.
- Do not unpack or inspect closed app packages for implementation.
- Do not change the project into Unity before the web desktop loop is proven.
- Do not overbuild modding before the core game is fun.
- Do not let AI narrative bypass deterministic game rules.

## 6. Startup Sim Design Rule

Reference games confirm the current principle:

> Real business is the simulation foundation; game feel is the player-facing experience.

For Startup Sim this becomes:

- The office is the board.
- Rooms are the controls.
- AI characters are advisors and narrative pressure, not rule owners.
- Deterministic systems decide numeric outcomes.
- Data definitions should be reusable enough to support scenarios, localization, and future desktop distribution.
