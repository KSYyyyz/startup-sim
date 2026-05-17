# Alpha 版本推进清单

## 代码检查

- [ ] 所有新代码通过 `make format`（black + isort）
- [ ] 所有新代码通过 `make lint`（ruff check，无新增 error）
- [ ] 新增模块有对应的测试文件
- [ ] 测试覆盖新功能的正常路径和边界情况
- [ ] 无硬编码魔法数字（使用常量或配置）

## 工程质量

- [ ] `make test` 全部通过，测试数量有增无减
- [ ] `make playtest` 五种策略正常运行，结局分布合理
- [ ] `make docs-check` 文档一致性检查通过
- [ ] `make check` 整体通过
- [ ] 无新增 `print()` 调试语句遗留
- [ ] 导入顺序正确（标准库 → 第三方 → 项目内部）

## 文档一致性检查

- [ ] VERSION 与 README 标题一致
- [ ] README 当前版本号正确
- [ ] README 功能列表与代码实际接入一致
- [ ] REPORTS.md 已记录本版本真实 pytest 结果
- [ ] REPORTS.md 已记录本版本真实 playtest 结果
- [ ] REPORTS.md 顶部"当前路线"指向最新版本
- [ ] 数量类描述已用代码/命令验证，不手写猜测
- [ ] 旧文案已 grep 检查无残留
- [ ] README / REPORTS 中没有与当前版本矛盾的历史表述
- [ ] 如果存在随机性结果，已区分"稳定结果"和"偶发结果"

建议检查命令：
```
grep -n "Alpha 1.5\\|Alpha 1.4\\|25个事件\\|中性类5个\\|纯研发会破产" README.md REPORTS.md
```
> 注意：grep 关键词以后可以按版本实际情况调整。

## 验收

- [ ] playtest 策略对比结果无退化
- [ ] 不新增游戏功能（除非版本计划明确要求）
- [ ] 不改变数值平衡（除非有参数调优记录）
- [ ] GitHub Actions CI 绿色通过（含 docs-check）
- [ ] 不接 LLM / 不做 Web / 不新增外部依赖（除非计划允许）
