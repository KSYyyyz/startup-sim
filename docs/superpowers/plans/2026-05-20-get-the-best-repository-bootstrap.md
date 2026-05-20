# Get The Best Repository Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize the new `KSYyyyz/get-the-best` repository as the clean V2 home for 《壮志凌云 / Get The Best》 without carrying over the old panel-driven Godot frontend.

**Architecture:** The new repository starts as a documentation and project-governance baseline, not as a rushed Godot implementation. It imports the approved V2 direction docs, establishes hard boundaries against old `StartupSimGodot` contamination, and prepares the next implementation stage where a fresh Godot desktop frontend can be created.

**Tech Stack:** GitHub CLI, Markdown documentation, future Godot 4 .NET desktop frontend, C# Core reuse by planned migration/reference, no Web/Vercel frontend.

---

## File Structure

The bootstrap should create or update these files in the new repository:

- Create: `README.md`
  - Public entry point for 《壮志凌云 / Get The Best》.
  - States project identity, current status, and non-negotiable direction.

- Create: `docs/get_the_best_v2_execution_index.md`
  - Copy from `D:\Startup-sim\docs\get_the_best_v2_execution_index.md`.
  - Acts as the V2 route index.

- Create: `docs/get_the_best_v2_reference_game_study.md`
  - Copy from `D:\Startup-sim\docs\get_the_best_v2_reference_game_study.md`.
  - Defines same-genre research and anti-copy boundaries.

- Create: `docs/get_the_best_v2_engine_plugin_strategy.md`
  - Copy from `D:\Startup-sim\docs\get_the_best_v2_engine_plugin_strategy.md`.
  - Defines language, engine, plugin, and placeholder asset strategy.

- Create: `docs/get_the_best_v2_reset_architecture.md`
  - Copy from `D:\Startup-sim\docs\get_the_best_v2_reset_architecture.md`.
  - Defines isolation from the old panel UI prototype.

- Create: `docs/README.md`
  - Short navigation file listing the V2 documents.

- Create: `.github/workflows/docs.yml`
  - Minimal CI that checks Markdown files are readable UTF-8 and forbids banned player-facing terms in docs where appropriate.

- Create: `scripts/check_docs_bootstrap.py`
  - Small deterministic validation script for the new repository.
  - Keeps the initial CI lightweight before code migration begins.

Do not create the Godot project in this bootstrap task. The Godot project requires a separate implementation plan after the repo baseline is stable.

---

### Task 1: Prepare A Local Working Copy Under `D:\Startup-sim\.work`

**Files:**
- Create local clone folder: `D:\Startup-sim\.work\get-the-best`

- [ ] **Step 1: Verify the new repository exists**

Run:

```powershell
gh repo view KSYyyyz/get-the-best --json nameWithOwner,url,visibility
```

Expected: output includes `"nameWithOwner":"KSYyyyz/get-the-best"` and `"visibility":"PUBLIC"`.

- [ ] **Step 2: Clone into the allowed workspace**

Run:

```powershell
if (!(Test-Path 'D:\Startup-sim\.work')) {
  New-Item -ItemType Directory -Path 'D:\Startup-sim\.work' | Out-Null
}
if (Test-Path 'D:\Startup-sim\.work\get-the-best') {
  Remove-Item -LiteralPath 'D:\Startup-sim\.work\get-the-best' -Recurse -Force
}
gh repo clone KSYyyyz/get-the-best 'D:\Startup-sim\.work\get-the-best'
```

Expected: clone completes and `D:\Startup-sim\.work\get-the-best\.git` exists.

- [ ] **Step 3: Confirm the clone status**

Run:

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' status --short
git -C 'D:\Startup-sim\.work\get-the-best' branch --show-current
```

Expected: status is empty and branch is `main`.

---

### Task 2: Add Repository README And Document Navigation

**Files:**
- Modify: `D:\Startup-sim\.work\get-the-best\README.md`
- Create: `D:\Startup-sim\.work\get-the-best\docs\README.md`

- [ ] **Step 1: Replace README with the approved identity**

Set `README.md` to:

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
```

- [ ] **Step 2: Add docs navigation**

Create `docs/README.md`:

```markdown
# Get The Best 文档索引

## V2 执行基线

- `get_the_best_v2_execution_index.md`
- `get_the_best_v2_reference_game_study.md`
- `get_the_best_v2_engine_plugin_strategy.md`
- `get_the_best_v2_reset_architecture.md`

## 执行规则

新实现必须优先保护办公室经营主视角，不能把旧面板点击原型迁移进 V2。
```

- [ ] **Step 3: Check status**

