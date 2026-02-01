import sqlite3
DB_PATH = "agi1_persistence.db"
SPRINT_PLAN = {
    "DAY_1": {"FOCUS": "Architecture & Scope", "TASKS": ["Lock MVP Features", "Finalize Schema", "Setup Frontend Shell"]},
    "DAY_2": {"FOCUS": "Backend & API", "TASKS": ["Auth Logic", "Agent Router API", "Memory persistence integration"]},
    "DAY_3": {"FOCUS": "Admin Panel", "TASKS": ["KPI Dashboard", "Agent Status UI", "Promotion Panel"]},
    "DAY_4": {"FOCUS": "App Core", "TASKS": ["User Login", "Task Submission UI", "Response Streaming"]},
    "DAY_5": {"FOCUS": "Website & Docs", "TASKS": ["Landing Page", "Pricing Integration", "API Docs"]},
    "DAY_6": {"FOCUS": "Intelligence", "TASKS": ["Meta-Learning Wiring", "Evaluation Layer Benchmark"]},
    "DAY_7": {"FOCUS": "Feature Freeze", "TASKS": ["Bug Hardening", "Security Audit", "Performance Tuning"]},
    "DAY_8": {"FOCUS": "Cloud Deploy", "TASKS": ["Dockerize", "AWS/Railway Migration", "SSL & Domain"]},
    "DAY_9": {"FOCUS": "Launch", "TASKS": ["Beta User Invite", "Smoke Tests", "Public Release"]}
}
def load():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS sprint_calendar (day TEXT, focus TEXT, task TEXT, status TEXT DEFAULT 'PENDING')")
    for day, data in SPRINT_PLAN.items():
        for t in data["TASKS"]:
            c.execute("INSERT INTO sprint_calendar (day, focus, task) VALUES (?, ?, ?)", (day, data["FOCUS"], t))
    conn.commit(); conn.close()
    print("✅ 9-Day Sprint Calendar Injected.")
if __name__ == "__main__":
    load()
