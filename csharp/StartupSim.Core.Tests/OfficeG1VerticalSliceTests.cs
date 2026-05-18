using System.Collections.Generic;
using StartupSim.Core.Office;
using Xunit;

namespace StartupSim.Core.Tests;

public sealed class OfficeG1VerticalSliceTests
{
    [Fact]
    public void G1OfficeLoopConnectsZonesFacilitiesEmployeesNeedsAndCapacity()
    {
        var layout = new OfficeLayout(
            width: 12,
            height: 8,
            cellSize: 64,
            allowedZoneTypeIds: new[] { "product_zone", "sales_zone", "server_zone" });

        Assert.True(
            layout.TryDefineZone(
                "product_zone",
                "研发区",
                new OfficeRect(0, 0, 4, 3),
                out var productZone));
        Assert.True(
            layout.TryDefineZone(
                "sales_zone",
                "销售区",
                new OfficeRect(4, 0, 4, 3),
                out var salesZone));
        Assert.True(
            layout.TryDefineZone(
                "server_zone",
                "服务器区",
                new OfficeRect(8, 0, 3, 3),
                out var serverZone));

        Assert.True(
            layout.TryPlaceFacility(
                new OfficeFacilityDefinition(
                    "basic_desk",
                    new[] { "product_zone", "sales_zone" },
                    width: 1,
                    height: 1,
                    baseCost: 3000,
                    monthlyCost: 200),
                productZone!.Id,
                0,
                0,
                out var desk));
        Assert.True(
            layout.TryPlaceFacility(
                new OfficeFacilityDefinition(
                    "product_whiteboard",
                    new[] { "product_zone" },
                    width: 1,
                    height: 1,
                    baseCost: 5000,
                    monthlyCost: 300),
                productZone.Id,
                1,
                0,
                out var whiteboard));
        Assert.True(
            layout.TryPlaceFacility(
                new OfficeFacilityDefinition(
                    "starter_server_rack",
                    new[] { "server_zone" },
                    width: 1,
                    height: 2,
                    baseCost: 12000,
                    monthlyCost: 1200),
                serverZone!.Id,
                8,
                0,
                out var serverRack));
        Assert.True(
            layout.TryUpgradeFacility(
                whiteboard!.Id,
                new OfficeFacilityUpgradeDefinition(
                    "whiteboard_level_2",
                    "product_whiteboard",
                    level: 2,
                    upgradeCost: 6000,
                    monthlyCostDelta: 200)));

        var productEmployee = HireAndAssign(
            layout,
            "林知远",
            "product_engineer",
            productZone.Id,
            "product_zone",
            "product_development",
            82);
        HireAndAssign(
            layout,
            "陈向南",
            "sales_specialist",
            salesZone!.Id,
            "sales_zone",
            "sales_conversion",
            76);
        HireAndAssign(
            layout,
            "赵云岚",
            "ops_engineer",
            serverZone.Id,
            "server_zone",
            "infrastructure_ops",
            70);

        Assert.True(layout.TrainEmployee(productEmployee.Id, "product_development", 120, 8, 0.2m));
        layout.AdvanceEmployeeNeeds(hours: 3);

        var snapshot = layout.ToSnapshot();
        var capacity = layout.BuildCapacitySnapshot();

        Assert.Equal(3, snapshot.Zones.Count);
        Assert.Equal(3, snapshot.Facilities.Count);
        Assert.Equal(3, snapshot.Employees.Count);
        Assert.Equal(2, whiteboard.Level);
        Assert.Contains(snapshot.Employees, item => item.CurrentActivity == "培训中");
        Assert.All(snapshot.Employees, item => Assert.True(item.Fatigue > 0));
        Assert.True(capacity.ProductCapacity > 0);
        Assert.True(capacity.SalesCapacity > 0);
        Assert.True(capacity.Stability > 0);
        Assert.True(capacity.MonthlyFixedCost > 0);
        Assert.Contains("研发区", capacity.HumanSummary);
    }

    private static OfficeEmployee HireAndAssign(
        OfficeLayout layout,
        string name,
        string roleId,
        string zoneId,
        string zoneTypeId,
        string skillId,
        int skillValue)
    {
        Assert.True(
            layout.TryHireEmployee(
                new EmployeeCandidate
                {
                    Name = name,
                    RoleId = roleId,
                    Salary = 18000,
                    TargetZoneTypeIds = new List<string> { zoneTypeId },
                    Skills = new Dictionary<string, int> { [skillId] = skillValue },
                    PositiveTraits = new List<string> { "学习快" },
                    NegativeTraits = new List<string> { "容易疲劳" }
                },
                out var employee));
        Assert.True(layout.AssignEmployeeToZone(employee!.Id, zoneId));
        return employee;
    }
}
