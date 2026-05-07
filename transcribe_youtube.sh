#!/bin/bash
VIDEO_URL="$1"

VIDEO_ID=$(echo "$VIDEO_URL" | grep -oP 'v=[^&]+' | head -1 | cut -d'=' -f2)

yt-dlp --write-subs --write-auto-subs --skip-download --sub-lang en "$VIDEO_URL" -o "/tmp/yt_${VIDEO_ID}" 2>/dev/null

SUBTITLE_FILE=$(ls /tmp/yt_${VIDEO_ID}*.vtt 2>/dev/null | head -1)

if [ -n "$SUBTITLE_FILE" ]; then
    # Simple approach: skip lines that look like VTT metadata
    TRANSCRIPT=$(cat "$SUBTITLE_FILE" | \
        grep -v "^WEBVTT" | \
        grep -v "^Kind:" | \
        grep -v "^Language:" | \
        grep -v "^[0-9][0-9]:[0-9][0-9]:[0-9][0-9]" | \
        sed 's/<[^>]*>//g' | \
        sed 's/\[.*\]//g' | \
        tr '\n' ' ' | \
        sed 's/  */ /g' | \
        head -c 8000)
    
    TRANSCRIPT=$(echo "$TRANSCRIPT" | tr -d "'")
    
    if [ -n "$TRANSCRIPT" ]; then
        sudo -u postgres psql -d knowledge_base -c "UPDATE content_tracking_yt SET transcripcion = E'$TRANSCRIPT', transcripcion_status = 'completed' WHERE video_url LIKE '%$VIDEO_ID%'"
        echo "Saved!"
    else
        sudo -u postgres psql -d knowledge_base -c "UPDATE content_tracking_yt SET transcripcion_status = 'error' WHERE video_url LIKE '%$VIDEO_ID%'"
    fi
    rm -f "$SUBTITLE_FILE"
else
    sudo -u postgres psql -d knowledge_base -c "UPDATE content_tracking_yt SET transcripcion_status = 'error' WHERE video_url LIKE '%$VIDEO_ID%'"
    echo "No subtitle"
fi
