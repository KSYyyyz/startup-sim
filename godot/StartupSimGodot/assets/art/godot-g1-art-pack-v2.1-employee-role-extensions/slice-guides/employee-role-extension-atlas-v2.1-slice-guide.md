# employee-role-extension-atlas-v2.1 Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/employee-role-extension-atlas-v2.1.png`
- Grid: 8 columns x 8 rows
- Cell: 192x224 px
- Individual PNG directory: `exports/sprites`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=192, h=224 | founder_ceo-founder_ceo_idle_front | 创始人 CEO-正面待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“创始人 CEO-正面待机”使用。 |
| 0 | 1 | x=192, y=0, w=192, h=224 | founder_ceo-founder_ceo_idle_right | 创始人 CEO-右向待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“创始人 CEO-右向待机”使用。 |
| 0 | 2 | x=384, y=0, w=192, h=224 | founder_ceo-founder_ceo_working | 创始人 CEO-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“创始人 CEO-工作”使用。 |
| 0 | 3 | x=576, y=0, w=192, h=224 | founder_ceo-founder_ceo_presenting | 创始人 CEO-演示 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“创始人 CEO-演示”使用。 |
| 0 | 4 | x=768, y=0, w=192, h=224 | founder_ceo-founder_ceo_talking_negotiating | 创始人 CEO-沟通谈判 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“创始人 CEO-沟通谈判”使用。 |
| 0 | 5 | x=960, y=0, w=192, h=224 | founder_ceo-founder_ceo_stressed | 创始人 CEO-压力状态 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“创始人 CEO-压力状态”使用。 |
| 0 | 6 | x=1152, y=0, w=192, h=224 | founder_ceo-founder_ceo_celebrating | 创始人 CEO-庆祝 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“创始人 CEO-庆祝”使用。 |
| 0 | 7 | x=1344, y=0, w=192, h=224 | founder_ceo-founder_ceo_thinking_decision | 创始人 CEO-思考决策 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“创始人 CEO-思考决策”使用。 |
| 1 | 0 | x=0, y=224, w=192, h=224 | product_manager-product_manager_idle_front | 产品经理-正面待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“产品经理-正面待机”使用。 |
| 1 | 1 | x=192, y=224, w=192, h=224 | product_manager-product_manager_idle_right | 产品经理-右向待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“产品经理-右向待机”使用。 |
| 1 | 2 | x=384, y=224, w=192, h=224 | product_manager-product_manager_working | 产品经理-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“产品经理-工作”使用。 |
| 1 | 3 | x=576, y=224, w=192, h=224 | product_manager-product_manager_presenting | 产品经理-演示 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“产品经理-演示”使用。 |
| 1 | 4 | x=768, y=224, w=192, h=224 | product_manager-product_manager_talking_negotiating | 产品经理-沟通谈判 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“产品经理-沟通谈判”使用。 |
| 1 | 5 | x=960, y=224, w=192, h=224 | product_manager-product_manager_stressed | 产品经理-压力状态 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“产品经理-压力状态”使用。 |
| 1 | 6 | x=1152, y=224, w=192, h=224 | product_manager-product_manager_celebrating | 产品经理-庆祝 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“产品经理-庆祝”使用。 |
| 1 | 7 | x=1344, y=224, w=192, h=224 | product_manager-product_manager_thinking_decision | 产品经理-思考决策 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“产品经理-思考决策”使用。 |
| 2 | 0 | x=0, y=448, w=192, h=224 | designer-designer_idle_front | 设计师-正面待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“设计师-正面待机”使用。 |
| 2 | 1 | x=192, y=448, w=192, h=224 | designer-designer_idle_right | 设计师-右向待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“设计师-右向待机”使用。 |
| 2 | 2 | x=384, y=448, w=192, h=224 | designer-designer_working | 设计师-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“设计师-工作”使用。 |
| 2 | 3 | x=576, y=448, w=192, h=224 | designer-designer_presenting | 设计师-演示 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“设计师-演示”使用。 |
| 2 | 4 | x=768, y=448, w=192, h=224 | designer-designer_talking_negotiating | 设计师-沟通谈判 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“设计师-沟通谈判”使用。 |
| 2 | 5 | x=960, y=448, w=192, h=224 | designer-designer_stressed | 设计师-压力状态 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“设计师-压力状态”使用。 |
| 2 | 6 | x=1152, y=448, w=192, h=224 | designer-designer_celebrating | 设计师-庆祝 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“设计师-庆祝”使用。 |
| 2 | 7 | x=1344, y=448, w=192, h=224 | designer-designer_thinking_decision | 设计师-思考决策 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“设计师-思考决策”使用。 |
| 3 | 0 | x=0, y=672, w=192, h=224 | marketing_operator-marketing_operator_idle_front | 市场运营-正面待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“市场运营-正面待机”使用。 |
| 3 | 1 | x=192, y=672, w=192, h=224 | marketing_operator-marketing_operator_idle_right | 市场运营-右向待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“市场运营-右向待机”使用。 |
| 3 | 2 | x=384, y=672, w=192, h=224 | marketing_operator-marketing_operator_working | 市场运营-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“市场运营-工作”使用。 |
| 3 | 3 | x=576, y=672, w=192, h=224 | marketing_operator-marketing_operator_presenting | 市场运营-演示 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“市场运营-演示”使用。 |
| 3 | 4 | x=768, y=672, w=192, h=224 | marketing_operator-marketing_operator_talking_negotiating | 市场运营-沟通谈判 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“市场运营-沟通谈判”使用。 |
| 3 | 5 | x=960, y=672, w=192, h=224 | marketing_operator-marketing_operator_stressed | 市场运营-压力状态 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“市场运营-压力状态”使用。 |
| 3 | 6 | x=1152, y=672, w=192, h=224 | marketing_operator-marketing_operator_celebrating | 市场运营-庆祝 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“市场运营-庆祝”使用。 |
| 3 | 7 | x=1344, y=672, w=192, h=224 | marketing_operator-marketing_operator_thinking_decision | 市场运营-思考决策 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“市场运营-思考决策”使用。 |
| 4 | 0 | x=0, y=896, w=192, h=224 | customer_success-customer_success_idle_front | 客户成功-正面待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“客户成功-正面待机”使用。 |
| 4 | 1 | x=192, y=896, w=192, h=224 | customer_success-customer_success_idle_right | 客户成功-右向待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“客户成功-右向待机”使用。 |
| 4 | 2 | x=384, y=896, w=192, h=224 | customer_success-customer_success_working | 客户成功-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“客户成功-工作”使用。 |
| 4 | 3 | x=576, y=896, w=192, h=224 | customer_success-customer_success_presenting | 客户成功-演示 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“客户成功-演示”使用。 |
| 4 | 4 | x=768, y=896, w=192, h=224 | customer_success-customer_success_talking_negotiating | 客户成功-沟通谈判 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“客户成功-沟通谈判”使用。 |
| 4 | 5 | x=960, y=896, w=192, h=224 | customer_success-customer_success_stressed | 客户成功-压力状态 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“客户成功-压力状态”使用。 |
| 4 | 6 | x=1152, y=896, w=192, h=224 | customer_success-customer_success_celebrating | 客户成功-庆祝 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“客户成功-庆祝”使用。 |
| 4 | 7 | x=1344, y=896, w=192, h=224 | customer_success-customer_success_thinking_decision | 客户成功-思考决策 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“客户成功-思考决策”使用。 |
| 5 | 0 | x=0, y=1120, w=192, h=224 | finance_legal_specialist-finance_legal_specialist_idle_front | 财务法务-正面待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“财务法务-正面待机”使用。 |
| 5 | 1 | x=192, y=1120, w=192, h=224 | finance_legal_specialist-finance_legal_specialist_idle_right | 财务法务-右向待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“财务法务-右向待机”使用。 |
| 5 | 2 | x=384, y=1120, w=192, h=224 | finance_legal_specialist-finance_legal_specialist_working | 财务法务-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“财务法务-工作”使用。 |
| 5 | 3 | x=576, y=1120, w=192, h=224 | finance_legal_specialist-finance_legal_specialist_presenting | 财务法务-演示 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“财务法务-演示”使用。 |
| 5 | 4 | x=768, y=1120, w=192, h=224 | finance_legal_specialist-finance_legal_specialist_talking_negotiating | 财务法务-沟通谈判 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“财务法务-沟通谈判”使用。 |
| 5 | 5 | x=960, y=1120, w=192, h=224 | finance_legal_specialist-finance_legal_specialist_stressed | 财务法务-压力状态 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“财务法务-压力状态”使用。 |
| 5 | 6 | x=1152, y=1120, w=192, h=224 | finance_legal_specialist-finance_legal_specialist_celebrating | 财务法务-庆祝 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“财务法务-庆祝”使用。 |
| 5 | 7 | x=1344, y=1120, w=192, h=224 | finance_legal_specialist-finance_legal_specialist_thinking_decision | 财务法务-思考决策 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“财务法务-思考决策”使用。 |
| 6 | 0 | x=0, y=1344, w=192, h=224 | investor_advisor_npc-investor_advisor_npc_idle_front | 投资人顾问 NPC-正面待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“投资人顾问 NPC-正面待机”使用。 |
| 6 | 1 | x=192, y=1344, w=192, h=224 | investor_advisor_npc-investor_advisor_npc_idle_right | 投资人顾问 NPC-右向待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“投资人顾问 NPC-右向待机”使用。 |
| 6 | 2 | x=384, y=1344, w=192, h=224 | investor_advisor_npc-investor_advisor_npc_working | 投资人顾问 NPC-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“投资人顾问 NPC-工作”使用。 |
| 6 | 3 | x=576, y=1344, w=192, h=224 | investor_advisor_npc-investor_advisor_npc_presenting | 投资人顾问 NPC-演示 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“投资人顾问 NPC-演示”使用。 |
| 6 | 4 | x=768, y=1344, w=192, h=224 | investor_advisor_npc-investor_advisor_npc_talking_negotiating | 投资人顾问 NPC-沟通谈判 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“投资人顾问 NPC-沟通谈判”使用。 |
| 6 | 5 | x=960, y=1344, w=192, h=224 | investor_advisor_npc-investor_advisor_npc_stressed | 投资人顾问 NPC-压力状态 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“投资人顾问 NPC-压力状态”使用。 |
| 6 | 6 | x=1152, y=1344, w=192, h=224 | investor_advisor_npc-investor_advisor_npc_celebrating | 投资人顾问 NPC-庆祝 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“投资人顾问 NPC-庆祝”使用。 |
| 6 | 7 | x=1344, y=1344, w=192, h=224 | investor_advisor_npc-investor_advisor_npc_thinking_decision | 投资人顾问 NPC-思考决策 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“投资人顾问 NPC-思考决策”使用。 |
| 7 | 0 | x=0, y=1568, w=192, h=224 | interview_candidate-interview_candidate_idle_front | 面试候选人-正面待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“面试候选人-正面待机”使用。 |
| 7 | 1 | x=192, y=1568, w=192, h=224 | interview_candidate-interview_candidate_idle_right | 面试候选人-右向待机 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“面试候选人-右向待机”使用。 |
| 7 | 2 | x=384, y=1568, w=192, h=224 | interview_candidate-interview_candidate_working | 面试候选人-工作 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“面试候选人-工作”使用。 |
| 7 | 3 | x=576, y=1568, w=192, h=224 | interview_candidate-interview_candidate_presenting | 面试候选人-演示 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“面试候选人-演示”使用。 |
| 7 | 4 | x=768, y=1568, w=192, h=224 | interview_candidate-interview_candidate_talking_negotiating | 面试候选人-沟通谈判 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“面试候选人-沟通谈判”使用。 |
| 7 | 5 | x=960, y=1568, w=192, h=224 | interview_candidate-interview_candidate_stressed | 面试候选人-压力状态 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“面试候选人-压力状态”使用。 |
| 7 | 6 | x=1152, y=1568, w=192, h=224 | interview_candidate-interview_candidate_celebrating | 面试候选人-庆祝 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“面试候选人-庆祝”使用。 |
| 7 | 7 | x=1344, y=1568, w=192, h=224 | interview_candidate-interview_candidate_thinking_decision | 面试候选人-思考决策 | EmployeeLayer | feet_center | 1x1 | 0.75x1.2 | 在 Startup Sim 2.5D Godot 表现层中作为“面试候选人-思考决策”使用。 |
