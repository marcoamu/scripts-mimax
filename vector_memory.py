#!/usr/bin/env python3
"""
Vector Memory for OpenClaw
Uses Qdrant as a vector database to store and retrieve memories semantically.
Uses REST API directly for compatibility.
"""

import os
import json
import requests
from datetime import datetime
from langchain_ollama import OllamaEmbeddings

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "openclaw_memory"
EMBEDDING_MODEL = "nomic-embed-text"

# Initialize embeddings
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

def create_collection():
    """Create the memory collection if it doesn't exist."""
    resp = requests.get(f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{COLLECTION_NAME}")
    if resp.status_code == 404:
        requests.put(
            f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{COLLECTION_NAME}",
            json={
                "vectors": {"size": 768, "distance": "Cosine"}
            }
        )
        print(f"✅ Created collection: {COLLECTION_NAME}")
    else:
        print(f"ℹ️  Collection exists: {COLLECTION_NAME}")

def index_memory_file(file_path, category, metadata=None):
    """Index a memory file into Qdrant."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return 0
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    if not content.strip():
        print(f"⚠️  Empty file: {file_path}")
        return 0
    
    # Create embedding
    vector = embeddings.embed_query(content[:2000])
    
    # Parse frontmatter if exists
    title = os.path.basename(file_path)
    if metadata:
        title = metadata.get('title', title)
    
    point_id = hash(file_path) % 1000000
    
    payload = {
        "source": file_path,
        "category": category,
        "title": title,
        "content": content[:5000],
        "indexed_at": datetime.now().isoformat(),
        "type": "memory"
    }
    
    requests.put(
        f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{COLLECTION_NAME}/points",
        json={
            "points": [{
                "id": point_id,
                "vector": vector,
                "payload": payload
            }]
        }
    )
    print(f"✅ Indexed: {file_path} ({len(content)} chars)")
    return 1

def index_all_memories():
    """Index all memory files from the workspace."""
    memory_dir = "/root/.openclaw/workspace/memory"
    docs_dir = "/root/.openclaw/workspace/docs"
    obsidian_dir = "/root/.obsidian"
    
    create_collection()
    
    total = 0
    
    # Index memory files
    if os.path.exists(memory_dir):
        for filename in os.listdir(memory_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(memory_dir, filename)
                category = "memory"
                if filename.startswith('20'):
                    category = "session_log"
                elif filename == "INDEX.md":
                    category = "index"
                total += index_memory_file(filepath, category, {"title": filename})
    
    # Index docs
    if os.path.exists(docs_dir):
        for filename in os.listdir(docs_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(docs_dir, filename)
                total += index_memory_file(filepath, "documentation")
    
    # Index Obsidian vault
    if os.path.exists(obsidian_dir):
        for root, dirs, files in os.walk(obsidian_dir):
            for filename in files:
                if filename.endswith('.md'):
                    filepath = os.path.join(root, filename)
                    # Extract folder as category
                    rel_path = os.path.relpath(filepath, obsidian_dir)
                    folder = rel_path.split('/')[0] if '/' in rel_path else "root"
                    total += index_memory_file(filepath, f"obsidian/{folder}")
    
    print(f"\n📊 Total indexed: {total} documents")
    return total

def search_memory(query, limit=5):
    """Search memories semantically using a query."""
    try:
        query_vector = embeddings.embed_query(query)
        
        resp = requests.post(
            f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{COLLECTION_NAME}/points/search",
            json={
                "vector": query_vector,
                "limit": limit,
                "with_payload": True
            }
        )
        
        results = resp.json().get("result", [])
        
        print(f"\n🔍 Search: '{query}'")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            payload = result.get("payload", {})
            print(f"\n{i}. [{payload.get('category', 'unknown')}] {payload.get('title', 'untitled')}")
            print(f"   Score: {result.get('score', 0):.3f}")
            print(f"   Source: {payload.get('source', 'unknown')}")
            print(f"   Preview: {payload.get('content', '')[:200]}...")
        
        return results
    
    except Exception as e:
        print(f"❌ Search error: {e}")
        import traceback
        traceback.print_exc()
        return []

def add_memory(content, category="general", title=None):
    """Add a new memory to the vector store."""
    create_collection()
    
    vector = embeddings.embed_query(content[:2000])
    
    point_id = int(datetime.now().timestamp() * 1000)
    
    payload = {
        "content": content,
        "category": category,
        "title": title or f"Memory {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "indexed_at": datetime.now().isoformat(),
        "type": "memory"
    }
    
    requests.put(
        f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{COLLECTION_NAME}/points",
        json={
            "points": [{
                "id": point_id,
                "vector": vector,
                "payload": payload
            }]
        }
    )
    print(f"✅ Memory added: {title or 'untitled'}")
    return True

def get_memory_stats():
    """Get statistics about the memory collection."""
    try:
        resp = requests.get(f"http://{QDRANT_HOST}:{QDRANT_PORT}/collections/{COLLECTION_NAME}")
        info = resp.json().get("result", {})
        
        print(f"\n📊 Memory Stats for '{COLLECTION_NAME}'")
        print("=" * 50)
        print(f"   Vectors: {info.get('indexed_vectors_count', 0)}")
        print(f"   Points: {info.get('points_count', 0)}")
        print(f"   Status: {info.get('status', 'unknown')}")
        return info
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def query_memory_context(query, limit=3):
    """Get memory context for a query - returns formatted text for injection."""
    results = search_memory(query, limit=limit)
    
    if not results:
        return ""
    
    context_parts = []
    for r in results:
        if r.get('score', 0) > 0.5:
            payload = r.get('payload', {})
            context_parts.append(f"[{payload.get('category', 'memory')}]: {payload.get('content', '')[:500]}")
    
    if context_parts:
        return "\n\n---\nRelevant memories:\n" + "\n---\n".join(context_parts)
    
    return ""

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("""
🧠 OpenClaw Vector Memory

Usage:
    python3 vector_memory.py index           - Index all memories
    python3 vector_memory.py search <query>   - Search memories
    python3 vector_memory.py add <text>       - Add a memory
    python3 vector_memory.py stats            - Show memory stats
        """)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "index":
        index_all_memories()
    elif command == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else "memories"
        search_memory(query)
    elif command == "add":
        content = sys.argv[2] if len(sys.argv) > 2 else ""
        if content:
            add_memory(content)
        else:
            print("❌ Provide content to add")
    elif command == "stats":
        get_memory_stats()
    else:
        print(f"❌ Unknown command: {command}")
