"""Investor agent swarm simulation.

Each investor is an independent LLM agent that evaluates the company and
returns a structured investment decision.

Fixes applied:
  - import json is now at module level (was inside a function)
  - investor_row_to_dict() replaces fragile numeric indices (inv[1], inv[2], …)
  - Specific exception types caught; full traceback logged for debugging
"""

import json
import traceback

from openai import OpenAI

from config import LLM_CONFIG
from db import get_investors, investor_row_to_dict

client = OpenAI(api_key=LLM_CONFIG["api_key"], base_url=LLM_CONFIG["base_url"])

INVESTOR_PROMPT = """你是投资人{name}，类型为{type}（aggressive=激进型关注增长，conservative=保守型关注利润，strategic=战略型关注协同，financial=财务型关注LTV/CAC和回报倍数）。

你当前对这家公司的信任度为{trust}/100。你专注投资{stage}阶段，意向支票金额{cmin}万-{cmax}万元。

请基于以下公司数据评估是否投资：
{state}

公司赛道：{track}
CEO的融资诉求：{request}

返回JSON：
{{
  "decision": "invest|reject|wait",
  "amount": 投资金额(万元)或0,
  "valuation_range": "估值区间描述",
  "terms_harshness": "lenient|moderate|harsh",
  "reasoning": "决策理由",
  "conditions": ["附加条件1", "附加条件2"]
}}
"""


def simulate_one_investor(inv_dict: dict, state_dict: dict, user_request: str) -> dict:
    """Simulate a single investor agent's evaluation.

    Args:
        inv_dict: Named dict from investor_row_to_dict().
        state_dict: Company state dict from state_row_to_dict().
        user_request: The CEO's natural-language fundraising ask.

    Returns:
        Parsed JSON decision dict.
    """
    prompt = INVESTOR_PROMPT.format(
        name=inv_dict["name"],
        type=inv_dict["type"],
        trust=inv_dict["trust_score"],
        stage=inv_dict["focus_stage"],
        cmin=inv_dict["check_size_min"],
        cmax=inv_dict["check_size_max"],
        state=state_dict,
        track=state_dict.get("track", ""),
        request=user_request,
    )

    resp = client.chat.completions.create(
        model=LLM_CONFIG["model"],
        messages=[{"role": "system", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,  # slightly higher for diversity
    )

    return json.loads(resp.choices[0].message.content)


def simulate_investors(state_dict: dict, user_request: str) -> dict:
    """Run all investor agents and return a summary.

    Args:
        state_dict: Company state dict.
        user_request: CEO's fundraising ask.

    Returns:
        {"results": [...], "summary": str, "invest_count": int}
    """
    investors = get_investors()
    results = []

    for row in investors:
        inv = investor_row_to_dict(row)
        try:
            r = simulate_one_investor(inv, state_dict, user_request)
            r["investor_name"] = inv["name"]
            r["investor_type"] = inv["type"]
            results.append(r)
        except json.JSONDecodeError:
            results.append(
                {
                    "investor_name": inv["name"],
                    "decision": "error",
                    "reasoning": "LLM returned invalid JSON",
                }
            )
        except Exception:
            results.append(
                {
                    "investor_name": inv["name"],
                    "decision": "error",
                    "reasoning": traceback.format_exc(),
                }
            )

    # Build summary
    decisions = [r for r in results if r.get("decision") == "invest"]
    summary = (
        f"共{len(investors)}位投资人评估: "
        f"{len(decisions)}位愿意投资, "
        f"{len(investors) - len(decisions)}位拒绝/观望。\n"
    )
    for r in decisions:
        summary += (
            f"- {r['investor_name']}({r['investor_type']}): "
            f"投{r['amount']}万, 条款{r.get('terms_harshness', '?')}\n"
        )
    for r in results:
        if r.get("decision") not in ("invest", "error"):
            summary += (
                f"- {r['investor_name']}: {r.get('decision', '?')} — " f"{r.get('reasoning', '')}\n"
            )

    return {
        "results": results,
        "summary": summary,
        "invest_count": len(decisions),
    }
