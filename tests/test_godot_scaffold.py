from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GODOT = ROOT / "godot" / "StartupSimGodot"
SCRIPTS = GODOT / "scripts"
SCENES = GODOT / "scenes"


def test_godot_migration_plan_exists_and_sets_godot_only_frontend_route():
    doc = ROOT / "docs" / "godot_migration_plan.md"

    assert doc.is_file()
    content = doc.read_text(encoding="utf-8")
    assert "Godot 4.6.x" in content
    assert "C# Core" in content
    assert "Unity 路线停止作为新增开发目标" in content
    assert "Web 前端路线已放弃" in content
    assert "俯视角办公室场景" in content
    assert "区域选择和区域框定" in content
    assert "设施摆放" in content
    assert "员工招聘" in content
    assert "暂停、正常速度、二倍速、三倍速" in content


def test_godot_project_scaffold_exists():
    required = [
        GODOT / "project.godot",
        GODOT / "StartupSimGodot.csproj",
        GODOT / "README.md",
        SCENES / "main.tscn",
        SCRIPTS / "StartupSimController.cs",
        SCRIPTS / "PreparedActionSnapshot.cs",
        SCRIPTS / "TurnResultSnapshot.cs",
        SCRIPTS / "GodotTurnBridge.cs",
        SCRIPTS / "OfficeRoomHotspot.cs",
        SCRIPTS / "OfficeGridView.cs",
        SCRIPTS / "ZonePaintingController.cs",
        SCRIPTS / "FacilityPlacementController.cs",
        SCRIPTS / "EmployeeManagementController.cs",
        SCRIPTS / "CapacityPreviewController.cs",
        SCRIPTS / "TimeProgressController.cs",
        SCRIPTS / "MonthlyReportController.cs",
        SCRIPTS / "G2OperationsPanelController.cs",
        SCRIPTS / "ArtImportPreviewController.cs",
        SCENES / "art_import_preview.tscn",
    ]

    for path in required:
        assert path.is_file(), f"missing Godot file: {path.relative_to(ROOT)}"

    project = (GODOT / "project.godot").read_text(encoding="utf-8")
    assert 'config/name="Startup Sim Godot"' in project
    assert 'run/main_scene="res://scenes/main.tscn"' in project


def test_godot_project_references_portable_csharp_core():
    csproj = (GODOT / "StartupSimGodot.csproj").read_text(encoding="utf-8")
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert 'Sdk="Godot.NET.Sdk/4.6.2"' in csproj
    assert "<TargetFramework>net8.0</TargetFramework>" in csproj
    assert "..\\..\\csharp\\StartupSim.Core\\StartupSim.Core.csproj" in csproj
    assert "dotnet build godot/StartupSimGodot/StartupSimGodot.csproj --configuration Debug" in ci
    assert "godot/**/.godot/" in gitignore
    assert "godot/**/obj/" in gitignore


def test_godot_scripts_keep_rules_inside_bridge_only():
    for path in SCRIPTS.glob("*.cs"):
        content = path.read_text(encoding="utf-8")
        assert "namespace StartupSim.Godot" in content
        if path.name != "GodotTurnBridge.cs":
            assert "DeterministicTurnEngine" not in content
            assert "StartupSim.Core.Engines" not in content

    snapshot = (SCRIPTS / "PreparedActionSnapshot.cs").read_text(encoding="utf-8")
    assert "ActionType" in snapshot
    assert "Budget" in snapshot
    assert "FundraiseAmount" in snapshot
    assert "EquityOffered" in snapshot

    bridge = (SCRIPTS / "GodotTurnBridge.cs").read_text(encoding="utf-8")
    assert "StartupSim.Core.Contracts" in bridge
    assert "StartupSim.Core.Engines" in bridge
    assert "DeterministicTurnEngine" in bridge
    assert "ExecuteCommand" in bridge

    controller = (SCRIPTS / "StartupSimController.cs").read_text(encoding="utf-8")
    assert "GodotTurnBridge" in controller
    assert "TurnResultReceived" in controller


def test_godot_main_scene_mounts_office_grid_view():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")

    assert "OfficeGridView" in scene
    assert "res://scripts/OfficeGridView.cs" in scene
    assert "GridCellHovered" in grid_script
    assert "GridCellSelected" in grid_script
    assert "OfficeGrid" in grid_script


