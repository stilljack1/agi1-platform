#!/bin/bash
ROLE=$1
if [ -z "$ROLE" ]; then echo "Usage: ./deploy_role.sh <role>"; exit 1; fi

mkdir -p logs pids

# Kill existing if running
if [ -f "pids/$ROLE.pid" ]; then
    PID=$(cat pids/$ROLE.pid)
    kill $PID 2>/dev/null
fi

# CRITICAL FIX: Add current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Launch with explicit python module call to avoid path issues
nohup python3 services/worker/agent.py --role "$ROLE" > logs/$ROLE.log 2>&1 &
echo $! > pids/$ROLE.pid

echo "✅ $ROLE live (PID $(cat pids/$ROLE.pid))"
