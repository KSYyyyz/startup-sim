# tycoon-action-icon-atlas-v2.2 Slice Guide

用途：给 Godot 集成会话明确每个经营分类、对象操作和状态提示图标的语义、文件、尺寸和推荐用法。

- Atlas: `exports/tycoon-action-icon-atlas-v2.2.png`
- Grid: 8 columns x 3 rows
- Cell: 224x224 px
- 64px icons: `exports/icons_64/`
- 48px icons: `exports/icons_48/`
- Text policy: 图标无烘焙文字；中文、数字、月份、KPI 均由 Godot Label 渲染。
- Cash wording: 使用“现金流可支撑时间”作为现金状态 UI 的唯一推荐中文语义。

| Row | Col | Region | ID | 中文说明 | 64px | 48px | 推荐层级 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=224, h=224 | business_categories-product_room_icon | 研发房间 | `exports/icons_64/product_room_icon.png` | `exports/icons_48/product_room_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“研发房间”图标使用。 |
| 0 | 1 | x=224, y=0, w=224, h=224 | business_categories-sales_room_icon | 销售房间 | `exports/icons_64/sales_room_icon.png` | `exports/icons_48/sales_room_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“销售房间”图标使用。 |
| 0 | 2 | x=448, y=0, w=224, h=224 | business_categories-server_room_icon | 服务器房间 | `exports/icons_64/server_room_icon.png` | `exports/icons_48/server_room_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“服务器房间”图标使用。 |
| 0 | 3 | x=672, y=0, w=224, h=224 | business_categories-recruiting_icon | 招聘 | `exports/icons_64/recruiting_icon.png` | `exports/icons_48/recruiting_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“招聘”图标使用。 |
| 0 | 4 | x=896, y=0, w=224, h=224 | business_categories-training_icon | 培训 | `exports/icons_64/training_icon.png` | `exports/icons_48/training_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“培训”图标使用。 |
| 0 | 5 | x=1120, y=0, w=224, h=224 | business_categories-finance_funding_icon | 财务/融资 | `exports/icons_64/finance_funding_icon.png` | `exports/icons_48/finance_funding_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“财务/融资”图标使用。 |
| 0 | 6 | x=1344, y=0, w=224, h=224 | business_categories-monthly_report_icon | 月报 | `exports/icons_64/monthly_report_icon.png` | `exports/icons_48/monthly_report_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“月报”图标使用。 |
| 0 | 7 | x=1568, y=0, w=224, h=224 | business_categories-stage_goal_icon | 阶段目标 | `exports/icons_64/stage_goal_icon.png` | `exports/icons_48/stage_goal_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“阶段目标”图标使用。 |
| 1 | 0 | x=0, y=224, w=224, h=224 | object_operations-facility_upgrade_icon | 升级设施 | `exports/icons_64/facility_upgrade_icon.png` | `exports/icons_48/facility_upgrade_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“升级设施”图标使用。 |
| 1 | 1 | x=224, y=224, w=224, h=224 | object_operations-facility_sell_icon | 出售设施 | `exports/icons_64/facility_sell_icon.png` | `exports/icons_48/facility_sell_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“出售设施”图标使用。 |
| 1 | 2 | x=448, y=224, w=224, h=224 | object_operations-facility_move_icon | 移动设施 | `exports/icons_64/facility_move_icon.png` | `exports/icons_48/facility_move_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“移动设施”图标使用。 |
| 1 | 3 | x=672, y=224, w=224, h=224 | object_operations-facility_repair_icon | 维修设施 | `exports/icons_64/facility_repair_icon.png` | `exports/icons_48/facility_repair_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“维修设施”图标使用。 |
| 1 | 4 | x=896, y=224, w=224, h=224 | object_operations-pause_usage_icon | 暂停使用 | `exports/icons_64/pause_usage_icon.png` | `exports/icons_48/pause_usage_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“暂停使用”图标使用。 |
| 1 | 5 | x=1120, y=224, w=224, h=224 | object_operations-cost_cutting_icon | 成本削减 | `exports/icons_64/cost_cutting_icon.png` | `exports/icons_48/cost_cutting_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“成本削减”图标使用。 |
| 1 | 6 | x=1344, y=224, w=224, h=224 | object_operations-bridge_funding_icon | 过桥融资 | `exports/icons_64/bridge_funding_icon.png` | `exports/icons_48/bridge_funding_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“过桥融资”图标使用。 |
| 1 | 7 | x=1568, y=224, w=224, h=224 | object_operations-view_detail_icon | 查看详情 | `exports/icons_64/view_detail_icon.png` | `exports/icons_48/view_detail_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“查看详情”图标使用。 |
| 2 | 0 | x=0, y=448, w=224, h=224 | status_hints-cash_support_warning_icon | 现金流可支撑时间预警 | `exports/icons_64/cash_support_warning_icon.png` | `exports/icons_48/cash_support_warning_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“现金流可支撑时间预警”图标使用。 |
| 2 | 1 | x=224, y=448, w=224, h=224 | status_hints-customer_growth_icon | 客户增长 | `exports/icons_64/customer_growth_icon.png` | `exports/icons_48/customer_growth_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“客户增长”图标使用。 |
| 2 | 2 | x=448, y=448, w=224, h=224 | status_hints-revenue_growth_icon | 收入增长 | `exports/icons_64/revenue_growth_icon.png` | `exports/icons_48/revenue_growth_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“收入增长”图标使用。 |
| 2 | 3 | x=672, y=448, w=224, h=224 | status_hints-product_progress_icon | 产品进展 | `exports/icons_64/product_progress_icon.png` | `exports/icons_48/product_progress_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“产品进展”图标使用。 |
| 2 | 4 | x=896, y=448, w=224, h=224 | status_hints-server_stability_icon | 服务器稳定性 | `exports/icons_64/server_stability_icon.png` | `exports/icons_48/server_stability_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“服务器稳定性”图标使用。 |
| 2 | 5 | x=1120, y=448, w=224, h=224 | status_hints-employee_fatigue_icon | 员工疲劳 | `exports/icons_64/employee_fatigue_icon.png` | `exports/icons_48/employee_fatigue_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“员工疲劳”图标使用。 |
| 2 | 6 | x=1344, y=448, w=224, h=224 | status_hints-employee_morale_icon | 员工士气 | `exports/icons_64/employee_morale_icon.png` | `exports/icons_48/employee_morale_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“员工士气”图标使用。 |
| 2 | 7 | x=1568, y=448, w=224, h=224 | status_hints-facility_blocked_icon | 设施阻塞 | `exports/icons_64/facility_blocked_icon.png` | `exports/icons_48/facility_blocked_icon.png` | HudLayer | 在 Startup Sim Godot 桌面版 HUD、对象面板或状态提示中作为“设施阻塞”图标使用。 |
