# Startup Sim — 版本开发报告

当前路线以最新 Alpha 1.9.1 体验验证；前端并行推进 Alpha 0.3 AI 指令解释层

---

## C# / Unity Migration Prep — ActionParser portable slice (2026-05-18)

**性质**: C# Core 规则迁移第一刀。目标是先把自然语言指令解析迁入 `StartupSim.Core`，让 Unity 未来可以拿到结构化行动，而不是依赖 Web 前端或 Python API 做输入理解。

**主要产出**:
- 新增 C# 合同：`ActionPlan`、`PlayerAction`、`ActionType`、`RiskLevel`。
- 新增 `StartupSim.Core.Parsing.ActionParser.ParseMulti()`，承接 Python `parse_multi()` 的最小行为：分段预算、研发/营销/招聘/战略/融资识别、风险词、融资额、出让比例、投后估值。
- 新增 `csharp/golden-cases/action_parser_multi.json`，以 Python 当前输出作为解析器黄金样例。
- 新增 `ActionParserTests` 与黄金样例校验，C# Core 测试数从 4 增加到 9。

**验收边界**:
- 本轮只迁移解析层，不迁移现金、产品、用户、董事会、竞品或结局结算。
- C# 解析器继续保持 `UnityEngine` 零依赖。
- Python 仍是完整玩法参考实现，C# 只承接已被黄金样例覆盖的输入解析切片。

---

## C# / Unity Migration Prep — Compile gate and CI coverage (2026-05-18)

**性质**: C# Core 迁移基础设施收口。目标是让 `StartupSim.Core` 不再只是文件骨架，而是进入可编译、可测试、可在 GitHub CI 上守门的状态。

**主要产出**:
- 新增 `csharp/StartupSim.Core.Tests/` xUnit 测试工程，覆盖首个产品投入切片、输入状态不可变、未知指令兜底，以及 Python 参考黄金样例读取。
- CI 新增 `.NET 8` 安装与 `dotnet test csharp/StartupSim.Core.Tests/StartupSim.Core.Tests.csproj --configuration Release`，后续 C# 规则迁移会被自动编译验证。
- `.gitignore` 新增 `csharp/**/bin/` 和 `csharp/**/obj/`，避免把本地编译产物推入仓库。
- `docs/csharp_unity_migration_plan.md` 补充 C# 测试门禁、CI 命令、本地 `.work/dotnet` SDK 使用边界。

**验收边界**:
- C# Core 仍保持 `UnityEngine` 零依赖。
- Unity 侧仍只是适配层，不拥有现金、产品、估值、董事会或竞品结算规则。
- Python TurnEngine 仍是完整规则参考实现，C# 只迁移已纳入黄金样例的切片。

---

## C# / Unity Migration Prep — Core and adapter scaffold (2026-05-18)

**性质**: 技术路线切换准备。目标是把项目从 Web 前端打磨主线，转向 C# Core + Unity 表现层的可迁移架构。

**主要产出**:
- 新增 `docs/csharp_unity_migration_plan.md`，明确 Web 前端降级为规则验证台，`StartupSim.Core` 成为未来规则层。
- 新增 `csharp/StartupSim.Core/` 纯 C# 核心库骨架，包含 `GameState`、`GameMetrics`、`TurnCommand`、`TurnResult`、`ScenarioDefinition`、`ITurnEngine`、`DeterministicTurnEngine`。
- 新增 `csharp/golden-cases/month01_product_investment.json`，作为 Python 参考实现到 C# 迁移的第一条黄金样例。
- 新增 `unity/StartupSimUnity/Assets/Scripts/StartupSim/` Unity 适配组件：房间热点、行动展示、回合提交、API 桥接。
- 新增 `tests/test_csharp_unity_scaffold.py`，锁定 C# Core 不依赖 `UnityEngine`，Unity 侧不拥有结算规则。

**当前限制**:
- 本机只有 .NET Runtime，没有 .NET SDK，因此本轮先用仓库测试验证结构边界；后续安装 SDK 后再补 C# 编译与单元测试。
- Unity 组件目前是竖切准备脚本，还不是完整 Unity 工程。

---

## Frontend Alpha 0.5 — 十轮推进验收收口 (2026-05-18)

**性质**: 本轮连续推进收口。目标是把第 4-10 轮新增体验纳入自动化验收，而不是只靠手工截图判断。

**主要产出**:
- Playwright 主流程新增对 `指令完整度`、`本月判定`、`本局路线`、董事会关键信号、竞品关键信号的验收。
- 本轮不新增机制，只确认桌面主链路从行动选择、指令准备、执行回合到结果反馈都能看见新增读条。

**验收边界**:
- 不触碰体外资产包。
- 不改变后端结算。
- 保持建议默认折叠和“现金流可支撑时间”文案。

---

## Frontend Alpha 0.5 — 本局路线识别 (2026-05-18)

**性质**: 创业风格反馈切片。目标是让玩家感到“这局在走某种路线”，形成可复盘的故事。

**主要产出**:
- `buildPlaystyleRoute()` 根据本回合指令和结算变化识别产品信仰、资本狂飙、增长试验、精益创业、均衡探索等路线。
- 左侧信息流新增“本局路线”卡，展示路线、当前叙事和风险。
- 路线识别只解释玩家已经发生的打法，不生成下一步指令。

**验收边界**:
- 不改变阶段目标和结算规则。
- 不新增强制路线锁定。

---

## Frontend Alpha 0.5 — 右侧关键信号摘要 (2026-05-18)

**性质**: 信息密度收口切片。目标是让右侧董事会和竞品面板先给玩家一个扫描入口，再显示详细列表。

**主要产出**:
- `buildSidePanelBrief()` 生成董事会/竞品的关键信号摘要。
- 董事会面板显示角色数量、优先回应数量和当前焦点。
- 竞品面板显示动态数量、高优先级数量和当前焦点。

**验收边界**:
- 不隐藏已有可操作入口。
- 不改变建议默认折叠规则。

---

## Frontend Alpha 0.5 — 指令完整度提示 (2026-05-18)

**性质**: 自由输入可控性增强切片。目标是帮助玩家自己写清楚 CEO 指令，而不是依赖系统生成命令。

**主要产出**:
- `buildCommandReadiness()` 检查自由输入是否包含动作、预算或规模、行动对象。
- 底部指令区新增“指令完整度”提示：等待指令、需要更具体、可以执行。
- 提示只指出缺失项，不给玩家生成可复制命令。

**验收边界**:
- 不改变命令解析和 TurnEngine。
- 不新增一键生成指令。

---

## Frontend Alpha 0.5 — 竞品威胁读条 (2026-05-18)

**性质**: 竞品态势可读性增强切片。目标是让玩家看到竞品动作时能判断优先级，而不是只读一条状态文本。

**主要产出**:
- `buildCompetitorMoves()` 现在附带 `高威胁 / 中威胁 / 低威胁` 和一句判断读条。
- 竞品面板展示威胁等级与判断句，例如“优先判断是否会影响你的核心客户”。
- 威胁读条只解释态势，不替代玩家决策。

**验收边界**:
- 不改变竞品结算或后端模拟。
- 不新增自动反击逻辑。

---

## Frontend Alpha 0.5 — 董事会氛围摘要 (2026-05-18)

**性质**: 角色反馈可读性增强切片。目标是让董事会不是一串平铺消息，而是先给玩家一个总体状态。

**主要产出**:
- `buildBoardRoomMood()` 根据董事成员信任趋势和压力标签生成 `董事会认可 / 董事会承压 / 董事会有分歧 / 董事会观望`。
- 董事会面板顶部新增“董事会氛围”摘要，显示当前焦点。
- CFO 在现金下降时会更明确进入承压状态，压力标签指向“现金压力 / 控制支出”。

**验收边界**:
- 只基于当前董事成员和 settled metrics，不凭空出现投资方。
- 不改变董事会反馈生成后端逻辑。

---

## Frontend Alpha 0.5 — 本月判定卡 (2026-05-18)

**性质**: 回合结算可读性增强切片。目标是让玩家提交一回合后，先看到一句游戏化判定，再看详细月报。

**主要产出**:
- `buildTurnVerdict()` 将结算后的现金、产品、用户、收入变化翻译成 `漂亮 / 有进展 / 承压 / 危险 / 平稳` 等短判定。
- 月度战报顶部新增“本月判定”卡，包含判定、原因和下月关注点。
- 判定仍然只读取 settled metrics，不参与数值结算。

**验收边界**:
- 不改变 TurnEngine。
- 不引入新商业系统。
- 判定只解释状态，不提供一键指令。

---

## Frontend Alpha 0.5 — 房间行动预期读条 (2026-05-18)

**性质**: 房间行动可读性增强切片。目标是让玩家在点击办公室房间后，先看懂行动的收益、代价、适合时机和风险，再决定是否采用。

**主要产出**:
- `GameplayActionDefinition` 新增可选 `expectation` 字段，用四段人话描述行动预期。
- 产品室、研发团队、销售区、董事会、服务器的房间行动均补齐 `收益 / 代价 / 适合时机 / 风险`。
- `OfficeStage` 的房间行动卡新增紧凑预期读条，保留原有 tradeoff 标签和采用行动按钮。
- 测试覆盖所有房间行动必须提供预期读条，并禁止把公式、专业指标或“一键”依赖写进该区域。

**验收边界**:
- 本轮只增强行动理解，不改变 TurnEngine 结算、融资、估值或现金逻辑。
- 预期读条是解释，不是自动建议；玩家仍可自由输入 CEO 指令。
- 不触碰体外资产包。

---

## Frontend Alpha 0.5 — 本月目标游戏化轨道 (2026-05-18)

