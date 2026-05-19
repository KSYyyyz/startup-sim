using Godot;
using StartupSim.Core.Office;
using CoreBusinessIntentSnapshot = StartupSim.Core.Contracts.BusinessIntentSnapshot;

namespace StartupSim.Godot;

[GlobalClass]
public partial class BusinessIntentSnapshot : Resource
{
    [Export] public float ProductFocus { get; set; }
    [Export] public float SalesFocus { get; set; }
    [Export] public float StabilityFocus { get; set; }
    [Export] public float OrganizationFocus { get; set; }
    [Export] public int MonthlyFixedCost { get; set; }
    [Export] public string Summary { get; set; } = string.Empty;

    public static BusinessIntentSnapshot FromOfficeCapacity(OfficeCapacitySnapshot capacity)
    {
        return new BusinessIntentSnapshot
        {
            ProductFocus = (float)capacity.ProductCapacity,
            SalesFocus = (float)capacity.SalesCapacity,
            StabilityFocus = (float)capacity.Stability,
            OrganizationFocus = (float)capacity.OrganizationEfficiency,
            MonthlyFixedCost = capacity.MonthlyFixedCost,
            Summary = capacity.HumanSummary
        };
    }

    public CoreBusinessIntentSnapshot ToCoreIntent()
    {
        return new CoreBusinessIntentSnapshot
        {
            ProductFocus = (decimal)ProductFocus,
            SalesFocus = (decimal)SalesFocus,
            StabilityFocus = (decimal)StabilityFocus,
            OrganizationFocus = (decimal)OrganizationFocus,
            MonthlyFixedCost = MonthlyFixedCost,
            SourceSummary = Summary
        };
    }
}
