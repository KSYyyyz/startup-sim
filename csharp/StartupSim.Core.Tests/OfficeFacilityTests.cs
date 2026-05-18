using StartupSim.Core.Office;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class OfficeFacilityTests
{
    [Fact]
    public void PlaceFacilityRequiresMatchingZoneAndFreeCells()
    {
        var layout = new OfficeLayout(8, 6, 64, new[] { "product_zone", "sales_zone" });
        layout.TryDefineZone("product_zone", "研发区", new OfficeRect(0, 0, 4, 3), out var zone);
        var desk = new OfficeFacilityDefinition(
            "basic_desk",
            new[] { "product_zone", "sales_zone" },
            width: 1,
            height: 1,
            baseCost: 3000,
            monthlyCost: 200);

        var placed = layout.TryPlaceFacility(desk, zone!.Id, 1, 1, out var facility);

        Assert.True(placed);
        Assert.NotNull(facility);
        Assert.Equal("basic_desk", facility!.FacilityTypeId);
        Assert.Equal(zone.Id, facility.ZoneId);
        Assert.False(layout.TryPlaceFacility(desk, zone.Id, 1, 1, out _));
    }

    [Fact]
    public void PlaceFacilityRejectsWrongZoneAndOutOfZoneFootprint()
    {
        var layout = new OfficeLayout(8, 6, 64, new[] { "product_zone", "server_zone" });
        layout.TryDefineZone("product_zone", "研发区", new OfficeRect(0, 0, 3, 2), out var zone);
        var serverRack = new OfficeFacilityDefinition(
            "starter_server_rack",
            new[] { "server_zone" },
            width: 1,
            height: 2,
            baseCost: 30000,
            monthlyCost: 3000);
        var whiteboard = new OfficeFacilityDefinition(
            "product_whiteboard",
            new[] { "product_zone" },
            width: 2,
            height: 1,
            baseCost: 8000,
            monthlyCost: 300);

        Assert.False(layout.TryPlaceFacility(serverRack, zone!.Id, 0, 0, out _));
        Assert.False(layout.TryPlaceFacility(whiteboard, zone.Id, 2, 1, out _));
    }

    [Fact]
    public void UpgradeFacilityAppliesLevelCostAndEffects()
    {
        var layout = new OfficeLayout(8, 6, 64, new[] { "product_zone" });
        layout.TryDefineZone("product_zone", "研发区", new OfficeRect(0, 0, 4, 3), out var zone);
        var whiteboard = new OfficeFacilityDefinition(
            "product_whiteboard",
            new[] { "product_zone" },
            width: 2,
            height: 1,
            baseCost: 8000,
            monthlyCost: 300);
        layout.TryPlaceFacility(whiteboard, zone!.Id, 0, 0, out var facility);
        var upgrade = new OfficeFacilityUpgradeDefinition(
            "product_whiteboard_level_2",
            "product_whiteboard",
            level: 2,
            upgradeCost: 12000,
            monthlyCostDelta: 500);

        Assert.True(layout.TryUpgradeFacility(facility!.Id, upgrade));
        Assert.Equal(2, facility.Level);
        Assert.Equal(20000, facility.TotalCost);
        Assert.Equal(800, facility.MonthlyCost);
    }

    [Fact]
    public void FacilitySnapshotIsReadyForGodotPersistence()
    {
        var layout = new OfficeLayout(8, 6, 64, new[] { "product_zone" });
        layout.TryDefineZone("product_zone", "研发区", new OfficeRect(0, 0, 4, 3), out var zone);
        var desk = new OfficeFacilityDefinition(
            "basic_desk",
            new[] { "product_zone" },
            width: 1,
            height: 1,
            baseCost: 3000,
            monthlyCost: 200);
        layout.TryPlaceFacility(desk, zone!.Id, 1, 1, out var facility);

        var snapshot = layout.ToSnapshot();

        Assert.Single(snapshot.Facilities);
        Assert.Equal(facility!.Id, snapshot.Facilities[0].Id);
        Assert.Equal("basic_desk", snapshot.Facilities[0].FacilityTypeId);
        Assert.Equal(1, snapshot.Facilities[0].X);
    }
}
