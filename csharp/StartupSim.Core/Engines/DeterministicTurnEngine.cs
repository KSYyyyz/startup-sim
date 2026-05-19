using System;
using StartupSim.Core.Contracts;
using StartupSim.Core.Parsing;

namespace StartupSim.Core.Engines
{
    public sealed class DeterministicTurnEngine : ITurnEngine
    {
        public TurnResult Execute(GameState currentState, TurnCommand command)
        {
            if (currentState == null)
            {
                throw new ArgumentNullException(nameof(currentState));
            }

            var next = currentState.Clone();
            var startingMonthlyBurn = next.Metrics.MonthlyBurn;
            next.Metrics.Month += 1;

            var result = new TurnResult
            {
                State = next,
                NextPressure = "下月需要选择一个更明确的经营动作。"
            };

            var plan = ActionParser.ParseMulti(command?.RawText ?? string.Empty);
            foreach (var action in plan.Actions)
            {
                ApplyAction(next, result, action);
            }

            ApplyMonthlyOperations(next, result, startingMonthlyBurn);
            ApplyPostTurnStateChecks(next, result);

            if (result.ChangedMetrics.Count == 0)
            {
                result.ReplayBasis.Add("本回合保持观察，尚未形成强变化。");
                result.ChangedMetrics.Add("现金 稳定");
            }

            return result;
        }

        public TurnResult ExecuteBusinessIntent(GameState currentState, BusinessIntentSnapshot intent)
        {
            if (currentState == null)
            {
                throw new ArgumentNullException(nameof(currentState));
            }

            intent = intent ?? new BusinessIntentSnapshot();
            var next = currentState.Clone();
            var startingMonthlyBurn = Math.Max(next.Metrics.MonthlyBurn, intent.MonthlyFixedCost);
            next.Metrics.Month += 1;

            var result = new TurnResult
            {
                State = next,
                NextPressure = "下月继续观察办公室产能是否转化为收入增长。"
            };

            foreach (var action in BuildActionsFromBusinessIntent(intent))
            {
                ApplyAction(next, result, action);
            }

            if (intent.MonthlyFixedCost > next.Metrics.MonthlyBurn)
            {
                next.Metrics.MonthlyBurn = intent.MonthlyFixedCost;
                result.ChangedMetrics.Add($"办公室固定支出 {intent.MonthlyFixedCost / 10_000m:0}万");
            }

            ApplyMonthlyOperations(next, result, startingMonthlyBurn);
            ApplyPostTurnStateChecks(next, result);
            BuildBusinessFacts(next, result, intent);

            if (result.ChangedMetrics.Count == 0)
            {
                result.ReplayBasis.Add("本月办公室产能保持观察，尚未形成强变化。");
                result.ChangedMetrics.Add("现金 稳定");
            }

            return result;
        }

        private static PlayerAction[] BuildActionsFromBusinessIntent(BusinessIntentSnapshot intent)
        {
            var actions = new System.Collections.Generic.List<PlayerAction>();
            if (intent.ProductFocus > 0m)
            {
                actions.Add(new PlayerAction
                {
                    Type = ActionType.Product,
                    Intent = "办公室研发产能转化为产品推进",
                    Budget = intent.ProductFocus * 10_000m,
                    RiskLevel = RiskLevel.Medium
                });
            }

            if (intent.SalesFocus > 0m)
            {
                actions.Add(new PlayerAction
                {
                    Type = ActionType.Marketing,
                    Intent = "办公室销售产能转化为获客增长",
                    Budget = intent.SalesFocus * 8_000m,
                    RiskLevel = RiskLevel.Medium
                });
            }

            if (intent.StabilityFocus + intent.OrganizationFocus > 0m)
            {
                actions.Add(new PlayerAction
                {
                    Type = ActionType.Strategy,
                    Intent = "办公室稳定性转化为经营韧性",
                    Budget = (intent.StabilityFocus + intent.OrganizationFocus) * 4_000m,
                    RiskLevel = RiskLevel.Low
                });
            }

            return actions.ToArray();
        }

