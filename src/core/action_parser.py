"""Mock ActionParser: keyword-matching parser for natural-language player input.

Phase 1A: no real LLM calls. Uses keyword matching and simple regex to extract
actions and budgets from player text.
"""

from __future__ import annotations

import re
from typing import Tuple

from src.core.models import ActionPlan, ActionType, PlayerAction, RiskLevel


# ── Keyword → action type mapping ─────────────────────────────────────────────

KEYWORD_MAP: list[Tuple[list[str], ActionType, RiskLevel]] = [
    (["融资", "见投资人", "见投资", "投资人", "路演", "募资", "fundraise", "funding", "vc"], ActionType.FUNDRAISING, RiskLevel.LOW),
    (["招", "hire", "招聘", "雇", "挖人", "团队建设", "扩团队", "招人"], ActionType.TEAM, RiskLevel.MEDIUM),
    (["降价", "投放", "广告", "营销", "推广", "获客", "市场", "增长", "seo", "sem",
      "marketing", "ads", "广告投放", "种子客户", "种子用户"], ActionType.MARKETING, RiskLevel.MEDIUM),
    (["研发", "功能", "产品", "开发", "迭代", "feature", "特性", "技术", "代码",
      "product", "dev", "r&d", "工单", "ai"], ActionType.PRODUCT, RiskLevel.MEDIUM),
    (["转型", "并购", "新市场", "战略", "pivot", "strategy", "收购", "出海",
      "扩张", "新业务"], ActionType.STRATEGY, RiskLevel.HIGH),
]


def _extract_budget(text: str) -> int:
    """Extract a budget number from text. Looks for patterns like '花20万', '50万',
    '预算30', 'budget 100000', '100万元' etc. Returns 0 if none found.
    """
    # Pattern: digits followed by optional 万 (multiply by 10000)
    match = re.findall(r"(\d+)\s*万", text)
    if match:
        return int(match[0]) * 10_000

    # Pattern: bare digits that look like budget amounts (>= 1000)
    bare = re.findall(r"(?:花|预算|花掉|花费|投入|allocate|spend|budget)\s*(\d+)", text)
    if bare:
        return int(bare[0])

    return 0


def _determine_risk(text: str, action_type: ActionType) -> RiskLevel:
    """Determine risk level from text cues."""
    high_keywords = ["激进", "烧钱", "高风险", "all in", "all-in", "豪赌", "猛砸"]
    low_keywords = ["保守", "稳健", "试探", "小规模", "谨慎", "低成本"]

    for kw in high_keywords:
        if kw in text:
            return RiskLevel.HIGH
    for kw in low_keywords:
        if kw in text:
            return RiskLevel.LOW

    # Default risk by action type
    defaults = {
        ActionType.FUNDRAISING: RiskLevel.LOW,
        ActionType.TEAM: RiskLevel.MEDIUM,
        ActionType.MARKETING: RiskLevel.MEDIUM,
        ActionType.PRODUCT: RiskLevel.MEDIUM,
        ActionType.STRATEGY: RiskLevel.HIGH,
    }
    return defaults.get(action_type, RiskLevel.MEDIUM)


def parse(raw_input: str) -> ActionPlan:
    """Parse natural-language player input into an ActionPlan using keyword matching.

    Detects up to 2 distinct action types from the input, extracts budgets,
    and returns a structured ActionPlan.
    """
    actions = []
    seen_types = set()

    for keywords, action_type, default_risk in KEYWORD_MAP:
        if action_type in seen_types:
            continue
        if any(kw in raw_input for kw in keywords):
            budget = _extract_budget(raw_input)
            # If multiple actions would share the same budget, split it
            # For simplicity, first action gets the full extracted budget, others get 0
            if len(actions) > 0 and budget > 0:
                budget = max(0, budget - sum(a.budget for a in actions))

            risk = _determine_risk(raw_input, action_type)
            actions.append(PlayerAction(
                type=action_type,
                intent=raw_input.strip(),
                budget=budget,
                risk_level=risk,
            ))
            seen_types.add(action_type)

        if len(actions) >= 2:
            break

    return ActionPlan(raw_input=raw_input, actions=actions)


def _extract_budget_per_segment(text: str) -> int:
    """Extract budget from a single clause. Looks for 'NN万' pattern and
    returns the amount in 元 (e.g. '30万' → 300000). Returns 0 if none found.
    """
    match = re.search(r'(\d+)万', text)
    if match:
        return int(match.group(1)) * 10_000
    return 0


def parse_multi(raw_input: str) -> ActionPlan:
    """Parse natural-language input into an ActionPlan with up to 5 actions.

    Enhancement over parse():
    - Extracts fundraising (融资+出让) from full text first
    - Splits input by Chinese/English punctuation into clauses
    - Each clause is independently keyword-matched and budget-extracted
    - Skips clauses that contain fundraising-related keywords
    - Max 5 actions total

    Args:
        raw_input: Natural-language player input (e.g. "融资500万出让10%，花200万研发，100万招聘")

    Returns:
        ActionPlan with parsed actions
    """
    actions = []
    seen_types = set()

    # ── Step 1: Extract fundraising from full text ────────────────────────
    fundraise_match = re.search(r'融资(\d+)万.*?出让(\d+)%', raw_input)
    fundraise_amount = 0
    equity_offered = 0
    if fundraise_match:
        fundraise_amount = int(fundraise_match.group(1)) * 10_000
        equity_offered = int(fundraise_match.group(2))

    # ── Step 2: Split into clauses ────────────────────────────────────────
    clauses = re.split(r'[，,；;、]', raw_input)
    clauses = [c.strip() for c in clauses if c.strip()]

    # ── Step 3: Process each clause ───────────────────────────────────────
    for clause in clauses:
        # Skip clauses about fundraising/dilution (already handled)
        if '融资' in clause or '出让' in clause:
            continue

        # Match action type via keywords
        matched_type = None
        matched_risk = RiskLevel.MEDIUM
        for keywords, action_type, default_risk in KEYWORD_MAP:
            if action_type in seen_types:
                continue
            if any(kw in clause for kw in keywords):
                matched_type = action_type
                matched_risk = default_risk
                break

        if matched_type is None:
            continue

        budget = _extract_budget_per_segment(clause)
        risk = _determine_risk(clause, matched_type)
        if risk == RiskLevel.MEDIUM:
            risk = matched_risk

        actions.append(PlayerAction(
            type=matched_type,
            intent=clause.strip(),
            budget=budget,
            risk_level=risk,
        ))
        seen_types.add(matched_type)

        if len(actions) >= 5:
            break

    # ── Step 4: Add fundraising action if detected ────────────────────────
    if fundraise_amount > 0 and ActionType.FUNDRAISING not in seen_types and len(actions) < 5:
        actions.append(PlayerAction(
            type=ActionType.FUNDRAISING,
            intent=f"融资{fundraise_amount // 10_000}万出让{equity_offered}%",
            budget=0,  # fundraising doesn't consume budget
            risk_level=RiskLevel.LOW,
            fundraise_amount=fundraise_amount,
            equity_offered=equity_offered,
        ))

    return ActionPlan(raw_input=raw_input, actions=actions)
