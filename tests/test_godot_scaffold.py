from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GODOT = ROOT / "godot" / "StartupSimGodot"
SCRIPTS = GODOT / "scripts"
SCENES = GODOT / "scenes"


def _method_body(source: str, signature: str) -> str:
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[brace : index + 1]
    raise AssertionError(f"method body not found: {signature}")


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
        SCRIPTS / "OfficeProjection.cs",
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
        "office-tile-expansion-atlas-v0.4.png",
        "zone-state-overlay-atlas-v0.6.png",
        "facility-placement-atlas-v0.3.png",
        "employee-motion-atlas-v0.2.png",
        "employee-status-icon-atlas-v0.5.png",
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


def test_godot_main_scene_uses_pseudo3d_art_pack_layers():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")

    for atlas in [
        "pseudo3d-office-structure-atlas-v1.1b.png",
        "zone-carpet-build-marker-atlas-v1.2.png",
        "large-facility-sprite-atlas-v1.3.png",
        "employee-pseudo3d-motion-atlas-v1.4.png",
        "business-event-feedback-bubble-atlas-v1.6.png",
    ]:
        assert atlas in scene

    assert "company-main-scene-background" not in scene
    assert "Pseudo3DStructureAtlas = ExtResource" in scene
    assert "ZoneCarpetAtlas = ExtResource" in scene
    assert "LargeFacilityAtlas = ExtResource" in scene
    assert "EmployeePseudo3DAtlas = ExtResource" in scene
    assert "BusinessFeedbackBubbleAtlas = ExtResource" in scene

    for symbol in [
        "Pseudo3DStructureAtlas",
        "ZoneCarpetAtlas",
        "LargeFacilityAtlas",
        "EmployeePseudo3DAtlas",
        "BusinessFeedbackBubbleAtlas",
        "DrawPseudo3DOfficeShell",
        "DrawPseudo3DFloorTiles",
        "DrawZoneCarpets",
        "DrawPseudo3DVisualStack",
        "RenderDepthKey",
        "DrawLargeFacilityVisual",
        "DrawPseudo3DEmployeeVisual",
    ]:
        assert symbol in grid_script


def test_godot_hud_kpi_assets_use_cash_support_semantics():
    art_pack = GODOT / "assets" / "art" / "godot-g1-art-pack-v1.5-hud-kpi-ui-chrome"
    index = (art_pack / "asset-index.json").read_text(encoding="utf-8")
    guide = (art_pack / "slice-guides" / "hud-kpi-ui-chrome-atlas-v1.5-slice-guide.md").read_text(
        encoding="utf-8"
    )

    assert "cash_support_clock" in index
    assert "kpi_icons-cash_support_clock.png" in index
    assert "cash_support_clock" in guide
    assert "runway_clock" not in index
    assert "runway_clock" not in guide


def test_godot_main_scene_links_named_art_packs_by_function_and_use():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")
    zone_script = (SCRIPTS / "ZonePaintingController.cs").read_text(encoding="utf-8")

    for asset_path in [
        "office-tile-expansion-atlas-v0.4.png",
        "zone-state-overlay-atlas-v0.6.png",
        "facility-placement-atlas-v0.3.png",
        "employee-motion-atlas-v0.2.png",
        "employee-status-icon-atlas-v0.5.png",
        "feedback-portrait-sheet-v0.7.png",
    ]:
        assert asset_path in scene

    assert "company-main-scene-background-v0.7.1.png" not in scene
    assert 'texture = SubResource("AtlasTexture_feedback_portrait")' in scene

    assert "RegisterZoneVisual" in grid_script
    assert "ClearZoneVisual" in grid_script
    assert '"product_zone" => 0' in grid_script
    assert '"sales_zone" => 1' in grid_script
    assert '"server_zone" => 2' in grid_script
    assert "columns: 6, rows: 5, column: sourceColumn, row: 0" in grid_script

    assert '"basic_desk" => 0' in grid_script
    assert '"product_whiteboard" => 1' in grid_script
    assert '"starter_server_rack" => 2' in grid_script
    assert "columns: 6, rows: 3, sourceColumn, row: 0" in grid_script

    assert '"product_engineer" => 0' in grid_script
    assert '"sales_specialist" => 2' in grid_script
    assert '"ops_engineer" => 4' in grid_script
    assert "columns: 12, rows: 6, sourceColumn, row: sourceRow" in grid_script
    assert "columns: 8, rows: 4, column: 12 % 8, row: 12 / 8" in grid_script

    assert "GridView?.RegisterZoneVisual(zone.Id, zone.ZoneTypeId);" in zone_script
    assert "GridView?.ClearZoneVisual(zoneId);" in zone_script


def test_godot_main_scene_looks_like_tycoon_office_scene_not_grid_editor():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "OfficeBackdrop" in scene
    assert (
        "GridVisibleByDefault = true" in scene
        or "GridVisibleByDefault { get; set; } = true" in grid_script
    )
    assert (
        "DefaultGridAlpha = 0.08" in scene
        or "DefaultGridAlpha { get; set; } = 0.08f" in grid_script
    )
    assert (
        "BuildModeGridAlpha = 0.24" in scene
        or "BuildModeGridAlpha { get; set; } = 0.24f" in grid_script
    )
    assert "TopStatusBar" in scene
    assert "BottomActionDock" in scene
    assert "FloatingEventFeed" in scene
    assert "RoomContextPanel" in scene
    assert "MonthlyReportModal" in scene
    assert "PanelBacking" not in scene
    assert 'text = "公司经营面板"' not in scene
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


