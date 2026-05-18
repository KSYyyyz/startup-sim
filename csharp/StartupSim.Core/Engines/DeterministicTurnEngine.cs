using System;
using System.Linq;
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
            next.Metrics.Month += 1;

            var plan = ActionParser.ParseMulti(command?.RawText ?? string.Empty);
            var productAction = plan.Actions.FirstOrDefault(action => action.Type == ActionType.Product);
            if (productAction != null)
            {
                var budget = productAction.Budget > 0m ? productAction.Budget : 100_000m;
                var productGain = Math.Max(1, (int)(budget / 12_500m));
                next.Metrics.Cash -= budget;
                next.Metrics.ProductScore += productGain;
                return new TurnResult
                {
                    State = next,
                    ReplayBasis =
                    {
                        "研发投入提升了产品分，但现金消耗上升。"
                    },
                    ChangedMetrics =
                    {
                        $"现金 -{budget / 10_000m:0}万",
                        $"产品 +{productGain}"
                    },
                    NextPressure = "产品有进展，但要验证能否转化为用户或收入。"
                };
            }

            var marketingAction = plan.Actions.FirstOrDefault(action => action.Type == ActionType.Marketing);
            if (marketingAction != null)
            {
                var budget = marketingAction.Budget > 0m ? marketingAction.Budget : 100_000m;
                var userGain = Math.Max(1, (int)(budget / 1_000m));
                var mrrGain = userGain * 500m;
                next.Metrics.Cash -= budget;
                next.Metrics.Users += userGain;
                next.Metrics.MonthlyRecurringRevenue += mrrGain;
                return new TurnResult
                {
                    State = next,
                    ReplayBasis =
                    {
                        "营销投入带来了新用户和收入增长，但需要继续观察留存。"
                    },
                    ChangedMetrics =
                    {
                        $"现金 -{budget / 10_000m:0}万",
                        $"用户 +{userGain}",
                        $"MRR +{mrrGain / 10_000m:0}万"
                    },
                    NextPressure = "增长开始出现，但要确认获客是否能持续转化。"
                };
            }

            var teamAction = plan.Actions.FirstOrDefault(action => action.Type == ActionType.Team);
            if (teamAction != null)
            {
                var budget = teamAction.Budget > 0m ? teamAction.Budget : 100_000m;
                var employees = Math.Max(1, (int)(budget / 50_000m));
                var burnIncrease = employees * 10_000m;
                next.Metrics.Cash -= budget;
                next.Metrics.EmployeeCount += employees;
                next.Metrics.MonthlyBurn += burnIncrease;
                next.Metrics.TeamMorale = Math.Min(100, next.Metrics.TeamMorale + 5);
                return new TurnResult
                {
                    State = next,
                    ReplayBasis =
                    {
                        "招聘扩充了团队产能，但固定支出也随之上升。"
                    },
                    ChangedMetrics =
                    {
                        $"现金 -{budget / 10_000m:0}万",
                        $"团队 +{employees}人",
                        $"固定支出 +{burnIncrease / 10_000m:0}万"
                    },
                    NextPressure = "团队能力增强了，但要确保新增固定支出能转化成产品或增长。"
                };
            }

            return new TurnResult
            {
                State = next,
                ReplayBasis =
                {
                    "本回合保持观察，尚未形成强变化。"
                },
                ChangedMetrics =
                {
                    "现金 稳定"
                },
                NextPressure = "下月需要选择一个更明确的经营动作。"
            };
        }
    }
}
