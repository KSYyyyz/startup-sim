using Godot;

namespace StartupSim.Godot;

[GlobalClass]
public partial class PreparedActionSnapshot : Resource
{
    [Export] public string RoomName { get; set; } = string.Empty;
    [Export] public string Command { get; set; } = string.Empty;
    [Export] public string ActionType { get; set; } = string.Empty;
    [Export] public int Budget { get; set; }
    [Export] public int FundraiseAmount { get; set; }
    [Export] public float EquityOffered { get; set; }
}
