-- Startup Sim Database Schema
-- Multi-session game with competitors support.

CREATE TABLE IF NOT EXISTS game_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL DEFAULT 'Player',
    scenario_id TEXT NOT NULL DEFAULT 'ai_customer_service_saas',
    current_month INTEGER NOT NULL DEFAULT 1,
    difficulty TEXT NOT NULL DEFAULT 'normal',
    status TEXT NOT NULL DEFAULT 'active',
    seed INTEGER NOT NULL DEFAULT 42,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS company_state (
    session_id INTEGER NOT NULL REFERENCES game_sessions(id),
    cash INTEGER NOT NULL DEFAULT 1000000,
    monthly_burn INTEGER NOT NULL DEFAULT 180000,
    mrr INTEGER NOT NULL DEFAULT 0,
    users INTEGER NOT NULL DEFAULT 0,
    product_score INTEGER NOT NULL DEFAULT 20,
    team_morale INTEGER NOT NULL DEFAULT 70,
    founder_equity INTEGER NOT NULL DEFAULT 100,
    board_control INTEGER NOT NULL DEFAULT 100,
    market_share INTEGER NOT NULL DEFAULT 0,
    reputation INTEGER NOT NULL DEFAULT 50,
    PRIMARY KEY (session_id)
);

CREATE TABLE IF NOT EXISTS competitors (
    session_id INTEGER NOT NULL REFERENCES game_sessions(id),
    name TEXT NOT NULL,
    strategy TEXT NOT NULL DEFAULT '',
    cash INTEGER NOT NULL DEFAULT 0,
    product_score INTEGER NOT NULL DEFAULT 0,
    market_share INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (session_id, name)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES game_sessions(id),
    month INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'medium',
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES game_sessions(id),
    month INTEGER NOT NULL,
    raw_input TEXT NOT NULL,
    action_plan_json TEXT NOT NULL DEFAULT '[]',
    result_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES game_sessions(id),
    month INTEGER NOT NULL,
    state_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS external_sessions (
    source TEXT NOT NULL,
    external_user_id TEXT NOT NULL,
    session_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    PRIMARY KEY (source, external_user_id)
);

CREATE TABLE IF NOT EXISTS role_memory_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES game_sessions(id),
    month INTEGER NOT NULL,
    role_id TEXT NOT NULL,
    role_name TEXT NOT NULL,
    fact TEXT NOT NULL,
    implication TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'settled-turn-facts',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
