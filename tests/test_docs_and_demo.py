"""Documentation and demo script verification tests for Alpha 1.7.

Validates that all new Alpha 1.7 documentation files exist and
the start_demo.py script is runnable.
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
]

README_NAV_KEYWORDS = [
    "QUICKSTART.md",
    "examples/sample_run_balanced.md",
    "docs/troubleshooting.md",
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

        assert "Alpha 1.7" in out, f"Expected version in output, got: {out[:200]}"
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

    def test_readme_title_contains_alpha_1_7(self):
        readme = (PROJECT_DIR / "README.md").read_text(encoding="utf-8")
        assert "Alpha 1.7" in readme, "README title should contain Alpha 1.7"


class TestVersion:
    def test_version_is_1_7(self):
        version = (PROJECT_DIR / "VERSION").read_text(encoding="utf-8").strip()
        assert version == "1.7", f"VERSION should be '1.7', got '{version}'"
