# Startup Sim 项目交接文档

更新时间：2026-05-18  
固定工作目录：`D:\Startup-sim`  
GitHub 仓库：`https://github.com/KSYyyyz/startup-sim`  
当前主线：Godot 桌面端独立游戏  
当前分支：`master`

## 1. 必须遵守的工作规则

1. 所有操作必须在 `D:\Startup-sim` 下完成。
2. 不再使用 C 盘旧工作副本。
3. 每完成一轮有效修改，必须本地验证、commit、push，并检查 GitHub Actions。
4. 以后只做 Godot 前端，不再维护 Vercel/Web 前端。
5. 所有项目文档默认使用中文。
6. AI 玩法暂时不做。
7. Godot 美术资产包现在可以跟踪在 `godot/StartupSimGodot/assets/art/`，后续新增资源需保留索引、prompt、源图、导出图和切片指南。
8. Python CLI/飞书代码暂时作为规则参考和回归测试来源保留，不能在 C# Core 完整覆盖前删除。
9. C# Core 是规则核心，Godot 负责表现层和交互，不要在 Godot UI 里复制经营规则。
10. 玩家可见文案使用“现金流可支撑时间”，不要恢复“跑道”或 `Runway`。

## 2. 当前仓库状态

最近已推送功能提交：

- `a9f551e test: add godot g1 vertical slice acceptance`
- `d7d9749 feat: add monthly report feedback`
- `6ed4689 feat: add godot time progression`
- `cdb6d47 feat: add office capacity preview`
- `a8b1446 feat: add employee growth and needs`

第 1 到第 10 轮 Godot G1 推进已经完成并推送：

1. 内容数据层。
2. 办公室网格系统。
3. 区域框定。
4. 设施摆放与升级。
5. 员工招聘与岗位适配。
6. 员工成长与需求。
7. 产能快照。
8. 时间推进与月度结算。
9. 月报与反馈面板。
10. G1 可玩切片验收。

最新 CI 已通过：

- `CSharp core tests`
- `Godot CSharp project build`
- `Pytest`
- `Godot content data check`
- `Playtest`
- `Docs consistency check`
- Python 格式与静态检查

当前美术资产：

- `godot/StartupSimGodot/assets/art/`

该目录现在作为 Godot 资产包跟踪。新增资源应先补齐 `asset-index.json`、prompt、source、export 和 slice guide，再进入 Godot 导入验证。

## 3. 当前核心文件

产品与路线：

- `docs/startup_sim_development_plan.md`
- `docs/godot_g1_acceptance_report.md`
- `docs/godot_migration_plan.md`
- `docs/csharp_core_migration_plan.md`
- `docs/gameplay_contracts.md`
- `docs/reference_game_analysis.md`
- `docs/workspace_rules.md`

Godot 工程：

- `godot/StartupSimGodot/project.godot`
- `godot/StartupSimGodot/scenes/main.tscn`
- `godot/StartupSimGodot/scripts/StartupSimController.cs`
- `godot/StartupSimGodot/scripts/GodotTurnBridge.cs`
- `godot/StartupSimGodot/scripts/OfficeGridView.cs`
- `godot/StartupSimGodot/scripts/ZonePaintingController.cs`
- `godot/StartupSimGodot/scripts/FacilityPlacementController.cs`
- `godot/StartupSimGodot/scripts/EmployeeManagementController.cs`
- `godot/StartupSimGodot/scripts/CapacityPreviewController.cs`
- `godot/StartupSimGodot/scripts/TimeProgressController.cs`
- `godot/StartupSimGodot/scripts/MonthlyReportController.cs`

C# Core：

- `csharp/StartupSim.Core/Contracts/`
- `csharp/StartupSim.Core/Engines/`
- `csharp/StartupSim.Core/Office/`
- `csharp/StartupSim.Core/Parsing/`
- `csharp/StartupSim.Core.Tests/`

内容数据：

- `godot/StartupSimGodot/data/`
- `scripts/validate_godot_content.py`

Python 参考实现：

