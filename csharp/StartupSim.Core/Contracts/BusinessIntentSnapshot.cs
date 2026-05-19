namespace StartupSim.Core.Contracts
{
    public sealed class BusinessIntentSnapshot
    {
        public decimal ProductFocus { get; set; }
        public decimal SalesFocus { get; set; }
        public decimal StabilityFocus { get; set; }
        public decimal OrganizationFocus { get; set; }
        public int MonthlyFixedCost { get; set; }
        public string SourceSummary { get; set; } = string.Empty;
    }
}
