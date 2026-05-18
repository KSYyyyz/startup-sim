from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "csharp" / "StartupSim.Core"
CORE_TESTS = ROOT / "csharp" / "StartupSim.Core.Tests"
UNITY = ROOT / "unity" / "StartupSimUnity" / "Assets" / "Scripts" / "StartupSim"


def test_csharp_core_and_unity_migration_docs_exist():
    doc = ROOT / "docs" / "csharp_unity_migration_plan.md"

    assert doc.is_file()
    content = doc.read_text(encoding="utf-8")
    assert "StartupSim.Core" in content
    assert "UnityEngine" in content
    assert "黄金测试" in content
    assert "Web 前端降级为规则验证台" in content


def test_csharp_core_scaffold_is_unity_independent():
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

    ignored = gitignore.read_text(encoding="utf-8")
    assert "csharp/**/bin/" in ignored
    assert "csharp/**/obj/" in ignored


def test_unity_component_scaffold_is_adapter_only():
    required = [
        UNITY / "OfficeRoomHotspot.cs",
        UNITY / "PreparedActionPresenter.cs",
        UNITY / "PreparedActionSnapshot.cs",
        UNITY / "TurnExecutorPresenter.cs",
        UNITY / "StartupSimUnityApiClient.cs",
        UNITY / "README.md",
    ]

    for path in required:
        assert path.is_file(), f"missing Unity component file: {path.relative_to(ROOT)}"

    for path in required:
        content = path.read_text(encoding="utf-8")
        assert "TurnEngine" not in content or "does not settle" in content

    snapshot = (UNITY / "PreparedActionSnapshot.cs").read_text(encoding="utf-8")
    assert "ActionType" in snapshot
    assert "Budget" in snapshot
    assert "FundraiseAmount" in snapshot
    assert "EquityOffered" in snapshot


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
