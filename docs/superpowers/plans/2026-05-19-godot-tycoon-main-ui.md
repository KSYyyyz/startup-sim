# Godot Tycoon Main UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current right-side Godot operations dashboard with a tycoon-style HUD where the office scene is primary and controls live in top, bottom, floating, and modal layers.

**Architecture:** Keep `G2OperationsPanelController` as the existing interaction coordinator, but change its scene children and NodePath defaults to a full-screen HUD. Preserve C# Core ownership of business rules and keep Godot responsible for presentation and interaction only.

**Tech Stack:** Godot 4.6.2 .NET, C#, `.tscn` scene editing through Godot tooling, Python pytest scaffold checks.

---

### Task 1: Lock the UI Direction With Tests and Docs

**Files:**
- Create: `docs/godot_tycoon_main_ui_design.md`
- Modify: `tests/test_godot_scaffold.py`

- [x] **Step 1: Write the failing tests**

Add assertions that `main.tscn` contains `TopStatusBar`, `BottomActionDock`, `FloatingEventFeed`, `RoomContextPanel`, and `MonthlyReportModal`, and no longer contains `PanelBacking` or `text = "公司经营面板"`.

- [x] **Step 2: Write the Chinese design spec**

Save the design direction in `docs/godot_tycoon_main_ui_design.md`, including the phrase “右侧常驻看板退场” and the reference direction “疯狂游戏大亨 2”.

- [ ] **Step 3: Run the focused tests and verify they fail before implementation**

Run:

```powershell
pytest tests/test_godot_scaffold.py::test_godot_main_scene_uses_mad_games_tycoon_style_hud_layout tests/test_godot_scaffold.py::test_godot_main_scene_keeps_operations_hud_inside_default_viewport -q
```

Expected before implementation: failures mentioning missing `TopStatusBar`, missing design doc, or old right-side offsets.

### Task 2: Rebuild the Godot HUD Scene

**Files:**
- Modify: `godot/StartupSimGodot/scenes/main.tscn`

- [ ] **Step 1: Use Godot scene tools to make `G2OperationsPanel` full-screen**

Set `G2OperationsPanel` offsets to `0, 0, 1152, 648`.

- [ ] **Step 2: Remove the right-side dashboard children**

Remove `PanelBacking`, `TitleLabel`, old direct labels, old direct button groups, and the old feedback portrait node.

- [ ] **Step 3: Add the new HUD child tree**

Create `TopStatusBar`, `FloatingEventFeed`, `BottomActionDock`, `RoomContextPanel`, and `MonthlyReportModal`, with the existing button names preserved under new parent groups so the controller can reconnect them.

- [ ] **Step 4: Set exported NodePaths on `G2OperationsPanel`**

Set:

```text
StatusLabelPath = NodePath("FloatingEventFeed/StatusLabel")
MetricsLabelPath = NodePath("TopStatusBar/MetricsLabel")
GoalsLabelPath = NodePath("RoomContextPanel/GoalsLabel")
CapacityLabelPath = NodePath("RoomContextPanel/CapacityLabel")
ReportLabelPath = NodePath("MonthlyReportModal/ReportLabel")
ReplayLabelPath = NodePath("MonthlyReportModal/ReplayLabel")
```

### Task 3: Update Controller Paths and Modal Behavior

**Files:**
- Modify: `godot/StartupSimGodot/scripts/G2OperationsPanelController.cs`

- [ ] **Step 1: Update default NodePaths**

Change label defaults to the new HUD child paths.

- [ ] **Step 2: Update button connection paths**

Use paths such as `BottomActionDock/BuildTools/ProductZoneButton` and `TopStatusBar/TimeButtons/TripleSpeedButton`.

- [ ] **Step 3: Add report modal behavior**

Add `HideMonthlyReport()` and `ShowMonthlyReport()`. Call `ShowMonthlyReport()` after a successful month settlement or save-load report display.

- [ ] **Step 4: Keep business semantics unchanged**

Do not reference `DeterministicTurnEngine` or rewrite cash, users, MRR, product, burn, financing, board, competitor, or customer logic in Godot UI.

### Task 4: Verify and Ship

**Files:**
- Test: `tests/test_godot_scaffold.py`
- Test: Godot MCP runtime

- [ ] **Step 1: Run focused pytest**

Run:

```powershell
pytest tests/test_godot_scaffold.py::test_godot_main_scene_uses_mad_games_tycoon_style_hud_layout tests/test_godot_scaffold.py::test_godot_month_settlement_updates_top_metrics_snapshot -q
```

Expected: pass.

- [ ] **Step 2: Build Godot C#**

Run:

```powershell
$env:PATH='D:\Startup-sim\.work\dotnet;' + $env:PATH
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj --configuration Debug
```

Expected: `0 warning, 0 error`.

- [ ] **Step 3: Run the Godot scene with MCP**

Run `res://scenes/main.tscn`, verify the HUD starts with C# Core metrics in `TopStatusBar/MetricsLabel`, and verify a month settlement opens `MonthlyReportModal`.

- [ ] **Step 4: Run full local validation**

Run ruff, black, isort, C# tests, Godot build, Godot import, content validation, docs consistency, pytest, and playtest.

- [ ] **Step 5: Commit, push, and check Actions**

Commit only the design, plan, controller, scene, and test files for this task. Leave art-agent worktree changes untouched.
