# Godot 迁移方案

Status: active engine direction
Date: 2026-05-18

## 1. Direction

Startup Sim 的最终独立游戏表现层切换为 Godot。

Unity 路线暂停。此前已经创建的 Unity 适配脚本保留为历史探索材料，但后续新增工程、场景、交互原型和桌面端可分发路线都以 Godot 为准。

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

frontend/
  Rule validation bench only
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

Godot scripts must not duplicate gameplay settlement rules. They can display structured action snapshots and call either the current API or a future local C# bridge.

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

## 6. Near-Term Order

1. Keep migrating gameplay rules into `StartupSim.Core`.
2. Build Godot office shell around structured actions.
3. Use `GodotTurnBridge` for local desktop playtests.
4. Add optional API bridge only if a remote service is needed for AI features.
5. Keep Vercel frontend available for rule QA and quick remote demos.
