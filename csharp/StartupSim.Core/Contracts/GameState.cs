using System.Collections.Generic;

namespace StartupSim.Core.Contracts
{
    public sealed class GameState
    {
        public string CompanyName { get; set; } = "NimbusAI";
        public string Status { get; set; } = "active";
        public GameMetrics Metrics { get; set; } = new GameMetrics();
        public IList<string> BoardMessages { get; set; } = new List<string>();
        public IList<string> CompetitorSignals { get; set; } = new List<string>();

        public GameState Clone()
        {
            return new GameState
            {
                CompanyName = CompanyName,
                Status = Status,
                Metrics = Metrics.Clone(),
                BoardMessages = new List<string>(BoardMessages),
                CompetitorSignals = new List<string>(CompetitorSignals)
            };
        }
    }
}
