import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "design-assets" / "manifest.json"
GODOT_ART_ROOT = ROOT / "godot" / "StartupSimGodot" / "assets" / "art"
GODOT_ART_PACK = GODOT_ART_ROOT / "godot-g1-art-pack-v0.1"
GODOT_EMPLOYEE_MOTION_PACK = GODOT_ART_ROOT / "godot-g1-art-pack-v0.2-employee-motion"


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


def test_godot_followup_art_packs_are_tracked_and_import_ready():
    expected_packs = [
        (
            "godot-g1-art-pack-v0.3-facility-placements",
            "facility-placement-atlas-v0.3",
            {"columns": 6, "rows": 3},
            {"cell_width_px": 256, "cell_height_px": 342},
            (1536, 1026),
        ),
        (
            "godot-g1-art-pack-v0.4-office-tiles",
            "office-tile-expansion-atlas-v0.4",
            {"columns": 8, "rows": 5},
            {"cell_width_px": 200, "cell_height_px": 200},
            (1600, 1000),
        ),
        (
            "godot-g1-art-pack-v0.5-employee-status-icons",
            "employee-status-icon-atlas-v0.5",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 224, "cell_height_px": 224},
            (1792, 896),
        ),
        (
            "godot-g1-art-pack-v0.6-zone-state-overlays",
            "zone-state-overlay-atlas-v0.6",
            {"columns": 6, "rows": 5},
            {"cell_width_px": 230, "cell_height_px": 230},
            (1380, 1150),
        ),
        (
            "godot-g1-art-pack-v0.7-feedback-portraits",
            "feedback-portrait-sheet-v0.7",
            {"columns": 4, "rows": 3},
            {"cell_width_px": 384, "cell_height_px": 384},
            (1536, 1152),
        ),
        (
            "godot-g1-art-pack-v0.8-business-feedback-fx",
            "business-feedback-fx-atlas-v0.8",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 224, "cell_height_px": 224},
            (1792, 896),
            32,
            (224, 224),
        ),
        (
            "godot-g1-art-pack-v0.9-facility-state-variants",
            "facility-state-variant-atlas-v0.9",
            {"columns": 8, "rows": 3},
            {"cell_width_px": 224, "cell_height_px": 224},
            (1792, 672),
            24,
            (224, 224),
        ),
        (
            "godot-g1-art-pack-v1.0-employee-activity-states",
            "employee-activity-state-atlas-v1.0",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 192, "cell_height_px": 192},
            (1536, 768),
            32,
            (192, 192),
        ),
        (
            "godot-g1-art-pack-v1.1-pseudo3d-office-foundation",
            "pseudo3d-office-foundation-atlas-v1.1",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 222, "cell_height_px": 222},
            (1776, 888),
            32,
            (222, 222),
        ),
        (
            "godot-g1-art-pack-v1.1b-pseudo3d-office-structure",
            "pseudo3d-office-structure-atlas-v1.1b",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 222, "cell_height_px": 222},
            (1776, 888),
            32,
            (222, 222),
        ),
        (
            "godot-g1-art-pack-v1.2-zone-carpets-build-markers",
            "zone-carpet-build-marker-atlas-v1.2",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 222, "cell_height_px": 222},
            (1776, 888),
            32,
            (222, 222),
        ),
        (
            "godot-g1-art-pack-v1.3-large-facility-sprites",
            "large-facility-sprite-atlas-v1.3",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 222, "cell_height_px": 222},
            (1776, 888),
            32,
            (222, 222),
        ),
        (
            "godot-g1-art-pack-v1.4-employee-pseudo3d-motion",
            "employee-pseudo3d-motion-atlas-v1.4",
            {"columns": 12, "rows": 4},
            {"cell_width_px": 192, "cell_height_px": 224},
            (2304, 896),
            48,
            (192, 224),
        ),
        (
            "godot-g1-art-pack-v1.5-hud-kpi-ui-chrome",
            "hud-kpi-ui-chrome-atlas-v1.5",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 224, "cell_height_px": 224},
            (1792, 896),
            32,
            (224, 224),
        ),
        (
            "godot-g1-art-pack-v1.6-business-event-feedback-bubbles",
            "business-event-feedback-bubble-atlas-v1.6",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 224, "cell_height_px": 224},
            (1792, 896),
            32,
            (224, 224),
        ),
        (
            "godot-g1-art-pack-v1.7-facility-upgrade-tiers",
            "facility-upgrade-tier-atlas-v1.7",
            {"columns": 8, "rows": 6},
            {"cell_width_px": 224, "cell_height_px": 224},
            (1792, 1344),
            48,
            (224, 224),
        ),
        (
            "godot-g1-art-pack-v1.8-build-upgrade-feedback-fx",
            "build-upgrade-feedback-fx-atlas-v1.8",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 224, "cell_height_px": 224},
            (1792, 896),
            32,
            (224, 224),
        ),
        (
            "godot-g1-art-pack-v1.9-management-panel-detail-ui",
            "management-panel-detail-ui-atlas-v1.9",
            {"columns": 8, "rows": 4},
            {"cell_width_px": 224, "cell_height_px": 224},
            (1792, 896),
            32,
            (224, 224),
        ),
        (
            "godot-g1-art-pack-v2.0-office-expansion-themes",
            "office-expansion-theme-atlas-v2.0",
            {"columns": 8, "rows": 5},
            {"cell_width_px": 224, "cell_height_px": 224},
            (1792, 1120),
            40,
            (224, 224),
        ),
        (
            "godot-g1-art-pack-v2.1-employee-role-extensions",
            "employee-role-extension-atlas-v2.1",
            {"columns": 8, "rows": 8},
            {"cell_width_px": 192, "cell_height_px": 224},
            (1536, 1792),
            64,
            (192, 224),
        ),
    ]

    for pack_item in expected_packs:
        pack_name, asset_id, grid, slice_size, image_size, *icon_expectation = pack_item
        pack = GODOT_ART_ROOT / pack_name
        index_path = pack / "asset-index.json"
        assert index_path.is_file(), f"missing index for {pack_name}"
        assert (pack / "ART_PACK_SPEC.md").is_file()
        assert (pack / "GODOT_IMPORT_NOTES.md").is_file()

        index = json.loads(index_path.read_text(encoding="utf-8"))
        assert index["pack_id"] == f"startup-sim-{pack_name}"
        assert "backup only" in index["storage_policy"]

        assert [asset["id"] for asset in index["assets"]] == [asset_id]
        asset = index["assets"][0]
        export_path = pack / asset["file"]
        import_path = export_path.with_name(f"{export_path.name}.import")
        source_path = pack / asset["source"]
        raw_source_path = pack / asset["raw_source"]
        prompt_path = pack / asset["prompt"]
        slice_guide_path = pack / asset["slice_guide"]
        preview_path = pack / asset["preview"]

        assert export_path.is_file(), f"missing export for {asset_id}"
        assert import_path.is_file(), f"missing Godot import metadata for {asset_id}"
        assert source_path.is_file(), f"missing source for {asset_id}"
        assert raw_source_path.is_file(), f"missing raw source for {asset_id}"
        assert prompt_path.is_file(), f"missing prompt for {asset_id}"
        assert slice_guide_path.is_file(), f"missing slice guide for {asset_id}"
        assert preview_path.is_file(), f"missing preview for {asset_id}"
        assert asset["grid"] == grid
        assert asset["slice"] == slice_size

        width, height = read_png_size(export_path)
        assert (width, height) == image_size

        if icon_expectation:
            expected_icon_count, expected_icon_size = icon_expectation
            icon_dir = pack / asset["sliced_icons_dir"]
            icon_paths = sorted(icon_dir.glob("*.png"))
            assert len(icon_paths) == asset["sliced_icon_count"] == expected_icon_count
            assert asset["preview"].endswith("-transparent-contact-sheet.png")
            assert all(read_png_size(path) == expected_icon_size for path in icon_paths)

        if (
            pack_name.startswith("godot-g1-art-pack-v1.1")
            or pack_name.startswith("godot-g1-art-pack-v1.2")
            or pack_name.startswith("godot-g1-art-pack-v1.3")
            or pack_name.startswith("godot-g1-art-pack-v1.4")
            or pack_name.startswith("godot-g1-art-pack-v1.5")
            or pack_name.startswith("godot-g1-art-pack-v1.6")
            or pack_name.startswith("godot-g1-art-pack-v1.7")
            or pack_name.startswith("godot-g1-art-pack-v1.8")
            or pack_name.startswith("godot-g1-art-pack-v1.9")
            or pack_name.startswith("godot-g1-art-pack-v2.0")
            or pack_name.startswith("godot-g1-art-pack-v2.1")
        ):
            assert (ROOT / "docs" / "art_asset_metadata_standard.md").is_file()
            assert "texture_metadata_schema" in asset
            textures = asset["textures"]
            assert len(textures) == asset["sliced_icon_count"] == expected_icon_count
            required_texture_fields = {
                "id",
                "semantic_name",
                "zh_name",
                "category",
                "file",
                "atlas",
                "atlas_region",
                "grid_position",
                "intended_layer",
                "anchor",
                "footprint_cells",
                "visual_size_cells",
                "usage",
                "state_tags",
                "godot_hint",
            }
            for texture in textures:
                assert required_texture_fields <= set(texture), texture["id"]
                assert (pack / texture["file"]).is_file()
                assert texture["atlas"] == asset["file"]
                assert texture["anchor"] in {"center", "bottom_center", "feet_center"}
                assert texture["intended_layer"].endswith("Layer")
                assert texture["zh_name"]
                assert "???" not in texture["zh_name"]
                assert texture["usage"]
                assert "???" not in texture["usage"]
                assert texture["state_tags"]
                assert texture["godot_hint"]["text_policy"].startswith("No baked text")

                region = texture["atlas_region"]
                assert region["w"] == expected_icon_size[0]
                assert region["h"] == expected_icon_size[1]
                assert region["x"] == texture["grid_position"]["column"] * expected_icon_size[0]
                assert region["y"] == texture["grid_position"]["row"] * expected_icon_size[1]

                footprint = texture["footprint_cells"]
                visual_size = texture["visual_size_cells"]
                assert footprint["w"] > 0
                assert footprint["h"] > 0
                assert visual_size["w"] > 0
                assert visual_size["h"] > 0


