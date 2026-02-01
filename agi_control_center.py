import os
import time
import subprocess

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def deploy_cluster(path_pattern, name):
    print(f"\n🚀 Deploying {name} Cluster...")
    files = [f for f in os.listdir(path_pattern) if f.endswith('.py')]
    print(f"Found {len(files)} agents.")
    for f in files:
        full_path = os.path.join(path_pattern, f)
        role = f.replace('.py', '')
        subprocess.Popen(["python3", full_path], stdout=open(f"logs/{role}.log", 'a'), stderr=subprocess.STDOUT)
        print(f"   ✅ {role} online")
    print(f"\n✅ {name} Cluster Active.")
    input("Press Enter...")

def main():
    while True:
        clear()
        print("=== AGI-1 MASTER CONTROL ===")
        print("1. [APP TEAM] Deploy")
        print("2. [RESEARCH] Deploy")
        print("3. [CORE] Deploy Executive Swarm")
        print("9. [MONITOR] Launch Monitor")
        print("0. [KILL] Stop All")
        choice = input("SELECT > ")
        if choice == "1": deploy_cluster("services/app_team", "App Team")
        elif choice == "3": os.system("./deploy_role.sh jack_strategy")
        elif choice == "9": os.system("./monitor_swarm.sh")
        elif choice == "0": os.system("pkill -f 'services/'")

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    main()
