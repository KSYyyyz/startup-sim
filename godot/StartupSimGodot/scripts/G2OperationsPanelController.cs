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
    private const string DockRoomsCategory = "rooms";
    private const string DockFacilitiesCategory = "facilities";
    private const string DockEmployeesCategory = "employees";
    private const string DockFinanceCategory = "finance";
    private const string DockSystemCategory = "system";

    private string activeMode = string.Empty;
    private string activeDockCategory = DockRoomsCategory;
    private string selectedEmployeeId = string.Empty;
    private string selectedFacilityId = string.Empty;
    private int selectedCellX = -1;
    private int selectedCellY = -1;
    private bool hasZoneStart;
    private int zoneStartX;
    private int zoneStartY;
    private bool endgameReached;
    private float speedBeforePlayerOperation;
    private bool playerOperationPausedTime;

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
    [Export] public NodePath ObjectiveProgressBarPath { get; set; } = new NodePath("ObjectiveTracker/ObjectiveProgressBar");
    [Export] public NodePath ObjectiveTitleLabelPath { get; set; } = new NodePath("ObjectiveTracker/ObjectiveTitleLabel");
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
    private Label? ObjectiveTitleLabel => GetNodeOrNull<Label>(ObjectiveTitleLabelPath);
    private ProgressBar? ObjectiveProgressBar => GetNodeOrNull<ProgressBar>(ObjectiveProgressBarPath);
    private Label? ReportLabel => GetNodeOrNull<Label>(ReportLabelPath);
    private Label? ReplayLabel => GetNodeOrNull<Label>(ReplayLabelPath);
    private Label? ReportTitle => GetNodeOrNull<Label>(new NodePath("MonthlyReportModal/ReportTitle"));
    private Label? ObjectActionTitleLabel => GetNodeOrNull<Label>(new NodePath("ObjectActionPanel/ObjectActionTitleLabel"));
    private Label? ObjectActionDetailLabel => GetNodeOrNull<Label>(new NodePath("ObjectActionPanel/ObjectActionDetailLabel"));

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

        ConnectDockCategoryButtons();
        ConnectButton("BottomActionDock/ToolGroups/BuildTools/ProductZoneButton", SelectProductZoneTool);
        ConnectButton("BottomActionDock/ToolGroups/BuildTools/SalesZoneButton", SelectSalesZoneTool);
        ConnectButton("BottomActionDock/ToolGroups/BuildTools/ServerZoneButton", SelectServerZoneTool);
        ConnectButton("BottomActionDock/ToolGroups/FacilityTools/DeskButton", SelectDeskFacilityTool);
        ConnectButton("BottomActionDock/ToolGroups/FacilityTools/WhiteboardButton", SelectWhiteboardFacilityTool);
        ConnectButton("BottomActionDock/ToolGroups/FacilityTools/ServerRackButton", SelectServerFacilityTool);
        ConnectButton("BottomActionDock/ToolGroups/EmployeeTools/HireProductButton", HireProductEmployee);
        ConnectButton("BottomActionDock/ToolGroups/EmployeeTools/HireSalesButton", HireSalesEmployee);
        ConnectButton("BottomActionDock/ToolGroups/EmployeeTools/HireOpsButton", HireOpsEmployee);
        ConnectButton("BottomActionDock/ToolGroups/EmployeeTools/TrainButton", TrainSelectedEmployee);
        ConnectButton("BottomActionDock/ToolGroups/CrisisTools/SellFacilityButton", SellSelectedFacility);
        ConnectButton("BottomActionDock/ToolGroups/CrisisTools/ReduceCostButton", ReduceFixedCost);
        ConnectButton("BottomActionDock/ToolGroups/CrisisTools/BridgeFundingButton", SeekBridgeFunding);
        ConnectButton("ObjectActionPanel/UpgradeSelectedFacilityButton", UpgradeSelectedFacility);
        ConnectButton("ObjectActionPanel/SellSelectedFacilityButton", SellSelectedFacility);
        ConnectButton("ObjectActionPanel/TrainSelectedObjectButton", TrainSelectedEmployee);
        ConnectButton("TopStatusBar/TimeButtons/PauseButton", SetPaused);
        ConnectButton("TopStatusBar/TimeButtons/NormalSpeedButton", SetNormalSpeed);
        ConnectButton("TopStatusBar/TimeButtons/DoubleSpeedButton", SetDoubleSpeed);
        ConnectButton("TopStatusBar/TimeButtons/TripleSpeedButton", SetTripleSpeed);
        ConnectButton("TopStatusBar/TimeButtons/AdvanceMonthButton", AdvanceMonth);
        ConnectButton("BottomActionDock/ToolGroups/MetaTools/SaveButton", SaveRun);
        ConnectButton("BottomActionDock/ToolGroups/MetaTools/LoadButton", LoadRun);
        ConnectButton("FloatingEventFeed/OpenReportButton", ShowMonthlyReport);
        ConnectButton("MonthlyReportModal/ReportCloseButton", HideMonthlyReport);
        SetSpeedButtonState(TimeProgressController?.SpeedMultiplier ?? 0f);
        SetReportAvailable(false);
        HideObjectActionPanel();
        if (TimeProgressController != null)
        {
            TimeProgressController.MonthReady += OnMonthReady;
        }

        RefreshInitialMetrics();
        RefreshCompanyProgress();
        ConfigureReadableLabels();
        ConstrainHudButtons();
        SetGameplayControlsLocked(false);
        ShowDockCategory(DockRoomsCategory);
        EnsureResponsiveHudLayout();

        SetEventCue("开局", "先布置办公室，再推进月份查看经营反馈。");
    }

    public override void _Notification(int what)
    {
        if (what == NotificationResized)
        {
            EnsureResponsiveHudLayout();
        }
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
        if (GuardEndgameOperation("训练员工"))
        {
            return;
        }

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
        ShowEmployeeObjectActionPanel(employee, FindZoneForEmployee(employee));
    }

    public void SellSelectedFacility()
    {
        if (GuardEndgameOperation("出售设施"))
        {
            return;
        }

        ClearActiveBuildMode();
        if (string.IsNullOrWhiteSpace(selectedFacilityId))
        {
            SetEventCue("设施", "先点选办公室里的设施，再执行出售。");
            return;
        }

        if (FacilityPlacementController == null
            || !FacilityPlacementController.SellFacility(selectedFacilityId))
        {
            SetEventCue("设施", "出售失败，请重新选中一个已摆放设施。");
            return;
        }

        OfficeGridView?.HideFacilityVisual(selectedFacilityId);
        selectedFacilityId = string.Empty;
        HideObjectActionPanel();
        RefreshCapacity();
        ApplyBridgeCommand("出售设施节流20万", "已出售闲置设施并执行节流，");
    }

    public void UpgradeSelectedFacility()
    {
        if (GuardEndgameOperation("升级设施"))
        {
            return;
        }

        ClearActiveBuildMode();
        if (string.IsNullOrWhiteSpace(selectedFacilityId))
        {
            SetEventCue("升级", "先点选一个设施，再升级。");
            return;
        }

        if (FacilityPlacementController == null
            || !FacilityPlacementController.UpgradeFacility(selectedFacilityId))
        {
            SetEventCue("升级", "升级失败，当前设施可能已达到可用等级上限。");
            return;
        }

        var facility = FindFacility(selectedFacilityId);
        if (facility != null)
        {
            OfficeGridView?.ShowFacilityVisual(
                facility.Id,
                facility.FacilityTypeId,
                facility.X,
                facility.Y,
                facility.Level);
            UpdateObjectActionPanel(FindZoneAt(facility.X, facility.Y), facility, facility.Id);
        }

        RefreshCapacity();
        SetEventCue("升级", BuildFacilityUpgradeStatus(facility));
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

        PauseForSettlementReview();
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
        PauseForSettlementReview();
        HideObjectActionPanel();
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
        if (GuardEndgameOperation("危机操作"))
        {
            return;
        }

        ClearActiveBuildMode();
        if (TimeProgressController?.TurnBridge == null)
        {
            UpdateStatus("危机操作失败：C# Core bridge 未就绪。");
            return;
        }

        var result = TimeProgressController.TurnBridge.ExecuteCommand(command);
        TimeProgressController.SyncExternalSettlement(result);
        PauseForSettlementReview();
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
        selectedCellX = x;
        selectedCellY = y;
        var zone = FindZoneAt(x, y);
        var facility = FindFacilityAt(x, y);
        var employee = FindEmployee(occupantId);
        selectedFacilityId = facility?.Id ?? string.Empty;
        selectedEmployeeId = employee?.Id ?? string.Empty;
        var zoneText = zone == null ? "未划分房间" : zone.DisplayName;
        var facilityText = facility == null ? "无设施" : FacilityDisplayName(facility.FacilityTypeId);
        var occupantText = string.IsNullOrWhiteSpace(occupantId) ? "空闲格" : occupantId;
        var advice = BuildRoomAdvice(zone, facility, occupantText);

        SetLabel(
            ContextLabel,
            $"选中：({x}, {y}) / {zoneText}\n内容：{occupantText} / {facilityText}\n{advice}");
        UpdateObjectActionPanel(zone, facility, occupantText);
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
        if (GuardEndgameOperation($"划分{displayName}"))
        {
            return;
        }

        if (ZonePaintingController == null || !ZonePaintingController.SelectZoneType(zoneTypeId))
        {
            UpdateStatus($"{displayName} 工具不可用。");
            return;
        }

        PauseForPlayerOperation();
        activeMode = PaintZoneMode;
        hasZoneStart = false;
        OfficeGridView?.ClearBuildPreview();
        OfficeGridView?.SetBuildMode(true);
        UpdateStatus($"正在划分{displayName}：点击起点，再点击终点。");
    }

    private void SelectFacilityTool(string facilityTypeId, string displayName)
    {
        if (GuardEndgameOperation($"摆放{displayName}"))
        {
            return;
        }

        if (FacilityPlacementController == null
            || !FacilityPlacementController.SelectFacilityType(facilityTypeId))
        {
            UpdateStatus($"{displayName} 工具不可用。");
            return;
        }

        PauseForPlayerOperation();
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
        RestoreSpeedAfterPlayerOperation();
    }

    private void PauseForPlayerOperation()
    {
        if (!playerOperationPausedTime)
        {
            speedBeforePlayerOperation = TimeProgressController?.SpeedMultiplier ?? 0f;
            playerOperationPausedTime = true;
        }

        TimeProgressController?.SetPaused();
        SetSpeedButtonState(0f);
    }

    private void PauseForSettlementReview()
    {
        playerOperationPausedTime = false;
        speedBeforePlayerOperation = 0f;
        TimeProgressController?.SetPaused();
        TimeProgressController?.ResetMonthProgress();
        SetSpeedButtonState(0f);
    }

    private bool GuardEndgameOperation(string operationName)
    {
        if (!endgameReached)
        {
            return false;
        }

        PauseForSettlementReview();
        ClearActiveBuildMode();
        HideObjectActionPanel();
        SetGameplayControlsLocked(true);
        SetEventCue("结局", $"结局复盘已锁定经营操作，{operationName}不会生效。请读取存档或重新开始。");
        return true;
    }

    private void RestoreSpeedAfterPlayerOperation()
    {
        if (!playerOperationPausedTime)
        {
            return;
        }

        playerOperationPausedTime = false;
        if (endgameReached)
        {
            return;
        }

        if (speedBeforePlayerOperation >= 3f)
        {
            TimeProgressController?.SetTripleSpeed();
            SetSpeedButtonState(3f);
        }
        else if (speedBeforePlayerOperation >= 2f)
        {
            TimeProgressController?.SetDoubleSpeed();
            SetSpeedButtonState(2f);
        }
        else if (speedBeforePlayerOperation >= 1f)
        {
            TimeProgressController?.SetNormalSpeed();
            SetSpeedButtonState(1f);
        }
        else
        {
            TimeProgressController?.SetPaused();
            SetSpeedButtonState(0f);
        }
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
        var startX = zoneStartX;
        var startY = zoneStartY;
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
        if (!string.IsNullOrWhiteSpace(zoneId))
        {
            UpdateRoomContext(x, y, string.Empty);
        }

        UpdateStatus(string.IsNullOrWhiteSpace(zoneId)
            ? "区域创建失败，请避开已有区域或边界。"
            : BuildZoneCreatedStatus(zoneId, startX, startY, x, y));
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
        UpdateObjectActionPanel(zone, FindFacility(facilityId), facilityId);
        UpdateRoomContext(x, y, facilityId);
        UpdateStatus(BuildFacilityPlacedStatus(FindFacility(facilityId), zone));
    }

    private void HireAndAssignEmployee(
        string candidateId,
        string targetZoneTypeId,
        string skillId,
        string displayName)
    {
        if (GuardEndgameOperation($"招聘{displayName}"))
        {
            return;
        }

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
            var employeeCell = FindEmployeeVisualCell(zone);
            OfficeGridView?.ShowEmployeeVisual(
                employeeId,
                employee?.RoleId ?? string.Empty,
                employeeCell.X,
                employeeCell.Y);
            if (employee != null)
            {
                UpdateRoomContext(employeeCell.X, employeeCell.Y, employeeId);
                ShowEmployeeObjectActionPanel(employee, zone);
            }
        }

        EmployeeManagementController.TrainEmployee(employeeId, skillId);
        RefreshCapacity();
        UpdateStatus(zone == null
            ? $"已招聘{displayName}，请先创建匹配区域再分配。"
            : BuildEmployeeAssignedStatus(FindEmployee(employeeId), zone));
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

    private OfficeFacility? FindFacility(string facilityId)
    {
        if (ZonePaintingController == null || string.IsNullOrWhiteSpace(facilityId))
        {
            return null;
        }

        return ZonePaintingController.Layout.Facilities.FirstOrDefault(
            facility => facility.Id == facilityId);
    }

    private OfficeZone? FindZoneForEmployee(OfficeEmployee employee)
    {
        if (ZonePaintingController == null || string.IsNullOrWhiteSpace(employee.AssignedZoneId))
        {
            return null;
        }

        return ZonePaintingController.Layout.Zones.FirstOrDefault(
            zone => zone.Id == employee.AssignedZoneId);
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
            : $"产能预览：{FormatCapacitySummary(summary)}");
        RefreshCompanyProgress();
        RefreshSelectedObjectContext();
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
        SetLabel(GoalsLabel, FormatGoalSummary(summary));
        UpdateObjectiveProgressBar();
    }

    private void RefreshSelectedObjectContext()
    {
        if (selectedCellX < 0 || selectedCellY < 0)
        {
            return;
        }

        var facility = FindFacilityAt(selectedCellX, selectedCellY);
        var employee = FindEmployee(selectedEmployeeId);
        var employeeZone = employee == null ? null : FindZoneForEmployee(employee);
        var occupantId = facility?.Id ?? string.Empty;
        if (employee != null && employeeZone != null && facility == null)
        {
            occupantId = employee.Id;
        }

        UpdateRoomContext(selectedCellX, selectedCellY, occupantId);
        if (employee != null && employeeZone != null && facility == null)
        {
            ShowEmployeeObjectActionPanel(employee, employeeZone);
        }
    }

    private void UpdateObjectiveProgressBar()
    {
        var progress = CompanyProgressController?.LastStageProgressPercent ?? 0;
        if (ObjectiveProgressBar != null)
        {
            ObjectiveProgressBar.Value = progress;
        }

        SetLabel(ObjectiveTitleLabel, $"阶段目标 {progress}%");
    }

    private void ConfigureReadableLabels()
    {
        ApplyReadableLabel(StatusLabel, 22);
        ApplyReadableLabel(GoalsLabel, 16);
        ApplyReadableLabel(CapacityLabel, 16);
        ApplyReadableLabel(ContextLabel, 18);
        ApplyReadableLabel(ObjectActionDetailLabel, 20);
        ApplyReadableLabel(ReportLabel, 20);
        ApplyReadableLabel(ReplayLabel, 20);
    }

    private static void ApplyReadableLabel(Label? label, int fontSize)
    {
        if (label == null)
        {
            return;
        }

        label.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        label.ClipText = false;
        label.AddThemeFontSizeOverride("font_size", fontSize);
    }

    private void EnsureResponsiveHudLayout()
    {
        var viewportSize = GetViewportRect().Size;
        if (viewportSize.X <= 0f || viewportSize.Y <= 0f)
        {
            viewportSize = Size;
        }

        if (viewportSize.X <= 0f || viewportSize.Y <= 0f)
        {
            return;
        }

        LayoutBottomDock(viewportSize);
        SetControlRect("TopStatusBar", 0f, 0f, viewportSize.X, 54f);
        SetControlRect("TopStatusBar/MetricsLabel", 18f, 12f, MathF.Max(360f, viewportSize.X - 430f), 30f);
        SetControlRect("TopStatusBar/TimeButtons", MathF.Max(744f, viewportSize.X - 408f), 9f, 394f, 36f);
        SetControlRect("ObjectiveTracker", 18f, 64f, 262f, 74f);
        SetControlRect("FloatingEventFeed", MathF.Max(300f, viewportSize.X - 538f), 66f, 520f, 72f);
        SetControlRect("FloatingEventFeed/StatusLabel", 40f, 8f, 360f, 56f);
        SetControlRect("FloatingEventFeed/OpenReportButton", 410f, 18f, 96f, 32f);
        SetControlRect("RoomContextPanel", 18f, MathF.Max(190f, viewportSize.Y - 526f), 354f, 364f);
        SetControlRect("RoomContextPanel/ContextLabel", 14f, 10f, 322f, 70f);
        SetControlRect("RoomContextPanel/GoalsLabel", 14f, 88f, 322f, 170f);
        SetControlRect("RoomContextPanel/CapacityLabel", 14f, 270f, 322f, 78f);
        SetControlRect("ObjectActionPanel", MathF.Max(386f, viewportSize.X - 378f), 150f, 360f, 260f);
        SetControlRect("ObjectActionPanel/ObjectActionDetailLabel", 14f, 48f, 330f, 132f);
        SetControlRect(
            "MonthlyReportModal",
            MathF.Max(18f, (viewportSize.X - 640f) * 0.5f),
            MathF.Max(64f, (viewportSize.Y - 460f) * 0.5f),
            640f,
            460f);
        SetControlRect("MonthlyReportModal/ReportLabel", 20f, 62f, 600f, 188f);
        SetControlRect("MonthlyReportModal/ReplayLabel", 20f, 258f, 600f, 144f);
        SetControlRect("MonthlyReportModal/ReportCloseButton", 520f, 414f, 96f, 32f);
    }

    private void LayoutBottomDock(Vector2 viewportSize)
    {
        SetControlRect("BottomActionDock", 0f, MathF.Max(0f, viewportSize.Y - 88f), viewportSize.X, 88f);
        SetControlRect("BottomActionDock/DockCategoryTabs", 8f, 6f, 392f, 28f);
        SetControlRect("BottomActionDock/ToolGroups", 8f, 38f, MathF.Max(320f, viewportSize.X - 16f), 48f);
    }

    private void SetControlRect(string path, float x, float y, float width, float height)
    {
        var control = GetNodeOrNull<Control>(new NodePath(path));
        if (control == null)
        {
            return;
        }

        control.Position = new Vector2(x, y);
        control.Size = new Vector2(width, height);
    }

    private void ConnectDockCategoryButtons()
    {
        ConnectButton("BottomActionDock/DockCategoryTabs/RoomsCategoryButton", () => ShowDockCategory(DockRoomsCategory));
        ConnectButton("BottomActionDock/DockCategoryTabs/FacilitiesCategoryButton", () => ShowDockCategory(DockFacilitiesCategory));
        ConnectButton("BottomActionDock/DockCategoryTabs/EmployeesCategoryButton", () => ShowDockCategory(DockEmployeesCategory));
        ConnectButton("BottomActionDock/DockCategoryTabs/FinanceCategoryButton", () => ShowDockCategory(DockFinanceCategory));
        ConnectButton("BottomActionDock/DockCategoryTabs/SystemCategoryButton", () => ShowDockCategory(DockSystemCategory));
    }

    private void ShowDockCategory(string category)
    {
        if (activeDockCategory != category)
        {
            ClearActiveBuildMode();
        }

        activeDockCategory = category;
        SetNodeVisible("BottomActionDock/ToolGroups/BuildTools", category == DockRoomsCategory);
        SetNodeVisible("BottomActionDock/ToolGroups/FacilityTools", category == DockFacilitiesCategory);
        SetNodeVisible("BottomActionDock/ToolGroups/EmployeeTools", category == DockEmployeesCategory);
        SetNodeVisible("BottomActionDock/ToolGroups/CrisisTools", category == DockFinanceCategory);
        SetNodeVisible("BottomActionDock/ToolGroups/MetaTools", category == DockSystemCategory);
        SetDockCategoryButtonState();
    }

    private void SetDockCategoryButtonState()
    {
        SetCategoryButtonPressed("BottomActionDock/DockCategoryTabs/RoomsCategoryButton", DockRoomsCategory);
        SetCategoryButtonPressed("BottomActionDock/DockCategoryTabs/FacilitiesCategoryButton", DockFacilitiesCategory);
        SetCategoryButtonPressed("BottomActionDock/DockCategoryTabs/EmployeesCategoryButton", DockEmployeesCategory);
        SetCategoryButtonPressed("BottomActionDock/DockCategoryTabs/FinanceCategoryButton", DockFinanceCategory);
        SetCategoryButtonPressed("BottomActionDock/DockCategoryTabs/SystemCategoryButton", DockSystemCategory);
    }

    private void SetCategoryButtonPressed(string path, string category)
    {
        var button = GetNodeOrNull<Button>(new NodePath(path));
        if (button != null)
        {
            button.ToggleMode = true;
            button.ButtonPressed = activeDockCategory == category;
        }
    }

    private void ConstrainHudButtons()
    {
        ApplyButtonChrome("TopStatusBar/TimeButtons/PauseButton", new Vector2(56f, 36f));
        ApplyButtonIcon("TopStatusBar/TimeButtons/PauseButton", ActionIcon("pause_usage_icon.png"));
        ApplyButtonChrome("TopStatusBar/TimeButtons/NormalSpeedButton", new Vector2(56f, 36f));
        ApplyButtonChrome("TopStatusBar/TimeButtons/DoubleSpeedButton", new Vector2(56f, 36f));
        ApplyButtonChrome("TopStatusBar/TimeButtons/TripleSpeedButton", new Vector2(56f, 36f));
        ApplyButtonChrome("TopStatusBar/TimeButtons/AdvanceMonthButton", new Vector2(112f, 36f));
        ApplyButtonIcon("TopStatusBar/TimeButtons/AdvanceMonthButton", ActionIcon("monthly_report_icon.png"));
        SetButtonIconExpand("TopStatusBar/TimeButtons/AdvanceMonthButton");

        foreach (var (path, iconName) in new[]
        {
            ("BottomActionDock/ToolGroups/BuildTools/ProductZoneButton", "product_room_icon.png"),
            ("BottomActionDock/ToolGroups/BuildTools/SalesZoneButton", "sales_room_icon.png"),
            ("BottomActionDock/ToolGroups/BuildTools/ServerZoneButton", "server_room_icon.png"),
            ("BottomActionDock/ToolGroups/FacilityTools/DeskButton", "facility_upgrade_icon.png"),
            ("BottomActionDock/ToolGroups/FacilityTools/WhiteboardButton", "product_progress_icon.png"),
            ("BottomActionDock/ToolGroups/FacilityTools/ServerRackButton", "server_stability_icon.png"),
            ("BottomActionDock/ToolGroups/EmployeeTools/HireProductButton", "recruiting_icon.png"),
            ("BottomActionDock/ToolGroups/EmployeeTools/HireSalesButton", "recruiting_icon.png"),
            ("BottomActionDock/ToolGroups/EmployeeTools/HireOpsButton", "recruiting_icon.png"),
            ("BottomActionDock/ToolGroups/EmployeeTools/TrainButton", "training_icon.png"),
            ("BottomActionDock/ToolGroups/CrisisTools/SellFacilityButton", "facility_sell_icon.png"),
            ("BottomActionDock/ToolGroups/CrisisTools/ReduceCostButton", "cost_cutting_icon.png"),
            ("BottomActionDock/ToolGroups/CrisisTools/BridgeFundingButton", "bridge_funding_icon.png"),
            ("BottomActionDock/ToolGroups/MetaTools/SaveButton", "view_detail_icon.png"),
            ("BottomActionDock/ToolGroups/MetaTools/LoadButton", "view_detail_icon.png"),
        })
        {
            ApplyButtonChrome(path, new Vector2(64f, 48f));
            ApplyButtonIcon(path, ActionIcon(iconName));
        }

        foreach (var (path, iconName) in new[]
        {
            ("ObjectActionPanel/UpgradeSelectedFacilityButton", "facility_upgrade_icon.png"),
            ("ObjectActionPanel/SellSelectedFacilityButton", "facility_sell_icon.png"),
            ("ObjectActionPanel/TrainSelectedObjectButton", "training_icon.png"),
        })
        {
            ApplyButtonChrome(path, new Vector2(74f, 36f));
            ApplyButtonIcon(path, ActionIcon(iconName));
        }
    }

    private void ApplyButtonChrome(string path, Vector2 minimumSize)
    {
        var button = GetNodeOrNull<Button>(path);
        if (button == null)
        {
            return;
        }

        button.CustomMinimumSize = minimumSize;
        button.ClipText = true;
        SetButtonIconExpand(path);
    }

    private void ApplyButtonIcon(string path, string resourcePath)
    {
        var button = GetNodeOrNull<Button>(path);
        var icon = GD.Load<Texture2D>(resourcePath);
        if (button != null && icon != null)
        {
            button.Icon = icon;
        }
    }

    private static string ActionIcon(string filename)
    {
        return $"res://assets/art/godot-g1-art-pack-v2.2-tycoon-action-icons/exports/icons_48/{filename}";
    }

    private void SetButtonIconExpand(string path)
    {
        var button = GetNodeOrNull<Button>(path);
        if (button != null)
        {
            button.ExpandIcon = true;
        }
    }

    private void ConnectButton(string path, Action action)
    {
        var button = GetNodeOrNull<Button>(path);
        if (button != null)
        {
            button.ToggleMode = path.Contains("/TimeButtons/", StringComparison.Ordinal)
                && !path.EndsWith("AdvanceMonthButton", StringComparison.Ordinal);
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

        PauseForSettlementReview();
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
            ? $"第 {result.Month} 月已结算，查看月报。"
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
        PauseForSettlementReview();
        ClearActiveBuildMode();
        HideObjectActionPanel();
        SetGameplayControlsLocked(true);
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
        SetEventCue("提示", message);
    }

    private void SetEventCue(string title, string message)
    {
        SetLabel(StatusLabel, FormatEventCue(title, message));
    }

    private static string FormatEventCue(string title, string message)
    {
        return $"{title}：{message}";
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

    private static string FormatCapacitySummary(string summary)
    {
        var lines = summary
            .Replace("\r\n", "\n", StringComparison.Ordinal)
            .Split('\n', StringSplitOptions.RemoveEmptyEntries)
            .Select(line => line.Trim())
            .Where(line => line.Length > 0)
            .Take(3);
        return string.Join("\n", lines);
    }

    private static string FormatGoalSummary(string summary)
    {
        var lines = summary
            .Replace("\r\n", "\n", StringComparison.Ordinal)
            .Split('\n', StringSplitOptions.RemoveEmptyEntries)
            .Select(line => line.Trim())
            .Where(line => line.Length > 0)
            .Where(line =>
                line.StartsWith("阶段目标", StringComparison.Ordinal)
                || line.StartsWith("进度", StringComparison.Ordinal)
                || line.StartsWith("下一步", StringComparison.Ordinal)
                || line.StartsWith("成就", StringComparison.Ordinal))
            .Take(4)
            .ToArray();
        return lines.Length == 0 ? summary : string.Join("\n", lines);
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

    private string BuildZoneCreatedStatus(string zoneId, int startX, int startY, int endX, int endY)
    {
        var minX = Math.Min(startX, endX);
        var maxX = Math.Max(startX, endX);
        var minY = Math.Min(startY, endY);
        var maxY = Math.Max(startY, endY);
        var zone = ZonePaintingController?.Layout.Zones.FirstOrDefault(item => item.Id == zoneId);
        var zoneName = zone?.DisplayName ?? "区域";
        return $"已创建{zoneName}：{maxX - minX + 1}x{maxY - minY + 1} 格，覆盖 x={minX}..{maxX} / y={minY}..{maxY}。";
    }

    private static string BuildFacilityPlacedStatus(OfficeFacility? facility, OfficeZone? zone)
    {
        if (facility == null)
        {
            return "已摆放设施，产能预览已更新。";
        }

        return $"已摆放{FacilityDisplayName(facility.FacilityTypeId)}：月成本 +{facility.MonthlyCost}，{zone?.DisplayName ?? "房间"}产能已更新。";
    }

    private static string BuildFacilityUpgradeStatus(OfficeFacility? facility)
    {
        if (facility == null)
        {
            return "设施等级提升，产能已更新。";
        }

        return $"{FacilityDisplayName(facility.FacilityTypeId)}升至 {facility.Level} 级：月成本 {facility.MonthlyCost}，产能已更新。";
    }

    private static string BuildEmployeeAssignedStatus(OfficeEmployee? employee, OfficeZone? zone)
    {
        if (employee == null)
        {
            return $"员工已分配到{zone?.DisplayName ?? "房间"}，产能预览已更新。";
        }

        return $"已分配{employee.Name}：{EmployeeRoleName(employee.RoleId)} / {zone?.DisplayName ?? "未分配"}，训练会先压低效率再提升产能。";
    }

    private static string BuildRoomAdvice(
        OfficeZone? zone,
        OfficeFacility? facility,
        string occupantText)
    {
        if (zone == null)
        {
            return "房间产出：无\n推荐操作：先从底部经营菜单划分研发区、销售区或服务器区";
        }

        var output = ZoneOutputText(zone);
        var hasFacility = facility != null;
        var hasOccupant = occupantText != "空闲格";
        var advice = BuildRoomActionRecommendation(zone, hasFacility, hasOccupant);

        return $"房间产出：{output}\n推荐操作：{advice}";
    }

    private static string ZoneOutputText(OfficeZone zone)
    {
        return zone.ZoneTypeId switch
        {
            "product_zone" => "产品分和研发产能",
            "sales_zone" => "用户增长和 MRR",
            "server_zone" => "稳定性和运维余量",
            _ => "基础办公产能"
        };
    }

    private static string BuildRoomActionRecommendation(
        OfficeZone zone,
        bool hasFacility,
        bool hasOccupant)
    {
        return zone.ZoneTypeId switch
        {
            "product_zone" when !hasFacility => "摆放办公桌或产品白板",
            "product_zone" when !hasOccupant => "招研发员工并训练",
            "sales_zone" when !hasFacility => "摆放办公桌",
            "sales_zone" when !hasOccupant => "招销售员工验证收入",
            "server_zone" when !hasFacility => "摆放服务器机柜，注意需要 1x2 连续服务器区",
            "server_zone" when !hasOccupant => "招运维员工降低稳定性风险",
            _ => "继续观察月报瓶颈，再决定扩建或节流"
        };
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

    private void UpdateObjectActionPanel(
        OfficeZone? zone,
        OfficeFacility? facility,
        string occupantText)
    {
        if (facility != null)
        {
            ShowObjectActionPanel(
                $"设施：{FacilityDisplayName(facility.FacilityTypeId)}",
                string.Join(
                    "\n",
                    $"等级：{facility.Level}  月成本：{facility.MonthlyCost}",
                    $"房间：{zone?.DisplayName ?? "未划分"}  坐标：({facility.X}, {facility.Y})",
                    "影响：提升房间产能；升级更强，出售降低月成本。"),
                upgradeVisible: true,
                sellVisible: true,
                trainVisible: false);
            return;
        }

        if (zone != null)
        {
            ShowObjectActionPanel(
                $"房间：{zone.DisplayName}",
                string.Join(
                    "\n",
                    $"范围：{zone.Width}x{zone.Height}  当前：{occupantText}",
                    $"产出：{ZoneOutputText(zone)}",
                    BuildRoomActionRecommendation(zone, hasFacility: false, hasOccupant: occupantText != "空闲格")),
                upgradeVisible: false,
                sellVisible: false,
                trainVisible: false);
            return;
        }

        ShowObjectActionPanel(
            $"格子：({selectedCellX}, {selectedCellY})",
            "未划分房间。先从底部经营菜单选择房间类型，再框选办公室区域。",
            upgradeVisible: false,
            sellVisible: false,
            trainVisible: false);
    }

    private void ShowEmployeeObjectActionPanel(OfficeEmployee employee, OfficeZone? zone)
    {
        ShowObjectActionPanel(
            $"员工：{employee.Name}",
            string.Join(
                "\n",
                $"岗位：{EmployeeRoleName(employee.RoleId)}  等级：{employee.Level}",
                $"分配：{zone?.DisplayName ?? "未分配"}  心情：{employee.Mood}  疲劳：{employee.Fatigue}",
                "训练：短期效率下降，长期产能提升。"),
            upgradeVisible: false,
            sellVisible: false,
            trainVisible: true);
    }

    private void ShowObjectActionPanel(
        string title,
        string detail,
        bool upgradeVisible,
        bool sellVisible,
        bool trainVisible)
    {
        SetNodeVisible("ObjectActionPanel", true);
        SetLabel(ObjectActionTitleLabel, title);
        SetLabel(ObjectActionDetailLabel, detail);
        SetButtonVisible("ObjectActionPanel/UpgradeSelectedFacilityButton", upgradeVisible);
        SetButtonVisible("ObjectActionPanel/SellSelectedFacilityButton", sellVisible);
        SetButtonVisible("ObjectActionPanel/TrainSelectedObjectButton", trainVisible);
    }

    private void HideObjectActionPanel()
    {
        SetNodeVisible("ObjectActionPanel", false);
    }

    private void SetGameplayControlsLocked(bool locked)
    {
        foreach (var path in new[]
        {
            "BottomActionDock/ToolGroups/BuildTools/ProductZoneButton",
            "BottomActionDock/ToolGroups/BuildTools/SalesZoneButton",
            "BottomActionDock/ToolGroups/BuildTools/ServerZoneButton",
            "BottomActionDock/ToolGroups/FacilityTools/DeskButton",
            "BottomActionDock/ToolGroups/FacilityTools/WhiteboardButton",
            "BottomActionDock/ToolGroups/FacilityTools/ServerRackButton",
            "BottomActionDock/ToolGroups/EmployeeTools/HireProductButton",
            "BottomActionDock/ToolGroups/EmployeeTools/HireSalesButton",
            "BottomActionDock/ToolGroups/EmployeeTools/HireOpsButton",
            "BottomActionDock/ToolGroups/EmployeeTools/TrainButton",
            "BottomActionDock/ToolGroups/CrisisTools/SellFacilityButton",
            "BottomActionDock/ToolGroups/CrisisTools/ReduceCostButton",
            "BottomActionDock/ToolGroups/CrisisTools/BridgeFundingButton",
            "ObjectActionPanel/UpgradeSelectedFacilityButton",
            "ObjectActionPanel/SellSelectedFacilityButton",
            "ObjectActionPanel/TrainSelectedObjectButton",
            "TopStatusBar/TimeButtons/NormalSpeedButton",
            "TopStatusBar/TimeButtons/DoubleSpeedButton",
            "TopStatusBar/TimeButtons/TripleSpeedButton",
            "TopStatusBar/TimeButtons/AdvanceMonthButton",
        })
        {
            SetButtonDisabled(path, locked);
        }
    }

    private void SetButtonDisabled(string path, bool disabled)
    {
        var button = GetNodeOrNull<Button>(new NodePath(path));
        if (button != null)
        {
            button.Disabled = disabled;
        }
    }

    private void SetButtonVisible(string path, bool visible)
    {
        SetNodeVisible(path, visible);
    }

    private static string EmployeeRoleName(string roleId)
    {
        return roleId switch
        {
            "sales_specialist" => "销售",
            "ops_engineer" => "运维",
            "product_engineer" => "研发",
            _ => roleId
        };
    }
}
