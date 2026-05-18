# Startup Sim 🚀  Alpha 1.9.1

**AI创业模拟器** — 回合制创业策略游戏，CLI + 飞书双端可玩。

你是AI客服SaaS创始人，种子轮100万。12个月内做产品/营销/招聘/融资决策，在董事会、竞品、客户三方博弈中活下来。

> ⚠️ Alpha 1.9.1 是体验验证与路线收口版本。Alpha 1.9 已完成核心矛盾/竞品态势/经营洞察/危机解释等反馈增强。
> 后续开发以 C# Core + Godot 表现层为主。Vercel/Web 前端路线已放弃，后续只做 Godot 前端。

### 🔗 快速导航

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 3分钟快速启动指南 |
| [examples/sample_run_balanced.md](examples/sample_run_balanced.md) | 官方样例局：均衡策略→A轮成功 |
| [examples/sample_run_marketing_failure.md](examples/sample_run_marketing_failure.md) | 官方失败样例：全营销→慢性死亡 |
| [docs/indie_game_product_direction.md](docs/indie_game_product_direction.md) | 独立游戏化产品方向与可分发路线 |
| [docs/startup_sim_development_plan.md](docs/startup_sim_development_plan.md) | Godot 主线完整开发规划 |
| [docs/reference_game_analysis.md](docs/reference_game_analysis.md) | 本地参考游戏结构分析与 Startup Sim 借鉴边界 |
| [docs/godot_migration_plan.md](docs/godot_migration_plan.md) | Godot 独立游戏表现层迁移方案 |
| [docs/csharp_core_migration_plan.md](docs/csharp_core_migration_plan.md) | C# Core 规则迁移方案 |
| [docs/project_layout.md](docs/project_layout.md) | 本地与云端项目布局标准 |
| [docs/playtest_feedback_template.md](docs/playtest_feedback_template.md) | 玩家试玩反馈模板 |
| [docs/troubleshooting.md](docs/troubleshooting.md) | 常见问题排查

## 🧭 当前主线

后续新增工程、场景、交互原型和桌面端可分发路线都以 Godot 为准。

- Godot 工程：`godot/StartupSimGodot/`
- 规则核心：`csharp/StartupSim.Core/`
- 完整参考实现：`src/core/`
- 旧 Web/Vercel 前端已删除，后续前端只在 Godot 中实现。

## 🧱 C# Core / Godot 迁移进度

`csharp/StartupSim.Core/` 已开始承接可迁移玩法核心，目标是给未来 Godot 独立游戏版本复用同一套结算逻辑。

- 已完成 `ActionParser.ParseMulti()` 的 C# 迁移切片，支持研发、营销、招聘、战略、融资、多动作、预算、风险词、融资额和出让比例。
- 已完成最小 `DeterministicTurnEngine` 切片：产品、营销、团队、战略、融资、多动作聚合、现金透支破产保护。
- 已建立 C# xUnit 测试与 GitHub CI 门禁，当前 C# Core 测试覆盖 17 个用例。
- Godot 侧已有 `godot/StartupSimGodot/` 工程骨架、主场景、办公室热点脚本、`PreparedActionSnapshot`、`TurnResultSnapshot` 和 `GodotTurnBridge`。
- `StartupSimGodot.csproj` 已引用 `csharp/StartupSim.Core`，Godot 可以通过本地 C# Core 执行回合结算。
- Unity 路线停止作为新增开发目标。

## 🎮 快速开始

```bash
pip install -r requirements.txt
python app.py new --name "你的名字"                    # CLI版
# 或在飞书里说「创业模拟器 开始」                          # 飞书版
```

## 🕹️ 玩法

自然语言输入决策，每回合 ≤5 个动作：

```
👉 见投资人融资500万，出让10%股权，花50万研发产品，30万招聘，20万做营销
```

> ⚠️ 当前版本普通非融资支出受可用现金限制；本回合融资到账可以计入可用现金；融资现金流入不受65%现金变化限制。

### 行动类型

| 类型 | 关键词 | 效果 |
|------|--------|------|
| 🛠️ 产品研发 | 研发、开发、功能 | 提升产品分（投入+团队+士气） |
| 📣 市场营销 | 广告、推广、投放 | 获客 + 影响竞品反应 |
| 👥 招聘 | 招人、团队 | +3员工/次，+士气，+研发效率 |
| 💰 融资 | 见投资人、融资 | 现金↑股权↓，决定估值 |
| 🎯 战略 | 转型、新市场 | 影响市场份额 |

