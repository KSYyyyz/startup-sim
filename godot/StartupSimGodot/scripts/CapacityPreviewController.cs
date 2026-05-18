using Godot;

namespace StartupSim.Godot;

public partial class CapacityPreviewController : Node
{
    [Signal]
    public delegate void CapacityPreviewChangedEventHandler(
        float productCapacity,
        float salesCapacity,
        float stability,
        int monthlyFixedCost,
        string humanSummary);

    [Export] public NodePath ZonePaintingControllerPath { get; set; } = new NodePath("");

    public ZonePaintingController? ZoneController { get; private set; }
    public string LastHumanSummary { get; private set; } = string.Empty;

    public override void _Ready()
    {
        if (!ZonePaintingControllerPath.IsEmpty)
        {
            ZoneController = GetNodeOrNull<ZonePaintingController>(ZonePaintingControllerPath);
        }
    }

    public string RefreshCapacityPreview()
    {
        if (ZoneController == null)
        {
            LastHumanSummary = string.Empty;
            return LastHumanSummary;
        }

        var snapshot = ZoneController.Layout.BuildCapacitySnapshot();
        LastHumanSummary = snapshot.HumanSummary;
        EmitSignal(
            SignalName.CapacityPreviewChanged,
            (float)snapshot.ProductCapacity,
            (float)snapshot.SalesCapacity,
            (float)snapshot.Stability,
            snapshot.MonthlyFixedCost,
            snapshot.HumanSummary);
        return LastHumanSummary;
    }
}
