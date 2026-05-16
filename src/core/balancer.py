"""Numerical balancer: runs simulations to verify game balance and diversity.

Uses the real TurnEngine with seed action inputs — no mocking.
Validates that different endings can be reached and game length is reasonable.
"""

from __future__ import annotations

from typing import Dict, List
from collections import Counter

from src.core.difficulty import Difficulty, get_difficulty
from src.core.models import EndingType
from src.core.turn_engine import TurnEngine
from src.db import repository
from src.db.connection import init_db


# ── Seed action sequences for simulation ──────────────────────────────────────

# Each sequence represents a different "play style"
SEED_ACTIONS: List[List[str]] = [
    # Play style 1: heavy product focus
    [
        "研发产品花30万",
        "研发AI功能花25万",
        "招3个工程师 花20万",
        "研发产品花30万",
        "研发产品花20万",
        "市场推广花15万",
        "研发产品花25万",
        "研发产品花20万",
        "市场推广花20万",
        "融资见投资人 花5万",
        "研发产品花20万",
        "市场推广花25万",
    ],
    # Play style 2: aggressive marketing
    [
        "市场推广花30万",
        "广告投放花25万",
        "市场推广花20万",
        "招销售团队 花20万",
        "市场推广花25万",
        "研发产品花15万",
        "市场推广花20万",
        "融资见投资人 花5万",
        "市场推广花30万",
        "广告投放花20万",
        "市场推广花15万",
        "研发产品花20万",
    ],
    # Play style 3: balanced
    [
        "研发产品花15万",
        "市场推广花15万",
        "招3个工程师 花10万",
        "研发产品花20万",
        "市场推广花15万",
        "研发产品花15万",
        "市场推广花10万",
        "研发产品花10万",
        "融资见投资人 花5万",
        "市场推广花15万",
        "研发产品花15万",
        "市场推广花15万",
    ],
    # Play style 4: fundraising-heavy
    [
        "融资见投资人 花5万",
        "研发产品花15万",
        "融资见投资人 花5万",
        "融资见投资人 花5万",
        "市场推广花15万",
        "融资见投资人 花5万",
        "研发产品花15万",
        "市场推广花15万",
        "融资见投资人 花5万",
        "研发产品花10万",
        "融资见投资人 花5万",
        "市场推广花15万",
    ],
    # Play style 5: conservative / survival
    [
        "研发产品花10万",
        "研发产品花10万",
        "研发产品花10万",
        "研发产品花10万",
        "研发产品花10万",
        "市场推广花10万",
        "研发产品花15万",
        "研发产品花15万",
        "研发产品花15万",
        "市场推广花15万",
        "研发产品花20万",
        "市场推广花20万",
    ],
    # Play style 6: reckless spending
    [
        "激进投放市场花50万",
        "疯狂招人花40万",
        "市场推广花50万",
        "广告投放花60万",
        "招人花40万",
        "市场推广花50万",
        "广告投放花50万",
        "招人花50万",
        "市场推广花50万",
        "广告投放花50万",
        "市场推广花60万",
        "广告投放花50万",
    ],
]


def simulate_run(
    turn_engine: TurnEngine,
    difficulty: Difficulty,
    actions: List[str],
    max_months: int = 12,
) -> dict:
    """Simulate one full game with a sequence of actions.

    Args:
        turn_engine: a TurnEngine already initialized with a session
        difficulty: the Difficulty preset
        actions: list of raw input strings, one per turn
        max_months: stop after this many months even if game hasn't ended

    Returns dict with:
        - ending: EndingType value
        - months_played: actual number of months played
        - final_state: CompanyState at end
        - events_triggered: count of events
    """
    ending = EndingType.NONE
    months_played = 0
    event_count = 0

    for i, raw_input in enumerate(actions):
        if i >= max_months:
            break

        state_before = repository.load_state(turn_engine.session_id)
        if state_before is None:
            break

        try:
            result = turn_engine.process_turn(raw_input)
            months_played = result.month
            event_count += len(result.events)

            if result.ending != EndingType.NONE:
                ending = result.ending
                break
        except Exception:
            # If a turn fails (e.g., validation error), skip it
            continue

    # Load final state
    final_state = repository.load_state(turn_engine.session_id)

    return {
        "ending": ending.value if ending else "none",
        "months_played": months_played,
        "final_cash": final_state.cash if final_state else 0,
        "final_mrr": final_state.mrr if final_state else 0,
        "final_product_score": final_state.product_score if final_state else 0,
        "events_triggered": event_count,
    }


