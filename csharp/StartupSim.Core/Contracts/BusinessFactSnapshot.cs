namespace StartupSim.Core.Contracts
{
    public sealed class BusinessFactSnapshot
    {
        public string FactType { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Severity { get; set; } = "info";
    }
}
