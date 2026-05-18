# Startup Sim Frontend API Contract

Status: Web validation bench API contract
Date: 2026-05-18

The Web validation bench talks to a small local HTTP API. The Python simulation remains the complete reference implementation for game rules while C# Core gradually becomes the Godot runtime rules layer.

## Data Shape

### GameStateView

```json
{
  "session_id": 1,
  "status": "active",
  "metrics": {
    "month": 1,
    "cash": 1000000,
    "cash_change": 0,
    "cash_coverage_label": "现金流可支撑时间",
    "cash_coverage_months": 8.3,
    "mrr": 0,
    "mrr_change": 0,
    "users": 0,
    "users_change": 0,
    "product_score": 20,
    "product_change": 0,
    "reputation": 50,
    "founder_equity": 100,
    "valuation": 2640000
  },
  "stage": {
    "company_name": "NimbusAI",
    "week_label": "Week 1, Mon",
    "focus": "活下去、做产品、拿到下一轮机会"
  },
  "core_tension": {
    "title": "产品推进 vs 现金消耗",
    "description": "继续研发会提升产品，但现金流可支撑时间会缩短。",
    "severity": "medium",
    "next_focus": "先验证产品改善能否转化成增长。"
  },
  "insight": {
    "title": "本月经营洞察",
    "description": "产品还在早期，建议先用小预算验证客户需求。"
  },
  "phase_goals": {
    "phase_label": "0-12个月",
    "title": "早期生存目标",
    "summary": "先让产品、现金流和用户反馈进入可验证节奏。",
    "objectives": [
      {
        "id": "product-readiness",
        "title": "提升产品成熟度",
        "status": "进行中",
        "progress_label": "产品 20/35",
        "action_directions": ["研发投入", "客户访谈", "小范围试点"],
        "risk_hint": "不要在客户验证不足时一次性加大投放。"
      }
    ]
  },
  "board": [
    {
      "name": "CFO",
      "role": "财务负责人",
      "message": "现金仍可支撑一段时间，但要控制固定支出。",
      "confidence": 82
    }
  ],
  "competitors": [
    {
      "name": "快答科技",
      "status": "保持跟进",
      "mrr": 24000,
      "trend": "up"
    }
  ],
  "advice_entry": {
    "label": "查看建议",
    "summary": "输入「建议」查看详情"
  },
  "ending": {
    "type": "none",
    "description": ""
  }
}
```

## Endpoints

### `GET /api/health`

Returns service status.

Response:

```json
{ "ok": true, "service": "startup-sim-api" }
```

### `POST /api/sessions`

Creates a new local game session.

Request:

```json
{
  "player_name": "Player",
  "company_name": "NimbusAI",
  "scenario_id": "ai_customer_service_saas",
  "difficulty": "normal"
}
```

Response: `GameStateView`

### `GET /api/sessions/{session_id}`

Returns the latest state for a session.

Response: `GameStateView`

### `POST /api/sessions/{session_id}/turns`

Processes one player command.

Request:

```json
{
  "command": "花10万研发产品"
}
```

Response:

```json
{
  "state": "GameStateView",
  "turn": {
    "month": 1,
    "delta_reasons": ["product: 预算=100000, 风险=medium"],
    "parsed_actions": [],
    "events": [],
    "customer_response": {},
    "raw_competitor_moves": [],
    "turn_facts": {
      "month": 1,
      "command": "<player command>",
      "changes": [
        {
          "metric": "cash",
          "label": "<short metric label>",
          "delta": -220000,
          "value": "-220000",
          "tone": "bad"
        }
      ],
      "replay_basis": ["product: budget=100000, risk=medium"],
      "next_pressure": "<post-settlement rule pressure>",
      "authority": "backend-turn-engine"
    },
    "role_memory": [
      {
        "role_id": "cfo",
        "role_name": "CFO",
        "month": 1,
        "fact": "cash changed by -220000",
        "implication": "<settled role implication>",
        "source": "settled-turn-facts"
      }
    ],
    "memory_history": [
      {
        "role_id": "cfo",
        "role_name": "CFO",
        "month": 1,
        "fact": "cash changed by -220000",
        "implication": "<settled role implication>",
        "source": "settled-turn-facts"
      }
    ],
    "recent_role_memory": [
      {
        "role_id": "cfo",
        "role_name": "CFO",
        "month": 1,
        "fact": "cash changed by -220000",
        "implication": "<settled role implication>",
        "source": "settled-turn-facts"
      }
    ],
    "office_signals": [
      {
        "id": "month-1-core-tension",
        "room_id": "product",
        "title": "<settled core tension title>",
        "description": "<settled core tension description>",
        "severity": "low",
        "source": "settled-core-tension",
        "visual_intent": "surface-in-office"
      }
    ],
    "story_events": [
      {
        "id": "month-1-insight",
        "title": "<settled event title>",
        "description": "<settled event description>",
        "tone": "neutral",
        "source": "business-insight"
      }
    ],
    "objective_updates": [
      {
        "id": "product-readiness",
        "title": "提升产品成熟度",
        "status": "推进中",
        "summary": "产品成熟度目标有推进。"
      }
    ]
  }
}
```

