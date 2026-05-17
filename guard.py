def validate(changes, state):
    """校验StateGuard规则"""
    violations = []
    corrected = dict(changes)

    # 股权总和必须=1
    fe = changes.get("founder_equity", state["founder_equity"])
    ie = changes.get("investor_equity", 0) or 0
    op = changes.get("option_pool", 0) or 0
    total = fe + ie + op
    if total > 1.0:
        violations.append(f"股权总和{total}>1.0，已自动调整")
        corrected["founder_equity"] = round(fe - (total - 1.0), 6)

    # 融资后创始人持股红线（软警告，不硬拦截）
    if "founder_equity" in changes and changes["founder_equity"] < 0.34:
        violations.append("⚠️ 创始人持股已低于34%一票否决线")

    # 现金不能为负（除非是融资后正常支出）
    if changes.get("cash", state["cash"]) < -100:
        violations.append("现金低于-100万不合理，已限制")
        corrected["cash"] = -100

    return {
        "passed": len([v for v in violations if not v.startswith("⚠️")]) == 0,
        "violations": violations,
        "corrected": corrected,
        "message": "; ".join(violations) if violations else "通过",
    }