def test_godot_main_scene_uses_mad_games_tycoon_style_hud_layout():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")
    project = (GODOT / "project.godot").read_text(encoding="utf-8")
    design = (ROOT / "docs" / "godot_tycoon_main_ui_design.md").read_text(encoding="utf-8")

    assert "疯狂游戏大亨 2" in design
    assert "房间主导" in design
    assert "底部工具栏" in design
    assert "右侧常驻看板退场" in design

    assert "window/size/mode=2" in project
    assert 'window/stretch/mode="canvas_items"' in project
    assert 'window/stretch/aspect="expand"' in project
    assert "offset_right = 1152.0" not in scene
    assert "offset_bottom = 648.0" not in scene
    assert "anchors_preset = 15" in scene
    assert "anchor_right = 1.0" in scene
    assert "anchor_bottom = 1.0" in scene
    assert "offset_left = 816.0" not in scene
    assert "offset_top = 24.0" not in scene
    panel_block = scene.split('[node name="G2OperationsPanel" type="Control" parent="."', 1)[
        1
    ].split("\n\n", 1)[0]
    assert "mouse_filter = 2" in panel_block
    assert 'node name="TopStatusBar" type="ColorRect" parent="G2OperationsPanel"' in scene
    assert 'node name="BottomActionDock" type="ColorRect" parent="G2OperationsPanel"' in scene
    assert 'node name="FloatingEventFeed" type="ColorRect" parent="G2OperationsPanel"' in scene
    assert 'node name="RoomContextPanel" type="ColorRect" parent="G2OperationsPanel"' in scene
    assert 'node name="MonthlyReportModal" type="ColorRect" parent="G2OperationsPanel"' in scene
    assert "visible = false" in scene

    assert 'new NodePath("TopStatusBar/MetricsLabel")' in panel_script
    assert 'new NodePath("FloatingEventFeed/StatusLabel")' in panel_script
    assert 'new NodePath("RoomContextPanel/CapacityLabel")' in panel_script
    assert 'new NodePath("MonthlyReportModal/ReportLabel")' in panel_script

    assert (
        'ConnectButton("BottomActionDock/ToolGroups/BuildTools/ProductZoneButton", SelectProductZoneTool)'
        in panel_script
    )
    assert (
        'ConnectButton("BottomActionDock/ToolGroups/EmployeeTools/HireProductButton", HireProductEmployee)'
        in panel_script
    )
    assert (
        'ConnectButton("TopStatusBar/TimeButtons/TripleSpeedButton", SetTripleSpeed)'
        in panel_script
    )
    assert (
        'ConnectButton("MonthlyReportModal/ReportCloseButton", HideMonthlyReport)' in panel_script
    )
    assert "ShowMonthlyReport()" in panel_script
    assert "EnsureResponsiveHudLayout()" in panel_script
    assert "LayoutBottomDock(" in panel_script


def test_godot_auto_month_report_is_non_blocking_and_reopenable():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert (
        'node name="OpenReportButton" type="Button" parent="G2OperationsPanel/FloatingEventFeed"'
        in scene
    )
    assert 'ConnectButton("FloatingEventFeed/OpenReportButton", ShowMonthlyReport)' in panel_script
    assert "SetReportAvailable(false)" in panel_script
    assert "SetReportAvailable(true)" in panel_script
    assert "SettleMonthFromCurrentIntent(clearBuildMode: true, showReport: true)" in panel_script
    assert "SettleMonthFromCurrentIntent(clearBuildMode: false, showReport: false)" in panel_script
    assert "if (showReport)" in panel_script
    assert "第 {result.Month} 月已结算，点击查看月报。" in panel_script


def test_godot_room_context_panel_tracks_selected_office_cell():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert (
        'node name="ContextLabel" type="Label" parent="G2OperationsPanel/RoomContextPanel"' in scene
    )
    assert 'new NodePath("RoomContextPanel/ContextLabel")' in panel_script
    assert "private Label? ContextLabel" in panel_script
    assert "UpdateRoomContext(x, y, occupantId);" in panel_script
    assert "private void UpdateRoomContext(int x, int y, string occupantId)" in panel_script
    assert "FindZoneAt(x, y)" in panel_script
    assert "FindFacilityAt(x, y)" in panel_script
    assert "ContextLabel," in panel_script


def test_godot_office_view_keeps_kairosoft_style_grid_interaction_readable():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")

    assert "mouse_filter = 2" in scene
    assert (
        "GridVisibleByDefault = true" in scene
        or "GridVisibleByDefault { get; set; } = true" in grid_script
    )
    assert (
        "DefaultGridAlpha = 0.08" in scene
        or "DefaultGridAlpha { get; set; } = 0.08f" in grid_script
    )
    assert (
        "BuildModeGridAlpha = 0.24" in scene
        or "BuildModeGridAlpha { get; set; } = 0.24f" in grid_script
    )

    assert "DefaultGridAlpha" in grid_script
    assert "DrawOfficeFrame" in grid_script
    assert "UsePseudo3DProjection" in grid_script
    assert "DrawProjectedFloorTiles" in grid_script
    assert "DrawProjectedGridLines" in grid_script
    assert "DrawProjectedCellMarker" in grid_script
    assert "DrawTextureRectRegion(" in grid_script
    assert "for (var x = 0; x < GridWidth; x++)" in grid_script
    assert "for (var y = 0; y < GridHeight; y++)" in grid_script
    assert "buildModeEnabled ? BuildModeGridAlpha : DefaultGridAlpha" in grid_script


