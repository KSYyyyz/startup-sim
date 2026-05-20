# Godot 插件接入说明

本文记录当前 Godot 桌面前端可用的第三方插件，以及它们在项目中的使用边界。

## 核心边界

- C# Core 是规则核心。
- Godot 插件只负责表现层、交互层、编辑器效率和测试辅助。
- 插件不得复制经营规则、结算公式、阶段目标判定或结局判定。
- 插件产生的选择、对话、镜头和测试结果必须通过现有控制器调用 C# Core 或展示 C# Core 的结果。

## 已纳入插件

### Phantom Camera 0.11.0.2

来源：https://github.com/ramokz/phantom-camera

用途：

- 办公室镜头平移、缩放和聚焦。
- 选中房间、设施、员工时的镜头反馈。
- 月报、事件和阶段目标触发时的轻量镜头转场。

当前状态：

- 已 vendored 到 `godot/StartupSimGodot/addons/phantom_camera/`。
- 当前主场景还没有接入镜头控制，后续应先补 `Camera2D` 与办公室视图边界，再启用插件行为。

### Dialogue Manager 3.10.4

来源：https://github.com/nathanhoad/godot_dialogue_manager

用途：

- 新手引导、顾问提示、阶段目标解释。
- 月报旁白和经营事件的文本展示。
- 只展示经营状态，不决定经营结果。

当前状态：

- 已 vendored 到 `godot/StartupSimGodot/addons/dialogue_manager/`。
- 后续第一步建议只做 3 条开局顾问提示，确认不会干扰办公室点击和月结体验。

### GdUnit4 6.1.3

来源：https://github.com/godot-gdunit-labs/gdUnit4

用途：

- Godot 场景级 UI 回归测试。
- 覆盖 MCP 试玩发现的高风险问题，例如切换菜单时隐藏建造态、HUD 不阻塞办公室点击、月报不自动打断。
- 作为 Python 文本测试和 MCP 真实试玩之间的补充。

当前状态：

- 已 vendored 到 `godot/StartupSimGodot/addons/gdUnit4/`。
- 暂不把 GdUnit4 测试接入 CI，先保留为本地 Godot 场景测试候选，避免一次性扩大 CI 风险。

## 后续接入顺序

1. 先用 Phantom Camera 做办公室镜头聚焦 spike。
2. 再用 Dialogue Manager 做开局顾问提示 spike。
3. 最后用 GdUnit4 把已复现的 Godot UI 交互 bug 固化成场景测试。

每一步都需要单独本地验证、提交、推送并检查 GitHub Actions。
