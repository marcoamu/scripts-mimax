#!/bin/bash
# Daily TikTok AI Research - runs at 5 AM

cd /root/.openclaw/workspace

# Search for trending AI TikTok creators
echo "$(date): Buscando nuevos creadores de AI en TikTok..."

# Use Tavily to find trending topics
RESULTS=$(curl -s -X POST "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "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",
    "query": "top AI TikTok influencers creators 2026 trending",
    "max_results": 5
  }')

# Extract creator names and create tasks
echo "$RESULTS" | python3 -c "
import json, sys, subprocess

data = json.load(sys.stdin)
for r in data.get('results', [])[:3]:
    title = r.get('title', '')
    url = r.get('url', '')
    
    # Create task in backlog
    task = {
        'title': f'Research: {title}',
        'description': f'Fuente: {url}',
        'agent': 'research',
        'priority': 'medium',
        'status': 'backlog'
    }
    
    import requests
    try:
        subprocess.run(['curl', '-s', '-X', 'POST', 'http://localhost:3001/api/tasks', 
           '-H', 'Content-Type: application/json',
           '-d', json.dumps(task)])
        print(f'Created task: {title}')
    except:
        pass
"

echo "$(date): Búsqueda completada"
