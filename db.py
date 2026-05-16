"""Database layer — SQLite state persistence with named column access.

Fixes applied:
  - UNIQUE constraint on investors.name prevents duplicate inserts
  - Column-name constants replace hardcoded numeric indices everywhere
  - state_row_to_dict() / investor_row_to_dict() map rows to named dicts
  - Bulk investor insert via executemany
"""

import json
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "startup_state.db")

# ---------------------------------------------------------------------------
# Column-name constants — single source of truth for row position
# ---------------------------------------------------------------------------

# company_state table (id=1 singleton row)
STATE_COLS = [
    "id",              # 0
    "company_name",    # 1
    "cash",            # 2
    "burn_rate",       # 3
    "revenue_mrr",     # 4
    "team_size",       # 5
    "team_morale",     # 6
    "product_stage",   # 7
    "founder_equity",  # 8
    "investor_equity", # 9
    "option_pool",     # 10
    "round",           # 11
    "turn",            # 12
    "market_sentiment",# 13
    "track",           # 14
]

# investors table
INVESTOR_COLS = [
    "id",              # 0
    "name",            # 1
    "type",            # 2
    "check_size_min",  # 3
    "check_size_max",  # 4
    "focus_stage",     # 5
    "trust_score",     # 6
    "memory",          # 7
]

# events_log table
EVENT_COLS = [
    "id",             # 0
    "turn",           # 1
    "event_type",     # 2
    "description",    # 3
    "data",           # 4
]

# ---------------------------------------------------------------------------
# Row → dict helpers (single source of truth for index mapping)
# ---------------------------------------------------------------------------

def state_row_to_dict(row: tuple) -> dict:
    """Convert a raw company_state tuple into a named dict."""
    if row is None:
        return {}
    return dict(zip(STATE_COLS, row))


def investor_row_to_dict(row: tuple) -> dict:
    """Convert a raw investors tuple into a named dict."""
    if row is None:
        return {}
    return dict(zip(INVESTOR_COLS, row))


# ---------------------------------------------------------------------------
# Schema (UNIQUE on investors.name prevents duplicate inserts)
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS company_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    company_name TEXT,
    cash REAL,              -- 万元
    burn_rate REAL,         -- 万元/月
    revenue_mrr REAL,       -- 万元/月
    team_size INTEGER,
    team_morale INTEGER,    -- 0-100
    product_stage TEXT,     -- idea/mvp/pmf/scaling
    founder_equity REAL,    -- 0.0-1.0
    investor_equity REAL,   -- 0.0-1.0
    option_pool REAL,       -- 0.0-1.0
    round TEXT,             -- angel/A/B/C
    turn INTEGER DEFAULT 1,
    market_sentiment TEXT,  -- hot/neutral/cold
    track TEXT              -- 赛道
);

CREATE TABLE IF NOT EXISTS investors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT,              -- aggressive/conservative/strategic/financial
    check_size_min REAL,    -- 万元
    check_size_max REAL,
    focus_stage TEXT,       -- angel/A/B/C
    trust_score REAL DEFAULT 50.0,  -- 0-100
    memory TEXT DEFAULT '[]'        -- JSON list of past interactions
);

CREATE TABLE IF NOT EXISTS events_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turn INTEGER,
    event_type TEXT,
    description TEXT,
    data TEXT
);
"""

# ---------------------------------------------------------------------------
# Pre-seeded investors
# ---------------------------------------------------------------------------

_DEFAULT_INVESTORS = [
    ("红杉激进", "aggressive", 100, 2000, "angel"),
    ("经纬保守", "conservative", 200, 5000, "A"),
    ("腾讯战略", "strategic", 500, 10000, "A"),
    ("高瓴财务", "financial", 1000, 50000, "B"),
    ("真格天使", "aggressive", 50, 500, "angel"),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_db():
    """Create tables + seed initial state if empty.  Safe to call repeatedly."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    # Seed company state (singleton row)
    conn.execute(
        "INSERT OR IGNORE INTO company_state "
        "(id, company_name, cash, burn_rate, revenue_mrr, team_size, team_morale, "
        " product_stage, founder_equity, investor_equity, option_pool, round, "
        " market_sentiment, track) "
        "VALUES (1, 'Startup', 50, 10, 0, 3, 70, 'mvp', 1.0, 0.0, 0.0, "
        "        'seed', 'hot', '')"
    )

    # Seed investors (UNIQUE constraint on name prevents duplicates)
    conn.executemany(
        "INSERT OR IGNORE INTO investors "
        "(name, type, check_size_min, check_size_max, focus_stage) "
        "VALUES (?, ?, ?, ?, ?)",
        _DEFAULT_INVESTORS,
    )

    conn.commit()
    return conn


def get_state():
    """Return the raw company_state row (tuple).  Prefer state_row_to_dict()."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT * FROM company_state WHERE id = 1").fetchone()
    conn.close()
    return row


def get_investors():
    """Return all investor rows (list of tuples).  Prefer investor_row_to_dict()."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT * FROM investors").fetchall()
    conn.close()
    return rows


def update_state(**kwargs):
    """Update company_state columns by keyword argument."""
    if not kwargs:
        return
    conn = sqlite3.connect(DB_PATH)
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values())
    conn.execute(f"UPDATE company_state SET {sets} WHERE id = 1", vals)
    conn.commit()
    conn.close()


def update_investor(inv_id: int, **kwargs):
    """Update an investor row by id."""
    if not kwargs:
        return
    conn = sqlite3.connect(DB_PATH)
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [inv_id]
    conn.execute(f"UPDATE investors SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()


def log_event(turn: int, event_type: str, description: str, data=None):
    """Append a row to the events_log."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO events_log (turn, event_type, description, data) VALUES (?, ?, ?, ?)",
        (turn, event_type, description, json.dumps(data) if data else None),
    )
    conn.commit()
    conn.close()
