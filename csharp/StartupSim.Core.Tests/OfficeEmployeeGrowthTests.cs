using System.Collections.Generic;
using StartupSim.Core.Office;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class OfficeEmployeeGrowthTests
{
    [Fact]
    public void SimulateEmployeeNeedsChangesFatigueMoodHealthAndActivity()
    {
        var layout = BuildLayoutWithAssignedEngineer(out var employee);

        layout.AdvanceEmployeeNeeds(hours: 6);

        Assert.True(employee.Fatigue > 0);
        Assert.True(employee.RestNeed > 0);
        Assert.True(employee.ToiletNeed > 0);
        Assert.True(employee.Mood < 80);
        Assert.Equal("工作", employee.CurrentActivity);
    }

    [Fact]
    public void TrainingAddsExperienceAndCanLevelUpWithShortTermPenalty()
    {
        var layout = BuildLayoutWithAssignedEngineer(out var employee);

        var trained = layout.TrainEmployee(
            employee.Id,
            skillId: "product_development",
            experienceGain: 120,
            fatigueDelta: 8,
            outputPenalty: 0.25m);

        Assert.True(trained);
        Assert.Equal(2, employee.Level);
        Assert.Equal(120, employee.ExperienceBySkill["product_development"]);
        Assert.Equal("培训中", employee.CurrentActivity);
        Assert.Equal(8, employee.Fatigue);
        Assert.Equal(0.25m, employee.OutputPenalty);
    }

    [Fact]
    public void GrowthAndNeedsAppearInSnapshot()
    {
        var layout = BuildLayoutWithAssignedEngineer(out var employee);
        layout.TrainEmployee(employee.Id, "product_development", 120, 8, 0.25m);
        layout.AdvanceEmployeeNeeds(hours: 2);

        var snapshot = layout.ToSnapshot();

        Assert.Equal(2, snapshot.Employees[0].Level);
        Assert.Equal("培训中", snapshot.Employees[0].CurrentActivity);
        Assert.True(snapshot.Employees[0].Fatigue > 0);
        Assert.Equal(120, snapshot.Employees[0].ExperienceBySkill["product_development"]);
    }

    private static OfficeLayout BuildLayoutWithAssignedEngineer(out OfficeEmployee employee)
    {
        var layout = new OfficeLayout(8, 6, 64, new[] { "product_zone" });
        layout.TryDefineZone("product_zone", "研发区", new OfficeRect(0, 0, 4, 3), out var zone);
        layout.TryHireEmployee(
            new EmployeeCandidate
            {
                Name = "林知远",
                RoleId = "product_engineer",
                Salary = 22000,
                TargetZoneTypeIds = new List<string> { "product_zone" },
                Skills = new Dictionary<string, int> { ["product_development"] = 72 },
                PositiveTraits = new List<string> { "fast_learner" },
                NegativeTraits = new List<string> { "easily_tired" }
            },
            out var hiredEmployee);
        employee = hiredEmployee!;
        layout.AssignEmployeeToZone(employee.Id, zone!.Id);
        return layout;
    }
}
