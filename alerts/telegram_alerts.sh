#!/bin/bash
# Telegram Alert System using OpenClaw
# Sends notifications when services are down

USER_ID="291245843"
LOG="/root/.openclaw/workspace/cron/alerts.log"
DATE=$(date '+%Y-%m-%d %H:%M')

send_alert() {
    local message="$1"
    local priority="${2:-info}"
    
    local emoji="ℹ️"
    [ "$priority" = "critical" ] && emoji="🚨"
    [ "$priority" = "warning" ] && emoji="⚠️"
    [ "$priority" = "success" ] && emoji="✅"
    
    openclaw message broadcast --channel telegram --targets "$USER_ID" --message "$emoji $message" 2>&1 | tee -a "$LOG"
}

# Check services
check_service() {
    local name=$1
    local port=$2
    
    if ! ss -tlnp | grep -q ":$port "; then
        send_alert "<b>$name CAÍDO</b>%0APuerto: $port%0AHora: $(date '+%H:%M')" "critical"
        return 1
    fi
    return 0
}

echo "[$DATE] Checking services..." >> "$LOG"

# Check and alert
check_service "Backend" 8000
check_service "Frontend" 3000

# Send success if all OK
if ss -tlnp | grep -q ":8000 " && ss -tlnp | grep -q ":3000 "; then
    echo "[$DATE] ✅ Servicios OK" >> "$LOG"
fi