### 研发公式

```
产品提升 = 投入(每8万+1) + 团队(每3人+1) + 士气(每10点+1)
          = budget // 80_000 + employee_count // 3 + team_morale // 10
有机增长 = 团队≥5人时，每回合自然+1产品分
```

员工越多 → 同样投入产出更高，但每人月薪1.5万会推高烧钱。

## 📊 状态面板（14项核心指标固定显示）

| 分类 | 指标 |
|------|------|
| 💰 财务 | 现金 · 月烧钱 · MRR · 估值 |
| 👥 运营 | 用户数 · 员工数 · 产品单价 |
| 📦 产品 | 产品评分 · 团队士气 · 声誉 |
| 📊 股权 | 创始人% · 投资人% · 董事会控制% |
| ⏳ 生存 | 可支撑(月) |
| 🏪 市场 | 市场份额 |

### MRR 自动计算

```
付费用户 = 总用户 × 转化率(产品分决定)
MRR = 付费用户 × 单价
```

| 产品分 | 付费转化率 |
|--------|-----------|
| <30 | 2% |
| 30-50 | 5% |
| 50-70 | 10% |
| >70 | 18% |

## 🏛️ 游戏系统

### 👔 董事会（4角色）

每回合基于同一公司状态给出矛盾建议：

| 角色 | 关注点 |
|------|--------|
| CFO | 现金流、可支撑时间、烧钱速度 |
| CTO | 产品分、技术路线 |
| COO | 运营效率、交付质量 |
| 具名投资机构代表 | 增长指标、PMF验证，仅在融资相关场景出现 |

### 🏪 竞品博弈

| 竞品 | 策略 | 触发条件 |
|------|------|----------|
| 快答科技 | 价格战抢客户 | 你产品分超过它 |
| 灵犀客服云 | 差异化守高端 | 不参与价格战 |

### 👥 客户Agent

四因子驱动：产品分 · 营销投入 · 竞品价格 · 团队士气
- 营销获客统一由 CustomerAgent 处理（CAC=800元/人），不再重复结算
- 产品分决定留存率和付费转化率

### ⚖️ StateGuard 校验层

Pydantic 强类型 + 规则引擎，所有状态变更必须通过校验：
- 普通现金流出单回合最多限制为当前现金的65%；**融资现金流入不受该限制**。
- 产品分/士气单回合变动有上限
- 所有值自动 clamp 到合法范围

## 🏁 5种结局

| 结局 | 触发条件 |
|------|----------|
| 💸 破产 | 现金 ≤ 0 |
| 👋 创始人出局 | 股权<34% 且 董事会<45% 且 可支撑<4月 |
| 🎉 A轮成功 | 12月 MRR≥30万 产品≥65 股权≥50% |
| 😐 勉强存活 | 12月 MRR≥10万 现金>0 |
| 🐌 慢性死亡 | 12月未达标 |

## 🎯 难度系统

| 难度 | 现金倍率 | 产品 | 士气 | 事件频率 | 竞品侵略性 |
|------|----------|------|------|----------|------------|
| Easy | 1.5× | +10 | +10 | 0.5× | 0.7× |
| Normal | 1.0× | 0 | 0 | 1.0× | 1.0× |
| Hard | 0.7× | -5 | -5 | 1.5× | 1.3× |

## 🧪 自动化测试

```bash
pytest tests/ -v    # 402 passed
```

测试覆盖：
- **平衡测试**：5种策略 × 12回合自动运行，验证结局多样性 ≥3 种
- **补充测试**：process_turn_raw 端到端流程、营销不重复结算、融资现金豁免、研发公式验证
- **Alpha 1.4 测试**：结局叙事变体、玩家路径分类、董事会冲突检测、复盘系统、创始人画像、策略评分
- **Alpha 1.5 测试**：回放系统、成就徽章、策略对比
- **Alpha 1.6 测试**：建议引擎(17)、新手引导(18)、状态解读(21)
- **Alpha 1.8 测试**：融资估值引擎(10)、声誉效果(6)、状态面板(6)、反馈可见性(4)、StateGuard建议(5)
- 规则解析器、StateGuard、竞品、客户、董事会、结局判定全覆盖

