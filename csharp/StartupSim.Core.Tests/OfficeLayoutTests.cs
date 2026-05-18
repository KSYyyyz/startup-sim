using StartupSim.Core.Office;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class OfficeLayoutTests
{
    [Fact]
    public void DefineZoneOccupiesGridCellsAndReturnsStableZone()
    {
        var layout = new OfficeLayout(12, 8, 64, new[] { "product_zone", "sales_zone", "server_zone" });

        var created = layout.TryDefineZone(
            "product_zone",
            "第一研发区",
            new OfficeRect(1, 1, 3, 2),
            out var zone);

        Assert.True(created);
        Assert.NotNull(zone);
        Assert.Equal("product_zone", zone!.ZoneTypeId);
        Assert.Equal("第一研发区", zone.DisplayName);
        Assert.True(layout.Grid.IsOccupied(new OfficeCell(1, 1)));
        Assert.Equal(zone.Id, layout.Grid.GetOccupant(new OfficeCell(3, 2)));
    }

    [Fact]
    public void DefineZoneRejectsUnknownTypesOverlapsAndOutOfBounds()
    {
        var layout = new OfficeLayout(6, 4, 64, new[] { "product_zone", "sales_zone" });

        Assert.True(layout.TryDefineZone("product_zone", "研发区", new OfficeRect(1, 1, 2, 2), out _));
        Assert.False(layout.TryDefineZone("server_zone", "服务器区", new OfficeRect(3, 1, 1, 1), out _));
        Assert.False(layout.TryDefineZone("sales_zone", "销售区", new OfficeRect(2, 2, 2, 1), out _));
        Assert.False(layout.TryDefineZone("sales_zone", "销售区", new OfficeRect(5, 3, 2, 1), out _));
    }

    [Fact]
    public void RenameAndRemoveZoneUpdateLayoutState()
    {
        var layout = new OfficeLayout(6, 4, 64, new[] { "product_zone", "sales_zone" });
        layout.TryDefineZone("product_zone", "研发区", new OfficeRect(1, 1, 2, 2), out var zone);

        Assert.True(layout.RenameZone(zone!.Id, "产品作战室"));
        Assert.Equal("产品作战室", layout.Zones[0].DisplayName);

        Assert.True(layout.RemoveZone(zone.Id));
        Assert.Empty(layout.Zones);
        Assert.False(layout.Grid.IsOccupied(new OfficeCell(1, 1)));
    }

    [Fact]
    public void SnapshotListsZonesForGodotPersistence()
    {
        var layout = new OfficeLayout(12, 8, 64, new[] { "product_zone", "sales_zone", "server_zone" });
        layout.TryDefineZone("product_zone", "研发区", new OfficeRect(0, 0, 3, 2), out var product);
        layout.TryDefineZone("sales_zone", "销售区", new OfficeRect(4, 0, 2, 2), out _);

        var snapshot = layout.ToSnapshot();

        Assert.Equal(12, snapshot.Grid.Width);
        Assert.Equal(2, snapshot.Zones.Count);
        Assert.Equal(product!.Id, snapshot.Zones[0].Id);
        Assert.Equal("product_zone", snapshot.Zones[0].ZoneTypeId);
        Assert.Equal(3, snapshot.Zones[0].Width);
    }
}
