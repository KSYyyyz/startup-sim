using System.Collections.Generic;

namespace StartupSim.Core.Office
{
    public sealed class OfficeEmployee
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string RoleId { get; set; } = string.Empty;
        public int Salary { get; set; }
        public List<string> TargetZoneTypeIds { get; set; } = new List<string>();
        public Dictionary<string, int> Skills { get; set; } = new Dictionary<string, int>();
        public List<string> PositiveTraits { get; set; } = new List<string>();
        public List<string> NegativeTraits { get; set; } = new List<string>();
        public string AssignedZoneId { get; set; } = string.Empty;
        public int RoleFitScore { get; set; }
        public int Level { get; set; } = 1;
        public Dictionary<string, int> ExperienceBySkill { get; set; } =
            new Dictionary<string, int>();
        public int Fatigue { get; set; }
        public int RestNeed { get; set; }
        public int ToiletNeed { get; set; }
        public int EntertainmentNeed { get; set; }
        public int Mood { get; set; } = 80;
        public int Health { get; set; } = 100;
        public decimal OutputPenalty { get; set; }
        public string CurrentActivity { get; set; } = "待命";
    }
}
