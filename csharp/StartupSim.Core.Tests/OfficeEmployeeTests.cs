using System.Collections.Generic;
using StartupSim.Core.Office;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class OfficeEmployeeTests
{
    [Fact]
    public void HireEmployeeKeepsRoleSkillsTraitsAndSalary()
    {
        var layout = new OfficeLayout(8, 6, 64, new[] { "product_zone", "sales_zone" });
        var candidate = BuildProductEngineerCandidate();

        var hired = layout.TryHireEmployee(candidate, out var employee);

        Assert.True(hired);
        Assert.NotNull(employee);
        Assert.Equal("product_engineer", employee!.RoleId);
        Assert.Equal(22000, employee.Salary);
        Assert.Equal(72, employee.Skills["product_development"]);
        Assert.Contains("fast_learner", employee.PositiveTraits);
        Assert.Contains("easily_tired", employee.NegativeTraits);
    }

    [Fact]
    public void AssignEmployeeRequiresRoleMatchingZone()
    {
        var layout = new OfficeLayout(8, 6, 64, new[] { "product_zone", "sales_zone" });
        layout.TryDefineZone("product_zone", "研发区", new OfficeRect(0, 0, 4, 3), out var productZone);
        layout.TryDefineZone("sales_zone", "销售区", new OfficeRect(4, 0, 3, 3), out var salesZone);
        layout.TryHireEmployee(BuildProductEngineerCandidate(), out var employee);

        Assert.False(layout.AssignEmployeeToZone(employee!.Id, salesZone!.Id));
        Assert.True(layout.AssignEmployeeToZone(employee.Id, productZone!.Id));
        Assert.Equal(productZone.Id, employee.AssignedZoneId);
        Assert.Equal(100, employee.RoleFitScore);
    }

    [Fact]
    public void EmployeeSnapshotIsReadyForGodotManagementPanel()
    {
        var layout = new OfficeLayout(8, 6, 64, new[] { "product_zone" });
        layout.TryDefineZone("product_zone", "研发区", new OfficeRect(0, 0, 4, 3), out var productZone);
        layout.TryHireEmployee(BuildProductEngineerCandidate(), out var employee);
        layout.AssignEmployeeToZone(employee!.Id, productZone!.Id);

        var snapshot = layout.ToSnapshot();

        Assert.Single(snapshot.Employees);
        Assert.Equal(employee.Id, snapshot.Employees[0].Id);
        Assert.Equal("product_engineer", snapshot.Employees[0].RoleId);
        Assert.Equal(productZone.Id, snapshot.Employees[0].AssignedZoneId);
        Assert.Equal(100, snapshot.Employees[0].RoleFitScore);
    }

    private static EmployeeCandidate BuildProductEngineerCandidate()
    {
        return new EmployeeCandidate
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
    }
}
