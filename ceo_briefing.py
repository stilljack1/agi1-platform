import sqlite3
import os

DB = "agi1_persistence.db"

def get_briefing():
    if not os.path.exists(DB):
        print("❌ Persistence DB not found yet.")
        return

    conn = sqlite3.connect(DB); c = conn.cursor()
    
    # Get System Health
    c.execute("SELECT COUNT(*) FROM agent_registry WHERE status='ACTIVE'")
    active_count = c.fetchone()[0]
    
    # Get Top Performer (Evolutionary Tier 3)
    c.execute("SELECT role, tier, total_reward FROM agent_registry ORDER BY tier DESC, total_reward DESC LIMIT 1")
    top_agent = c.fetchone()
    
    # Get Quality Metric
    c.execute("SELECT AVG(kpi_score) FROM task_events")
    avg_quality = c.fetchone()[0] or 0.0

    print("\n" + "="*40)
    print("📈 AGI-1 CEO POST-DEPLOYMENT BRIEFING")
    print("="*40)
    print(f"🤖 Active Agents: {active_count}")
    print(f"💎 System Quality: {avg_quality:.4%}")
    if top_agent:
        print(f"🏆 Top Performer: {top_agent[0]} (Tier {top_agent[1]})")
    print(f"🧠 Meta-Learning: Active & Persistent")
    print("="*40)
    conn.close()

if __name__ == "__main__":
    get_briefing()