def test_godot_office_view_keeps_selection_feedback_after_grid_click():
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "private OfficeCell selectedCell = new(-1, -1);" in grid_script
    assert "SelectionColor" in grid_script
    assert "selectedCell = cell;" in grid_script
    assert "DrawSelectedCell();" in grid_script
    assert "private void DrawSelectedCell()" in grid_script
    assert "DrawProjectedCellMarker(selectedCell" in grid_script

    assert "OfficeGridView.GridCellHovered += OnGridCellHovered;" in panel_script
    assert "private void OnGridCellHovered(int x, int y, string occupantId)" in panel_script
    assert "悬停格子" in panel_script


def test_godot_office_view_uses_mouse_event_position_for_grid_automation():
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")

    assert "GetCellAtEventPosition(InputEventMouse inputEvent)" in grid_script
    assert "inputEvent.Position" in grid_script
    assert "GetCellAtWorldPosition(GetGlobalMousePosition())" not in grid_script


def test_godot_office_view_has_projection_foundation_not_static_background():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    projection_script = (SCRIPTS / "OfficeProjection.cs").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")

    assert "public readonly struct OfficeProjection" in projection_script
    assert "CellToScreen" in projection_script
    assert "ScreenToCell" in projection_script
    assert "CellDiamond" in projection_script
    assert "CellBounds" in projection_script

    assert "UsePseudo3DProjection { get; set; } = true" in grid_script
    assert "ProjectedTileWidth" in grid_script
    assert "ProjectedTileHeight" in grid_script
    assert "ProjectedOrigin" in grid_script
    assert "GetProjectedCellAtLocalPosition" in grid_script
    assert "BuildProjection()" in grid_script
    assert "DrawOfficeShellFoundation" in grid_script
    assert "DrawProjectedFloorTiles" in grid_script
    assert "DrawProjectedZoneOverlay" in grid_script
    assert "ProjectedVisualSlot" in grid_script
    assert "ScreenToCell(local)" in grid_script

    assert 'node name="OfficeBackdrop" type="ColorRect"' in scene
    assert "company-main-scene-background-v0.7.1.png" not in scene
    assert 'texture = ExtResource("16")' not in scene


def test_godot_office_view_draws_pseudo3d_build_previews():
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")

    assert "private OfficeRect? zonePreviewRect;" in grid_script
    assert "private OfficeRect? facilityPreviewRect;" in grid_script
    assert "PreviewValidColor" in grid_script
    assert "PreviewInvalidColor" in grid_script
    assert "ShowZoneSelectionPreview" in grid_script
    assert "ShowFacilityPlacementPreview" in grid_script
    assert "ClearBuildPreview" in grid_script
    assert "DrawBuildPreviews();" in grid_script
    assert "DrawProjectedRectPreview" in grid_script
    assert "facilityPreviewValid ? PreviewValidColor : PreviewInvalidColor" in grid_script


def test_godot_operations_panel_updates_previews_from_hovered_cells():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")
    facility_script = (SCRIPTS / "FacilityPlacementController.cs").read_text(encoding="utf-8")

    assert "UpdateBuildPreview(x, y);" in panel_script
    assert "var startX = hasZoneStart ? zoneStartX : x;" in panel_script
    assert "ShowZoneSelectionPreview(" in panel_script
    assert "ShowFacilityPlacementPreview(" in panel_script
    assert "GetSelectedFacilityPlacementFailure(zoneId, x, y)" in panel_script
    assert "OfficeGridView?.ClearBuildPreview();" in panel_script
    assert "ClearActiveBuildMode()" in panel_script

    assert "SelectedFacilityWidth" in facility_script
    assert "SelectedFacilityHeight" in facility_script
    assert "CanPlaceSelectedFacility" in facility_script
    assert "definition.AllowedZoneTypeIds.Contains(zone.ZoneTypeId)" in facility_script


def test_godot_g2_company_progress_data_and_loader_exist():
    content_database = (SCRIPTS / "ContentDatabase.cs").read_text(encoding="utf-8")
    validator = (ROOT / "scripts" / "validate_godot_content.py").read_text(encoding="utf-8")

    for data_file in [
        GODOT / "data" / "company" / "company_goals.json",
        GODOT / "data" / "company" / "revenue_targets.json",
        GODOT / "data" / "company" / "achievements.json",
        GODOT / "data" / "actions" / "derived_actions.json",
    ]:
        assert data_file.is_file(), f"missing G2 content data: {data_file.relative_to(ROOT)}"
        text = data_file.read_text(encoding="utf-8")
        assert '"schema_version": "godot-content.g2"' in text
        assert '"items"' in text

    assert "CompanyGoals" in content_database
    assert "RevenueTargets" in content_database
    assert "Achievements" in content_database
    assert "DerivedActions" in content_database
    assert 'LoadItems("company/company_goals.json")' in content_database
    assert 'LoadItems("actions/derived_actions.json")' in content_database

    assert '"company_goals"' in validator
    assert '"revenue_targets"' in validator
    assert '"achievements"' in validator
    assert '"derived_actions"' in validator
    assert '"godot-content.g2"' in validator