## 📋 Alpha 1.9 更新内容

**真实内测反馈修复版** — 不堆功能，只提升可理解性、反馈质量和复玩动力。

1. **本月核心矛盾** — `src/core/conflict_engine.py`
   - 每回合识别最紧迫的经营矛盾（现金流/PMF/增长/股权/交付/竞争/团队）
   - 1-2句话描述 + 严重程度 + 建议聚焦方向
   - CLI 和飞书每回合显示

2. **竞品态势强化** — `src/core/turn_engine.py`
   - 市场格局估算：你的份额 vs 快答科技+灵犀客服云
   - 每回合显示竞品动作对玩家的具体影响（份额变化、用户变化）
   - 竞品状态一目了然

3. **经营洞察** — `src/core/insight_engine.py`
   - 每回合根据动作和结果生成一条经营洞察
   - 覆盖：融资成功/被拒、高营销低产品、高研发低现金、MRR增长信号、声誉下滑、士气下降
   - 复盘记录最重要的3条洞察，融入下局建议

4. **危机解释和可复制策略** — `src/core/state_guard.py`
   - 预算超限、融资被拒、可支撑<2月、现金<月消耗、股权<70%时
   - 显示危机解释 + 2-3条可直接复制粘贴的恢复输入
   - 所有替代输入可被 parse_multi 解析

5. **StateGuard 拦截进入复盘** — `src/core/review_engine.py`
   - 被 StateGuard 拦截时记录 KeyMoment：「第X月：预算计划超出现金承受能力」
   - 不影响正常通过的回合

6. **内测反馈日志** — `docs/playtest_feedback_log.md`
   - 标准化反馈模板：玩家代号、结局、拦截次数、理解度、再玩意愿、困惑月份等

7. **Playtest 输出增强** — `scripts/playtest.py`
   - 每种策略增加：核心矛盾摘要、经营洞察数量、危机解释次数、融资拒绝、StateGuard拦截

## 📋 Alpha 1.8 更新内容


1. **融资估值约束系统** — `src/core/fundraising_engine.py`
   - 投资人根据 MRR、用户数、产品分、声誉、可支撑时间计算合理估值区间
   - 报价过高（>上限×1.5）被拒绝并给出反报价，报价过低（<下限×0.5）警告但接受
   - 估值公式：base = max(MRR×60, users×3000, 300万)，乘以产品分/声誉/可支撑时间修正因子

2. **声誉影响系统** — 接入4个系统
   - 融资估值修正：高声望(+15%)/低声望(-25%) 影响估值区间
   - CAC 修正：rep≥80 → CAC=720（-10%），rep<40 → CAC=960（+20%）
   - 团队士气加成：rep≥80 时招聘额外+2士气
   - 营销声誉衰减：高声望时营销声誉增益递减

3. **固定状态面板** — `src/core/status_formatter.py`
   - 14项核心指标始终显示（含市场份额），不因状态变化隐藏字段
   - `format_status_panel()` 完整面板（CLI），`format_status_panel_short()` 紧凑面板（飞书）

4. **每回合强制董事会+市场反馈** — `_format_result()` 改为强制输出
   - board_feedback、competitor_moves、customer_response 每回合必定有值
   - 空值情况下填充默认文案，不再随机缺失

5. **StateGuard 拦截后给出可复制替代输入** — `src/core/state_guard.py`
   - 预算超限错误含2-3条可复制示例输入（「花X万研发产品」格式）
   - 高股权时自动包含融资选项，低股权时仅建议降预算
   - 示例包含「」中文书名号，可直接复制粘贴

## 📋 Alpha 1.6 更新内容

1. **新手引导** — `src/core/tutorial.py`
   - `TutorialEngine`：新开局4步引导（欢迎/输入方式/决策类型/指标说明）
   - 6种阈值提示：可支撑<3月现金流风险、股权<70%稀释提醒、低产品分营销泡沫、高产品低MRR商业化提醒、士气危机、董事会控制权风险
   - 纯函数无副作用，不改变任何游戏数值

