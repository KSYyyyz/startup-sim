using System;
using System.Linq;
using Godot;
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
    [Export] public NodePath StatusLabelPath { get; set; } = new NodePath("StatusLabel");
    [Export] public NodePath MetricsLabelPath { get; set; } = new NodePath("MetricsLabel");
    [Export] public NodePath GoalsLabelPath { get; set; } = new NodePath("GoalsLabel");
    [Export] public NodePath CapacityLabelPath { get; set; } = new NodePath("CapacityLabel");
    [Export] public NodePath ReportLabelPath { get; set; } = new NodePath("ReportLabel");
    [Export] public NodePath ReplayLabelPath { get; set; } = new NodePath("ReplayLabel");

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

    private Label? StatusLabel => GetNodeOrNull<Label>(StatusLabelPath);
    private Label? MetricsLabel => GetNodeOrNull<Label>(MetricsLabelPath);
    private Label? GoalsLabel => GetNodeOrNull<Label>(GoalsLabelPath);
    private Label? CapacityLabel => GetNodeOrNull<Label>(CapacityLabelPath);
    private Label? ReportLabel => GetNodeOrNull<Label>(ReportLabelPath);
    private Label? ReplayLabel => GetNodeOrNull<Label>(ReplayLabelPath);

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

        ConnectButton("ZoneButtons/ProductZoneButton", SelectProductZoneTool);
        ConnectButton("ZoneButtons/SalesZoneButton", SelectSalesZoneTool);
        ConnectButton("ZoneButtons/ServerZoneButton", SelectServerZoneTool);
        ConnectButton("FacilityButtons/DeskButton", SelectDeskFacilityTool);
        ConnectButton("FacilityButtons/WhiteboardButton", SelectWhiteboardFacilityTool);
        ConnectButton("FacilityButtons/ServerRackButton", SelectServerFacilityTool);
        ConnectButton("EmployeeButtons/HireProductButton", HireProductEmployee);
        ConnectButton("EmployeeButtons/HireSalesButton", HireSalesEmployee);
        ConnectButton("EmployeeButtons/HireOpsButton", HireOpsEmployee);
        ConnectButton("EmployeeButtons/TrainButton", TrainSelectedEmployee);
        ConnectButton("TimeButtons/PauseButton", SetPaused);
        ConnectButton("TimeButtons/NormalSpeedButton", SetNormalSpeed);
        ConnectButton("TimeButtons/DoubleSpeedButton", SetDoubleSpeed);
        ConnectButton("TimeButtons/TripleSpeedButton", SetTripleSpeed);
        ConnectButton("TimeButtons/AdvanceMonthButton", AdvanceMonth);
        ConnectButton("MetaButtons/SaveButton", SaveRun);
        ConnectButton("MetaButtons/LoadButton", LoadRun);
        SetSpeedButtonState(TimeProgressController?.SpeedMultiplier ?? 1f);
        RefreshCompanyProgress();

        UpdateStatus("选择区域、设施或员工操作，现金流可支撑时间由 C# Core 月结结果解释。");
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

    public void SetPaused()
    {
        ClearActiveBuildMode();
        TimeProgressController?.SetPaused();
        SetSpeedButtonState(0f);
        UpdateStatus("已暂停。");
    }

    public void SetNormalSpeed()
    {
        ClearActiveBuildMode();
        TimeProgressController?.SetNormalSpeed();
        SetSpeedButtonState(1f);
        UpdateStatus("正常速度推进。");
    }

    public void SetDoubleSpeed()
    {
        ClearActiveBuildMode();
        TimeProgressController?.SetDoubleSpeed();
        SetSpeedButtonState(2f);
        UpdateStatus("二倍速推进。");
    }

    public void SetTripleSpeed()
    {
        ClearActiveBuildMode();
        TimeProgressController?.SetTripleSpeed();
        SetSpeedButtonState(3f);
        UpdateStatus("三倍速推进。");
    }

    public void AdvanceMonth()
    {
        ClearActiveBuildMode();

        if (TimeProgressController == null)
        {
            UpdateStatus("时间控制器未就绪。");
            return;
        }

        lastIntent = BusinessIntentController?.BuildCurrentIntent();
        var result = lastIntent == null || TimeProgressController.TurnBridge == null
            ? TimeProgressController.SubmitMonthSettlement(
                "推进月份：根据办公室产能继续打磨产品和获取客户。")
            : TimeProgressController.TurnBridge.ExecuteBusinessIntent(lastIntent);
        if (result == null)
        {
            UpdateStatus("月度结算失败：C# Core bridge 未就绪。");
            return;
        }

        lastResult = result;
        var report = MonthlyReportController?.BuildMonthlyReport(result) ?? string.Empty;
        SetLabel(MetricsLabel, BuildMetricsText(result));
        SetLabel(ReportLabel, BuildReportText(result, report));
        RefreshCompanyProgress();
        UpdateStatus($"第 {result.Month} 月已结算，现金流可支撑时间请查看月报反馈。");
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
        UpdateStatus("已读取本地存档复盘。");
    }

    private void OnGridCellSelected(int x, int y, string occupantId)
    {
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
            UpdateStatus("请在已划分区域内摆放设施。");
            return;
        }

        var facilityId = FacilityPlacementController.PlaceFacility(zone.Id, x, y);
        if (string.IsNullOrWhiteSpace(facilityId))
        {
            var requiredZone = RequiredZoneText(FacilityPlacementController.SelectedFacilityTypeId);
            UpdateStatus($"设施摆放失败：当前设施只能放在{requiredZone}。");
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
            button.ToggleMode = path.StartsWith("TimeButtons/", StringComparison.Ordinal);
            button.Pressed += action;
        }
    }

    private void SetSpeedButtonState(float speedMultiplier)
    {
        SetSpeedButtonPressed("TimeButtons/PauseButton", speedMultiplier, 0f);
        SetSpeedButtonPressed("TimeButtons/NormalSpeedButton", speedMultiplier, 1f);
        SetSpeedButtonPressed("TimeButtons/DoubleSpeedButton", speedMultiplier, 2f);
        SetSpeedButtonPressed("TimeButtons/TripleSpeedButton", speedMultiplier, 3f);
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
            "\n",
            $"现金：{result.Cash}",
            $"现金流可支撑时间：{BuildCashSupportTimeText(result)}",
            $"MRR：{result.MonthlyRecurringRevenue}",
            $"用户：{result.Users}",
            $"产品：{result.ProductScore}");
    }

    private static string BuildReportText(TurnResultSnapshot result, string report)
    {
        if (string.IsNullOrWhiteSpace(result.BusinessFactsText))
        {
            return report;
        }

        return $"{report}\n{result.BusinessFactsText}";
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
}
