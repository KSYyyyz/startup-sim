using System;
using System.Linq;
using Godot;
using StartupSim.Core.Contracts;
using StartupSim.Core.Office;

namespace StartupSim.Godot;

public partial class G2OperationsPanelController : Control
{
    private const string PaintZoneMode = "paint_zone";
    private const string PlaceFacilityMode = "place_facility";

    private string activeMode = string.Empty;
    private string selectedEmployeeId = string.Empty;
    private string selectedFacilityId = string.Empty;
    private bool hasZoneStart;
    private int zoneStartX;
    private int zoneStartY;
    private bool endgameReached;

    [Export] public NodePath ZonePaintingControllerPath { get; set; } = new NodePath("");
    [Export] public NodePath FacilityPlacementControllerPath { get; set; } = new NodePath("");
    [Export] public NodePath EmployeeManagementControllerPath { get; set; } = new NodePath("");
    [Export] public NodePath CapacityPreviewControllerPath { get; set; } = new NodePath("");
    [Export] public NodePath TimeProgressControllerPath { get; set; } = new NodePath("");
    [Export] public NodePath MonthlyReportControllerPath { get; set; } = new NodePath("");
    [Export] public NodePath BusinessIntentControllerPath { get; set; } = new NodePath("");
    [Export] public NodePath CompanyProgressControllerPath { get; set; } = new NodePath("");
    [Export] public NodePath LocalSaveControllerPath { get; set; } = new NodePath("");
    [Export] public NodePath OfficeGridViewPath { get; set; } = new NodePath("");
    [Export] public NodePath StatusLabelPath { get; set; } = new NodePath("FloatingEventFeed/StatusLabel");
    [Export] public NodePath MetricsLabelPath { get; set; } = new NodePath("TopStatusBar/MetricsLabel");
    [Export] public NodePath GoalsLabelPath { get; set; } = new NodePath("RoomContextPanel/GoalsLabel");
    [Export] public NodePath CapacityLabelPath { get; set; } = new NodePath("RoomContextPanel/CapacityLabel");
    [Export] public NodePath ContextLabelPath { get; set; } = new NodePath("RoomContextPanel/ContextLabel");
    [Export] public NodePath ReportLabelPath { get; set; } = new NodePath("MonthlyReportModal/ReportLabel");
    [Export] public NodePath ReplayLabelPath { get; set; } = new NodePath("MonthlyReportModal/ReplayLabel");

    public ZonePaintingController? ZonePaintingController { get; private set; }
    public FacilityPlacementController? FacilityPlacementController { get; private set; }
    public EmployeeManagementController? EmployeeManagementController { get; private set; }
    public CapacityPreviewController? CapacityPreviewController { get; private set; }
    public TimeProgressController? TimeProgressController { get; private set; }
    public MonthlyReportController? MonthlyReportController { get; private set; }
    public BusinessIntentController? BusinessIntentController { get; private set; }
    public CompanyProgressController? CompanyProgressController { get; private set; }
    public LocalSaveController? LocalSaveController { get; private set; }
    public OfficeGridView? OfficeGridView { get; private set; }

    private TurnResultSnapshot? lastResult;
    private BusinessIntentSnapshot? lastIntent;
    private bool reportAvailable;

    private Label? StatusLabel => GetNodeOrNull<Label>(StatusLabelPath);
    private Label? MetricsLabel => GetNodeOrNull<Label>(MetricsLabelPath);
    private Label? GoalsLabel => GetNodeOrNull<Label>(GoalsLabelPath);
    private Label? CapacityLabel => GetNodeOrNull<Label>(CapacityLabelPath);
    private Label? ContextLabel => GetNodeOrNull<Label>(ContextLabelPath);
    private Label? ReportLabel => GetNodeOrNull<Label>(ReportLabelPath);
    private Label? ReplayLabel => GetNodeOrNull<Label>(ReplayLabelPath);
    private Label? ReportTitle => GetNodeOrNull<Label>(new NodePath("MonthlyReportModal/ReportTitle"));

