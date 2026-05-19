using System.Collections.Generic;
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

    [Signal]
    public delegate void GridCellHoveredEventHandler(int x, int y, string occupantId);

    [Signal]
    public delegate void GridCellSelectedEventHandler(int x, int y, string occupantId);

    private OfficeGrid grid = new(12, 8, 64);
    private OfficeCell hoveredCell = new(-1, -1);
    private OfficeCell selectedCell = new(-1, -1);
    private readonly Dictionary<string, string> zoneTypeByZoneId = new();
    private readonly Dictionary<string, FacilityVisual> facilityVisuals = new();
    private readonly Dictionary<string, EmployeeVisual> employeeVisuals = new();

    [Export] public int GridWidth { get; set; } = 12;
    [Export] public int GridHeight { get; set; } = 8;
    [Export] public int CellSize { get; set; } = 64;
    [Export] public Texture2D? OfficeTileAtlas { get; set; }
    [Export] public Texture2D? ZoneOverlayAtlas { get; set; }
    [Export] public Texture2D? FacilityAtlas { get; set; }
    [Export] public Texture2D? EmployeeAtlas { get; set; }
    [Export] public Texture2D? StatusIconAtlas { get; set; }
    [Export] public bool GridVisibleByDefault { get; set; } = true;
    [Export] public float DefaultGridAlpha { get; set; } = 0.08f;
    [Export] public float BuildModeGridAlpha { get; set; } = 0.24f;
    [Export] public float FloorTileTextureAlpha { get; set; } = 0.38f;
    [Export] public Color OfficeBackdropColor { get; set; } = new(0.17f, 0.19f, 0.18f, 1f);
    [Export] public Color FloorBaseColor { get; set; } = new(0.72f, 0.69f, 0.62f, 1f);
    [Export] public Color GridColor { get; set; } = new(0.25f, 0.42f, 0.66f, 0.55f);
    [Export] public Color HoverColor { get; set; } = new(0.2f, 0.55f, 0.95f, 0.22f);
    [Export] public Color SelectionColor { get; set; } = new(0.98f, 0.86f, 0.28f, 0.75f);
    [Export] public Color OccupiedColor { get; set; } = new(0.95f, 0.72f, 0.25f, 0.25f);

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
        return grid.WorldToCell(local.X, local.Y);
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

    public override void _Draw()
    {
        DrawOfficeBackdrop();
        DrawOfficeFrame();
        DrawOccupiedCells();
        DrawFacilityVisuals();
        DrawEmployeeVisuals();
        if (ShouldDrawGrid())
        {
            DrawGridLines();
        }

        DrawSelectedCell();
        DrawHoverCell();
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

    private void DrawOfficeBackdrop()
    {
        var officeRect = new Rect2(0, 0, GridWidth * CellSize, GridHeight * CellSize);
        DrawRect(officeRect.Grow(14f), OfficeBackdropColor, filled: true);
        DrawFloorTiles(officeRect);
    }

    private void DrawOfficeFrame()
    {
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
                    cell.Grow(1f),
                    AtlasCell(OfficeTileAtlas, columns: 8, rows: 5, column: sourceColumn, row: sourceRow),
                    new Color(1f, 1f, 1f, FloorTileTextureAlpha));
            }
        }
    }

    private static bool ShouldDrawDecorativeFloorTile(int x, int y)
    {
        return x == 0 || y == 0 || (x + y) % 5 == 0;
    }

    private void DrawOccupiedCells()
    {
        foreach (var cell in grid.ToSnapshot().OccupiedCells)
        {
            var rect = CellRect(cell.X, cell.Y);
            if (ZoneOverlayAtlas != null)
            {
                var sourceColumn = zoneTypeByZoneId.TryGetValue(cell.OccupantId, out var zoneTypeId)
                    ? zoneTypeId switch
                    {
                        "product_zone" => 0,
                        "sales_zone" => 1,
                        "server_zone" => 2,
                        _ => 0
                    }
                    : 0;
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

    private void DrawFacilityVisuals()
    {
        if (FacilityAtlas == null)
        {
            return;
        }

        foreach (var visual in facilityVisuals.Values)
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
                FacilityVisualSlot(visual.X, visual.Y),
                AtlasCell(FacilityAtlas, columns: 6, rows: 3, sourceColumn, row: 0),
                Colors.White);
        }
    }

    private void DrawEmployeeVisuals()
    {
        if (EmployeeAtlas == null)
        {
            return;
        }

        var offset = 0;
        foreach (var visual in employeeVisuals.Values)
        {
            var sourceRow = visual.RoleId switch
            {
                "product_engineer" => 0,
                "sales_specialist" => 2,
                "ops_engineer" => 4,
                _ => 0
            };
            var sourceColumn = 9;
            var destination = EmployeeVisualSlot(visual.X, visual.Y);
            destination.Position += new Vector2(offset * 4, -offset * 3);
            DrawTextureRectRegion(
                EmployeeAtlas,
                destination,
                AtlasCell(EmployeeAtlas, columns: 12, rows: 6, sourceColumn, row: sourceRow),
                Colors.White);

            DrawStatusIcon(visual.X, visual.Y, offset);
            offset++;
        }
    }

    private void DrawStatusIcon(int x, int y, int offset)
    {
        if (StatusIconAtlas == null)
        {
            return;
        }

        var iconSize = CellSize * 0.28f;
        var destination = new Rect2(
            x * CellSize + CellSize - iconSize - 4,
            y * CellSize + 4 + offset * 3,
            iconSize,
            iconSize);
        DrawTextureRectRegion(
            StatusIconAtlas,
            destination,
            AtlasCell(StatusIconAtlas, columns: 8, rows: 4, column: 12 % 8, row: 12 / 8),
            Colors.White);
    }

    private Rect2 FacilityVisualSlot(int x, int y)
    {
        return CellRect(x, y).Grow(-6f);
    }

    private Rect2 EmployeeVisualSlot(int x, int y)
    {
        return new Rect2(
            x * CellSize + CellSize * 0.1f,
            y * CellSize + CellSize * 0.04f,
            CellSize * 0.52f,
            CellSize * 0.78f);
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

        var rect = new Rect2(selectedCell.X * CellSize, selectedCell.Y * CellSize, CellSize, CellSize);
        DrawRect(rect.Grow(-3f), new Color(SelectionColor.R, SelectionColor.G, SelectionColor.B, 0.16f), filled: true);
        DrawRect(rect.Grow(-2f), SelectionColor, filled: false, width: 3f);
    }

    private bool ShouldDrawGrid()
    {
        return buildModeEnabled || GridVisibleByDefault;
    }

    private Rect2 CellRect(int x, int y)
    {
        return new Rect2(x * CellSize, y * CellSize, CellSize, CellSize);
    }

    private static Rect2 AtlasCell(Texture2D atlas, int columns, int rows, int column, int row)
    {
        var textureSize = atlas.GetSize();
        var cellWidth = textureSize.X / columns;
        var cellHeight = textureSize.Y / rows;
        return new Rect2(column * cellWidth, row * cellHeight, cellWidth, cellHeight);
    }
}