def run_balance_check(
    difficulty_name: str = "normal",
    num_runs: int = 6,
    scenario_id: str = "ai_customer_service_saas",
) -> dict:
    """Run balance check for a difficulty level.

    Simulates num_runs games using different seed action strategies.
    Checks:
    - At least 2 different endings appear
    - Average game length is 6-9 months
    - No 100% same ending (diversity check)

    Returns dict with:
        - passed: bool
        - issues: list of issue strings
        - endings: Counter of ending types
        - avg_months: float average game length
        - runs: list of per-run result dicts
    """
    from config import SCENARIOS_PATH
    import yaml

    difficulty = get_difficulty(difficulty_name)
    endings_counter: Counter = Counter()
    all_runs = []

    # Use a subset of seed actions
    seeds_to_use = SEED_ACTIONS[:num_runs]
    if num_runs > len(SEED_ACTIONS):
        seeds_to_use = SEED_ACTIONS * (num_runs // len(SEED_ACTIONS) + 1)
    seeds_to_use = seeds_to_use[:num_runs]

    for i, actions in enumerate(seeds_to_use):
        # Create a fresh session for each run
        init_db()

        # Load scenario and apply difficulty
        if not SCENARIOS_PATH.exists():
            raise FileNotFoundError(f"Scenarios file not found: {SCENARIOS_PATH}")
        with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        scenario_dict = data["scenarios"][scenario_id]
        adjusted = difficulty.apply_to_scenario(scenario_dict)
        init_state = adjusted["initial_state"]

        from src.core.models import CompanyState
        scenario_state = CompanyState(
            cash=init_state["cash"],
            monthly_burn=init_state["monthly_burn"],
            mrr=init_state["mrr"],
            users=init_state["users"],
            product_score=init_state["product_score"],
            team_morale=init_state["team_morale"],
            founder_equity=init_state["founder_equity"],
            board_control=init_state["board_control"],
            market_share=init_state["market_share"],
            reputation=init_state["reputation"],
            month=1,
        )

        session_id = repository.create_session(
            player_name=f"balancer_bot_{i}",
            scenario_id=scenario_id,
            difficulty=difficulty_name,
        )
        repository.init_session_state(session_id, scenario_state)

        # Create engine with difficulty awareness
        engine = TurnEngine(session_id, difficulty=difficulty)

        # Run
        run_result = simulate_run(engine, difficulty, actions)
        run_result["seed_index"] = i
        all_runs.append(run_result)

        endings_counter[run_result["ending"]] += 1

    # ── Checks ────────────────────────────────────────────────────────────────
    issues: List[str] = []
    played_months = [r["months_played"] for r in all_runs if r["months_played"] > 0]
    avg_months = sum(played_months) / len(played_months) if played_months else 0

    # Check: at least 2 different endings
    unique_endings = len(endings_counter)
    if unique_endings < 2:
        issues.append(
            f"Only {unique_endings} unique ending(s) found: {dict(endings_counter)}. "
            f"Expected at least 2 different endings for diversity."
        )

    # Check: average game length 6-9 months
    if avg_months < 6 or avg_months > 9:
        issues.append(
            f"Average game length is {avg_months:.1f} months (expected 6-9)."
        )

    # Check: no 100% same ending
    most_common_count = endings_counter.most_common(1)
    if most_common_count and len(all_runs) > 1:
        if most_common_count[0][1] == len(all_runs):
            issues.append(
                f"All {len(all_runs)} runs ended with the same ending: "
                f"{most_common_count[0][0]}"
            )

    passed = len(issues) == 0

    return {
        "passed": passed,
        "difficulty": difficulty_name,
        "issues": issues,
        "endings": dict(endings_counter),
        "avg_months": round(avg_months, 1),
        "runs": all_runs,
    }
