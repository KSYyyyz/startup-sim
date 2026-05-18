namespace StartupSim.Core.Office
{
    public sealed class OfficeZone
    {
        public string Id { get; set; } = string.Empty;
        public string ZoneTypeId { get; set; } = string.Empty;
        public string DisplayName { get; set; } = string.Empty;
        public int X { get; set; }
        public int Y { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }

        public OfficeRect ToRect()
        {
            return new OfficeRect(X, Y, Width, Height);
        }
    }
}
