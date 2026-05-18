namespace StartupSim.Core.Office
{
    public sealed class OfficeFacility
    {
        public string Id { get; set; } = string.Empty;
        public string FacilityTypeId { get; set; } = string.Empty;
        public string ZoneId { get; set; } = string.Empty;
        public int X { get; set; }
        public int Y { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }
        public int Level { get; set; } = 1;
        public int TotalCost { get; set; }
        public int MonthlyCost { get; set; }

        public OfficeRect ToRect()
        {
            return new OfficeRect(X, Y, Width, Height);
        }
    }
}
