#!/usr/bin/env python3
"""
Kanban Crew Orchestrator - Multi-agent system for task processing
Uses CrewAI with Ollama for local LLM processing
"""

import os
import sys
import time
from datetime import datetime

import psycopg2
from crewai import Agent, Task, Crew, Process

# Database
DB_URL = "postgresql://postgres:postgres@localhost:5432/knowledge_base"

def get_db():
    return psycopg2.connect(DB_URL)

# LLM Configuration - Using Ollama
MINIMAX_LLM = "ollama/llama3.2:1b"

# ============================================================================
# AGENTS
# ============================================================================

chief_agent = Agent(
    role="Chief Coordinator",
    goal="Efficiently analyze and delegate tasks to the appropriate specialized agent",
    backstory="""You are the chief coordinator of an AI agent team. You analyze tasks 
    and delegate to the most appropriate specialist: Research, Finance, Frontend, Backend, or Coding.""",
    verbose=True,
    llm=MINIMAX_LLM,
)

research_agent = Agent(
    role="Research Agent",
    goal="Find and synthesize the best information on any topic",
    backstory="""You are a research expert. You find high-quality information from 
    multiple sources, analyze it, and provide comprehensive summaries with key insights.""",
    verbose=True,
    llm=MINIMAX_LLM,
)

finance_agent = Agent(
    role="Finance Analyst",
    goal="Analyze financial data, trends, and provide investment insights",
    backstory="""You are a financial analyst. You analyze markets, stocks, crypto, 
    and provide data-driven insights for decision making.""",
    verbose=True,
    llm=MINIMAX_LLM,
)

frontend_agent = Agent(
    role="Frontend Developer",
    goal="Create beautiful, functional Vue.js and React interfaces",
    backstory="""You are a frontend expert. You build responsive, modern UIs with 
    Vue.js, React, TailwindCSS, and other modern frameworks.""",
    verbose=True,
    llm=MINIMAX_LLM,
)

backend_agent = Agent(
    role="Backend Developer",
    goal="Build robust APIs and database solutions",
    backstory="""You are a backend expert. You create FastAPI endpoints, PostgreSQL 
    queries, Docker configurations, and scalable server solutions.""",
    verbose=True,
    llm=MINIMAX_LLM,
)

coding_agent = Agent(
    role="Coding Assistant",
    goal="Help with any coding task efficiently and with best practices",
    backstory="""You are a coding assistant. You help with Python, JavaScript, 
    debugging, code review, and implementation of any software task.""",
    verbose=True,
    llm=MINIMAX_LLM,
)

# ============================================================================
# TASK EXECUTORS
# ============================================================================

def analyze_and_delegate(task_id: int, title: str, description: str) -> dict:
    """Use Chief agent to analyze task and decide which agent should handle it."""
    
    analysis_task = Task(
        description=f"""Analyze this task and determine the best agent to handle it:
        
        Task: {title}
        Description: {description}
        
        Available agents:
        - research: For information gathering, investigations, learning
        - finance: For financial analysis, market data, investments
        - frontend: For Vue.js, React, UI/UX, CSS, web interfaces
        - backend: For Python, APIs, databases, server logic
        - coding: For general coding tasks, debugging, scripts
        
        Respond with ONLY the agent name (research/finance/frontend/backend/coding) that should handle this task.
        If unsure, default to 'coding'.""",
        agent=chief_agent,
        expected_output="Single word: the agent category"
    )
    
    crew = Crew(agents=[chief_agent], tasks=[analysis_task], process=Process.sequential)
    result = crew.kickoff()
    
    category = str(result).strip().lower()
    if category not in ['research', 'finance', 'frontend', 'backend', 'coding']:
        category = 'coding'
    
    return {"category": category}

def execute_research_task(task_id: int, title: str, description: str) -> str:
    """Execute research task with Research agent."""
    
    research_task = Task(
        description=f"""Research the following topic thoroughly:
        
        Title: {title}
        Description: {description}
        
        Provide:
        1. Executive summary
        2. Key findings
        3. Sources consulted
        4. actionable insights
        
        Be comprehensive and cite sources.""",
        agent=research_agent,
        expected_output="Comprehensive research report"
    )
    
    crew = Crew(agents=[research_agent], tasks=[research_task], process=Process.sequential)
    result = crew.kickoff()
    return str(result)

def execute_finance_task(task_id: int, title: str, description: str) -> str:
    """Execute finance task with Finance agent."""
    
    finance_task = Task(
        description=f"""Analyze the following financial topic:
        
        Title: {title}
        Description: {description}
        
        Provide:
        1. Analysis
        2. Key metrics
        3. Recommendations
        
        Be data-driven and specific.""",
        agent=finance_agent,
        expected_output="Financial analysis and recommendations"
    )
    
    crew = Crew(agents=[finance_agent], tasks=[finance_task], process=Process.sequential)
    result = crew.kickoff()
    return str(result)