def test_godot_company_main_scene_background_pack_is_import_ready():
    pack_name = "godot-g1-art-pack-v0.7.1-company-main-scene-background"
    pack = GODOT_ART_ROOT / pack_name
    index_path = pack / "asset-index.json"

    assert index_path.is_file()
    assert (pack / "ART_PACK_SPEC.md").is_file()
    assert (pack / "GODOT_IMPORT_NOTES.md").is_file()

    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert index["pack_id"] == f"startup-sim-{pack_name}"
    assert "backup only" in index["storage_policy"]
    assert index["source_tooling"]["transparency"] == (
        "opaque background image retained as RGBA for Godot compatibility"
    )

    assert [asset["id"] for asset in index["assets"]] == ["company-main-scene-background-v0.7.1"]
    asset = index["assets"][0]
    export_path = pack / asset["file"]
    import_path = export_path.with_name(f"{export_path.name}.import")
    source_path = pack / asset["source"]
    raw_source_path = pack / asset["raw_source"]
    prompt_path = pack / asset["prompt"]
    layout_guide_path = pack / asset["layout_guide"]
    preview_path = pack / asset["preview"]

    assert export_path.is_file()
    assert import_path.is_file()
    assert source_path.is_file()
    assert raw_source_path.is_file()
    assert prompt_path.is_file()
    assert layout_guide_path.is_file()
    assert preview_path.is_file()
    assert asset["dimensions"] == {"width_px": 1920, "height_px": 1080}
    assert asset["grid_intent"]["role"].startswith("full-scene background")
    assert asset["grid_intent"]["safe_ui_edges"] == ["right", "bottom"]

    width, height = read_png_size(export_path)
    assert (width, height) == (1920, 1080)


