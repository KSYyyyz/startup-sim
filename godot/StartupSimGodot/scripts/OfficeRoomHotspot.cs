using Godot;

namespace StartupSim.Godot;

public partial class OfficeRoomHotspot : Area2D
{
    [Signal]
    public delegate void ActionPreparedEventHandler(PreparedActionSnapshot snapshot);

    [Export] public string RoomName { get; set; } = string.Empty;
    [Export] public string Command { get; set; } = string.Empty;
    [Export] public string ActionType { get; set; } = string.Empty;
    [Export] public int Budget { get; set; }
    [Export] public int FundraiseAmount { get; set; }
    [Export] public float EquityOffered { get; set; }

    public override void _InputEvent(Viewport viewport, InputEvent @event, int shapeIdx)
    {
        if (@event is InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Left })
        {
            EmitSignal(SignalName.ActionPrepared, BuildSnapshot());
        }
    }

    public PreparedActionSnapshot BuildSnapshot()
    {
        return new PreparedActionSnapshot
        {
            RoomName = RoomName,
            Command = Command,
            ActionType = ActionType,
            Budget = Budget,
            FundraiseAmount = FundraiseAmount,
            EquityOffered = EquityOffered
        };
    }
}
