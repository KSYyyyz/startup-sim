using System.Collections.Generic;

namespace StartupSim.Core.Contracts
{
    public sealed class ScenarioDefinition
    {
        public string Id { get; set; } = "ai-saas-seed";
        public string Title { get; set; } = "AI SaaS 初创公司";
        public IList<string> Rooms { get; set; } = new List<string>
        {
            "product",
            "team",
            "sales",
            "board",
            "servers"
        };
        public GameState InitialState { get; set; } = new GameState();
    }
}