2. **建议引擎** — `src/core/suggestion_engine.py`
   - `SuggestionEngine.generate(state)` 返回3条建议：稳健路线/激进路线/风险提示
   - 每条建议包含 title/description/example_input/risk_level/reason
   - example_input 可被 parse_multi 直接解析
   - 基于状态智能判断：低现金→控支保命、高产品低MRR→商业化、低产品→研发优先

3. **状态解读** — `src/core/state_explainer.py`
   - `StateExplainer` 将数值翻译为人话：现金→可支撑时间估算、产品分→成熟度(原型/MVP/可用/成熟/优秀/顶尖)、MRR用户→转化问题、股权→控制权描述
   - CLI 状态面板和飞书均调用

4. **CLI 每回合建议** — `app.py`
   - 每回合仅显示「建议」入口；输入「建议」后显示3条路线（稳健/激进/风险）+ 可执行示例
   - 输入 help/帮助/怎么玩/指令 显示完整帮助
   - 状态面板集成 StateExplainer 人话解读

5. **飞书增强** — `feishu_play.py`
   - 每回合后显示风险提示 + 2个可复制输入示例
   - 新开局显示轻量引导提示
   - 支持 help/帮助/怎么玩/指令 路由
   - 会话持久化：external_user_id → session_id 绑定写入 SQLite `external_sessions` 表，进程重启可恢复
   - 「状态」命令只读不创建新 session，「重新开始」才创建新 session 并覆盖绑定
   - 「会话」命令输出 external_user_id / session_id / 当前月份 / 状态 / 最近更新时间
   - 调试日志写入 `logs/feishu_session.log`

6. **StateGuard 错误提示增强** — `src/core/state_guard.py`
   - 预算超限错误含：哪里错了、当前限制、怎么改、可复制示例输入
   - 全部中文，结构化输出（❌错误 💡解决方法 📝示例）

7. **Help 命令** — `app.py` + `feishu_play.py`
   - 游戏目标、输入格式、五种决策类型、关键指标说明、示例输入

## 📋 Alpha 1.3 更新内容

1. **随机事件池（27个事件）** — `src/core/events.py`
   - 机会类10个：大客户签约、媒体报道、技术洞察、政策利好、竞品失误、自然裂变、人才入职、渠道合作、奖项入围、口碑推荐
   - 危机类10个：服务器宕机、员工离职、客户投诉、竞品挖角、数据安全传闻、支付故障、监管问询、基础设施涨价、投资人动摇、客户流失
   - 中性类7个：行业大会、投资人引荐、团队内部分歧、市场传闻、用户需求反馈、收购意向、技术范式变化
   - 每事件影响 ≤±3产品分/±5士气/±2市场份额，约20%概率触发→每12回合2-3个
   - 与现有3个固定事件（runway_warning/board_coup_risk/product_breakthrough）共存，不破坏接口

2. **董事会争议系统** — `src/agents/board.py`
   - CFO/CTO/COO/具名投资机构代表基于同一state给出矛盾建议
   - `generate_board_minutes()` 函数输出格式化董事会会议记录
   - 自动检测分歧焦点（CFO砍预算 vs CTO加研发、CFO保守 vs COO增长）

3. **竞品状态化** — `src/agents/competitors.py`
   - `CompetitorState` 数据类：product_score/cash/market_share/strategy_cooldown
   - `periodic_action()` 方法：竞品每回合独立行动（自主降价、企业功能发布、市场份额增长）
   - 竞品状态写入月度战报

4. **月度战报** — `src/core/turn_engine.py`
   - `generate_monthly_report(result, state_before, state_after)` 函数
   - 6个板块：关键变化、董事会争议、竞品动作、客户反馈、风险提醒、下月建议
   - CLI和飞书共用

5. **结局叙事增强** — `src/core/ending_evaluator.py`
   - 玩家路径分类：研发派/营销派/融资派/均衡派/保守派
   - 5种结局 × 5种路径 = 每种结局2-3种文案变体
   - `describe_ending_with_seed()` 支持确定性叙事（用于测试）

## 📋 Alpha 1.5 更新内容

