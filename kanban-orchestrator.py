#!/usr/bin/env python3
"""
🤖 Kanban Orchestrator - Processes tasks through the board
"""

import psycopg2
import os
import time
import json

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/knowledge_base")

AGENTS = {
    "research": {"name": "Research Agent", "emoji": "📚", "topics": ["investigación", "analizar", "buscar", "competidores", "links", "información"]},
    "finance": {"name": "Finance Agent", "emoji": "💰", "topics": ["finanzas", "dinero", "inversión", "presupuesto", "gastos", "ingresos"]},
    "frontend": {"name": "Frontend Agent", "emoji": "🎨", "topics": ["frontend", "vue", "react", "ui", "diseño", "interfaz", "css", "javascript", "vista"]},
    "backend": {"name": "Backend Agent", "emoji": "⚙️", "topics": ["backend", "api", "base de datos", "servidor", "python", "fastapi", "postgresql", "datos"]},
    "general": {"name": "General Agent", "emoji": "🔧", "topics": ["general", "tarea", "varios"]}
}

def get_db():
    return psycopg2.connect(DB_URL)

def assign_best_agent(task_title, task_desc):
    """Analyze task and assign best agent"""
    text = (task_title + " " + (task_desc or "")).lower()
    best_agent = "general"
    best_score = 0
    
    for agent_id, agent in AGENTS.items():
        score = 0
        for topic in agent["topics"]:
            if topic.lower() in text:
                score += 3
        if score > best_score:
            best_score = score
            best_agent = agent_id
    
    return best_agent

def process_one_task():
    """Process exactly ONE task - move to inprogress, work, move to review"""
    conn = get_db()
    cur = conn.cursor()
    
    # Get ONE task in todo
    cur.execute("""
        SELECT id, title, description, agent 
        FROM kanban_tasks 
        WHERE status = 'todo' 
        ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, id DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    
    if not row:
        cur.close()
        conn.close()
        return False
    
    task_id, title, desc, current_agent = row
    
    # Assign agent if not assigned
    if not current_agent or current_agent == 'general':
        current_agent = assign_best_agent(title, desc)
        print(f"  → Asignando a {AGENTS[current_agent]['emoji']} {current_agent}")
    
    # Step 1: Move to INPROGRESS
    cur.execute("UPDATE kanban_tasks SET status = 'inprogress', agent = %s, updated_at = NOW() WHERE id = %s", 
                (current_agent, task_id))
    conn.commit()
    print(f"  ⏳ Task {task_id} en progreso...")
    
    # Step 2: Simulate work (in real system, this would call the actual agent)
    time.sleep(2)  # Simulate work time
    
    # Generate result based on agent type
    agent = AGENTS.get(current_agent, AGENTS["general"])
    
    results = {
        "research": f"📚 Investigación completada: {title}\n\nSe analizó el tema y se reunió información relevante.",
        "finance": f"💰 Análisis financiero: {title}\n\nSe realizaron los cálculos y proyecciones pertinentes.",
        "frontend": f"🎨 Trabajo de frontend: {title}\n\nSe implementó la interfaz de usuario.",
        "backend": f"⚙️ Trabajo de backend: {title}\n\nSe implementó la lógica y/base de datos.",
        "general": f"✅ Tarea procesada: {title}\n\nTrabajo completado."
    }
    
    result_text = results.get(current_agent, results["general"])
    comments = f"Procesado por {agent['name']}"
    
    # Step 3: Move to REVIEW with result
    cur.execute("""
        UPDATE kanban_tasks 
        SET status = 'review', result_text = %s, comments = %s, updated_at = NOW() 
        WHERE id = %s
    """, (result_text, comments, task_id))
    conn.commit()
    
    cur.close()
    conn.close()
    print(f"  ✅ Task {task_id} movido a REVIEW")
    return True

def run_orchestrator():
    print("🚀 Kanban Orchestrator started...")
    
    while True:
        try:
            # Process ONE task per cycle
            processed = process_one_task()
            
            if not processed:
                print(".", end="", flush=True)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    run_orchestrator()
