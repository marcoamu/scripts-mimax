#!/usr/bin/env python3
"""
🎭 Playwright Scraper - Web scraping con browser automation
Usa Chromium para sites con JavaScript
"""
import argparse
import json
from playwright.sync_api import sync_playwright
import sys

def scrape(url, selector=None, text_only=True, screenshot=None, wait=2):
    """Scrapea una URL usando Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set viewport
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        print(f"🔍 Navegando a {url}...")
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Wait for dynamic content
        if wait > 0:
            page.wait_for_timeout(wait * 1000)
        
        result = {"url": url}
        
        if screenshot:
            page.screenshot(path=screenshot, full_page=True)
            result["screenshot"] = screenshot
            print(f"📸 Screenshot guardado: {screenshot}")
        
        if selector:
            elements = page.query_selector_all(selector)
            result["count"] = len(elements)
            result["items"] = []
            for i, el in enumerate(elements):
                if text_only:
                    result["items"].append(el.inner_text()[:500])
                else:
                    result["items"].append(el.inner_html()[:500])
                if i >= 20:  # Max 20 items
                    break
            print(f"📊 Encontrados {len(elements)} elementos")
        else:
            result["title"] = page.title()
            result["content"] = page.content()[:2000]
        
        browser.close()
        return result

def main():
    parser = argparse.ArgumentParser(description="🎭 Playwright Scraper")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("-s", "--selector", help="CSS selector")
    parser.add_argument("-t", "--text", action="store_true", help="Extract text only")
    parser.add_argument("-ss", "--screenshot", help="Save screenshot path")
    parser.add_argument("-w", "--wait", type=int, default=2, help="Wait seconds for JS")
    parser.add_argument("-o", "--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    result = scrape(args.url, args.selector, not args.text, args.screenshot, args.wait)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"💾 Guardado en {args.output}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
