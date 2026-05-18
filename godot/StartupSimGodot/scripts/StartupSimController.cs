using Godot;

namespace StartupSim.Godot;

public partial class StartupSimController : Node
{
    [Signal]
    public delegate void PreparedActionChangedEventHandler(string command);

    [Signal]
    public delegate void PreparedActionSubmittedEventHandler(string command);

    [Export] public string ApiBaseUrl { get; set; } = "http://127.0.0.1:8000";

    public PreparedActionSnapshot CurrentPreparedAction { get; private set; } = new();

    public override void _Ready()
    {
        GD.Print("Startup Sim Godot presentation layer ready.");
    }

    public void PrepareAction(PreparedActionSnapshot snapshot)
    {
        CurrentPreparedAction = snapshot ?? new PreparedActionSnapshot();
        EmitSignal(SignalName.PreparedActionChanged, CurrentPreparedAction.Command);
    }

    public void ClearPreparedAction()
    {
        CurrentPreparedAction = new PreparedActionSnapshot();
        EmitSignal(SignalName.PreparedActionChanged, string.Empty);
    }

    public void SubmitPreparedAction()
    {
        if (string.IsNullOrWhiteSpace(CurrentPreparedAction.Command))
        {
            return;
        }

        EmitSignal(SignalName.PreparedActionSubmitted, CurrentPreparedAction.Command);
        GD.Print($"Startup Sim submit prepared command via {ApiBaseUrl}: {CurrentPreparedAction.Command}");
    }
}
