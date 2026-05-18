using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using StartupSim.Core.Contracts;

namespace StartupSim.Core.Parsing
{
    public static class ActionParser
    {
        private sealed class KeywordRule
        {
            public KeywordRule(IEnumerable<string> keywords, ActionType actionType, RiskLevel defaultRisk)
            {
                Keywords = keywords.ToArray();
                ActionType = actionType;
                DefaultRisk = defaultRisk;
            }

            public string[] Keywords { get; }
            public ActionType ActionType { get; }
            public RiskLevel DefaultRisk { get; }
        }

        private static readonly KeywordRule[] KeywordMap =
        {
            new KeywordRule(
                new[] { "融资", "见投资人", "见投资", "投资人", "路演", "募资", "fundraise", "funding", "vc" },
                ActionType.Fundraising,
                RiskLevel.Low),
            new KeywordRule(
                new[] { "招", "hire", "招聘", "雇", "挖人", "团队建设", "扩团队", "招人" },
                ActionType.Team,
                RiskLevel.Medium),
            new KeywordRule(
                new[] { "转型", "并购", "新市场", "战略", "策略", "pivot", "strategy", "收购", "出海", "扩张", "新业务" },
                ActionType.Strategy,
                RiskLevel.High),
            new KeywordRule(
                new[] { "降价", "投放", "广告", "营销", "推广", "获客", "市场", "增长", "seo", "sem", "marketing", "ads", "广告投放", "种子客户", "种子用户" },
                ActionType.Marketing,
                RiskLevel.Medium),
            new KeywordRule(
                new[] { "研发", "功能", "产品", "开发", "迭代", "feature", "特性", "技术", "代码", "product", "dev", "r&d", "工单", "ai" },
                ActionType.Product,
                RiskLevel.Medium)
        };

        private static readonly string[] HighRiskKeywords =
        {
            "激进", "烧钱", "高风险", "all in", "all-in", "豪赌", "猛砸"
        };

        private static readonly string[] LowRiskKeywords =
        {
            "保守", "稳健", "试探", "小规模", "谨慎", "低成本"
        };

        public static ActionPlan ParseMulti(string rawInput)
        {
            var input = rawInput ?? string.Empty;
            var actions = new List<PlayerAction>();
            var seenTypes = new HashSet<ActionType>();
            var fundraising = ExtractFundraising(input);

            foreach (var clause in SplitClauses(input))
            {
                if (clause.Contains("融资") || clause.Contains("出让"))
                {
                    continue;
                }

                var matched = MatchRule(clause, seenTypes);
                if (matched == null)
                {
                    continue;
                }

                var explicitRisk = DetermineRisk(clause, matched.ActionType);
                actions.Add(new PlayerAction
                {
                    Type = matched.ActionType,
                    Intent = clause,
                    Budget = ExtractBudgetPerSegment(clause),
                    RiskLevel = explicitRisk == RiskLevel.Medium ? matched.DefaultRisk : explicitRisk
                });
                seenTypes.Add(matched.ActionType);

                if (actions.Count >= 5)
                {
                    break;
                }
            }

            if (fundraising.Amount > 0m && !seenTypes.Contains(ActionType.Fundraising) && actions.Count < 5)
            {
                actions.Add(new PlayerAction
                {
                    Type = ActionType.Fundraising,
                    Intent = $"融资{fundraising.Amount / 10_000m:0}万出让{fundraising.Equity:0}%",
                    Budget = 0m,
                    RiskLevel = RiskLevel.Low,
                    FundraiseAmount = fundraising.Amount,
                    EquityOffered = fundraising.Equity,
                    PostMoneyValuation = fundraising.Equity > 0m
                        ? fundraising.Amount / (fundraising.Equity / 100m)
                        : 0m
                });
            }

            return new ActionPlan
            {
                RawInput = input,
                Actions = actions
            };
        }

        private static IEnumerable<string> SplitClauses(string input)
        {
            return Regex.Split(input, "[，,；;、]")
                .Select(clause => clause.Trim())
                .Where(clause => clause.Length > 0);
        }

        private static KeywordRule? MatchRule(string clause, ISet<ActionType> seenTypes)
        {
            foreach (var rule in KeywordMap)
            {
                if (seenTypes.Contains(rule.ActionType))
                {
                    continue;
                }

                if (rule.Keywords.Any(keyword => ContainsKeyword(clause, keyword)))
                {
                    return rule;
                }
            }

            return null;
        }

        private static bool ContainsKeyword(string text, string keyword)
        {
            return text.IndexOf(keyword, StringComparison.OrdinalIgnoreCase) >= 0;
        }

        private static RiskLevel DetermineRisk(string text, ActionType actionType)
        {
            if (HighRiskKeywords.Any(keyword => ContainsKeyword(text, keyword)))
            {
                return RiskLevel.High;
            }

            if (LowRiskKeywords.Any(keyword => ContainsKeyword(text, keyword)))
            {
                return RiskLevel.Low;
            }

            return actionType == ActionType.Fundraising
                ? RiskLevel.Low
                : actionType == ActionType.Strategy
                    ? RiskLevel.High
                    : RiskLevel.Medium;
        }

        private static decimal ExtractBudgetPerSegment(string text)
        {
            var match = Regex.Match(text, "(\\d+)\\s*万");
            return match.Success ? decimal.Parse(match.Groups[1].Value) * 10_000m : 0m;
        }

        private static (decimal Amount, decimal Equity) ExtractFundraising(string input)
        {
            var amountBeforeEquity = Regex.Match(input, "融资(\\d+)万.*?出让(\\d+)%");
            if (amountBeforeEquity.Success)
            {
                return (
                    decimal.Parse(amountBeforeEquity.Groups[1].Value) * 10_000m,
                    decimal.Parse(amountBeforeEquity.Groups[2].Value));
            }

            var equityBeforeAmount = Regex.Match(input, "出让(\\d+)%.*?融资(\\d+)万");
            if (equityBeforeAmount.Success)
            {
                return (
                    decimal.Parse(equityBeforeAmount.Groups[2].Value) * 10_000m,
                    decimal.Parse(equityBeforeAmount.Groups[1].Value));
            }

            return (0m, 0m);
        }
    }
}
