using StartupSim.Core.Contracts;

namespace StartupSim.Core.Engines
{
    public interface ITurnEngine
    {
        TurnResult Execute(GameState currentState, TurnCommand command);
    }
}