def test_godot_tycoon_action_icon_pack_is_import_ready():
    pack_name = "godot-g1-art-pack-v2.2-tycoon-action-icons"
    pack = GODOT_ART_ROOT / pack_name
    index_path = pack / "asset-index.json"

    assert index_path.is_file()
    assert (pack / "ART_PACK_SPEC.md").is_file()
    assert (pack / "GODOT_IMPORT_NOTES.md").is_file()

    index_text = index_path.read_text(encoding="utf-8")
    assert "现金流可支撑时间" in index_text
    assert "跑道" not in index_text
    assert "Runway" not in index_text

    index = json.loads(index_text)
    assert index["pack_id"] == f"startup-sim-{pack_name}"
    assert "backup only" in index["storage_policy"]

    assert [asset["id"] for asset in index["assets"]] == ["tycoon-action-icon-atlas-v2.2"]
    asset = index["assets"][0]
    export_path = pack / asset["file"]
    source_path = pack / asset["source"]
    raw_source_path = pack / asset["raw_source"]
    prompt_path = pack / asset["prompt"]
    slice_guide_path = pack / asset["slice_guide"]
    preview_path = pack / asset["preview"]

    assert export_path.is_file()
    assert export_path.with_name(f"{export_path.name}.import").is_file()
    assert source_path.is_file()
    assert raw_source_path.is_file()
    assert prompt_path.is_file()
    assert slice_guide_path.is_file()
    assert preview_path.is_file()
    assert asset["grid"] == {"columns": 8, "rows": 3}
    assert asset["slice"] == {"cell_width_px": 224, "cell_height_px": 224}
    assert asset["image"] == {"width": 1792, "height": 672}
    assert asset["text_policy"]["cash_support_wording"] == "现金流可支撑时间"
    assert asset["sliced_icon_count"] == 24

    assert read_png_size(export_path) == (1792, 672)
    for icon_dir, icon_size in [
        ("exports/icons_224", (224, 224)),
        ("exports/icons_64", (64, 64)),
        ("exports/icons_48", (48, 48)),
    ]:
        icon_paths = sorted((pack / icon_dir).glob("*.png"))
        assert len(icon_paths) == 24
        assert all(read_png_size(path) == icon_size for path in icon_paths)
        assert all(path.with_name(f"{path.name}.import").is_file() for path in icon_paths)

    required_texture_fields = {
        "id",
        "semantic_name",
        "zh_name",
        "category",
        "file",
        "file_64",
        "file_48",
        "atlas",
        "atlas_region",
        "grid_position",
        "intended_layer",
        "anchor",
        "footprint_cells",
        "visual_size_cells",
        "usage",
        "state_tags",
        "godot_hint",
    }
    assert len(asset["textures"]) == 24
    for texture in asset["textures"]:
        assert required_texture_fields <= set(texture), texture["id"]
        assert (pack / texture["file"]).is_file()
        assert (pack / texture["file_64"]).is_file()
        assert (pack / texture["file_48"]).is_file()
        assert texture["atlas"] == asset["file"]
        assert texture["anchor"] == "center"
        assert texture["intended_layer"] == "HudLayer"
        assert texture["zh_name"]
        assert "跑道" not in texture["zh_name"]
        assert "Runway" not in texture["zh_name"]
        assert "跑道" not in texture["usage"]
        assert "Runway" not in texture["usage"]
        assert texture["godot_hint"]["text_policy"].startswith("No baked text")

        region = texture["atlas_region"]
        assert region["w"] == 224
        assert region["h"] == 224
        assert region["x"] == texture["grid_position"]["column"] * 224
        assert region["y"] == texture["grid_position"]["row"] * 224


def read_png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    assert header[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name} is not a PNG"
    return struct.unpack(">II", header[16:24])