- `src/core/`
- `src/agents/`
- `app.py`
- `feishu_play.py`
- `tests/`

## 4. 当前验证命令

PowerShell 中执行：

```powershell
cd /d D:\Startup-sim

python -m ruff check .
python -m black --check --line-length 100 --target-version py311 .
python -m isort --check-only --profile black --line-length 100 .

$env:PATH='D:\Startup-sim\.work\dotnet;' + $env:PATH
dotnet test csharp\StartupSim.Core.Tests\StartupSim.Core.Tests.csproj --configuration Release
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj --configuration Debug

python scripts\validate_godot_content.py
python scripts\check_docs_consistency.py
pytest tests/ -q
python scripts\playtest.py
```

最近一次完整本地验证结果：

- C# Core 测试：38 passed
- Godot C# build：0 warnings，0 errors
- Pytest：422 passed
- Godot 内容数据检查：8 个文件，25 条定义，通过
- 文档一致性检查：通过
- 自动试玩脚本：退出码 0，但仍提示当前平衡下结局分布只有破产

自动试玩的“所有策略都破产”是已知平衡问题，不是 G1 办公室切片阻断项。后续应该在规则平衡阶段处理。

## 5. 当前产品方向

项目不再以 CLI 文本指令作为最终玩法形态。核心玩法已经调整为：

1. 玩家以俯视角管理一块办公室。
2. 玩家从区域划分目录里选择研发区、销售区、服务器区等部门，在办公室网格里框定区域。
3. 玩家在区域内添加设施，例如办公桌、白板、服务器机柜等。
4. 设施有升级梯度，等级越高，价格和维护费越高，增益也越强。
5. 玩家通过员工管理入口招聘、分配、训练员工，查看能力、岗位适配、特性和需求状态。
6. 员工有自己的状态算法，会疲劳、休息、娱乐、上厕所、情绪波动、生病，并影响公司产能。
7. 游戏时间持续推进，支持暂停、正常速度、二倍速、三倍速。
8. 主线目标是公司经营发展、收益增长、阶段成就和复盘故事；办公室建设和员工成长服务于这条主线。

当前仍坚持的产品原则：

> 真实商业作为底层逻辑，游戏性作为表层体验。

玩家看到的是选择、冲突、爽点和反馈；现金流、估值、融资、竞品、董事会、客户、结局等复杂规则由 C# Core 在后台推演。

## 6. 已完成的 G1 能力

G1 当前具备代码级纵向切片：

1. 办公室网格。
2. 区域框定。
3. 设施摆放与升级。
4. 员工招聘与岗位适配。
5. 员工成长与需求。
6. 产能快照。
7. 时间推进与月度结算。
8. 月报与反馈。
9. G1 纵向切片自动化测试。

对应验收报告：

- `docs/godot_g1_acceptance_report.md`

对应关键测试：

- `csharp/StartupSim.Core.Tests/OfficeG1VerticalSliceTests.cs`
- `tests/test_godot_scaffold.py::test_godot_g1_acceptance_report_exists`

## 7. 下一步建议

下一阶段应该进入 G2：Godot 可操作 UI 与 C# Core 经营规则对齐。

建议优先级：

1. 把当前 Godot 控制器连接成最小可操作 UI，让玩家可以真实点击完成划区、摆设施、招聘、训练、推进月份。
2. 建立公司目标、收入目标和阶段成就数据。
3. 将办公室产能快照转化为 C# Core 可消费的结构化经营意图。
4. 补齐 C# Core 的现金、产品、用户、MRR、融资拒绝、董事会、竞品、客户和结局事实。
5. 建立 Godot 本地存档与读取。
6. 建立 Godot 复盘页。
7. 等基础局可离线完成后，再准备 Windows 可试玩包。

暂时不要做：

- Web/Vercel 前端恢复。
- Unity 分支恢复。
- AI 自由指令或 AI 对话。
- 移动端适配。
- 上市、债务、回款、毛利等后期复杂系统一次性加入。
- 跳过资产索引直接提交零散美术文件。

## 8. 新会话接力提示词

