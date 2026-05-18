using System.Collections.Generic;

namespace StartupSim.Core.Office
{
    public sealed class OfficeLayoutSnapshot
    {
        public OfficeGridSnapshot Grid { get; set; } = new OfficeGridSnapshot();
        public List<OfficeZoneSnapshot> Zones { get; set; } = new List<OfficeZoneSnapshot>();
    }

    public sealed class OfficeZoneSnapshot
    {
        public string Id { get; set; } = string.Empty;
        public string ZoneTypeId { get; set; } = string.Empty;
        public string DisplayName { get; set; } = string.Empty;
        public int X { get; set; }
        public int Y { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }
    }
}