def test_godot_g2_business_intent_and_core_facts_are_wired():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    bridge = (SCRIPTS / "GodotTurnBridge.cs").read_text(encoding="utf-8")
    intent_snapshot = (SCRIPTS / "BusinessIntentSnapshot.cs").read_text(encoding="utf-8")
    intent_controller = (SCRIPTS / "BusinessIntentController.cs").read_text(encoding="utf-8")
    result_snapshot = (SCRIPTS / "TurnResultSnapshot.cs").read_text(encoding="utf-8")
    core_intent = (
        ROOT / "csharp" / "StartupSim.Core" / "Contracts" / "BusinessIntentSnapshot.cs"
    ).read_text(encoding="utf-8")
    core_fact = (
        ROOT / "csharp" / "StartupSim.Core" / "Contracts" / "BusinessFactSnapshot.cs"
    ).read_text(encoding="utf-8")
    core_result = (ROOT / "csharp" / "StartupSim.Core" / "Contracts" / "TurnResult.cs").read_text(
        encoding="utf-8"
    )
    engine = (
        ROOT / "csharp" / "StartupSim.Core" / "Engines" / "DeterministicTurnEngine.cs"
    ).read_text(encoding="utf-8")

    assert "BusinessIntentController" in scene
    assert 'CapacityPreviewControllerPath = NodePath("../CapacityPreviewController")' in scene
    assert "BuildCurrentIntent" in intent_controller
    assert "BusinessIntentSnapshot.FromOfficeCapacity" in intent_controller
    assert "ExecuteBusinessIntent" in bridge
    assert "ExecuteBusinessIntent(CurrentState, intent.ToCoreIntent())" in bridge

    assert "ProductFocus" in intent_snapshot
    assert "SalesFocus" in intent_snapshot
    assert "StabilityFocus" in intent_snapshot
    assert "OrganizationFocus" in intent_snapshot
    assert "MonthlyFixedCost" in intent_snapshot
    assert "ToCoreIntent()" in intent_snapshot

    assert "public sealed class BusinessIntentSnapshot" in core_intent
    assert "public sealed class BusinessFactSnapshot" in core_fact
    assert "IList<BusinessFactSnapshot> BusinessFacts" in core_result
    assert "BuildBusinessFacts" in engine
    assert "ExecuteBusinessIntent(GameState currentState, BusinessIntentSnapshot intent)" in engine

    assert "BusinessFactsText" in result_snapshot
    assert "string.Join" in result_snapshot


def test_godot_g2_local_save_and_replay_panel_are_mounted():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")
    save_script = (SCRIPTS / "LocalSaveController.cs").read_text(encoding="utf-8")
    progress_script = (SCRIPTS / "CompanyProgressController.cs").read_text(encoding="utf-8")

    assert "LocalSaveController" in scene
    assert "CompanyProgressController" in scene
    assert "ReplayLabel" in scene
    assert "SaveButton" in scene
    assert "LoadButton" in scene
    assert "GoalsLabelPath" in panel_script
    assert "ReplayLabelPath" in panel_script
    assert "LocalSaveControllerPath" in scene
    assert "CompanyProgressControllerPath" in scene
    assert "BusinessIntentControllerPath" in scene

    assert "SaveCurrentRun" in save_script
    assert "LoadCurrentRun" in save_script
    assert "BuildReplaySummary" in save_script
    assert "user://startup-sim-save.json" in save_script
    assert "GodotTurnBridge" not in save_script

    assert "RefreshProgress" in progress_script
    assert "BuildGoalSummary" in progress_script
    assert "BuildAchievementSummary" in progress_script
    assert "现金流可支撑时间" in progress_script
    assert "Runway" not in progress_script

    assert (
        'ConnectButton("BottomActionDock/ToolGroups/MetaTools/SaveButton", SaveRun)' in panel_script
    )
    assert (
        'ConnectButton("BottomActionDock/ToolGroups/MetaTools/LoadButton", LoadRun)' in panel_script
    )
    assert "SetLabel(GoalsLabel" in panel_script
    assert "SetLabel(ReplayLabel" in panel_script


def test_godot_main_scene_keeps_operations_hud_inside_default_viewport():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert 'node name="TopStatusBar" type="ColorRect" parent="G2OperationsPanel"' in scene
    assert 'node name="BottomActionDock" type="ColorRect" parent="G2OperationsPanel"' in scene
    assert "offset_right = 1152.0" not in scene
    assert "offset_bottom = 648.0" not in scene
    assert "EnsureResponsiveHudLayout()" in panel_script
    assert "GetViewportRect().Size" in panel_script
    assert "offset_left = 816.0" not in scene
    assert "offset_top = 24.0" not in scene
    assert "offset_left = 840.0" not in scene
    assert "offset_right = 1240.0" not in scene