**性质**: 早期目标反馈增强切片。目标是让“本月小目标”从提示文案变成更像游戏任务的进度轨道。

**主要产出**:
- `buildCurrentMonthGoal()` 现在输出 `trackLabel`、`progressPercent` 和 `checkpoints`，用于展示产品成熟度、现金安全线、市场验证等目标轨道。
- `本月小目标` UI 新增进度条和检查点列表，让玩家能看到当前目标推进到哪里。
- 检查点只包含状态和方向，例如“产品达到可验证区间”“现金流可支撑时间保持安全”，不包含固定命令。
- Playwright 查询进一步收紧到语义区域和标题，避免引导文案与主面板标题重复时产生误判。

**验收边界**:
- 本轮仍不改变后端结算，不增加 PMF/贷款/上市等复杂机制。
- 本月目标不提供按钮，不生成一键行动，不把建议变成自动指令。

---

## Frontend Alpha 0.5 — 前三回合经营节奏与本月小目标 (2026-05-18)

**性质**: 桌面端第一体验切片。目标是让新玩家前 3 个月知道该看什么、怎么理解结算、如何形成本局路线，同时避免依赖一键生成指令。

**主要产出**:
- `frontend/src/game/gameplayContent.ts` 新增 `buildNewPlayerGuidance()`，只在第 1-3 月显示经营节奏：先读局面、读懂结算、形成路线。
- 新增 `buildCurrentMonthGoal()`，把阶段目标翻译成本月小目标，例如产品验证前、现金承压、验证市场。
- `frontend/src/App.tsx` 在左侧信息流中显示“新手经营节奏”和“本月小目标”，只展示方向标签、检查点和风险提示，不提供按钮或固定命令。
- `frontend/src/App.test.tsx` 和 `frontend/src/game/gameplayContent.test.ts` 覆盖新手引导、本月目标、无一键/无固定指令依赖。

**验收边界**:
- 不改变 TurnEngine、StateGuard、融资、估值或现金结算。
- 不新增复杂商业机制。
- 不触碰体外资产包。
- 玩家可见文案继续使用“现金流可支撑时间”，不出现“跑道”或 Runway。

---

## Frontend Performance Pass — PixiJS optional chunk boundary (2026-05-18)

**性质**: 桌面前端性能边界收口。目标是让办公室 Canvas 层继续可选，同时避免 PixiJS 被误并入主入口。

**主要产出**:
- `frontend/src/buildChunks.ts` 新增 Vite/Rollup 分包规则，将 `pixi.js` 和 `@pixi/*` 统一命名到 `pixi-overlay` chunk。
- `frontend/vite.config.ts` 接入分包规则，并把当前发布预算调整到适合“主入口轻、Pixi 可选异步加载”的边界。
- `frontend/src/buildConfig.test.ts` 锁定分包规则，防止未来改动把 Pixi 重新吸回主包。
- `docs/frontend_alpha_0_2_desktop_game_layer.md` 更新性能结论：当前路线继续保留 Pixi 可选层，未来只有在低端设备或桌面包冷启动变差时才替换更轻 renderer。

**验证重点**:
- `npm run build` 输出主入口约 243KB，`pixi-overlay` 约 853KB，且不再出现大 chunk 警告。
- 本轮不改变 TurnEngine、不改变房间行动结算、不触碰体外资产包。

---

## Alpha 0.4 — TurnFacts 后端序列化第一切片 (2026-05-18)

**性质**: 共同合同层的第一轮后端落地。目标是让前端和未来 Unity 不再从 UI 文案或分散字段里猜“本回合事实”。

**主要产出**:
- `src/api/app.py` 新增 `turn.turn_facts`，从 settled `TurnResult` 序列化 `month`、`command`、`changes`、`replay_basis`、`next_pressure`、`authority`。
- `tests/test_frontend_api.py` 覆盖 `turn_facts` 来自后端结算结果、`delta.reasons` 和结算后压力。
- `frontend/src/types.ts`、`frontend/src/store.ts`、`frontend/src/App.tsx` 兼容可选 `turn_facts`；有新事实时月报优先使用它，旧响应仍走 `delta_reasons`。
- `docs/frontend_api_contract.md` 和 `docs/gameplay_contracts.md` 更新为当前 HTTP 合同。

**Agent 参与方式**:
- 后端/规则 Agent 实现 serializer、后端测试和合同文档。
- 前端/美术 Agent 实现类型、store 和月报兼容适配。
- 主控完成集成、冲突检查、完整验证、提交和推送。

**验收边界**:
- TurnEngine 结算逻辑不变。
- `changes` 第一切片只覆盖现金、月经常收入、用户、产品四类核心变化。
- `RoleMemory` 和 `OfficeSignal` 仍未暴露 HTTP，后续必须基于 `TurnFacts` 继续推进。

---

## Alpha 0.4 Contract & Agent Workflow Prep (2026-05-18)

**性质**: 为后续 Web/Tauri/Unity 可迁移路线做的工作流和合同层收口。

**主要产出**:
- `docs/workspace_rules.md` 新增双 Agent 并行工作流：前端/美术 Agent、后端/规则 Agent、共同合同层的写权限和边界。
- `docs/gameplay_contracts.md` 新增合同基线，覆盖 `ActionPlan`、`TurnFacts`、`RoleMemory`、`OfficeSignal`、`ScenarioDefinition`、`AssetManifest`。
- `frontend/src/game/contracts.ts` 建立前端可引用的引擎无关合同 manifest 和转换函数。
- `docs/unity_migration_probe.md` 固定未来 Unity 最小验证边界：只做办公室房间到 `ActionPlan`，不重写 TurnEngine。
- `design-assets/` 规范强化：image-2 资产必须登记 `used_by`，且引用文件必须存在并直接引用 `public_url`。
- `docs/frontend_api_contract.md` 对齐当前 API 字段，减少文档与实现漂移。

**Agent 参与方式**:
- 前端/美术 Agent 已真实修改 `design-assets/README.md` 和 `design-assets/manifest.json`，补强资产 usage contract。
- 后端/规则 Agent 已真实修改 `docs/gameplay_contracts.md`，补充后端迁移 notes。
- 主控负责合同基线、测试、提交、推送、CI 和线上验证。

**验收边界**:
- 本阶段不切 Unity，只保留可迁移路径。
- 前端仍不能结算数值。
- 后端仍不输出布局结构。
- 新合同字段在 HTTP 暴露前必须先补 serializer 和测试。

---

## Frontend Alpha 0.3 — 月度叙事事实引用切片 (2026-05-18)

**性质**: Alpha 0.3 AI 叙事层的事实约束切片。目标是让月度战报更像复盘故事，同时明确告诉玩家每段判断来自哪些已发生事实。

**主要产出**:
- `MonthlyReport` 新增 `factCitations`，包含执行指令、结算变化、复盘依据三类事实。
- `buildMonthlyReport()` 只从本回合命令、指标变化和后端 `delta_reasons` 生成事实引用。
- 前端月度战报新增紧凑的“事实依据”区块，避免再堆一个独立大面板。
- 补充 Vitest 覆盖月报事实引用和前端展示。

**验收边界**:
- 事实依据只引用已经发生的指令和结算结果，不生成新状态。
- 数值结果仍由 TurnEngine/StateGuard 负责。
- 叙事增强必须服务复盘，不替代核心经营判断。

---

## Frontend Alpha 0.3 — 执行前预期与角色记忆切片 (2026-05-18)

**性质**: Alpha 0.3 AI 指令解释层的第二个可玩切片。目标是让 AI 感不只来自手动输入解释，而是进入所有行动入口和董事会连续反馈。

**主要产出**:
- `buildPreparedActionPreview()`：房间行动、底部快捷行动、董事会回应、竞品回应、月报补救行动都可以生成同一套只读执行前预期。
- 底部 `AI 指令解释` 面板现在会在选择预设行动后自动出现，不必额外点击“解释指令”。
- 董事会 NPC 画像新增轻量记忆事实：例如 CFO 会记住上月现金减少，CTO 会记住产品改善或被忽视。
- 角色记忆只消费上一回合指令和已结算指标，不直接修改现金、产品、用户等核心数值。
- 补充 Vitest 覆盖统一预期生成和董事会记忆展示。

**验收边界**:
- 所有数值结算仍由 TurnEngine 执行。
- 记忆事实必须基于已有状态，不凭空生成投资方或改写董事会结构。
- 新反馈进入现有底部解释面板和董事会行内文案，不新增大面板。

---

## Frontend Alpha 0.3 — AI 指令解释层首个切片 (2026-05-18)

**性质**: 前端独立游戏化的 AI 原生玩法切片。目标是让自由 CEO 指令不再只是文本框，而是在执行前被解释成玩家可理解、可复核的行动候选。

**主要产出**:
- `POST /api/sessions/{session_id}/command-preview` — 只读命令解释 API，复用现有 `parse_multi`，不推进月份、不修改存档。
- `frontend/src/api.ts` / `frontend/src/store.ts` — 接入命令预览状态和 demo fallback。
- `frontend/src/App.tsx` — 底部指令区新增“解释指令”和紧凑 `AI 指令解释` 面板。
- `docs/frontend_alpha_0_3_ai_command_layer.md` — Alpha 0.3 执行计划。
- `docs/frontend_api_contract.md` — 补充命令预览 API 合同。

**设计边界**:
- 当前是规则解释原型，不引入真实 LLM 依赖。
- AI 风格反馈只解释玩家意图，不拥有数值结算权。
- 最终状态变化仍由 TurnEngine、StateGuard 和后端规则执行。
- 线上 Vercel 没有真实后端时仍可用 demo fallback 展示解释。

