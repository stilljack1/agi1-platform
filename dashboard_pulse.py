import requests
import time
import os

def render_dashboard():
    os.system('clear')
    print("🏭 AGI-1 FACTORY LIVE PULSE")
    print("------------------------------------------------")
    try:
        # Pings the Control Plane API
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        data = response.json()
        print(f"{'ROLE':<20} | {'AVG KPI':<10} | {'TASKS':<10}")
        print("-" * 45)
        for row in data:
            # Threshold Check
            status_icon = "🟢" if row['avg_kpi'] >= 0.9899 else "🟡"
            print(f"{row['role']:<20} | {row['avg_kpi']:<10.4f} | {row['tasks']:<10} {status_icon}")
    except Exception as e:
        print("📡 Waiting for Control Plane to initialize...")

if __name__ == "__main__":
    while True:
        render_dashboard()
        time.sleep(5)
