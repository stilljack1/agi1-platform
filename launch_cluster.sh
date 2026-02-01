#!/bin/bash
CLUSTER=$1
mkdir -p logs
echo "🚀 Deploying Cluster: $CLUSTER..."
for f in services/$CLUSTER/*.py; do
    role=$(basename "$f" .py)
    nohup python3 "$f" > logs/"$role".log 2>&1 &
    echo "   [ONLINE] $role"
done
echo "✅ Cluster $CLUSTER is now operating under Singularity Protocol."
