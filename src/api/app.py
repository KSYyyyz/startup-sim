"""Local HTTP API for the Startup Sim frontend.

This module is intentionally thin: it maps HTTP requests to the existing
repository and TurnEngine layers, then shapes the response for the web UI.
"""

from __future__ import annotations

import json
import math
import sqlite3
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agents import CFO, COO, CTO
from src.agents.competitors import KuaiDaTech, LingxiCSCloud
from src.core.achievement_engine import AchievementEngine
from src.core.action_parser import parse_multi
from src.core.conflict_engine import ConflictEngine
from src.core.models import (
    ActionPlan,
    ActionType,
    CompanyState,
    EndingType,
    RiskLevel,
    StateDelta,
    TurnResult,
)
from src.core.review_engine import ReviewEngine
from src.core.suggestion_engine import SuggestionEngine
from src.core.turn_engine import TurnEngine
from src.db import repository
from src.db.connection import get_connection, init_db

FORBIDDEN_COPY = {
    "跑道": "现金流可支撑时间",
    "Runway": "现金流可支撑时间",
    "runway": "现金流可支撑时间",
}


class CreateSessionRequest(BaseModel):
    player_name: str = Field(default="Player")
    company_name: str = Field(default="NimbusAI")
    scenario_id: str = Field(default="ai_customer_service_saas")
    difficulty: str = Field(default="normal")


class TurnRequest(BaseModel):
    command: str = Field(default="")


