using System.Collections.Generic;

namespace StartupSim.Core.Contracts
{
    public sealed class TurnResult
    {
        public GameState State { get; set; } = new GameState();
        public IList<string> ReplayBasis { get; set; } = new List<string>();
        public IList<string> ChangedMetrics { get; set; } = new List<string>();
        public string NextPressure { get; set; } = string.Empty;
        public string Authority { get; set; } = "csharp-startup-sim-core";
    }
}
