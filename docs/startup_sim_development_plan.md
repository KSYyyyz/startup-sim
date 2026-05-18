# 创业模拟器完整开发规划

Status: active master plan
Date: 2026-05-18
Owner: Codex

## 1. 项目定位

Startup Sim 是一款以 AI 创业公司经营为主题的独立模拟经营游戏。

一句话目标：

> 玩家作为 AI SaaS 创始人，在可互动办公室中做经营取舍，通过产品、现金流、团队、客户、融资、董事会和竞品压力，走出不同创业命运。

项目第一原则：

> 真实商业作为底层逻辑，游戏性作为表层体验。

玩家不应该被迫参加财务考试。复杂机制用于后台推演，前台只呈现选择、冲突、反馈、故事和复盘。

## 2. 当前路线结论

后续主线：

- 表现层：`godot/StartupSimGodot/`
- 规则核心：`csharp/StartupSim.Core/`
- 完整参考实现：`src/core/`
- 内容数据层：`godot/StartupSimGodot/data/` 与 `data/`
- 资产库：`design-assets/` 与 `godot/StartupSimGodot/assets/`

已经停止的路线：

- 不再维护 Vercel/Web 前端。
- 不再新增 Unity 主线代码。
- 不再把 CLI/飞书作为最终游戏形态。

保留的路线：

- Python CLI/飞书代码作为完整规则参考和回归测试来源保留。
- C# Core 逐步迁移 Python 规则，直到可以支撑 Godot 离线完整游玩。
- Godot 成为唯一正式前端和可分发桌面端。

## 3. 产品体验目标

### 3.1 目标体验

玩家进入游戏后看到的是一个可操作的创业办公室，而不是仪表盘墙。

核心体验包括：

- 点击办公室房间，选择本月行动。
- 通过董事会、客户、竞品、团队反馈理解经营压力。
- 在现金流可支撑时间、产品能力、用户增长、融资压力之间做取舍。
- 使用自由 CEO 指令表达意图，但系统必须给出可解释预览。
- 每回合结束看到清晰月报：发生了什么、为什么、下月压力是什么。
- 每局结束进入复盘：关键转折、失败原因、可改进策略、成就。

### 3.2 玩家可见语言

必须使用玩家能理解的表达。

使用：

- 现金流可支撑时间
- 本月焦点
- 经营洞察
- 董事会争议
- 竞品态势
- 客户反馈
- 回合结果

避免默认展示：

- Runway
- LTV/CAC
- Gross Margin
- ARR Growth
- PMF 复杂公式
- 上市板块法规

高级指标可以进入详情层，但不能压在主界面。

### 3.3 失败体验

失败不是惩罚弹窗，而是一段可复盘创业故事。

每个失败结局都必须回答：

- 为什么失败。
- 哪些信号提前出现过。
- 当时有哪些可选补救。
- 下局可以换哪条路线。

## 4. 目标玩家与产品形态

优先目标玩家：

- 喜欢模拟经营、策略取舍、公司成长题材的玩家。
- 能接受文字反馈，但希望有可操作空间和视觉反馈。
- 对创业、AI、商业竞争、融资故事有兴趣。

产品参考方向：

- 《疯狂游戏大亨2》：长期经营、办公室空间、内容库、公司成长。
- 《Big Ambitions》：商业布局、场景配置、外置内容数据。
- 《Game Dev Tycoon》：轻量循环、事件反馈、Mod 边界。
- 《STONKS-9800》：简单数据文件、名字库、本地化和扩展入口。
- 《历史模拟器：崇祯》：事件、叙事、复盘和策略压力。

Startup Sim 不直接复制任何参考游戏玩法、素材或代码，只吸收工程组织和产品结构经验。

## 5. 总体架构

```text
Player
  -> Godot Office UI
  -> Content Database
  -> Action Preview
  -> C# Core StateGuard
  -> C# Core Turn Settlement
  -> Fact Snapshots
  -> AI Narrative Layer
  -> Godot Monthly Report / Review
```

### 5.1 Godot 表现层

Godot 负责：

- 办公室场景。
- 房间热点。
- 行动卡和命令输入。
- HUD 与月报。
- 角色反馈、动画、音效、镜头和交互。
- 本地存档和桌面端导出。