    public override void _Ready()
    {
        ZonePaintingController = GetNodeOrNull<ZonePaintingController>(ZonePaintingControllerPath);
        FacilityPlacementController = GetNodeOrNull<FacilityPlacementController>(
            FacilityPlacementControllerPath);
        EmployeeManagementController = GetNodeOrNull<EmployeeManagementController>(
            EmployeeManagementControllerPath);
        CapacityPreviewController = GetNodeOrNull<CapacityPreviewController>(
            CapacityPreviewControllerPath);
        TimeProgressController = GetNodeOrNull<TimeProgressController>(TimeProgressControllerPath);
        MonthlyReportController = GetNodeOrNull<MonthlyReportController>(MonthlyReportControllerPath);
        BusinessIntentController = GetNodeOrNull<BusinessIntentController>(
            BusinessIntentControllerPath);
        CompanyProgressController = GetNodeOrNull<CompanyProgressController>(
            CompanyProgressControllerPath);
        LocalSaveController = GetNodeOrNull<LocalSaveController>(LocalSaveControllerPath);
        OfficeGridView = GetNodeOrNull<OfficeGridView>(OfficeGridViewPath);

        if (OfficeGridView != null)
        {
            OfficeGridView.GridCellSelected += OnGridCellSelected;
            OfficeGridView.GridCellHovered += OnGridCellHovered;
        }

        ConnectButton("BottomActionDock/BuildTools/ProductZoneButton", SelectProductZoneTool);
        ConnectButton("BottomActionDock/BuildTools/SalesZoneButton", SelectSalesZoneTool);
        ConnectButton("BottomActionDock/BuildTools/ServerZoneButton", SelectServerZoneTool);
        ConnectButton("BottomActionDock/FacilityTools/DeskButton", SelectDeskFacilityTool);
        ConnectButton("BottomActionDock/FacilityTools/WhiteboardButton", SelectWhiteboardFacilityTool);
        ConnectButton("BottomActionDock/FacilityTools/ServerRackButton", SelectServerFacilityTool);
        ConnectButton("BottomActionDock/EmployeeTools/HireProductButton", HireProductEmployee);
        ConnectButton("BottomActionDock/EmployeeTools/HireSalesButton", HireSalesEmployee);
        ConnectButton("BottomActionDock/EmployeeTools/HireOpsButton", HireOpsEmployee);
        ConnectButton("BottomActionDock/EmployeeTools/TrainButton", TrainSelectedEmployee);
        ConnectButton("BottomActionDock/CrisisTools/SellFacilityButton", SellSelectedFacility);
        ConnectButton("BottomActionDock/CrisisTools/ReduceCostButton", ReduceFixedCost);
        ConnectButton("BottomActionDock/CrisisTools/BridgeFundingButton", SeekBridgeFunding);
        ConnectButton("TopStatusBar/TimeButtons/PauseButton", SetPaused);
        ConnectButton("TopStatusBar/TimeButtons/NormalSpeedButton", SetNormalSpeed);
        ConnectButton("TopStatusBar/TimeButtons/DoubleSpeedButton", SetDoubleSpeed);
        ConnectButton("TopStatusBar/TimeButtons/TripleSpeedButton", SetTripleSpeed);
        ConnectButton("TopStatusBar/TimeButtons/AdvanceMonthButton", AdvanceMonth);
        ConnectButton("BottomActionDock/MetaTools/SaveButton", SaveRun);
        ConnectButton("BottomActionDock/MetaTools/LoadButton", LoadRun);
        ConnectButton("FloatingEventFeed/OpenReportButton", ShowMonthlyReport);
        ConnectButton("MonthlyReportModal/ReportCloseButton", HideMonthlyReport);
        SetSpeedButtonState(TimeProgressController?.SpeedMultiplier ?? 0f);
        SetReportAvailable(false);
        if (TimeProgressController != null)
        {
            TimeProgressController.MonthReady += OnMonthReady;
        }

        RefreshInitialMetrics();
        RefreshCompanyProgress();

        UpdateStatus("游戏已暂停。先布置办公室，再推进月份；现金流可支撑时间由 C# Core 月结结果解释。");
    }

    public void SelectProductZoneTool()
    {
        SelectZoneTool("product_zone", "研发区");
    }

    public void SelectSalesZoneTool()
    {
        SelectZoneTool("sales_zone", "销售区");
    }

    public void SelectServerZoneTool()
    {
        SelectZoneTool("server_zone", "服务器区");
    }

    public void SelectDeskFacilityTool()
    {
        SelectFacilityTool("basic_desk", "办公桌");
    }

    public void SelectWhiteboardFacilityTool()
    {
        SelectFacilityTool("product_whiteboard", "产品白板");
    }

    public void SelectServerFacilityTool()
    {
        SelectFacilityTool("starter_server_rack", "服务器机柜");
    }

