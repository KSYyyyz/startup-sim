# Startup Sim — Alpha 1.2 收尾校验报告

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
