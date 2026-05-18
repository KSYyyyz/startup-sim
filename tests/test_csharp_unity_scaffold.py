from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "csharp" / "StartupSim.Core"
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
        CORE / "Contracts" / "TurnCommand.cs",
        CORE / "Contracts" / "TurnResult.cs",
        CORE / "Contracts" / "ScenarioDefinition.cs",
        CORE / "Engines" / "ITurnEngine.cs",
        CORE / "Engines" / "DeterministicTurnEngine.cs",
    ]

    for path in required:
        assert path.is_file(), f"missing C# core file: {path.relative_to(ROOT)}"

    csproj = (CORE / "StartupSim.Core.csproj").read_text(encoding="utf-8")
    assert "<TargetFramework>netstandard2.1</TargetFramework>" in csproj

    for path in CORE.rglob("*.cs"):
        content = path.read_text(encoding="utf-8")
        assert "UnityEngine" not in content, f"Core must stay Unity-independent: {path}"


def test_unity_component_scaffold_is_adapter_only():
    required = [
        UNITY / "OfficeRoomHotspot.cs",
        UNITY / "PreparedActionPresenter.cs",
        UNITY / "TurnExecutorPresenter.cs",
        UNITY / "StartupSimUnityApiClient.cs",
        UNITY / "README.md",
    ]

    for path in required:
        assert path.is_file(), f"missing Unity component file: {path.relative_to(ROOT)}"

    for path in required:
        content = path.read_text(encoding="utf-8")
        assert "TurnEngine" not in content or "does not settle" in content


def test_golden_case_seed_exists_for_csharp_port():
    golden = ROOT / "csharp" / "golden-cases" / "month01_product_investment.json"

    assert golden.is_file()
    content = golden.read_text(encoding="utf-8")
    assert '"command": "花10万研发产品"' in content
    assert '"authority": "python-turn-engine-reference"' in content
