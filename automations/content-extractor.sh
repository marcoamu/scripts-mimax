#!/bin/bash
###############################################################################
# CONTENT EXTRACTOR AUTOMATION - TikTok & YouTube
# 
# Este script extrae contenido de creators en tracking automáticamente.
# Designed for OpenClaw AI Media System
#
# Uso: ./content-extractor.sh [tiktok|youtube|all] [limit]
# Ejemplo: ./content-extractor.sh tiktok 5
#
# Cron suggested:
# 0 8 * * * /root/.openclaw/workspace/scripts/automations/content-extractor.sh all 3
# 0 20 * * * /root/.openclaw/workspace/scripts/automations/content-extractor.sh all 3
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Config
API_URL="http://localhost:3001"
LOG_FILE="/root/.openclaw/workspace/logs/extraction.log"
PLATFORM="${1:-all}"
LIMIT="${2:-3}"

# Create logs directory
mkdir -p /root/.openclaw/workspace/logs

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "🚀 INICIANDO EXTRACCIÓN AUTOMÁTICA"
log "=========================================="
info "Plataforma: $PLATFORM"
info "Límite por creador: $LIMIT"
log ""

# Function to extract content
extract_platform() {
    local platform=$1
    local limit=$2
    
    info "Extrayendo $platform..."
    
    # Call the extraction API
    local response=$(curl -s -X POST "$API_URL/api/tracking/extract" \
        -H "Content-Type: application/json" \
        -d "{\"plataforma\": \"$platform\", \"limite\": $limit}" \
        2>&1)
    
    if [ $? -eq 0 ]; then
        log "✅ Extracción $platform completada: $response"
        echo "$response"
    else
        error "❌ Error extrayendo $platform: $response"
    fi
}

# Function to get content stats
get_stats() {
    local platform=$1
    local response=$(curl -s "$API_URL/api/content-simple" 2>/dev/null)
    
    if [ "$platform" = "tiktok" ] || [ "$platform" = "all" ]; then
        local tt_count=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('tiktok',[])))" 2>/dev/null || echo "0")
        info "TikTok videos: $tt_count"
    fi
    
    if [ "$platform" = "youtube" ] || [ "$platform" = "all" ]; then
        local yt_count=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('youtube',[])))" 2>/dev/null || echo "0")
        info "YouTube videos: $yt_count"
    fi
}

# Function to send notification
send_notification() {
    local message="$1"
    # Telegram notification (optional)
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID" \
            -d "text=$message" > /dev/null 2>&1
    fi
}

# Main execution
start_time=$(date +%s)

case "$PLATFORM" in
    tiktok)
        extract_platform "tiktok" "$LIMIT"
        ;;
    youtube)
        extract_platform "youtube" "$LIMIT"
        ;;
    all)
        info "Extrayendo TikTok y YouTube..."
        extract_platform "tiktok" "$LIMIT"
        sleep 2
        extract_platform "youtube" "$LIMIT"
        ;;
    *)
        error "Plataforma no válida: $PLATFORM"
        echo "Uso: $0 [tiktok|youtube|all] [limit]"
        exit 1
        ;;
esac

# Get final stats
sleep 2
get_stats "$PLATFORM"

end_time=$(date +%s)
duration=$((end_time - start_time))

log ""
log "=========================================="
log "✅ EXTRACCIÓN COMPLETADA"
log "Tiempo: ${duration}s"
log "=========================================="

# Send notification
send_notification "🤖 Extracción automática completada en ${duration}s"

exit 0
