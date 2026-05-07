#!/bin/bash
# ============================================
# Daily TikTok AI Research Automation
# Extracts: photos, descriptions, categories, topics
# ============================================

cd /root/.openclaw/workspace

API="http://localhost:3001"
TAVILY_KEY="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"

echo "=========================================="
echo "🔬 Daily TikTok AI Research"
echo "=========================================="
echo "$(date)"

# Step 1: Search for new AI TikTok creators
echo ""
echo "1️⃣ Buscando nuevos creadores de IA..."

SEARCH_RESULTS=$(curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"$TAVILY_KEY\",
    \"query\": \"top AI TikTok influencers creators 2026\",
    \"max_results\": 10
  }")

echo "$SEARCH_RESULTS" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data.get('results', []):
    title = r.get('title', '')
    url = r.get('url', '')
    print(f'{title}|{url}')
" 2>/dev/null

# Step 2: Extract detailed info from creators
echo ""
echo "2️⃣ Extrayendo información de creadores..."

CREATORS_DATA=(
  "rileybrown.ai|AI Education|Tutoriales de AI, coding, developer tools, vibe coding"
  "gazi.ai|Coding/Lifestyle|Coding, LeetCode, programmer humor, vida diaria"
  "tony.aube|Design/Tech|Diseño, Silicon Valley, Google AI, tech trends"
  "bio_makers1|Robotics/AI|IA, robótica humanoides, tecnología"
  "kanekallaway|Tech/AI|Tecnología, AI education, trends"
  "justinfineberg|AI Automation|automatización, AI, startup, Cassidy.ai"
  "shedoesai|AI Tools|AI tools, newsletter, recursos"
  "andyhafell|AI Agents|AI Agents, Infactory, builder tools"
  "thechriswinfield|AI Education|AI, tutoriales 90 segundos"
  "aicenturyclips|AI Content|AI clips, trends"
)

for creator_data in "${CREATORS_DATA[@]}"; do
  IFS='|' read -r username categoria temas <<< "$creator_data"
  
  echo "   Processing @$username..."
  
  # Get videos
  VIDEOS=$(timeout 20 yt-dlp --flat-playlist --playlist-end 5 \
      "https://www.tiktok.com/@$username" \
      --print "%(title)s|%(view_count)s" 2>/dev/null)
  
  BEST_VIEW=0
  BEST_TITLE=""
  
  while IFS='|' read -r title views; do
    if [ -n "$views" ] && [ "$views" -gt "$BEST_VIEW" ]; then
      BEST_VIEW=$views
      BEST_TITLE=$title
    fi
  done <<< "$VIDEOS"
  
  # Generate avatar
  AVATAR_URL="https://api.dicebear.com/7.x/initials/svg?seed=$username&backgroundColor=8b5cf6,ec4899,3b82f5,22c55e,ef4444,f59e0b"
  
  # Parse temas into array for JSON
  TEMAS_ARRAY="["
  IFS=',' read -ra TEMAS <<< "$temas"
  for i in "${!TEMAS[@]}"; do
    TEMAS_ARRAY+="\"${TEMAS[$i]}\""
    if [ $i -lt $((${#TEMAS[@]} - 1)) ]; then TEMAS_ARRAY+=","; fi
  done
  TEMAS_ARRAY+="]"
  
  # Update in database
  curl -s -X PUT "$API/api/creators/$username" \
    -H "Content-Type: application/json" \
    -d "{
      \"categoria\": \"$categoria\",
      \"temas\": $TEMAS_ARRAY,
      \"mejor_video_views\": $BEST_VIEW,
      \"mejor_video_titulo\": \"$BEST_TITLE\",
      \"foto_url\": \"$AVATAR_URL\"
    }" > /dev/null 2>&1
  
  echo "      ✓ $categoria | Best: $BEST_VIEW views"
done

# Step 3: Create research task
echo ""
echo "3️⃣ Creando tarea de investigación..."

curl -s -X POST "$API/api/tasks" -H "Content-Type: application/json" -d "{
  \"title\": \"Research: Tendencias IA TikTok $(date +%Y-%m-%d)\",
  \"description\": \"Investigación diaria de trends de IA en TikTok\",
  \"agent\": \"research\",
  \"priority\": \"medium\",
  \"status\": \"backlog\"
}" > /dev/null 2>&1

echo ""
echo "✅ Proceso completado"
echo "=========================================="