def test_godot_main_scene_uses_art_atlases_for_office_visuals():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    for atlas in [
        "office-tile-atlas-v0.1.png",
        "zone-state-overlay-atlas-v0.1.png",
        "facility-upgrade-atlas-v0.1.png",
        "employee-sprite-atlas-v0.1.png",
        "status-icon-atlas-v0.1.png",
    ]:
        assert atlas in scene

    assert "OfficeTileAtlas = ExtResource" in scene
    assert "ZoneOverlayAtlas = ExtResource" in scene
    assert "FacilityAtlas = ExtResource" in scene
    assert "EmployeeAtlas = ExtResource" in scene
    assert "StatusIconAtlas = ExtResource" in scene
    assert "DrawTextureRectRegion" in grid_script
    assert "DrawFloorTiles" in grid_script
    assert "ShowFacilityVisual" in grid_script
    assert "ShowEmployeeVisual" in grid_script
    assert "DrawFacilityVisuals" in grid_script
    assert "DrawEmployeeVisuals" in grid_script
    assert "ShowFacilityVisual" in panel_script
    assert "ShowEmployeeVisual" in panel_script


def test_godot_main_scene_looks_like_office_management_scene_not_grid_editor():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "OfficeBackdrop" in scene
    assert "GridVisibleByDefault = true" in scene
    assert "DefaultGridAlpha = 0.08" in scene
    assert "BuildModeGridAlpha = 0.24" in scene
    assert 'text = "公司经营面板"' in scene
    for label in ["现金：", "现金流可支撑时间：", "MRR：", "用户：", "产品："]:
        assert label in scene
    assert "G2 最小操作台" not in scene

    assert "GridVisibleByDefault" in grid_script
    assert "BuildModeGridAlpha" in grid_script
    assert "SetBuildMode" in grid_script
    assert "DrawOfficeBackdrop" in grid_script
    assert "ShouldDrawGrid" in grid_script
    assert "if (ShouldDrawGrid())" in grid_script

    assert "OfficeGridView?.SetBuildMode(true)" in panel_script
    assert "OfficeGridView?.SetBuildMode(false)" in panel_script


def test_godot_office_view_keeps_kairosoft_style_grid_interaction_readable():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")

    assert "mouse_filter = 2" in scene
    assert "GridVisibleByDefault = true" in scene
    assert "DefaultGridAlpha = 0.08" in scene
    assert "BuildModeGridAlpha = 0.24" in scene

    assert "DefaultGridAlpha" in grid_script
    assert "DrawOfficeFrame" in grid_script
    assert "DrawTextureRectRegion(" in grid_script
    assert "CellRect(x, y).Grow(1f)" in grid_script
    assert "for (var x = 0; x < GridWidth; x++)" in grid_script
    assert "for (var y = 0; y < GridHeight; y++)" in grid_script
    assert "buildModeEnabled ? BuildModeGridAlpha : DefaultGridAlpha" in grid_script


def test_godot_main_scene_mounts_zone_painting_controller():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    controller = (SCRIPTS / "ZonePaintingController.cs").read_text(encoding="utf-8")

    assert "ZonePaintingController" in scene
    assert "res://scripts/ZonePaintingController.cs" in scene
    assert "SelectZoneType" in controller
    assert "BeginSelection" in controller
    assert "CommitSelection" in controller
    assert "RenameZone" in controller
    assert "RemoveZone" in controller
    assert "OfficeLayout" in controller


def test_godot_main_scene_mounts_facility_placement_controller():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    controller = (SCRIPTS / "FacilityPlacementController.cs").read_text(encoding="utf-8")

    assert "FacilityPlacementController" in scene
    assert "res://scripts/FacilityPlacementController.cs" in scene
    assert "SelectFacilityType" in controller
    assert "PlaceFacility" in controller
    assert "UpgradeFacility" in controller
    assert "OfficeFacilityDefinition" in controller


def test_godot_main_scene_mounts_employee_management_controller():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    controller = (SCRIPTS / "EmployeeManagementController.cs").read_text(encoding="utf-8")

    assert "EmployeeManagementController" in scene
    assert "res://scripts/EmployeeManagementController.cs" in scene
    assert "HireCandidate" in controller
    assert "AssignEmployeeToZone" in controller
    assert "TrainEmployee" in controller
    assert "AdvanceEmployeeNeeds" in controller
    assert "EmployeeCandidate" in controller
    assert "RoleFitScore" in controller


def test_godot_main_scene_mounts_capacity_preview_controller():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    controller = (SCRIPTS / "CapacityPreviewController.cs").read_text(encoding="utf-8")

    assert "CapacityPreviewController" in scene
    assert "res://scripts/CapacityPreviewController.cs" in scene
    assert "RefreshCapacityPreview" in controller
    assert "BuildCapacitySnapshot" in controller
    assert "CapacityPreviewChanged" in controller


