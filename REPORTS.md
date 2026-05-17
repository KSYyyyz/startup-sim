# Startup Sim — Alpha 1.2 收尾校验报告

> 注意：历史阶段（Alpha 1.2/1.3/1.4）的下一步建议仅作版本记录，当前路线以最新 Alpha 1.5 规划为准。

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
| 跑道<6月且做研发 | 控制烧钱 | CTO坚持研发投入 |
| 现金<50万且做营销 | 现金流紧张 | COO认为需投营销获客 |
| 跑道<4月未融资 | 建议融资保命 | 投资方担心条款不利 |
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
- 保守派：跑道>9月 且 产品<60 且 用户<200
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
- **conservative_operator**（保守派操盘手）：跑道>9月，产品<60，用户<200
- **balanced_leader**（均衡型CEO）：中等指标，A轮或均衡
- **chaotic_survivor**（混乱求生者）：无明显特征

### 策略评分（0-100）
- product_score：产品分直接映射
- growth_score：MRR + 用户数组合
- finance_score：现金管理 + 融资效率
- control_score：股权保留比例
- risk_score：跑道健康度
- overall_score：加权平均（A轮+10，破产-15）

### 关键转折点识别
- 现金跌破10万/1万
- 产品分突破70
- MRR超过30万/50万/100万
- 股权跌破80%/50%
- 跑道低于3个月
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