Godot 不负责：

- 重写现金、估值、融资、竞品、客户、董事会规则。
- 绕过 C# Core 修改核心数值。
- 在 UI 层硬编码大量游戏内容。

### 5.2 C# Core 规则核心

C# Core 负责：

- 动作解析。
- 预算和现金校验。
- 回合结算。
- 产品、用户、MRR、估值、股权、声誉、团队等状态变化。
- 董事会、竞品、客户、经营洞察、结局的事实快照。
- 可重复测试的确定性规则。

### 5.3 Python 参考实现

Python 继续负责：

- 作为完整规则参考。
- 作为回归测试来源。
- 作为迁移对照。
- 在 C# Core 未完整对齐前，不删除 `src/core/`。

删除 Python 参考实现的前置条件：

- C# Core 已覆盖完整 12 个月基础局。
- C# Core 已覆盖融资、StateGuard、董事会、竞品、客户、洞察、结局和复盘。
- Godot 可以离线完成一局并展示完整复盘。
- Python 与 C# 的 golden case 对齐通过。
- CI 不再依赖 Python 规则测试。

### 5.4 内容数据层

参考游戏目录后，本项目必须尽早建立内容数据层。

目标目录：

```text
godot/StartupSimGodot/data/
  scenarios/
  rooms/
  actions/
  events/
  board/
  competitors/
  customers/
  investors/
  help/
  locales/

data/
  golden_cases/
  balance_cases/
  content_schema/
```

内容数据层负责：

- 剧本定义。
- 房间定义。
- 玩家行动入口。
- 董事会角色。
- 竞品原型。
- 投资人原型。
- 客户类型。
- 月度事件。
- 帮助文本。
- 本地化文本。

Godot 必须从内容数据读取可变内容，而不是把内容写死在场景脚本中。

## 6. 核心玩法循环

### 6.1 单回合循环

1. 玩家观察办公室状态、本月焦点和风险提示。
2. 玩家点击房间或选择行动入口。
3. 系统展示行动取舍，不直接展示复杂公式。
4. 玩家确认行动，或输入自由 CEO 指令。
5. 系统生成行动预览，说明预计影响和风险。
6. C# Core 通过 StateGuard 校验行动。
7. C# Core 执行回合结算。
8. Godot 展示月度结果、角色反馈、竞品态势和经营洞察。
9. 历史事实进入复盘记录。

### 6.2 中期循环

1. 验证产品方向。
2. 获得早期用户。
3. 面对现金流可支撑时间压力。
4. 在产品、增长、招聘、融资、节流之间取舍。
5. 形成公司路线风格。

### 6.3 长期循环

1. 路线成型：产品信仰、资本狂飙、大客户、精益创业、产业合作。
2. 逐步解锁 PMF、销售体系、回款、毛利、组织压力、合规、上市路线。
3. 进入多种结局：破产、勉强存活、A 轮成功、被收购、技术孤岛、创始人出局、独角兽、IPO。

## 7. 阶段解锁设计

复杂度必须渐进解锁。

| 阶段 | 玩家关注 | 新增概念 |
| --- | --- | --- |
| 0-12 个月 | 活下去、做产品、拿 A 轮 | 现金流、产品、用户、融资 |
| A 轮后 | 找 PMF、增长、团队扩张 | 客户验证、留存、组织压力 |
| B 轮后 | 销售体系、回款、毛利 | 大客户、交付、毛利、回款 |
| C 轮后 | 资本结构、行业地位 | 董事会、战略合作、竞品并购 |
| Pre-IPO | 盈利、治理、上市选择 | 合规、审计、上市路径 |

每个阶段只引入 1-2 个新概念。

## 8. 行动系统

### 8.1 基础行动

第一阶段必须支持：

- 研发产品。
- 招聘人才。
- 市场营销。
- 融资谈判。
- 控制成本。
- 客户验证。

每个行动必须包含：

- 玩家可读名称。
- 所属房间。
- 适用阶段。
- 成本或资源消耗。
- 主要收益。
- 主要风险。
- 一句人话解释。

### 8.2 自由 CEO 指令

自由指令不能变成万能沙盒。

正确流程：