def execute_coding_task(task_id: int, title: str, description: str) -> str:
    """Execute general coding task with Coding agent."""
    
    coding_task = Task(
        description=f"""Help with the following coding task:
        
        Title: {title}
        Description: {description}
        
        Provide clean, well-commented code with explanations.""",
        agent=coding_agent,
        expected_output="Code solution with explanation"
    )
    
    crew = Crew(agents=[coding_agent], tasks=[coding_task], process=Process.sequential)
    result = crew.kickoff()
    return str(result)

def execute_frontend_task(task_id: int, title: str, description: str) -> str:
    """Execute frontend task with Frontend agent."""
    
    frontend_task = Task(
        description=f"""Help with the following frontend task:
        
        Title: {title}
        Description: {description}
        
        Stack: Vue.js, React, TailwindCSS, JavaScript
        
        Provide:
        1. Component code
        2. Styling
        3. Implementation notes""",
        agent=frontend_agent,
        expected_output="Frontend solution with code"
    )
    
    crew = Crew(agents=[frontend_agent], tasks=[frontend_task], process=Process.sequential)
    result = crew.kickoff()
    return str(result)

def execute_backend_task(task_id: int, title: str, description: str) -> str:
    """Execute backend task with Backend agent."""
    
    backend_task = Task(
        description=f"""Help with the following backend task:
        
        Title: {title}
        Description: {description}
        
        Stack: Python, FastAPI, PostgreSQL
        
        Provide:
        1. API design if applicable
        2. Python/FastAPI code
        3. SQL queries if needed
        4. Security considerations""",
        agent=backend_agent,
        expected_output="Backend solution in Spanish"
    )
    
    crew = Crew(agents=[backend_agent], tasks=[backend_task], process=Process.sequential)
    result = crew.kickoff()
    return str(result)

# ============================================================================
# ORCHESTRATOR
# ============================================================================

def process_one_task():
    """Process ONE task from the Kanban board"""
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get oldest 'todo' task
    cur.execute("""
        SELECT id, title, description, priority, agent 
        FROM kanban_tasks 
        WHERE status = 'todo' 
        ORDER BY created_at ASC 
        LIMIT 1
    """)
    
    task = cur.fetchone()
    if not task:
        print("No tasks to process")
        cur.close()
        conn.close()
        return None
    
    task_id, title, description, priority, current_agent = task
    title = title or ""
    description = description or ""
    
    print(f"📋 Processing Task #{task_id}: {title[:50]}")
    
    # Move to in_progress
    cur.execute("""
        UPDATE kanban_tasks 
        SET status = 'inprogress', agent = %s, updated_at = NOW() 
        WHERE id = %s
    """, (current_agent or 'chief', task_id))
    conn.commit()
    
    try:
        # Step 1: Analyze and delegate
        print("  🤔 Analyzing task...")
        decision = analyze_and_delegate(task_id, title, description)
        category = decision["category"]
        print(f"  → Delegating to: {category}")
        
        # Step 2: Execute with appropriate agent
        executors = {
            'research': execute_research_task,
            'finance': execute_finance_task,
            'frontend': execute_frontend_task,
            'backend': execute_backend_task,
            'coding': execute_coding_task,
        }
        
        executor = executors.get(category, execute_coding_task)
        result = executor(task_id, title, description)
        
        # Step 3: Move to REVIEW with result
        cur.execute("""
            UPDATE kanban_tasks 
            SET status = 'review', agent = %s, result_text = %s, updated_at = NOW() 
            WHERE id = %s
        """, (category, result[:5000] if result else '', task_id))
        conn.commit()
        
        print(f"  ✅ Task #{task_id} completed, moved to REVIEW")
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"  ❌ {error_msg}")
        
        cur.execute("""
            UPDATE kanban_tasks 
            SET status = 'review', agent = 'chief', result_text = %s, updated_at = NOW() 
            WHERE id = %s
        """, (error_msg[:5000], task_id))
        conn.commit()
    
    cur.close()
    conn.close()
    
    return task_id

def run_orchestrator():
    """Main orchestrator loop"""
    print("🚀 Kanban Crew Orchestrator started...")
    print(f"   Using Ollama ({MINIMAX_LLM}) for reasoning")
    
    while True:
        try:
            result = process_one_task()
            if result is None:
                # No tasks, wait before checking again
                time.sleep(10)
            else:
                # Task processed, brief pause before next
                time.sleep(2)
        except Exception as e:
            print(f"❌ Orchestrator error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_orchestrator()
