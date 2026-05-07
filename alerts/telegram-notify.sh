#!/bin/bash
###############################################################################
# Telegram Alert System
# Send notifications to Telegram
###############################################################################

# Config - these should be set as environment variables
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-291245843}"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

send_message() {
    local message="$1"
    local parse_mode="${2:-Markdown}"
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        echo -e "${YELLOW}⚠️ TELEGRAM_BOT_TOKEN not set${NC}"
        return 1
    fi
    
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_CHAT_ID" \
        -d "text=$message" \
        -d "parse_mode=$parse_mode" \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Alert sent${NC}"
    else
        echo -e "${RED}❌ Failed to send alert${NC}"
    fi
}

# Alert types
alert_system_status() {
    local status="$1"
    local message="🤖 *System Status Update*

📊 Status: $status
⏰ Time: $(date '+%Y-%m-%d %H:%M:%S')"
    send_message "$message"
}

alert_new_content() {
    local platform="$1"
    local count="$2"
    local message="📥 *New Content Extracted*

Platform: $platform
Videos: $count
⏰ Time: $(date '+%H:%M:%S')"
    send_message "$message"
}

alert_research_complete() {
    local topic="$1"
    local message="🔬 *Research Complete*

Topic: $topic
⏰ Time: $(date '+%H:%M:%S')"
    send_message "$message"
}

alert_error() {
    local error="$1"
    local message="⚠️ *System Error*

Error: $error
⏰ Time: $(date '+%H:%M:%S')"
    send_message "$message"
}

# CLI interface
case "$1" in
    status)
        alert_system_status "$2"
        ;;
    content)
        alert_new_content "$2" "$3"
        ;;
    research)
        alert_research_complete "$2"
        ;;
    error)
        alert_error "$2"
        ;;
    test)
        send_message "✅ *OpenClaw Alert System Test*

Alerts are working! 🤖"
        ;;
    *)
        echo "Usage: $0 {status|content|research|error|test} [args]"
        echo ""
        echo "Examples:"
        echo "  $0 status 'All systems operational'"
        echo "  $0 content 'TikTok' 5"
        echo "  $0 research 'AI trends'"
        echo "  $0 error 'Database connection failed'"
        echo "  $0 test"
        ;;
esac
