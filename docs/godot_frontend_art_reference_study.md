# Godot 前端美术表现参考研究

状态：当前美术与表现层落地参考
日期：2026-05-19
适用范围：`godot/StartupSimGodot` 的办公室主场景、美术资源制作、后续 Godot 接入

本文件基于项目已有 `docs/reference_game_analysis.md`、`docs/startup_sim_development_plan.md`、
`docs/godot_migration_plan.md` 和当前 Godot 场景/脚本状态补充整理，重点回答：
这些参考游戏的“前端美术表现”应该怎样转化成 Startup Sim 自己的 Godot 分层表现与资源优先级。

更具体的“疯狂游戏大亨式斜俯视 / 伪 3D 轻像素”方向、页面布局、数值展示和 v1.1+
资源缺口，见 `docs/godot_pseudo3d_frontend_art_optimization.md`。

## 1. 参考游戏学到的表现重点

本研究只吸收工程组织和视觉表达经验，不复制任何参考游戏的玩法、素材、UI 或代码。

### Mad Games Tycoon 2

可借鉴点：
- 办公室不是背景板，而是主要操作面。办公室、生产设施、服务器房和员工增长共同表达公司扩张。
- 设施和房间需要明显承担业务含义，玩家看到摆放结构就能理解公司当前能力短板。
- 从小车库到大公司的成长要通过空间密度、设施等级、员工规模和办公环境变化可视化。

对 Startup Sim 的落地：
- 主场景必须持续可读：地板、区域、设施、员工、状态反馈应分层显示。
- 设施状态资源优先级高于装饰大图，例如 idle、active、upgrading、blocked、high_efficiency。
- 公司扩张感先通过可摆放格子、区域边界、设施等级和员工活动体现，不急着做大规模建筑外观。

### Big Ambitions

可借鉴点：
- 商业经营的可信感来自“空间配置 + 设施 + 员工 + 基础设施”一起出现。
- 装修、家具和总部不是纯装饰，它们支持员工、经理、物流、采购等业务系统。
- 生活模拟和城市尺度很强，但 Startup Sim 当前不应照搬 3D 城市自由行动。

对 Startup Sim 的落地：
- Godot 主场景重点是 top-down 办公室，不扩到城市街区。
- 办公室背景要给“公司主场景”氛围，但交互资产仍应以透明 PNG 设施、员工、图标为主。
- 每一批新资源都要能回答：它服务哪个业务信号？它会挂在哪个节点或哪类 atlas cell？

### Game Dev Tycoon

可借鉴点：
- 轻量循环的优势是阶段清楚：小办公室开始，研究技术，搬进更大办公室，招募和训练团队。
- 复杂经营结论通过报告、事件和短反馈解释，而不是全部压在主界面数值上。
- 员工成长、项目反馈和办公室变化共同讲述公司成长。

对 Startup Sim 的落地：
- 月报、反馈气泡、短 FX 和员工状态图标必须进入表现层，不能只做静态办公室。
- UI 文本由 Godot `Label` / `RichTextLabel` 渲染，关键中文不烘焙进图片。
- 美术资源应优先补“经营动作的视觉反馈”，例如培训、压力、低效、升级中、产出提升。

### Game Dev Story / Kairosoft 系经营表达

可借鉴点：
- 员工是核心可视对象：不同能力、训练、职业和成长要能在小空间里被玩家感知。
- 小尺寸角色和图标也能承载强反馈，关键是轮廓、姿态、表情和状态差异清楚。
- 办公室升级和人员容量变化要被视觉化。

对 Startup Sim 的落地：
- 后续员工素材不能只有同脸、同朝向、同职业制服；年龄、脸型、发型、服饰、表情和朝向要继续拉开。
- 员工活动资源优先于大头像：working、rest、entertainment、sick、training、pressure、idle walk。
- 小图标要保持透明背景、强轮廓、少文字，避免缩到 32-48px 后不可读。

### STONKS-9800

可借鉴点：
- 强文本/数据经营也可以靠克制的视觉风格、节奏感和事件反馈形成记忆点。
- 本地化和数据驱动内容很重要，表现层不能把核心文案写死进图片。

