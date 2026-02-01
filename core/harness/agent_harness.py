import time, random, sys, os
sys.path.append(os.getcwd())
from services.registry.agent_registry import heartbeat
from services.queue.task_queue import get_next_task
from core.intelligence.brain import CORTEX

class AgentHarness:
    def __init__(self, role, context):
        self.role = role
        self.context = context

    def run(self):
        print(f"🛡️ [HARNESS] {self.role} is now under Governance.")
        while True:
            heartbeat(self.role)
            task = get_next_task(self.role)
            
            # If no specific task, perform Autonomous R&D based on CEO Directive
            prompt = f"Execute next step for: {task[1] if task else 'General Mission'}"
            
            thought = CORTEX.think(prompt=prompt, context=self.context)
            
            if thought['status'] == 'SUCCESS':
                print(f"✅ [{self.role}] Executed: {thought['output'][:50]}...")
            
            # Anti-Collision Sleep (Jitter)
            time.sleep(random.uniform(20, 40))

if __name__ == "__main__":
    # Example usage for any agent
    role_name = sys.argv[1] if len(sys.argv) > 1 else "unnamed_agent"
    harness = AgentHarness(role_name, f"Role: {role_name}")
    harness.run()
