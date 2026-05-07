#!/usr/bin/env python3
"""📰 News with MiniMax"""

import requests, psycopg2, json, re
from datetime import datetime

DB = "postgresql://postgres:postgres@localhost:5432/knowledge_base"
API_KEY = "YOUR_MINIMAX_API_KEY_HERE"

def get_db():
    return psycopg2.connect(DB)

def ask(prompt):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "MiniMax-M2.1", 
        "messages": [{"role": "system", "content": "Responde solo con JSON array de noticias. Sin texto extra."}, {"role": "user", "content": prompt}],
        "max_tokens": 2000
    }
    r = requests.post("https://api.minimax.io/v1/chat/completions", headers=headers, json=payload, timeout=60)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    return None

def parse_response(text):
    """Extract JSON after thinking"""
    # Remove thinking if present
    if "<think>" in text:
        text = text.split("</think>")[-1]
    text = text.strip()
    # Remove markdown
    text = re.sub(r'^```json?', '', re.sub(r'```$', '', text))
    try:
        return json.loads(text.strip())
    except:
        return None

def main():
    topics = [
        ("España y mundo", "general"),
        ("Tecnología e IA", "tech")
    ]
    
    all_news = []
    for topic, cat in topics:
        print(f"🔍 {cat}: {topic}...")
        result = ask(f"8 noticias importantes de HOY 15 marzo 2026 sobre {topic}. JSON: [{{\"titular\": \"...\", \"categoria\": \"{cat}\", \"importancia\": 1-10}}]")
        
        if result:
            news = parse_response(result)
            if news:
                for n in news:
                    all_news.append({"title": n.get("titular", ""), "category": n.get("categoria", cat), "importance": n.get("importancia", 5)})
                print(f"   ✅ {len(news)} noticias")
            else:
                print(f"   ❌ No se pudo parsear")
        else:
            print(f"   ❌ Error de API")
    
    if all_news:
        conn = get_db()
        cur = conn.cursor()
        saved = 0
        for item in all_news:
            cur.execute("SELECT id FROM news WHERE title = %s", (item["title"],))
            if not cur.fetchone():
                cur.execute("INSERT INTO news (title, source, category, scraped_at, published_date) VALUES (%s, %s, %s, NOW(), NOW())", 
                           (item["title"], "MiniMax", item["category"]))
                saved += 1
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Guardadas: {saved}")
    else:
        print("❌ Sin noticias")

if __name__ == "__main__":
    main()
