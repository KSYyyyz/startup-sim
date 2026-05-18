"""Local HTTP API for the Startup Sim frontend.

This module is intentionally thin: it maps HTTP requests to the existing
repository and TurnEngine layers, then shapes the response for the web UI.
"""

from __future__ import annotations

import math
import sqlite3
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.agents import CFO, COO, CTO
from src.agents.competitors import KuaiDaTech, LingxiCSCloud
from src.core.conflict_engine import ConflictEngine
from src.core.insight_engine import InsightEngine
from src.core.models import ActionPlan, CompanyState, EndingType, StateDelta
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
        payload = {
            "state": state,
            "turn": {
                "month": result.month,
                "delta_reasons": result.delta.reasons,
                "events": [event.model_dump() for event in result.events],
                "customer_response": result.customer_response,
                "raw_competitor_moves": result.competitor_moves,
                "parsed_actions": [action.model_dump() for action in result.action_plan.actions],
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

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.app:app", host="127.0.0.1", port=8000, reload=True)
