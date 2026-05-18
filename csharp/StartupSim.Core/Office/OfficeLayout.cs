using System.Collections.Generic;
using System.Linq;

namespace StartupSim.Core.Office
{
    public sealed class OfficeLayout
    {
        private readonly HashSet<string> allowedZoneTypeIds;
        private readonly List<OfficeZone> zones = new List<OfficeZone>();
        private int nextZoneNumber = 1;

        public OfficeLayout(int width, int height, int cellSize, IEnumerable<string> allowedZoneTypeIds)
        {
            Grid = new OfficeGrid(width, height, cellSize);
            this.allowedZoneTypeIds = new HashSet<string>(allowedZoneTypeIds);
        }

        public OfficeGrid Grid { get; }
        public IReadOnlyList<OfficeZone> Zones => zones;

        public bool TryDefineZone(
            string zoneTypeId,
            string displayName,
            OfficeRect rect,
            out OfficeZone? zone)
        {
            zone = null;
            if (!allowedZoneTypeIds.Contains(zoneTypeId) || string.IsNullOrWhiteSpace(displayName))
            {
                return false;
            }

            var zoneId = $"zone-{nextZoneNumber:000}";
            if (!Grid.TryOccupy(rect, zoneId))
            {
                return false;
            }

            zone = new OfficeZone
            {
                Id = zoneId,
                ZoneTypeId = zoneTypeId,
                DisplayName = displayName,
                X = rect.X,
                Y = rect.Y,
                Width = rect.Width,
                Height = rect.Height
            };
            zones.Add(zone);
            nextZoneNumber++;
            return true;
        }

        public bool RenameZone(string zoneId, string displayName)
        {
            if (string.IsNullOrWhiteSpace(displayName))
            {
                return false;
            }

            var zone = zones.FirstOrDefault(item => item.Id == zoneId);
            if (zone == null)
            {
                return false;
            }

            zone.DisplayName = displayName;
            return true;
        }

        public bool RemoveZone(string zoneId)
        {
            var zone = zones.FirstOrDefault(item => item.Id == zoneId);
            if (zone == null)
            {
                return false;
            }

            Grid.Release(zone.ToRect());
            zones.Remove(zone);
            return true;
        }

        public OfficeLayoutSnapshot ToSnapshot()
        {
            return new OfficeLayoutSnapshot
            {
                Grid = Grid.ToSnapshot(),
                Zones = zones
                    .Select(zone => new OfficeZoneSnapshot
                    {
                        Id = zone.Id,
                        ZoneTypeId = zone.ZoneTypeId,
                        DisplayName = zone.DisplayName,
                        X = zone.X,
                        Y = zone.Y,
                        Width = zone.Width,
                        Height = zone.Height
                    })
                    .ToList()
            };
        }
    }
}
