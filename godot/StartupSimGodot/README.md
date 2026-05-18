# Startup Sim Godot

这是 Startup Sim 的 Godot 桌面表现层。

目标编辑器：Godot 4.6.x .NET。

当前范围：

- 可启动的 `main.tscn` 外壳。
- 只负责表现层的 C# 脚本。
- 结构化的预备行动快照。
- `GodotTurnBridge` 调用可移植 C# Core；Godot 脚本不复制结算规则。

规则权威仍在 `../../csharp/StartupSim.Core/`。

从仓库根目录构建检查：

```powershell
$env:PATH = "D:\Startup-sim\.work\dotnet;$env:PATH"
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj
```

旧 Web/Vercel 前端路线已经移除。新的表现层工作都应放在这个 Godot 项目中。

## 内容数据

- G1 内容数据放在 `data/`。
- 区域类型、设施、设施升级、员工职位、技能、特性、成长轨道和培训动作都使用 JSON 定义。
- 从仓库根目录执行 `python scripts/validate_godot_content.py` 校验内容。
- 新增玩法内容必须保持 ID 唯一、引用有效。不要把区域、设施或员工定义硬编码进场景脚本。
