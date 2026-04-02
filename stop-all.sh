#!/bin/bash
# Chronicler - Stop All Services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${YELLOW}Stopping Chronicler services...${NC}"

# Stop frontend
if [ -f ".frontend.pid" ]; then
    kill $(cat .frontend.pid) 2>/dev/null || true
    rm .frontend.pid
    echo -e "${GREEN}✓ Frontend stopped${NC}"
fi

# Stop API
if [ -f ".api.pid" ]; then
    kill $(cat .api.pid) 2>/dev/null || true
    rm .api.pid
    echo -e "${GREEN}✓ API stopped${NC}"
fi

# Stop Neo4j
read -p "Stop Neo4j container? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker stop chronicler_neo4j 2>/dev/null || true
    echo -e "${GREEN}✓ Neo4j stopped${NC}"
fi

echo -e "${GREEN}✅ All services stopped${NC}"