**验收重点**:
- 玩家输入自由命令后，可以先看到动作类别、预算、风险和取舍。
- 解释面板明确提示“数值结算仍由 TurnEngine 执行”。
- 预览 API 不会推进回合。
- 文案继续使用“现金流可支撑时间”，不出现“跑道”或 Runway。

---

## Frontend Alpha 0.3 — 线上试玩 Bug 修复 (2026-05-18)

**来源**: 人工试玩 Vercel 当前版本后发现的问题。主流程可用，但 demo fallback、移动端快捷条和解释面板密度仍影响试玩质量。

**修复内容**:
- Vercel 静态前端在未配置真实 API 时直接进入 demo fallback，不再先请求 `/api/*` 产生 405 控制台错误。
- `demoCommandPreview()` 改为按分句解析自由命令，`花10万研发产品，花5万做营销` 会正确显示产品研发 10 万、市场营销 5 万。
- 移动端快捷指令条增加“解释”按钮，并在空指令时禁用“解释/执行”。
- `AI 指令解释` 面板改为紧凑样式，隐藏重复 intent 文本，减少底部区域重新变重的问题。
- Playwright 覆盖移动端解释路径和空指令禁用状态。

**验证重点**:
- 线上 demo 不应出现 `/api/sessions`、`/api/turns`、`/api/command-preview` 的 405 fallback 噪声。
- 桌面和移动端都能先解释指令，再执行回合。
- 解释结果仍强调数值结算由 TurnEngine 执行。

---

## Reference Game Scan — 本地参考游戏结构分析 (2026-05-18)

本轮对五个本地安装目录做了只读结构扫描，产出文档：[docs/reference_game_analysis.md](docs/reference_game_analysis.md)。

- `Mad Games Tycoon 2`：确认 Unity 经营游戏的公司空间、房间、设施、图标和文本资源组织方向，只作为办公室经营形态参考，不复制资源。
- `STONKS-9800`：确认公开 mod/localization/data-like 目录价值，作为 Startup Sim 后续原始数据层、场景包、文本本地化和未来 mod 边界的参考。
- `历史模拟器：崇祯`：确认 Electron/Chromium 桌面分发形态，支持当前 Web 先行、桌面打包预留的技术路线。
- `Game Dev Story / 游戏开发物语`：确认小屏、快节奏、渐进复杂度的经营循环价值，提醒 Startup Sim 早期回合必须轻巧。
- `Game Dev Tycoon`：确认 NW.js/Web 技术桌面分发、i18n、mods、公开 mod API 目录价值，进一步支持 Web 先行、桌面包装、数据扩展路线。

结论：继续保持 Vite/React/PixiJS 桌面 Web 试玩路线，不切 Unity；下一步优先把房间、行动、压力响应、竞品反馈、办公室信号等前端玩法定义逐步数据化，并为未来 Tauri/Electron/NW.js 类桌面分发留空间。

## Frontend Alpha 0.2 — 桌面游戏层连续推进 (2026-05-18)

**性质**: 前端独立游戏化切片。目标是把 Web 入口从状态面板推进为可点击、可操作、可反馈的办公室经营场景。

**线上入口**: https://startup-sim-khaki.vercel.app

**主要产出**:
- `frontend/src/game/gameplayContent.ts` — UI 无关的房间/行动/取舍标签数据层，作为后续剧本包和内容数据化的起点。
- `frontend/src/game/OfficeStage.tsx` — 办公室主场景、房间热点、动态反馈、月末变化。
- `frontend/src/App.tsx` — 董事会/竞品/建议/记录面板与底部 CEO 指令闭环。
- `frontend/e2e/startup-sim.spec.ts` — 桌面 1366×768、1440×900、1920×1080 与移动 smoke 覆盖。
- `docs/frontend_alpha_0_2_desktop_game_layer.md` — 前端 Alpha 0.2 执行计划与迭代进度。

**已完成的可玩闭环**:
1. 办公室房间可点击，行动卡可生成自然语言 CEO 指令。
2. 董事会信号和竞品信号可从办公室动态反馈进入右侧面板。
3. 董事会压力可生成回应指令，并显示来源解释。
4. 竞品压力可生成回应指令，并显示来源解释。
5. 回应指令会显示取舍标签，如 `用户 +`、`现金 -`、`现金流可支撑时间 +`。
6. 提交回合后，办公室场景内显示月末变化，左侧显示月度战报。
7. 房间和行动定义已从 UI 组件中抽出，为后续原创剧本包、行业包和本地化做准备。
8. 董事会/竞品压力回应模板已进入玩法数据层，UI 只负责触发和展示回应。
9. 底部快捷行动已进入玩法数据层，并复用“已准备行动”预览。
10. 办公室压力脉冲路由已进入玩法数据层，为未来剧本/行业包扩展房间信号做准备。
11. 办公室行动、快捷行动、董事会回应、竞品回应已统一到同一套“已准备行动”预览。
12. 房间经营状态已数据化，可在办公室场景显示“运转中”“产品改善”等状态。

**验证记录**:
- Python: `pytest tests/ -q` → 400 passed
- Frontend: `npm test -- --run` → 15 passed
- Frontend E2E: `npm run test:e2e` → 8 passed
- GitHub CI: latest pushed frontend slices passed
- Vercel smoke: `https://startup-sim-khaki.vercel.app` verified after push

**下一步**:
- 将普通办公室行动卡、底部快捷按钮与压力回应统一为同一套执行前预期系统。
- 继续桌面端优先，移动端保持 smoke 级别。
- 后续性能 pass 需要处理 PixiJS 大 chunk。

---

## Frontend Alpha 0.2 — 桌面信息减负修复 (2026-05-18)

**来源**: 桌面预览图反馈。问题是首屏信息过密，中心办公室被多层浮动信息遮挡，右侧竞品内容重复，底部指令区占位过重，导致玩家无法顺畅完成“看办公室 → 选房间 → 选行动 → 执行回合”的主流程。

**修复方向**:
- 顶部 HUD 从 9 项缩减为 6 项核心经营指标：月份、现金、现金流可支撑时间、月经常收入、用户、产品。
- “当前剧本”改为默认折叠，只保留标题、状态和难度，避免左侧首屏继续拉长。
- 中央办公室移除默认动态反馈条、事件气泡和底部洞察条，只保留本月焦点、房间热点、房间状态、操作台和回合后的月末变化。
- 经营洞察移入左侧核心矛盾面板，保持可见但不遮挡主场景。
- 右侧移除重复的竞品概览卡，竞品详情只在“竞品”标签页展示。
- 底部指令区压缩空状态和按钮高度，降低对主场景的挤压。

**验收重点**:
- 首屏视觉焦点回到办公室主场景。
- 玩家不用在多个重复面板中寻找竞品信息。
- 董事会、竞品、建议、记录仍可通过右侧标签进入。
- 建议仍默认折叠，现金相关文案继续使用“现金流可支撑时间”。

---

## Alpha 1.9.1 — 体验验证与路线收口 (2026-05-17)

**性质**: 体验验证与路线收口版本。**本轮不添加任何复杂游戏机制。**

**背景**: Alpha 1.9 完成了5项核心反馈增强（核心矛盾、竞品态势、经营洞察、危机解释、StateGuard进复盘）。Alpha 1.9.1 的目标是在真人试玩验证之前，把文档、规划、反馈模板和版本一致性全部收口。

**主要产出**:
- `plans/20260517-gameplay-first-roadmap.md` — 游戏性优先后续路线规划（Alpha 2.0/2.1/2.2/3.0）
- `docs/playtest_alpha_1_9_1_plan.md` — Alpha 1.9.1 试玩验证计划（3-5次真人试玩，7个核心问题，4类反馈归类）
- `docs/playtest_feedback_log.md` — 补充创业风格自评字段
- `docs/playtest_observation.md` — 补充 Alpha 1.9.1 专项观察字段（核心矛盾理解、竞品感知、洞察作用、危机处理、复盘清晰度）
- `README.md` — 版本文案统一为 Alpha 1.9.1
- `REPORTS.md` — 新增本记录
- `VERSION` — 1.9 → 1.9.1

**设计原则（本轮确认）**:
1. 真实性是地基，游戏性是房子。玩家玩的不是商业考试。
2. 复杂机制（PMF、回款、毛利、上市等）全部后台化，不直接压给玩家。
3. 每个新系统上线前必须回答：是否带来有趣选择？10秒能否理解？能否产生可复盘的故事？
4. 每阶段只引入 1-2 个新概念。
5. Alpha 2.0 轻量 PMF 只展示"客户验证：弱/中/强"和"PMF信号：未验证/初步验证/明确验证"，不做计算。

**下一步**: Alpha 1.9.1 真人试玩验证 → 反馈修复 → Alpha 2.0 轻量 PMF

**不包含**: 银行贷款、政府补贴、PMF详细系统、上市板块、财务报表、多赛道、Web、排行榜、真实LLM

---

## Alpha 1.9 — 真实内测反馈修复 (2026-05-17)

**来源**: 真实玩家试玩反馈 — 核心诉求是每回合更清晰地理解当前矛盾、竞品动态、决策有效性。

**设计原则**:
1. 不堆功能，只提升可理解性和张力
2. 每回合必须给玩家一个"经营判断"
3. 失败和拦截要变成学习点
4. 所有提示必须能被飞书和CLI看到
5. 不破坏 Alpha 1.8 融资估值、声誉、固定状态面板、飞书持久会话

**新增文件**:
- `src/core/conflict_engine.py` — 本月核心矛盾引擎（7种压力类型）
- `src/core/insight_engine.py` — 经营洞察引擎（8种洞察类别）
- `docs/playtest_feedback_log.md` — 内测反馈日志模板

