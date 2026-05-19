# zone-carpet-build-marker-atlas-v1.2 Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/zone-carpet-build-marker-atlas-v1.2.png`
- Grid: 8 columns x 4 rows
- Cell: 222x222 px
- Individual PNG directory: `exports/overlays`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=222, h=222 | department_carpet_centers-product_zone_carpet_center | 产品区地毯中心 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“产品区地毯中心”使用。 |
| 0 | 1 | x=222, y=0, w=222, h=222 | department_carpet_centers-sales_zone_carpet_center | 销售区地毯中心 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“销售区地毯中心”使用。 |
| 0 | 2 | x=444, y=0, w=222, h=222 | department_carpet_centers-server_zone_carpet_center | 服务器区地毯中心 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“服务器区地毯中心”使用。 |
| 0 | 3 | x=666, y=0, w=222, h=222 | department_carpet_centers-meeting_zone_carpet_center | 会议区地毯中心 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“会议区地毯中心”使用。 |
| 0 | 4 | x=888, y=0, w=222, h=222 | department_carpet_centers-recruiting_zone_carpet_center | 招聘区地毯中心 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“招聘区地毯中心”使用。 |
| 0 | 5 | x=1110, y=0, w=222, h=222 | department_carpet_centers-rest_zone_carpet_center | 休息区地毯中心 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“休息区地毯中心”使用。 |
| 0 | 6 | x=1332, y=0, w=222, h=222 | department_carpet_centers-market_zone_carpet_center | 市场区地毯中心 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“市场区地毯中心”使用。 |
| 0 | 7 | x=1554, y=0, w=222, h=222 | department_carpet_centers-admin_zone_carpet_center | 行政区地毯中心 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“行政区地毯中心”使用。 |
| 1 | 0 | x=0, y=222, w=222, h=222 | department_carpet_edges_corners-product_carpet_edge | 产品区地毯边 | ZoneOverlayLayer | center | 1x1 | 1x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“产品区地毯边”使用。 |
| 1 | 1 | x=222, y=222, w=222, h=222 | department_carpet_edges_corners-sales_carpet_edge | 销售区地毯边 | ZoneOverlayLayer | center | 1x1 | 1x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“销售区地毯边”使用。 |
| 1 | 2 | x=444, y=222, w=222, h=222 | department_carpet_edges_corners-server_carpet_edge | 服务器区地毯边 | ZoneOverlayLayer | center | 1x1 | 1x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“服务器区地毯边”使用。 |
| 1 | 3 | x=666, y=222, w=222, h=222 | department_carpet_edges_corners-meeting_carpet_edge | 会议区地毯边 | ZoneOverlayLayer | center | 1x1 | 1x0.45 | 在 Startup Sim 2.5D 办公室渲染器中作为“会议区地毯边”使用。 |
| 1 | 4 | x=888, y=222, w=222, h=222 | department_carpet_edges_corners-recruiting_carpet_corner | 招聘区地毯角 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“招聘区地毯角”使用。 |
| 1 | 5 | x=1110, y=222, w=222, h=222 | department_carpet_edges_corners-rest_carpet_corner | 休息区地毯角 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“休息区地毯角”使用。 |
| 1 | 6 | x=1332, y=222, w=222, h=222 | department_carpet_edges_corners-market_carpet_corner | 市场区地毯角 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“市场区地毯角”使用。 |
| 1 | 7 | x=1554, y=222, w=222, h=222 | department_carpet_edges_corners-admin_carpet_corner | 行政区地毯角 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“行政区地毯角”使用。 |
| 2 | 0 | x=0, y=444, w=222, h=222 | projected_build_markers-hover_diamond | 悬停菱形 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“悬停菱形”使用。 |
| 2 | 1 | x=222, y=444, w=222, h=222 | projected_build_markers-selected_diamond | 选中菱形 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“选中菱形”使用。 |
| 2 | 2 | x=444, y=444, w=222, h=222 | projected_build_markers-placement_valid_diamond | 可放置菱形 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“可放置菱形”使用。 |
| 2 | 3 | x=666, y=444, w=222, h=222 | projected_build_markers-placement_invalid_diamond | 不可放置菱形 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“不可放置菱形”使用。 |
| 2 | 4 | x=888, y=444, w=222, h=222 | projected_build_markers-blocked_diamond | 阻塞菱形 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“阻塞菱形”使用。 |
| 2 | 5 | x=1110, y=444, w=222, h=222 | projected_build_markers-upgrade_target_ring | 升级目标环 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“升级目标环”使用。 |
| 2 | 6 | x=1332, y=444, w=222, h=222 | projected_build_markers-sell_remove_marker | 出售移除标记 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“出售移除标记”使用。 |
| 2 | 7 | x=1554, y=444, w=222, h=222 | projected_build_markers-move_relocate_marker | 移动重定位标记 | PlacementPreviewLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“移动重定位标记”使用。 |
| 3 | 0 | x=0, y=666, w=222, h=222 | zone_status_overlays-capacity_healthy_overlay | 容量健康叠层 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“容量健康叠层”使用。 |
| 3 | 1 | x=222, y=666, w=222, h=222 | zone_status_overlays-capacity_tight_warning_overlay | 容量紧张警告叠层 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“容量紧张警告叠层”使用。 |
| 3 | 2 | x=444, y=666, w=222, h=222 | zone_status_overlays-production_active_pulse | 生产活跃脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“生产活跃脉冲”使用。 |
| 3 | 3 | x=666, y=666, w=222, h=222 | zone_status_overlays-morale_boost_pulse | 士气提升脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“士气提升脉冲”使用。 |
| 3 | 4 | x=888, y=666, w=222, h=222 | zone_status_overlays-risk_incident_pulse | 风险事件脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“风险事件脉冲”使用。 |
| 3 | 5 | x=1110, y=666, w=222, h=222 | zone_status_overlays-under_construction_hatch | 施工斜线叠层 | ZoneOverlayLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“施工斜线叠层”使用。 |
| 3 | 6 | x=1332, y=666, w=222, h=222 | zone_status_overlays-high_efficiency_sparkle_tile | 高效率闪光地块 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“高效率闪光地块”使用。 |
| 3 | 7 | x=1554, y=666, w=222, h=222 | zone_status_overlays-low_efficiency_dim_tile | 低效率变暗地块 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim 2.5D 办公室渲染器中作为“低效率变暗地块”使用。 |
