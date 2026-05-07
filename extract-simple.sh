#!/bin/bash
PLATAFORMA="$1"
LIMITE="${2:-5}"

LOGFILE="/tmp/extract_$(date +%s).log"

echo "Starting extraction: $PLATAFORMA, limit: $LIMITE" >> "$LOGFILE"

cd /root/.openclaw/workspace

# Run extraction
node scripts/content-tracker.js "$PLATAFORMA" "$LIMITE" >> "$LOGFILE" 2>&1

echo "Done at $(date)" >> "$LOGFILE"
