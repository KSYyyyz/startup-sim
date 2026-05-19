using System.Linq;
using Godot;

namespace StartupSim.Godot;

public partial class CompanyProgressController : Node
{
    public ContentDatabase Database { get; } = new();
    public string LastGoalSummary { get; private set; } = string.Empty;
    public string LastAchievementSummary { get; private set; } = string.Empty;
    public int LastStageProgressPercent { get; private set; }

    public override void _Ready()
    {
        EnsureLoaded();
        RefreshProgress(null, null);
    }

    public string RefreshProgress(TurnResultSnapshot? result, BusinessIntentSnapshot? intent)
    {
        EnsureLoaded();
        LastGoalSummary = BuildGoalSummary(result, intent);
        LastAchievementSummary = BuildAchievementSummary(result, intent);
        LastStageProgressPercent = BuildStageProgressPercent(result);
        return $"{LastGoalSummary}\n{LastAchievementSummary}";
    }

    public int BuildStageProgressPercent(TurnResultSnapshot? result)
    {
        if (result == null)
        {
            return 0;
        }

        var productProgress = Mathf.Clamp(result.ProductScore / 80f, 0f, 1f);
        var userProgress = Mathf.Clamp(result.Users / 60f, 0f, 1f);
        var revenueProgress = Mathf.Clamp((float)(result.MonthlyRecurringRevenue / 30_000m), 0f, 1f);
        var cashProgress = result.MonthlyBurn <= 0
            ? 1f
            : Mathf.Clamp((float)(result.Cash / result.MonthlyBurn) / 3f, 0f, 1f);
        return Mathf.RoundToInt((productProgress + userProgress + revenueProgress + cashProgress) * 25f);
    }

    private void EnsureLoaded()
    {
        if (Database.CompanyGoals.Count == 0)
        {
            Database.LoadAll();
        }
    }

    public string BuildGoalSummary(TurnResultSnapshot? result, BusinessIntentSnapshot? intent)
    {
        var goal = Database.CompanyGoals.FirstOrDefault();
        if (goal == null)
        {
            return "公司目标：等待目标数据。";
        }

        var progress = result == null
            ? "进度：等待第一轮月结"
            : $"进度：产品{result.ProductScore} 用户{result.Users} MRR{result.MonthlyRecurringRevenue}";
        var support = result == null
            ? "现金流可支撑时间：等待月结"
            : $"现金流可支撑时间：{BuildCashSupportTimeText(result)}";
        return string.Join(
            "\n",
            $"阶段目标：{goal.DisplayName}",
            progress,
            support,
            $"瓶颈：{BuildBottleneckText(result)}",
            $"下一步：{BuildNextActionText(result, intent)}");
    }

    public string BuildAchievementSummary(TurnResultSnapshot? result, BusinessIntentSnapshot? intent)
    {
        var unlocked = Database.Achievements
            .Where(item => IsAchievementUnlocked(item.Id, result, intent))
            .Select(item => item.DisplayName)
            .ToArray();
        return unlocked.Length == 0 ? "成就：暂无" : $"成就：{string.Join("、", unlocked)}";
    }

    private static bool IsAchievementUnlocked(
        string achievementId,
        TurnResultSnapshot? result,
        BusinessIntentSnapshot? intent)
    {
        return achievementId switch
        {
            "achievement_first_revenue" => result?.MonthlyRecurringRevenue >= 50000,
            "achievement_product_team" => intent?.ProductFocus >= 8f,
            _ => intent != null && !string.IsNullOrWhiteSpace(intent.Summary)
        };
    }

    private static string BuildCashSupportTimeText(TurnResultSnapshot result)
    {
        if (result.MonthlyBurn <= 0)
        {
            return "暂无固定消耗压力";
        }

        return $"{(float)result.Cash / result.MonthlyBurn:0.0} 个月";
    }

    private static string BuildBottleneckText(TurnResultSnapshot? result)
    {
        if (result == null)
        {
            return "等待办公室产能进入月结";
        }

        if (result.MonthlyBurn > 0 && result.Cash / result.MonthlyBurn < 2m)
        {
            return "现金流可支撑时间过短";
        }

        if (result.ProductScore < 80)
        {
            return "产品能力还不足以支撑稳定增长";
        }

        if (result.Users < 60 || result.MonthlyRecurringRevenue < 30_000m)
        {
            return "客户和收入验证不足";
        }

        return "准备第 12 月结局复盘";
    }

    private static string BuildNextActionText(
        TurnResultSnapshot? result,
        BusinessIntentSnapshot? intent)
    {
        if (result == null)
        {
            return intent == null
                ? "先划分研发区、销售区和服务器区"
                : "推进一次月结验证办公室配置";
        }

        if (result.MonthlyBurn > 0 && result.Cash / result.MonthlyBurn < 2m)
        {
            return "节流、出售设施或临时融资";
        }

        if (result.ProductScore < 80)
        {
            return "扩研发区、摆白板、训练研发";
        }

        if (result.Users < 60 || result.MonthlyRecurringRevenue < 30_000m)
        {
            return "扩销售区、招销售、观察 MRR";
        }

        return "稳住现金流并推进到第 12 月";
    }
}
