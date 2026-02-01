import sqlite3, json
DB = "agi1_persistence.db"

def recommend_strategy(role):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT task_input FROM task_events WHERE role=? AND kpi_score > 0.9 ORDER BY id DESC LIMIT 5", (role,))
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows] if rows else None
