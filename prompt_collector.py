#!/usr/bin/env python3
"""
AI Prompt Collector - Fetches prompts from various sources and saves to database
"""

import os
import sys
import re
import requests
from datetime import datetime
import psycopg2

DB_URL = "postgresql://postgres:postgres@localhost:5432/knowledge_base"

def get_db():
    return psycopg2.connect(DB_URL)

def is_duplicate(prompt_text):
    """Check if prompt already exists in database"""
    conn = get_db()
    cur = conn.cursor()
    # Check by similarity (first 100 chars)
    cur.execute("SELECT id FROM ai_prompts WHERE LEFT(prompt_text, 100) = LEFT(%s, 100) LIMIT 1", (prompt_text[:100],))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

def save_prompt(title, prompt_text, source, source_url="", category="general", style="general"):
    """Save prompt if not duplicate"""
    if is_duplicate(prompt_text):
        return False
    
    # Calculate scores based on prompt quality indicators
    quality = calculate_quality(prompt_text)
    usefulness = calculate_usefulness(prompt_text)
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO ai_prompts (title, prompt_text, source, source_url, category, style, quality_score, usefulness_score, rating)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (title[:500], prompt_text[:2000], source, source_url, category, style, quality, usefulness, 
          'high' if usefulness >= 7 else 'low' if usefulness < 4 else 'medium'))
    conn.commit()
    cur.close()
    conn.close()
    return True

def calculate_quality(prompt):
    """Calculate quality score 1-10 based on prompt structure"""
    score = 5
    # Bonus for detailed descriptions
    if len(prompt) > 100: score += 1
    if len(prompt) > 300: score += 1
    # Bonus for style indicators
    if any(word in prompt.lower() for word in ['style', 'lighting', 'composition', 'portrait', 'landscape']): score += 1
    # Bonus for quality indicators
    if any(word in prompt.lower() for word in ['4k', '8k', 'high resolution', 'detailed', 'photorealistic']): score += 1
    # Bonus for specific art styles
    if any(word in prompt.lower() for word in ['oil painting', 'digital art', 'concept art', 'illustration']): score += 1
    return min(10, max(1, score))

def calculate_usefulness(prompt):
    """Calculate how useful for YouTube content"""
    score = 5
    prompt_lower = prompt.lower()
    # High value for YouTube
    if any(word in prompt_lower for word in ['youtube', ' shorts', 'thumbnail', 'content']): score += 2
    if any(word in prompt_lower for word in ['trending', 'viral', 'popular']): score += 1
    # Versatile topics score higher
    if any(word in prompt_lower for word in ['portrait', 'landscape', 'character', 'concept art']): score += 2
    # Platform specific
    if any(word in prompt_lower for word in ['midjourney', 'dalle', 'stable diffusion', 'flux']): score += 1
    return min(10, max(1, score))

def scrape_clickup():
    """Scrape AI art prompts from ClickUp"""
    print("📥 Scraping ClickUp...")
    prompts_found = 0
    try:
        url = "https://clickup.com/blog/ai-art-prompts/"
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            # Extract prompts - they have numbered lists
            text = resp.text
            # Simple pattern matching for prompts
            patterns = [
                r'"([^"]+)"(?:isch|as)\s*(?:a|an)\s*([^\.]+)',
                r'(?:Try|Prompt|Use):\s*["\']?([^"\'\n]+)',
            ]
            for match in re.finditer(r'"([^"]{50,500})"', text):
                prompt = match.group(1).strip()
                if len(prompt) > 30 and not prompt.startswith('http'):
                    if save_prompt(f"ClickUp Prompt", prompt, "ClickUp", url, "general", "artistic"):
                        prompts_found += 1
    except Exception as e:
        print(f"  ⚠️ Error: {e}")
    return prompts_found