**修改文件**:
- `src/core/models.py` — 新增 ConflictSummary、BusinessInsight、CrisisGuidance 模型；TurnResult 增加 conflict_summary/insight/stateguard_intercepted 字段
- `src/core/turn_engine.py` — 集成 ConflictEngine 和 InsightEngine；月度战报增加核心矛盾/竞品态势/经营洞察板块
- `src/core/state_guard.py` — 新增 generate_crisis_guidance() 函数（5种危机类型）
- `src/core/review_engine.py` — 支持 StateGuard 拦截关键转折点和经营洞察
- `app.py` — CLI 显示核心矛盾/经营洞察/危机解释；StateGuard 拦截追踪
- `feishu_play.py` — 飞书显示核心矛盾/经营洞察/危机解释；StateGuard 错误处理
- `scripts/playtest.py` — 输出增加核心矛盾摘要/洞察数量/危机解释次数/融资拒绝/StateGuard拦截
- `VERSION` — 1.8 → 1.9
- `README.md` — Alpha 1.9 功能说明
- `REPORTS.md` — 本记录

**新增测试**: test_conflict_engine.py, test_business_insights.py, test_crisis_explanations.py, test_competitor_visibility.py, test_review_stateguard_moments.py

**不包含的内容**:
- ❌ 真实LLM调用
- ❌ Web界面
- ❌ 排行榜系统
- ❌ 多赛道选择
- ❌ 新增复杂经营系统（供应链、定价策略等）

---

# Startup Sim — 版本开发报告

> 注意：历史阶段（Alpha 1.2/1.3/1.4/1.5/1.8）仅作版本记录，当前路线以最新 Alpha 1.9.1 规划为准。

## Alpha 1.8 — 试玩反馈修复 (2026-05-17)

**来源**: test1（天天）和 test2（CLI自动化）试玩反馈

**修复问题**:
1. 融资估值缺少逻辑 → 新增 fundraising_engine.py，按MRR/用户/产品/声誉/现金流可支撑时间计算合理估值区间
2. 声誉作用不明显 → 接入4系统：融资估值修正/CAC修正/团队士气加成/营销声誉衰减
3. 状态面板指标不固定 → 新增 status_formatter.py，14项核心指标始终显示
4. 董事会/市场反馈随机缺失 → _format_result() 改为强制每回合输出，空值时填默认文案
5. StateGuard拦截后无方向 → 拦截错误增强为2-3条可复制替代输入

**新增文件**: fundraising_engine.py, status_formatter.py
**新增测试**: test_fundraising_engine.py, test_reputation_effects.py, test_status_formatter.py, test_feedback_visibility.py, test_stateguard_suggestions.py
**测试总数**: 337
**make check**: ✅ 全部通过

---

Alpha 1.2 主流程已完成，剩余仅为文案和格式收尾。

## 1. 修改了哪些文件

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `src/core/ending_evaluator.py` | 修改 | SERIES_A 产品分阈值 70→65 |
| `tests/test_balance_simulation.py` | 修改 | fundraise_then_growth 策略：产品研发月数 4→5 |
| `scripts/playtest.py` | 修改 | fundraise_then_growth 策略：产品研发月数 4→5 |
| `tests/test_supplementary.py` | 新增 | 26 个补充测试 |
| `README.md` | 修改 | 更新至 Alpha 1.2，修正现金限制描述与 StateGuard 一致 |
| `src/core/state_guard.py` | 修改 | 错误提示改为显示可用现金=当前现金+融资到账，移除误导性"先融资后下回合再投入" |
| `REPORTS.md` | 新增/更新 | 本报告 |
| `VERSION` | 修改 | 1.1 → 1.2 |

## 2. Playtest 五种策略最终结果

```
策略         | 结局                     | 回合 | 现金   | MRR    | 产品 | 用户   | 股权
全研发        | survived_but_average   | 月12 | 0万    | 18万   | 92  | 70    | 100%
全营销        | slow_death             | 月12 | 0万    | 5万    | 31  | 251   | 100%
先融资再增长   | series_a_success       | 月12 | 318万  | 101万  | 86  | 1070  | 90%
保守现金流     | survived_but_average   | 月12 | 0万    | 18万   | 100 | 160   | 100%
均衡          | series_a_success       | 月12 | 105万  | 39万   | 81  | 409   | 92%
```

**结局分布：3 种 → survived_but_average, slow_death, series_a_success**

✅ 平衡验证通过：≥3 种结局，不存在无脑获胜策略。

## 3. 哪些参数被调整（旧→新）

### Alpha 1.2 之前的调整（commit d05fec9）

| 文件 | 参数 | 旧值 | 新值 |
|------|------|------|------|
| models.py | Default monthly_burn | 180,000 | 120,000 |
| turn_engine.py | Product gain 除数 | 100k/5/20 | 80k/3/10 |
| turn_engine.py | Dev burn increase | budget // 20 | budget // 30 |
| turn_engine.py | Marketing burn increase | budget // 8 | budget // 12 |
| turn_engine.py | Team burn increase | budget // 3 | budget // 5 |
| turn_engine.py | Organic product learning | None | +1/turn (≥5 employees) |
| ending_evaluator.py | Series A MRR threshold | 500,000 | 300,000 |
| ending_evaluator.py | Survived MRR threshold | 200,000 | 100,000 |
| customers.py | CAC | 1,000 | 800 |
| playtest.py | 各策略预算 | 旧值 | 上调 |

### 本次 Alpha 1.2 收尾调整

| 文件 | 参数 | 旧值 | 新值 |
|------|------|------|------|
| ending_evaluator.py | Series A Product threshold | 70 | 65 |
| test_balance_simulation.py | fundraise_then_growth 产品月数 | 4 | 5 |
| playtest.py | fundraise_then_growth 产品月数 | 4 | 5 |
| state_guard.py | 预算超限错误提示 | "先融资后下回合再投入" | "超过当前现金X万+本回合融资到账Y万" |
| README.md | 现金限制描述 | "不能超过回合开始时现金" | "可用现金=当前现金+本回合融资到账，融资流入不受65%限制" |

### StateGuard 与 README 一致性校验 ✅

- StateGuard 规则：`total_budget <= cash + fundraising_inflow`（当前现金+本回合融资到账作为可用现金）
- README 描述：与 StateGuard 规则一致
- 错误提示：不再误导玩家"先融资后下回合再投入"，改为正确提示
- 融资现金流入不受 65% 现金变化限制（sanitize_delta 中 fundraising_cash 豁免）

## 4. 当前是否存在无脑最优策略

**不存在。** 分析如下：

- **全研发**：产品分很高（92）但 MRR 极低（18万），勉强存活。缺乏营销和融资，无法变现。
- **全营销**：慢性死亡。没有产品基础，用户留存率低（产品分31），MRR仅5万。
- **先融资再增长**：A轮成功。先大量融资（500万/10%），再集中研发产品，最后发力营销。产品86+MRR101万。这是"正确"策略但需要精准的资源分配。
- **保守现金流**：勉强存活。极低投入导致MRR仅18万，虽活下来但未达增长预期。
- **均衡**：A轮成功。小融资（200万/8%）+ 交替研发/营销，产品81+MRR39万。

2个策略能A轮成功（先融资再增长、均衡），3个策略无法达成最优结局。不存在单一策略永远获胜的情况。玩家需要根据市场反馈调整策略。

### 五种策略取舍验证 ✅

| 策略 | 设计目标 | 实际验证 |
|------|----------|----------|
| 全研发 | 产品强但现金压力大 | ✅ 产品92/用户仅70/现金趋零 |
| 全营销 | 增长快但产品差时不稳定 | ✅ 用户251/产品31/slow_death |
| 先融资再增长 | 现金足但股权下降 | ✅ 现金318万/股权90% |
| 保守现金流 | 不容易死但难拿好结局 | ✅ 产品100/存活但无A轮 |
| 均衡 | 稳定但不能100%无脑必赢 | ✅ A轮成功/MRR不如融资策略 |

## 5. 当前是否建议进入 Alpha 1.3

**建议进入 Alpha 1.3。** 理由：

✅ 数值平衡已完成 — 5种策略产生3种不同结局，无单一最优解
✅ 测试覆盖充分 — 129个测试全部通过，覆盖核心流程
✅ 核心游戏循环完整 — 12回合可玩，系统完整
✅ StateGuard 与 README 规则一致 — 错误提示不再误导
✅ 无需本次收尾阶段做任何数值调参 — 平衡良好

Alpha 1.3 建议方向：
- 接入真实 LLM 进行自然语言解析（替代规则解析器）
- 扩展游戏回合数或增加更多随机事件
- 增加更多竞品策略变化
- 真人试玩反馈收集

## 6. 下一步建议

1. **Alpha 1.3 核心目标**：替换 action_parser.py 为 LLM-backed 智能解析
2. **中期增强**：
   - 添加更多结局条件（IPO、被收购等）
   - 增加行业赛道选择（不只AI客服SaaS）
   - 多人模式或排行榜
3. **测试增强**：增加模糊测试（随机策略验证不会崩溃）
4. **文档完善**：添加策略指南和FAQ

---

## 附录：收尾校验清单

| 校验项 | 状态 |
|--------|------|
| pytest 129 测试全部通过 | ✅ |
| playtest 5 种策略正常运行 | ✅ |
| 5 种策略都有清晰结果和结局 | ✅ |
| README 与 StateGuard 规则一致 | ✅ |
| StateGuard 错误提示不再误导玩家 | ✅ |
| 未新增大功能/LLM/Web/排行榜 | ✅ |
| Alpha 1.2 可作为内部平衡测试版 | ✅ |

---

