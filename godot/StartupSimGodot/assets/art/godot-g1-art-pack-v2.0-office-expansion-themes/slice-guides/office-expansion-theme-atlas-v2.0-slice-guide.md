# office-expansion-theme-atlas-v2.0 Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/office-expansion-theme-atlas-v2.0.png`
- Grid: 8 columns x 5 rows
- Cell: 224x224 px
- Individual PNG directory: `exports/modules`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=224, h=224 | small_startup_office-small_startup_office_floor_patch | 小型创业办公室-地面块 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“小型创业办公室-地面块”使用。 |
| 0 | 1 | x=224, y=0, w=224, h=224 | small_startup_office-small_startup_office_wall_corner | 小型创业办公室-墙角 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“小型创业办公室-墙角”使用。 |
| 0 | 2 | x=448, y=0, w=224, h=224 | small_startup_office-small_startup_office_entrance_shell | 小型创业办公室-入口壳 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“小型创业办公室-入口壳”使用。 |
| 0 | 3 | x=672, y=0, w=224, h=224 | small_startup_office-small_startup_office_window_wall | 小型创业办公室-窗墙 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“小型创业办公室-窗墙”使用。 |
| 0 | 4 | x=896, y=0, w=224, h=224 | small_startup_office-small_startup_office_divider | 小型创业办公室-隔断 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“小型创业办公室-隔断”使用。 |
| 0 | 5 | x=1120, y=0, w=224, h=224 | small_startup_office-small_startup_office_special_corner | 小型创业办公室-特色角落 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“小型创业办公室-特色角落”使用。 |
| 0 | 6 | x=1344, y=0, w=224, h=224 | small_startup_office-small_startup_office_connector_strip | 小型创业办公室-连接条 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“小型创业办公室-连接条”使用。 |
| 0 | 7 | x=1568, y=0, w=224, h=224 | small_startup_office-small_startup_office_transition_tile | 小型创业办公室-过渡块 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“小型创业办公室-过渡块”使用。 |
| 1 | 0 | x=0, y=224, w=224, h=224 | growth_open_office-growth_open_office_floor_patch | 成长期开放办公区-地面块 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“成长期开放办公区-地面块”使用。 |
| 1 | 1 | x=224, y=224, w=224, h=224 | growth_open_office-growth_open_office_wall_corner | 成长期开放办公区-墙角 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“成长期开放办公区-墙角”使用。 |
| 1 | 2 | x=448, y=224, w=224, h=224 | growth_open_office-growth_open_office_entrance_shell | 成长期开放办公区-入口壳 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“成长期开放办公区-入口壳”使用。 |
| 1 | 3 | x=672, y=224, w=224, h=224 | growth_open_office-growth_open_office_window_wall | 成长期开放办公区-窗墙 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“成长期开放办公区-窗墙”使用。 |
| 1 | 4 | x=896, y=224, w=224, h=224 | growth_open_office-growth_open_office_divider | 成长期开放办公区-隔断 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“成长期开放办公区-隔断”使用。 |
| 1 | 5 | x=1120, y=224, w=224, h=224 | growth_open_office-growth_open_office_special_corner | 成长期开放办公区-特色角落 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“成长期开放办公区-特色角落”使用。 |
| 1 | 6 | x=1344, y=224, w=224, h=224 | growth_open_office-growth_open_office_connector_strip | 成长期开放办公区-连接条 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“成长期开放办公区-连接条”使用。 |
| 1 | 7 | x=1568, y=224, w=224, h=224 | growth_open_office-growth_open_office_transition_tile | 成长期开放办公区-过渡块 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“成长期开放办公区-过渡块”使用。 |
| 2 | 0 | x=0, y=448, w=224, h=224 | mature_glass_office-mature_glass_office_floor_patch | 成熟玻璃办公室-地面块 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“成熟玻璃办公室-地面块”使用。 |
| 2 | 1 | x=224, y=448, w=224, h=224 | mature_glass_office-mature_glass_office_wall_corner | 成熟玻璃办公室-墙角 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“成熟玻璃办公室-墙角”使用。 |
| 2 | 2 | x=448, y=448, w=224, h=224 | mature_glass_office-mature_glass_office_entrance_shell | 成熟玻璃办公室-入口壳 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“成熟玻璃办公室-入口壳”使用。 |
| 2 | 3 | x=672, y=448, w=224, h=224 | mature_glass_office-mature_glass_office_window_wall | 成熟玻璃办公室-窗墙 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“成熟玻璃办公室-窗墙”使用。 |
| 2 | 4 | x=896, y=448, w=224, h=224 | mature_glass_office-mature_glass_office_divider | 成熟玻璃办公室-隔断 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“成熟玻璃办公室-隔断”使用。 |
| 2 | 5 | x=1120, y=448, w=224, h=224 | mature_glass_office-mature_glass_office_special_corner | 成熟玻璃办公室-特色角落 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“成熟玻璃办公室-特色角落”使用。 |
| 2 | 6 | x=1344, y=448, w=224, h=224 | mature_glass_office-mature_glass_office_connector_strip | 成熟玻璃办公室-连接条 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“成熟玻璃办公室-连接条”使用。 |
| 2 | 7 | x=1568, y=448, w=224, h=224 | mature_glass_office-mature_glass_office_transition_tile | 成熟玻璃办公室-过渡块 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“成熟玻璃办公室-过渡块”使用。 |
| 3 | 0 | x=0, y=672, w=224, h=224 | server_room-server_room_floor_patch | 服务器房-地面块 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器房-地面块”使用。 |
| 3 | 1 | x=224, y=672, w=224, h=224 | server_room-server_room_wall_corner | 服务器房-墙角 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器房-墙角”使用。 |
| 3 | 2 | x=448, y=672, w=224, h=224 | server_room-server_room_entrance_shell | 服务器房-入口壳 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器房-入口壳”使用。 |
| 3 | 3 | x=672, y=672, w=224, h=224 | server_room-server_room_window_wall | 服务器房-窗墙 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器房-窗墙”使用。 |
| 3 | 4 | x=896, y=672, w=224, h=224 | server_room-server_room_divider | 服务器房-隔断 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器房-隔断”使用。 |
| 3 | 5 | x=1120, y=672, w=224, h=224 | server_room-server_room_special_corner | 服务器房-特色角落 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器房-特色角落”使用。 |
| 3 | 6 | x=1344, y=672, w=224, h=224 | server_room-server_room_connector_strip | 服务器房-连接条 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器房-连接条”使用。 |
| 3 | 7 | x=1568, y=672, w=224, h=224 | server_room-server_room_transition_tile | 服务器房-过渡块 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器房-过渡块”使用。 |
| 4 | 0 | x=0, y=896, w=224, h=224 | meeting_rest_front-meeting_rest_front_floor_patch | 会议休息前台-地面块 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“会议休息前台-地面块”使用。 |
| 4 | 1 | x=224, y=896, w=224, h=224 | meeting_rest_front-meeting_rest_front_wall_corner | 会议休息前台-墙角 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议休息前台-墙角”使用。 |
| 4 | 2 | x=448, y=896, w=224, h=224 | meeting_rest_front-meeting_rest_front_entrance_shell | 会议休息前台-入口壳 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议休息前台-入口壳”使用。 |
| 4 | 3 | x=672, y=896, w=224, h=224 | meeting_rest_front-meeting_rest_front_window_wall | 会议休息前台-窗墙 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议休息前台-窗墙”使用。 |
| 4 | 4 | x=896, y=896, w=224, h=224 | meeting_rest_front-meeting_rest_front_divider | 会议休息前台-隔断 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“会议休息前台-隔断”使用。 |
| 4 | 5 | x=1120, y=896, w=224, h=224 | meeting_rest_front-meeting_rest_front_special_corner | 会议休息前台-特色角落 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“会议休息前台-特色角落”使用。 |
| 4 | 6 | x=1344, y=896, w=224, h=224 | meeting_rest_front-meeting_rest_front_connector_strip | 会议休息前台-连接条 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“会议休息前台-连接条”使用。 |
| 4 | 7 | x=1568, y=896, w=224, h=224 | meeting_rest_front-meeting_rest_front_transition_tile | 会议休息前台-过渡块 | ShellLayer | bottom_center | 1x1 | 1x1 | 在 Startup Sim 2.5D Godot 表现层中作为“会议休息前台-过渡块”使用。 |