1. 玩家输入自然语言。
2. 系统解析为结构化行动计划。
3. UI 展示预览。
4. 玩家确认。
5. StateGuard 校验。
6. TurnEngine 结算。

自由指令不能直接改写核心状态。

### 8.3 避免一键依赖

系统不能鼓励玩家依赖“一键生成最优指令”。

建议系统的定位：

- 解释当前局势。
- 提醒风险。
- 给方向，不给唯一答案。
- 提供 2-3 个风格不同的策略选择。
- 不自动替玩家填入最优行动。

## 9. 董事会、竞品与客户

### 9.1 董事会

董事会反馈必须基于本回合执行后的状态。

董事会角色来源：

- CFO：现金流、预算、融资风险。
- CTO：产品、技术债、研发路线。
- COO：交付、团队、运营效率。
- 投资机构代表：只在融资或外部投资相关场景出现。
- 独立董事：后期治理阶段解锁。

没有融资或外部投资时，不得凭空出现投资方董事。

### 9.2 竞品

竞品要像真实市场压力，而不是装饰文本。

第一阶段竞品要影响：

- 获客成本。
- 市场份额。
- 用户增长。
- 声誉。
- 投资人信心。

竞品行为包括：

- 降价抢客户。
- 发布新功能。
- 融资扩张。
- 抢大客户。
- 媒体曝光。

### 9.3 客户

客户反馈是 PMF 的人话表达。

第一阶段只展示：

- 客户验证：弱 / 中 / 强。
- 产品市场匹配：未验证 / 初步验证 / 明确验证。

后台可以计算访谈数、留存、激活、付费意愿、试点客户，但默认不展示公式。

## 10. AI 设计边界

AI 是体验增强层，不是规则层。

AI 可以做：

- 自由指令解析辅助。
- 角色反馈生成。
- 事件叙事。
- 复盘总结。
- 帮助解释。
- 个性化语气。

AI 不可以做：

- 绕过 C# Core 直接修改核心数值。
- 生成无法复现的结算结果。
- 凭空增加投资方、董事或事件事实。
- 在没有事实快照时编造原因。
- 把建议变成自动最优解按钮。

所有 AI 输出必须基于事实快照。

## 11. Godot 开发规划

### G0：工程骨架与桥接

状态：已完成基础切片。

验收：

- Godot 4.x .NET 工程可打开。
- Godot 项目可引用 `StartupSim.Core`。
- 主场景可启动。
- `GodotTurnBridge` 可调用 C# Core。
- CI 可构建 Godot C# 项目。

### G1：本地可玩垂直切片

目标：Godot 内完成一个基础回合。

验收：

- 至少 5 个房间热点。
- 每个房间至少 1 个基础行动。
- 行动可预览。
- 行动可提交。
- 回合由 C# Core 结算。
- HUD 显示现金、现金流可支撑时间、MRR、用户、产品、声誉、股权、估值。
- 月报显示本月变化、原因、董事会、竞品、经营洞察。

### G2：内容数据层

目标：行动、房间、角色、竞品、事件从数据读取。

验收：

- `ContentDatabase` 可加载 JSON 内容。
- 内容 ID 唯一性检查通过。
- Godot 房间和行动不再硬编码。
- 缺字段、重复 ID、引用失效会在验证脚本中失败。
- README 或 docs 写明新增内容的方法。

### G3：C# Core 规则对齐

目标：C# Core 支撑 12 个月基础局。

验收：

- StateGuard 预算拦截完整。
- 融资估值和拒绝逻辑完整。
- 董事会事实快照完整。
- 竞品事实快照完整。
- 客户事实快照完整。
- 结局与复盘事实完整。
- Python golden case 与 C# golden case 对齐。

### G4：办公室经营感

目标：办公室成为可读的经营空间。

验收：

- 房间有状态：正常、风险、机会、阻塞、改善。
- 状态变化来自结算事实。
- 角色气泡来自事实快照。
- 行动结果有轻量动画或视觉变化。
- 信息密度低于旧 Web 仪表盘。

### G5：AI 原生体验

目标：AI 成为可感知的角色和解释层。

验收：

- 自由指令有预览。
- 角色反馈引用历史事实。
- 复盘总结引用关键回合。
- AI 不可用时有 deterministic fallback。
- AI 输出不改变核心结算。

