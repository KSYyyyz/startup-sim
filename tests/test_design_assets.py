import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "design-assets" / "manifest.json"


def test_design_asset_manifest_uses_image_2_policy():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["policy"]["required_generation_model"] == "image-2"
    assert manifest["assets"], "design asset manifest should register frontend visual assets"


def test_registered_design_assets_have_existing_files_and_prompts():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    for asset in manifest["assets"]:
        assert asset["generation_model"] == "image-2"
        assert (ROOT / asset["source_prompt_path"]).is_file()
        assert (ROOT / asset["library_path"]).is_file()
        assert (ROOT / asset["frontend_path"]).is_file()
        assert asset["public_url"].startswith("/assets/")
        assert asset["used_by"], f"{asset['id']} should declare frontend usage"
