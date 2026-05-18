using System.Collections.Generic;

namespace StartupSim.Core.Contracts
{
    public sealed class ActionPlan
    {
        public string RawInput { get; set; } = string.Empty;
        public IList<PlayerAction> Actions { get; set; } = new List<PlayerAction>();
    }
}
