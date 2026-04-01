#!/bin/bash
# Chronicler Master Startup Script
# Starts Neo4j, Backend API, and Frontend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "📚 Chronicler - Starting Services"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

check_port() {
    local port=$1
    if lsof -Pi :"$port" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 1. Start Neo4j
echo -e "\n${YELLOW}🕸️ Starting Neo4j...${NC}"
if docker ps | grep -q "chronicler_neo4j"; then
    echo -e "${GREEN}✓ Neo4j already running${NC}"
elif docker ps -a | grep -q "chronicler_neo4j"; then
    docker start chronicler_neo4j
    echo -e "${GREEN}✓ Neo4j started${NC}"
else
    echo -e "${YELLOW}Creating Neo4j container...${NC}"
    docker run -d \
        --name chronicler_neo4j \
        -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/chronicler123 \
        neo4j:5.14.0
    echo -e "${GREEN}✓ Neo4j created and started${NC}"
fi
sleep 3

# 2. Re-index vault if needed
echo -e "\n${YELLOW}📂 Setting up vault...${NC}"
VAULT_PATH="/home/dmoniz/Documents/obsidian/Obsidian/Etheria/The Ehteria Chronicles"
if [ -d "$VAULT_PATH" ]; then
    echo -e "${GREEN}✓ Vault found${NC}"
else
    echo -e "${RED}✗ Vault not found at: $VAULT_PATH${NC}"
    echo "Please update VAULT_PATH in this script"
fi

# 3. Start Backend API
echo -e "\n${YELLOW}🚀 Starting Backend API...${NC}"
if check_port 8004; then
    echo -e "${GREEN}✓ API already running on port 8004${NC}"
else
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}✗ Virtual environment not found${NC}"
        exit 1
    fi
    
    # Install dependencies if needed
    pip install -r backend/requirements.txt -q 2>/dev/null || true
    
    nohup python -m uvicorn backend.api:app --host 0.0.0.0 --port 8004 --reload > api.log 2>&1 &
    echo $! > .api.pid
    sleep 2
    
    if check_port 8004; then
        echo -e "${GREEN}✓ API started on http://localhost:8004${NC}"
    else
        echo -e "${RED}✗ Failed to start API${NC}"
    fi
fi

# 4. Index vault if needed (optional)
if [ -f "scripts/index_vault_v3.py" ]; then
    echo -e "\n${YELLOW}📤 Checking if vault needs indexing...${NC}"
    read -p "Re-index vault? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        source venv/bin/activate
        python scripts/index_vault_v3.py
        echo -e "${GREEN}✓ Vault indexed${NC}"
    fi
fi

# 5. Start Frontend
echo -e "\n${YELLOW}🌐 Starting Frontend...${NC}"
cd frontend
if check_port 3050; then
    echo -e "${GREEN}✓ Frontend already running on port 3050${NC}"
else
    if [ -d "node_modules" ]; then
        nohup npm run dev > frontend.log 2>&1 &
        echo $! > ../.frontend.pid
        sleep 3
        
        if check_port 3050; then
            echo -e "${GREEN}✓ Frontend started on http://localhost:3050${NC}"
        else
            echo -e "${RED}✗ Failed to start frontend${NC}"
        fi
    else
        echo -e "${RED}✗ node_modules not found${NC}"
        echo "Run: npm install"
    fi
fi
cd "$SCRIPT_DIR"

echo -e "\n=========================================="
echo -e "${GREEN}✅ Chronicler is ready!${NC}"
echo "=========================================="
echo ""
echo "🌐 Web App:  http://localhost:3050"
echo "🔌 API:      http://localhost:8004"
echo "🗄️ Neo4j:   http://localhost:7474"
echo ""
echo "To stop: ./stop-all.sh"
