"""飞书路由 — 在飞书对话中玩创业模拟器 Phase 1 (持久化版)"""
import sys, os, json
from dataclasses import asdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.models import (
    CompanyState, PlayerAction, ActionPlan, ActionType, StateDelta
)
from src.core.state_guard import (
    validate_action_plan, sanitize_delta, apply_delta, StateGuardError
)
from src.core.action_parser import parse as parse_action
from src.core.event_engine import EventEngine
from src.core.ending_evaluator import evaluate as eval_ending, describe_ending
from src.core.difficulty import Difficulty
from src.agents.board import CFO, CTO, COO, InvestorDirector
from src.agents.competitors import KuaiDaTech, LingxiCSCloud
from src.agents.customers import CustomerAgent

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feishu_state.json")

# 全局状态（单用户MVP，通过 save/load 跨进程持久化）
_game_state = None
_difficulty = None
_board = None
_competitors = None
_customer = None
_events = None

def _save():
    """保存游戏状态到 JSON 文件"""
    if _game_state:
        data = {
            "state": _game_state.model_dump(),
            "difficulty": asdict(_difficulty) if _difficulty else None,
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def _load():
    """从 JSON 文件加载游戏状态"""
    global _game_state, _difficulty
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        _game_state = CompanyState(**data["state"])
        if data.get("difficulty"):
            _difficulty = Difficulty(**data["difficulty"])
        return True
    return False

def _ensure_agents():
    """确保所有 Agent 已初始化"""
    global _board, _competitors, _customer, _events
    if not _board:
        _board = [CFO(), CTO(), COO(), InvestorDirector()]
        _competitors = [KuaiDaTech(), LingxiCSCloud()]
        _customer = CustomerAgent()
        _events = EventEngine()

def start(track="AI客服SaaS", difficulty="normal"):
    global _game_state, _difficulty
    _ensure_agents()
    
    diff_map = {"easy": Difficulty.easy(), "hard": Difficulty.hard()}
    _difficulty = diff_map.get(difficulty, Difficulty.normal())
    
    _game_state = CompanyState(
        cash=int(1_000_000 * _difficulty.cash_multiplier),
        monthly_burn=180_000, mrr=0, users=0,
        product_score=max(0, 20 + _difficulty.product_score_add),
        team_morale=max(0, 70 + _difficulty.team_morale_add),
        founder_equity=100, board_control=100,
        market_share=0, reputation=50,
        employee_count=10, price=5000, valuation=5_000_000, month=1
    )
    _save()
    return _render_state()

def _smart_parse(raw: str, state: CompanyState):
    """智能解析：按逗号分句，每句独立提取动作+预算。融资=收入，其余=支出。"""
    import re
    
    # 先全文中提取融资和股权出让（不管逗号位置）
    fundraise_amount = 0
    equity_cost = 0
    
    fm = re.search(r'(?:融资|募资)\s*(\d+)\s*万', raw)
    if fm:
        fundraise_amount = int(fm.group(1)) * 10000
    
    em = re.search(r'出让\s*(\d+)\s*%', raw)
    if em:
        equity_cost = int(em.group(1))
    
    # 按中英文逗号分号分句
    segments = re.split(r'[，,；;、]', raw)
    actions = []
    
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        
        # 跳过纯融资/股权出让的分句
        if any(kw in seg for kw in ['融资', '见投资人', '募资', '出让']):
            continue
        
        budget = 0
        m = re.search(r'(\d+)\s*万', seg)
        if m:
            budget = int(m.group(1)) * 10000
        
        # 动作分类
        if any(kw in seg for kw in ['招', 'hire', '招聘', '雇', '团队']):
            actions.append(PlayerAction(type=ActionType.TEAM, intent=seg, budget=budget))
        elif any(kw in seg for kw in ['投放', '广告', '营销', '推广', '市场', '获客', 'marketing']):
            actions.append(PlayerAction(type=ActionType.MARKETING, intent=seg, budget=budget))
        elif any(kw in seg for kw in ['研发', '产品', '开发', '功能', '迭代', 'feature', 'product', 'r&d']):
            actions.append(PlayerAction(type=ActionType.PRODUCT, intent=seg, budget=budget))
        elif budget > 0:
            # 有预算但没识别到动作类型，默认产品研发
            actions.append(PlayerAction(type=ActionType.PRODUCT, intent=seg, budget=budget))
    
    if not actions:
        actions.append(PlayerAction(type=ActionType.PRODUCT, budget=100000))
    
    return ActionPlan(raw_input=raw, actions=actions), fundraise_amount, equity_cost

def turn(user_input):
    global _game_state
    _ensure_agents()
    
    # 尝试从文件加载（跨进程恢复）
    if not _game_state:
        _load()
    
    if not _game_state:
        return "❌ 游戏还没开始。说「创业模拟器 开始」来开局。"
    
    ending = eval_ending(_game_state)
    if ending:
        return f"🎮 游戏已结束：{describe_ending(ending, _game_state)}\n说「创业模拟器 开始」重新开局。"
    
    # 1. 智能解析（融资单独处理）
    plan, fundraise_amount, equity_cost = _smart_parse(user_input, _game_state)
    
    # 2. 融资处理
    fundraise_narrative = ""
    if fundraise_amount > 0 and equity_cost > 0:
        # 投后估值 = 融资金额 / 出让比例
        post_money = int(fundraise_amount / (equity_cost / 100))
        _game_state = CompanyState(**_game_state.model_dump() | {
            "cash": _game_state.cash + fundraise_amount,
            "founder_equity": max(0, _game_state.founder_equity - equity_cost),
            "board_control": max(0, _game_state.board_control - equity_cost),
            "valuation": post_money,
        })
        fundraise_narrative = f"💰 融资{fundraise_amount//10000}万，出让{equity_cost}%！投后估值{post_money//10000}万"
    
    # 3. StateGuard（只检查支出动作）
    try:
        validate_action_plan(plan, _game_state)
    except StateGuardError as e:
        return f"⚠️ {e}\n请调整你的决策后重试。"
    
    # 4. 董事会
    board_msgs = [f"  [{m.name}] {m.speak(_game_state, plan)}" for m in _board]
    
    # 5. 竞品
    comp_moves, comp_msgs = [], []
    for c in _competitors:
        r = c.respond(_game_state, plan)
        comp_moves.append(r)
        comp_msgs.append(f"  [{r['name']}] {r['action']} — {r['narrative']}")
    
    # 6. 客户
    cust_resp = _customer.evaluate(_game_state, plan, comp_moves)
    
    # 7. 结算
    total_cost = sum(a.budget for a in plan.actions)
    
    # 研发产出 = 投入 + 团队效率 + 士气
    product_boost = 0
    product_narrative = ""
    if any(a.type == ActionType.PRODUCT for a in plan.actions):
        product_budget = sum(a.budget for a in plan.actions if a.type == ActionType.PRODUCT)
        budget_effect = max(1, product_budget // 100_000)     # 每10万投入+1
        team_effect = _game_state.employee_count // 5          # 每5人+1
        morale_effect = _game_state.team_morale // 20          # 每20点士气+1
        product_boost = budget_effect + team_effect + morale_effect
        product_narrative = (
            f"研发投入{product_budget//10000}万(+{budget_effect}) + "
            f"团队{_game_state.employee_count}人(+{team_effect}) + "
            f"士气{_game_state.team_morale}(+{morale_effect}) = 产品+{product_boost}"
        )
    
    # 营销获客 = 预算 / 500元每人
    marketing_boost = 0
    if any(a.type == ActionType.MARKETING for a in plan.actions):
        marketing_budget = sum(a.budget for a in plan.actions if a.type == ActionType.MARKETING)
        marketing_boost = max(50, marketing_budget // 500)
    
    hire_boost = 8 if any(a.type == ActionType.TEAM for a in plan.actions) else 0
    new_hires = sum(1 for a in plan.actions if a.type == ActionType.TEAM) * 3  # 每次招聘+3人
    
    # 每月固定烧钱随员工数增长
    new_burn = _game_state.employee_count * 15000 + new_hires * 15000
    burn_delta = new_burn - _game_state.monthly_burn
    
    delta = StateDelta(
        cash=-(total_cost + new_burn),
        monthly_burn=burn_delta,
        users=marketing_boost + cust_resp.get("growth_change", 0),
        mrr=cust_resp.get("revenue_change", 0),
        product_score=product_boost,
        team_morale=hire_boost,
        employee_count=new_hires,
        reasons=[
            *([f"融资{fundraise_amount//10000}万，出让{equity_cost}%"] if fundraise_amount else []),
            f"支出{total_cost//10000}万，月消耗{new_burn//10000}万"
        ]
    )
    
    safe_delta = sanitize_delta(delta, _game_state)
    _game_state = apply_delta(_game_state, safe_delta)
    _game_state = CompanyState(**_game_state.model_dump() | {"month": _game_state.month + 1})
    
    # 8. 结局
    ending = eval_ending(_game_state)
    
    # 9. 保存
    _save()
    
    # 10. 输出
    lines = [
        f"📅 第{_game_state.month-1}月结果", "",
    ]
    if fundraise_narrative:
        lines.append(fundraise_narrative)
        lines.append("")
    if product_narrative:
        lines.append(f"🔬 研发明细：{product_narrative}")
        lines.append("")
    lines.extend([
        "**👔 董事会：**",
        *board_msgs, "",
        "**🏪 竞品：**",
        *comp_msgs, "",
        f"**👥 客户：** {cust_resp['narrative'][:150]}", "",
        _render_state(),
    ])
    if ending:
        lines.extend(["", f"🏁 **结局：{describe_ending(ending, _game_state)}**"])
    
    return "\n".join(lines)

def _render_state():
    if not _game_state: return ""
    s = _game_state
    diff_name = _difficulty.name if _difficulty else "normal"
    lines = [
        f"🏢 AI客服SaaS | 第{s.month}月 | {diff_name}模式",
        f"💰 现金:{s.cash//10000}万 | 🔥 烧钱:{s.monthly_burn//10000}万/月 | MRR:{s.mrr//10000}万",
        f"👥 用户:{s.users} | 👨‍💻 员工:{s.employee_count}人 | 💰 单价:{s.price}元/月",
        f"📦 产品:{s.product_score} | 💪 士气:{s.team_morale} | ⭐ 声誉:{s.reputation}",
        f"📊 股权:创始人{s.founder_equity}% | 投资人{100-s.founder_equity}% | 董事会控制:{s.board_control}%",
        f"🏦 估值:{s.valuation//10000}万 | ⏳ 跑道:{s.runway_months:.1f}月",
    ]
    return "\n".join(lines)

def status():
    global _game_state
    if not _game_state:
        _load()
    if not _game_state:
        return "🎮 游戏还没开始。说「创业模拟器 开始」来开局。"
    return _render_state()
