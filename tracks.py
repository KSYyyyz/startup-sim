"""Shared track (赛道) definitions — single source of truth for main.py and feishu_adapter.py."""

TRACKS = {
    "1": ("AI Agent", "赛道火热，投资人兴趣高，但估值泡沫风险大"),
    "2": ("SaaS工具", "市场稳定，增长慢但现金流好，适合保守型投资人"),
    "3": ("消费硬件", "烧钱快，天花板高，需要大量融资"),
    "4": ("生物医药", "周期长，门槛极高，但一旦成功回报惊人"),
}

DEFAULT_TRACK = "通用科技"


def resolve_track(choice: str) -> str:
    """Resolve a user choice (digit, track name, or custom) to a track name."""
    choice = choice.strip()
    if choice in TRACKS:
        return TRACKS[choice][0]
    return choice or DEFAULT_TRACK