# Startup Sim — Alpha 1.3 开发记录

## 1. 修改了哪些文件

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `src/core/events.py` | **新增** | 27个随机事件池（机会/危机/中性三类） |
| `src/core/event_engine.py` | 修改 | 集成随机事件池，保持原固定事件接口不变 |
| `src/agents/board.py` | 重写 | 董事会建议冲突增强 + `generate_board_minutes()` |
| `src/agents/competitors.py` | 重写 | 新增 `CompetitorState` + `periodic_action()` |
| `src/agents/__init__.py` | 修改 | 导出新增函数 `generate_board_minutes`、`get_competitor_summary` |
| `src/core/turn_engine.py` | 修改 | 竞品 periodic_action 集成 + `generate_monthly_report()` |
| `src/core/ending_evaluator.py` | 重写 | 玩家路径分类 + 结局叙事变体（25种变体） |
| `tests/test_endings.py` | 修改 | 新增路径分类测试、叙事变体确定性测试 |
| `README.md` | 修改 | 更新至 Alpha 1.3，添加新功能说明 |
| `REPORTS.md` | 修改 | 追加本记录 |
| `VERSION` | 修改 | 1.2 → 1.3 |

## 2. Playtest 五种策略最终结果（Alpha 1.3）

```
策略         | 结局                     | 回合 | 现金   | MRR    | 产品 | 用户   | 股权
全研发        | survived_but_average   | 月12 | 0万    | 18万   | 93  | 80    | 100%
全营销        | slow_death             | 月12 | 0万    | 4万    | 31  | 229   | 100%
先融资再增长   | series_a_success       | 月12 | 318万  | 101万  | 86  | 1055  | 90%
保守现金流     | survived_but_average   | 月12 | 0万    | 18万   | 100 | 160   | 100%
均衡          | series_a_success       | 月12 | 105万  | 39万   | 81  | 409   | 92%
```

**结局分布：3 种 → survived_but_average, slow_death, series_a_success** ✅

结局叙事变体生效：
- 全研发 → 【小而美】（研发派存活叙事）
- 全营销 → 【渐渐消失】（均衡派慢性死亡叙事）
- 先融资再增长 → 【产品信仰】（研发派A轮成功叙事）
- 均衡 → 【技术驱动】（研发派A轮成功叙事）

> ⚠️ **补充说明**：全研发策略（strategy_all_rnd）处于破产边缘——产品分高但MRR极低，现金趋零。在部分随机种子下（如遭遇负面事件组合），可能触发 bankruptcy。这是合理的平衡信号：策略选择存在真实风险，全研发不是无脑安全选项。**bankruptcy 不作为稳定结局统计**，当前稳定可复现结局为上述3种。

## 3. 新增事件池统计

| 类别 | 数量 | 示例 |
|------|------|------|
| 机会 (opportunity) | 10 | 大客户签约、媒体报道、技术洞察、政策利好、竞品失误 |
| 危机 (crisis) | 10 | 服务器宕机、员工离职、客户投诉、竞品挖角、数据安全传闻 |
| 中性 (neutral) | 7 | 行业大会、投资人引荐、团队内部分歧、市场传闻、收购意向 |

事件引擎接口：`sample_random_events(current, triggered, base_chance=0.20)`
- 每回合~20%概率触发一个随机事件
- ~2.4个/12回合
- 与原有3个固定事件共存，不破坏现有接口

## 4. 董事会冲突检测规则

| 冲突条件 | CFO立场 | 对立方立场 |
|----------|---------|-----------|
| 可支撑<6月且做研发 | 控制烧钱 | CTO坚持研发投入 |
| 现金<50万且做营销 | 现金流紧张 | COO认为需投营销获客 |
| 可支撑<4月未融资 | 建议融资保命 | 投资方担心条款不利 |
| 产品<40且MRR<10万 | — | CTO先产品 vs 投资方先增长 |

董事会会议记录通过 `generate_board_minutes()` 输出，包含：
- 公司现状快照
- 本回合行动
- 董事发言
- 分歧焦点（自动检测）

## 5. 竞品状态系统

| 竞品 | 初始产品分 | 初始市场份额 | 周期性行为 |
|------|-----------|-------------|-----------|
| 快答科技 | 25 | 15% | 每2回合+1产品分，每4回合降价抢市场 |
| 灵犀客服云 | 35 | 12% | 每2回合+1产品分，每5回合发布企业功能 |

竞品行为写入月度战报 `get_competitor_summary()`。

## 6. 月度战报板块

`generate_monthly_report(result, state_before, state_after)` 输出：
1. 📈 本月关键变化（9项指标前后对比）
2. 🏛️ 董事会争议（分歧焦点提取）
3. 🎯 竞品动作（含竞品状态）
4. 💬 客户反馈
5. ⚠️ 风险提醒（7种风险条件检测）
6. 💡 下月建议（最多5条）

CLI和飞书共用此函数。

## 7. 结局叙事变体

5种结局 × 5种玩家路径（研发派/营销派/融资派/均衡派/保守派）

每种结局至少一个路径有2-3种文案变体，总计25种变体。

路径分类规则：
- 保守派：可支撑>9月 且 产品<60 且 用户<200
- 融资派：股权<50%
- 研发派：产品≥70
- 营销派：用户≥500 且 MRR≥20万
- 均衡派：其余情况

## 8. Alpha 1.3 验收标准

| 验证项 | 状态 |
|--------|------|
| 无无脑最优策略 | ✅ 单一策略无法保证获胜 |
| 无绝对必死策略 | ✅ 所有策略均有存活路径 |
| 策略差异明显 | ✅ 5策略→3种结局，路径分化 |
| 全研发存在现金流压力 | ✅ 产品高但MRR低，破产边缘 |
| 融资和均衡路线可稳定成功 | ✅ series_a_success 可复现 |
| 全营销无法无脑获胜 | ✅ 产品分低下 slow_death |
| pytest 136 测试全部通过 | ✅ |
| playtest 5 策略正常运行 | ✅ |
| 随机事件不影响平衡 | ✅ (delta ≤±3产品/±5士气/±2市场份额) |
| 竞品 periodic_action 不破坏平衡 | ✅ |
| 无新增 Web/排行榜/LLM | ✅ |

## 9. 不包含的内容

- ❌ Web界面
- ❌ 排行榜系统
- ❌ 多赛道选择
- ❌ 真实LLM调用
- ❌ 大规模重构
- ❌ 新结局类型

---

*Alpha 1.3 游戏体验增强版 — 2026-05-17*

---

# Startup Sim — Alpha 1.4 开发记录

## 1. 修改了哪些文件

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `src/core/review_engine.py` | **新增** | ReviewEngine：复盘报告生成 + 创始人画像 + 策略评分 + 关键转折点 + 结局解释 |
| `src/core/models.py` | 修改 | 新增 FounderProfile / StrategyScore / KeyMoment / GameReview 四个 Pydantic 模型 |
| `src/db/repository.py` | 修改 | 新增 list_snapshots / list_actions / list_events 三个历史查询函数 |
| `app.py` | 修改 | CLI 结局复盘输出（print_review 函数） |
| `feishu_play.py` | 修改 | 飞书简版复盘输出（_format_review_short 函数） |
| `scripts/playtest.py` | 修改 | 每种策略结束后输出复盘摘要（结局标题/创始人画像/综合评分/转折点数） |
| `tests/test_review_engine.py` | **新增** | 25 个测试覆盖复盘系统 |
| `README.md` | 修改 | 更新至 Alpha 1.4，添加新功能说明 |
| `REPORTS.md` | 修改 | 追加本记录 |
| `VERSION` | 修改 | 1.3 → 1.4 |

## 2. Playtest 五种策略复盘摘要（Alpha 1.4）

```
策略         | 结局                    | 创始人画像    | 综合评分 | 关键转折点
全研发        | survived_but_average   | 技术极客     | 50      | 8个
全营销        | slow_death             | 混乱求生者   | 33      | 8个
先融资再增长   | series_a_success       | 技术极客     | 100     | 5个
保守现金流     | survived_but_average   | 技术极客     | 55      | 8个
均衡          | series_a_success       | 技术极客     | 100     | 3个
```

**结局分布：3 种 → survived_but_average, slow_death, series_a_success** ✅

策略评分差异显著：A轮成功策略评分远高于失败的（100 vs 33-55），且关键转折点能捕捉到不同策略的关键事件。

## 3. 新增核心模块：ReviewEngine

### 创始人画像分类（6种）
- **tech_visionary**（技术极客）：产品分≥70，A轮或存活
- **growth_hacker**（增长黑客）：用户≥500，MRR≥20万
- **capital_player**（资本玩家）：股权<80%，估值>2000万
- **conservative_operator**（保守派操盘手）：可支撑>9月，产品<60，用户<200
- **balanced_leader**（均衡型CEO）：中等指标，A轮或均衡
- **chaotic_survivor**（混乱求生者）：无明显特征

### 策略评分（0-100）
- product_score：产品分直接映射
- growth_score：MRR + 用户数组合
- finance_score：现金管理 + 融资效率
- control_score：股权保留比例
- risk_score：现金流可支撑时间健康度
- overall_score：加权平均（A轮+10，破产-15）

### 关键转折点识别
- 现金跌破10万/1万
- 产品分突破70
- MRR超过30万/50万/100万
- 股权跌破80%/50%
- 现金流可支撑时间低于3个月
- 重大事件触发

### 结局解释增强
- series_a_success：技术驱动/增长为王/资本杠杆/稳健制胜
- survived_but_average：小而美/增长不足/现金流守成/技术孤岛
- slow_death：营销泡沫/产品不足/错失融资窗口/方向迷失
- bankruptcy：烧钱自焚/研发生不逢时/现金断裂
- founder_removed：出局

