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
    [Export] public Color GridColor { get; set; } = new(0.25f, 0.42f, 0.66f, 0.55f);
    [Export] public Color HoverColor { get; set; } = new(0.2f, 0.55f, 0.95f, 0.22f);
    [Export] public Color OccupiedColor { get; set; } = new(0.95f, 0.72f, 0.25f, 0.25f);

    public OfficeGrid Grid => grid;

    public override void _Ready()
    {
        grid = new OfficeGrid(GridWidth, GridHeight, CellSize);
        QueueRedraw();
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (@event is InputEventMouseMotion)
        {
            UpdateHoveredCell();
            return;
        }

        if (@event is InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left })
        {
            var cell = GetCellAtWorldPosition(GetGlobalMousePosition());
            if (!grid.Contains(cell))
            {
                return;
            }

            EmitSignal(SignalName.GridCellSelected, cell.X, cell.Y, grid.GetOccupant(cell) ?? string.Empty);
        }
    }

    public OfficeCell GetCellAtWorldPosition(Vector2 worldPosition)
    {
        var local = ToLocal(worldPosition);
        return grid.WorldToCell(local.X, local.Y);
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

    public override void _Draw()
    {
        DrawFloorTiles();
        DrawOccupiedCells();
        DrawFacilityVisuals();
        DrawEmployeeVisuals();
        DrawGridLines();
        DrawHoverCell();
    }

    private void UpdateHoveredCell()
    {
        var cell = GetCellAtWorldPosition(GetGlobalMousePosition());
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

        for (var x = 0; x <= GridWidth; x++)
        {
            var pixelX = x * CellSize;
            DrawLine(new Vector2(pixelX, 0), new Vector2(pixelX, heightPixels), GridColor, 1f);
        }

        for (var y = 0; y <= GridHeight; y++)
        {
            var pixelY = y * CellSize;
            DrawLine(new Vector2(0, pixelY), new Vector2(widthPixels, pixelY), GridColor, 1f);
        }
    }

    private void DrawFloorTiles()
    {
        if (OfficeTileAtlas == null)
        {
            return;
        }

        var source = AtlasCell(OfficeTileAtlas, columns: 8, rows: 4, column: 0, row: 0);
        for (var x = 0; x < GridWidth; x++)
        {
            for (var y = 0; y < GridHeight; y++)
            {
                DrawTextureRectRegion(
                    OfficeTileAtlas,
                    CellRect(x, y),
                    source,
                    Colors.White);
            }
        }
    }

    private void DrawOccupiedCells()
    {
        foreach (var cell in grid.ToSnapshot().OccupiedCells)
        {
            var rect = CellRect(cell.X, cell.Y);
            if (ZoneOverlayAtlas != null)
            {
                DrawTextureRectRegion(
                    ZoneOverlayAtlas,
                    rect,
                    AtlasCell(ZoneOverlayAtlas, columns: 8, rows: 5, column: 0, row: 0),
                    new Color(1f, 1f, 1f, 0.72f));
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
                "product_whiteboard" => 1,
                "starter_server_rack" => 3,
                _ => 0
            };
            DrawTextureRectRegion(
                FacilityAtlas,
                CellRect(visual.X, visual.Y).Grow(-4),
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
            var sourceColumn = visual.RoleId switch
            {
                "sales_specialist" => 1,
                "ops_engineer" => 3,
                _ => 0
            };
            var destination = CellRect(visual.X, visual.Y).Grow(-10);
            destination.Position += new Vector2(offset * 4, -offset * 3);
            DrawTextureRectRegion(
                EmployeeAtlas,
                destination,
                AtlasCell(EmployeeAtlas, columns: 6, rows: 5, sourceColumn, row: 1),
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
            AtlasCell(StatusIconAtlas, columns: 8, rows: 4, column: 0, row: 0),
            Colors.White);
    }

    private void DrawHoverCell()
    {
        if (!grid.Contains(hoveredCell))
        {
            return;
        }

        DrawRect(
            new Rect2(hoveredCell.X * CellSize, hoveredCell.Y * CellSize, CellSize, CellSize),
            HoverColor,
            filled: true);
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
