# business-event-feedback-bubble-atlas-v1.6 Slice Guide

用途：给 Godot 集成会话查找每个 atlas cell 的语义、层级、锚点和占格信息，避免按坐标硬猜。

- Atlas: `exports/business-event-feedback-bubble-atlas-v1.6.png`
- Grid: 8 columns x 4 rows
- Cell: 224x224 px
- Individual PNG directory: `exports/bubbles`

| Row | Col | Region | ID | 中文名称 | 推荐层级 | 锚点 | 逻辑占格 | 视觉尺寸 | 用途 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=224, h=224 | employee_bubbles-idea_bulb_bubble | 灵感气泡 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“灵感气泡”使用。 |
| 0 | 1 | x=224, y=0, w=224, h=224 | employee_bubbles-fatigue_sleep_bubble | 疲劳睡眠气泡 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“疲劳睡眠气泡”使用。 |
| 0 | 2 | x=448, y=0, w=224, h=224 | employee_bubbles-stress_pressure_bubble | 压力气泡 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“压力气泡”使用。 |
| 0 | 3 | x=672, y=0, w=224, h=224 | employee_bubbles-training_book_bubble | 训练学习气泡 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“训练学习气泡”使用。 |
| 0 | 4 | x=896, y=0, w=224, h=224 | employee_bubbles-morale_smile_bubble | 士气气泡 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“士气气泡”使用。 |
| 0 | 5 | x=1120, y=0, w=224, h=224 | employee_bubbles-conflict_sparks_bubble | 冲突气泡 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“冲突气泡”使用。 |
| 0 | 6 | x=1344, y=0, w=224, h=224 | employee_bubbles-sick_health_bubble | 健康异常气泡 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“健康异常气泡”使用。 |
| 0 | 7 | x=1568, y=0, w=224, h=224 | employee_bubbles-focus_work_bubble | 专注工作气泡 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“专注工作气泡”使用。 |
| 1 | 0 | x=0, y=224, w=224, h=224 | business_events-customer_complaint | 客户投诉 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“客户投诉”使用。 |
| 1 | 1 | x=224, y=224, w=224, h=224 | business_events-customer_praise | 客户好评 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“客户好评”使用。 |
| 1 | 2 | x=448, y=224, w=224, h=224 | business_events-competitor_alert | 竞品预警 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“竞品预警”使用。 |
| 1 | 3 | x=672, y=224, w=224, h=224 | business_events-cash_crunch | 现金流紧张 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“现金流紧张”使用。 |
| 1 | 4 | x=896, y=224, w=224, h=224 | business_events-product_breakthrough | 产品突破 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“产品突破”使用。 |
| 1 | 5 | x=1120, y=224, w=224, h=224 | business_events-investor_interest | 投资人兴趣 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“投资人兴趣”使用。 |
| 1 | 6 | x=1344, y=224, w=224, h=224 | business_events-server_outage | 服务器故障 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“服务器故障”使用。 |
| 1 | 7 | x=1568, y=224, w=224, h=224 | business_events-hiring_candidate | 招聘候选人 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“招聘候选人”使用。 |
| 2 | 0 | x=0, y=448, w=224, h=224 | floating_metric_fx-money_gain_burst | 现金增加浮层 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“现金增加浮层”使用。 |
| 2 | 1 | x=224, y=448, w=224, h=224 | floating_metric_fx-money_loss_burst | 现金减少浮层 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“现金减少浮层”使用。 |
| 2 | 2 | x=448, y=448, w=224, h=224 | floating_metric_fx-mrr_growth_pulse | MRR 增长脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“MRR 增长脉冲”使用。 |
| 2 | 3 | x=672, y=448, w=224, h=224 | floating_metric_fx-user_growth_pulse | 用户增长脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“用户增长脉冲”使用。 |
| 2 | 4 | x=896, y=448, w=224, h=224 | floating_metric_fx-product_progress_pulse | 产品进度脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“产品进度脉冲”使用。 |
| 2 | 5 | x=1120, y=448, w=224, h=224 | floating_metric_fx-churn_loss_pulse | 流失损失脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“流失损失脉冲”使用。 |
| 2 | 6 | x=1344, y=448, w=224, h=224 | floating_metric_fx-risk_warning_pulse | 风险警告脉冲 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“风险警告脉冲”使用。 |
| 2 | 7 | x=1568, y=448, w=224, h=224 | floating_metric_fx-reputation_gain_sparkle | 声誉提升闪光 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“声誉提升闪光”使用。 |
| 3 | 0 | x=0, y=672, w=224, h=224 | review_markers-board_meeting_marker | 董事会会议标记 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“董事会会议标记”使用。 |
| 3 | 1 | x=224, y=672, w=224, h=224 | review_markers-monthly_report_stamp | 月报标记 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“月报标记”使用。 |
| 3 | 2 | x=448, y=672, w=224, h=224 | review_markers-objective_milestone | 目标里程碑 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“目标里程碑”使用。 |
| 3 | 3 | x=672, y=672, w=224, h=224 | review_markers-crisis_review | 危机复盘 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“危机复盘”使用。 |
| 3 | 4 | x=896, y=672, w=224, h=224 | review_markers-opportunity_review | 机会复盘 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“机会复盘”使用。 |
| 3 | 5 | x=1120, y=672, w=224, h=224 | review_markers-achievement_unlock | 成就解锁 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“成就解锁”使用。 |
| 3 | 6 | x=1344, y=672, w=224, h=224 | review_markers-failed_strategy | 策略失败 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“策略失败”使用。 |
| 3 | 7 | x=1568, y=672, w=224, h=224 | review_markers-next_month_pressure | 下月压力 | FeedbackFxLayer | center | 1x1 | 1x1 | 在 Startup Sim Godot 中作为“下月压力”使用。 |
