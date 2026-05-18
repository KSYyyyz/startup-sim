using System.Collections.Generic;
using System.Linq;

namespace StartupSim.Core.Office
{
    public sealed class OfficeLayout
    {
        private readonly HashSet<string> allowedZoneTypeIds;
        private readonly List<OfficeZone> zones = new List<OfficeZone>();
        private readonly Dictionary<OfficeCell, string> facilityOccupants =
            new Dictionary<OfficeCell, string>();
        private readonly List<OfficeFacility> facilities = new List<OfficeFacility>();
        private int nextZoneNumber = 1;
        private int nextFacilityNumber = 1;

        public OfficeLayout(int width, int height, int cellSize, IEnumerable<string> allowedZoneTypeIds)
        {
            Grid = new OfficeGrid(width, height, cellSize);
            this.allowedZoneTypeIds = new HashSet<string>(allowedZoneTypeIds);
        }

        public OfficeGrid Grid { get; }
        public IReadOnlyList<OfficeZone> Zones => zones;
        public IReadOnlyList<OfficeFacility> Facilities => facilities;

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

            if (facilities.Any(item => item.ZoneId == zoneId))
            {
                return false;
            }

            Grid.Release(zone.ToRect());
            zones.Remove(zone);
            return true;
        }

        public bool TryPlaceFacility(
            OfficeFacilityDefinition definition,
            string zoneId,
            int x,
            int y,
            out OfficeFacility? facility)
        {
            facility = null;
            var zone = zones.FirstOrDefault(item => item.Id == zoneId);
            if (zone == null || !definition.AllowedZoneTypeIds.Contains(zone.ZoneTypeId))
            {
                return false;
            }

            var rect = new OfficeRect(x, y, definition.Width, definition.Height);
            var cells = rect.Cells().ToArray();
            if (cells.Length == 0
                || cells.Any(cell => !ZoneContains(zone, cell) || facilityOccupants.ContainsKey(cell)))
            {
                return false;
            }

            var facilityId = $"facility-{nextFacilityNumber:000}";
            facility = new OfficeFacility
            {
                Id = facilityId,
                FacilityTypeId = definition.Id,
                ZoneId = zoneId,
                X = x,
                Y = y,
                Width = definition.Width,
                Height = definition.Height,
                Level = 1,
                TotalCost = definition.BaseCost,
                MonthlyCost = definition.MonthlyCost
            };

            foreach (var cell in cells)
            {
                facilityOccupants[cell] = facilityId;
            }

            facilities.Add(facility);
            nextFacilityNumber++;
            return true;
        }

        public bool TryUpgradeFacility(
            string facilityId,
            OfficeFacilityUpgradeDefinition upgradeDefinition)
        {
            var facility = facilities.FirstOrDefault(item => item.Id == facilityId);
            if (facility == null || facility.FacilityTypeId != upgradeDefinition.FacilityTypeId)
            {
                return false;
            }

            if (upgradeDefinition.Level <= facility.Level)
            {
                return false;
            }

            facility.Level = upgradeDefinition.Level;
            facility.TotalCost += upgradeDefinition.UpgradeCost;
            facility.MonthlyCost += upgradeDefinition.MonthlyCostDelta;
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
                    .ToList(),
                Facilities = facilities
                    .Select(facility => new OfficeFacilitySnapshot
                    {
                        Id = facility.Id,
                        FacilityTypeId = facility.FacilityTypeId,
                        ZoneId = facility.ZoneId,
                        X = facility.X,
                        Y = facility.Y,
                        Width = facility.Width,
                        Height = facility.Height,
                        Level = facility.Level,
                        TotalCost = facility.TotalCost,
                        MonthlyCost = facility.MonthlyCost
                    })
                    .ToList()
            };
        }

        private static bool ZoneContains(OfficeZone zone, OfficeCell cell)
        {
            return cell.X >= zone.X
                && cell.X < zone.X + zone.Width
                && cell.Y >= zone.Y
                && cell.Y < zone.Y + zone.Height;
        }
    }
}
