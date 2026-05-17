"""AgentPipeline — 4-step reasoning engine for the startup simulator.

Step 1: Load company state
Step 2: Parse user intent  (LLM)
Step 3: Run investor swarm if fundraising
Step 4: StateGuard validation + DB write-back

Fixes applied:
  - state_row_to_dict() replaces fragile numeric indices
  - import json at module level
  - try/except around LLM API call with fallback narrative
"""

import json

from openai import OpenAI

from agents import simulate_investors
from config import LLM_CONFIG
from db import get_state, log_event, state_row_to_dict, update_state
from guard import validate

client = OpenAI(api_key=LLM_CONFIG["api_key"], base_url=LLM_CONFIG["base_url"])

SYSTEM_PROMPT = """你是一个创业模拟器的AI世界引擎。玩家是创业公司CEO，每回合输入战略决策。

你的任务：
1. 解析玩家的自然语言意图
2. 结合公司当前状态进行推演
3. 返回结构化的推演结果

公司状态包含：现金(万元)、烧钱率(万元/月)、MRR(万元/月)、团队人数、团队士气、产品阶段、创始人持股、当前融资轮次、市场环境、赛道。

赛道会影响投资人态度：热门赛道估值高但泡沫风险大，冷门赛道估值低但竞争小。

对于融资类决策，你会收到投资人群体仿真的结果。

返回JSON格式：
{
  "intent": "fundraise|hire|price_change|feature|layoff|other",
  "reasoning": "推演逻辑简述",
  "state_changes": {"cash": 新值, ...},
  "events": ["事件描述1", "事件描述2"],
  "narrative": "给玩家的叙事反馈"
}
"""


def parse_intent(user_input: str, state_dict: dict) -> dict:
    """Step 2: Parse CEO's natural-language intent via LLM."""
    try:
        resp = client.chat.completions.create(
            model=LLM_CONFIG["model"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"当前状态: {state_dict}\n\n"
                    f"CEO决策: {user_input}\n\n"
                    f"解析意图并推演后果，返回JSON。",
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        return json.loads(resp.choices[0].message.content)
    except (json.JSONDecodeError, Exception) as exc:
        return {
            "intent": "other",
            "reasoning": f"LLM调用失败: {exc}",
            "state_changes": {},
            "events": [],
            "narrative": f"⚠️ AI引擎暂时无法响应: {exc}\n请重试或换个说法。",
        }


def process(user_input: str) -> dict:
    """Main reasoning pipeline — run one turn of the simulation."""
    # Steps 1–2: Load state
    state_row = get_state()
    state_dict = state_row_to_dict(state_row)

    # Step 3: LLM intent parsing + world-model reasoning
    result = parse_intent(user_input, state_dict)

    # Step 3b: If fundraising, run investor swarm
    if result.get("intent") == "fundraise":
        inv_result = simulate_investors(state_dict, user_input)
        result["investor_simulation"] = inv_result
        result["narrative"] += f"\n\n📊 投资人仿真结果:\n{inv_result['summary']}"

    # Step 4: StateGuard validation
    validated = validate(result.get("state_changes", {}), state_dict)
    if not validated["passed"]:
        result["narrative"] += f"\n\n⚠️ StateGuard拦截:\n{validated['message']}"
        result["state_changes"] = validated["corrected"]

    # Step 5: Persist to DB
    if result.get("state_changes"):
        update_state(**result["state_changes"])

    # Log events
    for evt in result.get("events", []):
        log_event(state_dict["turn"], "game_event", evt)

    return result
