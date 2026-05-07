#!/bin/bash

API="http://localhost:3001"

echo "=== Running content tracking ==="

# Test YouTube extraction
echo ""
echo "📺 Testing YouTube (@lexfridman)..."
yt-dlp --flat-playlist --playlist-end 1 "https://www.youtube.com/@lexfridman/videos" \
    --print "%(title)s|%(view_count)s" 2>/dev/null | while read line; do
    echo "  Video: $line"
done

echo ""
echo "🎵 Testing TikTok (@rileybrown.ai)..."
yt-dlp --flat-playlist --playlist-end 1 "https://www.tiktok.com/@rileybrown.ai" \
    --print "%(title)s|%(view_count)s" 2>/dev/null | while read line; do
    echo "  Video: $line"
done

echo ""
echo "✅ Test complete"