def test_godot_month_settlement_updates_top_metrics_snapshot():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "MetricsLabelPath" in panel_script
    assert "private Label? MetricsLabel" in panel_script
    assert "SetLabel(MetricsLabel, BuildMetricsText(result));" in panel_script
    assert "private static string BuildMetricsText(TurnResultSnapshot result)" in panel_script
    assert "BuildCashSupportTimeText(result)" in panel_script
    assert "现金流可支撑时间" in panel_script
    assert "Runway" not in panel_script
    assert "跑道" not in panel_script


def test_godot_facility_failure_feedback_names_valid_zone():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "RequiredZoneText(FacilityPlacementController.SelectedFacilityTypeId)" in panel_script
    assert "只能放在" in panel_script
    assert '"product_whiteboard" => "研发区"' in panel_script
    assert '"starter_server_rack" => "服务器区"' in panel_script


def test_godot_speed_buttons_show_persistent_selected_state():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "SetSpeedButtonState(3f)" in panel_script
    assert "SetSpeedButtonState(2f)" in panel_script
    assert "SetSpeedButtonState(1f)" in panel_script
    assert "SetSpeedButtonState(0f)" in panel_script
    assert ".ButtonPressed = speedMultiplier" in panel_script


def test_godot_endgame_loop_starts_paused_and_stops_on_terminal_month():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    time_script = (SCRIPTS / "TimeProgressController.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert (
        "SpeedMultiplier = 0.0" in scene
        or "[Export] public float SpeedMultiplier { get; set; } = 0f;" in time_script
    )
    assert "public float SpeedMultiplier { get; set; } = 0f;" in time_script
    assert "IsEndgameResult(result)" in panel_script
    assert "ShowEndingReview(result)" in panel_script
    assert "TimeProgressController?.SetPaused();" in panel_script
    assert "第 12 月" in panel_script
    assert "现金耗尽" in panel_script


def test_godot_crisis_actions_are_mounted_and_use_core_bridge():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    for node_name in ["SellFacilityButton", "ReduceCostButton", "BridgeFundingButton"]:
        assert node_name in scene

    assert (
        'ConnectButton("BottomActionDock/ToolGroups/CrisisTools/SellFacilityButton", SellSelectedFacility)'
        in panel_script
    )
    assert (
        'ConnectButton("BottomActionDock/ToolGroups/CrisisTools/ReduceCostButton", ReduceFixedCost)'
        in panel_script
    )
    assert (
        'ConnectButton("BottomActionDock/ToolGroups/CrisisTools/BridgeFundingButton", SeekBridgeFunding)'
        in panel_script
    )
    assert "融资60万出让8%" in panel_script
    assert "TurnBridge.ExecuteCommand" in panel_script
    assert "现金流可支撑时间" in panel_script


def test_godot_tycoon_hud_uses_management_art_for_iconized_controls():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")

    assert "godot-g1-art-pack-v1.9-management-panel-detail-ui" in scene
    for resource_id in [
        "ActionIconHire",
        "ActionIconSell",
        "ActionIconTrain",
        "ActionIconUpgrade",
        "ActionIconPause",
        "ActionIconFastForward",
        "ObjectiveProgressBarFrame",
    ]:
        assert resource_id in scene

    for icon_assignment in [
        'icon = ExtResource("ActionIconPause")',
        'icon = ExtResource("ActionIconFastForward")',
        'icon = ExtResource("ActionIconHire")',
        'icon = ExtResource("ActionIconTrain")',
        'icon = ExtResource("ActionIconSell")',
    ]:
        assert icon_assignment in scene


def test_godot_tycoon_icon_buttons_are_grouped_for_adaptive_viewports():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "custom_minimum_size = Vector2(56, 36)" in scene
    assert "custom_minimum_size = Vector2(64, 48)" in scene
    assert "custom_minimum_size = Vector2(74, 36)" in scene
    assert "expand_icon = true" in scene
    assert "DockCategoryTabs" in scene
    assert "RoomsCategoryButton" in scene
    assert "FacilitiesCategoryButton" in scene
    assert "EmployeesCategoryButton" in scene
    assert "FinanceCategoryButton" in scene
    assert "SystemCategoryButton" in scene
    assert "BottomActionDock/ToolGroups/BuildTools" in scene
    assert "BottomActionDock/ToolGroups/FacilityTools" in scene
    assert "BottomActionDock/ToolGroups/EmployeeTools" in scene
    assert "BottomActionDock/ToolGroups/CrisisTools" in scene
    assert "BottomActionDock/ToolGroups/MetaTools" in scene
    assert "ConstrainHudButtons()" in panel_script
    assert "ConnectDockCategoryButtons()" in panel_script
    assert "ShowDockCategory(" in panel_script
    assert "ApplyButtonChrome(" in panel_script
    assert "ApplyButtonIcon(" in panel_script
    assert "godot-g1-art-pack-v2.2-tycoon-action-icons/exports/icons_48" in panel_script
    assert '"product_room_icon.png"' in panel_script
    assert '"facility_sell_icon.png"' in panel_script
    assert 'ActionIcon("monthly_report_icon.png")' in panel_script
    assert "new Vector2(56f, 36f)" in panel_script
    assert "new Vector2(64f, 48f)" in panel_script
    assert "new Vector2(74f, 36f)" in panel_script
    assert 'SetButtonIconExpand("TopStatusBar/TimeButtons/AdvanceMonthButton")' in panel_script
    assert '!path.EndsWith("AdvanceMonthButton", StringComparison.Ordinal)' in panel_script


