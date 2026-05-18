namespace StartupSim.Core.Office
{
    public sealed class OfficeFacilityUpgradeDefinition
    {
        public OfficeFacilityUpgradeDefinition(
            string id,
            string facilityTypeId,
            int level,
            int upgradeCost,
            int monthlyCostDelta)
        {
            Id = id;
            FacilityTypeId = facilityTypeId;
            Level = level;
            UpgradeCost = upgradeCost;
            MonthlyCostDelta = monthlyCostDelta;
        }

        public string Id { get; }
        public string FacilityTypeId { get; }
        public int Level { get; }
        public int UpgradeCost { get; }
        public int MonthlyCostDelta { get; }
    }
}
