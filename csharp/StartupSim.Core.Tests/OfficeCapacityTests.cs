using System.Collections.Generic;
using StartupSim.Core.Office;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class OfficeCapacityTests
{
    [Fact]
    public void CapacitySnapshotCombinesFacilitiesEmployeesAndNeeds()
    {
        var layout = BuildPlayableOffice(out var employee);
        layout.AdvanceEmployeeNeeds(hours: 4);

        var capacity = layout.BuildCapacitySnapshot();

        Assert.True(capacity.ProductCapacity > 0);
        Assert.True(capacity.OrganizationEfficiency > 0);
        Assert.Equal(1, capacity.EmployeeCount);
        Assert.Equal(22200, capacity.MonthlyFixedCost);
        Assert.Contains("研发区", capacity.HumanSummary);
        Assert.True(capacity.EmployeeEfficiency < 1.0m);
    }

    [Fact]
    public void TrainingPenaltyReducesEmployeeEfficiencyInCapacityPreview()
    {
        var layout = BuildPlayableOffice(out var employee);

        var before = layout.BuildCapacitySnapshot();
        layout.TrainEmployee(employee.Id, "product_development", 120, 8, 0.25m);
        var after = layout.BuildCapacitySnapshot();

        Assert.True(after.EmployeeEfficiency < before.EmployeeEfficiency);
        Assert.True(after.ProductCapacity >= before.ProductCapacity);
        Assert.Contains("培训", after.HumanSummary);
    }

    private static OfficeLayout BuildPlayableOffice(out OfficeEmployee employee)
    {
        var layout = new OfficeLayout(8, 6, 64, new[] { "product_zone" });
        layout.TryDefineZone("product_zone", "研发区", new OfficeRect(0, 0, 4, 3), out var zone);
        layout.TryPlaceFacility(
            new OfficeFacilityDefinition(
                "basic_desk",
                new[] { "product_zone" },
                width: 1,
                height: 1,
                baseCost: 3000,
                monthlyCost: 200),
            zone!.Id,
            0,
            0,
            out _);
        layout.TryHireEmployee(
            new EmployeeCandidate
            {
                Name = "林知远",
                RoleId = "product_engineer",
                Salary = 22000,
                TargetZoneTypeIds = new List<string> { "product_zone" },
                Skills = new Dictionary<string, int> { ["product_development"] = 80 },
                PositiveTraits = new List<string> { "fast_learner" },
                NegativeTraits = new List<string> { "easily_tired" }
            },
            out var hiredEmployee);
        employee = hiredEmployee!;
        layout.AssignEmployeeToZone(employee.Id, zone.Id);
        return layout;
    }
}
