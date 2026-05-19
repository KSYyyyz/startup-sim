using System.Linq;
using Godot;
using StartupSim.Core.Contracts;

namespace StartupSim.Godot;

[GlobalClass]
public partial class TurnResultSnapshot : Resource
{
    [Export] public int Month { get; set; }
    [Export] public string Status { get; set; } = "active";
    [Export] public int Cash { get; set; }
    [Export] public int MonthlyRecurringRevenue { get; set; }
    [Export] public int Users { get; set; }
    [Export] public int ProductScore { get; set; }
    [Export] public int Reputation { get; set; }
    [Export] public int MonthlyBurn { get; set; }
    [Export] public int EmployeeCount { get; set; }
    [Export] public int TeamMorale { get; set; }
    [Export] public float FounderEquityPercent { get; set; }
    [Export] public int Valuation { get; set; }
    [Export] public string ChangedMetricsText { get; set; } = string.Empty;
    [Export] public string ReplayBasisText { get; set; } = string.Empty;
    [Export] public string BusinessFactsText { get; set; } = string.Empty;
    [Export] public string NextPressure { get; set; } = string.Empty;

    public static TurnResultSnapshot FromTurnResult(TurnResult result)
    {
        var metrics = result.State.Metrics;
        return new TurnResultSnapshot
        {
            Month = metrics.Month,
            Status = result.State.Status,
            Cash = DecimalToInt(metrics.Cash),
            MonthlyRecurringRevenue = DecimalToInt(metrics.MonthlyRecurringRevenue),
            Users = metrics.Users,
            ProductScore = metrics.ProductScore,
            Reputation = metrics.Reputation,
            MonthlyBurn = DecimalToInt(metrics.MonthlyBurn),
            EmployeeCount = metrics.EmployeeCount,
            TeamMorale = metrics.TeamMorale,
            FounderEquityPercent = (float)metrics.FounderEquityPercent,
            Valuation = DecimalToInt(metrics.Valuation),
            ChangedMetricsText = string.Join("\n", result.ChangedMetrics),
            ReplayBasisText = string.Join("\n", result.ReplayBasis),
            BusinessFactsText = string.Join(
                "\n",
                result.BusinessFacts.Select(fact => $"{fact.Title}：{fact.Description}")),
            NextPressure = result.NextPressure
        };
    }

    private static int DecimalToInt(decimal value)
    {
        return (int)decimal.Round(value, 0);
    }
}
