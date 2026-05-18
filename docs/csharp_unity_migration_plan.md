# C# / Unity 迁移方案

Status: active migration preparation
Date: 2026-05-18

## 1. Direction

Startup Sim will shift from frontend polish to portable gameplay-core preparation.

The Web frontend is now downgraded to a rule validation bench: it should keep opening sessions, submitting turns, and displaying settled facts, but it is no longer the target presentation layer.

The long-term presentation layer is Unity. The long-term rule layer is `StartupSim.Core`.

## 2. Architecture

```text
csharp/
  StartupSim.Core/              Pure C# gameplay core, no UnityEngine dependency
  golden-cases/                 Python reference outputs for C# parity tests

unity/
  StartupSimUnity/
    Assets/Scripts/StartupSim/  Unity adapter components and presenters
```

`StartupSim.Core` owns portable contracts and deterministic gameplay services:

- `ActionPlan`
- `ActionType`
- `GameState`
- `GameMetrics`
- `PlayerAction`
- `RiskLevel`
- `TurnCommand`
- `TurnResult`
- `ScenarioDefinition`
- `ITurnEngine`
- `ActionParser`
- minimal `DeterministicTurnEngine` settlement for product, marketing, team, strategy, fundraising, multi-action turns, and bankruptcy guard

Unity owns only presentation and input:

- office room hotspots
- prepared action display
- turn execution presenter
- API or local-core bridge

Unity components must not settle cash, users, product score, valuation, board state, competitor state, or endings.

## 3. Migration Rules

1. `StartupSim.Core` must not reference `UnityEngine`.
2. Unity scripts may reference `StartupSim.Core`, but they must not duplicate TurnEngine rules.
3. Python remains the reference implementation until C# golden tests cover the same scenarios.
4. Web 前端降级为规则验证台，不继续作为最终游戏表现层大规模打磨。
5. Any migrated rule must have a golden case before it is considered portable.

## 4. Golden Tests

黄金测试 compare fixed inputs and outputs:

- initial state + command
- expected metric delta
- expected ending status
- expected board / competitor / replay facts

The first golden case is:

- `month01_product_investment.json`
- command: `花10万研发产品`
- authority: `python-turn-engine-reference`

The first parser golden fixture is:

- `action_parser_multi.json`
- commands: mixed R&D, marketing, hiring, and fundraising inputs
- authority: `python-action-parser-reference`

The first C# portable turn fixture is:

- `turn_engine_minimal.json`
- commands: product budget, marketing budget, fundraising + multi-action, and bankruptcy guard
- authority: `csharp-portable-turn-slice`

`StartupSim.Core.Tests` is the compile gate for the portable C# layer. It currently verifies:

- deterministic turn execution for the first product-investment slice
- C# `ActionParser.ParseMulti()` behavior against segmented budgets and fundraising terms
- minimal C# turn settlement for product, marketing, team, strategy, fundraising, multi-action turns, and bankruptcy guard
- input state immutability
- unknown-command fallback behavior
- golden fixtures imported from the Python reference layer

CI must run:

```bash
dotnet test csharp/StartupSim.Core.Tests/StartupSim.Core.Tests.csproj --configuration Release
```

Local Windows development can use a repo-local SDK under `.work/dotnet`; `.work/`, `csharp/**/bin/`, and `csharp/**/obj/` are intentionally ignored.

## 5. Unity Component Preparation

The first Unity vertical slice should contain:

1. An office scene.
2. Five room hotspots.
3. A prepared action presenter.
4. A turn executor presenter.
5. A bridge that can call the current HTTP API or later swap to `StartupSim.Core`.
6. `PreparedActionSnapshot` for displaying parsed action type, budget, fundraising amount, and equity offered.

This lets Unity validate interaction feel while the C# core catches up to the Python reference.

## 6. Near-Term Order

1. Build C# contracts and skeleton engine. Done.
2. Add golden fixtures from Python. Done for parser reference and initial turn reference.
3. Add C# test project and CI compile gate. Done.
4. Port `ActionParser`. Done for the current `parse_multi()` slice.
5. Port the minimum `TurnEngine` loop. In progress: product, marketing, team, strategy, fundraising, multi-action, and bankruptcy guard are covered.
6. Add Unity office-room vertical slice. In progress: adapter scripts and structured action snapshot exist; Unity scene assembly remains.
7. Decide whether Unity calls local C# core directly or continues through API during transition. Pending.
