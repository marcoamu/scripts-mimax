#!/bin/bash
###############################################################################
# BULK TRANSCRIPTION SCRIPT
# Transcribe all pending TikTok videos using Whisper
###############################################################################

API_URL="http://localhost:3001"
LOG_FILE="/root/.openclaw/workspace/logs/transcription.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "🎤 INICIANDO TRANSCRIPCIONES AUTOMÁTICAS"
log "=========================================="

# Get pending transcriptions from API
response=$(curl -s "$API_URL/api/content-simple" 2>/dev/null)

# Count pending
pending=$(echo "$response" | python3 -c "
import json,sys
d = json.load(sys.stdin)
tiktok = d.get('tiktok',[])
pending = [v for v in tiktok if not v.get('transcripcion_status') or v.get('transcripcion_status') != 'completed']
print(len(pending))
" 2>/dev/null || echo "0")

log "Videos pendientes: $pending"

if [ "$pending" = "0" ] || [ "$pending" = "" ]; then
    log "✅ No hay videos pendientes"
    exit 0
fi

# Get IDs of pending videos
ids=$(echo "$response" | python3 -c "
import json,sys
d = json.load(sys.stdin)
tiktok = d.get('tiktok',[])
pending = [v for v in tiktok if not v.get('transcripcion_status') or v.get('transcripcion_status') != 'completed']
for v in pending[:10]:  # Max 10 at a time
    print(v['id'])
" 2>/dev/null)

count=0
for id in $ids; do
    log "Transcribiendo: $id"
    result=$(curl -s -X POST "$API_URL/api/content/$id/transcribe-whisper" \
        -H "Content-Type: application/json" \
        -d '{}' 2>&1)
    
    if echo "$result" | grep -q "success"; then
        log "✅ $id: Transcripción iniciada"
        count=$((count + 1))
    else
        log "❌ $id: Error"
    fi
    
    sleep 3  # Wait between requests
done

log "=========================================="
log "✅ $count transcripciones iniciadas"
log "=========================================="
