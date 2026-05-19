using Godot;

namespace StartupSim.Godot;

public partial class TimeProgressController : Node
{
    private const float HoursPerMonth = 720f;
    private float accumulatedMonthHours;
    private float accumulatedNeedHours;

    [Signal]
    public delegate void TimeSpeedChangedEventHandler(float speedMultiplier);

    [Signal]
    public delegate void MonthReadyEventHandler(int monthIndex);

    [Signal]
    public delegate void MonthSettledEventHandler(TurnResultSnapshot snapshot);

    [Export] public NodePath TurnBridgePath { get; set; } = new NodePath("");
    [Export] public NodePath EmployeeManagementControllerPath { get; set; } = new NodePath("");
    [Export] public float SpeedMultiplier { get; set; } = 1f;
    [Export] public float GameHoursPerRealSecond { get; set; } = 24f;
    [Export] public int MonthIndex { get; set; } = 1;

    public GodotTurnBridge? TurnBridge { get; private set; }
    public EmployeeManagementController? EmployeeManagement { get; private set; }

    public override void _Ready()
    {
        if (!TurnBridgePath.IsEmpty)
        {
            TurnBridge = GetNodeOrNull<GodotTurnBridge>(TurnBridgePath);
        }

        if (!EmployeeManagementControllerPath.IsEmpty)
        {
            EmployeeManagement = GetNodeOrNull<EmployeeManagementController>(
                EmployeeManagementControllerPath);
        }
    }

    public override void _Process(double delta)
    {
        AdvanceGameHours((float)delta * GameHoursPerRealSecond);
    }

    public void SetPaused()
    {
        SetSpeed(0f);
    }

    public void SetNormalSpeed()
    {
        SetSpeed(1f);
    }

    public void SetDoubleSpeed()
    {
        SetSpeed(2f);
    }

    public void SetTripleSpeed()
    {
        SetSpeed(3f);
    }

    public void AdvanceGameHours(float realHours)
    {
        if (SpeedMultiplier <= 0f || realHours <= 0f)
        {
            return;
        }

        var gameHours = realHours * SpeedMultiplier;
        accumulatedNeedHours += gameHours;
        if (accumulatedNeedHours >= 1f)
        {
            var wholeHours = (int)accumulatedNeedHours;
            accumulatedNeedHours -= wholeHours;
            EmployeeManagement?.AdvanceEmployeeNeeds(wholeHours);
        }

        accumulatedMonthHours += gameHours;
        while (accumulatedMonthHours >= HoursPerMonth)
        {
            accumulatedMonthHours -= HoursPerMonth;
            EmitSignal(SignalName.MonthReady, MonthIndex);
        }
    }

    public TurnResultSnapshot? SubmitMonthSettlement(string command)
    {
        if (TurnBridge == null)
        {
            return null;
        }

        var result = TurnBridge.ExecuteCommand(command);
        MonthIndex = result.Month;
        EmitSignal(SignalName.MonthSettled, result);
        return result;
    }

    public TurnResultSnapshot? SubmitBusinessIntent(BusinessIntentSnapshot intent)
    {
        if (TurnBridge == null)
        {
            return null;
        }

        var result = TurnBridge.ExecuteBusinessIntent(intent);
        MonthIndex = result.Month;
        EmitSignal(SignalName.MonthSettled, result);
        return result;
    }

    private void SetSpeed(float speed)
    {
        SpeedMultiplier = speed;
        EmitSignal(SignalName.TimeSpeedChanged, SpeedMultiplier);
    }
}
