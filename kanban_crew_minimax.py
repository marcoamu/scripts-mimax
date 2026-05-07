#!/usr/bin/env python3
"""
Kanban Crew Orchestrator - MiniMax M2.7
Chief Coordinator + Specialized Agents using MiniMax with Fallback Chain
"""

import os
import sys
import json
import time
from datetime import datetime
from crew_tools import get_db, save_research

# MiniMax API Configuration
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_URL = "https://api.minimax.io/anthropic/v1/messages"
MODEL = "MiniMax-M2.7"

def call_minimax(prompt, timeout=30, fallback=True):
    """Call MiniMax with fallback chain."""
    import urllib.request
    import urllib.error
    
    # Try MiniMax first
    try:
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        req = urllib.request.Request(
            MINIMAX_URL,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode())
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
    except Exception as e:
        if fallback:
            print(f"⚠️ MiniMax failed ({e}), trying Ollama...")
            return call_ollama(prompt)
        else:
            return f"Error: {str(e)}"

def call_ollama(prompt, model="llama3.2:1b", timeout=60):
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

def analyze_task_with_minimax(task_title, task_description, context=""):
    """Chief Coordinator analyzes task and decides agent delegation."""
    
    prompt = f"""You are the Chief Coordinator of a multi-agent system.

Task to analyze:
- Title: {task_title}
- Description: {task_description}
{context}

Based on the task, decide:
1. Which specialized agent should handle it?
2. What priority (high/medium/low)?
3. What's the estimated complexity (1-10)?

Available agents:
- research: Web searches, investigations, information gathering
- coding: Code generation, debugging, technical tasks  
- frontend: UI/UX, Vue.js, React, styling
- backend: APIs, databases, server logic
- finance: Financial analysis, trading, numbers
- general: Everything else

Respond in JSON format:
{{"agent": "agent_name", "priority": "high/medium/low", "complexity": 1-10, "reasoning": "why this agent"}}
"""

    result = call_minimax(prompt, timeout=30)
    
    try:
        if "{" in result and "}" in result:
            json_str = result[result.find("{"):result.rfind("}")+1]
            return json.loads(json_str)
        else:
            return {"agent": "general", "priority": "medium", "complexity": 5, "reasoning": result[:200]}
    except:
        return {"agent": "general", "priority": "medium", "complexity": 5, "reasoning": result[:200]}

def execute_agent_task(agent, task_title, task_description, db_task_id):
    """Execute task with specified agent using MiniMax."""
    
    agent_prompts = {
        "research": f"""You are a Research Agent. Investigate thoroughly.

Task: {task_description}

Provide:
1. Key findings (3-5 bullet points)
2. Sources used
3. Confidence level (high/medium/low)
4. Follow-up suggestions

Be thorough and cite sources.""",

        "coding": f"""You are a Coding Agent. Write clean, functional code.

Task: {task_description}

Provide:
1. Code solution with comments
2. Dependencies needed
3. How to run it
4. Potential issues to watch

Write actual working code, not pseudocode.""",

        "frontend": f"""You are a Frontend Agent. Build beautiful UIs.

Task: {task_description}

Provide:
1. Vue.js/React component code
2. Styling (CSS/Tailwind)
3. Props and state management
4. How to integrate

Focus on modern, clean design.""",

        "backend": f"""You are a Backend Agent. Build robust APIs.

Task: {task_description}

Provide:
1. API endpoint design
2. Database schema if needed
3. Error handling approach
4. Security considerations

Use best practices.""",

        "finance": f"""You are a Finance Agent. Analyze numbers and trends.

Task: {task_description}

Provide:
1. Key metrics
2. Trend analysis
3. Recommendations
4. Risk assessment

Be precise with numbers.""",

        "general": f"""You are a versatile AI Assistant.

Task: {task_description}

Provide a comprehensive response with:
1. Main answer/solution
2. Supporting details
3. Practical next steps

Be helpful and thorough."""
    }
    
    prompt = agent_prompts.get(agent, agent_prompts["general"])
    result = call_minimax(prompt, timeout=60)
    
    return result

def process_pending_tasks():
    """Main orchestrator loop - process pending tasks."""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, title, description, status, priority, agent
        FROM kanban_tasks
        WHERE status = 'pending'
        ORDER BY 
            CASE priority 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END,
            created_at ASC
        LIMIT 3
    """)
    tasks = cur.fetchall()
    
    processed = 0
    errors = 0
    
    for task in tasks:
        task_id, title, description, status, priority, assigned_agent = task
        
        print(f"\n📋 Processing Task #{task_id}: {title[:50]}...")
        
        try:
            print(f"   🔍 Analyzing with Chief Coordinator...")
            analysis = analyze_task_with_minimax(title, description or "")
            chosen_agent = analysis.get("agent", assigned_agent or "general")
            
            print(f"   → Delegating to: {chosen_agent} (confidence: {analysis.get('complexity', '?')}/10)")
            
            result = execute_agent_task(chosen_agent, title, description or "", task_id)
            
            if "Error:" in str(result)[:50]:
                new_status = "review"
                print(f"   ❌ Task failed: {result[:100]}")
            else:
                new_status = "done"
                print(f"   ✅ Task completed")
            
            cur.execute("""
                UPDATE kanban_tasks 
                SET status = %s, result_text = %s, agent = %s, updated_at = NOW()
                WHERE id = %s
            """, (new_status, str(result)[:5000], chosen_agent, task_id))
            
            if new_status == "done":
                save_research(title, result[:1000], chosen_agent, task_id)
            
            processed += 1
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            print(f"   ❌ Error processing task: {e}")
            errors += 1
            cur.execute("""
                UPDATE kanban_tasks 
                SET status = 'review', result_text = %s, updated_at = NOW()
                WHERE id = %s
            """, (f"Error: {str(e)[:500]}", task_id))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {"processed": processed, "errors": errors}

if __name__ == "__main__":
    print(f"🚀 Kanban Crew Orchestrator (MiniMax) - {datetime.now()}")
    print("=" * 50)
    
    result = process_pending_tasks()
    
    print("\n" + "=" * 50)
    print(f"✅ Processed: {result['processed']} | Errors: {result['errors']}")