namespace StartupSim.Core.Contracts
{
    public sealed class TurnCommand
    {
        public string RawText { get; set; } = string.Empty;
        public string Source { get; set; } = "player";
    }
}
