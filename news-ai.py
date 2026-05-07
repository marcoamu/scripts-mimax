#!/usr/bin/env python3
"""
📰 News: Brave Search + MiniMax Summary
"""

import requests
import psycopg2
import json
import re
from datetime import datetime

DB = "postgresql://postgres:postgres@localhost:5432/knowledge_base"
BRAVE_API = ""  # Add Brave API key if available
MINIMAX_KEY = "YOUR_MINIMAX_API_KEY_HERE"

def get_db():
    return psycopg2.connect(DB)

def search_news(query):
    """Search news using DuckDuckGo (no API key needed)"""
    try:
        url = f"https://duckduckgo.com/?q={query}&format=json"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        
        # Try alternative
        url = "https://html.duckduckgo.com/html/"
        data = {"q": query}
        r = requests.post(url, data=data, headers=headers, timeout=10)
        
        # Extract titles
        titles = re.findall(r'<a class="result__a"[^>]*>([^<]+)</a>', r.text)
        return titles[:10] if titles else []
    except Exception as e:
        print(f"Search error: {e}")
        return []

def summarize_with_minimax(news_list, category):
    """Use MiniMax to summarize and format news"""
    if not news_list:
        return []
    
    titles_text = "\n".join([f"- {t}" for t in news_list[:8]])
    
    prompt = f"""Resume y mejora estas noticias en JSON:
[{titles_text}]

Formato JSON: [{{"titular": "título mejorado", "categoria": "{category}", "importancia": 1-10}}]
Solo JSON, sin texto extra."""

    headers = {"Authorization": f"Bearer {MINIMAX_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "MiniMax-M2.1",
        "messages": [{"role": "system", "content": "Responde solo JSON array."}, {"role": "user", "content": prompt}],
        "max_tokens": 2000
    }
    
    try:
        r = requests.post("https://api.minimax.io/v1/chat/completions", headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            result = r.json()["choices"][0]["message"]["content"]
            # Extract JSON
            if "<think>" in result:
                result = result.split("</think>")[-1]
            result = re.sub(r'^```json?', '', re.sub(r'```$', '', result.strip()))
            return json.loads(result.strip())
    except Exception as e:
        print(f"MiniMax error: {e}")
    
    # Fallback - return original titles
    return [{"titular": t, "categoria": category, "importancia": 5} for t in news_list[:8]]

def main():
    print("🔍 Buscando noticias...")
    
    # Search topics
    general_news = search_news("noticias España mundo hoy")
    tech_news = search_news("tecnología inteligencia artificial noticias hoy")
    
    print(f"   General: {len(general_news)} encontrados")
    print(f"   Tech: {len(tech_news)} encontrados")
    
    # Process with MiniMax
    print("🤖 Procesando con MiniMax...")
    
    all_news = []
    
    if general_news:
        processed = summarize_with_minimax(general_news, "general")
        all_news.extend(processed)
        print(f"   General: {len(processed)} procesadas")
    
    if tech_news:
        processed = summarize_with_minimax(tech_news, "tech")
        all_news.extend(processed)
        print(f"   Tech: {len(processed)} procesadas")
    
    # Save to database
    if all_news:
        conn = get_db()
        cur = conn.cursor()
        saved = 0
        
        for item in all_news:
            title = item.get("titular", item.get("title", ""))
            if title:
                cur.execute("SELECT id FROM news WHERE title = %s", (title,))
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO news (title, source, category, scraped_at, published_date, summary)
                        VALUES (%s, %s, %s, NOW(), NOW(), %s)
                    """, (title, "AI Search", item.get("categoria", "general"), f"Importancia: {item.get('importancia', 5)}/10"))
                    saved += 1
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Guardadas: {saved} noticias nuevas")
    else:
        print("❌ Sin noticias para guardar")

if __name__ == "__main__":
    main()