### G6：可分发桌面 Demo

目标：导出 Windows 可试玩包。

验收：

- Windows 导出成功。
- 离线可完成基础局。
- 本地存档可读写。
- 至少 5 个结局可展示。
- 复盘页可展示成就和关键转折。
- 导出包有版本号和发布说明。

## 12. C# Core 迁移规划

迁移顺序：

1. 状态模型补齐。
2. 动作解析补齐。
3. StateGuard 预算和现金规则。
4. 产品、营销、招聘、战略结算。
5. 融资估值和拒绝逻辑。
6. 客户增长和 MRR。
7. 竞品行为。
8. 董事会事实快照。
9. 经营洞察。
10. 结局和复盘。
11. Golden case 对齐。
12. Godot 12 个月离线局。

每迁移一个模块都必须：

- 先写 C# 测试。
- 对照 Python 行为。
- 加入 CI。
- 更新文档。

## 13. 内容数据规划

第一批内容文件：

```text
godot/StartupSimGodot/data/scenarios/ai_saas_seed.json
godot/StartupSimGodot/data/rooms/office_rooms.json
godot/StartupSimGodot/data/actions/basic_actions.json
godot/StartupSimGodot/data/board/board_roles.json
godot/StartupSimGodot/data/competitors/early_competitors.json
godot/StartupSimGodot/data/customers/customer_segments.json
godot/StartupSimGodot/data/investors/investor_profiles.json
godot/StartupSimGodot/data/events/monthly_events.json
godot/StartupSimGodot/data/help/ceo_handbook.json
godot/StartupSimGodot/data/locales/zh-cn.json
```

第一批 schema：

- `ScenarioDefinition`
- `RoomDefinition`
- `ActionDefinition`
- `BoardRoleDefinition`
- `CompetitorDefinition`
- `CustomerSegmentDefinition`
- `InvestorProfileDefinition`
- `MonthlyEventDefinition`
- `HelpTopicDefinition`
- `LocalizationBundle`

## 14. 美术和资产规划

资产原则：

- 所有 AI 生成数字资源使用 image-2。
- Prompt 存入 `design-assets/image-2/prompts/`。
- 导出结果存入 `design-assets/image-2/exports/`。
- 可进 Godot 的稳定资产放入 `godot/StartupSimGodot/assets/`。
- 资产登记进入 `design-assets/manifest.json`。

优先资产：

1. 办公室基础背景。
2. 房间状态覆盖层。
3. 董事会、员工、客户、投资人头像。
4. 行动卡插画。
5. 竞品 Logo 和市场图标。
6. 事件图标。
7. 结局复盘插画。

资产不能承载关键 UI 文案。关键文本必须由 Godot 渲染，方便本地化和修改。

## 15. 存档与复盘规划

本地存档必须记录：

- 当前状态。
- 回合历史。
- 每回合行动。
- StateGuard 拦截记录。
- 董事会反馈。
- 竞品动作。
- 客户反馈。
- 经营洞察。
- 关键转折。
- 结局和成就。

复盘页必须展示：

- 最终结局。
- 公司路线风格。
- 关键 3-5 个转折。
- 最大风险。
- 最大机会。
- 下局建议方向。

## 16. 测试和验收体系

### 16.1 本地验证命令

Python：

```powershell
pytest tests/ -q
python scripts/check_docs_consistency.py
python -m ruff check .
python -m black --check .
python -m isort --check-only .
```

C#：

```powershell
dotnet test csharp\StartupSim.Core.Tests\StartupSim.Core.Tests.csproj --configuration Release
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj --configuration Debug
```

Godot：

```powershell
D:\Godot\godot.cmd --version
D:\Godot\godot.cmd --headless --path D:\Startup-sim\godot\StartupSimGodot --import
```

### 16.2 CI 门禁

每次有效修改必须：

1. 本地测试通过。
2. commit。
3. push。
4. 检查 GitHub Actions。
5. 若失败，优先修复 CI，不继续堆功能。

### 16.3 手动试玩验收

每个可玩切片必须完成：

