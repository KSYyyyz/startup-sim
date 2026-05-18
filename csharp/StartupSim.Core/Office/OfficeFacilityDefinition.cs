using System.Collections.Generic;
using System.Linq;

namespace StartupSim.Core.Office
{
    public sealed class OfficeFacilityDefinition
    {
        public OfficeFacilityDefinition(
            string id,
            IEnumerable<string> allowedZoneTypeIds,
            int width,
            int height,
            int baseCost,
            int monthlyCost)
        {
            Id = id;
            AllowedZoneTypeIds = allowedZoneTypeIds.ToArray();
            Width = width;
            Height = height;
            BaseCost = baseCost;
            MonthlyCost = monthlyCost;
        }

        public string Id { get; }
        public IReadOnlyList<string> AllowedZoneTypeIds { get; }
        public int Width { get; }
        public int Height { get; }
        public int BaseCost { get; }
        public int MonthlyCost { get; }
    }
}
