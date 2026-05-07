#!/bin/bash
VIDEO_URL="$1"
OUTPUT_ID="$2"
TEMP_FILE="/tmp/${OUTPUT_ID}.mp3"

echo "Downloading..."
yt-dlp -x --audio-format mp3 -o "$TEMP_FILE" "$VIDEO_URL" --quiet 2>&1

if [ -f "$TEMP_FILE" ]; then
    echo "Transcribing..."
    TRANSCRIPT=$(python3 << PYEOF
import whisper
model = whisper.load_model('base')
result = model.transcribe('$TEMP_FILE')
print(result['text'][:8000])
PYEOF
)
    
    # Update DB
    PGPASSWORD=postgres psql -h localhost -U postgres -d knowledge_base -c "
    UPDATE content_tracking SET transcripcion = '$TRANSCRIPT', transcripcion_status = 'completed' 
    WHERE video_url LIKE '%$OUTPUT_ID%'
    " 2>/dev/null
    
    rm -f "$TEMP_FILE"
    echo "Done! Saved to DB"
else
    echo "ERROR: Download failed"
fi