- 新开一局。
- 执行 3 个不同房间行动。
- 执行 1 次融资或融资失败。
- 触发 1 次现金流风险提示。
- 查看董事会、竞品、经营洞察。
- 保存并重新加载。

## 17. 协作工作流

开发默认采用双轨思路：

- 前端/表现轨：Godot 场景、交互、HUD、月报、资产接入。
- 后端/规则轨：C# Core、内容数据、规则测试、golden case。

并行工作必须遵守：

- 前端不复制规则。
- 后端不决定最终 UI 密度。
- 双方通过结构化 snapshot 和 content data 对接。
- 每轮修改后 commit + push。
- 遇到冲突时以 C# Core 规则和 Godot 数据层边界为准。

## 18. 近期十轮推进计划

### 第 1 轮：建立 Godot 内容数据层

产出：

- `godot/StartupSimGodot/data/` 目录。
- 第一批 JSON 内容文件。
- 内容验证脚本。
- 文档说明。

验收：

- 内容验证脚本通过。
- Godot 构建通过。

### 第 2 轮：Godot ContentDatabase

产出：

- C# `ContentDatabase`。
- 加载 scenario、rooms、actions。
- 单元测试或构建验证。

验收：

- Godot 能读取数据并显示房间/行动。

### 第 3 轮：行动入口数据化

产出：

- 房间热点绑定 action ID。
- 行动卡从 JSON 渲染。
- 移除硬编码基础行动。

验收：

- 新增行动只改 JSON 即可出现在 Godot。

### 第 4 轮：月报结构化

产出：

- C# Core 输出统一 `MonthlyReportSnapshot`。
- Godot 月报读取 snapshot。

验收：

- 月报包含变化、原因、董事会、竞品、洞察。

### 第 5 轮：C# StateGuard 对齐

产出：

- 预算校验。
- 现金流可支撑时间校验。
- 破产拦截。

验收：

- 固定支出大于现金时不能继续假运行。

### 第 6 轮：融资规则对齐

产出：

- 合理估值区间。
- 报价过高拒绝。
- 反报价。
- 投资人 profile。

验收：

- UI 显示估值和融资结果同源。

### 第 7 轮：董事会与竞品事实快照

产出：

- BoardFactSnapshot。
- CompetitorFactSnapshot。
- Godot 面板显示。

验收：

- 每回合都有董事会和竞品反馈。
- 没有融资时不出现投资方董事。

### 第 8 轮：本地存档

产出：

- 保存当前局。
- 读取当前局。
- 存档版本号。

验收：

- 关闭后重开可以继续一局。

### 第 9 轮：复盘与结局

产出：

- 结局页面。
- 关键转折记录。
- 成就徽章。

验收：

- 失败也有可读复盘。

### 第 10 轮：Windows 可试玩包

产出：

- Godot Windows 导出脚本。
- Release checklist。
- 本地试玩报告。

验收：

- 可生成一个可发给别人试玩的桌面包。

## 19. 版本路线

### Alpha G1

目标：Godot 内可完成基础单回合。

### Alpha G2

目标：Godot 内可完成 12 个月基础局。

### Alpha G3

目标：办公室空间、角色反馈、月报和复盘成型。

### Alpha G4

目标：AI 指令预览、角色叙事和复盘增强。

### Beta 0.1

目标：Windows 可分发试玩包。

### Beta 0.5

目标：多剧本、多结局、平衡性第一轮。

### 1.0

目标：完整独立游戏首发版本。

## 20. 当前不做

当前不做：

- Web/Vercel 前端恢复。
- Unity 主线恢复。
- 完整 3D 办公室。
- 多人联机。
- 云存档。
- 移动端适配。
- 上市、债务、回款、毛利等后期系统一次性上线。
- AI 自动生成最优行动。

这些内容只有在 Godot 基础可玩闭环稳定后再评估。

## 21. 下一步

下一步执行顺序：

1. 建立 Godot 内容数据层 v0.1。
2. 建立内容验证脚本。
3. 让 Godot 从数据读取房间和基础行动。
4. 把回合结果标准化为 Godot 可显示 snapshot。
5. 继续迁移 C# Core 规则，直到支撑 12 个月离线局。

完成上述内容后，Startup Sim 才真正从 CLI 规则原型进入 Godot 独立游戏工程阶段。