def test_godot_building_and_object_operations_pause_time_without_losing_speed():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "PauseForPlayerOperation()" in panel_script
    assert "RestoreSpeedAfterPlayerOperation()" in panel_script
    assert "speedBeforePlayerOperation" in panel_script
    assert "playerOperationPausedTime" in panel_script
    assert "PauseForPlayerOperation();" in panel_script
    assert "RestoreSpeedAfterPlayerOperation();" in panel_script


def test_godot_mcp_client_accepts_array_args_without_editor_errors():
    client = (GODOT / "addons" / "godot_mcp" / "mcp_client.gd").read_text(encoding="utf-8")

    assert "func _normalize_tool_args(raw_args: Variant) -> Dictionary:" in client
    assert "raw_args is Dictionary" in client
    assert "raw_args is Array" in client
    assert 'return {"items": raw_args}' in client
    assert 'var args: Dictionary = _normalize_tool_args(message.get(&"args", {}))' in client


def test_godot_plugin_spike_addons_are_vendored_with_rule_boundaries():
    plugin_expectations = {
        "phantom_camera": ("Phantom Camera", "0.11.0.2"),
        "dialogue_manager": ("Dialogue Manager", "3.10.4"),
        "gdUnit4": ("gdUnit4", "6.1.3"),
    }

    for addon_dir, (plugin_name, version) in plugin_expectations.items():
        plugin_cfg = GODOT / "addons" / addon_dir / "plugin.cfg"
        assert plugin_cfg.exists(), f"{addon_dir} plugin.cfg is missing"
        content = plugin_cfg.read_text(encoding="utf-8")
        assert f'name="{plugin_name}"' in content
        assert f'version="{version}"' in content

    notes = (ROOT / "docs" / "godot_plugin_integration_notes.md").read_text(encoding="utf-8")
    assert "C# Core 是规则核心" in notes
    assert "Godot 插件只负责表现层、交互层、编辑器效率和测试辅助" in notes
    assert "Phantom Camera" in notes
    assert "Dialogue Manager" in notes
    assert "GdUnit4" in notes


def test_godot_plugin_spike_keeps_third_party_csharp_out_of_project_build():
    csproj = (GODOT / "StartupSimGodot.csproj").read_text(encoding="utf-8")

    assert '<Compile Remove="addons\\**\\*.cs" />' in csproj


def test_godot_selected_object_panel_is_wired_to_room_facility_and_employee_actions():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    for node_name in [
        "ObjectActionPanel",
        "ObjectActionTitleLabel",
        "ObjectActionDetailLabel",
        "UpgradeSelectedFacilityButton",
        "SellSelectedFacilityButton",
        "TrainSelectedObjectButton",
    ]:
        assert node_name in scene

    assert "ShowObjectActionPanel(" in panel_script
    assert "HideObjectActionPanel()" in panel_script
    assert "UpdateObjectActionPanel(" in panel_script
    assert (
        'ConnectButton("ObjectActionPanel/UpgradeSelectedFacilityButton", UpgradeSelectedFacility)'
        in panel_script
    )
    assert (
        'ConnectButton("ObjectActionPanel/SellSelectedFacilityButton", SellSelectedFacility)'
        in panel_script
    )
    assert (
        'ConnectButton("ObjectActionPanel/TrainSelectedObjectButton", TrainSelectedEmployee)'
        in panel_script
    )
    assert "RefreshSelectedObjectContext()" in panel_script
    assert "BuildZoneCreatedStatus(" in panel_script
    assert "BuildFacilityPlacedStatus(" in panel_script
    assert "BuildEmployeeAssignedStatus(" in panel_script
    assert "经营菜单" in panel_script


def test_godot_selected_facility_sell_removes_core_layout_and_visual_object():
    layout = (ROOT / "csharp" / "StartupSim.Core" / "Office" / "OfficeLayout.cs").read_text(
        encoding="utf-8"
    )
    placement_script = (SCRIPTS / "FacilityPlacementController.cs").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "public bool RemoveFacility(string facilityId)" in layout
    assert "facilityOccupants.Remove(cell)" in layout
    assert "facilities.Remove(facility)" in layout
    assert "public bool SellFacility(string facilityId)" in placement_script
    assert "Layout.RemoveFacility(facilityId)" in placement_script
    assert "public void HideFacilityVisual(string facilityId)" in grid_script
    assert "facilityVisuals.Remove(facilityId)" in grid_script
    assert "FacilityPlacementController.SellFacility(selectedFacilityId)" in panel_script
    assert "OfficeGridView?.HideFacilityVisual(selectedFacilityId)" in panel_script