1. **回放系统** — `src/core/replay_engine.py`
   - `ReplayEngine.generate_replay()` 生成12个月叙事回放时间线
   - 每月有叙事标题（如"种子轮后的第一次豪赌""决定命运的融资窗口"）+ 风险等级 + 指标变化
   - 自动识别climax_month（最具戏剧性的转折月）+ 生成3-4个replay_tags（如"A轮赢家""惊险刺激""稳健经营"）
   - 5种结局各有定制结局叙事（A轮之路/小而美/温水/燃烧殆尽/失去王座）

2. **成就系统** — `src/core/achievement_engine.py`
   - `AchievementEngine.evaluate()` 评估15个成就徽章
   - 4种稀有度：common(7个) / rare(5个) / epic(2个) / legendary(1个)
   - 涵盖产品/增长/融资/风控/控制全维度：产品信仰者、增长机器、A轮赢家、死里逃生、现金守门员、控制权大师、稀释换增长、慢性死亡、研发陷阱、营销泡沫、小而美、资本玩家、危机处理者、稳健经营者、传奇创始人

3. **策略对比** — `src/core/strategy_compare.py`
   - `StrategyCompare.compare()` 输入多个 GameReview，输出策略对比表
   - 每维最佳 + 风控最弱排名：综合最优/产品最强/增长最快/财务最佳/控制最稳/风控最弱

4. **CLI 增强** — `app.py`
   - 游戏结束时输出回放线（5个关键月份）和成就徽章列表

5. **飞书增强** — `feishu_play.py`
   - 游戏结束时输出精简回放（2-3个关键月）+ 成就（前3个）

6. **Playtest 策略对比** — `scripts/playtest.py`
   - 所有策略结束后自动输出策略对比排名表

## 📋 Alpha 1.4 更新内容

1. **复盘系统** — `src/core/review_engine.py`
   - `ReviewEngine.generate_review()` 生成完整 GameReview 复盘报告
   - 6种创始人画像识别：技术极客/增长黑客/资本玩家/保守派操盘手/均衡型CEO/混乱求生者
   - 5维策略评分（0-100）：产品力/增长力/财务力/控制力/风控力 + 综合评分
   - 关键转折点识别：现金危机/产品突破/MRR里程碑/股权稀释/可支撑时间警告/重大事件
   - 结局解释增强：series_a_success 按风格区分4种叙事，survived_but_average 区分4种，slow_death 区分4种

2. **复盘数据结构** — `src/core/models.py`
   - `FounderProfile` / `StrategyScore` / `KeyMoment` / `GameReview` 四个 Pydantic 模型

3. **CLI 结局复盘** — `app.py`
   - 游戏结束时输出完整创业复盘报告：结局标题、一句话总结、最终指标、策略评分、关键转折点、创始人画像、下局建议

4. **飞书简版复盘** — `feishu_play.py`
   - 游戏结束时输出精简复盘：结局、总结、5项评分、3个关键转折点、下局建议

5. **数据库历史查询** — `src/db/repository.py`
   - 新增 `list_snapshots()` / `list_actions()` / `list_events()` 三个读接口，不破坏现有事务逻辑

6. **Playtest 增强** — `scripts/playtest.py`
   - 每种策略结束后输出简版复盘摘要：结局标题、创始人画像、综合评分、关键转折点数量

## 📋 Alpha 1.2 更新内容

1. **12 回合内部试玩** — `scripts/playtest.py` 跑满 5 种策略 × 12 回合
2. **5 种策略自动平衡测试** — 验证不存在无脑最优策略，结局种类 ≥3
3. **数值参数调优**：
   - 默认月烧钱 18万 → 12万
   - 研发公式除数 10万 → 8万；研发烧钱 1/20 → 1/30；营销烧钱 1/8 → 1/12
   - CAC 1000 → 800；有机产品学习新增：≥5员工 +1/回合
   - A轮 MRR 阈值 50万 → 30万；产品分 70 → 65
   - 存活 MRR 阈值 20万 → 10万
4. **避免无脑最优策略** — 纯研发现金流压力极大，稳定结果多为勉强存活，部分随机种子下可能破产；纯营销慢性死亡，需融资+平衡才更容易A轮成功。
5. **保持规则解析器 + Mock Agent**，不接真实 LLM，零 API 消耗

## 🏗️ 项目结构

