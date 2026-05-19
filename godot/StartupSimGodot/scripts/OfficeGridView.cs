using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using StartupSim.Core.Office;

namespace StartupSim.Godot;

public partial class OfficeGridView : Node2D
{
    private sealed class FacilityVisual
    {
        public string FacilityTypeId { get; init; } = string.Empty;
        public int X { get; init; }
        public int Y { get; init; }
    }

    private sealed class EmployeeVisual
    {
        public string RoleId { get; init; } = string.Empty;
        public int X { get; init; }
        public int Y { get; init; }
    }

    private sealed class VisualStackItem
    {
        public int SortKey { get; init; }
        public Action Draw { get; init; } = () => { };
    }

    [Signal]
    public delegate void GridCellHoveredEventHandler(int x, int y, string occupantId);

    [Signal]
    public delegate void GridCellSelectedEventHandler(int x, int y, string occupantId);

    private OfficeGrid grid = new(12, 8, 64);
    private OfficeCell hoveredCell = new(-1, -1);
    private OfficeCell selectedCell = new(-1, -1);
    private OfficeRect? zonePreviewRect;
    private OfficeRect? facilityPreviewRect;
    private bool facilityPreviewValid;
    private readonly Dictionary<string, string> zoneTypeByZoneId = new();
    private readonly Dictionary<string, FacilityVisual> facilityVisuals = new();
    private readonly Dictionary<string, EmployeeVisual> employeeVisuals = new();

    [Export] public int GridWidth { get; set; } = 12;
    [Export] public int GridHeight { get; set; } = 8;
    [Export] public int CellSize { get; set; } = 64;
    [Export] public bool UsePseudo3DProjection { get; set; } = true;
    [Export] public float ProjectedTileWidth { get; set; } = 72f;
    [Export] public float ProjectedTileHeight { get; set; } = 40f;
    [Export] public Vector2 ProjectedOrigin { get; set; } = new(330f, 42f);
    [Export] public Texture2D? OfficeTileAtlas { get; set; }
    [Export] public Texture2D? ZoneOverlayAtlas { get; set; }
    [Export] public Texture2D? FacilityAtlas { get; set; }
    [Export] public Texture2D? EmployeeAtlas { get; set; }
    [Export] public Texture2D? StatusIconAtlas { get; set; }
    [Export] public Texture2D? Pseudo3DStructureAtlas { get; set; }
    [Export] public Texture2D? ZoneCarpetAtlas { get; set; }
    [Export] public Texture2D? LargeFacilityAtlas { get; set; }
    [Export] public Texture2D? EmployeePseudo3DAtlas { get; set; }
    [Export] public Texture2D? BusinessFeedbackBubbleAtlas { get; set; }
    [Export] public bool GridVisibleByDefault { get; set; } = true;
    [Export] public float DefaultGridAlpha { get; set; } = 0.08f;
    [Export] public float BuildModeGridAlpha { get; set; } = 0.24f;
    [Export] public float FloorTileTextureAlpha { get; set; } = 0.38f;
    [Export] public Color OfficeBackdropColor { get; set; } = new(0.16f, 0.18f, 0.17f, 1f);
    [Export] public Color FloorBaseColor { get; set; } = new(0.73f, 0.70f, 0.64f, 1f);
    [Export] public Color GridColor { get; set; } = new(0.25f, 0.42f, 0.66f, 0.55f);
    [Export] public Color HoverColor { get; set; } = new(0.2f, 0.55f, 0.95f, 0.22f);
    [Export] public Color SelectionColor { get; set; } = new(0.98f, 0.86f, 0.28f, 0.75f);
    [Export] public Color OccupiedColor { get; set; } = new(0.95f, 0.72f, 0.25f, 0.25f);
    [Export] public Color ZonePreviewColor { get; set; } = new(0.34f, 0.72f, 1f, 0.28f);
    [Export] public Color PreviewValidColor { get; set; } = new(0.32f, 0.86f, 0.42f, 0.34f);
    [Export] public Color PreviewInvalidColor { get; set; } = new(0.95f, 0.24f, 0.18f, 0.36f);

    public OfficeGrid Grid => grid;
    private bool buildModeEnabled;

