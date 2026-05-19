# employee-pseudo3d-motion-atlas-v1.4 Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/employee-pseudo3d-motion-atlas-v1.4.png`
- Grid: 12 columns x 4 rows
- Cell: 192x224 px
- Individual PNG directory: `exports/sprites`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=192, h=224 | product_engineer-walk_down_a | 产品工程师-向下行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-向下行走 A”员工小图使用。 |
| 0 | 1 | x=192, y=0, w=192, h=224 | product_engineer-walk_down_b | 产品工程师-向下行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-向下行走 B”员工小图使用。 |
| 0 | 2 | x=384, y=0, w=192, h=224 | product_engineer-walk_right_a | 产品工程师-向右行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-向右行走 A”员工小图使用。 |
| 0 | 3 | x=576, y=0, w=192, h=224 | product_engineer-walk_right_b | 产品工程师-向右行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-向右行走 B”员工小图使用。 |
| 0 | 4 | x=768, y=0, w=192, h=224 | product_engineer-walk_up_a | 产品工程师-向上行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-向上行走 A”员工小图使用。 |
| 0 | 5 | x=960, y=0, w=192, h=224 | product_engineer-walk_up_b | 产品工程师-向上行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-向上行走 B”员工小图使用。 |
| 0 | 6 | x=1152, y=0, w=192, h=224 | product_engineer-walk_left_a | 产品工程师-向左行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-向左行走 A”员工小图使用。 |
| 0 | 7 | x=1344, y=0, w=192, h=224 | product_engineer-walk_left_b | 产品工程师-向左行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-向左行走 B”员工小图使用。 |
| 0 | 8 | x=1536, y=0, w=192, h=224 | product_engineer-working | 产品工程师-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-工作”员工小图使用。 |
| 0 | 9 | x=1728, y=0, w=192, h=224 | product_engineer-resting | 产品工程师-休息 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-休息”员工小图使用。 |
| 0 | 10 | x=1920, y=0, w=192, h=224 | product_engineer-training | 产品工程师-学习训练 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-学习训练”员工小图使用。 |
| 0 | 11 | x=2112, y=0, w=192, h=224 | product_engineer-stressed | 产品工程师-压力过载 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“产品工程师-压力过载”员工小图使用。 |
| 1 | 0 | x=0, y=224, w=192, h=224 | sales_representative-walk_down_a | 销售代表-向下行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-向下行走 A”员工小图使用。 |
| 1 | 1 | x=192, y=224, w=192, h=224 | sales_representative-walk_down_b | 销售代表-向下行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-向下行走 B”员工小图使用。 |
| 1 | 2 | x=384, y=224, w=192, h=224 | sales_representative-walk_right_a | 销售代表-向右行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-向右行走 A”员工小图使用。 |
| 1 | 3 | x=576, y=224, w=192, h=224 | sales_representative-walk_right_b | 销售代表-向右行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-向右行走 B”员工小图使用。 |
| 1 | 4 | x=768, y=224, w=192, h=224 | sales_representative-walk_up_a | 销售代表-向上行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-向上行走 A”员工小图使用。 |
| 1 | 5 | x=960, y=224, w=192, h=224 | sales_representative-walk_up_b | 销售代表-向上行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-向上行走 B”员工小图使用。 |
| 1 | 6 | x=1152, y=224, w=192, h=224 | sales_representative-walk_left_a | 销售代表-向左行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-向左行走 A”员工小图使用。 |
| 1 | 7 | x=1344, y=224, w=192, h=224 | sales_representative-walk_left_b | 销售代表-向左行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-向左行走 B”员工小图使用。 |
| 1 | 8 | x=1536, y=224, w=192, h=224 | sales_representative-working | 销售代表-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-工作”员工小图使用。 |
| 1 | 9 | x=1728, y=224, w=192, h=224 | sales_representative-resting | 销售代表-休息 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-休息”员工小图使用。 |
| 1 | 10 | x=1920, y=224, w=192, h=224 | sales_representative-training | 销售代表-学习训练 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-学习训练”员工小图使用。 |
| 1 | 11 | x=2112, y=224, w=192, h=224 | sales_representative-stressed | 销售代表-压力过载 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“销售代表-压力过载”员工小图使用。 |
| 2 | 0 | x=0, y=448, w=192, h=224 | ops_engineer-walk_down_a | 运维工程师-向下行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-向下行走 A”员工小图使用。 |
| 2 | 1 | x=192, y=448, w=192, h=224 | ops_engineer-walk_down_b | 运维工程师-向下行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-向下行走 B”员工小图使用。 |
| 2 | 2 | x=384, y=448, w=192, h=224 | ops_engineer-walk_right_a | 运维工程师-向右行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-向右行走 A”员工小图使用。 |
| 2 | 3 | x=576, y=448, w=192, h=224 | ops_engineer-walk_right_b | 运维工程师-向右行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-向右行走 B”员工小图使用。 |
| 2 | 4 | x=768, y=448, w=192, h=224 | ops_engineer-walk_up_a | 运维工程师-向上行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-向上行走 A”员工小图使用。 |
| 2 | 5 | x=960, y=448, w=192, h=224 | ops_engineer-walk_up_b | 运维工程师-向上行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-向上行走 B”员工小图使用。 |
| 2 | 6 | x=1152, y=448, w=192, h=224 | ops_engineer-walk_left_a | 运维工程师-向左行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-向左行走 A”员工小图使用。 |
| 2 | 7 | x=1344, y=448, w=192, h=224 | ops_engineer-walk_left_b | 运维工程师-向左行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-向左行走 B”员工小图使用。 |
| 2 | 8 | x=1536, y=448, w=192, h=224 | ops_engineer-working | 运维工程师-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-工作”员工小图使用。 |
| 2 | 9 | x=1728, y=448, w=192, h=224 | ops_engineer-resting | 运维工程师-休息 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-休息”员工小图使用。 |
| 2 | 10 | x=1920, y=448, w=192, h=224 | ops_engineer-training | 运维工程师-学习训练 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-学习训练”员工小图使用。 |
| 2 | 11 | x=2112, y=448, w=192, h=224 | ops_engineer-stressed | 运维工程师-压力过载 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“运维工程师-压力过载”员工小图使用。 |
| 3 | 0 | x=0, y=672, w=192, h=224 | admin_hr_generalist-walk_down_a | 行政 HR-向下行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-向下行走 A”员工小图使用。 |
| 3 | 1 | x=192, y=672, w=192, h=224 | admin_hr_generalist-walk_down_b | 行政 HR-向下行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-向下行走 B”员工小图使用。 |
| 3 | 2 | x=384, y=672, w=192, h=224 | admin_hr_generalist-walk_right_a | 行政 HR-向右行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-向右行走 A”员工小图使用。 |
| 3 | 3 | x=576, y=672, w=192, h=224 | admin_hr_generalist-walk_right_b | 行政 HR-向右行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-向右行走 B”员工小图使用。 |
| 3 | 4 | x=768, y=672, w=192, h=224 | admin_hr_generalist-walk_up_a | 行政 HR-向上行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-向上行走 A”员工小图使用。 |
| 3 | 5 | x=960, y=672, w=192, h=224 | admin_hr_generalist-walk_up_b | 行政 HR-向上行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-向上行走 B”员工小图使用。 |
| 3 | 6 | x=1152, y=672, w=192, h=224 | admin_hr_generalist-walk_left_a | 行政 HR-向左行走 A | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-向左行走 A”员工小图使用。 |
| 3 | 7 | x=1344, y=672, w=192, h=224 | admin_hr_generalist-walk_left_b | 行政 HR-向左行走 B | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-向左行走 B”员工小图使用。 |
| 3 | 8 | x=1536, y=672, w=192, h=224 | admin_hr_generalist-working | 行政 HR-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-工作”员工小图使用。 |
| 3 | 9 | x=1728, y=672, w=192, h=224 | admin_hr_generalist-resting | 行政 HR-休息 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-休息”员工小图使用。 |
| 3 | 10 | x=1920, y=672, w=192, h=224 | admin_hr_generalist-training | 行政 HR-学习训练 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-学习训练”员工小图使用。 |
| 3 | 11 | x=2112, y=672, w=192, h=224 | admin_hr_generalist-stressed | 行政 HR-压力过载 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D 办公室中作为“行政 HR-压力过载”员工小图使用。 |
