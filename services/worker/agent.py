import asyncio
import argparse
import random
import time
import sys
import os

# Ensure the core modules are importable
sys.path.append(os.getcwd())

from core.arbitration.engine import ARBITRATOR
from core.persistence.database import SessionLocal, TaskEvent
from core.lqm.evaluator import enforce_kpi

async def start_agent(role):
    db = SessionLocal()
    print(f"🚀 [INIT] {role.upper()} active. Monitoring for directives...")

    while True:
        start_time = time.time()
        
        # 1. Consensus Arbitration
        decision = await ARBITRATOR.run_arbitration(f"Routine optimization for {role}")
        
        # 2. KPI Enforcement (LQM Guardrail)
        status = enforce_kpi(decision['confidence'])
        latency = time.time() - start_time

        # 3. Persistent Logging to Database
        event = TaskEvent(
            role=role,
            task_input=f"Auto-task {int(time.time())}",
            status=status,
            kpi_score=decision['confidence'],
            latency=latency,
            arbitration_winner=decision['winner']
        )
        db.add(event)
        db.commit()

        print(f"📊 [{role.upper()}] Status: {status} | Winner: {decision['winner']} | Latency: {latency:.4f}")
        await asyncio.sleep(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True)
    args = parser.parse_args()
    asyncio.run(start_agent(args.role))
