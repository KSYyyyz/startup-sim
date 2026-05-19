using System.Linq;
using Godot;

namespace StartupSim.Godot;

public partial class CompanyProgressController : Node
{
    public ContentDatabase Database { get; } = new();
    public string LastGoalSummary { get; private set; } = string.Empty;
    public string LastAchievementSummary { get; private set; } = string.Empty;

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
        return $"{LastGoalSummary}\n{LastAchievementSummary}";
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
            ? "进度待月结"
            : $"产品{result.ProductScore} 用户{result.Users} MRR{result.MonthlyRecurringRevenue}";
        var support = result == null
            ? "现金流可支撑时间待月结"
            : $"现金流可支撑时间{BuildCashSupportTimeText(result)}";
        return $"目标：{goal.DisplayName}\n{progress} / {support}";
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
}
