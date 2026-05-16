"""Startup Sim configuration. No API keys needed for Phase 1A (mock LLM)."""
import os
from pathlib import Path

# Project root
ROOT_DIR = Path(__file__).parent.resolve()
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "startup_sim.db"
SCENARIOS_PATH = DATA_DIR / "scenarios.yaml"

# Mock mode — no real LLM calls in Phase 1A
USE_MOCK = True

# LLM config (for future phases)
LLM_CONFIG = {
    "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
    "base_url": "https://api.deepseek.com/v1",
    "model": "deepseek-chat",
}

# Game settings
MAX_TURNS = 12
MAX_ACTIONS_PER_TURN = 5
