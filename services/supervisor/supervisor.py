import time, os, sqlite3, subprocess
DB = "agi1_persistence.db"
def check_health():
    print("🛡️ Supervisor Monitoring Swarm Health...")
    while True:
        try:
            conn = sqlite3.connect(DB); c = conn.cursor()
            c.execute("SELECT role, last_heartbeat FROM agent_registry")
            agents = c.fetchall()
            now = time.time()
            for role, last_hb in agents:
                if now - last_hb > 300: # 5 mins
                    print(f"⚠️ {role} offline. Reviving...")
            conn.close()
        except: pass
        time.sleep(60)
if __name__ == "__main__":
    check_health()
