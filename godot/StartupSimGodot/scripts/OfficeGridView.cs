using Godot;
using StartupSim.Core.Office;

namespace StartupSim.Godot;

public partial class OfficeGridView : Node2D
{
    [Signal]
    public delegate void GridCellHoveredEventHandler(int x, int y, string occupantId);

    [Signal]
    public delegate void GridCellSelectedEventHandler(int x, int y, string occupantId);

    private OfficeGrid grid = new(12, 8, 64);
    private OfficeCell hoveredCell = new(-1, -1);

    [Export] public int GridWidth { get; set; } = 12;
    [Export] public int GridHeight { get; set; } = 8;
    [Export] public int CellSize { get; set; } = 64;
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

    public override void _Draw()
    {
        DrawOccupiedCells();
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

    private void DrawOccupiedCells()
    {
        foreach (var cell in grid.ToSnapshot().OccupiedCells)
        {
            DrawRect(
                new Rect2(cell.X * CellSize, cell.Y * CellSize, CellSize, CellSize),
                OccupiedColor,
                filled: true);
        }
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
}
