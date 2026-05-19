# pseudo3d-office-structure-atlas-v1.1b Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/pseudo3d-office-structure-atlas-v1.1b.png`
- Grid: 8 columns x 4 rows
- Cell: 222x222 px
- Individual PNG directory: `exports/tiles`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=222, h=222 | diamond_floor_modules-neutral_diamond_floor_tile | 中性菱形地砖 | FloorLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“中性菱形地砖”使用。 |
| 0 | 1 | x=222, y=0, w=222, h=222 | diamond_floor_modules-alternate_diamond_floor_tile | 备用菱形地砖 | FloorLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“备用菱形地砖”使用。 |
| 0 | 2 | x=444, y=0, w=222, h=222 | diamond_floor_modules-corridor_diamond_tile | 走廊菱形地砖 | FloorLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“走廊菱形地砖”使用。 |
| 0 | 3 | x=666, y=0, w=222, h=222 | diamond_floor_modules-buildable_boundary_diamond_tile | 可建造边界地砖 | FloorLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“可建造边界地砖”使用。 |
| 0 | 4 | x=888, y=0, w=222, h=222 | diamond_floor_modules-blocked_boundary_diamond_tile | 不可建造边界地砖 | FloorLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“不可建造边界地砖”使用。 |
| 0 | 5 | x=1110, y=0, w=222, h=222 | diamond_floor_modules-dark_floor_trim_tile | 深色地面收边 | FloorDetailLayer | center | 1x1 | 1x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“深色地面收边”使用。 |
| 0 | 6 | x=1332, y=0, w=222, h=222 | diamond_floor_modules-light_floor_trim_tile | 浅色地面收边 | FloorDetailLayer | center | 1x1 | 1x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“浅色地面收边”使用。 |
| 0 | 7 | x=1554, y=0, w=222, h=222 | diamond_floor_modules-corner_floor_transition_tile | 地面转角过渡 | FloorDetailLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“地面转角过渡”使用。 |
| 1 | 0 | x=0, y=222, w=222, h=222 | wall_corner_modules-north_wall_segment | 北侧墙段 | ShellLayer | bottom_center | 1x1 | 1x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“北侧墙段”使用。 |
| 1 | 1 | x=222, y=222, w=222, h=222 | wall_corner_modules-east_wall_segment | 东侧墙段 | ShellLayer | bottom_center | 1x1 | 1x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“东侧墙段”使用。 |
| 1 | 2 | x=444, y=222, w=222, h=222 | wall_corner_modules-south_wall_front_segment | 南侧前墙段 | ShellLayer | bottom_center | 1x1 | 1x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“南侧前墙段”使用。 |
| 1 | 3 | x=666, y=222, w=222, h=222 | wall_corner_modules-west_wall_segment | 西侧墙段 | ShellLayer | bottom_center | 1x1 | 1x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“西侧墙段”使用。 |
| 1 | 4 | x=888, y=222, w=222, h=222 | wall_corner_modules-inner_corner_ne | 东北内墙角 | ShellLayer | bottom_center | 1x1 | 1x1.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“东北内墙角”使用。 |
| 1 | 5 | x=1110, y=222, w=222, h=222 | wall_corner_modules-inner_corner_nw | 西北内墙角 | ShellLayer | bottom_center | 1x1 | 1x1.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“西北内墙角”使用。 |
| 1 | 6 | x=1332, y=222, w=222, h=222 | wall_corner_modules-outer_corner_se | 东南外墙角 | ShellLayer | bottom_center | 1x1 | 1x1.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“东南外墙角”使用。 |
| 1 | 7 | x=1554, y=222, w=222, h=222 | wall_corner_modules-outer_corner_sw | 西南外墙角 | ShellLayer | bottom_center | 1x1 | 1x1.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“西南外墙角”使用。 |
| 2 | 0 | x=0, y=444, w=222, h=222 | door_window_glass_connectors-single_office_door_closed | 单扇办公室门 | ShellLayer | bottom_center | 1x1 | 1x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“单扇办公室门”使用。 |
| 2 | 1 | x=222, y=444, w=222, h=222 | door_window_glass_connectors-double_glass_entrance_door | 双开玻璃入口门 | ShellLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“双开玻璃入口门”使用。 |
| 2 | 2 | x=444, y=444, w=222, h=222 | door_window_glass_connectors-window_wall_segment_short | 短窗墙段 | ShellLayer | bottom_center | 1x1 | 1x1.25 | 在 Startup Sim 2.5D 办公室渲染器中作为“短窗墙段”使用。 |
| 2 | 3 | x=666, y=444, w=222, h=222 | door_window_glass_connectors-window_wall_segment_long | 长窗墙段 | ShellLayer | bottom_center | 2x1 | 2x1.25 | 在 Startup Sim 2.5D 办公室渲染器中作为“长窗墙段”使用。 |
| 2 | 4 | x=888, y=444, w=222, h=222 | door_window_glass_connectors-glass_divider_straight | 直线玻璃隔断 | ShellLayer | bottom_center | 2x1 | 2x1.2 | 在 Startup Sim 2.5D 办公室渲染器中作为“直线玻璃隔断”使用。 |
| 2 | 5 | x=1110, y=444, w=222, h=222 | door_window_glass_connectors-glass_divider_corner | 转角玻璃隔断 | ShellLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D 办公室渲染器中作为“转角玻璃隔断”使用。 |
| 2 | 6 | x=1332, y=444, w=222, h=222 | door_window_glass_connectors-low_partition_segment | 矮隔断墙段 | ShellLayer | bottom_center | 1x1 | 1x0.9 | 在 Startup Sim 2.5D 办公室渲染器中作为“矮隔断墙段”使用。 |
| 2 | 7 | x=1554, y=444, w=222, h=222 | door_window_glass_connectors-low_partition_corner | 矮隔断转角 | ShellLayer | bottom_center | 1x1 | 1x0.9 | 在 Startup Sim 2.5D 办公室渲染器中作为“矮隔断转角”使用。 |
| 3 | 0 | x=0, y=666, w=222, h=222 | architectural_detail_overlays-window_light_diamond_overlay | 窗光菱形叠层 | LightOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“窗光菱形叠层”使用。 |
| 3 | 1 | x=222, y=666, w=222, h=222 | architectural_detail_overlays-cable_floor_channel_straight | 直线地面线槽 | FloorDetailLayer | center | 1x1 | 1x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“直线地面线槽”使用。 |
| 3 | 2 | x=444, y=666, w=222, h=222 | architectural_detail_overlays-cable_floor_channel_corner | 转角地面线槽 | FloorDetailLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“转角地面线槽”使用。 |
| 3 | 3 | x=666, y=666, w=222, h=222 | architectural_detail_overlays-floor_scuff_wear_patch | 地面磨损贴片 | FloorDetailLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“地面磨损贴片”使用。 |
| 3 | 4 | x=888, y=666, w=222, h=222 | architectural_detail_overlays-small_baseboard_strip | 小踢脚线条 | ShellLayer | center | 1x1 | 1x0.3 | 在 Startup Sim 2.5D 办公室渲染器中作为“小踢脚线条”使用。 |
| 3 | 5 | x=1110, y=666, w=222, h=222 | architectural_detail_overlays-column_base_plate | 柱脚底座 | FloorDetailLayer | center | 1x1 | 1x0.8 | 在 Startup Sim 2.5D 办公室渲染器中作为“柱脚底座”使用。 |
| 3 | 6 | x=1332, y=666, w=222, h=222 | architectural_detail_overlays-wall_shadow_strip | 墙脚阴影条 | ShadowLayer | center | 1x1 | 1x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“墙脚阴影条”使用。 |
| 3 | 7 | x=1554, y=666, w=222, h=222 | architectural_detail_overlays-room_edge_highlight_strip | 房间边缘高光条 | LightOverlayLayer | center | 1x1 | 1x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“房间边缘高光条”使用。 |
