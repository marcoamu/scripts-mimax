#!/usr/bin/env python3
"""
RAG Search
Semantic search over research documents
"""

import sys
import os
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import RealDictCursor

# Config
MODEL_NAME = 'all-MiniLM-L6-v2'
DB_CONFIG = {
    'host': 'localhost',
    'database': 'knowledge_base',
    'user': 'postgres',
    'password': 'postgres'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def embed_query(text):
    """Generate embedding for query"""
    model = SentenceTransformer(MODEL_NAME)
    embedding = model.encode([text])[0]
    return embedding.tolist()

def semantic_search(query, top_k=5):
    """Search research using semantic similarity"""
    
    # Generate query embedding
    print(f"🔍 Searching for: {query}")
    query_embedding = embed_query(query)
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Vector similarity search
    cur.execute("""
        SELECT 
            d.documento_id,
            d.contenido,
            i.tema,
            i.resumen,
            i.dominio,
            i.fecha,
            1 - (d.embedding <=> %s::vector) as similarity
        FROM document_embeddings d
        JOIN investigaciones i ON d.documento_id = i.id
        ORDER BY d.embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, query_embedding, top_k))
    
    results = cur.fetchall()
    conn.close()
    
    return results

def main():
    query = ' '.join(sys.argv[1:]) or "artificial intelligence"
    
    print("=" * 50)
    print("🔍 RAG Semantic Search")
    print("=" * 50)
    
    results = semantic_search(query)
    
    print(f"\n📊 Found {len(results)} results:\n")
    
    for i, r in enumerate(results, 1):
        sim = round(r['similarity'] * 100, 1)
        print(f"{i}. [{sim}% similarity] {r['tema']}")
        print(f"   Domain: {r.get('dominio', 'N/A')}")
        print(f"   Date: {r.get('fecha', 'N/A')}")
        print(f"   Summary: {r.get('resumen', '')[:150]}...")
        print()

if __name__ == '__main__':
    main()
