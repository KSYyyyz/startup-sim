from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GODOT = ROOT / "godot" / "StartupSimGodot"
SCRIPTS = GODOT / "scripts"
SCENES = GODOT / "scenes"


def test_godot_migration_plan_exists_and_sets_godot_only_frontend_route():
    doc = ROOT / "docs" / "godot_migration_plan.md"

    assert doc.is_file()
    content = doc.read_text(encoding="utf-8")
    assert "Godot 4.6.x" in content
    assert "C# Core" in content
    assert "Unity 路线停止作为新增开发目标" in content
    assert "Web 前端路线已放弃" in content
    assert "俯视角办公室场景" in content
    assert "区域选择和区域框定" in content
    assert "设施摆放" in content
    assert "员工招聘" in content
    assert "暂停、正常速度、二倍速、三倍速" in content


def test_godot_project_scaffold_exists():
    required = [
        GODOT / "project.godot",
        GODOT / "StartupSimGodot.csproj",
        GODOT / "README.md",
        SCENES / "main.tscn",
        SCRIPTS / "StartupSimController.cs",
        SCRIPTS / "PreparedActionSnapshot.cs",
        SCRIPTS / "TurnResultSnapshot.cs",
        SCRIPTS / "GodotTurnBridge.cs",
        SCRIPTS / "OfficeRoomHotspot.cs",
    ]

    for path in required:
        assert path.is_file(), f"missing Godot file: {path.relative_to(ROOT)}"

    project = (GODOT / "project.godot").read_text(encoding="utf-8")
    assert 'config/name="Startup Sim Godot"' in project
    assert 'run/main_scene="res://scenes/main.tscn"' in project


def test_godot_project_references_portable_csharp_core():
    csproj = (GODOT / "StartupSimGodot.csproj").read_text(encoding="utf-8")
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert 'Sdk="Godot.NET.Sdk/4.6.2"' in csproj
    assert "<TargetFramework>net8.0</TargetFramework>" in csproj
    assert "..\\..\\csharp\\StartupSim.Core\\StartupSim.Core.csproj" in csproj
    assert "dotnet build godot/StartupSimGodot/StartupSimGodot.csproj --configuration Debug" in ci
    assert "godot/**/.godot/" in gitignore
    assert "godot/**/obj/" in gitignore


def test_godot_scripts_keep_rules_inside_bridge_only():
    for path in SCRIPTS.glob("*.cs"):
        content = path.read_text(encoding="utf-8")
        assert "namespace StartupSim.Godot" in content
        if path.name != "GodotTurnBridge.cs":
            assert "DeterministicTurnEngine" not in content
            assert "StartupSim.Core.Engines" not in content

    snapshot = (SCRIPTS / "PreparedActionSnapshot.cs").read_text(encoding="utf-8")
    assert "ActionType" in snapshot
    assert "Budget" in snapshot
    assert "FundraiseAmount" in snapshot
    assert "EquityOffered" in snapshot

    bridge = (SCRIPTS / "GodotTurnBridge.cs").read_text(encoding="utf-8")
    assert "StartupSim.Core.Contracts" in bridge
    assert "StartupSim.Core.Engines" in bridge
    assert "DeterministicTurnEngine" in bridge
    assert "ExecuteCommand" in bridge

    controller = (SCRIPTS / "StartupSimController.cs").read_text(encoding="utf-8")
    assert "GodotTurnBridge" in controller
    assert "TurnResultReceived" in controller