def scrape_prompts_list():
    """Scrape from various prompt lists"""
    print("📥 Scraping prompt lists...")
    prompts_found = 0
    
    sources = [
        ("Stable Diffusion Prompts", "https://www.reddit.com/r/StableDiffusion/comments/1ci15q3/list_of_prompts_for_ai_image_generation_dalle/", "stable_diffusion"),
        ("AI Art Prompts", "https://starryai.com/en/blog/ai-art-prompts", "general"),
        ("AI Image Prompts", "https://pxz.ai/blog/best-prompt-for-ai-image-generator", "general"),
    ]
    
    for title, url, category in sources:
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                text = resp.text
                # Extract quoted strings that look like prompts
                for match in re.finditer(r'"([^"]{40,400})"', text):
                    prompt = match.group(1).strip()
                    if len(prompt) > 50 and not 'http' in prompt[:20]:
                        if save_prompt(f"{title}", prompt, title.split()[0], url, category, "general"):
                            prompts_found += 1
        except Exception as e:
            print(f"  ⚠️ {title}: {e}")
    
    return prompts_found

def generate_ai_prompts():
    """Generate AI prompts using MiniMax"""
    print("🤖 Generating AI prompts with MiniMax...")
    
    prompt_templates = [
        "Generate 10 creative AI image prompts for YouTube Shorts that would go viral. Include style, lighting, and composition details. Respond in JSON format: [{\"prompt\": \"...\", \"category\": \"...\", \"style\": \"...\"}]",
        
        "Create 10 Midjourney-style prompts for stunning landscape or portrait photography. Each prompt should include artistic style, lighting conditions, and camera settings. Respond in JSON format.",
        
        "Generate 10 prompts for abstract or surreal AI art that would make engaging YouTube thumbnails. Include vivid colors and eye-catching elements. Respond in JSON format.",
        
        "Create 10 prompts for character concept art in different styles (cyberpunk, fantasy, portrait, sci-fi). Each should be detailed enough for high-quality AI generation. Respond in JSON format.",
        
        "Generate 10 prompts for trending AI art styles in 2026 - include specific artists names, techniques, and visual elements. These should be unique and eye-catching. Respond in JSON format.",
    ]
    
    # Get API key from .env
    api_key = None
    with open("/root/.openclaw/.env") as f:
        for line in f:
            if line.startswith("MINIMAX_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                break
    
    if not api_key:
        print("  ⚠️ No MINIMAX_API_KEY found")
        return 0
    
    prompts_found = 0
    for template in prompt_templates:
        try:
            resp = requests.post(
                "https://api.minimax.io/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "MiniMax-M2.7", "messages": [{"role": "user", "content": template}], "temperature": 0.8, "max_tokens": 800},
                timeout=120
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                # Parse JSON from response
                import json
                try:
                    # Strip thinking tokens first
                    content = re.sub(r'.*?</think>', '', content, flags=re.DOTALL).strip()
                    # Extract JSON array
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0]
                    elif "[" in content and "]" in content:
                        start = content.find("[")
                        end = content.rfind("]") + 1
                        content = content[start:end]
                    
                    prompts = json.loads(content)
                    if isinstance(prompts, list):
                        for p in prompts:
                            if isinstance(p, dict) and "prompt" in p:
                                prompt_text = p["prompt"]
                                category = p.get("category", "general")
                                style = p.get("style", "general")
                                if save_prompt(f"AI Generated - {category}", prompt_text, "MiniMax", "", category, style):
                                    prompts_found += 1
                except json.JSONDecodeError:
                    # Try finding individual prompts
                    for line in content.split('\n'):
                        if len(line) > 50 and not line.startswith('#'):
                            if save_prompt("AI Generated", line.strip(), "MiniMax", "", "general", "general"):
                                prompts_found += 1
        except Exception as e:
            print(f"  ⚠️ Error: {e}")
    
    return prompts_found


# ============================================================================
# GITREVERSE SCRAPER
# ============================================================================

def scrape_gitreverse():
    """Scrape prompts from GitReverse library."""
    print("📥 Scraping GitReverse...")
    prompts_found = 0
    
    try:
        url = "https://www.gitreverse.com/library"
        resp = requests.get(url, timeout=30)
        
        if resp.status_code == 200:
            prompt_pattern = r'"description":"([^"]{50,500})"'
            for match in re.finditer(prompt_pattern, resp.text):
                prompt_text = match.group(1).strip()
                if len(prompt_text) > 30:
                    if save_prompt(f"GitReverse", prompt_text, "gitreverse", url, "general", "general"):
                        prompts_found += 1
    except Exception as e:
        print(f"  ⚠️ Error: {e}")
    
    return prompts_found

def fetch_gitreverse_api():
    """Fetch from GitReverse."""
    print("📥 Fetching GitReverse...")
    prompts_found = 0
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        for page in range(1, 20):
            url = f"https://www.gitreverse.com/library?sort=top&page={page}"
            resp = requests.get(url, headers=headers, timeout=30)
            
            if resp.status_code == 200:
                text = resp.text
                
                # Find prompts in description field
                desc_pattern = r'"description":"([^"]{50,500})"'
                for match in re.finditer(desc_pattern, text):
                    prompt_text = match.group(1).strip()
                    if len(prompt_text) > 30 and len(prompt_text) < 1000:
                        if save_prompt(f"GitReverse", prompt_text, "gitreverse", url, "general", "general"):
                            prompts_found += 1
                            
            if page > 3 and prompts_found > 10:
                break
                
    except Exception as e:
        print(f"  ⚠️ API Error: {e}")
    
    return prompts_found

def main():
    print(f"🎯 AI Prompt Collector started at {datetime.now()}")
    
    total = 0
    total += scrape_clickup()
    total += scrape_prompts_list()
    total += generate_ai_prompts()
    # GitReverse disabled - requires Playwright
    # total += fetch_gitreverse_api()
    # try:
    #     total += scrape_gitreverse_playwright()
    # except NameError:
    #     print("⚠️ scrape_gitreverse_playwright not defined, skipping")
    
    print(f"\n✅ Collected {total} new prompts")
    
    # Stats
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT rating, COUNT(*) FROM ai_prompts GROUP BY rating")
    stats = cur.fetchall()
    print("\n📊 Current stats:")
    for rating, count in stats:
        print(f"   {rating}: {count}")
    cur.close()
    conn.close()
    
    return total


# ============================================================================
# GITREVERSE SCRAPER (using Playwright)
# ============================================================================

def scrape_gitreverse_playwright():
    """Scrape prompts from GitReverse using Playwright."""
    print("📥 Scraping GitReverse with Playwright...")
    prompts_found = 0
    
    try:
        from playwright.sync_api import sync_playwright
        import re
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            api_data = []
            
            def handle_response(response):
                url = response.url
                if 'api' in url.lower():
                    try:
                        data = response.json()
                        api_data.append(data)
                    except:
                        pass
            
            page.on('response', handle_response)
            
            page.goto('https://www.gitreverse.com/library', wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(3000)
            
            for _ in range(3):
                page.evaluate('window.scrollBy(0, 800)')
                page.wait_for_timeout(1500)
            
            # Extract prompts from API
            for data in api_data:
                if isinstance(data, dict):
                    for key in ['prompts', 'items', 'data', 'results']:
                        if key in data:
                            items = data[key]
                            if isinstance(items, list):
                                for it in items:
                                    if isinstance(it, dict):
                                        for field in ['prompt', 'description', 'text']:
                                            if field in it:
                                                text = it[field]
                                                if isinstance(text, str) and len(text) > 30:
                                                    if save_prompt(f"GitReverse", text, "gitreverse", "https://www.gitreverse.com/library", "general", "general"):
                                                        prompts_found += 1
            
            browser.close()
            
    except ImportError:
        print("⚠️ Playwright not available, skipping GitReverse")
    except Exception as e:
        print(f"⚠️ GitReverse error: {e}")
    
    return prompts_found

if __name__ == '__main__':
    main()
