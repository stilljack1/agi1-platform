from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.persistence.database import SessionLocal, TaskEvent
from sqlalchemy import func
import asyncio
import os

app = FastAPI(title="AGI-1 Control Plane v2.0")

# --- DATA MODELS ---
class Directive(BaseModel):
    executive: str
    intent: str
    priority: int = 1

# --- API ENDPOINTS ---
@app.post("/directive/issue")
async def issue_directive(cmd: Directive):
    """Injects a high-priority executive order into the swarm."""
    print(f"👑 [DIRECTIVE] {cmd.executive} commands: {cmd.intent}")
    
    # Log the directive as a 'SEED' event for the agents to pick up
    db = SessionLocal()
    event = TaskEvent(
        role=cmd.executive.lower(),
        task_input=f"DIRECTIVE: {cmd.intent}",
        status="PENDING",
        kpi_score=1.0,
        latency=0.0,
        arbitration_winner="User-Override"
    )
    db.add(event)
    db.commit()
    db.close()
    
    return {"status": "Accepted", "propagation": "Immediate"}

@app.get("/health")
async def get_health():
    db = SessionLocal()
    stats = db.query(
        TaskEvent.role, 
        func.avg(TaskEvent.kpi_score),
        func.count(TaskEvent.id)
    ).group_by(TaskEvent.role).all()
    db.close()
    return [{"role": s[0], "avg_kpi": round(s[1], 4), "tasks": s[2]} for s in stats]
