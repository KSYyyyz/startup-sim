import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "design-assets" / "manifest.json"
GODOT_ART_PACK = ROOT / "godot" / "StartupSimGodot" / "assets" / "art" / "godot-g1-art-pack-v0.1"
GODOT_EMPLOYEE_MOTION_PACK = (
    ROOT / "godot" / "StartupSimGodot" / "assets" / "art" / "godot-g1-art-pack-v0.2-employee-motion"
)


def test_design_asset_manifest_uses_image_2_policy():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["policy"]["required_generation_model"] == "image-2"
    assert manifest["assets"], "design asset manifest should register Godot visual assets"


def test_registered_design_assets_have_existing_files_and_prompts():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    for asset in manifest["assets"]:
        assert asset["generation_model"] == "image-2"
        assert (ROOT / asset["source_prompt_path"]).is_file()
        assert (ROOT / asset["library_path"]).is_file()
        assert (ROOT / asset["godot_path"]).is_file()
        assert asset["used_by"], f"{asset['id']} should declare Godot usage"
        for used_by in asset["used_by"]:
            usage_file = ROOT / used_by
            assert usage_file.is_file(), f"{asset['id']} references missing usage file {used_by}"


def test_godot_art_pack_is_tracked_and_import_ready():
    index_path = GODOT_ART_PACK / "asset-index.json"
    import_notes_path = GODOT_ART_PACK / "GODOT_IMPORT_NOTES.md"

    assert index_path.is_file()
    assert import_notes_path.is_file()

    index = json.loads(index_path.read_text(encoding="utf-8"))
    import_notes = import_notes_path.read_text(encoding="utf-8")

    assert "tracked in this repository" in index["storage_policy"]
    assert "outside the project repository" not in import_notes
    assert "Do not store generated digital assets" not in import_notes

    required_core_asset_ids = {
        "office-tile-atlas-v0.1",
        "zone-state-overlay-atlas-v0.1",
        "facility-upgrade-atlas-v0.1",
        "employee-sprite-atlas-v0.1",
        "employee-direction-variants-v0.1",
        "status-icon-atlas-v0.1",
        "employee-animation-minimal-v0.1",
        "ui-core-atlas-v0.1",
        "feedback-fx-atlas-v0.1",
        "recruitment-portrait-sheet-v0.1",
        "recruitment-portrait-sheet-v0.2-angle-balanced",
    }
    actual_asset_ids = {asset["id"] for asset in index["assets"]}
    exported_asset_ids = {path.stem for path in (GODOT_ART_PACK / "exports").glob("*.png")}
    assert required_core_asset_ids <= actual_asset_ids
    assert exported_asset_ids == actual_asset_ids

    for asset in index["assets"]:
        export_path = GODOT_ART_PACK / asset["file"]
        import_path = export_path.with_name(f"{export_path.name}.import")
        source_path = GODOT_ART_PACK / asset["source"]
        prompt_path = GODOT_ART_PACK / asset["prompt"]
        slice_guide_path = GODOT_ART_PACK / "slice-guides" / f"{asset['id']}.md"

        assert export_path.is_file(), f"missing export for {asset['id']}"
        assert import_path.is_file(), f"missing Godot import metadata for {asset['id']}"
        assert source_path.is_file(), f"missing source for {asset['id']}"
        assert prompt_path.is_file(), f"missing prompt for {asset['id']}"
        assert slice_guide_path.is_file(), f"missing slice guide for {asset['id']}"
        assert asset["godot_use"], f"{asset['id']} should declare Godot import use"

        width, height = read_png_size(export_path)
        assert width == asset["image"]["width"]
        assert height == asset["image"]["height"]


def test_godot_employee_motion_pack_is_tracked_and_import_ready():
    index_path = GODOT_EMPLOYEE_MOTION_PACK / "asset-index.json"
    import_notes_path = GODOT_EMPLOYEE_MOTION_PACK / "GODOT_IMPORT_NOTES.md"
    spec_path = GODOT_EMPLOYEE_MOTION_PACK / "ART_PACK_SPEC.md"

    assert index_path.is_file()
    assert import_notes_path.is_file()
    assert spec_path.is_file()

    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert index["pack_id"] == "startup-sim-godot-g1-art-pack-v0.2-employee-motion"
    assert "backup only" in index["storage_policy"]

    assets = index["assets"]
    assert [asset["id"] for asset in assets] == ["employee-motion-atlas-v0.2"]

    asset = assets[0]
    export_path = GODOT_EMPLOYEE_MOTION_PACK / asset["file"]
    import_path = export_path.with_name(f"{export_path.name}.import")
    source_path = GODOT_EMPLOYEE_MOTION_PACK / asset["source"]
    raw_source_path = GODOT_EMPLOYEE_MOTION_PACK / asset["raw_source"]
    prompt_path = GODOT_EMPLOYEE_MOTION_PACK / asset["prompt"]
    slice_guide_path = GODOT_EMPLOYEE_MOTION_PACK / asset["slice_guide"]
    preview_path = GODOT_EMPLOYEE_MOTION_PACK / asset["preview"]

    assert export_path.is_file()
    assert import_path.is_file()
    assert source_path.is_file()
    assert raw_source_path.is_file()
    assert prompt_path.is_file()
    assert slice_guide_path.is_file()
    assert preview_path.is_file()
    assert asset["grid"] == {"columns": 12, "rows": 6}
    assert asset["slice"] == {
        "cell_width_px": 192,
        "cell_height_px": 192,
        "godot_region_hint": "12 columns x 6 rows; use 192 x 192 regions from the full atlas",
    }
    assert len(asset["row_labels"]) == 6
    assert len(asset["column_labels"]) == 12
    assert "right_walk_b_placeholder" in asset["column_labels"]

    width, height = read_png_size(export_path)
    assert width == 2304
    assert height == 1152


def read_png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    assert header[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name} is not a PNG"
    return struct.unpack(">II", header[16:24])
