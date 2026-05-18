from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "csharp" / "StartupSim.Core"
CORE_TESTS = ROOT / "csharp" / "StartupSim.Core.Tests"


def test_csharp_core_migration_doc_exists_and_points_to_godot():
    doc = ROOT / "docs" / "csharp_core_migration_plan.md"

    assert doc.is_file()
    content = doc.read_text(encoding="utf-8")
    assert "StartupSim.Core" in content
    assert "Godot" in content
    assert "黄金样例" in content
    assert "Web 前端" not in content or "规则验证" in content


def test_csharp_core_scaffold_is_engine_independent():
    required = [
        CORE / "StartupSim.Core.csproj",
        CORE / "Contracts" / "GameMetrics.cs",
        CORE / "Contracts" / "GameState.cs",
        CORE / "Contracts" / "ActionPlan.cs",
        CORE / "Contracts" / "ActionType.cs",
        CORE / "Contracts" / "PlayerAction.cs",
        CORE / "Contracts" / "RiskLevel.cs",
        CORE / "Contracts" / "TurnCommand.cs",
        CORE / "Contracts" / "TurnResult.cs",
        CORE / "Contracts" / "ScenarioDefinition.cs",
        CORE / "Engines" / "ITurnEngine.cs",
        CORE / "Engines" / "DeterministicTurnEngine.cs",
        CORE / "Parsing" / "ActionParser.cs",
    ]

    for path in required:
        assert path.is_file(), f"missing C# core file: {path.relative_to(ROOT)}"

    csproj = (CORE / "StartupSim.Core.csproj").read_text(encoding="utf-8")
    assert "<TargetFramework>netstandard2.1</TargetFramework>" in csproj

    for path in CORE.rglob("*.cs"):
        content = path.read_text(encoding="utf-8")
        assert "UnityEngine" not in content, f"Core must stay Unity-independent: {path}"
        assert "Godot" not in content, f"Core must stay Godot-independent: {path}"


def test_csharp_core_has_compile_gate_and_ci_coverage():
    test_project = CORE_TESTS / "StartupSim.Core.Tests.csproj"
    ci = ROOT / ".github" / "workflows" / "ci.yml"
    gitignore = ROOT / ".gitignore"

    assert test_project.is_file()
    test_content = test_project.read_text(encoding="utf-8")
    assert "<TargetFramework>net8.0</TargetFramework>" in test_content
    assert (
        '<ProjectReference Include="..\\StartupSim.Core\\StartupSim.Core.csproj" />' in test_content
    )
    assert (CORE_TESTS / "DeterministicTurnEngineTests.cs").is_file()
    assert (CORE_TESTS / "ActionParserTests.cs").is_file()
    assert (CORE_TESTS / "GoldenCaseTests.cs").is_file()

    ci_content = ci.read_text(encoding="utf-8")
    assert "actions/setup-dotnet@v4" in ci_content
    assert (
        "dotnet test csharp/StartupSim.Core.Tests/StartupSim.Core.Tests.csproj "
        "--configuration Release"
    ) in ci_content
    assert (
        "dotnet build godot/StartupSimGodot/StartupSimGodot.csproj --configuration Debug"
        in ci_content
    )

    ignored = gitignore.read_text(encoding="utf-8")
    assert "csharp/**/bin/" in ignored
    assert "csharp/**/obj/" in ignored


def test_golden_case_seed_exists_for_csharp_port():
    turn_golden = ROOT / "csharp" / "golden-cases" / "month01_product_investment.json"
    parser_golden = ROOT / "csharp" / "golden-cases" / "action_parser_multi.json"

    assert turn_golden.is_file()
    content = turn_golden.read_text(encoding="utf-8")
    assert '"command": "花10万研发产品"' in content
    assert '"authority": "python-turn-engine-reference"' in content

    assert parser_golden.is_file()
    parser_content = parser_golden.read_text(encoding="utf-8")
    assert '"authority": "python-action-parser-reference"' in parser_content
    assert '"command": "融资500万出让10%，花20万研发产品，花10万做营销推广"' in parser_content

    turn_minimal = ROOT / "csharp" / "golden-cases" / "turn_engine_minimal.json"
    assert turn_minimal.is_file()
    turn_content = turn_minimal.read_text(encoding="utf-8")
    assert '"authority": "csharp-portable-turn-slice"' in turn_content
    assert '"name": "fundraising_plus_product_and_marketing"' in turn_content
