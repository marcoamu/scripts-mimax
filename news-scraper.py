#!/usr/bin/env python3
"""
📰 News Scraper - Enhanced
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
import os

DB_URL = "postgresql://postgres:postgres@localhost:5432/knowledge_base"

def get_db():
    return psycopg2.connect(DB_URL)

# News sources
GENERAL_SOURCES = [
    {"name": "BBC Mundo", "url": "https://www.bbc.com/mundo", "category": "general"},
    {"name": "El Mundo", "url": "https://www.elmundo.es", "category": "general"},
    {"name": "Marca", "url": "https://www.marca.es", "category": "general"},
    {"name": "AS", "url": "https://www.as.com", "category": "general"},
]

TECH_SOURCES = [
    {"name": "TechCrunch", "url": "https://techcrunch.com", "category": "tech"},
    {"name": "The Verge", "url": "https://www.theverge.com", "category": "tech"},
    {"name": "Wired", "url": "https://www.wired.com", "category": "tech"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com", "category": "tech"},
]

def scrape_page(source):
    """Scrape news from website"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(source["url"], headers=headers, timeout=15)
        
        if r.status_code != 200:
            return []
        
        soup = BeautifulSoup(r.text, 'html.parser')
        articles = []
        
        # Find article titles
        for tag in ['h2', 'h3', 'a']:
            for elem in soup.find_all(tag):
                text = elem.get_text(strip=True)
                if text and len(text) > 30 and len(text) < 200:
                    # Filter out navigation
                    if any(x in text.lower() for x in ['menu', 'login', 'suscribe', 'footer', 'header']):
                        continue
                    articles.append({
                        "title": text,
                        "source": source["name"],
                        "category": source["category"]
                    })
        
        return articles[:8]  # Max 8 per source
        
    except Exception as e:
        print(f"  Error {source['name']}: {e}")
        return []

def save_news(news_list):
    conn = get_db()
    cur = conn.cursor()
    
    saved = 0
    for item in news_list:
        try:
            cur.execute("SELECT id FROM news WHERE title = %s AND category = %s", 
                       (item["title"], item["category"]))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO news (title, source, category, scraped_at, published_date)
                    VALUES (%s, %s, %s, NOW(), NOW())
                """, (item["title"], item["source"], item["category"]))
                saved += 1
        except:
            pass
    
    conn.commit()
    cur.close()
    conn.close()
    return saved

def main():
    print("🔄 Starting news scraper...")
    all_news = []
    
    print("📰 General news...")
    for source in GENERAL_SOURCES:
        news = scrape_page(source)
        print(f"  {source['name']}: {len(news)}")
        all_news.extend(news)
    
    print("💻 Tech news...")
    for source in TECH_SOURCES:
        news = scrape_page(source)
        print(f"  {source['name']}: {len(news)}")
        all_news.extend(news)
    
    saved = save_news(all_news)
    print(f"✅ Saved {saved} new articles")

if __name__ == "__main__":
    main()
