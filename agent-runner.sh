#!/bin/bash
# Agent Runner - Automates task management

API="http://localhost:3001"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🤖 Agent Runner Started${NC}"

while true; do
  # Get tasks in todo
  TASKS=$(curl -s "$API/api/tasks?status=todo" | grep -o '"id":[0-9]*' | head -5)
  
  if [ -n "$TASKS" ]; then
    echo -e "${GREEN}📋 Found tasks: $TASKS${NC}"
  fi
  
  # Get agent stats
  STATS=$(curl -s "$API/api/agent/stats")
  echo -e "📊 Agent Stats: $STATS"
  
  sleep 30
done
