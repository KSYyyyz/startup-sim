#!/usr/bin/env python3
"""启动前检查脚本 — 不绕过 app.py，只做启动检查和提示。

用法:
    python scripts/start_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent


def get_version() -> str:
    version_file = PROJECT_DIR / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "未知"


def check_python() -> tuple[bool, str]:
    v = sys.version_info
    ok = v.major >= 3 and v.minor >= 9
    return ok, f"{v.major}.{v.minor}.{v.micro}"


def check_requirements() -> bool:
    req_file = PROJECT_DIR / "requirements.txt"
    return req_file.exists()


def check_app() -> bool:
    app_file = PROJECT_DIR / "app.py"
    return app_file.exists()


def main():
    print("=" * 60)
    print("  Startup Sim — 启动前检查")
    print("=" * 60)
    print()

    # 1. 版本
    version = get_version()
    print(f"  📦 当前版本: Alpha {version}")

    # 2. 项目目录
    print(f"  📁 项目目录: {PROJECT_DIR}")

    # 3. Python 检查
    py_ok, py_ver = check_python()
    if py_ok:
        print(f"  ✅ Python 版本: {py_ver}")
    else:
        print(f"  ❌ Python 版本: {py_ver} (需要 3.9+)")
        print("     请安装 Python 3.9 或更高版本")
        return

    # 4. 依赖检查
    if check_requirements():
        print("  ✅ requirements.txt 存在")
    else:
        print("  ❌ requirements.txt 不存在")
        return

    # 5. app.py 检查
    if check_app():
        print("  ✅ app.py 存在")
    else:
        print("  ❌ app.py 不存在")
        return

    print()
    print("=" * 60)
    print("  🚀 推荐启动命令")
    print("=" * 60)
    print()
    print(f"  cd {PROJECT_DIR}")
    print("  pip install -r requirements.txt")
    print('  python app.py new --name "你的名字"')
    print()
    print("=" * 60)
    print("  💡 第一回合建议")
    print("=" * 60)
    print()
    print("  启动后你会看到公司初始状态面板，然后输入第一个决策。")
    print()
    print("  推荐试试:")
    print("    花20万研发产品，花10万做营销")
    print()
    print("  也可以:")
    print("    融资500万出让10%股权，花30万研发产品")
    print()
    print("  游戏中随时输入 'help' 查看帮助，'status' 查看状态。")
    print()
    print("  📖 快速开始: QUICKSTART.md")
    print("  📋 样例局: examples/")
    print("  🔧 遇到问题: docs/troubleshooting.md")
    print()


if __name__ == "__main__":
    main()
