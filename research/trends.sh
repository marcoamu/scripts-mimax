#!/bin/bash
###############################################################################
# Trends Detection Script
# Analyzes content to find trending topics
###############################################################################

API_URL="http://localhost:3001"
LOG_FILE="/root/.openclaw/workspace/logs/trends.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Trends Detection Started ==="

# Get content and analyze
CONTENT=$(curl -s "$API_URL/api/content-simple")

# Count by keyword (simple trending detection)
log "📊 Analyzing content..."

# Common AI/tech keywords
KEYWORDS=("claude" "openai" "gpt" "ai" "agent" "mcp" "cursor" "vscode" "python" "javascript")

for KEYWORD in "${KEYWORDS[@]}"; do
    COUNT=$(echo "$CONTENT" | grep -io "$KEYWORD" | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        log "  $KEYWORD: $COUNT mentions"
    fi
done

# Get top creators by views
log "🏆 Top creators:"
curl -s "$API_URL/api/content-simple" | python3 -c "
import json,sys,collections
data = json.load(sys.stdin)
all_content = data.get('tiktok',[]) + data.get('youtube',[])
creators = collections.Counter([c.get('username','') for c in all_content])
for creator, count in creators.most_common(5):
    print(f'  @${creator}: {count} videos')
"

log "=== Trends Complete ==="