Run:

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' status --short
```

Expected: `README.md` modified and `docs/README.md` added.

---

### Task 3: Copy Approved V2 Documents Into New Repository

**Files:**
- Create: `D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_execution_index.md`
- Create: `D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_reference_game_study.md`
- Create: `D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_engine_plugin_strategy.md`
- Create: `D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_reset_architecture.md`

- [ ] **Step 1: Copy the documents**

Run:

```powershell
Copy-Item -LiteralPath 'D:\Startup-sim\docs\get_the_best_v2_execution_index.md' -Destination 'D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_execution_index.md'
Copy-Item -LiteralPath 'D:\Startup-sim\docs\get_the_best_v2_reference_game_study.md' -Destination 'D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_reference_game_study.md'
Copy-Item -LiteralPath 'D:\Startup-sim\docs\get_the_best_v2_engine_plugin_strategy.md' -Destination 'D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_engine_plugin_strategy.md'
Copy-Item -LiteralPath 'D:\Startup-sim\docs\get_the_best_v2_reset_architecture.md' -Destination 'D:\Startup-sim\.work\get-the-best\docs\get_the_best_v2_reset_architecture.md'
```

Expected: all four files exist in the new repository.

- [ ] **Step 2: Verify the naming**

Run:

```powershell
Select-String -Path 'D:\Startup-sim\.work\get-the-best\docs\*.md' -Pattern 'Get The Best|壮志凌云|get-the-best'
```

Expected: matches appear in the copied V2 docs.

---

### Task 4: Add Minimal Docs CI

**Files:**
- Create: `D:\Startup-sim\.work\get-the-best\scripts\check_docs_bootstrap.py`
- Create: `D:\Startup-sim\.work\get-the-best\.github\workflows\docs.yml`

- [ ] **Step 1: Create the validation script**

Create `scripts/check_docs_bootstrap.py`:

```python
#!/usr/bin/env python3
"""Validate the Get The Best repository bootstrap docs."""

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
            failures.append(f"Missing required file: {path.relative_to(ROOT)}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"File is not valid UTF-8: {path.relative_to(ROOT)}: {exc}")
            continue
        if "\x00" in text:
            failures.append(f"File contains NUL byte: {path.relative_to(ROOT)}")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in REQUIRED_FILES if path.exists()
    )
    for term in REQUIRED_TERMS:
        if term not in combined:
            failures.append(f"Missing required term: {term}")
    for term in BANNED_TERMS:
        if term in combined:
            failures.append(f"Banned player-facing term found: {term}")

    if failures:
        print("Get The Best docs bootstrap check failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("Get The Best docs bootstrap check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Create GitHub Actions workflow**

Create `.github/workflows/docs.yml`:

```yaml
name: Docs

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
      - name: Check bootstrap docs
        run: python scripts/check_docs_bootstrap.py
```

- [ ] **Step 3: Run the validation locally**

Run:

```powershell
python 'D:\Startup-sim\.work\get-the-best\scripts\check_docs_bootstrap.py'
```

Expected: `Get The Best docs bootstrap check passed.`

---

### Task 5: Commit And Push New Repository Baseline

**Files:**
- Commit all changes in `D:\Startup-sim\.work\get-the-best`

- [ ] **Step 1: Inspect diff**

Run:

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' diff --check
git -C 'D:\Startup-sim\.work\get-the-best' status --short
```

Expected: no whitespace errors; only README, docs, script, and workflow files changed.

- [ ] **Step 2: Commit**

Run:

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' add README.md docs scripts .github
git -C 'D:\Startup-sim\.work\get-the-best' commit -m "docs: establish get the best v2 baseline"
```

Expected: commit succeeds.

- [ ] **Step 3: Push**

Run:

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' push
```

Expected: `main -> main`.

---

### Task 6: Check New Repository CI

**Files:**
- No file changes.

- [ ] **Step 1: Watch the Docs workflow**

Run:

```powershell
$run = gh run list --repo KSYyyyz/get-the-best --branch main --limit 1 --json databaseId --jq '.[0].databaseId'
gh run watch $run --repo KSYyyyz/get-the-best --exit-status
```

Expected: workflow passes.

- [ ] **Step 2: Confirm final repository status**

Run:

```powershell
git -C 'D:\Startup-sim\.work\get-the-best' status --short
gh repo view KSYyyyz/get-the-best --json nameWithOwner,url,visibility
```

Expected: local status is empty; repository remains public.

---

## Self-Review

Spec coverage:

- New repository baseline is covered by Tasks 1-6.
- V2 naming is covered by Task 2 and Task 4 validation.
- Approved V2 docs are copied by Task 3.
- CI is added and checked by Tasks 4 and 6.
- No Godot implementation is included, which matches the current “plan before code” decision.

Placeholder scan:

- This plan contains no TBD/TODO placeholders.
- Every command has an expected result.

Type and naming consistency:

- Repository slug is consistently `get-the-best`.
- Game English name is consistently `Get The Best`.
- Chinese name is consistently `壮志凌云`.