def test_godot_main_scene_mounts_time_progress_controller():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    controller = (SCRIPTS / "TimeProgressController.cs").read_text(encoding="utf-8")

    assert "TimeProgressController" in scene
    assert "res://scripts/TimeProgressController.cs" in scene
    assert "SetPaused" in controller
    assert "SetNormalSpeed" in controller
    assert "SetDoubleSpeed" in controller
    assert "SetTripleSpeed" in controller
    assert "AdvanceGameHours" in controller
    assert "SubmitMonthSettlement" in controller
    assert "GodotTurnBridge" in controller


def test_godot_main_scene_mounts_monthly_report_controller():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    controller = (SCRIPTS / "MonthlyReportController.cs").read_text(encoding="utf-8")

    assert "MonthlyReportController" in scene
    assert "res://scripts/MonthlyReportController.cs" in scene
    assert "BuildMonthlyReport" in controller
    assert "BuildBoardFeedback" in controller
    assert "BuildCompetitorSignal" in controller
    assert "BuildBusinessInsight" in controller
    assert "TurnResultSnapshot" in controller


def test_godot_main_scene_mounts_g2_minimal_operations_ui():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    controller = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "G2OperationsPanel" in scene
    assert "res://scripts/G2OperationsPanelController.cs" in scene
    assert 'ZonePaintingControllerPath = NodePath("../ZonePaintingController")' in scene
    assert 'FacilityPlacementControllerPath = NodePath("../FacilityPlacementController")' in scene
    assert 'EmployeeManagementControllerPath = NodePath("../EmployeeManagementController")' in scene
    assert 'TimeProgressControllerPath = NodePath("../TimeProgressController")' in scene
    assert 'CapacityPreviewControllerPath = NodePath("../CapacityPreviewController")' in scene
    assert 'MonthlyReportControllerPath = NodePath("../MonthlyReportController")' in scene
    assert 'OfficeGridViewPath = NodePath("../OfficeGridView")' in scene

    assert "SelectProductZoneTool" in controller
    assert "SelectSalesZoneTool" in controller
    assert "SelectServerZoneTool" in controller
    assert "SelectDeskFacilityTool" in controller
    assert "SelectWhiteboardFacilityTool" in controller
    assert "SelectServerFacilityTool" in controller
    assert "HireProductEmployee" in controller
    assert "TrainSelectedEmployee" in controller
    assert "AdvanceMonth" in controller
    assert "SetTripleSpeed" in controller
    assert "GridCellSelected" in controller
    assert "现金流可支撑时间" in controller
    assert "Runway" not in controller
    assert "跑道" not in controller
    assert "DeterministicTurnEngine" not in controller


def test_godot_art_import_preview_scene_references_core_atlases():
    scene = (SCENES / "art_import_preview.tscn").read_text(encoding="utf-8")
    controller = (SCRIPTS / "ArtImportPreviewController.cs").read_text(encoding="utf-8")

    assert "ArtImportPreview" in scene
    assert "res://scripts/ArtImportPreviewController.cs" in scene
    for atlas in [
        "office-tile-atlas-v0.1.png",
        "zone-state-overlay-atlas-v0.1.png",
        "facility-upgrade-atlas-v0.1.png",
        "employee-sprite-atlas-v0.1.png",
        "employee-direction-variants-v0.1.png",
        "status-icon-atlas-v0.1.png",
        "employee-animation-minimal-v0.1.png",
        "ui-core-atlas-v0.1.png",
        "feedback-fx-atlas-v0.1.png",
        "recruitment-portrait-sheet-v0.1.png",
        "recruitment-portrait-sheet-v0.2-angle-balanced.png",
    ]:
        assert atlas in scene

    assert "Scale100Percent" in scene
    assert "Scale75Percent" in scene
    assert "Scale50Percent" in scene
    assert "ValidateAtlasPreview" in controller
    assert "ValidateAtlasPreviewReport" in controller
    assert "AtlasTexture" in controller
    assert "Texture2D" in controller
    assert "ZoneStateOverlayAtlas" in controller
    assert "EmployeeDirectionAtlas" in controller
    assert "EmployeeAnimationAtlas" in controller
    assert "UiCoreAtlas" in controller
    assert "FeedbackFxAtlas" in controller
    assert "DeterministicTurnEngine" not in controller


def test_godot_g1_acceptance_report_exists():
    report = ROOT / "docs" / "godot_g1_acceptance_report.md"

    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "Godot G1 可玩切片验收报告" in text
    assert "办公室网格" in text
    assert "区域框定" in text
    assert "设施摆放与升级" in text
    assert "员工招聘与岗位适配" in text
    assert "员工成长与需求" in text
    assert "时间推进与月度结算" in text
    assert "月报与反馈" in text
    assert "G1 纵向切片" in text
