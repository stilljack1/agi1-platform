import time
import random

class RevenueSandbox:
    def __init__(self):
        self.mode = "SANDBOX"
        self.balance = 0.0
        self.ledger = []

    def process_transaction(self, amount, source):
        """Simulates a payment gateway event."""
        if self.mode != "SANDBOX":
            raise PermissionError("LIVE TRANSACTIONS DISABLED")
        
        # Simulate Gateway Latency
        time.sleep(random.uniform(0.1, 0.4))
        
        # Update Ledger
        self.balance += amount
        self.ledger.append({"src": source, "amt": amount, "ts": time.time()})
        
        return {
            "status": "CAPTURED", 
            "id": f"ch_{int(time.time())}", 
            "new_balance": self.balance
        }

REVENUE_CORE = RevenueSandbox()
