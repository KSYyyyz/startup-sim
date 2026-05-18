namespace StartupSim.Core.Office
{
    public sealed class OfficeCapacitySnapshot
    {
        public decimal ProductCapacity { get; set; }
        public decimal SalesCapacity { get; set; }
        public decimal Stability { get; set; }
        public decimal OrganizationEfficiency { get; set; }
        public decimal EmployeeEfficiency { get; set; } = 1m;
        public int EmployeeCount { get; set; }
        public int MonthlyFixedCost { get; set; }
        public string HumanSummary { get; set; } = string.Empty;
    }
}
