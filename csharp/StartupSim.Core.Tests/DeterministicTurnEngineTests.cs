using StartupSim.Core.Contracts;
using StartupSim.Core.Engines;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class DeterministicTurnEngineTests
{
    [Fact]
    public void ProductInvestmentAdvancesMonthAndImprovesProduct()
    {
        var engine = new DeterministicTurnEngine();
        var initial = new GameState
        {
            Metrics = new GameMetrics
            {
                Month = 1,
                Cash = 1_000_000m,
                ProductScore = 20
            }
        };

        var result = engine.Execute(initial, new TurnCommand { RawText = "花10万研发产品" });

        Assert.Equal(2, result.State.Metrics.Month);
        Assert.Equal(900_000m, result.State.Metrics.Cash);
        Assert.Equal(28, result.State.Metrics.ProductScore);
        Assert.Contains("现金 -10万", result.ChangedMetrics);
        Assert.Contains(result.ReplayBasis, item => item.Contains("研发投入提升了产品分"));
        Assert.Equal("csharp-startup-sim-core", result.Authority);
    }

    [Fact]
    public void ProductInvestmentUsesParsedActionBudget()
    {
        var engine = new DeterministicTurnEngine();
        var initial = new GameState
        {
            Metrics = new GameMetrics
            {
                Month = 1,
                Cash = 1_000_000m,
                ProductScore = 20
            }
        };

        var result = engine.Execute(initial, new TurnCommand { RawText = "花20万研发产品" });

        Assert.Equal(2, result.State.Metrics.Month);
        Assert.Equal(800_000m, result.State.Metrics.Cash);
        Assert.Equal(36, result.State.Metrics.ProductScore);
        Assert.Contains("现金 -20万", result.ChangedMetrics);
        Assert.Contains("产品 +16", result.ChangedMetrics);
    }

    [Fact]
    public void MarketingInvestmentGrowsUsersAndRevenue()
    {
        var engine = new DeterministicTurnEngine();
        var initial = new GameState
        {
            Metrics = new GameMetrics
            {
                Month = 1,
                Cash = 1_000_000m,
                MonthlyRecurringRevenue = 0m,
                Users = 0,
                ProductScore = 35
            }
        };

        var result = engine.Execute(initial, new TurnCommand { RawText = "花10万做营销推广" });

        Assert.Equal(2, result.State.Metrics.Month);
        Assert.Equal(900_000m, result.State.Metrics.Cash);
        Assert.Equal(100, result.State.Metrics.Users);
        Assert.Equal(50_000m, result.State.Metrics.MonthlyRecurringRevenue);
        Assert.Contains("现金 -10万", result.ChangedMetrics);
        Assert.Contains("用户 +100", result.ChangedMetrics);
        Assert.Contains("MRR +5万", result.ChangedMetrics);
    }

    [Fact]
    public void ExecuteDoesNotMutateInputState()
    {
        var engine = new DeterministicTurnEngine();
        var initial = new GameState
        {
            Metrics = new GameMetrics
            {
                Month = 1,
                Cash = 1_000_000m,
                ProductScore = 20
            }
        };

        engine.Execute(initial, new TurnCommand { RawText = "花10万研发产品" });

        Assert.Equal(1, initial.Metrics.Month);
        Assert.Equal(1_000_000m, initial.Metrics.Cash);
        Assert.Equal(20, initial.Metrics.ProductScore);
    }

    [Fact]
    public void UnknownCommandKeepsMetricsStableExceptMonth()
    {
        var engine = new DeterministicTurnEngine();
        var initial = new GameState
        {
            Metrics = new GameMetrics
            {
                Month = 3,
                Cash = 800_000m,
                ProductScore = 31
            }
        };

        var result = engine.Execute(initial, new TurnCommand { RawText = "内部复盘一下" });

        Assert.Equal(4, result.State.Metrics.Month);
        Assert.Equal(800_000m, result.State.Metrics.Cash);
        Assert.Equal(31, result.State.Metrics.ProductScore);
        Assert.Contains("现金 稳定", result.ChangedMetrics);
    }
}
