namespace StartupSim.Core.Contracts
{
    public sealed class PlayerAction
    {
        public ActionType Type { get; set; }
        public string Intent { get; set; } = string.Empty;
        public decimal Budget { get; set; }
        public RiskLevel RiskLevel { get; set; } = RiskLevel.Medium;
        public decimal FundraiseAmount { get; set; }
        public decimal EquityOffered { get; set; }
        public decimal PostMoneyValuation { get; set; }
    }
}
