# Startup Sim 项目布局

Status: active layout standard
Date: 2026-05-18

## 1. 根目录

唯一工作目录：

```text
D:\Startup-sim
```

所有本地开发、验证、提交和推送都在这个目录下完成。旧 C 盘工作副本、桌面临时文件和下载目录都不作为项目来源。

## 2. 当前有效目录

```text
csharp/                         Godot 可复用的 C# 规则核心
  StartupSim.Core/
  StartupSim.Core.Tests/
  golden-cases/

godot/
  StartupSimGodot/              Godot 4.6.x .NET 独立游戏表现层

src/                            Python 完整规则参考实现和当前 CLI/API 规则来源
tests/                          Python 回归测试

frontend/                       Web 规则验证台，不是最终产品外壳
design-assets/                  image-2 资产 prompt、规格和复用库
assets/                         项目静态素材
data/                           剧本、配置和未来内容数据
docs/                           当前有效项目文档
reports/                        测试报告和人工验证记录
scripts/                        本地检查、playtest、后续 Godot CLI 包装脚本
```

## 3. 已停止新增开发的内容

以下内容不再保留为仓库主线：

- `unity/`：旧 Unity 探索适配代码已删除。
- 旧 `frontend_alpha_*` 计划文档：核心结论已收口到 `docs/web_validation_bench.md`。
- 旧 C# / Unity 迁移文档：核心结论已收口到 `docs/csharp_core_migration_plan.md`。
- 旧 WIP 计划目录：后续以当前 Godot/C# 文档为准。
- 旧 Word 版前端方案：已被当前 Markdown 文档替代。

## 4. 云端布局要求

GitHub 仓库应只展示当前有效路线：

1. README 的快速导航必须指向 Godot、C# Core、Web 规则验证台和产品方向文档。
2. CI 必须同时验证 Python 规则参考、C# Core 测试、Godot C# build 和文档一致性。
3. 不允许重新加入 Unity 主线文件。
4. Web/Vercel 文件可以保留，但只能作为规则验证台和远程试玩入口。

## 5. 删除判断

删除代码或文档前必须满足：

1. 当前 Godot/C# 主线不依赖它。
2. CI、测试、文档一致性检查不依赖它。
3. 核心内容已经迁入当前文档或测试。
4. 删除后本地验证和 GitHub CI 都通过。