    public void HireProductEmployee()
    {
        HireAndAssignEmployee(
            "candidate_product_engineer",
            "product_zone",
            "product_development",
            "研发员工");
    }

    public void HireSalesEmployee()
    {
        HireAndAssignEmployee(
            "candidate_sales_specialist",
            "sales_zone",
            "sales_conversion",
            "销售员工");
    }

    public void HireOpsEmployee()
    {
        HireAndAssignEmployee(
            "candidate_ops_engineer",
            "server_zone",
            "infrastructure_ops",
            "运维员工");
    }

    public void TrainSelectedEmployee()
    {
        ClearActiveBuildMode();

        if (EmployeeManagementController == null || ZonePaintingController == null)
        {
            UpdateStatus("员工控制器未就绪。");
            return;
        }

        var employee = FindEmployee(selectedEmployeeId)
            ?? ZonePaintingController.Layout.Employees.FirstOrDefault();
        if (employee == null)
        {
            UpdateStatus("还没有可训练员工。");
            return;
        }

        var skillId = employee.RoleId switch
        {
            "sales_specialist" => "sales_conversion",
            "ops_engineer" => "infrastructure_ops",
            _ => "product_development"
        };

        if (!EmployeeManagementController.TrainEmployee(employee.Id, skillId))
        {
            UpdateStatus("训练失败，请确认员工状态。");
            return;
        }

        selectedEmployeeId = employee.Id;
        RefreshCapacity();
        UpdateStatus($"{employee.Name} 已训练，短期效率会下降，但长期产能会提升。");
    }

    public void SellSelectedFacility()
    {
        ApplyBridgeCommand("出售设施节流20万", "已出售闲置设施并执行节流，");
    }

    public void ReduceFixedCost()
    {
        ApplyBridgeCommand("节流20万", "已执行固定支出削减，");
    }

    public void SeekBridgeFunding()
    {
        ApplyBridgeCommand("融资60万出让8%", "已完成过桥融资，");
    }

    public void SetPaused()
    {
        ClearActiveBuildMode();
        TimeProgressController?.SetPaused();
        SetSpeedButtonState(0f);
        UpdateStatus("已暂停。");
    }

    public void SetNormalSpeed()
    {
        if (endgameReached)
        {
            UpdateStatus("结局复盘已触发，无法继续推进。");
            return;
        }

        ClearActiveBuildMode();
        TimeProgressController?.SetNormalSpeed();
        SetSpeedButtonState(1f);
        UpdateStatus("正常速度推进。");
    }

    public void SetDoubleSpeed()
    {
        if (endgameReached)
        {
            UpdateStatus("结局复盘已触发，无法继续推进。");
            return;
        }

        ClearActiveBuildMode();
        TimeProgressController?.SetDoubleSpeed();
        SetSpeedButtonState(2f);
        UpdateStatus("二倍速推进。");
    }

    public void SetTripleSpeed()
    {
        if (endgameReached)
        {
            UpdateStatus("结局复盘已触发，无法继续推进。");
            return;
        }

        ClearActiveBuildMode();
        TimeProgressController?.SetTripleSpeed();
        SetSpeedButtonState(3f);
        UpdateStatus("三倍速推进。");
    }

    public void AdvanceMonth()
    {
        if (endgameReached)
        {
            UpdateStatus("结局复盘已触发，无法继续推进。");
            return;
        }

        SettleMonthFromCurrentIntent(clearBuildMode: true, showReport: true);
    }

    public void SaveRun()
    {
        lastIntent ??= BusinessIntentController?.BuildCurrentIntent();
        var saved = LocalSaveController?.SaveCurrentRun(
            lastResult,
            lastIntent,
            CompanyProgressController?.LastGoalSummary ?? string.Empty,
            MonthlyReportController?.LastReport ?? string.Empty) ?? false;
        UpdateStatus(saved ? "本地存档已保存。" : "本地存档失败。");
    }

    public void LoadRun()
    {
        var summary = LocalSaveController?.LoadCurrentRun() ?? "本地存档控制器未就绪。";
        SetLabel(ReplayLabel, summary);
        ShowMonthlyReport();
        UpdateStatus("已读取本地存档复盘。");
    }

    public void ShowMonthlyReport()
    {
        SetNodeVisible("MonthlyReportModal", true);
        SetReportButtonVisible(false);
    }

    public void HideMonthlyReport()
    {
        SetNodeVisible("MonthlyReportModal", false);
        SetReportButtonVisible(reportAvailable);
    }

