#!/bin/bash
###############################################################################
# Health Check + Auto-Restart + Telegram Alerts
###############################################################################

LOG_FILE="/root/.openclaw/workspace/logs/health.log"
API_URL="http://localhost:3001"
STATIC_URL="http://localhost:4000"

# Telegram config (set these env vars)
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-291245843}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_alert() {
    local message="$1"
    if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=$message" \
            -d "parse_mode=Markdown" > /dev/null 2>&1
    fi
}

check_api() {
    curl -sf "$API_URL/api/creators" > /dev/null 2>&1
}

check_static() {
    curl -sf "$STATIC_URL/index.html" > /dev/null 2>&1
}

restart_api() {
    log "🔄 Restarting API..."
    pkill -f "node.*server" 2>/dev/null
    cd /root/.openclaw/workspace/ai-media-app
    node api/server.js > /tmp/api.log 2>&1 &
    sleep 5
    
    if check_api; then
        log "✅ API restarted"
        send_alert "✅ *API Reiniciada*\nEl servicio se recuperó automáticamente."
    else
        log "❌ API restart failed"
        send_alert "🔴 *API CAÍDA*\nNo se pudo reiniciar. Requiere atención manual."
    fi
}

restart_static() {
    log "🔄 Restarting Static..."
    pkill -f "python.*4000" 2>/dev/null
    cd /root/.openclaw/workspace/ai-media-app/public
    python3 -m http.server 4000 > /tmp/static.log 2>&1 &
    sleep 3
    
    if check_static; then
        log "✅ Static restarted"
    fi
}

# Main
log "=== Health Check ==="

if ! check_api; then
    log "❌ API DOWN - restarting..."
    send_alert "⚠️ *API Caída*\nReiniciando automáticamente..."
    restart_api
else
    log "✅ API OK"
fi

if ! check_static; then
    log "❌ Static DOWN - restarting..."
    restart_static
else
    log "✅ Static OK"
fi

log "=== Complete ==="
