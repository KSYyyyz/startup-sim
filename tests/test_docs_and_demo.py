"""Documentation and demo script verification tests for Alpha 1.9.

Validates that all new Alpha 1.9 documentation files exist,
start_demo.py is runnable, and QUICKSTART.md contains correct content.
"""

import io
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent

DOC_FILES = [
    "QUICKSTART.md",
    "examples/sample_run_balanced.md",
    "examples/sample_run_marketing_failure.md",
    "docs/playtest_feedback_template.md",
    "docs/troubleshooting.md",
    "docs/playtest_observation.md",
    "docs/reference_game_analysis.md",
]

README_NAV_KEYWORDS = [
    "QUICKSTART.md",
    "examples/sample_run_balanced.md",
    "docs/troubleshooting.md",
    "docs/reference_game_analysis.md",
    "docs/godot_migration_plan.md",
    "docs/csharp_core_migration_plan.md",
    "docs/project_layout.md",
]


class TestDocFilesExist:
    @pytest.mark.parametrize("rel_path", DOC_FILES)
    def test_doc_file_exists(self, rel_path: str):
        path = PROJECT_DIR / rel_path
        assert path.exists(), f"Missing: {rel_path}"

    def test_start_demo_exists(self):
        path = PROJECT_DIR / "scripts" / "start_demo.py"
        assert path.exists(), "Missing: scripts/start_demo.py"


class TestStartDemo:
    def test_start_demo_runs(self):
        """Import start_demo and call main(); captures output."""
        sys.path.insert(0, str(PROJECT_DIR))
        from scripts import start_demo

        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            start_demo.main()
            out = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
            sys.path.remove(str(PROJECT_DIR))

        assert "Alpha 1.9" in out, f"Expected version in output, got: {out[:200]}"
        assert "cd " in out or str(PROJECT_DIR) in out, "Expected project dir in output"
        assert "python app.py new" in out, "Expected launch command in output"

    def test_start_demo_importable(self):
        sys.path.insert(0, str(PROJECT_DIR))
        try:
            from scripts import start_demo

            assert hasattr(start_demo, "main"), "start_demo must have main()"
            assert callable(start_demo.main)
        finally:
            sys.path.remove(str(PROJECT_DIR))


class TestReadme:
    def test_readme_contains_quick_nav(self):
        readme = (PROJECT_DIR / "README.md").read_text(encoding="utf-8")
        for kw in README_NAV_KEYWORDS:
            assert kw in readme, f"README missing quick nav reference: {kw}"

    def test_readme_title_contains_alpha_1_9(self):
        readme = (PROJECT_DIR / "README.md").read_text(encoding="utf-8")
        assert "Alpha 1.9" in readme, "README title should contain Alpha 1.9"

    def test_readme_uses_named_investor_language(self):
        readme = (PROJECT_DIR / "README.md").read_text(encoding="utf-8")
        assert "投资方董事" not in readme, "README should use named investor representative wording"


class TestDocsConsistencyScript:
    def test_check_headers_are_well_formed(self):
        script = (PROJECT_DIR / "scripts" / "check_docs_consistency.py").read_text(encoding="utf-8")
        assert 'safe_print("\\n[检查 1:' not in script
        assert "[检查 1]" in script


class TestGodotGameplayDocs:
    def test_employee_growth_system_is_documented_as_company_lever(self):
        plan = (PROJECT_DIR / "docs" / "startup_sim_development_plan.md").read_text(encoding="utf-8")
        direction = (PROJECT_DIR / "docs" / "indie_game_product_direction.md").read_text(encoding="utf-8")
        contracts = (PROJECT_DIR / "docs" / "gameplay_contracts.md").read_text(encoding="utf-8")

        assert "员工成长系统" in plan
        assert "岗位经验、定向培训、项目突破和导师带教" in direction
        assert "EmployeeGrowthState" in contracts
        assert "成长系统必须服务于公司经营结果" in contracts


class TestQuickstart:
    @pytest.fixture(autouse=True)
    def _read_quickstart(self):
        self.content = (PROJECT_DIR / "QUICKSTART.md").read_text(encoding="utf-8")

    def test_contains_correct_path(self):
        assert (
            "D:\\Startup-sim" in self.content or "D:/Startup-sim" in self.content
        ), "QUICKSTART.md must contain the correct project path"

    def test_no_space_in_startup(self):
        assert "D:\\S tartup" not in self.content, "Path must not have space in 'Startup'"
        assert "D:/S tartup" not in self.content, "Path must not have space in 'Startup'"

    def test_no_space_before_sim(self):
        assert "D:\\Startup sim" not in self.content, "Path must not have space before 'sim'"
        assert "D:/Startup sim" not in self.content, "Path must not have space before 'sim'"

    def test_contains_three_routes(self):
        assert "融资300万出让8%" in self.content, "QUICKSTART must have 稳健 route"
        assert "融资500万出让10%" in self.content, "QUICKSTART must have 均衡 route"
        assert "控制支出" in self.content, "QUICKSTART must have 保守 route"

    def test_no_old_recommendations(self):
        assert (
            "花20万研发产品，花10万做营销" not in self.content
        ), "QUICKSTART must not contain old recommendation"


class TestVersion:
    def test_version_is_1_9_1(self):
        version = (PROJECT_DIR / "VERSION").read_text(encoding="utf-8").strip()
        assert version == "1.9.1", f"VERSION should be '1.9.1', got '{version}'"
