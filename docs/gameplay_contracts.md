# Startup Sim 玩法合同

状态：Godot 合同基线
日期：2026-05-18

本文定义 Godot 表现层与规则层之间共享的数据合同。

## 原则

规则层拥有事实，Godot 拥有表现。合同层只描述二者之间可以传递的数据。

## 合同列表

| 合同 | 归属 | 用途 |
| --- | --- | --- |
| `ActionPlan` | 共享 | 确定性结算前，玩家准备执行的行动。 |
| `TurnFacts` | 规则层 | 确定性结算后实际发生的事实。 |
| `RoleMemory` | 规则层 | 从历史事实派生出的角色记忆。 |
| `OfficeSignal` | 共享 | Godot 可渲染成房间动画、角色气泡或图标的办公室信号。 |
| `StoryEvent` | 规则层 | 从规则事件、竞品和经营洞察中派生出的短事件。 |
| `PhaseGoal` | 规则层 | 当前阶段目标、方向标签和风险提示。 |
| `ObjectiveUpdate` | 规则层 | 结算后阶段目标的进度变化。 |
| `ScenarioDefinition` | 共享 | 剧本、房间、角色、竞品和市场背景。 |
| `CompanyGoal` | 规则层 | 公司经营目标、收益目标和成就进度。 |
| `EmployeeState` | 共享 | 员工能力、职位、特性、疲劳、情绪、健康和需求状态。 |
| `TimeControlState` | Godot | 暂停、正常速度、二倍速、三倍速等时间控制状态。 |
| `AssetManifest` | Godot / 美术 | image-2 视觉资产和稳定引用。 |

## 必须遵守的边界

- Godot 可以准备行动、展示预览、提交经营意图。
- Godot 不得结算现金、用户、产品分、估值、股权、董事会状态、竞品状态或结局。
- C# Core 保持纯规则代码，不依赖 Godot API。
- Python 在 C# Core 对齐完成前继续作为完整参考实现。
- 新合同字段必须先补测试和文档，再让 Godot UI 依赖。
- 公司经营收益和成就是主线，办公室、设施和员工系统是支撑主线的输入。

## ActionPlan

`ActionPlan` 描述结算前的玩家行动。

必填字段：

- `id`
- `source`
- `sourceLabel`
- `title`
- `command`
- `readableIntent`
- `tradeoffs`
- `authority`

`authority` 字段必须是 `backend-turn-engine` 或 `csharp-core`。表现层的 `ActionPlan` 可以解释意图和取舍，但不能结算数值状态。

## TurnFacts

`TurnFacts` 描述结算后实际发生了什么。

必填字段：

- `month`
- `command`
- `changes`
- `replay_basis`
- `next_pressure`
- `authority`

`changes` 应包含来自已结算状态的指标事实、短标签和值。`replay_basis` 应引用确定性复盘事实。`next_pressure` 应来自结算后的规则输出。

## RoleMemory

`RoleMemory` 描述角色从已结算事实中记住什么。

必填字段：

- `role_id`
- `role_name`
- `month`
- `fact`
- `implication`
- `source`

`source` 字段必须是 `settled-turn-facts`。角色记忆不能来自悬停状态、未发送命令或推测性预览。

## OfficeSignal

`OfficeSignal` 描述 Godot 可渲染的办公室信号。

必填字段：

- `id`
- `room_id`
- `title`
- `description`
- `severity`
- `source`
- `visual_intent`

`visual_intent` 当前为 `surface-in-office`。Godot 可以把它渲染成房间动画、角色气泡或图标。Godot 不应从原始文本反推出业务规则。

## EmployeeState

`EmployeeState` 描述一个员工在时间推进中的当前状态。

必填字段：

- `employee_id`
- `name`
- `role`
- `skills`
- `specialties`
- `traits_positive`
- `traits_negative`
- `assigned_zone_id`
- `fatigue`
- `mood`
- `health`
- `needs`
- `current_activity`

`current_activity` 可以是工作、休息、娱乐、上厕所、请病假或空闲。员工状态会影响部门产能，但产能结算必须由规则层完成。

## TimeControlState

`TimeControlState` 描述 Godot 当前时间速度。

必填字段：

- `mode`
- `speed_multiplier`
- `is_paused`

允许模式：

- 暂停：`speed_multiplier = 0`
- 正常速度：`speed_multiplier = 1`
- 二倍速：`speed_multiplier = 2`
- 三倍速：`speed_multiplier = 3`

时间控制只影响推进速度，不得绕过规则层结算。

## StoryEvent

`StoryEvent` 描述月报和未来局后回放使用的紧凑事件。

必填字段：

- `id`
- `title`
- `description`
- `tone`
- `source`

`source` 字段必须是 `rule-event`、`competitor-fact` 或 `business-insight` 之一。故事事件不能修改指标、推进时间或引入已结算事实中不存在的结果。

## PhaseGoal

`PhaseGoal` 描述阶段目标和面向玩家的方向。

必填字段：

- `phase_label`
- `title`
- `summary`
- `objectives`

每个目标可包含 `id`、`title`、`status`、`progress_label`、`action_directions` 和 `risk_hint`。目标系统可以引导玩家思考，但不能包含一键执行元数据。

## ObjectiveUpdate

`ObjectiveUpdate` 描述结算结果如何影响阶段目标。

必填字段：

- `id`
- `title`
- `status`
- `summary`

它只能在结算后根据回合事实和回合后状态派生，不能推荐或执行下一步行动。

## 版本

当前兼容合同族为 `godot-contracts.g1`。
