#!/usr/bin/env python3
"""
CrewAI with MiniMax - Configuration Examples
Uses MiniMax M2.7 for intelligent agent reasoning
"""

import os

# MiniMax API Configuration (OpenAI-compatible)
os.environ["OPENAI_API_KEY"] = os.environ.get("MINIMAX_API_KEY", "your-minimax-api-key")
os.environ["OPENAI_API_BASE"] = "https://api.minimax.io/v1"  # MiniMax OpenAI-compatible endpoint

# Alternative: Use OpenRouter if you have it
# os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
# os.environ["OPENAI_API_KEY"] = "your-openrouter-key"

# Example 1: Basic CrewAI with MiniMax
"""
from crewai import Agent, Task, Crew

# Use MiniMax as the LLM
llm = "minimax/MiniMax-M2.7"  # Or just "gpt-4" if using OpenAI

researcher = Agent(
    role="Researcher",
    goal="Research AI trends thoroughly",
    backstory="You are an expert researcher",
    llm=llm,
    tools=[]
)

crew = Crew(
    agents=[researcher],
    tasks=[...],
    process=Process.sequential
)

result = crew.kickoff()
"""

# Example 2: LangChain with MiniMax
"""
from langchain_ollama import ChatOllama

# For Ollama (local, free)
llm = ChatOllama(model="llama3.2:7b")

# For MiniMax (more intelligent, API cost)
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model="minimax/MiniMax-M2.7",
    api_key=os.environ["MINIMAX_API_KEY"],
    base_url="https://api.minimax.io/v1"
)
"""

# Example 3: Full Integration with Qdrant Memory
"""
from crewai import Agent, Task, Crew, Process
from vector_memory import query_memory_context

# Tools
def search_memory(query: str):
    return query_memory_context(query, limit=5)

memory_tool = Tool(
    name="Knowledge Base",
    func=search_memory,
    description="Query personal knowledge base"
)

# MiniMax-powered agents
researcher = Agent(
    role="Research Analyst",
    goal="Research any topic deeply using the knowledge base",
    backstory="Expert researcher with access to personal knowledge",
    tools=[memory_tool],
    llm="minimax/MiniMax-M2.7"
)

writer = Agent(
    role="Content Writer",
    goal="Write clear summaries in Spanish",
    backstory="Professional writer specializing in technical content",
    llm="minimax/MiniMax-M2.7"
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential
)
"""

# MiniMax API endpoint details:
"""
Base URL: https://api.minimax.io/v1
Model: minimax/MiniMax-M2.7
Format: OpenAI-compatible

Example curl:
curl https://api.minimax.io/v1/chat/completions \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "minimax/MiniMax-M2.7", "messages": [{"role": "user", "content": "Hello"}]}'
"""

print("✅ MiniMax + CrewAI configuration loaded")
print("   Model: MiniMax-M2.7")
print("   Endpoint: https://api.minimax.io/v1")