def _sanitize_copy(value: Any) -> Any:
    """Replace product-banned wording in nested API payloads."""
    if isinstance(value, str):
        text = value
        for bad, good in FORBIDDEN_COPY.items():
            text = text.replace(bad, good)
        return text
    if isinstance(value, list):
        return [_sanitize_copy(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_copy(item) for key, item in value.items()}
    return value


def _safe_months(value: float) -> float:
    if math.isinf(value):
        return 999.0
    return round(value, 1)


def _load_session_status(session_id: int) -> str:
    conn = get_connection()
    try:
        row = conn.execute("SELECT status FROM game_sessions WHERE id=?", (session_id,)).fetchone()
        if row is None:
            raise KeyError(session_id)
        return row["status"]
    finally:
        conn.close()


def _default_board_feedback(state: CompanyState) -> dict[str, str]:
    empty_plan = ActionPlan(raw_input="", actions=[])
    return {
        member.name: member.speak(state, empty_plan)
        for member in [
            CFO(),
            CTO(),
            COO(),
        ]
    }


def _board_view(feedback: dict[str, str]) -> list[dict[str, Any]]:
    role_map = {
        "CFO": "财务负责人",
        "CTO": "技术负责人",
        "COO": "运营负责人",
    }
    board = []
    for idx, (name, message) in enumerate(feedback.items()):
        board.append(
            {
                "name": name,
                "role": role_map.get(name, "董事会成员"),
                "message": message,
                "confidence": max(68, 88 - idx * 5),
            }
        )
    return board


def _competitor_view_from_moves(moves: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    if moves:
        items = []
        for move in moves:
            delta = move.get("delta") or {}
            trend = "up" if delta.get("market_share", 0) >= 0 else "down"
            items.append(
                {
                    "name": move.get("name", "未知竞品"),
                    "status": move.get("description") or move.get("action") or "保持跟进",
                    "mrr": max(0, 18_000 + int(delta.get("users", 0)) * 40),
                    "trend": trend,
                }
            )
        return items

    competitors = [KuaiDaTech(), LingxiCSCloud()]
    return [
        {
            "name": competitor.name,
            "status": "本月暂无重大动作",
            "mrr": 18_000 + competitor.market_share * 1000,
            "trend": "flat",
        }
        for competitor in competitors
    ]


def _generic_insight(state: CompanyState) -> dict[str, str]:
    if state.cash < state.monthly_burn:
        return {
            "title": "现金流风险",
            "description": "当前现金不足以覆盖下月固定支出，需要立即融资或削减成本。",
        }
    if state.product_score < 40:
        return {
            "title": "产品仍在打磨期",
            "description": "现阶段优先把产品体验做稳，再考虑更大规模获客。",
        }
    return {
        "title": "本月经营洞察",
        "description": "公司状态可继续推进，但要同时关注现金流、产品质量和竞品动作。",
    }


def _state_view(
    session_id: int,
    state: CompanyState,
    *,
    status: str = "active",
    company_name: str = "NimbusAI",
    delta: StateDelta | None = None,
    board_feedback: dict[str, str] | None = None,
    competitor_moves: list[dict[str, Any]] | None = None,
    insight: Any = None,
    ending_type: EndingType | str = EndingType.NONE,
    ending_description: str = "",
) -> dict[str, Any]:
    conflict = ConflictEngine.identify(state)
    cash_change = delta.cash if delta else 0
    mrr_change = delta.mrr if delta else 0
    users_change = delta.users if delta else 0
    product_change = delta.product_score if delta else 0
    insight_view = (
        {
            "title": insight.title,
            "description": insight.description,
        }
        if insight
        else _generic_insight(state)
    )
    ending_value = ending_type.value if isinstance(ending_type, EndingType) else str(ending_type)

    payload = {
        "session_id": session_id,
        "status": status,
        "metrics": {
            "month": state.month,
            "cash": state.cash,
            "cash_change": cash_change,
            "cash_coverage_label": "现金流可支撑时间",
            "cash_coverage_months": _safe_months(state.runway_months),
            "mrr": state.mrr,
            "mrr_change": mrr_change,
            "users": state.users,
            "users_change": users_change,
            "product_score": state.product_score,
            "product_change": product_change,
            "reputation": state.reputation,
            "founder_equity": state.founder_equity,
            "valuation": state.valuation,
        },
        "stage": {
            "company_name": company_name,
            "week_label": f"Week {((state.month - 1) % 4) + 1}, Mon",
            "focus": "活下去、做产品、拿到下一轮机会",
        },
        "core_tension": {
            "title": conflict.title,
            "description": conflict.description,
            "severity": conflict.severity,
            "next_focus": conflict.next_focus,
        },
        "insight": insight_view,
        "board": _board_view(board_feedback or _default_board_feedback(state)),
        "competitors": _competitor_view_from_moves(competitor_moves),
        "advice_entry": {
            "label": "查看建议",
            "summary": "输入「建议」查看详情",
        },
        "ending": {
            "type": ending_value,
            "description": ending_description,
        },
    }
    return _sanitize_copy(payload)


def _suggestions_view(state: CompanyState) -> dict[str, Any]:
    result = SuggestionEngine.generate(state, turn_number=state.month)
    payload = {
        "items": [
            {
                "title": suggestion.title,
                "description": suggestion.description,
                "command": suggestion.example_input,
                "risk_level": suggestion.risk_level,
                "reason": suggestion.reason,
            }
            for suggestion in result.suggestions
        ],
        "warning": result.warning,
        "recommended_focus": result.recommended_focus,
    }
    return _sanitize_copy(payload)


ACTION_LABELS = {
    ActionType.PRODUCT: "产品研发",
    ActionType.MARKETING: "市场营销",
    ActionType.FUNDRAISING: "融资",
    ActionType.TEAM: "团队招聘",
    ActionType.STRATEGY: "战略动作",
}

RISK_LABELS = {
    RiskLevel.LOW: "低风险",
    RiskLevel.MEDIUM: "中风险",
    RiskLevel.HIGH: "高风险",
}

ACTION_TRADEOFFS = {
    ActionType.PRODUCT: ["产品 +", "现金 -"],
    ActionType.MARKETING: ["用户 +", "现金 -"],
    ActionType.FUNDRAISING: ["现金流可支撑时间 +", "股权 -"],
    ActionType.TEAM: ["团队 +", "固定支出 +"],
    ActionType.STRATEGY: ["机会 +", "不确定性 +"],
}


def _money_label(value: int) -> str:
    if value <= 0:
        return "无直接支出"
    if value % 10_000 == 0:
        return f"{value // 10_000}万"
    return f"{value:,}元"


def _change_tone(value: int) -> str:
    if value > 0:
        return "good"
    if value < 0:
        return "bad"
    return "neutral"


def _turn_fact_changes(delta: StateDelta) -> list[dict[str, Any]]:
    change_specs = [
        ("cash", "现金", delta.cash),
        ("mrr", "月经常收入", delta.mrr),
        ("users", "用户", delta.users),
        ("product_score", "产品", delta.product_score),
    ]
    return [
        {
            "metric": metric,
            "label": label,
            "delta": value,
            "value": str(value),
            "tone": _change_tone(value),
        }
        for metric, label, value in change_specs
        if value != 0
    ]


def _turn_facts_view(result: TurnResult) -> dict[str, Any]:
    next_pressure = result.conflict_summary.next_focus if result.conflict_summary else ""
    payload = {
        "month": result.month,
        "command": result.action_plan.raw_input,
        "changes": _turn_fact_changes(result.delta),
        "replay_basis": result.delta.reasons,
        "next_pressure": next_pressure,
        "authority": "backend-turn-engine",
    }
    return _sanitize_copy(payload)


ROLE_MEMORY_METRICS = {
    "CFO": ("cash", "mrr"),
    "CTO": ("product_score",),
    "COO": ("users", "mrr"),
}


def _first_change_for_role(changes: list[dict[str, Any]], role_name: str) -> dict[str, Any] | None:
    preferred_metrics = ROLE_MEMORY_METRICS.get(role_name, ())
    for metric in preferred_metrics:
        for change in changes:
            if change["metric"] == metric:
                return change
    return changes[0] if changes else None


def _role_memory_view(result: TurnResult, turn_facts: dict[str, Any]) -> list[dict[str, Any]]:
    memories = []
    changes = turn_facts["changes"]
    replay_basis = turn_facts["replay_basis"]
    fallback_fact = replay_basis[0] if replay_basis else turn_facts["command"]

    for role_name, implication in result.board_feedback.items():
        change = _first_change_for_role(changes, role_name)
        if change:
            fact = f'{change["metric"]} changed by {change["delta"]}'
        else:
            fact = fallback_fact
        memories.append(
            {
                "role_id": role_name.lower(),
                "role_name": role_name,
                "month": result.month,
                "fact": fact,
                "implication": implication,
                "source": "settled-turn-facts",
            }
        )
    return _sanitize_copy(memories)


def _memory_history_view(session_id: int) -> list[dict[str, Any]]:
    history = repository.list_recent_role_memory(session_id)
    return _sanitize_copy(
        [
            {
                "role_id": item["role_id"],
                "role_name": item["role_name"],
                "month": item["month"],
                "fact": item["fact"],
                "implication": item["implication"],
                "source": item["source"],
            }
            for item in history
        ]
    )


def _room_for_pressure(pressure_type: str) -> str:
    return {
        "cash": "board",
        "equity": "board",
        "pmf": "product",
        "delivery": "product",
        "growth": "sales",
        "competition": "sales",
        "team": "team",
    }.get(pressure_type, "product")


def _room_for_insight(category: str) -> str:
    if "cash" in category or "fundraising" in category:
        return "board"
    if "marketing" in category or "growth" in category:
        return "sales"
    if "product" in category:
        return "product"
    if "team" in category:
        return "team"
    return "product"


def _severity_for_insight(category: str) -> str:
    if category in {"cash_warning", "fundraising_fail", "risk_alert"}:
        return "medium"
    return "low"


def _office_signals_view(result: TurnResult) -> list[dict[str, Any]]:
    signals = []
    if result.conflict_summary:
        conflict = result.conflict_summary
        signals.append(
            {
                "id": f"month-{result.month}-core-tension",
                "room_id": _room_for_pressure(conflict.pressure_type),
                "title": conflict.title,
                "description": conflict.description,
                "severity": conflict.severity,
                "source": "settled-core-tension",
                "visual_intent": "surface-in-office",
            }
        )
    if result.insight:
        insight = result.insight
        signals.append(
            {
                "id": f"month-{result.month}-business-insight",
                "room_id": _room_for_insight(insight.category),
                "title": insight.title,
                "description": insight.description,
                "severity": _severity_for_insight(insight.category),
                "source": "settled-business-insight",
                "visual_intent": "surface-in-office",
            }
        )
    return _sanitize_copy(signals)


def _story_event_tone(delta: StateDelta) -> str:
    if delta.cash < 0 and not (delta.product_score > 0 or delta.users > 0 or delta.mrr > 0):
        return "warning"
    if delta.cash < 0:
        return "bad"
    if delta.product_score > 0 or delta.users > 0 or delta.mrr > 0:
        return "good"
    return "neutral"


def _story_events_view(result: TurnResult) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for idx, event in enumerate(result.events[:3], start=1):
        events.append(
            {
                "id": f"month-{result.month}-event-{idx}",
                "title": event.event_type,
                "description": event.description,
                "tone": _story_event_tone(event.delta),
                "source": "rule-event",
            }
        )

    for idx, move in enumerate(result.competitor_moves[:2], start=1):
        events.append(
            {
                "id": f"month-{result.month}-competitor-{idx}",
                "title": move.get("name", "竞品动态"),
                "description": move.get("description")
                or move.get("action")
                or "竞品本月保持观察。",
                "tone": (
                    "warning"
                    if (move.get("delta") or {}).get("market_share", 0) >= 0
                    else "opportunity"
                ),
                "source": "competitor-fact",
            }
        )

    if not events and result.insight:
        events.append(
            {
                "id": f"month-{result.month}-insight",
                "title": result.insight.title,
                "description": result.insight.description,
                "tone": "neutral",
                "source": "business-insight",
            }
        )
    return _sanitize_copy(events)


def _review_phase(ending_status: str) -> str:
    return "阶段复盘" if ending_status == "active" else "终局复盘"


def _review_status_copy(ending_status: str) -> str:
    return "进行中" if ending_status == "active" else "已结束"


def _review_key_moments_view(key_moments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    moments = []
    for moment in key_moments:
        item = dict(moment)
        title = item.get("title") or "关键节点"
        description = item.get("description") or ""
        item["display_title"] = title
        item["display_description"] = description
        item["display_tone"] = item.get("impact_type") or "neutral"
        moments.append(item)
    return moments


def _achievement_cards_view(achievements: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "title": item.title,
            "description": item.description,
            "rarity": item.rarity,
            "unlocked": True,
        }
        for item in achievements
    ]


def _first_sentence(text: str, max_chars: int = 48) -> str:
    clean = " ".join(str(_sanitize_copy(text or "")).split())
    if "。" in clean:
        clean = clean.split("。", 1)[0]
    clean = clean.strip(" 。")
    if not clean:
        clean = "复盘本局关键选择，下次开局先设定一个主目标"
    if len(clean) > max_chars:
        clean = clean[:max_chars].rstrip()
    return f"{clean}。"


def _next_run_suggestions_view(review: Any, final_state: CompanyState) -> list[str]:
    suggestions = [_first_sentence(review.advice_for_next_run)]
    coverage_months = (
        final_state.cash / final_state.monthly_burn if final_state.monthly_burn > 0 else 999
    )

    if coverage_months < 3:
        suggestions.append("优先控制现金消耗，先保证下轮决策空间。")
    elif coverage_months >= 8:
        suggestions.append("利用资金余量做小步实验，验证增长效率。")
    else:
        suggestions.append("保持资金纪律，把预算集中到最能验证假设的动作。")

    if final_state.product_score < 55:
        suggestions.append("继续打磨产品核心体验，再放大获客投入。")
    elif final_state.users < 200:
        suggestions.append("用低成本渠道获取种子用户，观察真实反馈。")
    else:
        suggestions.append("复盘高质量用户来源，集中资源复制有效渠道。")

    unique = []
    for item in suggestions:
        clean = _sanitize_copy(item)
        if clean and clean not in unique:
            unique.append(clean)
    return unique[:3]


def _review_payload(session_id: int) -> dict[str, Any]:
    final_state = repository.load_state(session_id)
    session = repository.get_session_status(session_id)
    if session is None:
        raise KeyError(session_id)

    snapshots = repository.list_snapshots(session_id)
    actions = repository.list_actions(session_id)
    events = repository.list_events(session_id)
    ending_status = session.get("status", "active")
    review = ReviewEngine.generate_review(
        initial_state=CompanyState(),
        snapshots=snapshots,
        action_logs=actions,
        event_logs=events,
        final_state=final_state,
        ending_status=ending_status,
        session_id=session_id,
    )
    achievements = AchievementEngine.evaluate(
        final_state=final_state,
        ending_status=ending_status,
        review=review,
        snapshots=snapshots,
    )
    payload = json.loads(review.model_dump_json())
    payload["review_phase"] = _review_phase(ending_status)
    payload["status_copy"] = _review_status_copy(ending_status)
    payload["key_moments"] = _review_key_moments_view(payload.get("key_moments", []))
    payload["achievements"] = [
        json.loads(item.model_dump_json()) for item in achievements.achievements
    ]
    payload["achievement_cards"] = _achievement_cards_view(achievements.achievements)
    payload["achievement_summary"] = {
        "total_count": achievements.total_count,
        "rare_count": achievements.rare_count,
        "summary": achievements.summary,
    }
    payload["next_run_suggestions"] = _next_run_suggestions_view(review, final_state)
    return _sanitize_copy(payload)


def _command_preview_view(command: str) -> dict[str, Any]:
    plan = parse_multi(command)
    actions = [
        {
            "type": action.type.value,
            "label": ACTION_LABELS.get(action.type, "经营动作"),
            "intent": action.intent,
            "budget": (
                action.fundraise_amount if action.type == ActionType.FUNDRAISING else action.budget
            ),
            "budget_label": _money_label(
                action.fundraise_amount if action.type == ActionType.FUNDRAISING else action.budget
            ),
            "risk_label": RISK_LABELS.get(action.risk_level, "中风险"),
            "tradeoffs": ACTION_TRADEOFFS.get(action.type, ["影响待观察"]),
        }
        for action in plan.actions
    ]
    if not actions:
        return _sanitize_copy(
            {
                "status": "needs_clarification",
                "summary": "没有识别到可执行动作。可以尝试写明预算和方向，例如：花10万研发产品。",
                "guardrail": "这是执行前解释，数值结算仍由 TurnEngine 执行。",
                "actions": [],
            }
        )
    payload = {
        "status": "ready",
        "summary": f"系统将这条 CEO 指令理解为 {len(actions)} 个可执行动作。",
        "guardrail": "这是执行前解释，数值结算仍由 TurnEngine 执行。",
        "actions": actions,
    }
    return _sanitize_copy(payload)


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(title="Startup Sim API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {"ok": True, "service": "startup-sim-api"}

    @app.post("/api/sessions")
    def create_session(request: CreateSessionRequest) -> dict[str, Any]:
        session_id = repository.create_session(
            request.player_name,
            scenario_id=request.scenario_id,
            difficulty=request.difficulty,
        )
        state = CompanyState()
        repository.init_session_state(session_id, state)
        return _state_view(session_id, state, company_name=request.company_name)

    @app.get("/api/sessions/{session_id}")
    def get_session(session_id: int):
        try:
            state = repository.load_state(session_id)
            status = _load_session_status(session_id)
        except (RuntimeError, KeyError, sqlite3.Error):
            return JSONResponse(status_code=404, content={"message": "未找到这个游戏存档。"})
        return _state_view(session_id, state, status=status)

    @app.post("/api/sessions/{session_id}/turns")
    def submit_turn(session_id: int, request: TurnRequest):
        command = request.command.strip()
        if not command:
            return JSONResponse(status_code=400, content={"message": "请输入本回合要执行的动作。"})

        try:
            repository.load_state(session_id)
        except RuntimeError:
            return JSONResponse(status_code=404, content={"message": "未找到这个游戏存档。"})

        try:
            result = TurnEngine(session_id).process_turn(command)
        except Exception as exc:
            return JSONResponse(status_code=400, content={"message": str(exc)})

        status = result.ending.value if result.ending != EndingType.NONE else "active"
        state = _state_view(
            session_id,
            result.state_after,
            status=status,
            delta=result.delta,
            board_feedback=result.board_feedback,
            competitor_moves=result.competitor_moves,
            insight=result.insight,
            ending_type=result.ending,
            ending_description=result.ending_description,
        )
        turn_facts = _turn_facts_view(result)
        role_memory = _role_memory_view(result, turn_facts)
        repository.save_role_memory_history(session_id, role_memory)
        memory_history = _memory_history_view(session_id)
        payload = {
            "state": state,
            "turn": {
                "month": result.month,
                "delta_reasons": result.delta.reasons,
                "events": [event.model_dump() for event in result.events],
                "customer_response": result.customer_response,
                "raw_competitor_moves": result.competitor_moves,
                "parsed_actions": [action.model_dump() for action in result.action_plan.actions],
                "turn_facts": turn_facts,
                "role_memory": role_memory,
                "memory_history": memory_history,
                "recent_role_memory": memory_history,
                "office_signals": _office_signals_view(result),
                "story_events": _story_events_view(result),
            },
        }
        return _sanitize_copy(payload)

    @app.get("/api/sessions/{session_id}/suggestions")
    def suggestions(session_id: int):
        try:
            state = repository.load_state(session_id)
        except RuntimeError:
            return JSONResponse(status_code=404, content={"message": "未找到这个游戏存档。"})
        return _suggestions_view(state)

    @app.get("/api/sessions/{session_id}/review")
    def review(session_id: int):
        try:
            return _review_payload(session_id)
        except (RuntimeError, KeyError, sqlite3.Error):
            return JSONResponse(status_code=404, content={"message": "未找到这个游戏存档。"})

    @app.post("/api/sessions/{session_id}/command-preview")
    def command_preview(session_id: int, request: TurnRequest):
        command = request.command.strip()
        if not command:
            return JSONResponse(status_code=400, content={"message": "请输入要解释的 CEO 指令。"})
        try:
            repository.load_state(session_id)
        except RuntimeError:
            return JSONResponse(status_code=404, content={"message": "未找到这个游戏存档。"})
        return _command_preview_view(command)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.app:app", host="127.0.0.1", port=8000, reload=True)