def test_godot_object_readability_badges_and_stage_progress_are_visible():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")
    progress_script = (SCRIPTS / "CompanyProgressController.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "ObjectiveTracker" in scene
    assert "ObjectiveProgressBar" in scene
    assert "ObjectiveTitleLabel" in scene
    assert "LastStageProgressPercent" in progress_script
    assert "BuildStageProgressPercent(" in progress_script
    assert "UpdateObjectiveProgressBar()" in panel_script

    assert "Level { get; init; }" in grid_script
    assert "DrawFacilityLevelBadge" in grid_script
    assert "DrawEmployeeRoleBadge" in grid_script
    assert "DrawSelectionObjectBadge" in grid_script


def test_godot_event_feed_uses_lightweight_game_cues_not_developer_log_copy():
    scene = (SCENES / "main.tscn").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "EventCueBadge" in scene
    assert "SetEventCue(" in panel_script
    assert "FormatEventCue(" in panel_script
    assert "SetLabel(StatusLabel, FormatEventCue" in panel_script


def test_godot_facility_failure_feedback_explains_real_invalid_reason():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")
    placement_script = (SCRIPTS / "FacilityPlacementController.cs").read_text(encoding="utf-8")

    assert "GetSelectedFacilityPlacementFailure" in placement_script
    assert "需要 1x2 连续服务器区" in panel_script
    assert "格子已被其他设施占用" in placement_script
    assert "当前房间类型不匹配" in placement_script
    assert "设施占地超出当前房间" in placement_script


def test_godot_room_context_shows_bottleneck_and_next_action():
    progress_script = (SCRIPTS / "CompanyProgressController.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "阶段目标：" in progress_script
    assert "瓶颈：" in progress_script
    assert "下一步：" in progress_script
    assert "BuildRoomAdvice" in panel_script
    assert "房间产出" in panel_script
    assert "推荐操作" in panel_script


def test_godot_time_loop_drives_monthly_business_settlement():
    controller = (SCRIPTS / "TimeProgressController.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "public override void _Process(double delta)" in controller
    assert "GameHoursPerRealSecond" in controller
    assert "AdvanceGameHours((float)delta * GameHoursPerRealSecond)" in controller
    assert "accumulatedNeedHours" in controller
    assert "while (accumulatedMonthHours >= HoursPerMonth)" in controller
    assert "SubmitBusinessIntent(BusinessIntentSnapshot intent)" in controller
    assert "MonthIndex = result.Month" in controller

    assert "TimeProgressController.MonthReady += OnMonthReady" in panel_script
    assert "private void OnMonthReady(int monthIndex)" in panel_script
    assert "SettleMonthFromCurrentIntent(clearBuildMode: false, showReport: false)" in panel_script
    assert "TimeProgressController.SubmitBusinessIntent(lastIntent)" in panel_script


def test_godot_month_settlement_pauses_and_resets_time_after_each_month():
    controller = (SCRIPTS / "TimeProgressController.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "public void ResetMonthProgress()" in controller
    assert "accumulatedMonthHours = 0f" in controller

    advance_body = _method_body(panel_script, "public void AdvanceMonth()")
    assert "PauseForSettlementReview();" in advance_body
    assert "SettleMonthFromCurrentIntent(clearBuildMode: true, showReport: true)" in advance_body

    settle_body = _method_body(
        panel_script,
        "private void SettleMonthFromCurrentIntent(bool clearBuildMode, bool showReport)",
    )
    assert "PauseForSettlementReview();" in settle_body
    pause_body = _method_body(panel_script, "private void PauseForSettlementReview()")
    assert "TimeProgressController?.ResetMonthProgress();" in pause_body
    assert "SetSpeedButtonState(0f);" in panel_script


def test_godot_endgame_locks_mutating_gameplay_operations():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "private bool GuardEndgameOperation(string operationName)" in panel_script
    assert "结局复盘已锁定经营操作" in panel_script

    for signature in [
        "private void SelectZoneTool(string zoneTypeId, string displayName)",
        "private void SelectFacilityTool(string facilityTypeId, string displayName)",
        "private void HireAndAssignEmployee(",
        "public void TrainSelectedEmployee()",
        "public void SellSelectedFacility()",
        "public void UpgradeSelectedFacility()",
        "private void ApplyBridgeCommand(string command, string statusPrefix)",
    ]:
        body = _method_body(panel_script, signature)
        assert "GuardEndgameOperation" in body

    ending_body = _method_body(
        panel_script, "private void ShowEndingReview(TurnResultSnapshot result)"
    )
    assert "ClearActiveBuildMode();" in ending_body
    assert "HideObjectActionPanel();" in ending_body
    assert "SetGameplayControlsLocked(true);" in ending_body


def test_godot_dock_category_switch_cancels_hidden_build_or_place_mode():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    body = _method_body(panel_script, "private void ShowDockCategory(string category)")
    assert "ClearActiveBuildMode();" in body
    assert body.index("ClearActiveBuildMode();") < body.index("activeDockCategory = category;")


def test_godot_hud_feedback_text_is_readable_and_not_clipped():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "ConfigureReadableLabels();" in panel_script
    assert "ApplyReadableLabel(StatusLabel" in panel_script
    assert "ApplyReadableLabel(ObjectActionDetailLabel" in panel_script
    assert "ApplyReadableLabel(ReportLabel" in panel_script
    assert "FormatGoalSummary(summary)" in panel_script
    assert "FormatCapacitySummary(summary)" in panel_script
    assert ".Take(3)" in panel_script
    assert "ClipText = false" in panel_script
    assert 'SetControlRect("FloatingEventFeed"' in panel_script
    assert "520f, 72f" in panel_script
    assert 'SetControlRect("ObjectActionPanel"' in panel_script
    assert "360f, 260f" in panel_script
    assert 'SetControlRect(\n            "MonthlyReportModal"' in panel_script
    assert "640f" in panel_script
    assert "460f" in panel_script


def test_godot_metrics_show_initial_core_state_before_first_month():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "RefreshInitialMetrics()" in panel_script
    assert "TimeProgressController?.TurnBridge?.CurrentState.Metrics" in panel_script
    assert "private static string BuildMetricsText(GameMetrics metrics)" in panel_script
    assert "等待月结" not in panel_script


def test_godot_office_grid_uses_low_noise_floor_and_separate_visual_slots():
    grid_script = (SCRIPTS / "OfficeGridView.cs").read_text(encoding="utf-8")

    assert "FloorTileTextureAlpha" in grid_script
    assert "ShouldDrawDecorativeFloorTile(x, y)" in grid_script
    assert "var sourceColumn = 0;" in grid_script
    assert "var sourceRow = 0;" in grid_script
    assert "new Color(1f, 1f, 1f, FloorTileTextureAlpha)" in grid_script
    assert "EmployeeVisualSlot" in grid_script
    assert "FacilityVisualSlot" in grid_script


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
        "office-tile-expansion-atlas-v0.4.png",
        "facility-placement-atlas-v0.3.png",
        "employee-status-icon-atlas-v0.5.png",
        "zone-state-overlay-atlas-v0.6.png",
        "feedback-portrait-sheet-v0.7.png",
        "company-main-scene-background-v0.7.1.png",
        "business-feedback-fx-atlas-v0.8.png",
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
    assert "OfficeTileExpansionAtlas" in controller
    assert "FacilityPlacementAtlas" in controller
    assert "EmployeeStatusIconAtlas" in controller
    assert "ZoneStateOverlayAtlasV06" in controller
    assert "FeedbackPortraitAtlasV07" in controller
    assert "MainSceneBackground" in controller
    assert "BusinessFeedbackFxAtlas" in controller
    assert "ValidateTexture(MainSceneBackground" in controller
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


def test_godot_action_buttons_explain_cost_output_and_business_role():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "ConfigureActionTooltips();" in panel_script
    assert "private void ConfigureActionTooltips()" in panel_script
    assert "SetButtonTooltip(" in panel_script
    for path in [
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
    ]:
        assert path in panel_script

    for label in [
        "研发区",
        "销售区",
        "服务器区",
        "办公桌",
        "产品白板",
        "服务器机柜",
        "成本",
        "月成本",
        "产出",
        "适用",
        "现金流可支撑时间",
    ]:
        assert label in panel_script
    assert "Runway" not in panel_script
    assert "跑道" not in panel_script


def test_godot_build_preview_explains_area_cost_and_failure_reasons():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")
    facility_script = (SCRIPTS / "FacilityPlacementController.cs").read_text(encoding="utf-8")

    hover_body = _method_body(
        panel_script, "private void OnGridCellHovered(int x, int y, string occupantId)"
    )
    assert "if (IsBuildModeActive())" in hover_body
    assert "BuildZonePreviewStatus(" in panel_script
    assert "BuildFacilityPreviewStatus(" in panel_script
    assert "GetSelectedFacilityPlacementFailure(zoneId, x, y)" in panel_script
    assert "ShowFacilityPlacementPreview(" in panel_script
    assert "isValid" in panel_script
    for label in ["预览", "格", "成本", "不可放置", "右键或 Esc 取消"]:
        assert label in panel_script

    assert "public OfficeFacilityDefinition? SelectedFacilityDefinition" in facility_script
    assert "GetSelectedFacilityPlacementFailure" in facility_script


def test_godot_build_mode_can_be_cancelled_by_right_click_or_escape():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "public override void _UnhandledInput(InputEvent @event)" in panel_script
    assert "InputEventMouseButton" in panel_script
    assert "MouseButton.Right" in panel_script
    assert "InputEventKey" in panel_script
    assert "Key.Escape" in panel_script
    assert "CancelCurrentBuildMode();" in panel_script


def test_godot_monthly_report_is_structured_business_report():
    report_script = (SCRIPTS / "MonthlyReportController.cs").read_text(encoding="utf-8")
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")

    assert "BuildCashSupportTimeText(snapshot)" in report_script
    assert "BuildNextMonthAdvice(snapshot)" in report_script
    for label in ["收入", "成本", "产品", "用户", "现金流", "下月建议"]:
        assert label in report_script
    assert "销售区" in report_script
    assert "销售员工" in report_script
    assert "服务器区" in report_script
    assert "MRR" in report_script
    assert "经营事实" in panel_script

    assert "DeterministicTurnEngine" not in report_script
    assert "StartupSim.Core.Engines" not in report_script


def test_godot_commercialization_chain_is_visible_without_rewriting_rules():
    panel_script = (SCRIPTS / "G2OperationsPanelController.cs").read_text(encoding="utf-8")
    report_script = (SCRIPTS / "MonthlyReportController.cs").read_text(encoding="utf-8")

    combined = panel_script + "\n" + report_script
    for label in ["产品", "用户", "MRR", "销售区", "销售员工", "服务器区"]:
        assert label in combined
    assert "BuildCommercializationHint(" in report_script
    assert "C# Core" not in report_script
    assert "DeterministicTurnEngine" not in panel_script
