# Startup Sim 工作目录规则

1. 本项目唯一工作根目录为：`D:\Startup-sim`
2. 所有后续项目相关文件必须保存在 `D:\Startup-sim` 或其子目录中。
3. 临时工作文件放入：`D:\Startup-sim\.work`
4. 测试报告和运行结果放入：`D:\Startup-sim\reports\test-runs`
5. 项目文档放入：`D:\Startup-sim\docs`
6. 图片、截图、素材放入：`D:\Startup-sim\assets`
7. 不允许把 startup-sim 相关文件保存到桌面、下载目录、C 盘临时目录或其他项目目录。
8. 每次开始处理 startup-sim 前，先确认当前目录是 `D:\Startup-sim`。
9. 如果需要创建新文件，先判断它属于源码、文档、报告、测试输出、素材还是临时文件，再放入对应目录。
10. 不允许在未经确认的情况下删除旧项目目录。

当前本地与云端布局标准见 `docs/project_layout.md`。

## 双 Agent 并行工作流

后续项目推进采用“Godot/美术 Agent + 后端/规则 Agent + 共同合同层”的协作方式。

### 角色分工

1. Godot/美术 Agent
   - 负责 `godot/StartupSimGodot/`、`design-assets/`、Godot 体验文档。
   - 负责办公室主场景、行动卡、布局降噪、image-2 资源库、角色头像/房间/事件气泡、Godot 桌面体验。
   - 不允许自行发明现金、用户、产品分、估值、股权等结算逻辑。
   - 不允许把新玩法规则写死在 Godot 节点脚本里；新增玩法内容必须优先进入玩法数据、C# Core 或合同层。

2. 后端/规则 Agent
   - 负责 `src/`、`tests/`、API 合同文档、规则一致性。
   - 负责 TurnEngine、StateGuard、ActionPlan、TurnFacts、RoleMemory、OfficeSignal、董事会、竞品、客户、事件系统。
   - 不负责前端排版和美术表现。
   - 不输出面向 UI 的大段布局文案；后端只提供事实、规则结果和可展示的短文本。

3. 共同合同层
   - `ActionPlan`：玩家准备执行什么。
   - `TurnFacts`：本回合实际发生了什么。
   - `RoleMemory`：角色根据历史事实记住什么。
   - `OfficeSignal`：办公室应该显示什么信号。
   - `ScenarioDefinition`：剧本、房间、角色、竞品和初始条件。
   - `AssetManifest`：美术资源如何被引用和复用。
   - `StartupSim.Core`：未来 Godot 可复用的纯 C# 规则核心，不允许依赖任何表现层引擎。

### 协作规则

1. 后端/规则 Agent 优先定义或扩展合同，Godot/美术 Agent 根据合同展示。
2. 表现层不得修改合同字段语义；如需新增字段，先写入合同文档并补测试。
3. 后端不得把展示结构写进规则层；规则层输出事实，展示层决定表现。
4. 两个 Agent 可以并行审计和设计，但代码修改必须保持写入范围清晰，避免同时改同一文件。
5. 每轮有效修改必须测试、commit、push。
6. 任何新系统上线前必须回答：
   - 是否带来有趣选择；
   - 玩家是否能在 10 秒内理解；
   - 是否能产生可复盘故事；
   - 是否保持未来 Godot 桌面分发的迁移空间。

## C# / Godot 迁移规则

1. `csharp/StartupSim.Core` 是底层规则迁移目标，必须保持纯 C#，不引用 Godot 或 Unity 引擎 API。
2. `godot/StartupSimGodot` 是新的独立游戏表现层工程。
3. Godot 组件可以准备行动、展示行动、提交回合，但不能结算现金、产品、用户、估值、股权或结局。
4. Python 当前逻辑仍是参考实现，C# 迁移必须通过黄金测试逐步对齐。
5. Web 前端停止作为最终产品外壳大规模打磨，只保留规则验证台和在线试玩价值。
6. Unity 路线停止作为新增开发目标；后续新增工程、场景、交互原型和桌面分发路线都以 Godot 为准。
