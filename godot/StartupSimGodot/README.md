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

The old Web/Vercel frontend route has been removed. New presentation work belongs in this Godot project.
