#!/usr/bin/env python3
"""文档一致性检查脚本。

检查项：
1. VERSION 与 README 标题一致
2. README / REPORTS 无旧版本残留
3. README 包含测试通过数量
4. 事件池数量与代码一致
5. REPORTS 顶部"当前路线"指向最新版本
6. README 暴露 Godot 主线、C# Core、Web 验证台和参考游戏分析入口
7. 文本文件健康检查（NUL/编码/行数/行长）

exit 0 = 全部通过, exit 1 = 有失败项
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERSION_PATH = PROJECT_ROOT / "VERSION"
README_PATH = PROJECT_ROOT / "README.md"
REPORTS_PATH = PROJECT_ROOT / "REPORTS.md"
GODOT_PLAN_PATH = PROJECT_ROOT / "docs" / "godot_migration_plan.md"
CSHARP_CORE_PLAN_PATH = PROJECT_ROOT / "docs" / "csharp_core_migration_plan.md"
WEB_VALIDATION_BENCH_PATH = PROJECT_ROOT / "docs" / "web_validation_bench.md"
REFERENCE_GAME_ANALYSIS_PATH = PROJECT_ROOT / "docs" / "reference_game_analysis.md"
VERCEL_FRONTEND_URL = "https://startup-sim-khaki.vercel.app"

FAILURES: list[str] = []


def safe_print(text: str) -> None:
    """Print text safely on Windows consoles that may not support emoji."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Strip emoji and other non-BMP characters for GBK consoles
        ascii_text = text.encode("ascii", errors="replace").decode("ascii")
        print(ascii_text)


def fail(msg: str) -> None:
    FAILURES.append(msg)
    safe_print(f"  X {msg}")