下面这段提示词可以直接复制到新的 Codex 会话：

```text
你现在接手 KSYyyyz/startup-sim 项目。

固定工作目录：
D:\Startup-sim

GitHub 仓库：
https://github.com/KSYyyyz/startup-sim

请先执行：
1. cd /d D:\Startup-sim
2. git status --short
3. git branch --show-current
4. git pull --ff-only
5. 阅读 HANDOFF.md、docs/startup_sim_development_plan.md、docs/godot_g1_acceptance_report.md

重要规则：
1. 所有操作都必须在 D:\Startup-sim 下完成。
2. 每完成一轮有效修改，都必须本地验证、commit、push，并检查 GitHub Actions。
3. 不要再使用 C 盘旧工作副本。
4. 以后只做 Godot 前端，不再维护 Vercel/Web 前端。
5. 所有项目文档默认用中文。
6. AI 玩法暂时不做。
7. godot/StartupSimGodot/assets/art/ 现在可以作为 Godot 美术资产包跟踪，后续新增资源也应补齐索引、prompt、源图、导出图和切片指南。
8. Python CLI/飞书代码暂时作为规则参考和回归测试来源保留，不能在 C# Core 完整覆盖前删除。
9. C# Core 是规则核心，Godot 负责表现层和交互，不要在 Godot UI 里复制经营规则。
10. 玩家可见文案必须使用“现金流可支撑时间”，不要恢复“跑道”或 Runway。

当前状态：
- Godot G1 十轮推进已完成并推送。
- 最新功能提交包括：
  - a9f551e test: add godot g1 vertical slice acceptance
  - d7d9749 feat: add monthly report feedback
  - 6ed4689 feat: add godot time progression
- 最新 CI 已通过。
- C# Core 测试最近为 38 passed。
- Pytest 最近为 422 passed。
- Godot 内容数据检查通过。
- 文档一致性检查通过。
- 自动试玩脚本退出码 0，但仍提示当前平衡下所有策略都破产，这是后续平衡问题，不是 G1 切片阻断项。

当前产品方向：
项目已经从 CLI 规则原型转向 Godot 桌面端独立游戏。核心玩法是俯视角办公室经营：
1. 玩家在办公室网格里划分研发区、销售区、服务器区等部门。
2. 在部门区域中摆放和升级设施。
3. 招聘、分配、训练员工，管理员工能力、岗位适配、特性和需求状态。
4. 员工会疲劳、休息、娱乐、上厕所、情绪波动、生病，并影响公司产能。
5. 游戏时间持续推进，支持暂停、正常速度、二倍速、三倍速。
6. 主线目标是公司经营发展、收益增长、阶段成就和复盘故事；办公室建设和员工成长服务于主线。

下一阶段请推进 G2：
1. 把当前 Godot 控制器连接成最小可操作 UI，让玩家可以真实点击完成划区、摆设施、招聘、训练、推进月份。
2. 建立公司目标、收入目标和阶段成就数据。
3. 将办公室产能快照转化为 C# Core 可消费的结构化经营意图。
4. 补齐 C# Core 的现金、产品、用户、MRR、融资拒绝、董事会、竞品、客户和结局事实。
5. 建立 Godot 本地存档与读取。
6. 建立 Godot 复盘页。
7. 等基础局可离线完成后，再准备 Windows 可试玩包。

验证命令：
python -m ruff check .
python -m black --check --line-length 100 --target-version py311 .
python -m isort --check-only --profile black --line-length 100 .
$env:PATH='D:\Startup-sim\.work\dotnet;' + $env:PATH
dotnet test csharp\StartupSim.Core.Tests\StartupSim.Core.Tests.csproj --configuration Release
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj --configuration Debug
python scripts\validate_godot_content.py
python scripts\check_docs_consistency.py
pytest tests/ -q
python scripts\playtest.py

请先同步仓库并阅读 HANDOFF.md，再基于当前真实状态给出下一轮执行计划，然后开始实现。每轮结束都要验证、commit、push、检查 CI。
```