    private void ApplyBridgeCommand(string command, string statusPrefix)
    {
        ClearActiveBuildMode();
        if (TimeProgressController?.TurnBridge == null)
        {
            UpdateStatus("危机操作失败：C# Core bridge 未就绪。");
            return;
        }

        var result = TimeProgressController.TurnBridge.ExecuteCommand(command);
        TimeProgressController.SyncExternalSettlement(result);
        lastResult = result;
        lastIntent = BusinessIntentController?.BuildCurrentIntent();
        var report = MonthlyReportController?.BuildMonthlyReport(result) ?? string.Empty;
        SetLabel(ReportTitle, "月度经营报告");
        SetLabel(MetricsLabel, BuildMetricsText(result));
        SetLabel(ReportLabel, BuildReportText(result, report));
        SetReportAvailable(true);
        RefreshCompanyProgress();
        if (IsEndgameResult(result))
        {
            ShowEndingReview(result);
            return;
        }

        UpdateStatus($"{statusPrefix}现金流可支撑时间：{BuildCashSupportTimeText(result)}。");
    }

    private void OnGridCellSelected(int x, int y, string occupantId)
    {
        UpdateRoomContext(x, y, occupantId);

        if (activeMode == PaintZoneMode)
        {
            PaintZoneByGridClick(x, y);
            return;
        }

        if (activeMode == PlaceFacilityMode)
        {
            PlaceFacilityByGridClick(x, y);
            return;
        }

        UpdateStatus($"已选择格子 ({x}, {y})。先选择区域或设施工具。");
    }

    private void OnGridCellHovered(int x, int y, string occupantId)
    {
        UpdateBuildPreview(x, y);
        var occupancyHint = string.IsNullOrWhiteSpace(occupantId) ? "空格子" : $"已有内容：{occupantId}";
        var actionHint = activeMode switch
        {
            PaintZoneMode when hasZoneStart => "再次点击可完成区域框选。",
            PaintZoneMode => "点击可设置区域起点。",
            PlaceFacilityMode => "点击可尝试摆放设施。",
            _ => "点击可选中格子。"
        };

        UpdateStatus($"悬停格子 ({x}, {y})，{occupancyHint}。{actionHint}");
    }

    private void UpdateRoomContext(int x, int y, string occupantId)
    {
        var zone = FindZoneAt(x, y);
        var facility = FindFacilityAt(x, y);
        var zoneText = zone == null ? "未划分房间" : zone.DisplayName;
        var facilityText = facility == null ? "无设施" : FacilityDisplayName(facility.FacilityTypeId);
        var occupantText = string.IsNullOrWhiteSpace(occupantId) ? "空闲格" : occupantId;
        var advice = BuildRoomAdvice(zone, facility, occupantText);

        SetLabel(
            ContextLabel,
            $"选中：({x}, {y}) / {zoneText}\n内容：{occupantText} / {facilityText}\n{advice}");
    }

    private void UpdateBuildPreview(int x, int y)
    {
        if (OfficeGridView == null)
        {
            return;
        }

        if (activeMode == PaintZoneMode && hasZoneStart)
        {
            OfficeGridView.ShowZoneSelectionPreview(zoneStartX, zoneStartY, x, y, ZonePaintingController?.SelectedZoneTypeId ?? string.Empty);
            return;
        }

        if (activeMode == PlaceFacilityMode && FacilityPlacementController != null)
        {
            var zone = FindZoneAt(x, y);
            var isValid = zone != null && FacilityPlacementController.CanPlaceSelectedFacility(zone.Id, x, y);
            OfficeGridView.ShowFacilityPlacementPreview(
                x,
                y,
                FacilityPlacementController.SelectedFacilityWidth,
                FacilityPlacementController.SelectedFacilityHeight,
                isValid);
            return;
        }

        OfficeGridView.ClearBuildPreview();
    }

    private void SelectZoneTool(string zoneTypeId, string displayName)
    {
        if (ZonePaintingController == null || !ZonePaintingController.SelectZoneType(zoneTypeId))
        {
            UpdateStatus($"{displayName} 工具不可用。");
            return;
        }

        activeMode = PaintZoneMode;
        hasZoneStart = false;
        OfficeGridView?.ClearBuildPreview();
        OfficeGridView?.SetBuildMode(true);
        UpdateStatus($"正在划分{displayName}：点击起点，再点击终点。");
    }

