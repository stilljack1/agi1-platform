#!/bin/bash
echo "🐝 AGI-1 HIVE ANALYTICS - $(date)"
echo "------------------------------------------------"
printf "%-20s %-10s %-10s %-10s\n" "ROLE" "KPI AVG" "WINNER" "STATUS"
echo "------------------------------------------------"

# This pulls the last state of each role from the persistence DB
python3 -c '
from core.persistence.database import SessionLocal, TaskEvent
from sqlalchemy import func
db = SessionLocal()
stats = db.query(TaskEvent.role, func.avg(TaskEvent.kpi_score), TaskEvent.arbitration_winner, TaskEvent.status)\
          .group_by(TaskEvent.role).all()
for s in stats:
    print(f"{s[0]:<20} {s[1]:<10.4f} {s[2]:<10} {s[3]:<10}")
'
