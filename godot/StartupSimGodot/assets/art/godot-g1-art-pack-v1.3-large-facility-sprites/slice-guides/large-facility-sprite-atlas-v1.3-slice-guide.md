# large-facility-sprite-atlas-v1.3 Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/large-facility-sprite-atlas-v1.3.png`
- Grid: 8 columns x 4 rows
- Cell: 222x222 px
- Individual PNG directory: `exports/facilities`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=222, h=222 | product_workstation_group_2x1-product_workstation_group_2x1_idle | 2x1 产品工位组-待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 产品工位组-待机”使用。 |
| 0 | 1 | x=222, y=0, w=222, h=222 | product_workstation_group_2x1-product_workstation_group_2x1_active | 2x1 产品工位组-工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 产品工位组-工作中”使用。 |
| 0 | 2 | x=444, y=0, w=222, h=222 | product_workstation_group_2x1-product_workstation_group_2x1_upgrading | 2x1 产品工位组-升级中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 产品工位组-升级中”使用。 |
| 0 | 3 | x=666, y=0, w=222, h=222 | product_workstation_group_2x1-product_workstation_group_2x1_blocked | 2x1 产品工位组-受阻 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 产品工位组-受阻”使用。 |
| 0 | 4 | x=888, y=0, w=222, h=222 | product_workstation_group_2x1-product_workstation_group_2x1_high_efficiency | 2x1 产品工位组-高效率 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 产品工位组-高效率”使用。 |
| 0 | 5 | x=1110, y=0, w=222, h=222 | product_workstation_group_2x1-product_workstation_group_2x1_low_efficiency | 2x1 产品工位组-低效率 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 产品工位组-低效率”使用。 |
| 0 | 6 | x=1332, y=0, w=222, h=222 | product_workstation_group_2x1-product_workstation_group_2x1_placement_preview_valid | 2x1 产品工位组-可放置预览 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 产品工位组-可放置预览”使用。 |
| 0 | 7 | x=1554, y=0, w=222, h=222 | product_workstation_group_2x1-product_workstation_group_2x1_placement_preview_invalid | 2x1 产品工位组-不可放置预览 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 产品工位组-不可放置预览”使用。 |
| 1 | 0 | x=0, y=222, w=222, h=222 | sales_phone_pod_group_2x1-sales_phone_pod_group_2x1_idle | 2x1 销售电话舱组-待机 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 销售电话舱组-待机”使用。 |
| 1 | 1 | x=222, y=222, w=222, h=222 | sales_phone_pod_group_2x1-sales_phone_pod_group_2x1_active | 2x1 销售电话舱组-工作中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 销售电话舱组-工作中”使用。 |
| 1 | 2 | x=444, y=222, w=222, h=222 | sales_phone_pod_group_2x1-sales_phone_pod_group_2x1_upgrading | 2x1 销售电话舱组-升级中 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 销售电话舱组-升级中”使用。 |
| 1 | 3 | x=666, y=222, w=222, h=222 | sales_phone_pod_group_2x1-sales_phone_pod_group_2x1_blocked | 2x1 销售电话舱组-受阻 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 销售电话舱组-受阻”使用。 |
| 1 | 4 | x=888, y=222, w=222, h=222 | sales_phone_pod_group_2x1-sales_phone_pod_group_2x1_high_efficiency | 2x1 销售电话舱组-高效率 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 销售电话舱组-高效率”使用。 |
| 1 | 5 | x=1110, y=222, w=222, h=222 | sales_phone_pod_group_2x1-sales_phone_pod_group_2x1_low_efficiency | 2x1 销售电话舱组-低效率 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 销售电话舱组-低效率”使用。 |
| 1 | 6 | x=1332, y=222, w=222, h=222 | sales_phone_pod_group_2x1-sales_phone_pod_group_2x1_placement_preview_valid | 2x1 销售电话舱组-可放置预览 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 销售电话舱组-可放置预览”使用。 |
| 1 | 7 | x=1554, y=222, w=222, h=222 | sales_phone_pod_group_2x1-sales_phone_pod_group_2x1_placement_preview_invalid | 2x1 销售电话舱组-不可放置预览 | FacilityLayer | bottom_center | 2x1 | 2x1.35 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x1 销售电话舱组-不可放置预览”使用。 |
| 2 | 0 | x=0, y=444, w=222, h=222 | server_rack_group_1x2-server_rack_group_1x2_idle | 1x2 服务器机柜组-待机 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“1x2 服务器机柜组-待机”使用。 |
| 2 | 1 | x=222, y=444, w=222, h=222 | server_rack_group_1x2-server_rack_group_1x2_active | 1x2 服务器机柜组-工作中 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“1x2 服务器机柜组-工作中”使用。 |
| 2 | 2 | x=444, y=444, w=222, h=222 | server_rack_group_1x2-server_rack_group_1x2_upgrading | 1x2 服务器机柜组-升级中 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“1x2 服务器机柜组-升级中”使用。 |
| 2 | 3 | x=666, y=444, w=222, h=222 | server_rack_group_1x2-server_rack_group_1x2_blocked | 1x2 服务器机柜组-受阻 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“1x2 服务器机柜组-受阻”使用。 |
| 2 | 4 | x=888, y=444, w=222, h=222 | server_rack_group_1x2-server_rack_group_1x2_high_efficiency | 1x2 服务器机柜组-高效率 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“1x2 服务器机柜组-高效率”使用。 |
| 2 | 5 | x=1110, y=444, w=222, h=222 | server_rack_group_1x2-server_rack_group_1x2_low_efficiency | 1x2 服务器机柜组-低效率 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“1x2 服务器机柜组-低效率”使用。 |
| 2 | 6 | x=1332, y=444, w=222, h=222 | server_rack_group_1x2-server_rack_group_1x2_placement_preview_valid | 1x2 服务器机柜组-可放置预览 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“1x2 服务器机柜组-可放置预览”使用。 |
| 2 | 7 | x=1554, y=444, w=222, h=222 | server_rack_group_1x2-server_rack_group_1x2_placement_preview_invalid | 1x2 服务器机柜组-不可放置预览 | FacilityLayer | bottom_center | 1x2 | 1.35x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“1x2 服务器机柜组-不可放置预览”使用。 |
| 3 | 0 | x=0, y=666, w=222, h=222 | meeting_rest_hybrid_2x2-meeting_rest_hybrid_2x2_idle | 2x2 会议休息混合区-待机 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x2 会议休息混合区-待机”使用。 |
| 3 | 1 | x=222, y=666, w=222, h=222 | meeting_rest_hybrid_2x2-meeting_rest_hybrid_2x2_active | 2x2 会议休息混合区-工作中 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x2 会议休息混合区-工作中”使用。 |
| 3 | 2 | x=444, y=666, w=222, h=222 | meeting_rest_hybrid_2x2-meeting_rest_hybrid_2x2_upgrading | 2x2 会议休息混合区-升级中 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x2 会议休息混合区-升级中”使用。 |
| 3 | 3 | x=666, y=666, w=222, h=222 | meeting_rest_hybrid_2x2-meeting_rest_hybrid_2x2_blocked | 2x2 会议休息混合区-受阻 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x2 会议休息混合区-受阻”使用。 |
| 3 | 4 | x=888, y=666, w=222, h=222 | meeting_rest_hybrid_2x2-meeting_rest_hybrid_2x2_high_efficiency | 2x2 会议休息混合区-高效率 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x2 会议休息混合区-高效率”使用。 |
| 3 | 5 | x=1110, y=666, w=222, h=222 | meeting_rest_hybrid_2x2-meeting_rest_hybrid_2x2_low_efficiency | 2x2 会议休息混合区-低效率 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x2 会议休息混合区-低效率”使用。 |
| 3 | 6 | x=1332, y=666, w=222, h=222 | meeting_rest_hybrid_2x2-meeting_rest_hybrid_2x2_placement_preview_valid | 2x2 会议休息混合区-可放置预览 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x2 会议休息混合区-可放置预览”使用。 |
| 3 | 7 | x=1554, y=666, w=222, h=222 | meeting_rest_hybrid_2x2-meeting_rest_hybrid_2x2_placement_preview_invalid | 2x2 会议休息混合区-不可放置预览 | FacilityLayer | bottom_center | 2x2 | 2x2 | 在 Startup Sim 2.5D 办公室渲染器中作为“2x2 会议休息混合区-不可放置预览”使用。 |
