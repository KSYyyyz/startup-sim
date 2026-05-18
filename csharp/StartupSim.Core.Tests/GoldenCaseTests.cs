using System.Text.Json;
using StartupSim.Core.Contracts;
using StartupSim.Core.Engines;
using StartupSim.Core.Parsing;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class GoldenCaseTests
{
    [Fact]
    public void ProductInvestmentGoldenCaseDocumentsPythonReference()
    {
        var root = FindRepositoryRoot();
        var goldenPath = Path.Combine(root, "csharp", "golden-cases", "month01_product_investment.json");
        var json = File.ReadAllText(goldenPath);
        using var document = JsonDocument.Parse(json);
        var rootElement = document.RootElement;

        Assert.Equal("python-turn-engine-reference", rootElement.GetProperty("authority").GetString());
        Assert.Equal("花10万研发产品", rootElement.GetProperty("input").GetProperty("command").GetString());
        Assert.Equal(2, rootElement.GetProperty("expected").GetProperty("month").GetInt32());
        Assert.Equal(-220000, rootElement.GetProperty("expected").GetProperty("cash_change").GetInt32());
        Assert.Equal(8, rootElement.GetProperty("expected").GetProperty("product_change").GetInt32());
    }

    [Fact]
    public void ActionParserGoldenCasesMatchPythonReference()
    {
        var root = FindRepositoryRoot();
        var goldenPath = Path.Combine(root, "csharp", "golden-cases", "action_parser_multi.json");
        var json = File.ReadAllText(goldenPath);
        using var document = JsonDocument.Parse(json);
        var rootElement = document.RootElement;

        Assert.Equal("python-action-parser-reference", rootElement.GetProperty("authority").GetString());

        foreach (var goldenCase in rootElement.GetProperty("cases").EnumerateArray())
        {
            var command = goldenCase.GetProperty("command").GetString() ?? string.Empty;
            var plan = ActionParser.ParseMulti(command);
            var expectedActions = goldenCase.GetProperty("actions").EnumerateArray().ToArray();

            Assert.Equal(command, plan.RawInput);
            Assert.Equal(expectedActions.Length, plan.Actions.Count);

            for (var i = 0; i < expectedActions.Length; i++)
            {
                var expected = expectedActions[i];
                var actual = plan.Actions[i];

                Assert.Equal(expected.GetProperty("type").GetString(), SerializeType(actual.Type));
                Assert.Equal(expected.GetProperty("intent").GetString(), actual.Intent);
                Assert.Equal(expected.GetProperty("budget").GetDecimal(), actual.Budget);
                Assert.Equal(expected.GetProperty("risk_level").GetString(), SerializeRisk(actual.RiskLevel));
                Assert.Equal(
                    expected.GetProperty("fundraise_amount").GetDecimal(),
                    actual.FundraiseAmount);
                Assert.Equal(expected.GetProperty("equity_offered").GetDecimal(), actual.EquityOffered);
                Assert.Equal(
                    expected.GetProperty("post_money_valuation").GetDecimal(),
                    actual.PostMoneyValuation);
            }
        }
    }

    [Fact]
    public void MinimalTurnEngineGoldenCasesMatchCSharpPortableSlice()
    {
        var root = FindRepositoryRoot();
        var goldenPath = Path.Combine(root, "csharp", "golden-cases", "turn_engine_minimal.json");
        var json = File.ReadAllText(goldenPath);
        using var document = JsonDocument.Parse(json);
        var rootElement = document.RootElement;
        var engine = new DeterministicTurnEngine();

        Assert.Equal("csharp-portable-turn-slice", rootElement.GetProperty("authority").GetString());

        foreach (var goldenCase in rootElement.GetProperty("cases").EnumerateArray())
        {
            var initial = goldenCase.GetProperty("initial");
            var command = goldenCase.GetProperty("command").GetString() ?? string.Empty;
            var expected = goldenCase.GetProperty("expected");
            var result = engine.Execute(BuildState(initial), new TurnCommand { RawText = command });

            Assert.Equal(expected.GetProperty("status").GetString(), result.State.Status);
            Assert.Equal(expected.GetProperty("cash").GetDecimal(), result.State.Metrics.Cash);
            Assert.Equal(expected.GetProperty("product_score").GetInt32(), result.State.Metrics.ProductScore);
            Assert.Equal(expected.GetProperty("users").GetInt32(), result.State.Metrics.Users);
            Assert.Equal(expected.GetProperty("mrr").GetDecimal(), result.State.Metrics.MonthlyRecurringRevenue);
            Assert.Equal(
                expected.GetProperty("founder_equity").GetDecimal(),
                result.State.Metrics.FounderEquityPercent);
            Assert.Equal(expected.GetProperty("valuation").GetDecimal(), result.State.Metrics.Valuation);
        }
    }

    private static string FindRepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory != null)
        {
            if (File.Exists(Path.Combine(directory.FullName, "pyproject.toml")))
            {
                return directory.FullName;
            }

            directory = directory.Parent;
        }

        throw new DirectoryNotFoundException("Could not find repository root.");
    }

    private static GameState BuildState(JsonElement initial)
    {
        return new GameState
        {
            Metrics = new GameMetrics
            {
                Month = initial.GetProperty("month").GetInt32(),
                Cash = initial.GetProperty("cash").GetDecimal(),
                ProductScore = initial.GetProperty("product_score").GetInt32(),
                Users = initial.GetProperty("users").GetInt32(),
                MonthlyRecurringRevenue = initial.GetProperty("mrr").GetDecimal(),
                FounderEquityPercent = initial.GetProperty("founder_equity").GetDecimal(),
                Valuation = initial.GetProperty("valuation").GetDecimal()
            }
        };
    }

    private static string SerializeType(ActionType type)
    {
        return type switch
        {
            ActionType.Product => "product",
            ActionType.Marketing => "marketing",
            ActionType.Fundraising => "fundraising",
            ActionType.Team => "team",
            ActionType.Strategy => "strategy",
            _ => throw new ArgumentOutOfRangeException(nameof(type), type, null)
        };
    }

    private static string SerializeRisk(RiskLevel risk)
    {
        return risk switch
        {
            RiskLevel.Low => "low",
            RiskLevel.Medium => "medium",
            RiskLevel.High => "high",
            _ => throw new ArgumentOutOfRangeException(nameof(risk), risk, null)
        };
    }
}
