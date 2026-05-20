# Get The Best 新仓库基线初始化执行计划

> **给执行代理的要求：** 必须使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`，按任务逐项执行。步骤使用复选框语法，方便执行中持续更新状态。

**目标：** 将 `KSYyyyz/get-the-best` 初始化为《壮志凌云 / Get The Best》的干净 V2 项目仓库，不迁移旧面板式 Godot 前端。

**架构：** 新仓库先作为文档和项目治理基线，不急着创建 Godot 工程。它导入已经批准的 V2 路线文档，建立防止旧 `StartupSimGodot` 原型污染新项目的硬边界，并为后续新 Godot 桌面前端工程做准备。

**技术栈：** GitHub CLI、Markdown 文档、未来 Godot 4 .NET 桌面前端、计划复用或迁移的 C# Core，不做 Web/Vercel 前端。

---

## 文件结构

本次初始化在新仓库中创建或更新以下文件：

- 创建或修改：`README.md`
  - 作为《壮志凌云 / Get The Best》的公开入口。
  - 说明项目身份、当前状态和不可变方向。

- 创建：`docs/get_the_best_v2_execution_index.md`
  - 从 `D:\Startup-sim\docs\get_the_best_v2_execution_index.md` 复制。
  - 作为 V2 路线索引。

- 创建：`docs/get_the_best_v2_reference_game_study.md`
  - 从 `D:\Startup-sim\docs\get_the_best_v2_reference_game_study.md` 复制。
  - 定义同类游戏研究结论和反照搬边界。

- 创建：`docs/get_the_best_v2_engine_plugin_strategy.md`
  - 从 `D:\Startup-sim\docs\get_the_best_v2_engine_plugin_strategy.md` 复制。
  - 定义语言、引擎、插件和占位素材策略。

- 创建：`docs/get_the_best_v2_reset_architecture.md`
  - 从 `D:\Startup-sim\docs\get_the_best_v2_reset_architecture.md` 复制。
  - 定义与旧面板 UI 原型的隔离方式。

- 创建：`docs/README.md`
  - 简短列出 V2 文档入口。

- 创建：`.github/workflows/docs.yml`
  - 最小 CI：检查 Markdown 文件可读，并检查项目文档语言和禁用词。

- 创建：`scripts/check_docs_bootstrap.py`
  - 新仓库的确定性文档校验脚本。
  - 在代码迁移前先保持 CI 轻量。

本次任务不创建 Godot 工程。Godot 工程需要在仓库基线稳定后另写实施计划。

---

### 任务 1：在 `D:\Startup-sim\.work` 下准备本地工作副本

**文件：**
- 创建本地克隆目录：`D:\Startup-sim\.work\get-the-best`

- [ ] **步骤 1：确认新仓库存在**

运行：

```powershell
gh repo view KSYyyyz/get-the-best --json nameWithOwner,url,visibility
```

预期：输出包含 `"nameWithOwner":"KSYyyyz/get-the-best"` 和 `"visibility":"PUBLIC"`。

- [ ] **步骤 2：克隆到允许的工作目录**

运行：

```powershell
if (!(Test-Path 'D:\Startup-sim\.work')) {
  New-Item -ItemType Directory -Path 'D:\Startup-sim\.work' | Out-Null
}
if (Test-Path 'D:\Startup-sim\.work\get-the-best') {
  Remove-Item -LiteralPath 'D:\Startup-sim\.work\get-the-best' -Recurse -Force
}
gh repo clone KSYyyyz/get-the-best 'D:\Startup-sim\.work\get-the-best'
```

预期：克隆完成，并且 `D:\Startup-sim\.work\get-the-best\.git` 存在。

- [ ] **步骤 3：确认克隆状态**

运行：

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' status --short
git -C 'D:\Startup-sim\.work\get-the-best' branch --show-current
```

预期：状态为空，分支为 `main`。

---

### 任务 2：添加仓库说明和文档导航

**文件：**
- 修改：`D:\Startup-sim\.work\get-the-best\README.md`
- 创建：`D:\Startup-sim\.work\get-the-best\docs\README.md`

