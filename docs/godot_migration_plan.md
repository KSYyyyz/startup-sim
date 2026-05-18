# Godot 迁移方案

Status: active engine direction
Date: 2026-05-18

## 1. Direction

Startup Sim 的最终独立游戏表现层切换为 Godot。

Unity 路线停止作为新增开发目标。此前已经创建的 Unity 适配脚本只作为历史探索材料保留；后续新增工程、场景、交互原型和桌面端可分发路线都以 Godot 为准。

Web 前端继续作为规则验证台：它负责快速验证 API、文本反馈和玩法规则，不再作为最终独立游戏表现层打磨。

## 2. Engine Version

目标版本：Godot 4.6.x .NET editor。

依据：

- Godot 官方下载归档已列出 4.6.x 稳定版本。
- Godot 官方 C#/.NET 文档说明，使用 C# 需要 .NET 版编辑器。
- Godot 官方文档提醒 `latest` 文档可能包含尚未适配稳定版的内容，因此项目文档以 stable / 4.6.x 为准。

References:

- https://godotengine.org/download/archive/
- https://docs.godotengine.org/en/latest/tutorials/scripting/c_sharp/index.html
- https://docs.godotengine.org/en/stable/about/release_policy.html

## 3. Architecture

```text
csharp/
  StartupSim.Core/                  Portable gameplay rules
  StartupSim.Core.Tests/            Compile and golden-case gate

godot/
  StartupSimGodot/
    StartupSimGodot.csproj          Godot C# project referencing StartupSim.Core
    project.godot                   Godot desktop project
    scenes/main.tscn                First boot scene
    scripts/                        Godot presentation adapters

```

## 4. Rules Boundary

`StartupSim.Core` / C# Core owns:

- action parsing
- turn settlement
- cash, product, users, MRR, valuation, equity, endings
- golden tests

Godot owns:

- office scene
- room hotspots
- prepared action display
- command submission
- animation, sound, layout, feedback timing

Godot scripts must not duplicate gameplay settlement rules. They can display structured action snapshots and call the local C# bridge. API access is optional and should only be added for remote AI or cloud-save features.

## 5. First Godot Slice

The first Godot slice should contain:

1. A bootable main scene.
2. Office room hotspots.
3. A prepared action snapshot model.
4. A controller that can prepare and clear actions.
5. A local bridge that calls `StartupSim.Core` directly.
6. A turn result snapshot that Godot UI can display.

Current bridge:

- `StartupSimGodot.csproj` references `../../csharp/StartupSim.Core/StartupSim.Core.csproj`.
- `GodotTurnBridge` owns a `GameState`, calls `DeterministicTurnEngine.Execute()`, and returns `TurnResultSnapshot`.
- `StartupSimController` submits the prepared action through `GodotTurnBridge` when the bridge is assigned.

Build check:

```powershell
$env:PATH = "D:\Startup-sim\.work\dotnet;$env:PATH"
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj
```

## 6. Godot CLI Workflow

Godot can be operated through the editor and the CLI.

Local commands:

```powershell
D:\Godot\godot.cmd --version
D:\Godot\godot.cmd --editor --path D:\Startup-sim\godot\StartupSimGodot
D:\Godot\godot.cmd --headless --path D:\Startup-sim\godot\StartupSimGodot --import
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj --configuration Debug
```

The project should add repo-local wrappers under `scripts/` before Godot build/export work becomes frequent.

## 7. C# Core Migration Link

The detailed rules migration plan lives in `docs/csharp_core_migration_plan.md`.

Near-term C# priorities:

1. Expand `GameState` / `GameMetrics` toward Python parity.
2. Port StateGuard cash and budget checks.
3. Port fundraising valuation and rejection logic.
4. Expose board, competitor, customer, insight, ending, and review facts as renderer-neutral snapshots.

## 8. Near-Term Order

1. Keep migrating gameplay rules into `StartupSim.Core`.
2. Build Godot office shell around structured actions.
3. Use `GodotTurnBridge` for local desktop playtests.
4. Add optional API bridge only if remote AI or cloud-save features require it.
5. Do not restore the deleted Vercel/Web frontend route; new presentation work belongs in Godot.

## 9. Adaptation Status

High-value core code is partially adapted for Godot:

- Completed: portable `ActionParser`, minimal deterministic C# turn engine, golden-case tests, Godot C# project, local `GodotTurnBridge`, and CI build gate.
- Not yet complete: full Python `TurnEngine` parity, StateGuard cash/budget rejection, fundraising valuation/rejection parity, board/competitor/customer/insight fact snapshots, ending/review parity, and a full 12-month Godot offline run.

Because of that, Python `src/core/` remains the complete reference implementation and must not be deleted until the C# Core parity gates are complete.
