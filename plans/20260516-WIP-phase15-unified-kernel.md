# Phase 1.5 — 统一内核 + 稳定可玩性

**状态:** WIP  
**版本:** Alpha 1.0 → 1.1  
**日期:** 2026-05-16

---

## 目标

消除 CLI/飞书双份逻辑，重构融资系统，改进解析器，自动平衡验证。

---

## 任务 1：统一 CLI 和飞书的回合逻辑

### 问题
- `feishu_play.py` 自己实现了完整的 turn() 函数（解析、融资、结算、董事会、竞品、客户、结局、渲染），与 TurnEngine 完全重复
- 两套代码独立演进，行为必然不一致

### 方案
在 `TurnEngine` 中新增 **无状态版本** `process_turn_raw(state, raw_input, difficulty)` → `TurnResult`：

```
def process_turn_raw(state: CompanyState, raw_input: str, difficulty: Difficulty) -> TurnResult:
    """Stateless turn processing: no DB, no session. Returns TurnResult."""
```

内部流程与 `process_turn()` 一致：
1. action_parser.parse(raw_input) → ActionPlan
2. board.speak(state, plan) → board_feedback
3. state_guard.validate(plan, state)
4. _simulate(plan, state) → delta
5. competitors.respond(state, plan) → competitor_moves
6. customer.evaluate(state, plan, competitor_moves) → customer_response
7. _merge_competitor_customer_delta(delta, competitor_moves, customer_response)
8. sanitize_delta(delta, state)
9. apply_delta(state, delta) → state_after
10. event_engine.evaluate(state_after) → events
11. event_engine.apply_event_deltas(state_after, events) → final state
12. month += 1
13. ending_evaluator.evaluate(final_state) → ending

返回 `TurnResult`（含 state_after, delta, events, board_feedback, competitor_moves, customer_response, ending）

### feishu_play.py 重构
- 删除所有游戏逻辑代码
- 只保留：
  1. 命令识别：`开始` → start_session / `状态` → status / 其他 → 决策
  2. 调用 `TurnEngine.process_turn_raw(state, raw_input, difficulty)`
  3. `_render_turn_result()` 格式化 TurnResult → 飞书消息
  4. `_save()/_load()` 持久化 CompanyState

### app.py (CLI) 保持
- 现有 `process_turn()` 带 DB 的版本不变
- 启动时调用 `process_turn_raw()` 或通过 TurnEngine 实例

---

## 任务 2：重构融资逻辑

### 问题
- 融资被当作普通支出 action（budget 字段复用为融资金额）
- StateGuard 把融资金额也算入预算总额检查
- 融资效果硬编码（`cash += budget*2`, `equity -= 5`）

### 方案

#### A. PlayerAction 扩展
```python
class PlayerAction(BaseModel):
    type: ActionType
    intent: str = ""
    budget: int = 0          # 支出类动作的预算
    risk_level: RiskLevel = RiskLevel.MEDIUM
    # 融资专用字段
    fundraise_amount: int = 0      # 融资金额
    equity_offered: int = 0        # 出让股权%
    post_money_valuation: int = 0  # 投后估值(自动计算)
```

#### B. StateGuard 修改
```python
def validate_action_plan(plan, state):
    # 总支出 = sum(非融资动作的 budget)
    expense_total = sum(a.budget for a in plan.actions if a.type != ActionType.FUNDRAISING)
    if expense_total > state.cash:
        raise StateGuardError(f"支出{expense_total}超过现金{state.cash}")
```

#### C. _simulate 修改
```python
elif action.type == "fundraising":
    if action.fundraise_amount > 0 and action.equity_offered > 0:
        delta.cash += action.fundraise_amount
        delta.founder_equity -= action.equity_offered
        delta.board_control -= action.equity_offered
        delta.valuation = int(action.fundraise_amount / (action.equity_offered / 100))
```

#### D. 测试
`tests/test_fundraising.py`:
- 融资 500 万出让 10%：cash+500万，equity-10%，board-10%，valuation=5000万
- 融资时 cash 不足但不应被拒绝（融资不算支出）
- 融资 0 或 equity=0 为非法

---

## 任务 3：改进 ActionParser

### 问题
- 只支持 2 个动作
- 预算提取只看第一个数字
- 融资和支出混在一起

### 方案

#### 新增 `parse_multi(raw_input)` 函数
```python
def parse_multi(raw_input: str) -> ActionPlan:
    """多分句解析，每句独立提取动作+预算"""
```

逻辑：
1. 全文提取融资信息：`re.search(r'融资(\d+)万.*?出让(\d+)%', raw)`
2. 按 `[，,；;、]` 分句
3. 跳过融资/股权出让分句
4. 每句：关键字匹配动作类型 + `re.search(r'(\d+)万', seg)` 提取预算
5. 最多 5 个动作

#### 测试
`tests/test_action_parser.py`:
```
"融资500万出让10%，花200万研发，100万招聘，50万投放"
→ fundraising amount=500万 equity=10%
→ product budget=200万
→ team budget=100万  
→ marketing budget=50万

"研发产品花30万"
→ product budget=30万 (1 action)

"降价到3000元抢市场"
→ marketing budget=0 (无预算数字，但识别为营销)
```

---

## 任务 4：自动平衡测试

### 文件
`tests/test_balance_simulation.py`

### 5 种固定策略

| # | 策略名 | 每月执行 |
|---|--------|----------|
| 1 | 全研发 | 研发花全部现金的 40% |
| 2 | 全营销 | 营销花全部现金的 40% |
| 3 | 保守现金流 | 不花任何钱，仅维持运营 |
| 4 | 激进融资增长 | T1融资，然后研发+营销疯狂烧钱 |
| 5 | 均衡策略 | 研发30% + 营销30% + 招聘20% |

### 验收标准
```python
def test_no_strategy_dominates():
    results = {name: run_strategy(name, fn) for name, fn in strategies.items()}
    winners = [r for r in results.values() if r.ending == "series_a_success"]
    assert len(winners) < len(strategies), "不能所有策略都赢"
    assert len(winners) > 0, "至少有一种策略能赢"
    # 每种结局至少出现一次
    all_endings = {r.ending for r in results.values()}
    assert len(all_endings) >= 3, "结局多样性不足"
```

---

## 任务 5：Alpha 1.1 验收

- [ ] CLI 和飞书同一决策 → TurnResult 完全一致
- [ ] `pytest tests/ -v` 全通过
- [ ] README 标题更新为 `Alpha 1.1`
- [ ] VERSION 文件更新为 `1.1`
- [ ] README 明确标注 "Mock LLM — Phase 2 接入真实 LLM Action Parser"
- [ ] Git commit + push

---

## 执行顺序

1. **先改 ActionParser**（任务3）→ 独立模块，测试先行
2. **重构融资**（任务2）→ 改 PlayerAction + StateGuard + _simulate
3. **统一内核**（任务1）→ TurnEngine.process_turn_raw()
4. **重写 feishu_play.py** → 只做路由+渲染
5. **平衡测试**（任务4）→ 跑 5 策略 × 12 月
6. **验收 + 版本更新**（任务5）

## 注意

- 不接真实 LLM，保持 Mock
- `process_turn_raw()` 不能依赖 DB
- 所有改动必须有测试覆盖
- 每次 commit message 清晰标注任务编号
