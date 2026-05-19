# management-panel-detail-ui-atlas-v1.9 Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/management-panel-detail-ui-atlas-v1.9.png`
- Grid: 8 columns x 4 rows
- Cell: 224x224 px
- Individual PNG directory: `exports/ui`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=224, h=224 | detail_panels-employee_detail_panel | 员工详情面板 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“员工详情面板”使用。 |
| 0 | 1 | x=224, y=0, w=224, h=224 | detail_panels-facility_detail_panel | 设施详情面板 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“设施详情面板”使用。 |
| 0 | 2 | x=448, y=0, w=224, h=224 | detail_panels-monthly_report_modal | 月报弹窗 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“月报弹窗”使用。 |
| 0 | 3 | x=672, y=0, w=224, h=224 | detail_panels-recruiting_candidate_card | 候选人卡片 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“候选人卡片”使用。 |
| 0 | 4 | x=896, y=0, w=224, h=224 | detail_panels-upgrade_confirm_modal | 升级确认弹窗 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“升级确认弹窗”使用。 |
| 0 | 5 | x=1120, y=0, w=224, h=224 | detail_panels-objective_milestone_card | 目标里程碑卡 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“目标里程碑卡”使用。 |
| 0 | 6 | x=1344, y=0, w=224, h=224 | detail_panels-compact_tooltip_box | 紧凑提示框 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“紧凑提示框”使用。 |
| 0 | 7 | x=1568, y=0, w=224, h=224 | detail_panels-dark_inspector_header | 深色检查器标题 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“深色检查器标题”使用。 |
| 1 | 0 | x=0, y=224, w=224, h=224 | resource_bars-pressure_bar_frame | 压力条框 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“压力条框”使用。 |
| 1 | 1 | x=224, y=224, w=224, h=224 | resource_bars-efficiency_bar_frame | 效率条框 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“效率条框”使用。 |
| 1 | 2 | x=448, y=224, w=224, h=224 | resource_bars-stability_bar_frame | 稳定性条框 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“稳定性条框”使用。 |
| 1 | 3 | x=672, y=224, w=224, h=224 | resource_bars-product_progress_bar_frame | 产品进度条框 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“产品进度条框”使用。 |
| 1 | 4 | x=896, y=224, w=224, h=224 | resource_bars-cash_runway_meter | 现金流仪表 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“现金流仪表”使用。 |
| 1 | 5 | x=1120, y=224, w=224, h=224 | resource_bars-morale_meter | 士气仪表 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“士气仪表”使用。 |
| 1 | 6 | x=1344, y=224, w=224, h=224 | resource_bars-server_health_meter | 服务器健康仪表 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器健康仪表”使用。 |
| 1 | 7 | x=1568, y=224, w=224, h=224 | resource_bars-recruitment_fit_meter | 招聘匹配仪表 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“招聘匹配仪表”使用。 |
| 2 | 0 | x=0, y=448, w=224, h=224 | action_icons-hire | 招聘 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“招聘”使用。 |
| 2 | 1 | x=224, y=448, w=224, h=224 | action_icons-train | 训练 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“训练”使用。 |
| 2 | 2 | x=448, y=448, w=224, h=224 | action_icons-upgrade | 升级 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“升级”使用。 |
| 2 | 3 | x=672, y=448, w=224, h=224 | action_icons-repair | 维修 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“维修”使用。 |
| 2 | 4 | x=896, y=448, w=224, h=224 | action_icons-sell | 出售 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“出售”使用。 |
| 2 | 5 | x=1120, y=448, w=224, h=224 | action_icons-move | 移动 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“移动”使用。 |
| 2 | 6 | x=1344, y=448, w=224, h=224 | action_icons-pause | 暂停 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“暂停”使用。 |
| 2 | 7 | x=1568, y=448, w=224, h=224 | action_icons-fast_forward | 快进 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“快进”使用。 |
| 3 | 0 | x=0, y=672, w=224, h=224 | small_controls-close_button | 关闭按钮 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“关闭按钮”使用。 |
| 3 | 1 | x=224, y=672, w=224, h=224 | small_controls-expand_button | 展开按钮 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“展开按钮”使用。 |
| 3 | 2 | x=448, y=672, w=224, h=224 | small_controls-collapse_button | 收起按钮 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“收起按钮”使用。 |
| 3 | 3 | x=672, y=672, w=224, h=224 | small_controls-filter_funnel | 筛选漏斗 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“筛选漏斗”使用。 |
| 3 | 4 | x=896, y=672, w=224, h=224 | small_controls-sort_arrows | 排序箭头 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“排序箭头”使用。 |
| 3 | 5 | x=1120, y=672, w=224, h=224 | small_controls-pin_marker | 固定标记 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“固定标记”使用。 |
| 3 | 6 | x=1344, y=672, w=224, h=224 | small_controls-notification_badge | 通知徽章 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“通知徽章”使用。 |
| 3 | 7 | x=1568, y=672, w=224, h=224 | small_controls-corner_bracket | 小型角标框 | HudLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“小型角标框”使用。 |
