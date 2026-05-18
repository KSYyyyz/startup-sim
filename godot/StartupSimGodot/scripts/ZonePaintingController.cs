using System;
using System.Linq;
using Godot;
using StartupSim.Core.Office;

namespace StartupSim.Godot;

public partial class ZonePaintingController : Node
{
    [Signal]
    public delegate void ZoneCreatedEventHandler(string zoneId, string zoneTypeId, string displayName);

    [Signal]
    public delegate void ZoneChangedEventHandler(string zoneId, string displayName);

    [Signal]
    public delegate void ZoneRemovedEventHandler(string zoneId);

    private static readonly string[] AllowedZoneTypeIds =
    {
        "product_zone",
        "sales_zone",
        "server_zone"
    };

    private readonly OfficeLayout layout = new(12, 8, 64, AllowedZoneTypeIds);
    private OfficeCell? selectionStart;

    [Export] public NodePath GridViewPath { get; set; } = new NodePath("");
    [Export] public string SelectedZoneTypeId { get; set; } = "product_zone";

    public OfficeLayout Layout => layout;
    public OfficeGridView? GridView { get; private set; }

    public override void _Ready()
    {
        if (!GridViewPath.IsEmpty)
        {
            GridView = GetNodeOrNull<OfficeGridView>(GridViewPath);
        }
    }

    public bool SelectZoneType(string zoneTypeId)
    {
        if (!AllowedZoneTypeIds.Contains(zoneTypeId))
        {
            return false;
        }

        SelectedZoneTypeId = zoneTypeId;
        return true;
    }

    public void BeginSelection(int x, int y)
    {
        selectionStart = new OfficeCell(x, y);
    }

    public string CommitSelection(int x, int y, string displayName = "")
    {
        if (selectionStart == null)
        {
            return string.Empty;
        }

        var rect = BuildRect(selectionStart.Value, new OfficeCell(x, y));
        var name = string.IsNullOrWhiteSpace(displayName)
            ? DefaultZoneDisplayName(SelectedZoneTypeId)
            : displayName;

        selectionStart = null;
        if (!layout.TryDefineZone(SelectedZoneTypeId, name, rect, out var zone) || zone == null)
        {
            return string.Empty;
        }

        GridView?.TryOccupyRect(zone.X, zone.Y, zone.Width, zone.Height, zone.Id);
        GridView?.RegisterZoneVisual(zone.Id, zone.ZoneTypeId);
        EmitSignal(SignalName.ZoneCreated, zone.Id, zone.ZoneTypeId, zone.DisplayName);
        return zone.Id;
    }

    public bool RenameZone(string zoneId, string displayName)
    {
        var renamed = layout.RenameZone(zoneId, displayName);
        if (renamed)
        {
            EmitSignal(SignalName.ZoneChanged, zoneId, displayName);
        }

        return renamed;
    }

    public bool RemoveZone(string zoneId)
    {
        var zone = layout.Zones.FirstOrDefault(item => item.Id == zoneId);
        if (zone == null)
        {
            return false;
        }

        var removed = layout.RemoveZone(zoneId);
        if (!removed)
        {
            return false;
        }

        GridView?.ReleaseRect(zone.X, zone.Y, zone.Width, zone.Height);
        GridView?.ClearZoneVisual(zoneId);
        EmitSignal(SignalName.ZoneRemoved, zoneId);
        return true;
    }

    private static OfficeRect BuildRect(OfficeCell start, OfficeCell end)
    {
        var x = Math.Min(start.X, end.X);
        var y = Math.Min(start.Y, end.Y);
        var width = Math.Abs(start.X - end.X) + 1;
        var height = Math.Abs(start.Y - end.Y) + 1;
        return new OfficeRect(x, y, width, height);
    }

    private static string DefaultZoneDisplayName(string zoneTypeId)
    {
        return zoneTypeId switch
        {
            "product_zone" => "研发区",
            "sales_zone" => "销售区",
            "server_zone" => "服务器区",
            _ => "办公区"
        };
    }
}
