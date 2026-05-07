#!/usr/bin/env python3
"""
🔍 Research Scraper con Playwright
Scraping de news, trends, social media
"""
import argparse
import json
from playwright.sync_api import sync_playwright
from datetime import datetime
import sys

SOURCES = {
    'hackernews': {
        'url': 'https://news.ycombinator.com',
        'selector': '.titleline > a',
        'title': 'Hacker News'
    },
    'reddit-tech': {
        'url': 'https://www.reddit.com/r/technology/hot/.json?limit=10',
        'selector': 'h3',
        'title': 'Reddit Tech'
    },
    'trending-github': {
        'url': 'https://github.com/trending',
        'selector': '.h3.lh-condensed',
        'title': 'GitHub Trending'
    }
}

def scrape_source(source_key, limit=10):
    """Scrapea una fuente específica"""
    if source_key not in SOURCES:
        print(f"❌ Fuente desconocida: {source_key}")
        print(f"Fuentes disponibles: {', '.join(SOURCES.keys())}")
        return None
    
    source = SOURCES[source_key]
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        print(f"🔍 Scraping {source['title']}...")
        page.goto(source['url'], wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)
        
        elements = page.query_selector_all(source['selector'])
        
        for i, el in enumerate(elements[:limit]):
            text = el.inner_text()[:200].strip()
            if text:
                results.append({
                    'id': i + 1,
                    'title': text,
                    'source': source_key,
                    'scraped_at': datetime.now().isoformat()
                })
        
        browser.close()
    
    return results

def scrape_all(limit=10):
    """Scrapea todas las fuentes"""
    all_results = {}
    
    for source_key in SOURCES.keys():
        results = scrape_source(source_key, limit)
        if results:
            all_results[source_key] = results
        else:
            all_results[source_key] = []
    
    return all_results

def main():
    parser = argparse.ArgumentParser(description="🔍 Research Scraper con Playwright")
    parser.add_argument('-s', '--source', help='Fuente específica (hackernews, reddit-tech, trending-github)')
    parser.add_argument('-l', '--limit', type=int, default=10, help='Límite de resultados')
    parser.add_argument('-o', '--output', help='Archivo JSON de salida')
    parser.add_argument('--screenshot', action='store_true', help='Tomar screenshot')
    
    args = parser.parse_args()
    
    if args.source:
        results = {args.source: scrape_source(args.source, args.limit)}
    else:
        results = scrape_all(args.limit)
    
    # Print summary
    for source, items in results.items():
        print(f"\n📊 {source}: {len(items)} items")
        for item in items[:3]:
            print(f"  {item['id']}. {item['title'][:80]}...")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Guardado en {args.output}")
    
    # Take screenshot if requested
    if args.screenshot:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(SOURCES[args.source or 'hackernews']['url'], wait_until="load")
            page.screenshot(path=f"/tmp/research_{args.source or 'all'}.png", full_page=True)
            browser.close()
            print(f"\n📸 Screenshot guardado")

if __name__ == "__main__":
    main()
