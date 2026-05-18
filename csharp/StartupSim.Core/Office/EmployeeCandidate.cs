using System.Collections.Generic;

namespace StartupSim.Core.Office
{
    public sealed class EmployeeCandidate
    {
        public string Name { get; set; } = string.Empty;
        public string RoleId { get; set; } = string.Empty;
        public int Salary { get; set; }
        public List<string> TargetZoneTypeIds { get; set; } = new List<string>();
        public Dictionary<string, int> Skills { get; set; } = new Dictionary<string, int>();
        public List<string> PositiveTraits { get; set; } = new List<string>();
        public List<string> NegativeTraits { get; set; } = new List<string>();
    }
}
