using System.Collections.Generic;
using System.Linq;
using Godot;
using StartupSim.Core.Office;

namespace StartupSim.Godot;

public partial class FacilityPlacementController : Node
{
    [Signal]
    public delegate void FacilityPlacedEventHandler(string facilityId, string facilityTypeId, string zoneId);

    [Signal]
    public delegate void FacilityUpgradedEventHandler(string facilityId, int level);

    [Signal]
    public delegate void FacilitySoldEventHandler(string facilityId);

    private readonly Dictionary<string, OfficeFacilityDefinition> facilityDefinitions = new();
    private readonly Dictionary<string, OfficeFacilityUpgradeDefinition> upgradeDefinitions = new();

    [Export] public NodePath ZonePaintingControllerPath { get; set; } = new NodePath("");
    [Export] public string SelectedFacilityTypeId { get; set; } = "basic_desk";

    public ZonePaintingController? ZoneController { get; private set; }
    public int SelectedFacilityWidth => facilityDefinitions.TryGetValue(
        SelectedFacilityTypeId,
        out var definition)
            ? definition.Width
            : 1;
    public int SelectedFacilityHeight => facilityDefinitions.TryGetValue(
        SelectedFacilityTypeId,
        out var definition)
            ? definition.Height
            : 1;
    public OfficeFacilityDefinition? SelectedFacilityDefinition => facilityDefinitions.TryGetValue(
        SelectedFacilityTypeId,
        out var definition)
            ? definition
            : null;

    public override void _Ready()
    {
        RegisterG1Definitions();
        if (!ZonePaintingControllerPath.IsEmpty)
        {
            ZoneController = GetNodeOrNull<ZonePaintingController>(ZonePaintingControllerPath);
        }
    }

    public bool SelectFacilityType(string facilityTypeId)
    {
        if (!facilityDefinitions.ContainsKey(facilityTypeId))
        {
            return false;
        }

        SelectedFacilityTypeId = facilityTypeId;
        return true;
    }

    public string PlaceFacility(string zoneId, int x, int y)
    {
        if (ZoneController == null || !facilityDefinitions.TryGetValue(SelectedFacilityTypeId, out var definition))
        {
            return string.Empty;
        }

        var placed = ZoneController.Layout.TryPlaceFacility(definition, zoneId, x, y, out var facility);
        if (!placed || facility == null)
        {
            return string.Empty;
        }

        EmitSignal(SignalName.FacilityPlaced, facility.Id, facility.FacilityTypeId, facility.ZoneId);
        return facility.Id;
    }

    public bool CanPlaceSelectedFacility(string zoneId, int x, int y)
    {
        if (ZoneController == null
            || !facilityDefinitions.TryGetValue(SelectedFacilityTypeId, out var definition))
        {
            return false;
        }

        return string.IsNullOrWhiteSpace(GetSelectedFacilityPlacementFailure(zoneId, x, y));
    }

    public string GetSelectedFacilityPlacementFailure(string zoneId, int x, int y)
    {
        if (ZoneController == null)
        {
            return "设施控制器未就绪。";
        }

        if (!facilityDefinitions.TryGetValue(SelectedFacilityTypeId, out var definition))
        {
            return "设施定义缺失。";
        }

        var zone = ZoneController.Layout.Zones.FirstOrDefault(item => item.Id == zoneId);
        if (zone == null || !definition.AllowedZoneTypeIds.Contains(zone.ZoneTypeId))
        {
            return "当前房间类型不匹配。";
        }

        var rect = new OfficeRect(x, y, definition.Width, definition.Height);
        var cells = rect.Cells().ToArray();
        if (cells.Length == 0 || cells.Any(cell => !ZoneContains(zone, cell)))
        {
            return "设施占地超出当前房间。";
        }

        if (cells.Any(FacilityOccupies))
        {
            return "格子已被其他设施占用。";
        }

        return string.Empty;
    }

    public bool UpgradeFacility(string facilityId)
    {
        if (ZoneController == null)
        {
            return false;
        }

        var facility = ZoneController.Layout.Facilities.Count == 0
            ? null
            : FindFacility(facilityId);
        if (facility == null)
        {
            return false;
        }

        if (!upgradeDefinitions.TryGetValue(facility.FacilityTypeId, out var upgrade))
        {
            return false;
        }

        var upgraded = ZoneController.Layout.TryUpgradeFacility(facilityId, upgrade);
        if (upgraded)
        {
            EmitSignal(SignalName.FacilityUpgraded, facilityId, upgrade.Level);
        }

        return upgraded;
    }

    public OfficeFacilityUpgradeDefinition? GetUpgradeDefinition(string facilityTypeId)
    {
        return upgradeDefinitions.TryGetValue(facilityTypeId, out var upgrade)
            ? upgrade
            : null;
    }

    public bool SellFacility(string facilityId)
    {
        if (ZoneController == null || string.IsNullOrWhiteSpace(facilityId))
        {
            return false;
        }

        var sold = ZoneController.Layout.RemoveFacility(facilityId);
        if (sold)
        {
            EmitSignal(SignalName.FacilitySold, facilityId);
        }

        return sold;
    }

    private OfficeFacility? FindFacility(string facilityId)
    {
        foreach (var facility in ZoneController!.Layout.Facilities)
        {
            if (facility.Id == facilityId)
            {
                return facility;
            }
        }

        return null;
    }

    private bool FacilityOccupies(OfficeCell cell)
    {
        return ZoneController?.Layout.Facilities.Any(
            facility => cell.X >= facility.X
                && cell.X < facility.X + facility.Width
                && cell.Y >= facility.Y
                && cell.Y < facility.Y + facility.Height) ?? false;
    }

    private static bool ZoneContains(OfficeZone zone, OfficeCell cell)
    {
        return cell.X >= zone.X
            && cell.X < zone.X + zone.Width
            && cell.Y >= zone.Y
            && cell.Y < zone.Y + zone.Height;
    }

    private void RegisterG1Definitions()
    {
        facilityDefinitions["basic_desk"] = new OfficeFacilityDefinition(
            "basic_desk",
            new[] { "product_zone", "sales_zone" },
            width: 1,
            height: 1,
            baseCost: 3000,
            monthlyCost: 200);
        facilityDefinitions["product_whiteboard"] = new OfficeFacilityDefinition(
            "product_whiteboard",
            new[] { "product_zone" },
            width: 2,
            height: 1,
            baseCost: 8000,
            monthlyCost: 300);
        facilityDefinitions["starter_server_rack"] = new OfficeFacilityDefinition(
            "starter_server_rack",
            new[] { "server_zone" },
            width: 1,
            height: 2,
            baseCost: 30000,
            monthlyCost: 3000);

        upgradeDefinitions["basic_desk"] = new OfficeFacilityUpgradeDefinition(
            "basic_desk_level_2",
            "basic_desk",
            level: 2,
            upgradeCost: 6000,
            monthlyCostDelta: 300);
        upgradeDefinitions["product_whiteboard"] = new OfficeFacilityUpgradeDefinition(
            "product_whiteboard_level_2",
            "product_whiteboard",
            level: 2,
            upgradeCost: 12000,
            monthlyCostDelta: 500);
        upgradeDefinitions["starter_server_rack"] = new OfficeFacilityUpgradeDefinition(
            "starter_server_rack_level_2",
            "starter_server_rack",
            level: 2,
            upgradeCost: 45000,
            monthlyCostDelta: 5000);
    }
}
