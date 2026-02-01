import asyncio
import argparse
import time
import sys
import os

# Path Fix
sys.path.append(os.getcwd())

from services.revenue.engine import REVENUE_CORE
from core.persistence.database import SessionLocal, TaskEvent

async def start_revenue_stream():
    print(f"💰 [REVENUE AGENT] Online. Sandbox Mode: ACTIVE")
    db = SessionLocal()

    while True:
        # Simulate Finding a Lead & Closing a Deal
        deal_value = random.choice([49.00, 199.00, 999.00])
        client = f"Client_{int(time.time())}"
        
        # Execute Transaction
        result = REVENUE_CORE.process_transaction(deal_value, client)
        
        # Log to Corporate Memory
        event = TaskEvent(
            role="revenue_agent",
            task_input=f"CHARGE: {client} | ${deal_value}",
            status="PASS",
            kpi_score=1.0, # Money is always perfect
            latency=0.2,
            arbitration_winner="Stripe-Mock"
        )
        db.add(event)
        db.commit()
        
        print(f"💵 [SALE] +${deal_value} | Balance: ${result['new_balance']:.2f}")
        await asyncio.sleep(5) # Closing deals takes time

if __name__ == "__main__":
    import random
    try:
        asyncio.run(start_revenue_stream())
    except KeyboardInterrupt:
        pass