        private static void BuildBusinessFacts(
            GameState state,
            TurnResult result,
            BusinessIntentSnapshot intent)
        {
            result.BusinessFacts.Add(new BusinessFactSnapshot
            {
                FactType = "office_intent",
                Title = "办公室产能已进入经营结算",
                Description = string.IsNullOrWhiteSpace(intent.SourceSummary)
                    ? "本月根据办公室区域、设施和员工状态生成经营意图。"
                    : intent.SourceSummary,
                Severity = "info"
            });

            result.BusinessFacts.Add(new BusinessFactSnapshot
            {
                FactType = "cash",
                Title = "现金流可支撑时间",
                Description = state.Metrics.MonthlyBurn <= 0m
                    ? "当前没有固定消耗压力。"
                    : $"{state.Metrics.Cash / state.Metrics.MonthlyBurn:0.0} 个月",
                Severity = state.Metrics.MonthlyBurn > 0m
                    && state.Metrics.Cash / state.Metrics.MonthlyBurn < 3m
                        ? "warning"
                        : "info"
            });

            if (state.Metrics.MonthlyRecurringRevenue > 0m)
            {
                result.BusinessFacts.Add(new BusinessFactSnapshot
                {
                    FactType = "revenue",
                    Title = "收入闭环",
                    Description = $"月经常收入达到 {state.Metrics.MonthlyRecurringRevenue / 10_000m:0} 万。",
                    Severity = "positive"
                });
            }
        }

        private static void ApplyMonthlyOperations(GameState state, TurnResult result, decimal monthlyBurn)
        {
            if (monthlyBurn > 0m)
            {
                state.Metrics.Cash -= monthlyBurn;
                result.ChangedMetrics.Add($"月度消耗 -{monthlyBurn / 10_000m:0}万");
                result.ReplayBasis.Add("月度固定消耗已结算。");
            }

            if (state.Metrics.EmployeeCount >= 5)
            {
                state.Metrics.ProductScore += 1;
                result.ChangedMetrics.Add("团队自然学习 产品 +1");
                result.ReplayBasis.Add("团队自然学习带来产品分提升。");
            }
        }

        private static void ApplyPostTurnStateChecks(GameState state, TurnResult result)
        {
            if (state.Metrics.Cash >= 0m)
            {
                return;
            }

            state.Metrics.Cash = 0m;
            state.Status = "bankruptcy";
            result.ChangedMetrics.Add("公司破产");
            result.ReplayBasis.Add("现金为负，经营无法继续。");
            result.NextPressure = "现金流断裂，公司进入破产结局。";
        }

        private static void ApplyAction(GameState state, TurnResult result, PlayerAction action)
        {
            switch (action.Type)
            {
                case ActionType.Product:
                    ApplyProductAction(state, result, action);
                    break;
                case ActionType.Marketing:
                    ApplyMarketingAction(state, result, action);
                    break;
                case ActionType.Team:
                    ApplyTeamAction(state, result, action);
                    break;
                case ActionType.Strategy:
                    ApplyStrategyAction(state, result, action);
                    break;
                case ActionType.Fundraising:
                    ApplyFundraisingAction(state, result, action);
                    break;
                default:
                    throw new ArgumentOutOfRangeException(nameof(action), action.Type, null);
            }
        }

        private static void ApplyProductAction(GameState state, TurnResult result, PlayerAction action)
        {
            var budget = action.Budget > 0m ? action.Budget : 100_000m;
            var productGain = Math.Max(
                1,
                (int)(budget / 80_000m) + state.Metrics.EmployeeCount / 3 + state.Metrics.TeamMorale / 10);
            state.Metrics.Cash -= budget;
            state.Metrics.ProductScore += productGain;
            state.Metrics.MonthlyBurn += Math.Floor(budget / 30m);
            result.ReplayBasis.Add("研发投入提升了产品分，但现金消耗上升。");
            result.ChangedMetrics.Add($"现金 -{budget / 10_000m:0}万");
            result.ChangedMetrics.Add($"产品 +{productGain}");
            result.NextPressure = "产品有进展，但要验证能否转化为用户或收入。";
        }

