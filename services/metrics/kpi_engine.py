import sqlite3
DB = "agi1_persistence.db"

def get_swarm_metrics():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT COUNT(*), AVG(kpi_score) FROM task_events")
    count, avg_kpi = c.fetchone()
    conn.close()
    return {"throughput": count, "avg_quality": avg_kpi}
