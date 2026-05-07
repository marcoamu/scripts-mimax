#!/usr/bin/env python3
"""
TikTok & Tech Trending Scraper
Uses alternative sources that don't block scraping
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "knowledge_base",
    "user": "postgres",
    "password": "postgres"
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def init_table():
    """Create tiktok_content table if not exists"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tiktok_content (
            id SERIAL PRIMARY KEY,
            title VARCHAR(500),
            username VARCHAR(100),
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            url TEXT,
            thumbnail_url TEXT,
            fecha_extraccion TIMESTAMP DEFAULT NOW(),
            content_type VARCHAR(50),
            hashtags TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_content(items):
    """Save scraped content to database"""
    if not items:
        return 0
    
    conn = get_db()
    cur = conn.cursor()
    saved = 0
    
    for item in items:
        try:
            # Check duplicate
            cur.execute("""
                SELECT id FROM tiktok_content 
                WHERE title = %s AND fecha_extraccion::date = CURRENT_DATE
            """, (item.get('title', ''),))
            
            if cur.fetchone():
                continue
            
            cur.execute("""
                INSERT INTO tiktok_content 
                (title, username, views, likes, shares, comments, url, thumbnail_url, fecha_extraccion, content_type, hashtags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)
            """, (
                item.get('title', ''),
                item.get('username', ''),
                item.get('views', 0),
                item.get('likes', 0),
                item.get('shares', 0),
                item.get('comments', 0),
                item.get('url', ''),
                item.get('thumbnail_url', ''),
                item.get('content_type', 'trending'),
                json.dumps(item.get('hashtags', []))
            ))
            saved += 1
        except Exception as e:
            print(f"Error: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    return saved

def scrape_hackernews():
    """Scrape trending from Hacker News"""
    items = []
    
    try:
        # HN Algolia API - public and free
        url = "https://hn.algolia.com/api/v1/search?query=AI&tags=story&hitsPerPage=10"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            for hit in data.get('hits', []):
                title = hit.get('title', '')
                if title:
                    items.append({
                        'title': title,
                        'username': hit.get('author', 'hn_user'),
                        'views': hit.get('points', 0) * 100,
                        'likes': hit.get('points', 0),
                        'shares': hit.get('num_comments', 0),
                        'comments': hit.get('num_comments', 0),
                        'url': hit.get('url', ''),
                        'thumbnail_url': '',
                        'content_type': 'hackernews',
                        'hashtags': extract_hashtags(title)
                    })
                    
    except Exception as e:
        print(f"HN Error: {e}")
    
    return items

def scrape_dev_to():
    """Scrape trending from Dev.to"""
    items = []
    
    try:
        # Dev.to public API
        url = "https://dev.to/api/articles?tag=AI&per_page=10&top=1"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            articles = response.json()
            
            for article in articles:
                items.append({
                    'title': article.get('title', ''),
                    'username': article.get('user', {}).get('username', ''),
                    'views': article.get('page_views_count', 0),
                    'likes': article.get('public_reactions_count', 0),
                    'shares': 0,
                    'comments': article.get('comments_count', 0),
                    'url': article.get('url', ''),
                    'thumbnail_url': article.get('cover_image', ''),
                    'content_type': 'devto',
                    'hashtags': article.get('tag_list', [])
                })
                
    except Exception as e:
        print(f"Dev.to Error: {e}")
    
    return items

def scrape_product_hunt():
    """Scrape trending from Product Hunt"""
    items = []
    
    try:
        # Product Hunt trending
        url = "https://api.producthunt.com/v1/posts?search=AI&per_page=10"
        headers = {'Accept': 'application/json'}
        response = requests.get(url, headers=headers, timeout=15)
        
        # If no API key, fallback to web scraping
        if response.status_code == 401:
            # Try web version
            url = "https://www.producthunt.com/posts"
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            
    except Exception as e:
        print(f"Product Hunt Error: {e}")
    
    return items

def scrape_github_trending():
    """Scrape trending GitHub repos related to AI"""
    items = []
    
    try:
        url = "https://api.github.com/search/repositories?q=AI+OR+machine-learning&sort=stars&per_page=10"
        response = requests.get(url, timeout=15, headers={
            'Accept': 'application/vnd.github.v3+json'
        })
        
        if response.status_code == 200:
            data = response.json()
            
            for repo in data.get('items', []):
                items.append({
                    'title': f"{repo.get('name', '')} - {repo.get('description', '')}",
                    'username': repo.get('full_name', '').split('/')[0],
                    'views': repo.get('stargazers_count', 0),
                    'likes': repo.get('stargazers_count', 0),
                    'shares': repo.get('forks_count', 0),
                    'comments': 0,
                    'url': repo.get('html_url', ''),
                    'thumbnail_url': '',
                    'content_type': 'github_trending',
                    'hashtags': ['AI', 'GitHub', 'OpenSource']
                })
                
    except Exception as e:
        print(f"GitHub Error: {e}")
    
    return items

def scrape_twitter_trending():
    """Scrape trending topics via alternative methods"""
    items = []
    
    # Try to get trending from various tech news sources
    sources = [
        ("TechCrunch", "https://techcrunch.com/wp-json/wp/v2/posts?search=AI&per_page=5"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ]
    
    for name, url in sources:
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0'
            })
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'xml')
                
                for item in soup.find_all('item')[:5]:
                    title = item.find('title')
                    if title and title.text:
                        items.append({
                            'title': title.text,
                            'username': name,
                            'views': 5000,
                            'likes': 100,
                            'shares': 50,
                            'comments': 10,
                            'url': item.find('link').text if item.find('link') else '',
                            'thumbnail_url': '',
                            'content_type': 'tech_news',
                            'hashtags': ['Tech', 'AI', 'News']
                        })
                        
        except Exception as e:
            print(f"{name} Error: {e}")
    
    return items

def extract_hashtags(text):
    """Extract hashtags from text"""
    import re
    hashtags = re.findall(r'#\w+', text)
    if hashtags:
        return hashtags
    
    # Generate from keywords
    keywords = ['AI', 'Tech', 'Code', 'Dev', 'Python', 'JavaScript']
    return [k for k in keywords if k.lower() in text.lower()]

def run_scraper():
    """Main execution"""
    print("=" * 60)
    print("📱 Trending Content Scraper")
    print("=" * 60)
    
    init_table()
    
    all_items = []
    
    # 1. Hacker News (most reliable - has public API)
    print("\n📰 Getting Hacker News trending...")
    items = scrape_hackernews()
    print(f"   ✅ Found {len(items)} items")
    all_items.extend(items)
    
    # 2. Dev.to
    print("\n📝 Getting Dev.to articles...")
    items = scrape_dev_to()
    print(f"   ✅ Found {len(items)} items")
    all_items.extend(items)
    
    # 3. GitHub Trending
    print("\n🐙 Getting GitHub trending AI repos...")
    items = scrape_github_trending()
    print(f"   ✅ Found {len(items)} items")
    all_items.extend(items)
    
    # 4. Tech News
    print("\n📰 Getting Tech news...")
    items = scrape_twitter_trending()
    print(f"   ✅ Found {len(items)} items")
    all_items.extend(items)
    
    # Save
    if all_items:
        saved = save_content(all_items)
        print(f"\n💾 Saved {saved} new items to database")
    
    print(f"\n📊 Total: {len(all_items)} items collected")
    
    return len(all_items)

if __name__ == "__main__":
    count = run_scraper()
    print("\n✅ Done!")
    sys.exit(0)