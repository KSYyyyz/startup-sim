# build-upgrade-feedback-fx-atlas-v1.8 Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/build-upgrade-feedback-fx-atlas-v1.8.png`
- Grid: 8 columns x 4 rows
- Cell: 224x224 px
- Individual PNG directory: `exports/fx`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=224, h=224 | construction_frames-blueprint_base | 蓝图底座 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“蓝图底座”使用。 |
| 0 | 1 | x=224, y=0, w=224, h=224 | construction_frames-cones_tools | 施工锥与工具 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“施工锥与工具”使用。 |
| 0 | 2 | x=448, y=0, w=224, h=224 | construction_frames-half_built_structure | 半成品结构 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“半成品结构”使用。 |
| 0 | 3 | x=672, y=0, w=224, h=224 | construction_frames-nearly_done_sparkle | 接近完成闪光 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“接近完成闪光”使用。 |
| 0 | 4 | x=896, y=0, w=224, h=224 | construction_frames-tool_swing | 工具挥动 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“工具挥动”使用。 |
| 0 | 5 | x=1120, y=0, w=224, h=224 | construction_frames-material_crate | 材料箱 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“材料箱”使用。 |
| 0 | 6 | x=1344, y=0, w=224, h=224 | construction_frames-work_light_glow | 施工灯光 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“施工灯光”使用。 |
| 0 | 7 | x=1568, y=0, w=224, h=224 | construction_frames-completion_pop | 完成弹光 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“完成弹光”使用。 |
| 1 | 0 | x=0, y=224, w=224, h=224 | upgrade_effects-upgrade_ring_small | 小升级环 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“小升级环”使用。 |
| 1 | 1 | x=224, y=224, w=224, h=224 | upgrade_effects-upgrade_ring_medium | 中升级环 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“中升级环”使用。 |
| 1 | 2 | x=448, y=224, w=224, h=224 | upgrade_effects-upgrade_ring_bright | 亮升级环 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“亮升级环”使用。 |
| 1 | 3 | x=672, y=224, w=224, h=224 | upgrade_effects-upgrade_ring_burst | 升级爆发环 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“升级爆发环”使用。 |
| 1 | 4 | x=896, y=224, w=224, h=224 | upgrade_effects-gear_spin | 齿轮旋转 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“齿轮旋转”使用。 |
| 1 | 5 | x=1120, y=224, w=224, h=224 | upgrade_effects-upward_arrows | 上升箭头 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“上升箭头”使用。 |
| 1 | 6 | x=1344, y=224, w=224, h=224 | upgrade_effects-polish_sparkle | 抛光闪光 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“抛光闪光”使用。 |
| 1 | 7 | x=1568, y=224, w=224, h=224 | upgrade_effects-upgrade_complete | 升级完成 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“升级完成”使用。 |
| 2 | 0 | x=0, y=448, w=224, h=224 | repair_malfunction-small_smoke | 小烟雾 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“小烟雾”使用。 |
| 2 | 1 | x=224, y=448, w=224, h=224 | repair_malfunction-big_smoke | 大烟雾 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“大烟雾”使用。 |
| 2 | 2 | x=448, y=448, w=224, h=224 | repair_malfunction-sparks | 火花 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“火花”使用。 |
| 2 | 3 | x=672, y=448, w=224, h=224 | repair_malfunction-warning_crackle | 警告电弧 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“警告电弧”使用。 |
| 2 | 4 | x=896, y=448, w=224, h=224 | repair_malfunction-wrench_repair | 扳手维修 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“扳手维修”使用。 |
| 2 | 5 | x=1120, y=448, w=224, h=224 | repair_malfunction-patch_panel | 补丁面板 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“补丁面板”使用。 |
| 2 | 6 | x=1344, y=448, w=224, h=224 | repair_malfunction-cooling_fan | 冷却风扇 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“冷却风扇”使用。 |
| 2 | 7 | x=1568, y=448, w=224, h=224 | repair_malfunction-repaired_glow | 修复完成光 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“修复完成光”使用。 |
| 3 | 0 | x=0, y=672, w=224, h=224 | placement_monthly-placement_valid_pulse | 可放置脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“可放置脉冲”使用。 |
| 3 | 1 | x=224, y=672, w=224, h=224 | placement_monthly-placement_invalid_pulse | 不可放置脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“不可放置脉冲”使用。 |
| 3 | 2 | x=448, y=672, w=224, h=224 | placement_monthly-selected_cell_pulse | 选中格脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“选中格脉冲”使用。 |
| 3 | 3 | x=672, y=672, w=224, h=224 | placement_monthly-move_ghost_marker | 移动虚影标记 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“移动虚影标记”使用。 |
| 3 | 4 | x=896, y=672, w=224, h=224 | placement_monthly-cash_gain_burst | 现金收益爆发 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“现金收益爆发”使用。 |
| 3 | 5 | x=1120, y=672, w=224, h=224 | placement_monthly-cash_loss_burst | 现金损失爆发 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“现金损失爆发”使用。 |
| 3 | 6 | x=1344, y=672, w=224, h=224 | placement_monthly-risk_burst | 风险爆发 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“风险爆发”使用。 |
| 3 | 7 | x=1568, y=672, w=224, h=224 | placement_monthly-objective_complete_burst | 目标完成爆发 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“目标完成爆发”使用。 |
