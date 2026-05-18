from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_obsolete_unity_tree_is_not_tracked():
    assert not (ROOT / "unity").exists(), "Unity tree should not remain in the Godot-first repo"


def test_obsolete_web_frontend_tree_is_not_tracked():
    assert not (
        ROOT / "frontend"
    ).exists(), "React/Vercel frontend should not remain in the Godot-only frontend repo"
    assert not (
        ROOT / "src" / "api"
    ).exists(), "Web frontend API wrapper should not remain after Vercel is abandoned"


def test_project_layout_doc_records_current_roots():
    doc = ROOT / "docs" / "project_layout.md"

    assert doc.is_file()
    content = doc.read_text(encoding="utf-8")
    assert "godot/" in content
    assert "csharp/" in content
    assert "后续前端只做 Godot" in content or "后续前端只在 Godot" in content
    assert "不允许重新加入 Unity 主线文件" in content
    assert "不允许重新加入 Vercel/Web 前端主线文件" in content


def test_old_frontend_word_plan_removed():
    stale_docs = list((ROOT / "docs").glob("Startup_Sim_Frontend_Alpha_0_1_*.docx"))

    assert stale_docs == []