```
startup-sim/
├── app.py                  # CLI入口
├── feishu_play.py          # 飞书薄适配层：命令识别 + session映射 + TurnEngine调用 + 格式化输出
├── godot/StartupSimGodot/  # Godot 4.6.x .NET 表现层
├── csharp/StartupSim.Core/ # 可迁移 C# 规则核心
├── config.py               # 配置
├── QUICKSTART.md           # 3分钟快速启动指南
├── data/scenarios.yaml     # 剧本
├── examples/
│   ├── sample_run_balanced.md         # 样例局：均衡→A轮成功
│   └── sample_run_marketing_failure.md # 样例局：全营销→慢性死亡
├── scripts/
│   ├── playtest.py              # 12回合自动试玩脚本
│   ├── check_docs_consistency.py # 文档一致性检查脚本
│   └── start_demo.py            # 启动前检查脚本
├── src/
│   ├── core/
│   │   ├── models.py           # Pydantic模型(含employee/price/valuation)
│   │   ├── state_guard.py      # StateGuard校验
│   │   ├── action_parser.py    # 自然语言解析
│   │   ├── events.py           # 随机事件池(Alpha 1.3)
│   │   ├── event_engine.py     # 事件引擎
│   │   ├── ending_evaluator.py # 结局判定+路径分类(Alpha 1.3)
│   │   ├── review_engine.py    # 复盘系统+创始人画像+策略评分(Alpha 1.4)
│   │   ├── replay_engine.py    # 回放系统+月历叙事(Alpha 1.5)
│   │   ├── achievement_engine.py # 成就徽章系统(Alpha 1.5)
│   │   ├── strategy_compare.py # 策略对比(Alpha 1.5)
│   │   ├── tutorial.py         # 新手引导+阈值提示(Alpha 1.6)
│   │   ├── suggestion_engine.py # 行动建议引擎(Alpha 1.6)
│   │   ├── state_explainer.py  # 状态人话解读(Alpha 1.6)
│   │   ├── turn_engine.py      # 回合主流程+月度战报(Alpha 1.3)
│   │   ├── fundraising_engine.py # 融资估值引擎(Alpha 1.8)
│   │   ├── status_formatter.py   # 状态面板格式化(Alpha 1.8)
│   │   ├── difficulty.py       # 难度系统
│   │   └── balancer.py         # 数值平衡器
│   ├── agents/
│   │   ├── base_agent.py       # Agent基类
│   │   ├── board.py            # 董事会(CFO/CTO/COO/投资方)
│   │   ├── competitors.py      # 竞品(快答/灵犀)
│   │   └── customers.py        # 客户群体(四因子+转化率)
│   └── db/
│       ├── connection.py / schema.sql / repository.py
├── docs/
│   ├── indie_game_product_direction.md          # 独立游戏化产品方向
│   ├── godot_migration_plan.md                  # Godot 表现层迁移方案
│   ├── csharp_core_migration_plan.md            # C# Core 规则迁移方案
│   ├── project_layout.md                        # 本地与云端布局标准
│   ├── playtest_feedback_template.md # 玩家试玩反馈模板
│   ├── playtest_observation.md       # 试玩观察记录模板
│   └── troubleshooting.md            # 常见问题排查
└── tests/                  # pytest 全覆盖
```

## 🛠️ 工程治理

| 命令 | 说明 |
|------|------|
| `make format` | black + isort 代码格式化 |
| `make lint` | ruff 静态检查 |
| `make test` | pytest 全量测试 |
| `make playtest` | 12回合自动试玩 + 策略对比 |
| `make docs-check` | 检查 VERSION / README / REPORTS / 事件统计等文档一致性 |
| `make check` | 依次执行 format + lint + test + playtest + docs-check |

每次版本推进前必须 `make check` 全部通过。

## 🛠️ 技术栈

- Python 3.9+ · Pydantic · SQLite · PyYAML · pytest
- Godot: Godot 4.6.x .NET + C# presentation scripts
- Portable core: .NET 8 tests + `StartupSim.Core`
- Alpha 1.8：规则解析器 + Mock Agent + 复盘/回放/成就/策略对比 + 新手引导/建议引擎/状态解读/Help + 融资估值引擎/声誉系统/状态面板/反馈强制 + 试玩文档体系
- 零API消耗，全规则引擎驱动

---

*体验验证版 Alpha 1.9.1 — 402 tests passed；后续开发以 Godot 表现层和 C# Core 规则迁移为主。*
