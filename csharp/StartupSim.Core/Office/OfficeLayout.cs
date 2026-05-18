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
        private readonly List<OfficeEmployee> employees = new List<OfficeEmployee>();
        private int nextZoneNumber = 1;
        private int nextFacilityNumber = 1;
        private int nextEmployeeNumber = 1;

        public OfficeLayout(int width, int height, int cellSize, IEnumerable<string> allowedZoneTypeIds)
        {
            Grid = new OfficeGrid(width, height, cellSize);
            this.allowedZoneTypeIds = new HashSet<string>(allowedZoneTypeIds);
        }

        public OfficeGrid Grid { get; }
        public IReadOnlyList<OfficeZone> Zones => zones;
        public IReadOnlyList<OfficeFacility> Facilities => facilities;
        public IReadOnlyList<OfficeEmployee> Employees => employees;

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

        public bool TryHireEmployee(EmployeeCandidate candidate, out OfficeEmployee? employee)
        {
            employee = null;
            if (string.IsNullOrWhiteSpace(candidate.Name)
                || string.IsNullOrWhiteSpace(candidate.RoleId)
                || candidate.Salary <= 0
                || candidate.TargetZoneTypeIds.Count == 0)
            {
                return false;
            }

            employee = new OfficeEmployee
            {
                Id = $"employee-{nextEmployeeNumber:000}",
                Name = candidate.Name,
                RoleId = candidate.RoleId,
                Salary = candidate.Salary,
                TargetZoneTypeIds = new List<string>(candidate.TargetZoneTypeIds),
                Skills = new Dictionary<string, int>(candidate.Skills),
                ExperienceBySkill = candidate.Skills.Keys.ToDictionary(skill => skill, _ => 0),
                PositiveTraits = new List<string>(candidate.PositiveTraits),
                NegativeTraits = new List<string>(candidate.NegativeTraits)
            };

            employees.Add(employee);
            nextEmployeeNumber++;
            return true;
        }

        public bool AssignEmployeeToZone(string employeeId, string zoneId)
        {
            var employee = employees.FirstOrDefault(item => item.Id == employeeId);
            var zone = zones.FirstOrDefault(item => item.Id == zoneId);
            if (employee == null || zone == null)
            {
                return false;
            }

            if (!employee.TargetZoneTypeIds.Contains(zone.ZoneTypeId))
            {
                return false;
            }

            employee.AssignedZoneId = zoneId;
            employee.RoleFitScore = 100;
            return true;
        }

        public void AdvanceEmployeeNeeds(int hours)
        {
            if (hours <= 0)
            {
                return;
            }

            foreach (var employee in employees.Where(item => !string.IsNullOrWhiteSpace(item.AssignedZoneId)))
            {
                employee.Fatigue = Clamp(employee.Fatigue + hours * 4, 0, 100);
                employee.RestNeed = Clamp(employee.RestNeed + hours * 3, 0, 100);
                employee.ToiletNeed = Clamp(employee.ToiletNeed + hours * 2, 0, 100);
                employee.EntertainmentNeed = Clamp(employee.EntertainmentNeed + hours, 0, 100);
                employee.Mood = Clamp(employee.Mood - hours, 0, 100);
                if (employee.Fatigue > 80)
                {
                    employee.Health = Clamp(employee.Health - 2, 0, 100);
                }

                if (employee.CurrentActivity != "培训中")
                {
                    employee.CurrentActivity = "工作";
                }
            }
        }

        public bool TrainEmployee(
            string employeeId,
            string skillId,
            int experienceGain,
            int fatigueDelta,
            decimal outputPenalty)
        {
            var employee = employees.FirstOrDefault(item => item.Id == employeeId);
            if (employee == null || string.IsNullOrWhiteSpace(skillId) || experienceGain <= 0)
            {
                return false;
            }

            if (!employee.ExperienceBySkill.ContainsKey(skillId))
            {
                employee.ExperienceBySkill[skillId] = 0;
            }

            employee.ExperienceBySkill[skillId] += experienceGain;
            employee.Level = CalculateLevel(employee.ExperienceBySkill.Values.DefaultIfEmpty(0).Max());
            employee.Fatigue = Clamp(employee.Fatigue + fatigueDelta, 0, 100);
            employee.OutputPenalty = outputPenalty;
            employee.CurrentActivity = "培训中";
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
                    .ToList(),
                Employees = employees
                    .Select(employee => new OfficeEmployeeSnapshot
                    {
                        Id = employee.Id,
                        Name = employee.Name,
                        RoleId = employee.RoleId,
                        Salary = employee.Salary,
                        AssignedZoneId = employee.AssignedZoneId,
                        RoleFitScore = employee.RoleFitScore,
                        Level = employee.Level,
                        ExperienceBySkill = new Dictionary<string, int>(employee.ExperienceBySkill),
                        Fatigue = employee.Fatigue,
                        RestNeed = employee.RestNeed,
                        ToiletNeed = employee.ToiletNeed,
                        EntertainmentNeed = employee.EntertainmentNeed,
                        Mood = employee.Mood,
                        Health = employee.Health,
                        CurrentActivity = employee.CurrentActivity,
                        OutputPenalty = employee.OutputPenalty,
                        PositiveTraits = new List<string>(employee.PositiveTraits),
                        NegativeTraits = new List<string>(employee.NegativeTraits),
                        Skills = new Dictionary<string, int>(employee.Skills)
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

        private static int CalculateLevel(int experience)
        {
            if (experience >= 260)
            {
                return 3;
            }

            return experience >= 100 ? 2 : 1;
        }

        private static int Clamp(int value, int min, int max)
        {
            if (value < min)
            {
                return min;
            }

            return value > max ? max : value;
        }
    }
}
