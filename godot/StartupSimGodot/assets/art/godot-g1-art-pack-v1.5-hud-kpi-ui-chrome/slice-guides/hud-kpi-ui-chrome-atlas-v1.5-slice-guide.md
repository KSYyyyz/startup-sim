# hud-kpi-ui-chrome-atlas-v1.5 Slice Guide

鐢ㄩ€旓細缁?Godot 闆嗘垚浼氳瘽鏌ユ壘姣忎釜 atlas cell 鐨勮涔夈€佸眰绾с€侀敋鐐瑰拰鍗犳牸淇℃伅锛岄伩鍏嶆寜鍧愭爣纭寽銆?

- Atlas: `exports/hud-kpi-ui-chrome-atlas-v1.5.png`
- Grid: 8 columns x 4 rows
- Cell: 224x224 px
- Individual PNG directory: `exports/ui`

| Row | Col | Region | ID | 涓枃鍚嶇О | 鎺ㄨ崘灞傜骇 | 閿氱偣 | 閫昏緫鍗犳牸 | 瑙嗚灏哄 | 鐢ㄩ€?|
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 0 | x=0, y=0, w=224, h=224 | kpi_icons-cash_stack | 鐜伴噾 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滅幇閲戔€濅娇鐢ㄣ€?|
| 0 | 1 | x=224, y=0, w=224, h=224 | kpi_icons-cash_support_clock | 鐜伴噾娴佸彲鏀拺鏃堕棿 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滅幇閲戞祦鍙敮鎾戞椂闂粹€濅娇鐢ㄣ€?|
| 0 | 2 | x=448, y=0, w=224, h=224 | kpi_icons-mrr_revenue_chart | MRR 鏀跺叆 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€淢RR 鏀跺叆鈥濅娇鐢ㄣ€?|
| 0 | 3 | x=672, y=0, w=224, h=224 | kpi_icons-users_customer_group | 鐢ㄦ埛鏁伴噺 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滅敤鎴锋暟閲忊€濅娇鐢ㄣ€?|
| 0 | 4 | x=896, y=0, w=224, h=224 | kpi_icons-product_box | 浜у搧杩涘害 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滀骇鍝佽繘搴︹€濅娇鐢ㄣ€?|
| 0 | 5 | x=1120, y=0, w=224, h=224 | kpi_icons-reputation_star | 澹拌獕 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滃０瑾夆€濅娇鐢ㄣ€?|
| 0 | 6 | x=1344, y=0, w=224, h=224 | kpi_icons-stability_shield | 绋冲畾鎬?| HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滅ǔ瀹氭€р€濅娇鐢ㄣ€?|
| 0 | 7 | x=1568, y=0, w=224, h=224 | kpi_icons-team_pressure_gauge | 鍥㈤槦鍘嬪姏 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滃洟闃熷帇鍔涒€濅娇鐢ㄣ€?|
| 1 | 0 | x=0, y=224, w=224, h=224 | trend_status_icons-trend_up | 涓婂崌瓒嬪娍 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滀笂鍗囪秼鍔库€濅娇鐢ㄣ€?|
| 1 | 1 | x=224, y=224, w=224, h=224 | trend_status_icons-trend_down | 涓嬮檷瓒嬪娍 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滀笅闄嶈秼鍔库€濅娇鐢ㄣ€?|
| 1 | 2 | x=448, y=224, w=224, h=224 | trend_status_icons-trend_flat | 鎸佸钩瓒嬪娍 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滄寔骞宠秼鍔库€濅娇鐢ㄣ€?|
| 1 | 3 | x=672, y=224, w=224, h=224 | trend_status_icons-warning | 璀﹀憡 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滆鍛娾€濅娇鐢ㄣ€?|
| 1 | 4 | x=896, y=224, w=224, h=224 | trend_status_icons-goal_completed | 鐩爣瀹屾垚 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滅洰鏍囧畬鎴愨€濅娇鐢ㄣ€?|
| 1 | 5 | x=1120, y=224, w=224, h=224 | trend_status_icons-risk_spike | 椋庨櫓鍔犲墽 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滈闄╁姞鍓р€濅娇鐢ㄣ€?|
| 1 | 6 | x=1344, y=224, w=224, h=224 | trend_status_icons-opportunity | 鏈轰細 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滄満浼氣€濅娇鐢ㄣ€?|
| 1 | 7 | x=1568, y=224, w=224, h=224 | trend_status_icons-churn_leak | 鐢ㄦ埛娴佸け | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滅敤鎴锋祦澶扁€濅娇鐢ㄣ€?|
| 2 | 0 | x=0, y=448, w=224, h=224 | operations_chrome-button_normal | 鏅€氭寜閽簳鏉?| HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滄櫘閫氭寜閽簳鏉库€濅娇鐢ㄣ€?|
| 2 | 1 | x=224, y=448, w=224, h=224 | operations_chrome-button_hover | 鎮仠鎸夐挳搴曟澘 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滄偓鍋滄寜閽簳鏉库€濅娇鐢ㄣ€?|
| 2 | 2 | x=448, y=448, w=224, h=224 | operations_chrome-button_pressed | 鎸変笅鎸夐挳搴曟澘 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滄寜涓嬫寜閽簳鏉库€濅娇鐢ㄣ€?|
| 2 | 3 | x=672, y=448, w=224, h=224 | operations_chrome-button_disabled | 绂佺敤鎸夐挳搴曟澘 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滅鐢ㄦ寜閽簳鏉库€濅娇鐢ㄣ€?|
| 2 | 4 | x=896, y=448, w=224, h=224 | operations_chrome-selected_tab | 閫変腑鏍囩搴曟澘 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滈€変腑鏍囩搴曟澘鈥濅娇鐢ㄣ€?|
| 2 | 5 | x=1120, y=448, w=224, h=224 | operations_chrome-badge_chip | 寰界珷鑺墖 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滃窘绔犺姱鐗団€濅娇鐢ㄣ€?|
| 2 | 6 | x=1344, y=448, w=224, h=224 | operations_chrome-divider_line | 鍒嗗壊绾?| HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滃垎鍓茬嚎鈥濅娇鐢ㄣ€?|
| 2 | 7 | x=1568, y=448, w=224, h=224 | operations_chrome-panel_corner | 闈㈡澘杞 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滈潰鏉胯浆瑙掆€濅娇鐢ㄣ€?|
| 3 | 0 | x=0, y=672, w=224, h=224 | report_chrome-success_card_accent | 鎴愬姛鍗＄墖寮鸿皟杈?| HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滄垚鍔熷崱鐗囧己璋冭竟鈥濅娇鐢ㄣ€?|
| 3 | 1 | x=224, y=672, w=224, h=224 | report_chrome-warning_card_accent | 璀﹀憡鍗＄墖寮鸿皟杈?| HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滆鍛婂崱鐗囧己璋冭竟鈥濅娇鐢ㄣ€?|
| 3 | 2 | x=448, y=672, w=224, h=224 | report_chrome-risk_card_accent | 椋庨櫓鍗＄墖寮鸿皟杈?| HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滈闄╁崱鐗囧己璋冭竟鈥濅娇鐢ㄣ€?|
| 3 | 3 | x=672, y=672, w=224, h=224 | report_chrome-opportunity_card_accent | 鏈轰細鍗＄墖寮鸿皟杈?| HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滄満浼氬崱鐗囧己璋冭竟鈥濅娇鐢ㄣ€?|
| 3 | 4 | x=896, y=672, w=224, h=224 | report_chrome-achievement_medal | 鎴愬氨濂栫珷 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滄垚灏卞绔犫€濅娇鐢ㄣ€?|
| 3 | 5 | x=1120, y=672, w=224, h=224 | report_chrome-failure_badge | 澶辫触寰界珷 | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滃け璐ュ窘绔犫€濅娇鐢ㄣ€?|
| 3 | 6 | x=1344, y=672, w=224, h=224 | report_chrome-progress_bar_frame | 杩涘害鏉℃ | HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滆繘搴︽潯妗嗏€濅娇鐢ㄣ€?|
| 3 | 7 | x=1568, y=672, w=224, h=224 | report_chrome-right_panel_header | 鍙充晶闈㈡澘鏍囬鏉?| HudLayer | center | 1x1 | 1x1 | 鍦?Startup Sim Godot 涓綔涓衡€滃彸渚ч潰鏉挎爣棰樻潯鈥濅娇鐢ㄣ€?|
