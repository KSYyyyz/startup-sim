import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GODOT = ROOT / "godot" / "StartupSimGodot"
DATA = GODOT / "data"


def test_godot_content_data_files_exist():
    required = [
        DATA / "zones" / "zone_types.json",
        DATA / "facilities" / "basic_facilities.json",
        DATA / "facilities" / "facility_upgrades.json",
        DATA / "employees" / "employee_roles.json",
        DATA / "employees" / "employee_traits.json",
        DATA / "employees" / "employee_skills.json",
        DATA / "employees" / "employee_growth_tracks.json",
        DATA / "employees" / "employee_training_actions.json",
    ]

    for path in required:
        assert path.is_file(), f"missing Godot content data file: {path.relative_to(ROOT)}"


def test_godot_content_data_has_first_g1_playable_definitions():
    zone_types = json.loads((DATA / "zones" / "zone_types.json").read_text(encoding="utf-8"))
    facilities = json.loads(
        (DATA / "facilities" / "basic_facilities.json").read_text(encoding="utf-8")
    )
    roles = json.loads((DATA / "employees" / "employee_roles.json").read_text(encoding="utf-8"))
    training = json.loads(
        (DATA / "employees" / "employee_training_actions.json").read_text(encoding="utf-8")
    )

    assert {item["id"] for item in zone_types["items"]} >= {
        "product_zone",
        "sales_zone",
        "server_zone",
    }
    assert {item["id"] for item in facilities["items"]} >= {
        "basic_desk",
        "product_whiteboard",
        "starter_server_rack",
    }
    assert {item["id"] for item in roles["items"]} >= {
        "product_engineer",
        "sales_specialist",
        "ops_engineer",
    }
    assert training["items"], "G1 needs at least one training action"


def test_godot_content_validator_accepts_seed_data():
    result = subprocess.run(
        [sys.executable, "scripts/validate_godot_content.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Godot 内容数据检查通过" in result.stdout


def test_godot_content_database_script_exists_for_future_scene_loading():
    script = GODOT / "scripts" / "ContentDatabase.cs"

    assert script.is_file()
    content = script.read_text(encoding="utf-8")
    assert "LoadAll" in content
    assert 'JsonPropertyName("display_name")' in content
    assert "zone_types.json" in content
    assert "employee_training_actions.json" in content


def test_ci_runs_godot_content_validator():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "Godot content data check" in ci
    assert "python scripts/validate_godot_content.py" in ci
