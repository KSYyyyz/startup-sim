using StartupSim.Core.Contracts;
using StartupSim.Core.Parsing;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class ActionParserTests
{
    [Fact]
    public void ParseMultiExtractsSegmentBudgetsAndFundraisingTerms()
    {
        var plan = ActionParser.ParseMulti("融资500万出让10%，花20万研发产品，花10万做营销推广");

        Assert.Equal("融资500万出让10%，花20万研发产品，花10万做营销推广", plan.RawInput);
        Assert.Equal(3, plan.Actions.Count);

        Assert.Equal(ActionType.Product, plan.Actions[0].Type);
        Assert.Equal("花20万研发产品", plan.Actions[0].Intent);
        Assert.Equal(200_000m, plan.Actions[0].Budget);
        Assert.Equal(RiskLevel.Medium, plan.Actions[0].RiskLevel);

        Assert.Equal(ActionType.Marketing, plan.Actions[1].Type);
        Assert.Equal("花10万做营销推广", plan.Actions[1].Intent);
        Assert.Equal(100_000m, plan.Actions[1].Budget);

        Assert.Equal(ActionType.Fundraising, plan.Actions[2].Type);
        Assert.Equal("融资500万出让10%", plan.Actions[2].Intent);
        Assert.Equal(0m, plan.Actions[2].Budget);
        Assert.Equal(5_000_000m, plan.Actions[2].FundraiseAmount);
        Assert.Equal(10m, plan.Actions[2].EquityOffered);
        Assert.Equal(50_000_000m, plan.Actions[2].PostMoneyValuation);
    }

    [Fact]
    public void ParseMultiSupportsEquityBeforeFundraisingAmount()
    {
        var plan = ActionParser.ParseMulti("出让8%融资300万，招人扩团队");

        Assert.Equal(2, plan.Actions.Count);
        Assert.Equal(ActionType.Team, plan.Actions[0].Type);
        Assert.Equal(ActionType.Fundraising, plan.Actions[1].Type);
        Assert.Equal(3_000_000m, plan.Actions[1].FundraiseAmount);
        Assert.Equal(8m, plan.Actions[1].EquityOffered);
        Assert.Equal(37_500_000m, plan.Actions[1].PostMoneyValuation);
    }

    [Fact]
    public void ParseMultiDetectsRiskCuesPerClause()
    {
        var plan = ActionParser.ParseMulti("小规模花5万研发产品，激进投放30万广告");

        Assert.Equal(2, plan.Actions.Count);
        Assert.Equal(RiskLevel.Low, plan.Actions[0].RiskLevel);
        Assert.Equal(RiskLevel.High, plan.Actions[1].RiskLevel);
    }

    [Fact]
    public void ParseMultiKeepsUnknownInputAsEmptyPlan()
    {
        var plan = ActionParser.ParseMulti("内部复盘一下，暂时不开新动作");

        Assert.Equal("内部复盘一下，暂时不开新动作", plan.RawInput);
        Assert.Empty(plan.Actions);
    }
}
