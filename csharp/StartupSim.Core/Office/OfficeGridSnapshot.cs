using System.Collections.Generic;

namespace StartupSim.Core.Office
{
    public sealed class OfficeGridSnapshot
    {
        public int Width { get; set; }
        public int Height { get; set; }
        public int CellSize { get; set; }
        public List<OccupiedOfficeCell> OccupiedCells { get; set; } = new List<OccupiedOfficeCell>();
    }

    public sealed class OccupiedOfficeCell
    {
        public int X { get; set; }
        public int Y { get; set; }
        public string OccupantId { get; set; } = string.Empty;
    }
}
