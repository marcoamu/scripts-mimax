#!/usr/bin/env python3
"""
RAG Embedding Generator
Generates embeddings for research documents using sentence-transformers
"""

import sys
import os
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import execute_values
import uuid

# Config
MODEL_NAME = 'all-MiniLM-L6-v2'  # Fast, 384 dimensions
DB_CONFIG = {
    'host': 'localhost',
    'database': 'knowledge_base',
    'user': 'postgres',
    'password': 'postgres'
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def load_research():
    """Load all research from database"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, tema, resumen, hipotesis, conclusion 
        FROM investigaciones 
        WHERE estado = 'completado'
    """)
    
    research = []
    for row in cur.fetchall():
        research.append({
            'id': str(row[0]),
            'tema': row[1] or '',
            'resumen': row[2] or '',
            'hipotesis': row[3] or '',
            'conclusion': row[4] or ''
        })
    
    conn.close()
    return research

def generate_embeddings(texts):
    """Generate embeddings for texts"""
    print(f"📊 Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    
    print(f"🔢 Generating embeddings for {len(texts)} documents...")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    return embeddings.tolist()

def save_embeddings(documents, embeddings):
    """Save embeddings to database"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Clear existing embeddings
    cur.execute("TRUNCATE TABLE document_embeddings CASCADE")
    
    # Insert new embeddings
    data = []
    for doc, emb in zip(documents, embeddings):
        data.append((
            doc['id'],
            'investigacion',
            doc['tema'] + ' ' + doc['resumen'][:1000],
            emb
        ))
    
    execute_values(
        cur,
        "INSERT INTO document_embeddings (documento_id, documento_tipo, contenido, embedding) VALUES %s",
        data
    )
    
    conn.commit()
    conn.close()
    
    print(f"✅ Saved {len(embeddings)} embeddings to database")

def main():
    print("=" * 50)
    print("🔬 RAG Embedding Generator")
    print("=" * 50)
    
    # Load research
    print("\n📥 Loading research from database...")
    research = load_research()
    print(f"   Found {len(research)} research documents")
    
    if len(research) == 0:
        print("❌ No research to process")
        return
    
    # Combine text for embedding
    texts = []
    for doc in research:
        text = f"{doc['tema']}. {doc['resumen'][:500]}".strip()
        texts.append(text)
    
    # Generate embeddings
    embeddings = generate_embeddings(texts)
    
    # Save to database
    save_embeddings(research, embeddings)
    
    print("\n" + "=" * 50)
    print("✅ Embedding generation complete!")
    print("=" * 50)

if __name__ == '__main__':
    main()
