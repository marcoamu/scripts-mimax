#!/usr/bin/env python3
"""
Crew Tools - Database utilities for Kanban Crew
"""

import psycopg2

DB_URL = "postgresql://postgres:postgres@localhost:5432/knowledge_base"

def get_db():
    """Get database connection."""
    return psycopg2.connect(DB_URL)

def save_research(title, content, agent, task_id):
    """Save research result to database."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO research_results (title, content, agent, source_task_id, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (title, content[:5000], agent, task_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ save_research error: {e}")

if __name__ == "__main__":
    # Test connection
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM kanban_tasks")
    print(f"✅ DB connected: {cur.fetchone()[0]} tasks in kanban")
    cur.close()
    conn.close()