## 4. Alpha 1.4 验收标准

| 验证项 | 状态 |
|--------|------|
| pytest 161 测试全部通过 | ✅ |
| playtest 5 策略正常运行并输出复盘 | ✅ |
| 每种结局有对应文案 | ✅ |
| 创始人画像随策略变化 | ✅ |
| 策略评分0-100 | ✅ |
| key_moments ≥ 1个 | ✅ |
| CLI 结局时输出复盘 | ✅ |
| 飞书结局时输出复盘 | ✅ |
| 不接 LLM | ✅ |
| 不做 Web/排行榜 | ✅ |
| 不破坏 Alpha 1.3 数值平衡 | ✅ |

## 5. 不包含的内容

- ❌ 真实LLM调用
- ❌ Web界面
- ❌ 排行榜系统
- ❌ 多赛道选择
- ❌ 新结局类型
- ❌ 数值参数调整

## 6. 是否建议进入 Alpha 1.5

**建议进入 Alpha 1.5。** 理由：

✅ 复盘系统为核心循环闭环：玩家 → 决策 → 结局 → 复盘 → 下次改进
✅ 创始���画像和策略评分为玩家提供有意义的反馈
✅ 测试覆盖充分（161个），不破坏原有平衡
✅ CLI和飞书双端可用
✅ 复盘系统为未来功能（存档比较、策略建议、成就系统）预留了扩展点

Alpha 1.5 建议方向：
- 真人试玩反馈收集
- 回放系统（按月重播决策细节）
- 策略对比（对比两次游戏的评分差异）
- 成就徽章系统

---

*Alpha 1.4 复盘系统增强版 — 2026-05-17*

---

# Startup Sim — Alpha 1.5 开发记录

## 1. 修改了哪些文件

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `src/core/replay_engine.py` | **新增** | ReplayEngine：12个月叙事回放时间线 + 高潮月识别 + 标签生成 |
| `src/core/achievement_engine.py` | **新增** | AchievementEngine：15个成就徽章，4种稀有度 |
| `src/core/strategy_compare.py` | **新增** | StrategyCompare：多策略对比 + 各维度排名 |
| `src/core/models.py` | 修改 | 新增 ReplayMonth/GameReplay/Achievement/AchievementResult/StrategyComparison 五个 Pydantic 模型 |
| `app.py` | 修改 | CLI 增加回放(5关键月)和成就徽章输出 |
| `feishu_play.py` | 修改 | 飞书精简版回放(2-3关键月)+成就(前3个) |
| `scripts/playtest.py` | 修改 | 策略对比排名表输出 |
| `tests/test_replay_engine.py` | **新增** | 18个回放测试 |
| `tests/test_achievement_engine.py` | **新增** | 21个成就测试 |
| `tests/test_strategy_compare.py` | **新增** | 17个策略对比测试 |
| `README.md` | 修改 | 更新至 Alpha 1.5，添加新功能说明 |
| `REPORTS.md` | 修改 | 追加本记录 |
| `VERSION` | 修改 | 1.4 → 1.5 |

## 2. Playtest 五种策略结果（Alpha 1.5）

```
策略         | 结局                     | 回合 | 现金   | MRR    | 产品 | 用户   | 股权
全研发        | survived_but_average   | 月12 | 0万    | 18万   | 93  | 80    | 100%
全营销        | slow_death             | 月12 | 0万    | 4万    | 31  | 229   | 100%
先融资再增长   | series_a_success       | 月12 | 318万  | 101万  | 86  | 1055  | 90%
保守现金流     | survived_but_average   | 月12 | 0万    | 18万   | 100 | 160   | 100%
均衡          | series_a_success       | 月12 | 105万  | 39万   | 81  | 409   | 92%
```

**结局分布：3 种 → survived_but_average, slow_death, series_a_success** ✅

策略对比排名（综合评分）：
1. 先融资再增长（100）
2. 均衡（100）
3. 保守现金流（55）
4. 全研发（50）
5. 全营销（33）

## 3. 新增核心模块

### ReplayEngine（回放系统）
- 12月每月叙事标题（_MONTH_THEMES）+ 风险等级 + 指标变化
- 自动识别高潮月（最早的高/关键风险月，或MRR高峰月，或最低现金月）
- 生成最多4个回放标签（A轮赢家/技术信仰/增长神话/极致产品/惊险刺激/稳健经营/控制力MAX/闪电增长/燃烧殆尽/温水青蛙）
- 5种结局各对应不同回放标题和结局叙事

### AchievementEngine（成就系统）
15个成就，4种稀有度：
- **Common (7)**：产品信仰者、增长机器、A轮赢家、死里逃生、现金守门员、控制权大师、稀释换增长
- **Rare (5)**：慢性死亡、研发陷阱、营销泡沫、小而美、资本玩家
- **Epic (2)**：危机处理者、稳健经营者
- **Legendary (1)**：传奇创始人（A轮+产品85+用户1000+股权80%）

### StrategyCompare（策略对比）
- 输入多个 GameReview → 输出 StrategyComparison
- 排名：综合最优/产品最强/增长最快/财务最佳/控制最稳/风控最弱
- 返回排序的 summary_table + conclusion

## 4. Alpha 1.5 验收标准

| 验证项 | 状态 |
|--------|------|
| pytest 217 测试全部通过 | ✅ |
| playtest 5 策略正常运行并输出对比 | ✅ |
| ReplayEngine 生成完整12月回放 | ✅ |
| AchievementEngine 评估15个成就 | ✅ |
| StrategyCompare 正确排名 | ✅ |
| CLI 结局时输出回放+成就 | ✅ |
| 飞书结局时输出回放+成就 | ✅ |
| 不接 LLM | ✅ |
| 不做 Web/排行榜 | ✅ |
| 不破坏 Alpha 1.4 数值平衡 | ✅ |

## 5. 不包含的内容

- ❌ 真实LLM调用
- ❌ Web界面
- ❌ 排行榜系统
- ❌ 多赛道选择
- ❌ 新结局类型
- ❌ 数值参数调整

---

*Alpha 1.5 回放/成就/策略对比版 — 2026-05-17*

## Alpha 1.6 新手引导 + 输入建议 + 试玩体验打磨 — 2026-05-17

## 1. 新增模块

| 文件 | 行数 | 说明 |
|------|------|------|
| `src/core/tutorial.py` | ~150 | TutorialEngine：4步新手引导 + 6种阈值提示 |
| `src/core/suggestion_engine.py` | ~200 | SuggestionEngine：3条建议(稳健/激进/风险) + 聚焦方向 |
| `src/core/state_explainer.py` | ~170 | StateExplainer：5维状态人话解读 |
| `src/core/models.py` | +16 | TutorialStep/TutorialHint/ActionSuggestion/SuggestionResult |

## 2. 修改文件

| 文件 | 修改说明 |
|------|----------|
| `app.py` | 导入新模块 → display_state集成StateExplainer → 新手引导显示 → 每回合建议 → help命令 |
| `feishu_play.py` | 导入新模块 → 新开局引导 → help命令路由 → 每回合简版建议 → status建议 |
| `src/core/state_guard.py` | 增强错误信息：结构化中文(❌错误💡解决方法📝示例) |
| `VERSION` | 1.5 → 1.6 |
| `README.md` | Alpha 1.6功能说明、项目结构更新、测试数273 |
| `REPORTS.md` | 本记录 |

## 3. 新增测试

| 文件 | 测试数 | 覆盖范围 |
|------|--------|----------|
| `tests/test_suggestion_engine.py` | 17 | 低现金建议/高产品低MRR建议/低产品高营销建议/example_input可解析性/边界情况 |
| `tests/test_tutorial.py` | 18 | 4步引导完整性/现金流提示触发阈值/股权提示/提示不重复/不改数值 |
| `tests/test_state_explainer.py` | 21 | 现金/产品/MRR用户关系/股权/士气/全维度解读 |

## 4. 关键设计决策

- **纯函数无副作用**：TutorialEngine/SuggestionEngine/StateExplainer均为静态方法，不修改任何游戏状态
- **建议可执行**：所有 example_input 必须能被 parse_multi 解析（已验证）
- **不强制操作**：引导和建议均为提示性质，不限制玩家决策自由
- **不改变数值**：不调整任何游戏平衡参数
- **保持兼容**：不破坏 Alpha 1.4/1.5 的复盘/回放/成就/策略对比

## 5. 验收标准

| 验证项 | 状态 |
|--------|------|
| pytest 273 测试全部通过 | ✅ |
| playtest 5 策略正常运行 | ✅ |
| 3个新模块测试全覆盖 | ✅ |
| 建议 example_input 可解析 | ✅ |
| StateGuard 错误信息结构化中文 | ✅ |
| CLI help 命令输出完整 | ✅ |
| 飞书 help 命令输出精简 | ✅ |
| 不接 LLM | ✅ |
| 不做 Web/排行榜 | ✅ |
| 不破坏 Alpha 1.5 数值平衡 | ✅ |

## 6. 不包含的内容

- ❌ 真实LLM调用
- ❌ Web界面
- ❌ 排行榜系统
- ❌ 多赛道选择
- ❌ 数值参数调整
- ❌ 新结局类型
- ❌ 强制教程（不限制玩家操作）

---

*Alpha 1.6 新手引导 + 建议引擎 + 状态解读版 — 2026-05-17*

---

## Alpha 1.6 工程规范更新 — 文档一致性规范接入

主题：文档一致性规范接入工程质量门

