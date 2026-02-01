import os, time, subprocess

def clear():
    os.system("clear")

def deploy_cluster(path_pattern, name):
    os.makedirs("logs", exist_ok=True)
    print(f"Deploying {name} Cluster...")
    if not os.path.exists(path_pattern):
        print(f"Error: {path_pattern} not found.")
        return
    files = [f for f in os.listdir(path_pattern) if f.endswith(".py")]
    for f in files:
        full_path = os.path.join(path_pattern, f)
        role = f.replace(".py", "")
        log_file = open(f"logs/{role}.log", "a")
        subprocess.Popen(["python3", full_path], stdout=log_file, stderr=subprocess.STDOUT)
        print(f"   ACTIVE: {role}")
    print(f"Cluster {name} is now online.")
    input("Press Enter...")

def main():
    while True:
        clear()
        print("==========================================")
        print("     AGI-1 CONTROL CENTER v3.6")
        print("==========================================")
        print("1. [RESEARCH CORE]  (35 Agents)")
        print("2. [APP TEAM]       (15 Agents)")
        print("3. [EXECUTIVE]      (4 Agents)")
        print("9. [MONITOR]        Launch Monitor")
        print("0. [KILL]           Stop All")
        print("==========================================")
        choice = input("SELECT > ")
        if choice == "1": deploy_cluster("services/research_core", "Research")
        elif choice == "2": deploy_cluster("services/app_team", "App")
        elif choice == "3":
            for r in ["jack_strategy", "julia_ops", "singularity_exec", "guardrail_safety"]:
                log = open(f"logs/{r}.log", "a")
                subprocess.Popen(["python3", "services/worker/agent.py", "--role", r], stdout=log, stderr=subprocess.STDOUT)
            input("Executive Swarm Live. Press Enter...")
        elif choice == "9": os.system("./monitor_swarm.sh")
        elif choice == "0":
            os.system("pkill -f "services/"")
            os.system("pkill -f "agent.py"")
            print("Stopping...")
            time.sleep(1)

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    main()