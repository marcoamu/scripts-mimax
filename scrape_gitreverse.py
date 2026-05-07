#!/usr/bin/env python3
"""Scrape GitReverse using Playwright - intercept API calls"""

import json
from playwright.sync_api import sync_playwright

def scrape_gitreverse():
    print("🚀 Starting GitReverse scrape...")
    
    prompts = []
    api_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Intercept API responses
        def handle_response(response):
            url = response.url
            if 'api' in url.lower() or 'prompt' in url.lower():
                try:
                    data = response.json()
                    api_data.append({'url': url, 'data': data})
                    print(f"📡 API call: {url[:80]}")
                except:
                    pass
        
        page.on('response', handle_response)
        
        try:
            page.goto('https://www.gitreverse.com/library', wait_until='networkidle', timeout=30000)
            print("📄 Page loaded")
            
            # Wait for content to load
            page.wait_for_timeout(5000)
            
            # Scroll to trigger lazy loading
            for _ in range(3):
                page.evaluate('window.scrollBy(0, 800)')
                page.wait_for_timeout(2000)
            
            print(f"📡 Intercepted {len(api_data)} API responses")
            
            # Extract prompts from API data
            for item in api_data:
                data = item.get('data', {})
                if isinstance(data, dict):
                    # Look for prompts in common fields
                    for key in ['prompts', 'items', 'data', 'results', 'cards']:
                        if key in data:
                            items = data[key]
                            if isinstance(items, list):
                                for it in items:
                                    if isinstance(it, dict):
                                        # Look for prompt text
                                        for field in ['prompt', 'description', 'text', 'content']:
                                            if field in it:
                                                text = it[field]
                                                if isinstance(text, str) and len(text) > 30:
                                                    prompts.append(text)
            
            print(f"✅ Found {len(prompts)} prompts")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()
    
    return prompts

if __name__ == "__main__":
    prompts = scrape_gitreverse()
    
    if prompts:
        with open('/tmp/gitreverse_prompts.json', 'w') as f:
            json.dump(prompts, f, indent=2)
        print(f"💾 Saved {len(prompts)} prompts")
        for i, p in enumerate(prompts[:5], 1):
            print(f"\n{i}. {p[:150]}...")
    else:
        print("❌ No prompts found")