对 Startup Sim 的落地：
- 经营洞察、董事会反馈、竞品事件、客户反馈应由数据驱动，Godot 只负责展示。
- 视觉上可以保留“创业经营压力”的冷静感，但不要退回文本列表游戏。

## 2. Godot 表现层建议架构

当前 `scenes/main.tscn` 已经具备可延展骨架：
- `OfficeBackdrop`：主场景背景图，当前接入 v0.7.1。
- `OfficeGridView`：自绘办公室网格、地板、区域覆盖、设施、员工、状态图标。
- `G2OperationsPanel`：右侧 Godot Control UI 面板。
- `MonthlyReportController`、`TimeProgressController`、`FacilityPlacementController`、`EmployeeManagementController` 等负责表现层交互。

短期建议保留这个结构，不做大重构。表现层按下面顺序分层：

1. 背景层
   使用 v0.7.1 公司主场景背景作为空间氛围，不承担点击语义。

2. 地板与办公室格子层
   继续用 `OfficeGridView` 自绘完成当前原型；当地图扩大或 tile 种类明显增加时，再迁移到 `TileMapLayer` + `TileSet`。Godot 4.6 官方建议 tilemap 用 TileMapLayer/TileSet 承载网格地图，适合后续大地图与碰撞/遮挡/导航。

3. 区域覆盖层
   区域状态使用透明 overlay atlas，颜色和纹理只表达部门归属、选中、阻塞、容量紧张，不写死中文。

4. 设施层
   设施视觉不只按类型选图，还要按状态选图。建议新增表现键：
   `facility_type_id + visual_state`，例如 `basic_desk.active`、`starter_server_rack.blocked`。

5. 员工层
   员工视觉不只按 role 选图，还要按活动状态选图。建议新增表现键：
   `role_id + current_activity + direction`。短期可用 `Sprite2D`/atlas region，下一步改成 `AnimatedSprite2D` 或 `AnimationPlayer` 播放活动动画。

6. 状态图标与业务反馈 FX 层
   v0.8 的透明图标适合短时浮层：收入、效率、风险、客户、董事会、现金流、压力等。图标由 Godot 控制出现、淡出、飘移，不把数值和文案烘焙进 PNG。

7. HUD / 面板层
   使用 `CanvasLayer` + `Control` 系节点固定在屏幕空间。按钮、标签、月报、招聘、设施详情和员工详情都用 Godot UI 文本渲染，图片只做图标、头像、边框纹理。

8. 轻量氛围层
   等主循环稳定后再加 `CanvasModulate`、`PointLight2D`、窗光、屏幕微光、升级闪光等。Godot 4.6 的 2D lights/shadows 支持增强深度，但不应早于主场景可读性。

## 3. 美术资源制作规则

### 透明图标规则

- 可交互图标、状态图标、设施状态、员工活动、FX 必须是 RGBA 透明 PNG。
- 四角 alpha 应为 0，避免出现黑/白底。
- atlas 之外也要导出 individual icons，方便 Godot 直接接入 `TextureRect`、`Sprite2D` 或临时 FX。

### 角色差异规则

- 后续员工角色必须拉开年龄、脸型、发型、服饰、饰品、表情、体型和朝向。
- 同一角色的活动状态可以保持身份一致，但姿态必须明显变化。
- 方向不能全往右看；至少准备 down/right/up/left 或 down-left/down-right/up-left/up-right 的可替代方案。

### 主场景规则

- 大背景只负责氛围和边界感，不承担设施和员工状态。
- 设施、员工、区域、反馈必须是独立透明层，便于 Godot 动态显示。
- 不做纯展示型大立绘堆叠，优先做办公室原型用得上的小尺寸可读素材。

### UI 规则

- 关键中文、数值、月份、指标名由 Godot 文本渲染。
- 图标只表达概念，不带难以本地化的文字。
- UI atlas 可提供按钮底、面板边、标签底、选中态、禁用态，但不要把完整面板文本画进图。

## 4. 后续 Godot 接入建议