        private static void ApplyMarketingAction(GameState state, TurnResult result, PlayerAction action)
        {
            var budget = action.Budget > 0m ? action.Budget : 100_000m;
            var userGain = Math.Max(1, (int)(budget / 1_000m));
            var mrrGain = userGain * 500m;
            state.Metrics.Cash -= budget;
            state.Metrics.Users += userGain;
            state.Metrics.MonthlyRecurringRevenue += mrrGain;
            result.ReplayBasis.Add("营销投入带来了新用户和收入增长，但需要继续观察留存。");
            result.ChangedMetrics.Add($"现金 -{budget / 10_000m:0}万");
            result.ChangedMetrics.Add($"用户 +{userGain}");
            result.ChangedMetrics.Add($"MRR +{mrrGain / 10_000m:0}万");
            result.NextPressure = "增长开始出现，但要确认获客是否能持续转化。";
        }

        private static void ApplyTeamAction(GameState state, TurnResult result, PlayerAction action)
        {
            var budget = action.Budget > 0m ? action.Budget : 100_000m;
            var employees = Math.Max(1, (int)(budget / 50_000m));
            var burnIncrease = employees * 10_000m;
            state.Metrics.Cash -= budget;
            state.Metrics.EmployeeCount += employees;
            state.Metrics.MonthlyBurn += burnIncrease;
            state.Metrics.TeamMorale = Math.Min(100, state.Metrics.TeamMorale + 5);
            result.ReplayBasis.Add("招聘扩充了团队产能，但固定支出也随之上升。");
            result.ChangedMetrics.Add($"现金 -{budget / 10_000m:0}万");
            result.ChangedMetrics.Add($"团队 +{employees}人");
            result.ChangedMetrics.Add($"固定支出 +{burnIncrease / 10_000m:0}万");
            result.NextPressure = "团队能力增强了，但要确保新增固定支出能转化成产品或增长。";
        }

        private static void ApplyStrategyAction(GameState state, TurnResult result, PlayerAction action)
        {
            var budget = action.Budget > 0m ? action.Budget : 100_000m;
            var reputationGain = Math.Max(1, (int)(budget / 33_333m));
            state.Metrics.Cash -= budget;
            state.Metrics.Reputation = Math.Min(100, state.Metrics.Reputation + reputationGain);
            state.Metrics.Valuation += budget;
            result.ReplayBasis.Add("战略试点提升了外部想象空间，但短期收入仍需要经营动作验证。");
            result.ChangedMetrics.Add($"现金 -{budget / 10_000m:0}万");
            result.ChangedMetrics.Add($"声誉 +{reputationGain}");
            result.ChangedMetrics.Add($"估值 +{budget / 10_000m:0}万");
            result.NextPressure = "战略故事变强了，下一步要用产品、收入或合作结果证明它。";
        }

        private static void ApplyFundraisingAction(GameState state, TurnResult result, PlayerAction action)
        {
            state.Metrics.Cash += action.FundraiseAmount;
            state.Metrics.FounderEquityPercent = Math.Max(
                0m,
                state.Metrics.FounderEquityPercent - action.EquityOffered);
            if (action.PostMoneyValuation > 0m)
            {
                state.Metrics.Valuation = action.PostMoneyValuation;
            }

            result.ReplayBasis.Add("融资增加了现金储备，但创始人股权被稀释。");
            result.ChangedMetrics.Add($"融资 +{action.FundraiseAmount / 10_000m:0}万");
            result.ChangedMetrics.Add($"创始人股权 -{action.EquityOffered:0}%");
            result.ChangedMetrics.Add($"估值 {state.Metrics.Valuation / 10_000m:0}万");
            result.NextPressure = "现金更充足了，但需要把融资换成可验证的业务进展。";
        }
    }
}
