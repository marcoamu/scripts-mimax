#!/usr/bin/env python3
"""Newsletter Generator - Creates daily HTML newsletter"""

import os
import json
import requests
from datetime import datetime

API_URL = "http://localhost:3001"
OUTPUT_DIR = "/root/.openclaw/workspace/newsletter"
DATE = datetime.now().strftime("%Y-%m-%d")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_content():
    """Get content stats from API"""
    try:
        r = requests.get(f"{API_URL}/api/content-simple", timeout=5)
        data = r.json()
        tiktok = data.get('tiktok', [])
        youtube = data.get('youtube', [])
        
        # Top content
        all_content = tiktok + youtube
        sorted_content = sorted(all_content, key=lambda x: x.get('views', 0), reverse=True)
        
        return {
            'tiktok_count': len(tiktok),
            'youtube_count': len(youtube),
            'total_views': sum(v.get('views', 0) for v in all_content),
            'top_content': sorted_content[:5]
        }
    except Exception as e:
        print(f"Error getting content: {e}")
        return {'tiktok_count': 0, 'youtube_count': 0, 'total_views': 0, 'top_content': []}

def get_research():
    """Get recent research"""
    try:
        r = requests.get(f"{API_URL}/api/investigaciones", timeout=5)
        return r.json()[:5] if r.status_code == 200 else []
    except:
        return []

# Get data
print(f"📰 Generating newsletter for {DATE}...")
content = get_content()
research = get_research()

# Build top content HTML
top_html = ""
for c in content['top_content']:
    title = c.get('titulo', 'Sin título')[:60]
    views = c.get('views', 0)
    platform = '🎵' if 'tiktok' in c.get('video_url', '') else '📺'
    top_html += f"<li>{platform} {title}... ({views:,} views)</li>\n"

# Build research HTML
research_html = ""
for r in research:
    tema = r.get('tema', 'Sin tema')[:80]
    research_html += f"<li>🔬 {tema}</li>\n"

if not research_html:
    research_html = "<li>No hay investigaciones recientes</li>"

# Generate HTML
html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>OpenClaw Newsletter - {DATE}</title>
  <style>
    body {{ font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #0f172a; color: white; }}
    h1 {{ color: #22c55e; border-bottom: 2px solid #22c55e; padding-bottom: 10px; }}
    h2 {{ color: #8b5cf6; margin-top: 30px; }}
    .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
    .stat {{ background: #1e293b; padding: 15px 25px; border-radius: 10px; text-align: center; }}
    .stat-value {{ font-size: 1.5rem; font-weight: bold; color: #22c55e; }}
    .stat-label {{ font-size: 0.85rem; color: #64748b; }}
    ul {{ line-height: 1.8; }}
    li {{ margin: 8px 0; }}
    .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #334155; color: #64748b; font-size: 0.85rem; }}
    .highlight {{ background: linear-gradient(90deg, #22c55e, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    a {{ color: #22c55e; }}
  </style>
</head>
<body>
  <h1>📰 OpenClaw Daily Digest</h1>
  <p><strong>Fecha:</strong> {DATE}</p>
  
  <h2>📊 Estado del Sistema</h2>
  <div class="stats">
    <div class="stat">
      <div class="stat-value">{content['tiktok_count']}</div>
      <div class="stat-label">TikTok Videos</div>
    </div>
    <div class="stat">
      <div class="stat-value">{content['youtube_count']}</div>
      <div class="stat-label">YouTube Videos</div>
    </div>
    <div class="stat">
      <div class="stat-value">{content['total_views']:,}</div>
      <div class="stat-label">Total Views</div>
    </div>
  </div>

  <h2>🔬 Investigaciones Recientes</h2>
  <ul>
    {research_html}
  </ul>

  <h2>🔥 Top Contenido</h2>
  <ul>
    {top_html}
  </ul>

  <div class="footer">
    <p>🤖 Generado automáticamente por <span class="highlight">OpenClaw</span></p>
    <p>📊 <a href="http://212.227.107.120:4000/">Ver Dashboard</a></p>
  </div>
</body>
</html>"""

# Save
output_file = f"{OUTPUT_DIR}/newsletter-{DATE}.html"
with open(output_file, 'w') as f:
    f.write(html)

print(f"✅ Newsletter saved: {output_file}")
print(f"   TikTok: {content['tiktok_count']}")
print(f"   YouTube: {content['youtube_count']}")
print(f"   Total Views: {content['total_views']:,}")
