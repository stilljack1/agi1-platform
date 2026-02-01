import os
import time
import subprocess

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def deploy_cluster(path_pattern, name):
    print(f"\n🚀 Deploying {name} Cluster...")
    files = [f for f in os.listdir(path_pattern) if f.endswith('.py')]
    for f in files:
        full_path = os.path.join(path_pattern, f)
        role = f.replace('.py', '')
        subprocess.Popen(["python3", full_path], stdout=open(f"logs/{role}.log", 'a'), stderr=subprocess.STDOUT)
        print(f"   ✅ {role} online")
    print(f"\n✅ {name} Cluster Active.")
    input("Press Enter to continue...")

def main():
    while True:
        clear()
        print("==================================================")
        print("       AGI-1 MASTER CONTROL CENTER (v3.0)")
        print("==================================================")
        print("1. [RESEARCH CORE]  Activate ASI/Research Team (35)")
        print("2. [APP TEAM]       Activate Delivery Squad (15)")
        print("3. [EXECUTIVE]      Activate Core Swarm (4)")
        print("9. [MONITOR]        Launch Monitor")
        print("0. [KILL]           Emergency Stop All")
        print("==================================================")
        
        choice = input("SELECT > ")
        if choice == "1": deploy_cluster("services/research_core", "Research Core")
        elif choice == "2": deploy_cluster("services/app_team", "App Team")
        elif choice == "3": 
            os.system("./deploy_role.sh jack_strategy")
            os.system("./deploy_role.sh julia_ops")
            os.system("./deploy_role.sh singularity_exec")
            os.system("./deploy_role.sh guardrail_safety")
            input("Executive Swarm Live. Enter...")
        elif choice == "9": os.system("./monitor_swarm.sh")
        elif choice == "0": os.system("pkill -f 'services/'")

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    os.makedirs("pids", exist_ok=True)
    main()