- [ ] **步骤 1：用批准后的项目身份替换 README**

将 `README.md` 写为：

```markdown
# Get The Best / 壮志凌云

《壮志凌云 / Get The Best》是一款 Godot 桌面端创业公司经营模拟游戏。

当前状态：V2 立项与工程隔离阶段。

## 核心方向

- 办公室空间是主棋盘。
- 公司成长是主目标。
- 房间、设施、员工和经营反馈服务创业主线。
- C# Core 是规则核心，Godot 只负责表现层和交互。
- 玩家可见文案使用“现金流可支撑时间”，不使用“跑道”或 Runway。
- 当前不做 Web/Vercel 前端。
- 当前不做 AI 玩法。

## V2 立项原因

旧 Godot 原型已经明显形成面板点击游戏惯性。V2 不在旧主场景上继续缝补，而是建立干净的 Godot 前端工程，并保留既有美术资源、C# Core、测试经验和 MCP 试玩经验。

## 文档入口

- `docs/get_the_best_v2_execution_index.md`
- `docs/get_the_best_v2_reference_game_study.md`
- `docs/get_the_best_v2_engine_plugin_strategy.md`
- `docs/get_the_best_v2_reset_architecture.md`

## 当前不做

- 不迁移旧 `StartupSimGodot/main.tscn` 作为 V2 主场景。
- 不复制旧 G2OperationsPanel。
- 不让 HUD 和日志成为主游戏体验。
- 不绕过 C# Core 实现经营规则。

## 文档语言

项目文档、执行计划、交接记录和 CI 说明默认使用中文。英文名 Get The Best、仓库名、代码标识符、命令、文件路径和 URL 可以保留原文。
```

- [ ] **步骤 2：添加文档导航**

创建 `docs/README.md`：

```markdown
# Get The Best 文档索引

## V2 执行基线

- `get_the_best_v2_execution_index.md`
- `get_the_best_v2_reference_game_study.md`
- `get_the_best_v2_engine_plugin_strategy.md`
- `get_the_best_v2_reset_architecture.md`

## 执行规则

新实现必须优先保护办公室经营主视角，不能把旧面板点击原型迁移进 V2。

## 文档语言

除英文名、仓库名、代码标识符、命令、文件路径和 URL 外，项目文档正文必须使用中文。
```

- [ ] **步骤 3：检查状态**

运行：

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' status --short
```

预期：`README.md` 已修改，`docs/README.md` 已新增。

---

### 任务 3：复制已批准的 V2 文档

**文件：**
- 创建：`D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_execution_index.md`
- 创建：`D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_reference_game_study.md`
- 创建：`D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_engine_plugin_strategy.md`
- 创建：`D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_reset_architecture.md`

- [ ] **步骤 1：复制文档**

运行：

```powershell
Copy-Item -LiteralPath 'D:\Startup-sim\docs\get_the_best_v2_execution_index.md' -Destination 'D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_execution_index.md'
Copy-Item -LiteralPath 'D:\Startup-sim\docs\get_the_best_v2_reference_game_study.md' -Destination 'D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_reference_game_study.md'
Copy-Item -LiteralPath 'D:\Startup-sim\docs\get_the_best_v2_engine_plugin_strategy.md' -Destination 'D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_engine_plugin_strategy.md'
Copy-Item -LiteralPath 'D:\Startup-sim\docs\get_the_best_v2_reset_architecture.md' -Destination 'D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_reset_architecture.md'
```

预期：四份文件都存在于新仓库。

- [ ] **步骤 2：验证命名**

运行：

```powershell
Select-String -Path 'D:\Startup-sim\.work\get-the-best\docs\*.md' -Pattern 'Get The Best|壮志凌云|get-the-best'
```

预期：复制的 V2 文档中能查到这些命名。

---

### 任务 4：添加最小文档 CI

**文件：**
- 创建：`D:\Startup-sim\.work\get-the-best\scripts\check_docs_bootstrap.py`
- 创建：`D:\Startup-sim\.work\get-the-best\.github\workflows\docs.yml`

- [ ] **步骤 1：创建文档校验脚本**

创建 `scripts/check_docs_bootstrap.py`：

```python
#!/usr/bin/env python3
"""校验 Get The Best 新仓库初始化文档。"""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REQUIRED_FILES = [
    ROOT / "README.md",
    DOCS / "README.md",
    DOCS / "get_the_best_v2_execution_index.md",
    DOCS / "get_the_best_v2_reference_game_study.md",
    DOCS / "get_the_best_v2_engine_plugin_strategy.md",
    DOCS / "get_the_best_v2_reset_architecture.md",
]
BANNED_TERMS = ["Runway", "跑道"]
REQUIRED_TERMS = ["Get The Best", "壮志凌云", "现金流可支撑时间"]