    private void SelectFacilityTool(string facilityTypeId, string displayName)
    {
        if (FacilityPlacementController == null
            || !FacilityPlacementController.SelectFacilityType(facilityTypeId))
        {
            UpdateStatus($"{displayName} 工具不可用。");
            return;
        }

        activeMode = PlaceFacilityMode;
        hasZoneStart = false;
        OfficeGridView?.ClearBuildPreview();
        OfficeGridView?.SetBuildMode(true);
        UpdateStatus($"正在摆放{displayName}：点击匹配区域内的格子。");
    }

    private void ClearActiveBuildMode()
    {
        activeMode = string.Empty;
        hasZoneStart = false;
        OfficeGridView?.SetBuildMode(false);
        OfficeGridView?.ClearBuildPreview();
    }

    private void PaintZoneByGridClick(int x, int y)
    {
        if (ZonePaintingController == null)
        {
            UpdateStatus("区域控制器未就绪。");
            return;
        }

        if (!hasZoneStart)
        {
            zoneStartX = x;
            zoneStartY = y;
            hasZoneStart = true;
            ZonePaintingController.BeginSelection(x, y);
            UpdateStatus($"区域起点为 ({x}, {y})，再点一次完成框选。");
            return;
        }

        var zoneId = ZonePaintingController.CommitSelection(x, y);
        hasZoneStart = false;
        if (!string.IsNullOrWhiteSpace(zoneId))
        {
            ClearActiveBuildMode();
        }
        else
        {
            OfficeGridView?.ClearBuildPreview();
        }

        RefreshCapacity();
        UpdateStatus(string.IsNullOrWhiteSpace(zoneId)
            ? "区域创建失败，请避开已有区域或边界。"
            : $"已创建区域 {zoneId}，范围从 ({zoneStartX}, {zoneStartY}) 到 ({x}, {y})。");
    }

    private void PlaceFacilityByGridClick(int x, int y)
    {
        if (ZonePaintingController == null || FacilityPlacementController == null)
        {
            UpdateStatus("设施控制器未就绪。");
            return;
        }

        var zone = FindZoneAt(x, y);
        if (zone == null)
        {
            UpdateStatus(FacilityPlacementController.SelectedFacilityTypeId == "starter_server_rack"
                ? "请在已划分服务器区内摆放设施，需要 1x2 连续服务器区。"
                : "请在已划分区域内摆放设施。");
            return;
        }

        var facilityId = FacilityPlacementController.PlaceFacility(zone.Id, x, y);
        if (string.IsNullOrWhiteSpace(facilityId))
        {
            var requiredZone = RequiredZoneText(FacilityPlacementController.SelectedFacilityTypeId);
            var failure = FacilityPlacementController.GetSelectedFacilityPlacementFailure(zone.Id, x, y);
            UpdateStatus(
                $"设施摆放失败：{BuildFacilityFailureMessage(failure, FacilityPlacementController.SelectedFacilityTypeId, requiredZone)}");
            return;
        }

        selectedFacilityId = facilityId;
        ClearActiveBuildMode();
        OfficeGridView?.ShowFacilityVisual(
            facilityId,
            FacilityPlacementController.SelectedFacilityTypeId,
            x,
            y);
        RefreshCapacity();
        UpdateStatus($"已摆放设施 {facilityId}。");
    }

    private void HireAndAssignEmployee(
        string candidateId,
        string targetZoneTypeId,
        string skillId,
        string displayName)
    {
        ClearActiveBuildMode();

        if (EmployeeManagementController == null || ZonePaintingController == null)
        {
            UpdateStatus("员工控制器未就绪。");
            return;
        }

        var employeeId = EmployeeManagementController.HireCandidate(candidateId);
        if (string.IsNullOrWhiteSpace(employeeId))
        {
            UpdateStatus($"{displayName}招聘失败。");
            return;
        }

        selectedEmployeeId = employeeId;
        var zone = ZonePaintingController.Layout.Zones.FirstOrDefault(
            item => item.ZoneTypeId == targetZoneTypeId);
        if (zone != null)
        {
            EmployeeManagementController.AssignEmployeeToZone(employeeId, zone.Id);
            var employee = FindEmployee(employeeId);
            OfficeGridView?.ShowEmployeeVisual(
                employeeId,
                employee?.RoleId ?? string.Empty,
                FindEmployeeVisualCellX(zone),
                FindEmployeeVisualCellY(zone));
        }

        EmployeeManagementController.TrainEmployee(employeeId, skillId);
        RefreshCapacity();
        UpdateStatus(zone == null
            ? $"已招聘{displayName}，请先创建匹配区域再分配。"
            : $"已招聘并分配{displayName}到{zone.DisplayName}。");
    }

