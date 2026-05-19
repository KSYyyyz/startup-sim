using Godot;

namespace StartupSim.Godot;

public partial class BusinessIntentController : Node
{
    [Signal]
    public delegate void BusinessIntentChangedEventHandler(string summary);

    [Export] public NodePath CapacityPreviewControllerPath { get; set; } = new NodePath("");

    public CapacityPreviewController? CapacityPreviewController { get; private set; }
    public BusinessIntentSnapshot LastIntent { get; private set; } = new();

    public override void _Ready()
    {
        if (!CapacityPreviewControllerPath.IsEmpty)
        {
            CapacityPreviewController =
                GetNodeOrNull<CapacityPreviewController>(CapacityPreviewControllerPath);
        }
    }

    public BusinessIntentSnapshot BuildCurrentIntent()
    {
        var zoneController = CapacityPreviewController?.ZoneController;
        if (zoneController == null)
        {
            LastIntent = new BusinessIntentSnapshot
            {
                Summary = "办公室产能尚未形成经营意图。"
            };
            return LastIntent;
        }

        var capacity = zoneController.Layout.BuildCapacitySnapshot();
        LastIntent = BusinessIntentSnapshot.FromOfficeCapacity(capacity);
        EmitSignal(SignalName.BusinessIntentChanged, LastIntent.Summary);
        return LastIntent;
    }
}