    public override void _Ready()
    {
        grid = new OfficeGrid(GridWidth, GridHeight, CellSize);
        buildModeEnabled = GridVisibleByDefault;
        QueueRedraw();
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (@event is InputEventMouseMotion mouseMotion)
        {
            UpdateHoveredCell(mouseMotion);
            return;
        }

        if (@event is InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left } mouseButton)
        {
            var cell = GetCellAtEventPosition(mouseButton);
            if (!grid.Contains(cell))
            {
                return;
            }

            selectedCell = cell;
            QueueRedraw();
            EmitSignal(SignalName.GridCellSelected, cell.X, cell.Y, grid.GetOccupant(cell) ?? string.Empty);
        }
    }

    public OfficeCell GetCellAtWorldPosition(Vector2 worldPosition)
    {
        var local = ToLocal(worldPosition);
        return UsePseudo3DProjection ? GetProjectedCellAtLocalPosition(local) : grid.WorldToCell(local.X, local.Y);
    }

    public OfficeCell GetProjectedCellAtLocalPosition(Vector2 local)
    {
        return BuildProjection().ScreenToCell(local);
    }

    public OfficeCell GetCellAtEventPosition(InputEventMouse inputEvent)
    {
        return GetCellAtWorldPosition(GetViewport().CanvasTransform.AffineInverse() * inputEvent.Position);
    }

    public bool TryOccupyRect(int x, int y, int width, int height, string occupantId)
    {
        var occupied = grid.TryOccupy(new OfficeRect(x, y, width, height), occupantId);
        if (occupied)
        {
            QueueRedraw();
        }

        return occupied;
    }

    public void ReleaseRect(int x, int y, int width, int height)
    {
        grid.Release(new OfficeRect(x, y, width, height));
        QueueRedraw();
    }

    public void RegisterZoneVisual(string zoneId, string zoneTypeId)
    {
        if (string.IsNullOrWhiteSpace(zoneId) || string.IsNullOrWhiteSpace(zoneTypeId))
        {
            return;
        }

        zoneTypeByZoneId[zoneId] = zoneTypeId;
        QueueRedraw();
    }

    public void ClearZoneVisual(string zoneId)
    {
        if (zoneTypeByZoneId.Remove(zoneId))
        {
            QueueRedraw();
        }
    }

    public void ShowFacilityVisual(string facilityId, string facilityTypeId, int x, int y)
    {
        if (string.IsNullOrWhiteSpace(facilityId))
        {
            return;
        }

        facilityVisuals[facilityId] = new FacilityVisual
        {
            FacilityTypeId = facilityTypeId,
            X = x,
            Y = y
        };
        QueueRedraw();
    }

    public void ShowEmployeeVisual(string employeeId, string roleId, int x, int y)
    {
        if (string.IsNullOrWhiteSpace(employeeId))
        {
            return;
        }

        employeeVisuals[employeeId] = new EmployeeVisual
        {
            RoleId = roleId,
            X = x,
            Y = y
        };
        QueueRedraw();
    }

    public void SetBuildMode(bool enabled)
    {
        if (buildModeEnabled == enabled)
        {
            return;
        }

        buildModeEnabled = enabled;
        QueueRedraw();
    }

    public void ShowZoneSelectionPreview(int startX, int startY, int endX, int endY, string zoneTypeId)
    {
        _ = zoneTypeId;
        zonePreviewRect = SelectionRect(startX, startY, endX, endY);
        facilityPreviewRect = null;
        QueueRedraw();
    }

    public void ShowFacilityPlacementPreview(int x, int y, int width, int height, bool isValid)
    {
        zonePreviewRect = null;
        facilityPreviewRect = new OfficeRect(x, y, Mathf.Max(1, width), Mathf.Max(1, height));
        facilityPreviewValid = isValid;
        QueueRedraw();
    }

    public void ClearBuildPreview()
    {
        if (zonePreviewRect == null && facilityPreviewRect == null)
        {
            return;
        }

        zonePreviewRect = null;
        facilityPreviewRect = null;
        QueueRedraw();
    }

    public override void _Draw()
    {
        DrawOfficeBackdrop();
        DrawOfficeFrame();
        DrawOccupiedCells();
        DrawBuildPreviews();
        if (UsePseudo3DProjection)
        {
            DrawPseudo3DVisualStack();
        }
        else
        {
            DrawFacilityVisuals();
            DrawEmployeeVisuals();
        }

        if (ShouldDrawGrid())
        {
            DrawGridLines();
        }

        DrawSelectedCell();
        DrawHoverCell();
    }

    private OfficeProjection BuildProjection()
    {
        return new OfficeProjection(ProjectedTileWidth, ProjectedTileHeight, ProjectedOrigin);
    }

    private void UpdateHoveredCell(InputEventMouse inputEvent)
    {
        var cell = GetCellAtEventPosition(inputEvent);
        if (cell.Equals(hoveredCell))
        {
            return;
        }

        hoveredCell = cell;
        if (grid.Contains(cell))
        {
            EmitSignal(SignalName.GridCellHovered, cell.X, cell.Y, grid.GetOccupant(cell) ?? string.Empty);
        }

        QueueRedraw();
    }

    private void DrawGridLines()
    {
        if (UsePseudo3DProjection)
        {
            DrawProjectedGridLines(BuildProjection());
            return;
        }

        var widthPixels = GridWidth * CellSize;
        var heightPixels = GridHeight * CellSize;
        var alpha = buildModeEnabled ? BuildModeGridAlpha : DefaultGridAlpha;
        var gridColor = new Color(GridColor.R, GridColor.G, GridColor.B, alpha);

        for (var x = 0; x <= GridWidth; x++)
        {
            var pixelX = x * CellSize;
            DrawLine(new Vector2(pixelX, 0), new Vector2(pixelX, heightPixels), gridColor, 1f);
        }

        for (var y = 0; y <= GridHeight; y++)
        {
            var pixelY = y * CellSize;
            DrawLine(new Vector2(0, pixelY), new Vector2(widthPixels, pixelY), gridColor, 1f);
        }
    }

    private void DrawProjectedGridLines(OfficeProjection projection)
    {
        var alpha = buildModeEnabled ? BuildModeGridAlpha : DefaultGridAlpha;
        var gridColor = new Color(GridColor.R, GridColor.G, GridColor.B, alpha);

        for (var x = 0; x < GridWidth; x++)
        {
            for (var y = 0; y < GridHeight; y++)
            {
                DrawDiamondOutline(projection.CellDiamond(x, y), gridColor, 1f);
            }
        }
    }

    private void DrawOfficeBackdrop()
    {
        if (UsePseudo3DProjection)
        {
            var projection = BuildProjection();
            DrawOfficeShellFoundation(projection);
            DrawPseudo3DFloorTiles(projection);
            DrawPseudo3DOfficeShell(projection);
            return;
        }

        var officeRect = new Rect2(0, 0, GridWidth * CellSize, GridHeight * CellSize);
        DrawRect(officeRect.Grow(14f), OfficeBackdropColor, filled: true);
        DrawFloorTiles(officeRect);
    }

    private void DrawOfficeShellFoundation(OfficeProjection projection)
    {
        var floor = new[]
        {
            projection.CellToScreen(0, 0),
            projection.CellToScreen(GridWidth, 0),
            projection.CellToScreen(GridWidth, GridHeight),
            projection.CellToScreen(0, GridHeight)
        };
        DrawPolygon(floor, Fill(OfficeBackdropColor, floor.Length));

        var wallColor = new Color(0.28f, 0.30f, 0.28f, 0.92f);
        var rimColor = new Color(0.08f, 0.09f, 0.08f, 0.78f);
        DrawLine(floor[0], floor[1], wallColor, 10f);
        DrawLine(floor[0], floor[3], wallColor, 10f);
        DrawLine(floor[2], floor[3], rimColor, 6f);
        DrawLine(floor[1], floor[2], rimColor, 6f);
    }

    private void DrawOfficeFrame()
    {
        if (UsePseudo3DProjection)
        {
            var projection = BuildProjection();
            var floor = new[]
            {
                projection.CellToScreen(0, 0),
                projection.CellToScreen(GridWidth, 0),
                projection.CellToScreen(GridWidth, GridHeight),
                projection.CellToScreen(0, GridHeight)
            };
            DrawDiamondOutline(floor, new Color(0.08f, 0.09f, 0.08f, 0.8f), 3f);
            return;
        }

        var officeRect = new Rect2(0, 0, GridWidth * CellSize, GridHeight * CellSize);
        DrawRect(officeRect.Grow(3f), new Color(0.08f, 0.09f, 0.08f, 0.8f), filled: false, width: 3f);
        DrawLine(
            new Vector2(0, GridHeight * CellSize),
            new Vector2(GridWidth * CellSize, GridHeight * CellSize),
            new Color(0.3f, 0.28f, 0.23f, 0.7f),
            8f);
    }

    private void DrawFloorTiles(Rect2 officeRect)
    {
        for (var x = 0; x < GridWidth; x++)
        {
            for (var y = 0; y < GridHeight; y++)
            {
                var cell = CellRect(x, y);
                DrawRect(cell, FloorBaseColor, filled: true);

                if (OfficeTileAtlas == null || !ShouldDrawDecorativeFloorTile(x, y))
                {
                    continue;
                }

                var sourceColumn = 0;
                var sourceRow = 0;
                DrawTextureRectRegion(
                    OfficeTileAtlas,
                    cell,
                    AtlasCell(OfficeTileAtlas, columns: 8, rows: 5, column: sourceColumn, row: sourceRow),
                    new Color(1f, 1f, 1f, FloorTileTextureAlpha));
            }
        }
    }

    private void DrawProjectedFloorTiles(OfficeProjection projection)
    {
        DrawPseudo3DFloorTiles(projection);
    }

    private void DrawPseudo3DFloorTiles(OfficeProjection projection)
    {
        for (var x = 0; x < GridWidth; x++)
        {
            for (var y = 0; y < GridHeight; y++)
            {
                var diamond = projection.CellDiamond(x, y);
                if (Pseudo3DStructureAtlas != null)
                {
                    var sourceColumn = (x + y) % 5 == 0 ? 1 : 0;
                    DrawTextureRectRegion(
                        Pseudo3DStructureAtlas,
                        ProjectedTileAtlasSlot(projection, x, y, 1.18f, 2.08f),
                        AtlasCell(Pseudo3DStructureAtlas, columns: 8, rows: 4, column: sourceColumn, row: 0),
                        Colors.White);
                }
                else
                {
                    var shade = (x + y) % 2 == 0 ? 0.02f : -0.02f;
                    var tileColor = new Color(
                        Mathf.Clamp(FloorBaseColor.R + shade, 0f, 1f),
                        Mathf.Clamp(FloorBaseColor.G + shade, 0f, 1f),
                        Mathf.Clamp(FloorBaseColor.B + shade, 0f, 1f),
                        FloorBaseColor.A);
                    DrawPolygon(diamond, Fill(tileColor, diamond.Length));
                }

                if (ShouldDrawDecorativeFloorTile(x, y))
                {
                    DrawDiamondOutline(diamond, new Color(0.9f, 0.86f, 0.74f, 0.18f), 1.5f);
                }
            }
        }
    }

    private void DrawPseudo3DOfficeShell(OfficeProjection projection)
    {
        if (Pseudo3DStructureAtlas == null)
        {
            return;
        }

        for (var x = 0; x < GridWidth; x++)
        {
            DrawStructureTile(projection, x, 0, column: x % 4 == 1 ? 2 : 0, row: 1, widthScale: 1.2f, heightScale: 2.2f);
        }

        for (var y = 1; y < GridHeight; y++)
        {
            DrawStructureTile(projection, 0, y, column: y % 3 == 0 ? 6 : 3, row: 1, widthScale: 1.2f, heightScale: 2.2f);
        }

        DrawStructureTile(projection, 0, 0, column: 5, row: 1, widthScale: 1.24f, heightScale: 2.3f);
        DrawStructureTile(projection, GridWidth - 1, 0, column: 4, row: 1, widthScale: 1.24f, heightScale: 2.3f);
        DrawStructureTile(projection, GridWidth - 2, GridHeight - 1, column: 1, row: 2, widthScale: 1.55f, heightScale: 2.25f);
    }

    private void DrawStructureTile(
        OfficeProjection projection,
        int x,
        int y,
        int column,
        int row,
        float widthScale,
        float heightScale)
    {
        if (Pseudo3DStructureAtlas == null)
        {
            return;
        }

        DrawTextureRectRegion(
            Pseudo3DStructureAtlas,
            ProjectedTileAtlasSlot(projection, x, y, widthScale, heightScale),
            AtlasCell(Pseudo3DStructureAtlas, columns: 8, rows: 4, column: column, row: row),
            Colors.White);
    }

    private static bool ShouldDrawDecorativeFloorTile(int x, int y)
    {
        return x == 0 || y == 0 || (x + y) % 5 == 0;
    }

    private void DrawOccupiedCells()
    {
        var projection = BuildProjection();
        foreach (var cell in grid.ToSnapshot().OccupiedCells.OrderBy(cell => cell.X + cell.Y).ThenBy(cell => cell.X))
        {
            if (UsePseudo3DProjection)
            {
                DrawZoneCarpets(projection, cell.X, cell.Y, cell.OccupantId);
                continue;
            }

            var rect = CellRect(cell.X, cell.Y);
            if (ZoneOverlayAtlas != null)
            {
                var sourceColumn = ZoneOverlayColumn(cell.OccupantId);
                DrawTextureRectRegion(
                    ZoneOverlayAtlas,
                    rect,
                    AtlasCell(ZoneOverlayAtlas, columns: 6, rows: 5, column: sourceColumn, row: 0),
                    new Color(1f, 1f, 1f, 0.46f));
            }
            else
            {
                DrawRect(rect, OccupiedColor, filled: true);
            }
        }
    }

    private void DrawProjectedZoneOverlay(OfficeProjection projection, int x, int y, string occupantId)
    {
        DrawZoneCarpets(projection, x, y, occupantId);
    }

    private void DrawZoneCarpets(OfficeProjection projection, int x, int y, string occupantId)
    {
        if (ZoneCarpetAtlas != null)
        {
            var sourceColumn = ZoneOverlayColumn(occupantId);
            DrawTextureRectRegion(
                ZoneCarpetAtlas,
                ProjectedTileAtlasSlot(projection, x, y, 1.24f, 2.14f),
                AtlasCell(ZoneCarpetAtlas, columns: 8, rows: 4, column: sourceColumn, row: 0),
                new Color(1f, 1f, 1f, 0.92f));

            return;
        }

        DrawProjectedZoneOverlayFallback(projection, x, y, occupantId);
    }

    private void DrawProjectedZoneOverlayFallback(OfficeProjection projection, int x, int y, string occupantId)
    {
        var zoneColor = ZoneOverlayColor(occupantId);
        var diamond = projection.CellDiamond(x, y);
        DrawPolygon(diamond, Fill(zoneColor, diamond.Length));
        DrawDiamondOutline(diamond, new Color(zoneColor.R, zoneColor.G, zoneColor.B, 0.58f), 1.5f);
    }

    private void DrawBuildPreviews()
    {
        if (zonePreviewRect != null)
        {
            DrawProjectedRectPreview(zonePreviewRect.Value, ZonePreviewColor);
        }

        if (facilityPreviewRect != null)
        {
            var facilityColor = facilityPreviewValid ? PreviewValidColor : PreviewInvalidColor;
            DrawProjectedRectPreview(facilityPreviewRect.Value, facilityColor);
        }
    }

    private void DrawProjectedRectPreview(OfficeRect rect, Color color)
    {
        var outlineColor = new Color(
            Mathf.Clamp(color.R + 0.18f, 0f, 1f),
            Mathf.Clamp(color.G + 0.18f, 0f, 1f),
            Mathf.Clamp(color.B + 0.18f, 0f, 1f),
            Mathf.Clamp(color.A + 0.32f, 0f, 1f));

        if (!UsePseudo3DProjection)
        {
            foreach (var cell in rect.Cells())
            {
                if (!grid.Contains(cell))
                {
                    continue;
                }

                var cellRect = CellRect(cell.X, cell.Y).Grow(-2f);
                DrawRect(cellRect, color, filled: true);
                DrawRect(cellRect, outlineColor, filled: false, width: 2f);
            }

            return;
        }

        var projection = BuildProjection();
        foreach (var cell in rect.Cells())
        {
            if (!grid.Contains(cell))
            {
                continue;
            }

            var diamond = projection.CellDiamond(cell.X, cell.Y);
            DrawPolygon(diamond, Fill(color, diamond.Length));
            DrawDiamondOutline(diamond, outlineColor, 2.5f);
        }
    }

    private int ZoneOverlayColumn(string occupantId)
    {
        return zoneTypeByZoneId.TryGetValue(occupantId, out var zoneTypeId)
            ? zoneTypeId switch
            {
                "product_zone" => 0,
                "sales_zone" => 1,
                "server_zone" => 2,
                _ => 0
            }
            : 0;
    }

    private Color ZoneOverlayColor(string occupantId)
    {
        return zoneTypeByZoneId.TryGetValue(occupantId, out var zoneTypeId)
            ? zoneTypeId switch
            {
                "product_zone" => new Color(0.18f, 0.42f, 0.78f, 0.30f),
                "sales_zone" => new Color(0.28f, 0.62f, 0.34f, 0.30f),
                "server_zone" => new Color(0.44f, 0.32f, 0.68f, 0.32f),
                _ => OccupiedColor
            }
            : OccupiedColor;
    }

    private void DrawFacilityVisuals()
    {
        if (FacilityAtlas == null)
        {
            return;
        }

        var projection = BuildProjection();
        foreach (var visual in facilityVisuals.Values.OrderBy(visual => visual.X + visual.Y).ThenBy(visual => visual.X))
        {
            var sourceColumn = visual.FacilityTypeId switch
            {
                "basic_desk" => 0,
                "product_whiteboard" => 1,
                "starter_server_rack" => 2,
                _ => 0
            };
            DrawTextureRectRegion(
                FacilityAtlas,
                FacilityVisualSlot(projection, visual.X, visual.Y),
                AtlasCell(FacilityAtlas, columns: 6, rows: 3, sourceColumn, row: 0),
                Colors.White);
        }
    }

    private void DrawPseudo3DVisualStack()
    {
        var projection = BuildProjection();
        var stack = new List<VisualStackItem>();

        foreach (var visual in facilityVisuals.Values)
        {
            stack.Add(new VisualStackItem
            {
                SortKey = RenderDepthKey(visual.X, visual.Y, 0),
                Draw = () => DrawLargeFacilityVisual(projection, visual)
            });
        }

        var offset = 0;
        foreach (var visual in employeeVisuals.Values)
        {
            var employeeOffset = offset;
            stack.Add(new VisualStackItem
            {
                SortKey = RenderDepthKey(visual.X, visual.Y, 20 + employeeOffset),
                Draw = () => DrawPseudo3DEmployeeVisual(projection, visual, employeeOffset)
            });
            offset++;
        }

        foreach (var item in stack.OrderBy(item => item.SortKey))
        {
            item.Draw();
        }
    }

    private static int RenderDepthKey(int x, int y, int layerOffset = 0)
    {
        return (x + y) * 1000 + x * 16 + layerOffset;
    }

    private void DrawLargeFacilityVisual(OfficeProjection projection, FacilityVisual visual)
    {
        if (LargeFacilityAtlas != null)
        {
            var (row, column, widthScale, heightScale) = LargeFacilityCell(visual.FacilityTypeId);
            DrawTextureRectRegion(
                LargeFacilityAtlas,
                ProjectedTileAtlasSlot(projection, visual.X, visual.Y, widthScale, heightScale),
                AtlasCell(LargeFacilityAtlas, columns: 8, rows: 4, column: column, row: row),
                Colors.White);
            return;
        }

        if (FacilityAtlas == null)
        {
            return;
        }

        var sourceColumn = visual.FacilityTypeId switch
        {
            "basic_desk" => 0,
            "product_whiteboard" => 1,
            "starter_server_rack" => 2,
            _ => 0
        };
        DrawTextureRectRegion(
            FacilityAtlas,
            FacilityVisualSlot(projection, visual.X, visual.Y),
            AtlasCell(FacilityAtlas, columns: 6, rows: 3, sourceColumn, row: 0),
            Colors.White);
    }

    private static (int Row, int Column, float WidthScale, float HeightScale) LargeFacilityCell(string facilityTypeId)
    {
        return facilityTypeId switch
        {
            "basic_desk" => (0, 1, 1.78f, 2.55f),
            "product_whiteboard" => (0, 4, 1.78f, 2.55f),
            "starter_server_rack" => (2, 1, 1.42f, 3.45f),
            _ => (3, 0, 1.9f, 2.85f)
        };
    }

    private void DrawPseudo3DEmployeeVisual(OfficeProjection projection, EmployeeVisual visual, int offset)
    {
        if (EmployeePseudo3DAtlas != null)
        {
            var sourceRow = visual.RoleId switch
            {
                "product_engineer" => 0,
                "sales_specialist" => 1,
                "ops_engineer" => 2,
                _ => 3
            };
            var destination = EmployeeVisualSlot(projection, visual.X, visual.Y);
            destination.Position += new Vector2(offset * 4, -offset * 3);
            DrawTextureRectRegion(
                EmployeePseudo3DAtlas,
                destination,
                AtlasCell(EmployeePseudo3DAtlas, columns: 12, rows: 4, column: 8, row: sourceRow),
                Colors.White);

            DrawBusinessFeedbackBubble(projection, visual.X, visual.Y, offset);
            return;
        }

        if (EmployeeAtlas == null)
        {
            return;
        }

        var fallbackRow = visual.RoleId switch
        {
            "product_engineer" => 0,
            "sales_specialist" => 2,
            "ops_engineer" => 4,
            _ => 0
        };
        var sourceColumn = 9;
        var fallbackDestination = EmployeeVisualSlot(projection, visual.X, visual.Y);
        fallbackDestination.Position += new Vector2(offset * 4, -offset * 3);
        DrawTextureRectRegion(
            EmployeeAtlas,
            fallbackDestination,
            AtlasCell(EmployeeAtlas, columns: 12, rows: 6, sourceColumn, row: fallbackRow),
            Colors.White);

        DrawStatusIcon(projection, visual.X, visual.Y, offset);
    }

    private void DrawBusinessFeedbackBubble(OfficeProjection projection, int x, int y, int offset)
    {
        if (BusinessFeedbackBubbleAtlas != null)
        {
            DrawTextureRectRegion(
                BusinessFeedbackBubbleAtlas,
                ProjectedBubbleSlot(projection, x, y, offset),
                AtlasCell(BusinessFeedbackBubbleAtlas, columns: 8, rows: 4, column: 0, row: 0),
                Colors.White);
            return;
        }

        DrawStatusIcon(projection, x, y, offset);
    }

    private void DrawEmployeeVisuals()
    {
        if (EmployeeAtlas == null)
        {
            return;
        }

        var projection = BuildProjection();
        var offset = 0;
        foreach (var visual in employeeVisuals.Values.OrderBy(visual => visual.X + visual.Y).ThenBy(visual => visual.X))
        {
            var sourceRow = visual.RoleId switch
            {
                "product_engineer" => 0,
                "sales_specialist" => 2,
                "ops_engineer" => 4,
                _ => 0
            };
            var sourceColumn = 9;
            var destination = EmployeeVisualSlot(projection, visual.X, visual.Y);
            destination.Position += new Vector2(offset * 4, -offset * 3);
            DrawTextureRectRegion(
                EmployeeAtlas,
                destination,
                AtlasCell(EmployeeAtlas, columns: 12, rows: 6, sourceColumn, row: sourceRow),
                Colors.White);

            DrawStatusIcon(projection, visual.X, visual.Y, offset);
            offset++;
        }
    }

    private void DrawStatusIcon(OfficeProjection projection, int x, int y, int offset)
    {
        if (StatusIconAtlas == null)
        {
            return;
        }

        var destination = UsePseudo3DProjection
            ? ProjectedStatusIconSlot(projection, x, y, offset)
            : FlatStatusIconSlot(x, y, offset);
        DrawTextureRectRegion(
            StatusIconAtlas,
            destination,
            AtlasCell(StatusIconAtlas, columns: 8, rows: 4, column: 12 % 8, row: 12 / 8),
            Colors.White);
    }

    private Rect2 FacilityVisualSlot(OfficeProjection projection, int x, int y)
    {
        return UsePseudo3DProjection ? ProjectedVisualSlot(projection, x, y, 1.08f, 1.06f) : CellRect(x, y).Grow(-6f);
    }

    private Rect2 EmployeeVisualSlot(OfficeProjection projection, int x, int y)
    {
        if (UsePseudo3DProjection)
        {
            return ProjectedVisualSlot(projection, x, y, 0.82f, 1.82f);
        }

        return new Rect2(
            x * CellSize + CellSize * 0.1f,
            y * CellSize + CellSize * 0.04f,
            CellSize * 0.52f,
            CellSize * 0.78f);
    }

    private Rect2 ProjectedTileAtlasSlot(
        OfficeProjection projection,
        int x,
        int y,
        float widthScale,
        float heightScale)
    {
        var width = projection.TileWidth * widthScale;
        var height = projection.TileHeight * heightScale;
        var anchor = projection.CellCenter(x, y);
        return new Rect2(anchor.X - width * 0.5f, anchor.Y - height * 0.52f, width, height);
    }

    private Rect2 ProjectedVisualSlot(OfficeProjection projection, int x, int y, float widthScale, float heightScale)
    {
        var width = projection.TileWidth * widthScale;
        var height = projection.TileHeight * heightScale;
        var anchor = projection.FootAnchor(x, y);
        return new Rect2(anchor.X - width * 0.5f, anchor.Y - height, width, height);
    }

    private Rect2 FlatStatusIconSlot(int x, int y, int offset)
    {
        var iconSize = CellSize * 0.28f;
        return new Rect2(
            x * CellSize + CellSize - iconSize - 4,
            y * CellSize + 4 + offset * 3,
            iconSize,
            iconSize);
    }

    private Rect2 ProjectedStatusIconSlot(OfficeProjection projection, int x, int y, int offset)
    {
        var iconSize = projection.TileHeight * 0.56f;
        var anchor = projection.CellCenter(x, y);
        return new Rect2(anchor.X + projection.TileWidth * 0.16f, anchor.Y - projection.TileHeight * 1.08f + offset * 3, iconSize, iconSize);
    }

    private Rect2 ProjectedBubbleSlot(OfficeProjection projection, int x, int y, int offset)
    {
        var iconSize = projection.TileHeight * 0.78f;
        var anchor = projection.CellCenter(x, y);
        return new Rect2(
            anchor.X + projection.TileWidth * 0.14f,
            anchor.Y - projection.TileHeight * 1.55f + offset * 3,
            iconSize,
            iconSize);
    }

    private void DrawHoverCell()
    {
        if (!ShouldDrawGrid())
        {
            return;
        }

        if (!grid.Contains(hoveredCell))
        {
            return;
        }

        if (UsePseudo3DProjection)
        {
            DrawProjectedCellMarker(hoveredCell, HoverColor, filled: true, width: 1f);
            return;
        }

        DrawRect(
            new Rect2(hoveredCell.X * CellSize, hoveredCell.Y * CellSize, CellSize, CellSize),
            HoverColor,
            filled: true);
    }

    private void DrawSelectedCell()
    {
        if (!grid.Contains(selectedCell))
        {
            return;
        }

        if (UsePseudo3DProjection)
        {
            DrawProjectedCellMarker(selectedCell, new Color(SelectionColor.R, SelectionColor.G, SelectionColor.B, 0.16f), filled: true, width: 1f);
            DrawProjectedCellMarker(selectedCell, SelectionColor, filled: false, width: 3f);
            return;
        }

        var rect = new Rect2(selectedCell.X * CellSize, selectedCell.Y * CellSize, CellSize, CellSize);
        DrawRect(rect.Grow(-3f), new Color(SelectionColor.R, SelectionColor.G, SelectionColor.B, 0.16f), filled: true);
        DrawRect(rect.Grow(-2f), SelectionColor, filled: false, width: 3f);
    }

    private void DrawProjectedCellMarker(OfficeCell cell, Color color, bool filled, float width)
    {
        var diamond = BuildProjection().CellDiamond(cell.X, cell.Y);
        if (filled)
        {
            DrawPolygon(diamond, Fill(color, diamond.Length));
            return;
        }

        DrawDiamondOutline(diamond, color, width);
    }

    private bool ShouldDrawGrid()
    {
        return buildModeEnabled || GridVisibleByDefault;
    }

    private static OfficeRect SelectionRect(int startX, int startY, int endX, int endY)
    {
        var x = Mathf.Min(startX, endX);
        var y = Mathf.Min(startY, endY);
        return new OfficeRect(
            x,
            y,
            Mathf.Abs(endX - startX) + 1,
            Mathf.Abs(endY - startY) + 1);
    }

    private Rect2 CellRect(int x, int y)
    {
        return new Rect2(x * CellSize, y * CellSize, CellSize, CellSize);
    }

    private static void DrawDiamondOutline(Node2D canvas, Vector2[] points, Color color, float width)
    {
        for (var index = 0; index < points.Length; index++)
        {
            canvas.DrawLine(points[index], points[(index + 1) % points.Length], color, width);
        }
    }

    private void DrawDiamondOutline(Vector2[] points, Color color, float width)
    {
        DrawDiamondOutline(this, points, color, width);
    }

    private static Color[] Fill(Color color, int count)
    {
        return Enumerable.Repeat(color, count).ToArray();
    }

    private static Rect2 AtlasCell(Texture2D atlas, int columns, int rows, int column, int row)
    {
        var textureSize = atlas.GetSize();
        var cellWidth = textureSize.X / columns;
        var cellHeight = textureSize.Y / rows;
        return new Rect2(column * cellWidth, row * cellHeight, cellWidth, cellHeight);
    }
}