    private OfficeZone? FindZoneAt(int x, int y)
    {
        if (ZonePaintingController == null)
        {
            return null;
        }

        return ZonePaintingController.Layout.Zones.FirstOrDefault(
            zone => x >= zone.X
                && x < zone.X + zone.Width
                && y >= zone.Y
                && y < zone.Y + zone.Height);
    }

    private OfficeEmployee? FindEmployee(string employeeId)
    {
        if (ZonePaintingController == null || string.IsNullOrWhiteSpace(employeeId))
        {
            return null;
        }

        return ZonePaintingController.Layout.Employees.FirstOrDefault(
            employee => employee.Id == employeeId);
    }

    private int FindEmployeeVisualCellX(OfficeZone zone)
    {
        return FindEmployeeVisualCell(zone).X;
    }

    private int FindEmployeeVisualCellY(OfficeZone zone)
    {
        return FindEmployeeVisualCell(zone).Y;
    }

    private OfficeCell FindEmployeeVisualCell(OfficeZone zone)
    {
        for (var y = zone.Y; y < zone.Y + zone.Height; y++)
        {
            for (var x = zone.X; x < zone.X + zone.Width; x++)
            {
                var hasFacility = ZonePaintingController?.Layout.Facilities.Any(
                    facility => facility.ZoneId == zone.Id
                        && x >= facility.X
                        && x < facility.X + facility.Width
                        && y >= facility.Y
                        && y < facility.Y + facility.Height) ?? false;
                if (!hasFacility)
                {
                    return new OfficeCell(x, y);
                }
            }
        }

        return new OfficeCell(zone.X, zone.Y);
    }

    private void RefreshCapacity()
    {
        var summary = CapacityPreviewController?.RefreshCapacityPreview() ?? string.Empty;
        lastIntent = BusinessIntentController?.BuildCurrentIntent();
        SetLabel(CapacityLabel, string.IsNullOrWhiteSpace(summary)
            ? "产能预览：等待区域、设施和员工。"
            : $"产能预览：{summary}");
        RefreshCompanyProgress();
    }

    private void RefreshInitialMetrics()
    {
        var metrics = TimeProgressController?.TurnBridge?.CurrentState.Metrics;
        if (metrics != null)
        {
            SetLabel(MetricsLabel, BuildMetricsText(metrics));
        }
    }

    private void RefreshCompanyProgress()
    {
        var summary = CompanyProgressController?.RefreshProgress(lastResult, lastIntent)
            ?? "公司目标：等待目标数据。";
        SetLabel(GoalsLabel, summary);
    }

    private void ConnectButton(string path, Action action)
    {
        var button = GetNodeOrNull<Button>(path);
        if (button != null)
        {
            button.ToggleMode = path.Contains("/TimeButtons/", StringComparison.Ordinal);
            button.Pressed += action;
        }
    }

    private void OnMonthReady(int monthIndex)
    {
        if (endgameReached)
        {
            return;
        }

        SettleMonthFromCurrentIntent(clearBuildMode: false, showReport: false);
    }

    private void SettleMonthFromCurrentIntent(bool clearBuildMode, bool showReport)
    {
        if (clearBuildMode)
        {
            ClearActiveBuildMode();
        }

        if (TimeProgressController == null)
        {
            UpdateStatus("时间控制器未就绪。");
            return;
        }

        lastIntent = BusinessIntentController?.BuildCurrentIntent();
        var result = lastIntent == null || TimeProgressController.TurnBridge == null
            ? TimeProgressController.SubmitMonthSettlement(
                "推进月份：根据办公室产能继续打磨产品和获取客户。")
            : TimeProgressController.SubmitBusinessIntent(lastIntent);
        if (result == null)
        {
            UpdateStatus("月度结算失败：C# Core bridge 未就绪。");
            return;
        }

        lastResult = result;
        var report = MonthlyReportController?.BuildMonthlyReport(result) ?? string.Empty;
        SetLabel(ReportTitle, "月度经营报告");
        SetLabel(MetricsLabel, BuildMetricsText(result));
        SetLabel(ReportLabel, BuildReportText(result, report));
        SetReportAvailable(true);
        if (showReport)
        {
            ShowMonthlyReport();
        }

        RefreshCompanyProgress();
        if (IsEndgameResult(result))
        {
            ShowEndingReview(result);
            return;
        }

        UpdateStatus(showReport
            ? $"第 {result.Month} 月已结算，现金流可支撑时间请查看月报反馈。"
            : $"第 {result.Month} 月已结算，点击查看月报。");
    }

