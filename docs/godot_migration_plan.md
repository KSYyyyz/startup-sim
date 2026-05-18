# Godot 迁移方案

状态：当前引擎方向
日期：2026-05-18

## 1. 方向

Startup Sim 的最终独立游戏表现层切换为 Godot。

Unity 路线停止作为新增开发目标。此前已经创建的 Unity 适配脚本只作为历史探索材料保留；后续新增工程、场景、交互原型和桌面端可分发路线都以 Godot 为准。

Web 前端路线已放弃。Godot 是唯一新增前端和最终独立游戏表现层。

## 2. 引擎版本

目标版本：Godot 4.6.x .NET 编辑器。

依据：

- Godot 官方下载归档已列出 4.6.x 稳定版本。
- Godot 官方 C#/.NET 文档说明，使用 C# 需要 .NET 版编辑器。
- Godot 官方文档提醒 `latest` 文档可能包含尚未适配稳定版的内容，因此项目文档以 stable / 4.6.x 为准。

参考链接：

- https://godotengine.org/download/archive/
- https://docs.godotengine.org/en/latest/tutorials/scripting/c_sharp/index.html
- https://docs.godotengine.org/en/stable/about/release_policy.html

## 3. 架构

```text
csharp/
  StartupSim.Core/                  可复用玩法规则
  StartupSim.Core.Tests/            编译和黄金用例门禁

godot/
  StartupSimGodot/
    StartupSimGodot.csproj          引用 StartupSim.Core 的 Godot C# 项目
    project.godot                   Godot 桌面项目
    scenes/main.tscn                首个启动场景
    scripts/                        Godot 表现层适配脚本

```

## 4. 规则边界

`StartupSim.Core` / C# Core 负责：

- 行动解析
- 时间推进与经营结算
- 现金、产品、用户、MRR、估值、股权、结局
- 黄金用例测试

Godot 负责：

- 俯视角办公室场景
- 大像素办公室网格
- 区域选择和区域框定
- 设施摆放、移动、出售和升级
- 员工招聘、分配、特性、需求和团队管理
- 公司目标、收益、成就和经营意图展示
- 时间控制：暂停、正常速度、二倍速、三倍速
- 动画、音效、布局和反馈节奏

Godot 脚本不得复制玩法结算规则。它们可以把办公室布局、设施、员工能力和员工状态转换为结构化经营意图快照，再调用本地 C# 桥接层。API、模型和云存档不属于近期路线，只能在离线 Godot 闭环稳定后重新评估。

## 5. 首个 Godot 切片

首个 Godot 切片应包含：

1. 可启动的主场景。
2. 俯视角办公室网格。
3. 区域选择和区域框定。
4. 设施摆放和升级数据。
5. 员工管理入口。
6. 员工能力、特性、疲劳、情绪、健康和需求状态。
7. 时间控制：暂停、正常速度、二倍速、三倍速。
8. 从区域、设施和员工状态派生出的经营意图快照。
9. 直接调用 `StartupSim.Core` 的本地桥接层。
10. Godot UI 可展示的回合结果快照。

当前桥接：

- `StartupSimGodot.csproj` references `../../csharp/StartupSim.Core/StartupSim.Core.csproj`.
- `GodotTurnBridge` owns a `GameState`, calls `DeterministicTurnEngine.Execute()`, and returns `TurnResultSnapshot`.
- `StartupSimController` 在桥接层可用时，通过 `GodotTurnBridge` 提交准备好的行动。

构建检查：

```powershell
$env:PATH = "D:\Startup-sim\.work\dotnet;$env:PATH"
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj
```

## 6. Godot 命令行工作流

Godot 可以通过编辑器和命令行操作。

本地命令：

```powershell
D:\Godot\godot.cmd --version
D:\Godot\godot.cmd --editor --path D:\Startup-sim\godot\StartupSimGodot
D:\Godot\godot.cmd --headless --path D:\Startup-sim\godot\StartupSimGodot --import
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj --configuration Debug
```

在 Godot 构建和导出工作变频繁前，项目应在 `scripts/` 下补充仓库内封装脚本。

## 7. C# Core 迁移链接

详细规则迁移方案见 `docs/csharp_core_migration_plan.md`。

近期 C# 优先级：

1. 扩展 `GameState` / `GameMetrics`，逐步对齐 Python 参考实现。
2. 迁移 StateGuard 现金和预算检查。
3. 迁移融资估值和拒绝逻辑。
4. 增加公司目标、收益、成就、员工状态和时间推进相关事实。
5. 输出董事会、竞品、客户、洞察、结局和复盘事实的表现层无关快照。

## 8. 近期顺序

1. 继续把玩法规则迁移到 `StartupSim.Core`。
2. 围绕公司目标、收益、区域、设施和员工建设 Godot 办公室经营外壳。
3. 通过 `GodotTurnBridge` 把办公室布局、设施、员工能力和员工状态转换为结构化经营意图快照。
4. 在离线 Godot 闭环稳定前，不增加 API、模型或云存档范围。
5. 不恢复已删除的 Vercel/Web 前端路线；新的表现层工作都属于 Godot。

## 9. 适配状态

高价值核心代码已经部分适配 Godot：

- 已完成：可移植 `ActionParser`、最小确定性 C# 回合引擎、黄金用例测试、Godot C# 项目、本地 `GodotTurnBridge` 和 CI 构建门禁。
- 未完成：完整 Python `TurnEngine` 对齐、StateGuard 现金/预算拒绝、融资估值/拒绝对齐、公司目标/收益/成就、员工自主状态、时间推进、董事会/竞品/客户/洞察事实快照、结局/复盘对齐，以及完整 12 个月 Godot 离线局。

因此，Python `src/core/` 仍是完整参考实现。C# Core 对齐门禁完成前，不得删除。
