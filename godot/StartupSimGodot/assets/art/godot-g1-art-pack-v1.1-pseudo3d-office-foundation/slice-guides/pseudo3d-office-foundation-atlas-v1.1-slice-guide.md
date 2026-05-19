# pseudo3d-office-foundation-atlas-v1.1 Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/pseudo3d-office-foundation-atlas-v1.1.png`
- Grid: 8 columns x 4 rows
- Cell: 222x222 px
- Individual PNG directory: `exports/props`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=222, h=222 | office_shell_boundary-wall_corner_l_piece | 墙体 L 形转角 | ShellLayer | bottom_center | 1x1 | 1x1.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“墙体 L 形转角”使用。 |
| 0 | 1 | x=222, y=0, w=222, h=222 | office_shell_boundary-window_wall_segment | 窗户墙段 | ShellLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“窗户墙段”使用。 |
| 0 | 2 | x=444, y=0, w=222, h=222 | office_shell_boundary-glass_divider_segment | 玻璃隔断段 | ShellLayer | bottom_center | 2x1 | 2x1.25 | 在 Startup Sim 2.5D 办公室渲染器中作为“玻璃隔断段”使用。 |
| 0 | 3 | x=666, y=0, w=222, h=222 | office_shell_boundary-entrance_door_segment | 入口门段 | ShellLayer | bottom_center | 2x1 | 2x1.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“入口门段”使用。 |
| 0 | 4 | x=888, y=0, w=222, h=222 | office_shell_boundary-square_column_pillar | 方形承重柱 | ShellLayer | bottom_center | 1x1 | 1x1.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“方形承重柱”使用。 |
| 0 | 5 | x=1110, y=0, w=222, h=222 | office_shell_boundary-exterior_threshold_strip | 外部门槛条 | ShellLayer | center | 2x1 | 2x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“外部门槛条”使用。 |
| 0 | 6 | x=1332, y=0, w=222, h=222 | office_shell_boundary-buildable_floor_edge_trim | 可建造地面边条 | FloorDetailLayer | center | 2x1 | 2x0.4 | 在 Startup Sim 2.5D 办公室渲染器中作为“可建造地面边条”使用。 |
| 0 | 7 | x=1554, y=0, w=222, h=222 | office_shell_boundary-blocked_floor_edge_trim | 不可建造地面边条 | FloorDetailLayer | center | 2x1 | 2x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“不可建造地面边条”使用。 |
| 1 | 0 | x=0, y=222, w=222, h=222 | floor_light_overlays-office_floor_tile_patch | 办公室地砖块 | FloorLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“办公室地砖块”使用。 |
| 1 | 1 | x=222, y=222, w=222, h=222 | floor_light_overlays-carpet_zone_patch | 区域地毯块 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“区域地毯块”使用。 |
| 1 | 2 | x=444, y=222, w=222, h=222 | floor_light_overlays-cable_run_strip | 线缆走线条 | FloorDetailLayer | center | 2x1 | 2x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“线缆走线条”使用。 |
| 1 | 3 | x=666, y=222, w=222, h=222 | floor_light_overlays-window_light_strip | 窗光条 | LightOverlayLayer | center | 2x1 | 2x0.7 | 在 Startup Sim 2.5D 办公室渲染器中作为“窗光条”使用。 |
| 1 | 4 | x=888, y=222, w=222, h=222 | floor_light_overlays-soft_workstation_shadow | 工位柔和阴影 | ShadowLayer | center | 1x1 | 1.2x0.75 | 在 Startup Sim 2.5D 办公室渲染器中作为“工位柔和阴影”使用。 |
| 1 | 5 | x=1110, y=222, w=222, h=222 | floor_light_overlays-large_facility_shadow | 大型设施阴影 | ShadowLayer | center | 2x1 | 2.2x1.2 | 在 Startup Sim 2.5D 办公室渲染器中作为“大型设施阴影”使用。 |
| 1 | 6 | x=1332, y=222, w=222, h=222 | floor_light_overlays-hover_highlight_marker | 悬停高亮标记 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“悬停高亮标记”使用。 |
| 1 | 7 | x=1554, y=222, w=222, h=222 | floor_light_overlays-selected_cell_marker | 选中格标记 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“选中格标记”使用。 |
| 2 | 0 | x=0, y=444, w=222, h=222 | build_zone_markers-placement_valid_marker | 可放置标记 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“可放置标记”使用。 |
| 2 | 1 | x=222, y=444, w=222, h=222 | build_zone_markers-placement_invalid_marker | 不可放置标记 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“不可放置标记”使用。 |
| 2 | 2 | x=444, y=444, w=222, h=222 | build_zone_markers-zone_start_marker | 区域起点标记 | PlacementPreviewLayer | bottom_center | 1x1 | 1x1.1 | 在 Startup Sim 2.5D 办公室渲染器中作为“区域起点标记”使用。 |
| 2 | 3 | x=666, y=444, w=222, h=222 | build_zone_markers-zone_end_marker | 区域终点标记 | PlacementPreviewLayer | bottom_center | 1x1 | 1x1.1 | 在 Startup Sim 2.5D 办公室渲染器中作为“区域终点标记”使用。 |
| 2 | 4 | x=888, y=444, w=222, h=222 | build_zone_markers-upgrade_progress_ring | 升级进度环 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“升级进度环”使用。 |
| 2 | 5 | x=1110, y=444, w=222, h=222 | build_zone_markers-capacity_warning_marker | 容量警告标记 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“容量警告标记”使用。 |
| 2 | 6 | x=1332, y=444, w=222, h=222 | build_zone_markers-traffic_arrow_marker | 动线箭头标记 | PlacementPreviewLayer | center | 1x1 | 1.2x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“动线箭头标记”使用。 |
| 2 | 7 | x=1554, y=444, w=222, h=222 | build_zone_markers-department_boundary_corner_marker | 部门边界角标 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“部门边界角标”使用。 |
| 3 | 0 | x=0, y=666, w=222, h=222 | small_office_props-potted_plant | 盆栽 | PropLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D 办公室渲染器中作为“盆栽”使用。 |
| 3 | 1 | x=222, y=666, w=222, h=222 | small_office_props-printer_copier | 打印复印机 | PropLayer | bottom_center | 1x1 | 1x1.05 | 在 Startup Sim 2.5D 办公室渲染器中作为“打印复印机”使用。 |
| 3 | 2 | x=444, y=666, w=222, h=222 | small_office_props-water_cooler | 饮水机 | PropLayer | bottom_center | 1x1 | 1x1.2 | 在 Startup Sim 2.5D 办公室渲染器中作为“饮水机”使用。 |
| 3 | 3 | x=666, y=666, w=222, h=222 | small_office_props-coffee_machine | 咖啡机 | PropLayer | bottom_center | 1x1 | 1x1.15 | 在 Startup Sim 2.5D 办公室渲染器中作为“咖啡机”使用。 |
| 3 | 4 | x=888, y=666, w=222, h=222 | small_office_props-trash_bin | 垃圾桶 | PropLayer | bottom_center | 1x1 | 0.8x0.9 | 在 Startup Sim 2.5D 办公室渲染器中作为“垃圾桶”使用。 |
| 3 | 5 | x=1110, y=666, w=222, h=222 | small_office_props-sticky_note_board | 便利贴白板 | PropLayer | bottom_center | 1x1 | 1.2x1.1 | 在 Startup Sim 2.5D 办公室渲染器中作为“便利贴白板”使用。 |
| 3 | 6 | x=1332, y=666, w=222, h=222 | small_office_props-cable_hub_router_box | 线缆路由盒 | PropLayer | bottom_center | 1x1 | 1.2x0.9 | 在 Startup Sim 2.5D 办公室渲染器中作为“线缆路由盒”使用。 |
| 3 | 7 | x=1554, y=666, w=222, h=222 | small_office_props-desk_accessory_cluster | 桌面配件组 | PropLayer | bottom_center | 1x1 | 1x0.85 | 在 Startup Sim 2.5D 办公室渲染器中作为“桌面配件组”使用。 |