`turn.turn_facts` is the first backend TurnFacts serializer slice. It is derived from the settled `TurnResult`, not from frontend UI state or command preview text. `changes` contains backend metric facts and short labels; frontend renderers decide layout, animation, and emphasis.

`phase_goals` is a renderer-neutral objective guide for the current stage. It may provide short action directions and risk hints, but it must not include executable `command`, `example_input`, or one-click action fields. The player still chooses the actual CEO command.

`turn.role_memory` is derived from settled TurnFacts plus post-turn role feedback in `TurnResult`. `turn.memory_history` and `turn.recent_role_memory` are read from persisted SQLite `role_memory_history` rows after the current turn is saved; newest memories are returned first. `turn.office_signals` is derived from settled state, core tension, and business insight. `turn.story_events` is derived from settled rule events, competitor moves, or business insight fallback. `turn.objective_updates` is derived from settled state and delta after the turn; it reports objective progress only and must not include executable command text. These fields are renderer-neutral: the backend supplies facts and short text, while frontend renderers decide placement, animation, and visual treatment.

### `GET /api/sessions/{session_id}/review`

Returns a read-only compact post-game review snapshot. This endpoint must not advance the month, mutate state, or change settlement results.

Response:

```json
{
  "session_id": 1,
  "ending_status": "active",
  "review_phase": "阶段复盘",
  "status_copy": "进行中",
  "ending_title": "<review title>",
  "ending_summary": "<review summary>",
  "archive_summary": "<compact in-run archive summary>",
  "archive_timeline": [
    {
      "id": "moment-1",
      "month": 2,
      "title": "<archive moment title>",
      "description": "<archive moment description>",
      "tone": "positive",
      "source": "key_moment"
    }
  ],
  "archive_badges": [
    {
      "title": "<archive badge title>",
      "description": "<archive badge description>",
      "rarity": "common",
      "source": "achievement"
    }
  ],
  "key_moments": [
    {
      "month": 2,
      "title": "<existing title>",
      "description": "<existing description>",
      "impact_type": "positive",
      "display_title": "<compact title>",
      "display_description": "<compact description>",
      "display_tone": "positive"
    }
  ],
  "final_metrics": { "month": 2 },
  "advice_for_next_run": "<review advice>",
  "achievement_cards": [
    {
      "title": "<achievement title>",
      "description": "<achievement description>",
      "rarity": "common",
      "unlocked": true
    }
  ],
  "next_run_suggestions": ["<short suggestion>", "<short suggestion>"],
  "achievements": [],
  "achievement_summary": {
    "total_count": 0,
    "rare_count": 0,
    "summary": "<achievement summary>"
  }
}
```

`review_phase` is `"阶段复盘"` while the session is active and `"终局复盘"` after an ending status. `status_copy` is short frontend-ready copy for the same status class. `key_moments` keeps existing `title` and `description` fields while adding compact `display_*` fields. `achievement_cards` is derived from unlocked achievements only. `next_run_suggestions` returns 2-3 short suggestions derived from `ReviewEngine.advice_for_next_run` plus final cash, product, and user performance; it must not introduce new settlement facts.

`archive_summary`, `archive_timeline`, and `archive_badges` are optional read-only archive projections for the in-game archive tab. Frontend clients display at most 5 timeline items and 3 badges. If these fields are absent, clients may fall back to `ending_summary`, `key_moments`, and `achievement_cards` without requesting a different endpoint. Valid timeline sources are `key_moment`, `action`, `event`, and `snapshot`; valid tones are `positive`, `negative`, and `neutral`.

### `POST /api/sessions/{session_id}/command-preview`

Explains a free-form CEO command before execution. This endpoint is read-only: it must not advance the month or mutate saved state.

Request:

```json
{
  "command": "花10万研发产品，花5万做营销"
}
```

Response:

```json
{
  "status": "ready",
  "summary": "系统将这条 CEO 指令理解为 2 个可执行动作。",
  "guardrail": "这是执行前解释，数值结算仍由 TurnEngine 执行。",
  "actions": [
    {
      "type": "product",
      "label": "产品研发",
      "intent": "花10万研发产品",
      "budget": 100000,
      "budget_label": "10万",
      "risk_label": "中风险",
      "tradeoffs": ["产品 +", "现金 -"]
    }
  ]
}
```

If no action can be recognized, return `status: "needs_clarification"` with an empty `actions` array and a player-facing clarification summary.

### `GET /api/sessions/{session_id}/suggestions`

Returns detailed suggestions on demand.

Response:

```json
{
  "items": [
    {
      "title": "先验证客户需求",
      "description": "小预算研发加客户访谈比一次性重投入更稳。",
      "command": "花10万研发产品",
      "risk_level": "conservative",
      "reason": "保持节奏"
    }
  ],
  "warning": "",
  "recommended_focus": "产品"
}
```

## Error Rules

- Unknown session returns `404`.
- Empty command returns `400`.
- Validation errors return a plain-language `message`.
- Game-ending responses still return `200` for a valid processed turn, with `ending.type` set.

## Copy Rules

- API response fields use English keys.
- Player-facing strings can be Chinese.
- Frontend must render `cash_coverage_months` as "现金流可支撑时间".
- Frontend must not render legacy cash-coverage wording.
