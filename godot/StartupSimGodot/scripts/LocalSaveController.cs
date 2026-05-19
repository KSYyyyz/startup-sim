using System.Text.Json;
using Godot;

namespace StartupSim.Godot;

public partial class LocalSaveController : Node
{
    private const string SavePath = "user://startup-sim-save.json";

    public string LastLoadedSummary { get; private set; } = string.Empty;

    public bool SaveCurrentRun(
        TurnResultSnapshot? result,
        BusinessIntentSnapshot? intent,
        string goalSummary,
        string reportSummary)
    {
        var save = new LocalSaveData
        {
            Month = result?.Month ?? 1,
            Cash = result?.Cash ?? 0,
            MonthlyRecurringRevenue = result?.MonthlyRecurringRevenue ?? 0,
            Users = result?.Users ?? 0,
            ProductScore = result?.ProductScore ?? 0,
            BusinessIntentSummary = intent?.Summary ?? string.Empty,
            GoalSummary = goalSummary ?? string.Empty,
            ReportSummary = reportSummary ?? string.Empty
        };
        using var file = FileAccess.Open(SavePath, FileAccess.ModeFlags.Write);
        if (file == null)
        {
            return false;
        }

        file.StoreString(JsonSerializer.Serialize(save));
        return true;
    }

    public string LoadCurrentRun()
    {
        if (!FileAccess.FileExists(SavePath))
        {
            LastLoadedSummary = "没有找到本地存档。";
            return LastLoadedSummary;
        }

        using var file = FileAccess.Open(SavePath, FileAccess.ModeFlags.Read);
        var json = file?.GetAsText() ?? string.Empty;
        var save = JsonSerializer.Deserialize<LocalSaveData>(json) ?? new LocalSaveData();
        LastLoadedSummary = BuildReplaySummary(save);
        return LastLoadedSummary;
    }

    public string BuildReplaySummary(LocalSaveData save)
    {
        return $"复盘：{save.Month}月 MRR{save.MonthlyRecurringRevenue} 用户{save.Users}";
    }

    public sealed class LocalSaveData
    {
        public int Month { get; set; }
        public int Cash { get; set; }
        public int MonthlyRecurringRevenue { get; set; }
        public int Users { get; set; }
        public int ProductScore { get; set; }
        public string BusinessIntentSummary { get; set; } = string.Empty;
        public string GoalSummary { get; set; } = string.Empty;
        public string ReportSummary { get; set; } = string.Empty;
    }
}
