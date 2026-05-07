#!/usr/bin/env python3
"""📰 News from RSS"""

import requests
import psycopg2
import xml.etree.ElementTree as ET

DB = "postgresql://postgres:postgres@localhost:5432/knowledge_base"

def get_db():
    return psycopg2.connect(DB)

RSS_FEEDS = {
    "general": [
        ("BBC", "https://feeds.bbci.co.uk/mundo/rss.xml"),
        ("Europa Press", "https://www.europapress.es/rss/rss.aspx"),
    ],
    "tech": [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("MIT Tech", "https://www.technologyreview.com/feed/"),
    ]
}

def fetch_rss(url, name):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            items = []
            for item in root.findall(".//item")[:5]:
                title = item.findtext("title", "").strip()[:150]
                link = item.findtext("link", "").strip()
                
                if title:
                    items.append({"title": title, "url": link[:500] if link else ""})
            return items
    except Exception as e:
        print(f"Error: {e}")
    return []

def main():
    print("📰 Extrayendo...")
    all_news = []
    
    for cat, feeds in RSS_FEEDS.items():
        for name, url in feeds:
            items = fetch_rss(url, name)
            if items:
                print(f"  ✅ {name}: {len(items)}")
                for item in items:
                    all_news.append({
                        "title": item["title"],
                        "url": item["url"],
                        "category": cat,
                        "source": name
                    })
    
    all_news = all_news[:20]
    
    if all_news:
        conn = get_db()
        cur = conn.cursor()
        saved = 0
        
        for item in all_news:
            cur.execute("SELECT id FROM news WHERE title = %s", (item["title"],))
            if not cur.fetchone():
                cur.execute("""INSERT INTO news (title, url, source, category, scraped_at, published_date) 
                    VALUES (%s, %s, %s, %s, NOW(), NOW())""",
                    (item["title"], item["url"], item["source"], item["category"]))
                saved += 1
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"\n✅ {saved} noticias nuevas")
    else:
        print("❌ Sin noticias")

if __name__ == "__main__":
    main()
