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
        LastReport = string.Join(
            "\n",
            $"第 {snapshot.Month} 月经营报表",
            $"收入：MRR {snapshot.MonthlyRecurringRevenue} / 用户 {snapshot.Users}。{BuildCommercializationHint(snapshot)}",
            $"成本：月消耗 {snapshot.MonthlyBurn} / 现金 {snapshot.Cash} / 可支撑 {BuildCashSupportTimeText(snapshot)}。",
            $"产品：产品分 {snapshot.ProductScore}。{BuildProductHint(snapshot)}",
            "用户：用销售区、销售员工和服务器区承接增长。",
            $"现金流：{BuildCashFlowHint(snapshot)}",
            $"下月建议：{BuildNextMonthAdvice(snapshot)}");
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

    private static string BuildCashSupportTimeText(TurnResultSnapshot snapshot)
    {
        if (snapshot.MonthlyBurn <= 0)
        {
            return "暂无固定消耗压力";
        }

        var supportMonths = (float)snapshot.Cash / snapshot.MonthlyBurn;
        return $"{supportMonths:0.0} 个月";
    }

    private static string BuildCommercializationHint(TurnResultSnapshot snapshot)
    {
        if (snapshot.MonthlyRecurringRevenue > 0)
        {
            return "继续观察销售效率和服务器承载。";
        }

        if (snapshot.ProductScore >= 60)
        {
            return "下一步用销售区和销售员工转成 MRR。";
        }

        return "先补研发产能，做出可销售 MVP。";
    }

    private static string BuildProductHint(TurnResultSnapshot snapshot)
    {
        if (snapshot.ProductScore >= 80)
        {
            return "可加大销售区和服务器区投入。";
        }

        if (snapshot.ProductScore >= 50)
        {
            return "继续补研发产能，同时准备销售验证。";
        }

        return "优先保证研发工位、白板和研发员工。";
    }

    private static string BuildCashFlowHint(TurnResultSnapshot snapshot)
    {
        if (snapshot.MonthlyRecurringRevenue <= 0)
        {
            return "仍靠现金储备支撑，扩张前先确认收入入口。";
        }

        if (snapshot.MonthlyRecurringRevenue >= snapshot.MonthlyBurn)
        {
            return "收入已覆盖月消耗，可考虑扩团队和设施。";
        }

        return "收入未覆盖月消耗，先控成本和转化。";
    }

    private static string BuildNextMonthAdvice(TurnResultSnapshot snapshot)
    {
        if (snapshot.Cash <= snapshot.MonthlyBurn * 2)
        {
            return "先节流或出售闲置设施，守住现金流可支撑时间。";
        }

        if (snapshot.ProductScore < 60)
        {
            return "建研发区，放办公桌/产品白板，招聘研发。";
        }

        if (snapshot.MonthlyRecurringRevenue <= 0)
        {
            return "建销售区并招聘销售，同时准备服务器区。";
        }

        if (snapshot.Users > 0 && snapshot.MonthlyRecurringRevenue > 0)
        {
            return "补服务器区和运维，稳定后再扩大销售。";
        }

        return "围绕产品、用户、MRR 和现金流可支撑时间做下一轮取舍。";
    }
}