内容：
- CONTRIBUTING 新增"文档一致性规范"章节（7条规则）
- release checklist 新增"文档一致性检查"章节（10个勾选项）
- 新增 `scripts/check_docs_consistency.py`：自动检查 VERSION 与 README 标题一致、旧版本残留、测试数量、事件池统计
- Makefile 新增 `make docs-check` target
- `.github/workflows/ci.yml` 新增 docs-check 步骤
- `make check` 现在覆盖格式、lint、测试、playtest、文档一致性五项
- 后续每次版本推进，`make check` 必须全部通过（含 docs-check）

---

## Alpha 1.7 首次玩家试玩验证版

主题：面向非开发者的首次试玩体验优化

内容：
- 新增 `QUICKSTART.md`：面向普通试玩者的3分钟启动指南（不涉及开发工具）
- 新增 `examples/sample_run_balanced.md`：均衡策略→A轮成功样例局（12个月决策/指标/成就/学习点）
- 新增 `examples/sample_run_marketing_failure.md`：全营销→慢性死亡失败样例（含失败原因分析和教训总结）
- 新增 `docs/playtest_feedback_template.md`：6个问题的玩家试玩反馈模板
- 新增 `docs/playtest_observation.md`：试玩观察记录模板（含操作统计和观察笔记）
- 新增 `docs/troubleshooting.md`：按"症状→解决方法"格式覆盖环境安装/游戏启动/开发工具/Git 问题
- 新增 `scripts/start_demo.py`：启动前检查脚本（Python版本/依赖/目录检查 + 推荐启动命令 + 第一回合建议）
- CLI `app.py` help 增加快速导航（QUICKSTART / examples / troubleshooting）
- 飞书 `feishu_play.py` help 增加快速导航
- README 更新至 Alpha 1.7，新增快速导航区块、项目结构更新
- VERSION 更新至 1.7
- 新增 `tests/test_docs_and_demo.py`：文档存在性检查 + start_demo.py 可运行验证 + VERSION 一致性

状态：适合小范围内部试玩，不适合公开发布

## Alpha 1.7 Hotfix — 飞书会话持久化 (2026-05-17)

**根因**：`feishu_play.py` 使用进程内 `_session_map = {}` 字典做 user_id→session_id 映射，进程重启或不同 handler 调用间映射丢失，导致玩家每回合找不到上一回合 session。

**方案**：删除内存字典，改用 SQLite `external_sessions` 表存持久化绑定。

**修改**：
- `src/db/schema.sql` — 新增 `external_sessions` 表（source + external_user_id 联合主键）
- `src/db/connection.py` — `get_connection()` 改为动态读取 `config.DB_PATH`（修复测试隔离）
- `src/db/repository.py` — 新增 5 个 external session 方法 + `update_session_month` 补 commit
- `feishu_play.py` — 删除 `_session_map`，全部改用 DB 查询；新增 `extract_feishu_identity()`、「重新开始」命令、「会话」诊断命令；debug 日志写入 `logs/feishu_session.log`
- `tests/test_feishu_session_persistence.py` — 新增 15 个测试用例（创建/复用/递增/重启恢复/多用户隔离/诊断）
- `tests/test_p0_unified.py` — 适配新 API（`_session_map` → repository 方法）
- `README.md` — 飞书会话说明
- `REPORTS.md` — 本 hotfix 记录

**命令新行为**：
- 「开始」：已有 active session 时提示进度，不覆盖
- 「重新开始」：删除旧绑定，创建新 session
- 「状态」：只读，不创建新 session
- 「会话」/「session」/「debug session」：返回 external_user_id / session_id / 月份 / 状态 / 绑定时间
- 普通决策：通过 external_user_id 找回 session，进程重启后自动恢复

**测试结果**：305 passed，make check 全部通过。VERSION 不变（hotfix）。

---

## Frontend Alpha 0.2 桌面游戏层推进 — 办公室事件气泡 (2026-05-18)

主题：把董事会、竞品、经营洞察转成办公室内可见事件。

内容：
- 新增 `buildOfficeEventBubbles()`，由游戏内容数据层生成办公室事件气泡。
- 办公室场景现在显示董事会、竞品、经营洞察三类事件提示。
- 董事会和竞品事件气泡可点击，分别打开右侧董事会/竞品面板。
- 前端测试扩展到 16 个用例，覆盖事件气泡生成与界面跳转。

状态：第三轮完成，下一轮推进更游戏化的月度战报。

---

## Frontend Alpha 0.2 桌面游戏层推进 — 月度战报行动化 (2026-05-18)

主题：让回合结算像游戏月报，而不是普通状态日志。

内容：
- 新增 `buildMonthlyReport()`，由玩法数据层生成月报标题、高光卡、复盘线索、下月压力和补救行动。
- 左侧月度战报新增一句式结论，例如“产品有进展，但现金在承压”。
- 月报补救行动可直接写入 CEO 指令，进入统一的已准备行动预览。
- 前端测试扩展到 17 个用例，覆盖月报数据生成和补救行动采用流程。

状态：第四轮完成，下一轮推进场景元数据种子。

---

## Frontend Alpha 0.2 桌面游戏层推进 — 场景元数据种子 (2026-05-18)

主题：为后续独立游戏化、多剧本和内容包扩展预留边界。

内容：
- 新增 `frontend/src/game/scenarios.ts`，定义内置 AI SaaS 初创公司场景。
- 场景元数据包含起始公司、五个办公室房间、董事角色、竞品、市场标签和内容包能力。
- 明确 `rulesAuthority: "backend-turn-engine"`，前端场景只描述内容，不接管数值结算。
- 前端测试扩展到 19 个用例，覆盖场景种子和内置场景目录。

状态：第五轮完成，下一轮推进 PixiJS 懒加载边界。

---

## Frontend Alpha 0.2 桌面游戏层推进 — PixiJS 懒加载边界 (2026-05-18)

主题：把可选画布层从 React 办公室组件中拆出去。

内容：
- 新增 `frontend/src/game/pixiOverlay.ts`，集中管理 PixiJS 动态导入、canvas 挂载和清理。
- `OfficeStage.tsx` 不再直接拥有 Pixi 初始化逻辑，只负责办公室交互和 React 热区。
- 新增 `frontend/src/game/pixiOverlay.test.ts`，验证测试环境下可选画布层保持惰性且可安全清理。
- 前端测试扩展到 20 个用例。

备注：生产构建中 Pixi 异步 chunk 仍超过 Vite 默认 500KB 提示线。当前已完成边界隔离，后续发行优化再决定轻量 renderer、进一步 tree-shaking 或调整发布 chunk 预算。

状态：第六轮完成。

---

## Frontend Alpha 0.2 桌面可玩性闭环 — 办公室交互强化 (2026-05-18)

主题：让办公室主界面更像经营游戏的操作场，而不是普通信息面板。

内容：
- 当前房间面板改为“办公室操作台”，并使用“选中房间”强化玩家正在操作的空间感。
- 活跃房间热点增加更明显的描边和层次，桌面视口下更容易识别当前选择。
- 办公室事件气泡压缩为“标题 + 类型”，详细内容保留为悬停提示，减少遮挡。
- 前端测试继续覆盖禁用“跑道/Runway”、办公室事件和房间操作路径。

状态：桌面可玩性闭环第 1 轮完成。

---

## Frontend Alpha 0.2 桌面可玩性闭环 — 董事会 NPC 角色面 (2026-05-18)

主题：让董事会从消息列表升级为有立场和压力变化的角色反馈。

内容：
- 新增 `buildBoardNpcProfiles()`，根据董事成员、现金流可支撑时间、产品变化和用户变化生成角色资料。
- 董事会面板展示固定立场、信任趋势和压力标签，例如“现金纪律 / 信任稳定 / 持续观察”。
- App 层移除临时 stance 判断，改为消费玩法数据层的董事会角色资料。
- 前端测试扩展到 21 个用例，覆盖董事会 NPC profile 数据和界面展示。

状态：桌面可玩性闭环第 2 轮完成。

---

## Frontend Alpha 0.2 桌面可玩性闭环 — 竞品动态系统面 (2026-05-18)

主题：让竞品反馈从静态状态变成可理解的市场动作。

内容：
- 新增 `buildCompetitorMoves()`，把竞品状态和趋势翻译为“功能升级 / 渠道抢量 / 价格压力 / 客户绑定 / 暂无大动作”。
- 竞品摘要和竞品面板展示动作类型、原因和可执行回应指令。
- 竞品动态仍然只做描述和指令准备，不接管任何数值结算。
- 前端测试扩展到 22 个用例，覆盖竞品动作生成和界面展示。

状态：桌面可玩性闭环第 3 轮完成。

---

## Frontend Alpha 0.2 桌面可玩性闭环 — 回合结算节奏 (2026-05-18)

主题：让每次执行回合都有清晰的结算顺序。

内容：
- 新增 `buildTurnResolutionSteps()`，生成“执行指令 → 月末变化 → 战报复盘”三步反馈。
- App 记录上一回合 CEO 指令，提交后在月度战报里展示回合结算时间线。
- 时间线复用月末高光和月报结论，不暴露公式和专业指标。
- 前端测试扩展到 23 个用例，覆盖结算步骤生成和界面展示。

状态：桌面可玩性闭环第 4 轮完成。

---

## Frontend Alpha 0.2 桌面可玩性闭环 — 场景选择入口 (2026-05-18)

主题：为后续多剧本和独立游戏内容包预留玩家入口。

内容：
- `ai-saas-seed` 场景新增菜单展示元数据：标题、副标题、难度、状态和特性标签。
- 左侧面板新增“当前剧本”入口，显示 AI SaaS 初创公司的当前可玩状态。
- 当前入口只展示内置剧本，不引入新结算规则，不改变 TurnEngine 权威边界。
- 前端测试扩展到 24 个用例，覆盖场景菜单数据和界面入口。

