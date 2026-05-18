# C# Core 迁移方案

Status: active core direction
Date: 2026-05-18

## 1. 目标

`csharp/StartupSim.Core/` 是后续 Godot 独立游戏版本的长期规则核心。

Python 版本仍是完整规则参考实现；C# Core 逐步承接已经被黄金样例覆盖的玩法切片。Godot 只能调用 C# Core 或展示 C# Core 的结果，不能复制现金、产品、用户、估值、股权、结局等结算规则。

## 2. 当前结构

```text
csharp/
  StartupSim.Core/          纯 C# 玩法规则核心，不依赖任何表现层引擎
  StartupSim.Core.Tests/    xUnit 编译与黄金样例门禁
  golden-cases/             Python 参考输出与 C# 便携规则样例

godot/
  StartupSimGodot/          Godot 4.6.x .NET 表现层
```

## 3. C# Core 已覆盖

- `ActionParser.ParseMulti()`：研发、营销、招聘、战略、融资、多动作、预算、风险词、融资额、出让比例和投后估值。
- `DeterministicTurnEngine` 最小回合结算：产品、营销、团队、战略、融资、多动作聚合、月度固定消耗、团队自然学习、现金透支破产保护。
- xUnit 测试与 GitHub CI 门禁。
- Godot 工程通过 `ProjectReference` 直接引用 `StartupSim.Core`。

## 4. 迁移规则

1. C# Core 必须保持纯规则层，不引用 Godot API。
2. Godot 脚本只负责输入、展示、动画和本地桥接。
3. Python 仍是完整玩法参考，C# 每迁移一个规则切片必须有黄金样例或等价单元测试。
4. 规则迁移优先级高于表现层扩张。
5. 新增字段先进入合同文档和测试，再进入 Godot UI。

## 5. 黄金测试

当前黄金样例：

- `csharp/golden-cases/month01_product_investment.json`
- `csharp/golden-cases/action_parser_multi.json`
- `csharp/golden-cases/turn_engine_minimal.json`

本地验证：

```powershell
dotnet test csharp\StartupSim.Core.Tests\StartupSim.Core.Tests.csproj --configuration Release
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj --configuration Debug
```

## 6. 下一步迁移顺序

1. 把 Python `CompanyState` 中 Godot 必需的状态字段补齐到 C# `GameState` / `GameMetrics`。
2. 迁移 StateGuard 的现金约束、预算拦截和中文可解释错误。
3. 迁移融资估值与拒绝逻辑，解决“显示估值”和“可融资估值”必须同源的问题。
4. 迁移董事会、竞品、客户和经营洞察的事实输出，不迁移表现文案布局。
5. 迁移结局与复盘事实，使 Godot 可以离线跑完 12 个月。
6. 用黄金样例覆盖一局 12 回合标准路线。

## 7. Godot 适配完成度

当前高价值核心代码已经完成“Godot 可调用”的第一阶段适配，但还没有完成“完整玩法迁移”。

已完成：

- C# Core 可编译、可测试。
- Godot 工程可引用 C# Core。
- `GodotTurnBridge` 可以本地执行准备好的行动。
- CI 已包含 C# Core tests 和 Godot C# build。

未完成：

- Python TurnEngine 全量规则 parity。
- StateGuard 预算拦截 parity。
- 融资估值和拒绝模型 parity。
- 董事会、竞品、客户、洞察和复盘事实 parity。
- 12 个月完整离线 Godot 流程。

## 8. 不做

- 不把 Godot UI 文案写回 C# Core。
- 不在 Godot 中重新实现 TurnEngine。
- 不再推进 Unity 适配层。
- 不为了完整复制 Python 一次性重写所有系统；每次只迁移可验证切片。
