#!/usr/bin/env python3
"""
Self-Reflection Agent - Runs nightly to analyze and improve the research process.
Improved version with proper error handling and MiniMax fallback chain.
"""

import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, '/root/.openclaw/workspace')
from crew_tools import get_db

import json
import urllib.request
import urllib.error

# MiniMax Configuration
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_URL = "https://api.minimax.io/anthropic/v1/messages"
MODEL = "MiniMax-M2.7"

def call_llm(prompt, timeout=120):
    """Call MiniMax with fallback to Ollama."""
    
    # Try MiniMax first
    try:
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        req = urllib.request.Request(
            MINIMAX_URL,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode())
            content_list = result.get("content", [])
            for item in content_list:
                if item.get("type") == "text":
                    return item["text"].strip()
            return str(content_list)
            
    except Exception as e:
        print(f"⚠️ MiniMax failed: {e}, trying Ollama...")
        return call_ollama(prompt)

def call_ollama(prompt, model="llama3.2:1b", timeout=120):
    """Fallback to Ollama."""
    try:
        import requests
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            return f"Error: Ollama failed with code {response.status_code}"
    except Exception as e:
        return f"Error: Ollama unavailable - {str(e)}"

def run_self_reflection():
    """Run nightly self-reflection analysis."""
    print(f"🌙 Self-Reflection started at {datetime.now()}")
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get tasks from last 24 hours
    cur.execute("""
        SELECT id, title, result_text, agent, created_at 
        FROM kanban_tasks 
        WHERE created_at > NOW() - INTERVAL '24 hours'
        AND status IN ('done', 'review')
        ORDER BY created_at DESC
    """)
    tasks = cur.fetchall()
    
    if not tasks:
        print("No tasks found in last 24 hours. Checking recent...")
        cur.execute("""
            SELECT id, title, result_text, agent, created_at 
            FROM kanban_tasks 
            WHERE status IN ('done', 'review')
            ORDER BY created_at DESC
            LIMIT 10
        """)
        tasks = cur.fetchall()
    
    # Build context
    context = f"Tasks analyzed ({len(tasks)} tasks):\n\n"
    for t in tasks:
        context += f"[{t[4].strftime('%Y-%m-%d %H:%M')}] Agent: {t[3]} - {t[1]}\n"
        if t[2]:
            context += f"  Result: {t[2][:300]}...\n"
        context += "\n"
    
    cur.close()
    conn.close()
    
    # Create analysis prompt
    analysis_prompt = f"""You are a self-improving AI system.

Analyze today's execution of the research and task agents.

{context}

Provide a structured improvement report with:
1. What worked well
2. What failed or was inefficient  
3. Source quality evaluation
4. Decision quality assessment
5. Specific improvement actions for tomorrow

Be critical and precise. No generic statements."""

    print("🤔 Running self-reflection analysis with MiniMax...")
    result = call_llm(analysis_prompt)
    
    # Save result to file
    output_file = f"/root/.obsidian/Research/AutoReflexion/self_reflection_{datetime.now().strftime('%Y%m%d')}.md"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(f"# Self-Reflection Report - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(f"## Analysis Result\n\n")
        f.write(result)
    
    print(f"✅ Reflection saved to {output_file}")
    
    # Also save to DB
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO analyzed_content (source_table, original_title, classification, selection_reason, analysis_full, fecha_extraccion)
            VALUES ('system', 'Self-Reflection Report', 'medium', 'System analysis', %s, NOW())
        """, (result[:5000],))
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Also saved to database")
    except Exception as e:
        print(f"⚠️ DB save failed: {e}")
    
    return result

if __name__ == "__main__":
    try:
        result = run_self_reflection()
        print("\n📊 RESULT:")
        print(result[:500] if len(str(result)) > 500 else result)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()