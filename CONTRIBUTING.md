# Contributing

## ⚠ 推送前强制要求

每次 commit 和 push 前，必须运行 `make check`，并确认以下全部通过：

- ruff: passed
- black: passed
- isort: passed
- pytest: 全部通过
- playtest: 平衡验证通过
- docs-check: 文档一致性检查通过

全部通过后，在 commit message 中注明 check 结果，再 push。禁止跳过任何一步。

## 文档一致性规范

### 1. VERSION 与 README 标题必须一致
- 例如 VERSION=1.6，则 README 标题必须是 `Startup Sim Alpha 1.6`。

### 2. README 必须与实际代码能力一致
- 不能写尚未接入 CLI / 飞书 / playtest 的功能。
- 不能写"已完成"但实际只是新增文件未接入。
- 不能写过期的路线建议。

### 3. REPORTS.md 必须记录真实验证结果
- pytest 结果必须来自真实运行。
- playtest 结果必须来自真实运行。
- 不允许为了好看修改结局结果。
- 如果随机种子导致偶发现象，必须写成"偶发"，不能写成稳定结论。
- REPORTS 标题统一使用 `# Startup Sim — 版本开发报告`，不写版本号。

### 4. 数量类描述必须以代码输出为准
- 事件数量以 `get_event_summary()` 为准。
- 测试数量以 pytest 实际输出为准。
- playtest 结局数量以 `scripts/playtest.py` 实际输出为准。
- 成就数量以 AchievementEngine 实际规则为准。
- 不允许手写猜数字。

### 5. 功能接入说明必须验证
- 如果 README 写"CLI 已接入"，必须确认 `app.py` 中真实调用。
- 如果 README 写"飞书已接入"，必须确认 `feishu_play.py` 中真实调用。
- 如果 README 写"playtest 已覆盖"，必须确认 `scripts/playtest.py` 真实调用主流程。
- 如果 README 写"工程治理已完成"，必须确认 `make check` 通过。

### 6. 历史阶段说明要标注时效
- REPORTS.md 中旧阶段的"下一步建议"只作为历史记录。
- 顶部必须写清楚"当前路线以最新 Alpha X.Y 为准"。

### 7. 文档更新不得替代代码实现
- 不允许只改 README / REPORTS 声称功能完成。
- 功能完成必须有代码、测试、playtest 或人工验证支撑。

## 开发流程

1. **建分支** — 从 `master` 创建功能分支：`git checkout -b feature/xxx`
2. **改代码** — 实现功能或修复，不新增游戏功能、不改数值平衡（除非明确要求）
3. **格式化** — `make format`（black + isort）
4. **静态检查** — `make lint`（ruff check）
5. **运行测试** — `make test`（pytest -v）
6. **试玩验证** — `make playtest`（python scripts/playtest.py）
7. **文档检查** — `make docs-check`（python scripts/check_docs_consistency.py）
8. **更新文档** — 同步更新 README.md / REPORTS.md / VERSION
9. **质量门** — `make check`（依次执行 format + lint + test + playtest + docs-check）
10. **提交** — `git commit -m "描述性信息"`
11. **推送** — `git push`
12. **确认 CI** — 确认 GitHub Actions CI 绿色通过（含 docs-check）

## 禁止项

- **未格式化提交** — 所有代码必须通过 `make format` 后再提交
- **README 与代码不一致** — 版本号、测试数量、功能描述必须与代码实际状态一致
- **playtest 未跑就更新版本** — 任何版本号更新前必须 `make playtest` 验证通过
- **为文档强行改数值** — 文档描述必须以实际代码行为为准，不得反向调整代码迁就文档
- **绕过主流程造假如通过** — 质量门必须真实通过，不得伪造通过记录
- **文档跳过一致性检查** — 版本推进必须通过 `make docs-check`，不得手动豁免