    private bool IsEndgameResult(TurnResultSnapshot result)
    {
        return result.Month >= 12
            || result.Cash <= 0
            || !string.Equals(result.Status, "active", StringComparison.OrdinalIgnoreCase);
    }

    private void ShowEndingReview(TurnResultSnapshot result)
    {
        endgameReached = true;
        TimeProgressController?.SetPaused();
        SetSpeedButtonState(0f);
        SetLabel(ReportTitle, BuildEndingTitle(result));
        SetLabel(ReportLabel, BuildEndingReportText(result));
        SetLabel(ReplayLabel, BuildEndingReplayText(result));
        SetReportAvailable(false);
        ShowMonthlyReport();
        RefreshCompanyProgress();
        UpdateStatus($"第 {result.Month} 月进入结局复盘：{BuildEndingTitle(result)}。");
    }

    private void SetSpeedButtonState(float speedMultiplier)
    {
        SetSpeedButtonPressed("TopStatusBar/TimeButtons/PauseButton", speedMultiplier, 0f);
        SetSpeedButtonPressed("TopStatusBar/TimeButtons/NormalSpeedButton", speedMultiplier, 1f);
        SetSpeedButtonPressed("TopStatusBar/TimeButtons/DoubleSpeedButton", speedMultiplier, 2f);
        SetSpeedButtonPressed("TopStatusBar/TimeButtons/TripleSpeedButton", speedMultiplier, 3f);
    }

    private void SetSpeedButtonPressed(string path, float speedMultiplier, float expectedSpeed)
    {
        var button = GetNodeOrNull<Button>(path);
        if (button != null)
        {
            button.ToggleMode = true;
            button.ButtonPressed = speedMultiplier == expectedSpeed;
        }
    }

    private void UpdateStatus(string message)
    {
        SetLabel(StatusLabel, message);
    }

    private void SetReportAvailable(bool available)
    {
        reportAvailable = available;
        SetReportButtonVisible(available && !IsNodeVisible("MonthlyReportModal"));
    }

    private void SetReportButtonVisible(bool visible)
    {
        SetNodeVisible("FloatingEventFeed/OpenReportButton", visible);
    }

    private bool IsNodeVisible(string path)
    {
        var node = GetNodeOrNull<CanvasItem>(new NodePath(path));
        return node?.Visible ?? false;
    }

    private void SetNodeVisible(string path, bool visible)
    {
        var node = GetNodeOrNull<CanvasItem>(new NodePath(path));
        if (node != null)
        {
            node.Visible = visible;
        }
    }

    private static void SetLabel(Label? label, string text)
    {
        if (label != null)
        {
            label.Text = text;
        }
    }

    private static string BuildMetricsText(TurnResultSnapshot result)
    {
        return string.Join(
            "    ",
            $"现金：{result.Cash}",
            $"现金流可支撑时间：{BuildCashSupportTimeText(result)}",
            $"MRR：{result.MonthlyRecurringRevenue}",
            $"用户：{result.Users}",
            $"产品：{result.ProductScore}");
    }

    private static string BuildMetricsText(GameMetrics metrics)
    {
        return string.Join(
            "    ",
            $"现金：{metrics.Cash}",
            $"现金流可支撑时间：{BuildCashSupportTimeText(metrics)}",
            $"MRR：{metrics.MonthlyRecurringRevenue}",
            $"用户：{metrics.Users}",
            $"产品：{metrics.ProductScore}");
    }

    private static string BuildReportText(TurnResultSnapshot result, string report)
    {
        if (string.IsNullOrWhiteSpace(result.BusinessFactsText))
        {
            return report;
        }

        return $"{report}\n{result.BusinessFactsText}";
    }

    private static string BuildEndingTitle(TurnResultSnapshot result)
    {
        if (result.Cash <= 0 || string.Equals(result.Status, "bankruptcy", StringComparison.OrdinalIgnoreCase))
        {
            return "现金耗尽";
        }

        return result.Month >= 12 ? "第 12 月结局复盘" : "阶段结局复盘";
    }

