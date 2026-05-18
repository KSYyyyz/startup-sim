using StartupSim.Core.Office;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class OfficeGridTests
{
    [Fact]
    public void GridCreatesLargePixelCellsAndMapsWorldPosition()
    {
        var grid = new OfficeGrid(width: 12, height: 8, cellSize: 64);

        Assert.Equal(12, grid.Width);
        Assert.Equal(8, grid.Height);
        Assert.Equal(64, grid.CellSize);
        Assert.Equal(new OfficeCell(2, 3), grid.WorldToCell(160, 224));
        Assert.True(grid.Contains(new OfficeCell(11, 7)));
        Assert.False(grid.Contains(new OfficeCell(12, 7)));
    }

    [Fact]
    public void OccupyRectangleRejectsOutOfBoundsAndOverlaps()
    {
        var grid = new OfficeGrid(width: 6, height: 4, cellSize: 64);

        Assert.True(grid.TryOccupy(new OfficeRect(1, 1, 2, 2), "product_zone"));
        Assert.True(grid.IsOccupied(new OfficeCell(1, 1)));
        Assert.True(grid.IsOccupied(new OfficeCell(2, 2)));
        Assert.False(grid.TryOccupy(new OfficeRect(2, 2, 2, 1), "sales_zone"));
        Assert.False(grid.TryOccupy(new OfficeRect(5, 3, 2, 1), "server_zone"));
    }

    [Fact]
    public void ReleaseRectangleFreesCellsForLaterUse()
    {
        var grid = new OfficeGrid(width: 6, height: 4, cellSize: 64);
        var rect = new OfficeRect(1, 1, 2, 2);

        Assert.True(grid.TryOccupy(rect, "product_zone"));
        grid.Release(rect);

        Assert.False(grid.IsOccupied(new OfficeCell(1, 1)));
        Assert.True(grid.TryOccupy(rect, "sales_zone"));
        Assert.Equal("sales_zone", grid.GetOccupant(new OfficeCell(1, 1)));
    }

    [Fact]
    public void SnapshotListsOccupiedCellsForGodotSerialization()
    {
        var grid = new OfficeGrid(width: 4, height: 3, cellSize: 64);

        grid.TryOccupy(new OfficeRect(0, 0, 2, 1), "product_zone");
        var snapshot = grid.ToSnapshot();

        Assert.Equal(4, snapshot.Width);
        Assert.Equal(3, snapshot.Height);
        Assert.Equal(64, snapshot.CellSize);
        Assert.Equal(2, snapshot.OccupiedCells.Count);
        Assert.Contains(snapshot.OccupiedCells, cell => cell.X == 0 && cell.Y == 0);
        Assert.Contains(snapshot.OccupiedCells, cell => cell.X == 1 && cell.Y == 0);
    }
}
