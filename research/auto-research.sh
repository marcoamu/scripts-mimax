#!/bin/bash
###############################################################################
# Auto-Research Script
# Runs daily research on trending AI topics
###############################################################################

API_URL="http://localhost:3001"
LOG_FILE="/root/.openclaw/workspace/logs/auto-research.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Topics to research
TOPICS=(
    "Claude Code best practices 2026"
    "AI agents comparison 2026"
    "OpenAI o3 vs Claude 2026"
    "MCP servers trending"
    "AI coding assistants comparison"
)

log "=== Auto Research Started ==="

for TOPIC in "${TOPICS[@]}"; do
    log "🔍 Researching: $TOPIC"
    
    # Run research (calls the research agent)
    cd /root/.openclaw/workspace/scripts
    node research-agent-v2.js "$TOPIC" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "✅ Completed: $TOPIC"
    else
        log "❌ Failed: $TOPIC"
    fi
    
    sleep 2
done

log "=== Auto Research Complete ==="