    private static string BuildEndingReportText(TurnResultSnapshot result)
    {
        var endingName = BuildEndingTitle(result);
        var businessReadiness = result.ProductScore >= 80
            && result.Users >= 60
            && result.MonthlyRecurringRevenue >= 30_000
            && result.Cash > 0
                ? "具备下一阶段融资叙事"
                : "仍缺少稳定商业化证明";
        return string.Join(
            "\n",
            $"结局：{endingName}",
            $"第 {result.Month} 月复盘，第 12 月是当前版本的标准结算终点。",
            $"现金流可支撑时间：{BuildCashSupportTimeText(result)}",
            $"产品：{result.ProductScore} / 用户：{result.Users} / MRR：{result.MonthlyRecurringRevenue}",
            $"判断：{businessReadiness}",
            $"压力：{result.NextPressure}");
    }

    private static string BuildEndingReplayText(TurnResultSnapshot result)
    {
        if (!string.IsNullOrWhiteSpace(result.ReplayBasisText))
        {
            return $"复盘记录：\n{result.ReplayBasisText}";
        }

        return "复盘记录：本局缺少可追踪经营动作，下一局优先建立研发、销售和现金流闭环。";
    }

    private static string BuildCashSupportTimeText(TurnResultSnapshot result)
    {
        if (result.MonthlyBurn <= 0)
        {
            return "暂无固定消耗压力";
        }

        var supportMonths = (float)result.Cash / result.MonthlyBurn;
        return $"{supportMonths:0.0} 个月";
    }

    private static string BuildCashSupportTimeText(GameMetrics metrics)
    {
        if (metrics.MonthlyBurn <= 0)
        {
            return "暂无固定消耗压力";
        }

        var supportMonths = (float)(metrics.Cash / metrics.MonthlyBurn);
        return $"{supportMonths:0.0} 个月";
    }

    private static string RequiredZoneText(string facilityTypeId)
    {
        return facilityTypeId switch
        {
            "product_whiteboard" => "研发区",
            "starter_server_rack" => "服务器区",
            "basic_desk" => "研发区或销售区",
            _ => "匹配区域"
        };
    }

    private static string BuildFacilityFailureMessage(
        string failure,
        string facilityTypeId,
        string requiredZone)
    {
        var reason = string.IsNullOrWhiteSpace(failure)
            ? $"当前设施只能放在{requiredZone}。"
            : failure;
        return facilityTypeId == "starter_server_rack"
            ? $"{reason}服务器机柜需要 1x2 连续服务器区。"
            : reason;
    }

    private static string BuildRoomAdvice(
        OfficeZone? zone,
        OfficeFacility? facility,
        string occupantText)
    {
        if (zone == null)
        {
            return "房间产出：无\n推荐操作：先从底部工具栏划分研发区、销售区或服务器区";
        }

        var output = zone.ZoneTypeId switch
        {
            "product_zone" => "产品分和研发产能",
            "sales_zone" => "用户增长和 MRR",
            "server_zone" => "稳定性和运维余量",
            _ => "基础办公产能"
        };
        var hasFacility = facility != null;
        var hasOccupant = occupantText != "空闲格";
        var advice = zone.ZoneTypeId switch
        {
            "product_zone" when !hasFacility => "摆放办公桌或产品白板",
            "product_zone" when !hasOccupant => "招研发员工并训练",
            "sales_zone" when !hasFacility => "摆放办公桌",
            "sales_zone" when !hasOccupant => "招销售员工验证收入",
            "server_zone" when !hasFacility => "摆放服务器机柜，注意需要 1x2 连续服务器区",
            "server_zone" when !hasOccupant => "招运维员工降低稳定性风险",
            _ => "继续观察月报瓶颈，再决定扩建或节流"
        };

        return $"房间产出：{output}\n推荐操作：{advice}";
    }

    private static string FacilityDisplayName(string facilityTypeId)
    {
        return facilityTypeId switch
        {
            "product_whiteboard" => "产品白板",
            "starter_server_rack" => "服务器机柜",
            "basic_desk" => "办公桌",
            _ => facilityTypeId
        };
    }

    private OfficeFacility? FindFacilityAt(int x, int y)
    {
        if (ZonePaintingController == null)
        {
            return null;
        }

        return ZonePaintingController.Layout.Facilities.FirstOrDefault(
            facility => x >= facility.X
                && x < facility.X + facility.Width
                && y >= facility.Y
                && y < facility.Y + facility.Height);
    }
}
