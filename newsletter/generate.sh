#!/bin/bash
###############################################################################
# Newsletter Generator
# Generates daily summary of research, content, and system activity
###############################################################################

API_URL="http://localhost:3001"
OUTPUT_DIR="/root/.openclaw/workspace/newsletter"
DATE=$(date +%Y-%m-%d)

mkdir -p "$OUTPUT_DIR"

echo "📰 Generando Newsletter para $DATE..."

# Get today's research
echo "🔬 Obteniendo investigaciones..."
RESEARCH=$(curl -s "$API_URL/api/investigaciones" 2>/dev/null | python3 -c "
import json,sys,datetime
data = json.load(sys.stdin)
today = datetime.date.today()
for r in data:
    try:
        fecha = datetime.datetime.fromisoformat(r.get('fecha','').replace('Z','+00:00')).date()
        if fecha == today:
            print(f\"- {r.get('tema', 'N/A')}\")
    except: pass
" 2>/dev/null | head -5)

# Get content stats
echo "📊 Obteniendo estadísticas..."
CONTENT_STATS=$(curl -s "$API_URL/api/content-simple" 2>/dev/null | python3 -c "
import json,sys
data = json.load(sys.stdin)
tt = len(data.get('tiktok',[]))
yt = len(data.get('youtube',[]))
print(f'TikTok: {tt} videos')
print(f'YouTube: {yt} videos')
" 2>/dev/null)

# Get top content
TOP_CONTENT=$(curl -s "$API_URL/api/content-simple" 2>/dev/null | python3 -c "
import json,sys
data = json.load(sys.stdin)
all_content = (data.get('tiktok',[]) + data.get('youtube',[]))
sorted_content = sorted(all_content, key=lambda x: x.get('views',0), reverse=True)
for c in sorted_content[:5]:
    print(f\"- {c.get('titulo','')[:60]}... ({c.get('views',0)} views)\")
" 2>/dev/null)

# Generate HTML newsletter
cat > "$OUTPUT_DIR/newsletter-$DATE.html" << HTML
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>OpenClaw Newsletter - $DATE</title>
  <style>
    body { font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0f172a; color: white; }
    h1 { color: #22c55e; border-bottom: 2px solid #22c55e; padding-bottom: 10px; }
    h2 { color: #8b5cf6; margin-top: 30px; }
    .stats { display: flex; gap: 20px; margin: 20px 0; }
    .stat { background: #1e293b; padding: 15px 25px; border-radius: 10px; text-align: center; }
    .stat-value { font-size: 1.5rem; font-weight: bold; color: #22c55e; }
    .stat-label { font-size: 0.85rem; color: #64748b; }
    ul { line-height: 1.8; }
    li { margin: 8px 0; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #334155; color: #64748b; font-size: 0.85rem; }
    .highlight { background: linear-gradient(90deg, #22c55e, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  </style>
</head>
<body>
  <h1>📰 OpenClaw Daily Digest</h1>
  <p><strong>Fecha:</strong> $DATE</p>
  
  <h2>📊 Estado del Sistema</h2>
  <div class="stats">
    <div class="stat">
      <div class="stat-value">$tt</div>
      <div class="stat-label">TikTok</div>
    </div>
    <div class="stat">
      <div class="stat-value">$yt</div>
      <div class="stat-label">YouTube</div>
    </div>
  </div>

  <h2>🔬 Investigaciones Recientes</h2>
  <ul>
    $RESEARCH
  </ul>

  <h2>🔥 Top Contenido</h2>
  <ul>
    $TOP_CONTENT
  </ul>

  <div class="footer">
    <p>🤖 Generado automáticamente por <span class="highlight">OpenClaw</span></p>
    <p>📊 <a href="http://212.227.107.120:4000/" style="color:#22c55e">Ver Dashboard</a></p>
  </div>
</body>
</html>
HTML

# Count stats
tt=$(curl -s "$API_URL/api/content-simple" 2>/dev/null | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('tiktok',[])))" 2>/dev/null || echo "0")
yt=$(curl -s "$API_URL/api/content-simple" 2>/dev/null | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('youtube',[])))" 2>/dev/null || echo "0")

echo "✅ Newsletter generado: $OUTPUT_DIR/newsletter-$DATE.html"
echo ""
echo "Estadísticas: TikTok $tt | YouTube $yt"

# Save to history
echo "$DATE: TikTok $tt, YouTube $yt" >> "$OUTPUT_DIR/history.txt"
