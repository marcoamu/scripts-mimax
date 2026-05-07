#!/usr/bin/env python3
"""
Multi-Agent System with MiniMax M2.7
CrewAI + Qdrant Memory + MiniMax Intelligence
"""

import os
import sys

# Add scripts path
sys.path.insert(0, '/root/.openclaw/workspace/scripts')

from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# MiniMax Configuration
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimax.io/v1"

# Initialize MiniMax LLM
llm_minimax = ChatOpenAI(
    model="MiniMax-M2.7",
    api_key=MINIMAX_API_KEY,
    base_url=MINIMAX_BASE_URL
)

# Import vector memory
try:
    from vector_memory import query_memory_context
    MEMORY_AVAILABLE = True
except:
    MEMORY_AVAILABLE = False
    print("⚠️ Vector memory not available")

def create_research_crew(topic: str):
    """Create a research crew with MiniMax"""
    
    # Research Agent
    researcher = Agent(
        role="Research Analyst",
        goal=f"Research '{topic}' thoroughly using web search and personal knowledge base",
        backstory="""You are an expert research analyst with deep knowledge of AI, 
        technology, and business trends. You excel at finding accurate information 
        and synthesizing key insights.""",
        llm=llm_minimax,
        verbose=True
    )
    
    # Writer Agent
    writer = Agent(
        role="Content Writer",
        goal="Write clear, engaging summaries in Spanish",
        backstory="""You are a professional content writer who specializes in 
        translating complex topics into accessible content. You write in Spanish 
        with perfect grammar and engaging style.""",
        llm=llm_minimax,
        verbose=True
    )
    
    # Tasks
    research_task = Task(
        description=f"Research '{topic}' comprehensively. Use web search for current info.",
        agent=researcher,
        expected_output="Comprehensive research notes with sources"
    )
    
    write_task = Task(
        description="Write a clear summary of the research in Spanish",
        agent=writer,
        expected_output="Final summary in Spanish"
    )
    
    # Create crew
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew

def create_finance_crew():
    """Create a finance analysis crew"""
    
    collector = Agent(
        role="Data Collector",
        goal="Collect and organize financial transaction data",
        backstory="You are a data specialist focused on personal finance.",
        llm=llm_minimax,
        verbose=True
    )
    
    analyst = Agent(
        role="Financial Analyst", 
        goal="Analyze spending patterns and detect anomalies",
        backstory="""You are a financial analyst with 10 years of experience. 
        You specialize in personal finance, budget optimization, and anomaly detection.""",
        llm=llm_minimax,
        verbose=True
    )
    
    reporter = Agent(
        role="Report Generator",
        goal="Generate clear financial reports in Spanish",
        backstory="You create clear, actionable financial reports.",
        llm=llm_minimax,
        verbose=True
    )
    
    # Tasks
    collect_task = Task(
        description="Analyze recent spending patterns from transactions",
        agent=collector,
        expected_output="Summary of spending by category"
    )
    
    analyze_task = Task(
        description="Detect anomalies and unusual patterns",
        agent=analyst,
        expected_output="Anomaly report with recommendations"
    )
    
    report_task = Task(
        description="Generate final report in Spanish",
        agent=reporter,
        expected_output="Final financial report"
    )
    
    crew = Crew(
        agents=[collector, analyst, reporter],
        tasks=[collect_task, analyze_task, report_task],
        process=Process.sequential
    )
    
    return crew

if __name__ == "__main__":
    print("""
🧠 Multi-Agent System with MiniMax M2.7
=========================================

Available crews:
1. Research Crew - Research any topic
2. Finance Crew - Analyze spending patterns

Usage:
    from minimax_agents import create_research_crew
    
    crew = create_research_crew("latest AI trends")
    result = crew.kickoff()
    print(result)
""")
    
    # Test MiniMax connection
    print("\n🔍 Testing MiniMax connection...")
    try:
        test = llm_minimax.invoke("Say 'OK' if you can read this")
        print(f"✅ MiniMax working: {test.content[:50]}...")
    except Exception as e:
        print(f"❌ MiniMax error: {e}")
        print("   Make sure MINIMAX_API_KEY is set")
