import sqlite3, json, time
DB = "agi1_persistence.db"

def add_task(role, task_data):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("INSERT INTO task_events (role, task_input, status) VALUES (?, ?, 'PENDING')", (role, json.dumps(task_data)))
    conn.commit(); conn.close()

def get_next_task(role):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT id, task_input FROM task_events WHERE role=? AND status='PENDING' ORDER BY id ASC LIMIT 1", (role,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE task_events SET status='PROCESSING' WHERE id=?", (row[0],))
        conn.commit()
    conn.close()
    return row
