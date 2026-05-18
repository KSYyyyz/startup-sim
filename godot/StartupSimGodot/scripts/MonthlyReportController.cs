using Godot;

namespace StartupSim.Godot;

public partial class MonthlyReportController : Node
{
    [Signal]
    public delegate void MonthlyReportChangedEventHandler(
        string report,
        string boardFeedback,
        string competitorSignal,
        string businessInsight);

    public string LastReport { get; private set; } = string.Empty;
    public string LastBoardFeedback { get; private set; } = string.Empty;
    public string LastCompetitorSignal { get; private set; } = string.Empty;
    public string LastBusinessInsight { get; private set; } = string.Empty;

    public string BuildMonthlyReport(TurnResultSnapshot snapshot)
    {
        LastReport =
            $"第 {snapshot.Month} 月战报：现金 {snapshot.Cash}，月经常收入 {snapshot.MonthlyRecurringRevenue}，用户 {snapshot.Users}，产品 {snapshot.ProductScore}。";
        LastBoardFeedback = BuildBoardFeedback(snapshot);
        LastCompetitorSignal = BuildCompetitorSignal(snapshot);
        LastBusinessInsight = BuildBusinessInsight(snapshot);
        EmitSignal(
            SignalName.MonthlyReportChanged,
            LastReport,
            LastBoardFeedback,
            LastCompetitorSignal,
            LastBusinessInsight);
        return LastReport;
    }

    public string BuildBoardFeedback(TurnResultSnapshot snapshot)
    {
        if (snapshot.Cash <= snapshot.MonthlyBurn * 2)
        {
            return "董事会提醒：现金流可支撑时间偏短，下月必须控制支出或提高收入。";
        }

        if (snapshot.ProductScore >= 70)
        {
            return "董事会认可：产品能力正在形成，但还要继续验证客户是否愿意付费。";
        }

        return "董事会关注：当前最重要的是把产品和收入拉到同一条增长线上。";
    }

    public string BuildCompetitorSignal(TurnResultSnapshot snapshot)
    {
        if (snapshot.Users < 100)
        {
            return "竞品态势：市场窗口仍在，但对手可能先拿到早期客户心智。";
        }

        return "竞品态势：你已经获得一批用户，对手可能通过降价或新功能反击。";
    }

    public string BuildBusinessInsight(TurnResultSnapshot snapshot)
    {
        if (snapshot.MonthlyRecurringRevenue <= 0)
        {
            return "经营洞察：产品和客户之间还没有形成收入闭环，先验证付费意愿。";
        }

        return "经营洞察：收入开始出现，但要继续观察现金流可支撑时间和留存质量。";
    }
}