状态：桌面可玩性闭环第 5 轮完成。

---

## Frontend Alpha 0.2 桌面可玩性闭环 — 生产验收抛光 (2026-05-18)

主题：把当前桌面可玩体验固化为前端生产验收标准。

内容：
- Playwright 主流程新增当前剧本、办公室操作台和回合结算断言。
- Vercel 部署文档更新生产 smoke 标准，明确检查“当前剧本”“办公室操作台”“月度战报”和“回合结算”。
- 继续要求生产页面使用“现金流可支撑时间”，不得出现“跑道”或 “Runway”。

状态：桌面可玩性闭环第 6 轮完成。

---

## Alpha 0.5 十轮推进 — 结算事实驱动的桌面经营闭环 (2026-05-18)

主题：把 `TurnFacts` 继续向角色记忆、办公室信号、月度事件和桌面降噪推进，形成 Alpha 0.5 的可玩闭环底座。

内容：
- 第 1 轮：后端 `POST /api/sessions/{session_id}/turns` 新增 `turn.role_memory`，由 settled `TurnFacts` 和董事会反馈派生，不从前端 hover、预览或未执行命令生成。
- 第 2 轮：前端董事会 NPC 优先消费后端 `role_memory`，缺失时才使用原 deterministic fallback，角色记忆不再只是前端猜测。
- 第 3 轮：后端新增 `turn.office_signals`，把核心矛盾和经营洞察转换为 renderer-neutral 办公室房间信号。
- 第 4 轮：前端办公室场景优先使用后端 `office_signals`，并以紧凑信号条和房间状态展示，不新增大面板。
- 第 5 轮：房间 id 对齐现有办公室空间：`product`、`team`、`sales`、`board`、`servers`，避免前端渲染不存在的房间。
- 第 6 轮：后端新增 `turn.story_events`，从规则事件、竞品事实或经营洞察生成紧凑月度事件。
- 第 7 轮：前端月度战报新增“本月事件”区，只展示少量可复盘事件，保持游戏性反馈而不是日志堆叠。
- 第 8 轮：`frontend/src/types.ts`、store 和 API fallback 测试同步扩展新契约，兼容 nested turn 字段和 top-level fallback 字段。
- 第 9 轮：`docs/frontend_api_contract.md` 和 `docs/gameplay_contracts.md` 同步补充 `RoleMemory`、`OfficeSignal`、`StoryEvent` 边界。
- 第 10 轮：本轮保持 TurnEngine 数值结算不变，所有新增层都是事实展示、角色反馈和月报表现层。

状态：Alpha 0.5 第一组十轮推进完成，下一步进入完整验证、Vercel smoke 和发布硬化。

---

## Alpha 0.5 十轮推进 — 持久记忆与轻量复盘闭环 (2026-05-18)

主题：把上一组 settled 事实反馈从“本回合展示”推进到“可持续记忆 + 可打开复盘”，让桌面经营局更像一段能被回看和复盘的游戏过程。

内容：
- 第 1 轮：新增 SQLite `role_memory_history` 表，用于保存每回合结算后生成的角色记忆事实。
- 第 2 轮：`src/db/repository.py` 新增角色记忆保存、最近记忆读取和重开清理逻辑，保持记忆来源为 settled turn facts。
- 第 3 轮：`POST /api/sessions/{session_id}/turns` 在回合结算后写入 `role_memory_history`，不改变 TurnEngine 数值结算。
- 第 4 轮：同一回合响应新增 `turn.memory_history` 和 `turn.recent_role_memory`，前端可直接消费最近记忆。
- 第 5 轮：前端类型、store 和 API 测试同步扩展角色记忆历史契约，兼容 nested turn 字段和 top-level fallback 字段。
- 第 6 轮：董事会 NPC 只展示当前最相关的一条角色记忆，避免多个历史事实堆叠到界面里。
- 第 7 轮：新增只读 `GET /api/sessions/{session_id}/review`，包装现有 `ReviewEngine` 与 `AchievementEngine`，不推进月份、不修改状态。
- 第 8 轮：前端新增 `loadReview()` 和 `openReview()`，把复盘作为按需入口，而不是默认铺满页面。
- 第 9 轮：月度战报新增紧凑“轻量复盘”入口，展示标题、摘要、一个关键时刻和下局建议。
- 第 10 轮：`docs/frontend_api_contract.md` 与 `docs/gameplay_contracts.md` 同步补充持久记忆、复盘接口和表现层边界。

状态：Alpha 0.5 第二组十轮推进进入完整验证、发布检查和 CI/Vercel smoke。

---

## Alpha 0.5 十轮推进 — 复盘与成就内嵌闭环 (2026-05-18)

主题：把“轻量复盘”从单句摘要升级为桌面端可用的内嵌复盘/成就反馈，同时保持不跳页、不堆信息、不改变结算规则。

内容：
- 第 1 轮：`GET /api/sessions/{session_id}/review` 增加 `review_phase` 与 `status_copy`，让前端直接消费阶段/终局文案。
- 第 2 轮：复盘接口为 `key_moments` 增加 `display_title`、`display_description`、`display_tone`，保持原字段兼容。
- 第 3 轮：复盘接口新增 `achievement_cards`，只从已解锁成就派生展示卡片，不新增成就规则。
- 第 4 轮：复盘接口新增 `next_run_suggestions`，由 ReviewEngine 建议和最终现金、产品、用户事实生成 2-3 条短建议。
- 第 5 轮：后端测试覆盖 active 阶段复盘、已结束终局复盘、只读性、成就卡、关键节点 display 字段和禁用词。
- 第 6 轮：前端 `GameReviewResponse` 类型同步扩展复盘阶段、状态、成就卡与下局建议字段。
- 第 7 轮：月度战报内的“轻量复盘”展示升级为紧凑区域：标题、状态标签、摘要、关键时刻、成就徽章和短建议。
- 第 8 轮：成就和建议展示都限制最多 3 条，避免复盘区重新变成信息堆叠。
- 第 9 轮：前端测试覆盖复盘接口缺失时的兜底提示、成就/建议数量限制、后端阶段文案优先级和禁用词。
- 第 10 轮：`docs/frontend_api_contract.md` 与 `docs/gameplay_contracts.md` 同步补充复盘展示契约和只读边界。

状态：Alpha 0.5 第三组十轮推进进入完整验证、发布检查和 CI/Vercel smoke。

---

## Alpha 0.5 十轮推进 — 局内档案与复盘资产化 (2026-05-18)

主题：把复盘结果从“看一次的摘要”沉淀为局内可回看的档案资产，帮助玩家理解这一局为什么走到当前状态。

内容：
- 第 1 轮：`GET /api/sessions/{session_id}/review` 新增 `archive_summary`，作为档案面板的一句话局势记录。
- 第 2 轮：复盘接口新增 `archive_timeline`，从关键时刻、行动、事件和快照投影最多 5 条可回看事实。
- 第 3 轮：复盘接口新增 `archive_badges`，从已解锁成就投影最多 3 个档案徽章。
- 第 4 轮：后端档案投影保持只读，不推进月份、不修改状态、不改变 TurnEngine 结算。
- 第 5 轮：后端测试覆盖档案字段存在、长度上限、字段结构、只读性和禁用词。
- 第 6 轮：前端 `GameReviewResponse` 同步扩展档案摘要、时间线和徽章字段。
- 第 7 轮：右侧信息区用“档案”替代原“记录”，保持 4 个 tab，不增加额外拥挤入口。
- 第 8 轮：档案 tab 按需加载 review，展示局势摘要、最多 5 条时间线、最多 3 个徽章，并保留状态/估值记录。
- 第 9 轮：前端兼容后端暂未返回 `archive_*` 的情况，回退到 `ending_summary`、`key_moments` 和 `achievement_cards`。
- 第 10 轮：`docs/frontend_api_contract.md` 与 `docs/gameplay_contracts.md` 同步补充档案投影契约和只读边界。

状态：Alpha 0.5 第四组十轮推进进入完整验证、发布检查和 CI/Vercel smoke。

---

## Alpha 0.6 十轮推进 — 阶段目标与任务方向闭环 (2026-05-18)

主题：让玩家知道当前阶段要达成什么，同时避免系统替玩家生成完整 CEO 指令。

内容：
- 第 1 轮：`GameStateView` 新增 `phase_goals`，描述当前阶段目标、摘要和 2-3 个轻量目标。
- 第 2 轮：每个目标只提供 `action_directions` 和 `risk_hint`，不提供 `command`、`example_input` 或一键执行元数据。
- 第 3 轮：阶段目标覆盖产品成熟度、现金纪律和真实用户反馈三条早期创业主线。
- 第 4 轮：`POST /api/sessions/{session_id}/turns` 新增 `turn.objective_updates`，回合后只反馈目标进展。
- 第 5 轮：目标进展由 settled `TurnResult`、`StateDelta` 和 post-turn `CompanyState` 派生，不改变 TurnEngine。
- 第 6 轮：左侧新增“阶段目标”紧凑面板，展示方向标签和风险提醒，不放按钮。
- 第 7 轮：月度战报新增“目标进展”区，展示完成、推进中或承压的结果反馈。
- 第 8 轮：前端测试覆盖目标面板无按钮、无完整指令、无自动填入行为。
- 第 9 轮：后端测试覆盖目标契约无 executable command 字段，并继续检查禁用词。
- 第 10 轮：`docs/frontend_api_contract.md` 与 `docs/gameplay_contracts.md` 同步补充目标/任务非执行契约。

状态：Alpha 0.6 第一组十轮推进进入完整验证、发布检查和 CI/Vercel smoke。
