using System.Collections.Generic;

namespace StartupSim.Core.Office
{
    public sealed class OfficeLayoutSnapshot
    {
        public OfficeGridSnapshot Grid { get; set; } = new OfficeGridSnapshot();
        public List<OfficeZoneSnapshot> Zones { get; set; } = new List<OfficeZoneSnapshot>();
        public List<OfficeFacilitySnapshot> Facilities { get; set; } =
            new List<OfficeFacilitySnapshot>();
        public List<OfficeEmployeeSnapshot> Employees { get; set; } =
            new List<OfficeEmployeeSnapshot>();
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

    public sealed class OfficeFacilitySnapshot
    {
        public string Id { get; set; } = string.Empty;
        public string FacilityTypeId { get; set; } = string.Empty;
        public string ZoneId { get; set; } = string.Empty;
        public int X { get; set; }
        public int Y { get; set; }
        public int Width { get; set; }
        public int Height { get; set; }
        public int Level { get; set; }
        public int TotalCost { get; set; }
        public int MonthlyCost { get; set; }
    }

    public sealed class OfficeEmployeeSnapshot
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string RoleId { get; set; } = string.Empty;
        public int Salary { get; set; }
        public string AssignedZoneId { get; set; } = string.Empty;
        public int RoleFitScore { get; set; }
        public int Level { get; set; }
        public Dictionary<string, int> ExperienceBySkill { get; set; } = new Dictionary<string, int>();
        public int Fatigue { get; set; }
        public int RestNeed { get; set; }
        public int ToiletNeed { get; set; }
        public int EntertainmentNeed { get; set; }
        public int Mood { get; set; }
        public int Health { get; set; }
        public string CurrentActivity { get; set; } = string.Empty;
        public decimal OutputPenalty { get; set; }
        public List<string> PositiveTraits { get; set; } = new List<string>();
        public List<string> NegativeTraits { get; set; } = new List<string>();
        public Dictionary<string, int> Skills { get; set; } = new Dictionary<string, int>();
    }
}
