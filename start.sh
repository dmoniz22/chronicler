#!/bin/bash
# Chronicler startup script
cd /home/dmoniz/projects/chronicler

# Start Neo4j if not running
if ! docker ps | grep -q chronicler_neo4j; then
    echo "Starting Neo4j..."
    docker start chronicler_neo4j
fi

# Activate venv and start API
source venv/bin/activate
echo "Starting Chronicler API on port 8004..."
python -m uvicorn backend.api:app --host 0.0.0.0 --port 8004 --reload