def main() -> int:
    failures: list[str] = []
    for path in REQUIRED_FILES:
        if not path.exists():
            failures.append(f"缺少必需文件: {path.relative_to(ROOT)}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"文件不是有效 UTF-8: {path.relative_to(ROOT)}: {exc}")
            continue
        if "\x00" in text:
            failures.append(f"文件包含 NUL 字节: {path.relative_to(ROOT)}")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in REQUIRED_FILES if path.exists()
    )
    for term in REQUIRED_TERMS:
        if term not in combined:
            failures.append(f"缺少必需词: {term}")
    for term in BANNED_TERMS:
        if term in combined:
            failures.append(f"发现禁用玩家可见词: {term}")

    if failures:
        print("Get The Best 文档初始化检查失败:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("Get The Best 文档初始化检查通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **步骤 2：创建 GitHub Actions 工作流**

创建 `.github/workflows/docs.yml`：

```yaml
name: 文档检查

on:
  push:
  pull_request:

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: 检查初始化文档
        run: python scripts/check_docs_bootstrap.py
```

- [ ] **步骤 3：本地运行校验**

运行：

```powershell
python 'D:\Startup-sim\.work\get-the-best\scripts\check_docs_bootstrap.py'
```

预期：输出 `Get The Best 文档初始化检查通过。`

---

### 任务 5：提交并推送新仓库基线

**文件：**
- 提交 `D:\Startup-sim\.work\get-the-best` 中的所有变更

- [ ] **步骤 1：检查差异**

运行：

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' diff --check
git -C 'D:\Startup-sim\.work\get-the-best' status --short
```

预期：没有空白错误；只出现 README、docs、script 和 workflow 文件变更。

- [ ] **步骤 2：提交**

运行：

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' add README.md docs scripts .github
git -C 'D:\Startup-sim\.work\get-the-best' commit -m "docs: establish get the best v2 baseline"
```

预期：提交成功。

- [ ] **步骤 3：推送**

运行：

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' push
```

预期：输出包含 `main -> main`。

---

### 任务 6：检查新仓库 CI

**文件：**
- 不修改文件。

- [ ] **步骤 1：观察文档工作流**

运行：

```powershell
$run = gh run list --repo KSYyyyz/get-the-best --branch main --limit 1 --json databaseId --jq '.[0].databaseId'
gh run watch $run --repo KSYyyyz/get-the-best --exit-status
```

预期：工作流通过。

- [ ] **步骤 2：确认最终仓库状态**

运行：

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' status --short
gh repo view KSYyyyz/get-the-best --json nameWithOwner,url,visibility
```

预期：本地状态为空；仓库仍为 public。

---

## 自检

规格覆盖：

- 新仓库基线由任务 1-6 覆盖。
- V2 命名由任务 2 和任务 4 校验覆盖。
- 已批准的 V2 文档由任务 3 复制。
- CI 由任务 4 添加，并由任务 6 检查。
- 不包含 Godot 实现，符合当前“先计划再写代码”的决定。

占位扫描：

- 本计划没有 TBD、TODO 或“以后补充”式占位。
- 每条命令都有预期结果。

命名一致性：

- 仓库 slug 统一为 `get-the-best`。
- 游戏英文名统一为 `Get The Best`。
- 中文名统一为 `壮志凌云`。
- 文档正文默认中文；英文名、仓库名、代码标识符、命令、文件路径和 URL 可保留原文。