这些是给另一个接入会话的实现提示，美术会话只需要按此提供资源。

### OfficeGridView 短期增强

- 增加 `FacilityVisualState`，让设施从 v0.9 选择状态图。
- 增加 `EmployeeActivityState`，让员工从 v1.0 选择活动图。
- 增加 `FeedbackFxQueue`，按 `OfficeSignal.visual_intent` 在格子上方生成 v0.8 图标。
- 把 atlas 坐标映射从硬编码 switch 逐步移到 manifest/JSON。

### 节点层级建议

```text
StartupSimMain
  OfficeBackdrop (TextureRect)
  OfficeWorld (Node2D)
    FloorLayer / OfficeGridView
    ZoneOverlayLayer
    FacilityLayer
    EmployeeLayer
    FeedbackFxLayer
  HudLayer (CanvasLayer)
    G2OperationsPanel
    MonthlyReportPanel
    EmployeeDetailPanel
    FacilityDetailPanel
```

当前可以继续把多层画在 `OfficeGridView._Draw()` 里；当动画和节点交互增多，再拆出独立 `Node2D` 子层。

### TileMapLayer 迁移时机

现在不用急着迁移。满足任一条件再迁移：
- 地图超过当前 12x8，需要更大办公室或滚动镜头。
- floor/wall/decor tile 超过 30 个，且需要编辑器中手工铺图。
- 需要 tile collision、occlusion、navigation 或 terrain transitions。

## 5. 下一批美术优先级

### P0：Godot 主场景可读性

- v1.1 办公室主场景 overlay/detail pack：墙角、门、窗、地毯、线缆、工位阴影、桌面小物。
- v1.2 设施 2x1 / 1x2 大尺寸版本：白板、会议桌、服务器架、休息区、电话销售位。
- v1.3 员工 4 向活动小动画：working、walking、rest、training、pressure。

### P1：经营反馈表现

- v1.4 OfficeSignal FX：董事会、客户反馈、竞品、现金流、事故、增长、风险。
- v1.5 月报视觉资源：面板底、趋势箭头、事件卡图标、阶段目标徽章。

### P2：长期风格增强

- v1.6 公司阶段变化背景：车库、小办公室、成长型办公室、成熟总部。
- v1.7 部门主题装饰：研发、销售、服务器、会议、招聘、休息区。

## 6. 验收清单

每批资源完成后必须检查：
- 文件存在数量与 `asset-index.json` 一致。
- 所有导出 PNG 为 RGBA。
- 透明资源四角 alpha 为 0。
- atlas cell 尺寸能被列数和行数整除。
- individual icons 与 atlas 对应语义一致。
- 备份路径 `D:\美术资源\startup-sim\...` 与体内路径 hash 一致。
- `pytest tests/test_design_assets.py -q` 通过。
- `git diff --check` 通过。

## 7. 参考来源

- Mad Games Tycoon 2 Steam: https://store.steampowered.com/app/1342330/Mad_Games_Tycoon_2/
- Big Ambitions Steam: https://store.steampowered.com/app/1331550/Big_Ambitions/
- Game Dev Tycoon Steam: https://store.steampowered.com/app/239820/Game_Dev_Tycoon/
- STONKS-9800 Steam: https://store.steampowered.com/app/1539140/STONKS9800_Stock_Market_Simulator/
- Game Dev Story App Store / Kairosoft listing: https://apps.apple.com/us/app/game-dev-story/id396085661
- Godot 4.6 TileSets / TileMapLayer: https://docs.godotengine.org/en/4.6/tutorials/2d/using_tilesets.html
- Godot 4.6 2D sprite animation: https://docs.godotengine.org/en/4.6/tutorials/2d/2d_sprite_animation.html
- Godot 4.6 Canvas layers: https://docs.godotengine.org/en/4.6/tutorials/2d/canvas_layers.html
- Godot 4.6 UI: https://docs.godotengine.org/en/4.6/tutorials/ui/
- Godot 4.6 2D lights and shadows: https://docs.godotengine.org/en/4.6/tutorials/2d/2d_lights_and_shadows.html
