using Godot;
using StartupSim.Core.Contracts;
using StartupSim.Core.Engines;

namespace StartupSim.Godot;

public partial class GodotTurnBridge : Node
{
    private readonly ITurnEngine turnEngine = new DeterministicTurnEngine();

    public GameState CurrentState { get; private set; } = new();

    public void ResetGame()
    {
        CurrentState = new GameState();
    }

    public TurnResultSnapshot ExecuteCommand(string command)
    {
        var result = turnEngine.Execute(CurrentState, new TurnCommand
        {
            RawText = command ?? string.Empty,
            Source = "godot"
        });
        CurrentState = result.State;
        return TurnResultSnapshot.FromTurnResult(result);
    }

    public TurnResultSnapshot ExecutePreparedAction(PreparedActionSnapshot snapshot)
    {
        return ExecuteCommand(snapshot?.Command ?? string.Empty);
    }
}
