using System.Collections.Generic;
using Godot;
using StartupSim.Core.Office;

namespace StartupSim.Godot;

public partial class EmployeeManagementController : Node
{
    [Signal]
    public delegate void EmployeeHiredEventHandler(string employeeId, string name, string roleId);

    [Signal]
    public delegate void EmployeeAssignedEventHandler(string employeeId, string zoneId, int roleFitScore);

    private readonly Dictionary<string, EmployeeCandidate> candidates = new();

    [Export] public NodePath ZonePaintingControllerPath { get; set; } = new NodePath("");

    public ZonePaintingController? ZoneController { get; private set; }

    public override void _Ready()
    {
        RegisterG1Candidates();
        if (!ZonePaintingControllerPath.IsEmpty)
        {
            ZoneController = GetNodeOrNull<ZonePaintingController>(ZonePaintingControllerPath);
        }
    }

    public string HireCandidate(string candidateId)
    {
        if (ZoneController == null || !candidates.TryGetValue(candidateId, out var candidate))
        {
            return string.Empty;
        }

        var hired = ZoneController.Layout.TryHireEmployee(candidate, out var employee);
        if (!hired || employee == null)
        {
            return string.Empty;
        }

        EmitSignal(SignalName.EmployeeHired, employee.Id, employee.Name, employee.RoleId);
        return employee.Id;
    }

    public bool AssignEmployeeToZone(string employeeId, string zoneId)
    {
        if (ZoneController == null)
        {
            return false;
        }

        var assigned = ZoneController.Layout.AssignEmployeeToZone(employeeId, zoneId);
        if (!assigned)
        {
            return false;
        }

        var employee = FindEmployee(employeeId);
        EmitSignal(SignalName.EmployeeAssigned, employeeId, zoneId, employee?.RoleFitScore ?? 0);
        return true;
    }

    private OfficeEmployee? FindEmployee(string employeeId)
    {
        foreach (var employee in ZoneController!.Layout.Employees)
        {
            if (employee.Id == employeeId)
            {
                return employee;
            }
        }

        return null;
    }

    private void RegisterG1Candidates()
    {
        candidates["candidate_product_engineer"] = new EmployeeCandidate
        {
            Name = "林知远",
            RoleId = "product_engineer",
            Salary = 22000,
            TargetZoneTypeIds = new List<string> { "product_zone" },
            Skills = new Dictionary<string, int>
            {
                ["product_development"] = 72,
                ["collaboration"] = 58
            },
            PositiveTraits = new List<string> { "fast_learner" },
            NegativeTraits = new List<string> { "easily_tired" }
        };
        candidates["candidate_sales_specialist"] = new EmployeeCandidate
        {
            Name = "陈嘉禾",
            RoleId = "sales_specialist",
            Salary = 18000,
            TargetZoneTypeIds = new List<string> { "sales_zone" },
            Skills = new Dictionary<string, int>
            {
                ["sales_conversion"] = 68,
                ["collaboration"] = 62
            },
            PositiveTraits = new List<string> { "strong_communicator" },
            NegativeTraits = new List<string> { "moody" }
        };
        candidates["candidate_ops_engineer"] = new EmployeeCandidate
        {
            Name = "周承安",
            RoleId = "ops_engineer",
            Salary = 20000,
            TargetZoneTypeIds = new List<string> { "server_zone" },
            Skills = new Dictionary<string, int>
            {
                ["infrastructure_ops"] = 70,
                ["resilience"] = 66
            },
            PositiveTraits = new List<string> { "fast_learner" },
            NegativeTraits = new List<string> { "easily_tired" }
        };
    }
}
