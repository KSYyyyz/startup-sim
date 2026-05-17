#!/usr/bin/env python3
"""文档一致性检查脚本。

检查项：
1. VERSION 与 README 标题一致
2. README / REPORTS 无旧版本残留
3. README 包含测试通过数量
4. 事件池数量与代码一致
5. REPORTS 顶部"当前路线"指向最新版本

6. 文本文件健康检查（NUL/编码/行数/行长）

exit 0 = 全部通过, exit 1 = 有失败项
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERSION_PATH = PROJECT_ROOT / "VERSION"
README_PATH = PROJECT_ROOT / "README.md"
REPORTS_PATH = PROJECT_ROOT / "REPORTS.md"

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)
    print(f"  ❌ {msg}")


def ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── 检查 1: VERSION 与 README 标题一致 ──────────────────────────


def check_version_readme_title() -> None:
    print("\n📋 检查 1: VERSION 与 README 标题一致")
    try:
        version_raw = read_text(VERSION_PATH).strip()
    except FileNotFoundError:
        fail("VERSION 文件不存在")
        return

    # 提取主版本号（如 "1.6"）
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

    # README 标题通常为 "# Startup Sim ... Alpha X.Y"
    title_pattern = rf"# Startup Sim\s+.*Alpha\s+{re.escape(version)}"
    if re.search(title_pattern, readme, re.IGNORECASE):
        ok(f"README 标题包含 Alpha {version}")
    else:
        # 尝试找出实际标题
        title_match = re.search(r"^# Startup Sim\s+(.*)", readme, re.MULTILINE)
        actual_title = title_match.group(0).strip() if title_match else "未找到标题"
        fail(f"README 标题版本不匹配: 期望 Alpha {version}, 实际: {actual_title}")


# ── 检查 2: README / REPORTS 无旧版本残留 ──────────────────────


def check_no_stale_versions() -> None:
    print("\n📋 检查 2: README / REPORTS 无旧版本残留")
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

    # 找出旧版本号：所有低于当前版本的 Alpha X.Y 引用
    stale_alphas = []
    for v_major in range(1, major + 1):
        max_minor = minor - 1 if v_major == major else 99
        for v_minor in range(0, max_minor + 1):
            if v_major == 1 and v_minor < 2:  # Alpha 1.0/1.1 不存在
                continue
            stale_alphas.append(f"Alpha {v_major}.{v_minor}")

    files_to_check = {
        "README.md": README_PATH,
        # REPORTS.md 是历史记录日志，H1 标题使用历史版本号是正常的；
        # REPORTS 的一致性只通过"当前路线"指向来检查
    }

    has_issues = False
    for name, path in files_to_check.items():
        try:
            content = read_text(path)
        except FileNotFoundError:
            continue

        for stale in stale_alphas:
            # 只检查 H1 标题（单 #），不检查历史章节的 ##/### 标题
            title_stale = re.search(rf"^#\s+[^#].*\b{re.escape(stale)}\b", content, re.MULTILINE)
            if title_stale:
                fail(f"{name}: H1 标题包含旧版本 {stale}")
                has_issues = True

    if not has_issues:
        ok("README / REPORTS 无 H1 标题旧版本残留")

    # 额外检查 REPORTS 顶部"当前路线"指向
    if REPORTS_PATH.exists():
        reports = read_text(REPORTS_PATH)
        # 检查顶部声明（前10行）
        top = "\n".join(reports.split("\n")[:10])
        current_marker = rf"当前路线以最新\s*Alpha\s*{re.escape(version)}"
        if re.search(current_marker, top):
            ok(f"REPORTS 顶部当前路线指向 Alpha {version}")
        else:
            # 尝试找到实际指向
            route_match = re.search(r"当前路线以最新\s*(Alpha\s*\d+\.\d+)", top)
            actual = route_match.group(1) if route_match else "未找到"
            fail(f"REPORTS 顶部当前路线不匹配: 期望 Alpha {version}, 实际: {actual}")


# ── 检查 3: README 包含测试通过数量 ──────────────────────────


def check_test_count_mentioned() -> None:
    print("\n📋 检查 3: README 包含测试通过数量")
    try:
        readme = read_text(README_PATH)
    except FileNotFoundError:
        fail("README.md 不存在")
        return

    # 检查是否提到 "passed" 或 测试数量
    if re.search(r"\d+\s+passed", readme):
        ok("README 包含测试通过数量")
    else:
        fail("README 未包含测试通过数量（如 '273 passed'）")


# ── 检查 4: 事件池数量与代码一致 ──────────────────────────


def check_event_pool_counts() -> None:
    print("\n📋 检查 4: 事件池数量与代码一致")
    try:
        # 动态导入 — 将项目根目录加入 sys.path
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

    # 检查 README 中的事件数量描述
    for doc_name, doc_path in [("README.md", README_PATH), ("REPORTS.md", REPORTS_PATH)]:
        try:
            content = read_text(doc_path)
        except FileNotFoundError:
            continue

        # 找 "X个事件" 或 "total: X" 这类模式
        event_count_match = re.search(r"(\d+)\s*个事件", content)
        if event_count_match:
            doc_count = int(event_count_match.group(1))
            if doc_count == actual["total"]:
                ok(f"{doc_name}: 事件总数 {doc_count} 与代码一致")
            else:
                fail(f"{doc_name}: 事件总数不匹配 — " f"文档 {doc_count}, 代码 {actual['total']}")

        # 检查各类别数量
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


HEALTH_FILES = [
    (PROJECT_ROOT / "QUICKSTART.md", 20),
    (PROJECT_ROOT / "tests/test_docs_and_demo.py", 20),
    (PROJECT_ROOT / "README.md", 0),
    (PROJECT_ROOT / "REPORTS.md", 0),
]


def check_text_file_health() -> None:
    print("\n📋 检查 5: 文本文件健康检查")
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
        if min_lines > 0 and len(lines) < min_lines:
            fail(f"{name}: 行数不足 ({len(lines)} < {min_lines})")

        for i, line in enumerate(lines, 1):
            if len(line) > 500:
                # 允许 URL 或表格行超长
                if "http" in line or "|" in line:
                    continue
                fail(f"{name}:{i} 单行过长 ({len(line)} 字符)")

    if not any("文本文件健康检查" in f for f in FAILURES):
        ok("所有受检文本文件通过健康检查")


# ── main ─────────────────────────────────────────────────────


def main() -> int:
    print("=" * 60)
    print("  文档一致性检查")
    print(f"  项目根目录: {PROJECT_ROOT}")
    print("=" * 60)

    check_version_readme_title()
    check_no_stale_versions()
    check_test_count_mentioned()
    check_event_pool_counts()
    check_text_file_health()

    print("\n" + "=" * 60)
    if FAILURES:
        print(f"  ❌ 失败 {len(FAILURES)} 项:")
        for f in FAILURES:
            print(f"     - {f}")
        print("=" * 60)
        return 1
    else:
        print("  ✅ 全部通过")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(main())
