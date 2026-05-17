# Contributing

## ⚠ 推送前强制要求

每次 commit 和 push 前，必须运行 `make check`，并确认以下全部通过：

- ruff: passed
- black: passed
- isort: passed
- pytest: 全部通过
- playtest: 平衡验证通过

全部通过后，在 commit message 中注明 check 结果，再 push。禁止跳过任何一步。

## 开发流程

1. **建分支** — 从 `master` 创建功能分支：`git checkout -b feature/xxx`
2. **改代码** — 实现功能或修复，不新增游戏功能、不改数值平衡（除非明确要求）
3. **格式化** — `make format`（black + isort）
4. **静态检查** — `make lint`（ruff check）
5. **运行测试** — `make test`（pytest -v）
6. **试玩验证** — `make playtest`（python scripts/playtest.py）
7. **更新文档** — 同步更新 README.md / REPORTS.md / VERSION
8. **质量门** — `make check`（依次执行 format + lint + test + playtest）
9. **提交** — `git commit -m "描述性信息"`
10. **推送** — `git push`
11. **确认 CI** — 确认 GitHub Actions CI 绿色通过

## 禁止项

- **未格式化提交** — 所有代码必须通过 `make format` 后再提交
- **README 与代码不一致** — 版本号、测试数量、功能描述必须与代码实际状态一致
- **playtest 未跑就更新版本** — 任何版本号更新前必须 `make playtest` 验证通过
- **为文档强行改数值** — 文档描述必须以实际代码行为为准，不得反向调整代码迁就文档
- **绕过主流程造假如通过** — 质量门必须真实通过，不得伪造通过记录
