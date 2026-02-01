import sqlite3, time
DB = "agi1_persistence.db"

def init_registry():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS agent_registry (role TEXT PRIMARY KEY, status TEXT, last_heartbeat REAL, kpi_score REAL DEFAULT 1.0)")
    conn.commit(); conn.close()

def heartbeat(role):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO agent_registry (role, status, last_heartbeat) VALUES (?, 'ACTIVE', ?)", (role, time.time()))
    conn.commit(); conn.close()
