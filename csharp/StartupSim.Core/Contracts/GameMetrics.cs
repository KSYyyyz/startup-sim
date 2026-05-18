using System;

namespace StartupSim.Core.Contracts
{
    public sealed class GameMetrics
    {
        public int Month { get; set; } = 1;
        public decimal Cash { get; set; } = 1_000_000m;
        public decimal MonthlyRecurringRevenue { get; set; }
        public int Users { get; set; }
        public int ProductScore { get; set; } = 20;
        public int Reputation { get; set; } = 50;
        public decimal FounderEquityPercent { get; set; } = 100m;
        public decimal Valuation { get; set; } = 2_640_000m;
        public decimal CashCoverageMonths { get; set; } = 8.3m;

        public GameMetrics Clone()
        {
            return (GameMetrics)MemberwiseClone();
        }
    }
}
