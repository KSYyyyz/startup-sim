using System;
using StartupSim.Core.Contracts;

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

            var text = command?.RawText ?? string.Empty;
            if (text.Contains("研发") || text.Contains("产品"))
            {
                next.Metrics.Cash -= 100_000m;
                next.Metrics.ProductScore += 8;
                return new TurnResult
                {
                    State = next,
                    ReplayBasis =
                    {
                        "研发投入提升了产品分，但现金消耗上升。"
                    },
                    ChangedMetrics =
                    {
                        "现金 -10万",
                        "产品 +8"
                    },
                    NextPressure = "产品有进展，但要验证能否转化为用户或收入。"
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
