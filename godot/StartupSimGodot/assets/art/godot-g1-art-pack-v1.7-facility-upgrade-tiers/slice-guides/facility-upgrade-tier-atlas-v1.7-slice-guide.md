# facility-upgrade-tier-atlas-v1.7 Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/facility-upgrade-tier-atlas-v1.7.png`
- Grid: 8 columns x 6 rows
- Cell: 224x224 px
- Individual PNG directory: `exports/facilities`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=224, h=224 | product_workstation-product_workstation_level_1_idle | 产品工位-1 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“产品工位-1 级待机”使用。 |
| 0 | 1 | x=224, y=0, w=224, h=224 | product_workstation-product_workstation_level_2_idle | 产品工位-2 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“产品工位-2 级待机”使用。 |
| 0 | 2 | x=448, y=0, w=224, h=224 | product_workstation-product_workstation_level_3_idle | 产品工位-3 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“产品工位-3 级待机”使用。 |
| 0 | 3 | x=672, y=0, w=224, h=224 | product_workstation-product_workstation_level_1_active | 产品工位-1 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“产品工位-1 级工作中”使用。 |
| 0 | 4 | x=896, y=0, w=224, h=224 | product_workstation-product_workstation_level_2_active | 产品工位-2 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“产品工位-2 级工作中”使用。 |
| 0 | 5 | x=1120, y=0, w=224, h=224 | product_workstation-product_workstation_level_3_active | 产品工位-3 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“产品工位-3 级工作中”使用。 |
| 0 | 6 | x=1344, y=0, w=224, h=224 | product_workstation-product_workstation_upgrading | 产品工位-升级中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“产品工位-升级中”使用。 |
| 0 | 7 | x=1568, y=0, w=224, h=224 | product_workstation-product_workstation_broken_blocked | 产品工位-故障受阻 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“产品工位-故障受阻”使用。 |
| 1 | 0 | x=0, y=224, w=224, h=224 | sales_phone_pod-sales_phone_pod_level_1_idle | 销售电话舱-1 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“销售电话舱-1 级待机”使用。 |
| 1 | 1 | x=224, y=224, w=224, h=224 | sales_phone_pod-sales_phone_pod_level_2_idle | 销售电话舱-2 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“销售电话舱-2 级待机”使用。 |
| 1 | 2 | x=448, y=224, w=224, h=224 | sales_phone_pod-sales_phone_pod_level_3_idle | 销售电话舱-3 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“销售电话舱-3 级待机”使用。 |
| 1 | 3 | x=672, y=224, w=224, h=224 | sales_phone_pod-sales_phone_pod_level_1_active | 销售电话舱-1 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“销售电话舱-1 级工作中”使用。 |
| 1 | 4 | x=896, y=224, w=224, h=224 | sales_phone_pod-sales_phone_pod_level_2_active | 销售电话舱-2 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“销售电话舱-2 级工作中”使用。 |
| 1 | 5 | x=1120, y=224, w=224, h=224 | sales_phone_pod-sales_phone_pod_level_3_active | 销售电话舱-3 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“销售电话舱-3 级工作中”使用。 |
| 1 | 6 | x=1344, y=224, w=224, h=224 | sales_phone_pod-sales_phone_pod_upgrading | 销售电话舱-升级中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“销售电话舱-升级中”使用。 |
| 1 | 7 | x=1568, y=224, w=224, h=224 | sales_phone_pod-sales_phone_pod_broken_blocked | 销售电话舱-故障受阻 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“销售电话舱-故障受阻”使用。 |
| 2 | 0 | x=0, y=448, w=224, h=224 | server_infrastructure-server_infrastructure_level_1_idle | 服务器设施-1 级待机 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器设施-1 级待机”使用。 |
| 2 | 1 | x=224, y=448, w=224, h=224 | server_infrastructure-server_infrastructure_level_2_idle | 服务器设施-2 级待机 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器设施-2 级待机”使用。 |
| 2 | 2 | x=448, y=448, w=224, h=224 | server_infrastructure-server_infrastructure_level_3_idle | 服务器设施-3 级待机 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器设施-3 级待机”使用。 |
| 2 | 3 | x=672, y=448, w=224, h=224 | server_infrastructure-server_infrastructure_level_1_active | 服务器设施-1 级工作中 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器设施-1 级工作中”使用。 |
| 2 | 4 | x=896, y=448, w=224, h=224 | server_infrastructure-server_infrastructure_level_2_active | 服务器设施-2 级工作中 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器设施-2 级工作中”使用。 |
| 2 | 5 | x=1120, y=448, w=224, h=224 | server_infrastructure-server_infrastructure_level_3_active | 服务器设施-3 级工作中 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器设施-3 级工作中”使用。 |
| 2 | 6 | x=1344, y=448, w=224, h=224 | server_infrastructure-server_infrastructure_upgrading | 服务器设施-升级中 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器设施-升级中”使用。 |
| 2 | 7 | x=1568, y=448, w=224, h=224 | server_infrastructure-server_infrastructure_broken_blocked | 服务器设施-故障受阻 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D Godot 表现层中作为“服务器设施-故障受阻”使用。 |
| 3 | 0 | x=0, y=672, w=224, h=224 | meeting_room-meeting_room_level_1_idle | 会议室-1 级待机 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议室-1 级待机”使用。 |
| 3 | 1 | x=224, y=672, w=224, h=224 | meeting_room-meeting_room_level_2_idle | 会议室-2 级待机 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议室-2 级待机”使用。 |
| 3 | 2 | x=448, y=672, w=224, h=224 | meeting_room-meeting_room_level_3_idle | 会议室-3 级待机 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议室-3 级待机”使用。 |
| 3 | 3 | x=672, y=672, w=224, h=224 | meeting_room-meeting_room_level_1_active | 会议室-1 级工作中 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议室-1 级工作中”使用。 |
| 3 | 4 | x=896, y=672, w=224, h=224 | meeting_room-meeting_room_level_2_active | 会议室-2 级工作中 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议室-2 级工作中”使用。 |
| 3 | 5 | x=1120, y=672, w=224, h=224 | meeting_room-meeting_room_level_3_active | 会议室-3 级工作中 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议室-3 级工作中”使用。 |
| 3 | 6 | x=1344, y=672, w=224, h=224 | meeting_room-meeting_room_upgrading | 会议室-升级中 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议室-升级中”使用。 |
| 3 | 7 | x=1568, y=672, w=224, h=224 | meeting_room-meeting_room_broken_blocked | 会议室-故障受阻 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D Godot 表现层中作为“会议室-故障受阻”使用。 |
| 4 | 0 | x=0, y=896, w=224, h=224 | rest_recovery_area-rest_recovery_area_level_1_idle | 休息恢复区-1 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“休息恢复区-1 级待机”使用。 |
| 4 | 1 | x=224, y=896, w=224, h=224 | rest_recovery_area-rest_recovery_area_level_2_idle | 休息恢复区-2 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“休息恢复区-2 级待机”使用。 |
| 4 | 2 | x=448, y=896, w=224, h=224 | rest_recovery_area-rest_recovery_area_level_3_idle | 休息恢复区-3 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“休息恢复区-3 级待机”使用。 |
| 4 | 3 | x=672, y=896, w=224, h=224 | rest_recovery_area-rest_recovery_area_level_1_active | 休息恢复区-1 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“休息恢复区-1 级工作中”使用。 |
| 4 | 4 | x=896, y=896, w=224, h=224 | rest_recovery_area-rest_recovery_area_level_2_active | 休息恢复区-2 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“休息恢复区-2 级工作中”使用。 |
| 4 | 5 | x=1120, y=896, w=224, h=224 | rest_recovery_area-rest_recovery_area_level_3_active | 休息恢复区-3 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“休息恢复区-3 级工作中”使用。 |
| 4 | 6 | x=1344, y=896, w=224, h=224 | rest_recovery_area-rest_recovery_area_upgrading | 休息恢复区-升级中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“休息恢复区-升级中”使用。 |
| 4 | 7 | x=1568, y=896, w=224, h=224 | rest_recovery_area-rest_recovery_area_broken_blocked | 休息恢复区-故障受阻 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“休息恢复区-故障受阻”使用。 |
| 5 | 0 | x=0, y=1120, w=224, h=224 | recruiting_hr_area-recruiting_hr_area_level_1_idle | 招聘 HR 区-1 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“招聘 HR 区-1 级待机”使用。 |
| 5 | 1 | x=224, y=1120, w=224, h=224 | recruiting_hr_area-recruiting_hr_area_level_2_idle | 招聘 HR 区-2 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“招聘 HR 区-2 级待机”使用。 |
| 5 | 2 | x=448, y=1120, w=224, h=224 | recruiting_hr_area-recruiting_hr_area_level_3_idle | 招聘 HR 区-3 级待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“招聘 HR 区-3 级待机”使用。 |
| 5 | 3 | x=672, y=1120, w=224, h=224 | recruiting_hr_area-recruiting_hr_area_level_1_active | 招聘 HR 区-1 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“招聘 HR 区-1 级工作中”使用。 |
| 5 | 4 | x=896, y=1120, w=224, h=224 | recruiting_hr_area-recruiting_hr_area_level_2_active | 招聘 HR 区-2 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“招聘 HR 区-2 级工作中”使用。 |
| 5 | 5 | x=1120, y=1120, w=224, h=224 | recruiting_hr_area-recruiting_hr_area_level_3_active | 招聘 HR 区-3 级工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“招聘 HR 区-3 级工作中”使用。 |
| 5 | 6 | x=1344, y=1120, w=224, h=224 | recruiting_hr_area-recruiting_hr_area_upgrading | 招聘 HR 区-升级中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“招聘 HR 区-升级中”使用。 |
| 5 | 7 | x=1568, y=1120, w=224, h=224 | recruiting_hr_area-recruiting_hr_area_broken_blocked | 招聘 HR 区-故障受阻 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D Godot 表现层中作为“招聘 HR 区-故障受阻”使用。 |