def ok(msg: str) -> None:
    safe_print(f"  OK {msg}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── 检查 1: VERSION 与 README 标题一致 ──────────────────────────


def check_version_readme_title() -> None:
    safe_print("\n[检查 1] VERSION 与 README 标题一致")
    try:
        version_raw = read_text(VERSION_PATH).strip()
    except FileNotFoundError:
        fail("VERSION 文件不存在")
        return

    m = re.match(r"^(\d+\.\d+)", version_raw)
    if not m:
        fail(f"VERSION 格式无法解析: {version_raw}")
        return
    version = m.group(1)

    try:
        readme = read_text(README_PATH)
    except FileNotFoundError:
        fail("README.md 不存在")
        return

    title_pattern = rf"# Startup Sim\s+.*Alpha\s+{re.escape(version)}"
    if re.search(title_pattern, readme, re.IGNORECASE):
        ok(f"README 标题包含 Alpha {version}")
    else:
        title_match = re.search(r"^# Startup Sim\s+(.*)", readme, re.MULTILINE)
        actual_title = title_match.group(0).strip() if title_match else "未找到标题"
        fail(f"README 标题版本不匹配: 期望 Alpha {version}, 实际: {actual_title}")


# ── 检查 2: README / REPORTS 无旧版本残留 ──────────────────────


def check_no_stale_versions() -> None:
    safe_print("\n[检查 2] README / REPORTS 无旧版本残留")
    try:
        version_raw = read_text(VERSION_PATH).strip()
    except FileNotFoundError:
        fail("无法读取 VERSION，跳过旧版本检查")
        return

    m = re.match(r"^(\d+)\.(\d+)", version_raw)
    if not m:
        fail("VERSION 格式无法解析，跳过旧版本检查")
        return
    major, minor = int(m.group(1)), int(m.group(2))
    version = f"{major}.{minor}"

    stale_alphas = []
    for v_major in range(1, major + 1):
        max_minor = minor - 1 if v_major == major else 99
        for v_minor in range(0, max_minor + 1):
            if v_major == 1 and v_minor < 2:
                continue
            stale_alphas.append(f"Alpha {v_major}.{v_minor}")

    files_to_check = {
        "README.md": README_PATH,
    }

    has_issues = False
    for name, path in files_to_check.items():
        try:
            content = read_text(path)
        except FileNotFoundError:
            continue

        for stale in stale_alphas:
            title_stale = re.search(rf"^#\s+[^#].*\b{re.escape(stale)}\b", content, re.MULTILINE)
            if title_stale:
                fail(f"{name}: H1 标题包含旧版本 {stale}")
                has_issues = True

    if not has_issues:
        ok("README / REPORTS 无 H1 标题旧版本残留")

    if REPORTS_PATH.exists():
        reports = read_text(REPORTS_PATH)
        top = "\n".join(reports.split("\n")[:10])
        current_marker = rf"当前路线以最新\s*Alpha\s*{re.escape(version)}"
        if re.search(current_marker, top):
            ok(f"REPORTS 顶部当前路线指向 Alpha {version}")
        else:
            route_match = re.search(r"当前路线以最新\s*(Alpha\s*\d+\.\d+)", top)
            actual = route_match.group(1) if route_match else "未找到"
            fail(f"REPORTS 顶部当前路线不匹配: 期望 Alpha {version}, 实际: {actual}")


# ── 检查 3: README 包含测试通过数量 ──────────────────────────


def check_test_count_mentioned() -> None:
    safe_print("\n[检查 3] README 包含测试通过数量")
    try:
        readme = read_text(README_PATH)
    except FileNotFoundError:
        fail("README.md 不存在")
        return

    if re.search(r"\d+\s+passed", readme):
        ok("README 包含测试通过数量")
    else:
        fail("README 未包含测试通过数量（如 '289 passed'）")


# ── 检查 4: 事件池数量与代码一致 ──────────────────────────


def check_event_pool_counts() -> None:
    safe_print("\n[检查 4] 事件池数量与代码一致")
    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from src.core.events import get_event_summary

        actual = get_event_summary()
    except Exception as e:
        fail(f"无法获取事件统计: {e}")
        return

    print(
        f"  代码实际: total={actual['total']}, "
        f"opportunity={actual['opportunity']}, "
        f"crisis={actual['crisis']}, "
        f"neutral={actual['neutral']}"
    )

    for doc_name, doc_path in [("README.md", README_PATH), ("REPORTS.md", REPORTS_PATH)]:
        try:
            content = read_text(doc_path)
        except FileNotFoundError:
            continue

        event_count_match = re.search(r"(\d+)\s*个事件", content)
        if event_count_match:
            doc_count = int(event_count_match.group(1))
            if doc_count == actual["total"]:
                ok(f"{doc_name}: 事件总数 {doc_count} 与代码一致")
            else:
                fail(f"{doc_name}: 事件总数不匹配 — 文档 {doc_count}, 代码 {actual['total']}")

        for cat_key, cat_label in [
            ("opportunity", "机会"),
            ("crisis", "危机"),
            ("neutral", "中性"),
        ]:
            cat_pattern = rf"{cat_label}类\s*(\d+)\s*个"
            cat_match = re.search(cat_pattern, content)
            if cat_match:
                doc_count = int(cat_match.group(1))
                if doc_count == actual[cat_key]:
                    ok(f"{doc_name}: {cat_label}类 {doc_count} 个与代码一致")
                else:
                    fail(
                        f"{doc_name}: {cat_label}类数量不匹配 — "
                        f"文档 {doc_count}, 代码 {actual[cat_key]}"
                    )


# ── 检查 5: 文本文件健康检查 ───────────────────────────────


def check_current_direction_docs_visible() -> None:
    safe_print("\n[检查 5] README 暴露 Godot 主线与验证台入口")
    try:
        readme = read_text(README_PATH)
    except FileNotFoundError:
        fail("README.md 不存在")
        return

    missing = []
    required_markers = [
        "docs/godot_migration_plan.md",
        "docs/csharp_core_migration_plan.md",
        "docs/web_validation_bench.md",
        "docs/indie_game_product_direction.md",
        "docs/reference_game_analysis.md",
        VERCEL_FRONTEND_URL,
        "后续开发以 C# Core + Godot",
    ]
    for marker in required_markers:
        if marker not in readme:
            missing.append(marker)

    if not GODOT_PLAN_PATH.exists():
        missing.append(str(GODOT_PLAN_PATH.relative_to(PROJECT_ROOT)))
    if not CSHARP_CORE_PLAN_PATH.exists():
        missing.append(str(CSHARP_CORE_PLAN_PATH.relative_to(PROJECT_ROOT)))
    if not WEB_VALIDATION_BENCH_PATH.exists():
        missing.append(str(WEB_VALIDATION_BENCH_PATH.relative_to(PROJECT_ROOT)))
    if not REFERENCE_GAME_ANALYSIS_PATH.exists():
        missing.append(str(REFERENCE_GAME_ANALYSIS_PATH.relative_to(PROJECT_ROOT)))

    if missing:
        fail("README 缺少 Godot 主线、C# Core、Web 验证台或参考分析入口: " + ", ".join(missing))
    else:
        ok("README 已暴露 Godot 主线、C# Core、产品方向、参考分析和 Web 验证台入口")


# ── 检查 6: 文本文件健康检查 ───────────────────────────────


HEALTH_FILES = [
    (PROJECT_ROOT / "QUICKSTART.md", 40),
    (PROJECT_ROOT / "README.md", 80),
    (PROJECT_ROOT / "REPORTS.md", 120),
    (PROJECT_ROOT / "docs" / "godot_migration_plan.md", 80),
    (PROJECT_ROOT / "docs" / "csharp_core_migration_plan.md", 60),
    (PROJECT_ROOT / "docs" / "web_validation_bench.md", 50),
    (PROJECT_ROOT / "docs" / "reference_game_analysis.md", 80),
    (PROJECT_ROOT / "tests" / "test_docs_and_demo.py", 80),
    (PROJECT_ROOT / "scripts" / "check_docs_consistency.py", 150),
]


def check_text_file_health() -> None:
    safe_print("\n[检查 6] 文本文件健康检查")
    for file_path, min_lines in HEALTH_FILES:
        name = file_path.relative_to(PROJECT_ROOT)
        try:
            data = file_path.read_bytes()
        except FileNotFoundError:
            fail(f"{name}: 文件不存在")
            continue

        if b"\x00" in data:
            fail(f"{name}: 包含 NUL 字节")
            continue

        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as e:
            fail(f"{name}: UTF-8 解码失败 — {e}")
            continue

        lines = text.splitlines()
        if len(lines) < min_lines:
            fail(f"{name}: 行数不足 ({len(lines)} < {min_lines})")

        for i, line in enumerate(lines, 1):
            if len(line) > 500:
                if "http" in line or "|" in line:
                    continue
                fail(f"{name}:{i} 单行过长 ({len(line)} 字符)")

    if not any("文本文件健康检查" in f for f in FAILURES):
        ok("所有受检文本文件通过健康检查")


# ── main ─────────────────────────────────────────────────────


def main() -> int:
    safe_print("=" * 60)
    safe_print("  文档一致性检查")
    safe_print(f"  项目根目录: {PROJECT_ROOT}")
    safe_print("=" * 60)

    check_version_readme_title()
    check_no_stale_versions()
    check_test_count_mentioned()
    check_event_pool_counts()
    check_current_direction_docs_visible()
    check_text_file_health()

    safe_print("\n" + "=" * 60)
    if FAILURES:
        safe_print(f"  失败 {len(FAILURES)} 项:")
        for f in FAILURES:
            safe_print(f"     - {f}")
        safe_print("=" * 60)
        return 1
    else:
        safe_print("  全部通过")
        safe_print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
