# Startup Sim Godot

This is the Godot desktop presentation layer for Startup Sim.

Target editor: Godot 4.6.x .NET.

Current scope:

- Bootable `main.tscn` shell.
- Presentation-only C# scripts.
- Structured prepared action snapshots.
- `GodotTurnBridge` calls the portable C# core; Godot scripts do not duplicate settlement rules.

Rule authority remains in `../../csharp/StartupSim.Core/`.

Build check from repository root:

```powershell
$env:PATH = "D:\Startup-sim\.work\dotnet;$env:PATH"
dotnet build godot\StartupSimGodot\StartupSimGodot.csproj
```

The existing Web frontend remains a rule validation bench and remote demo surface.
