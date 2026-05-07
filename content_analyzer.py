#!/usr/bin/env python3
"""
Content Analyzer Agent - Analyzes and classifies content using MiniMax M2.7
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict

import psycopg2
import requests

# MiniMax Configuration
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_API_BASE = "https://api.minimax.io/v1"
MODEL = "MiniMax-M2.7"

# Database
DB_URL = "postgresql://postgres:postgres@localhost:5432/knowledge_base"

def get_db():
    return psycopg2.connect(DB_URL)

def get_latest_content(limit: int = 15) -> List[Dict]:
    """Get latest content from all platforms."""
    conn = get_db()
    cur = conn.cursor()
    
    content = []
    
    # Get Reddit content
    cur.execute("""
        SELECT id, titulo, url, score, num_comments, subreddit, fecha_extraccion
        FROM content_tracking_reddit
        ORDER BY fecha_extraccion DESC LIMIT %s
    """, (limit,))
    for r in cur.fetchall():
        content.append({
            "source_table": "reddit",
            "id": str(r[0]),
            "title": r[1],
            "url": r[2],
            "score": r[3] or 0,
            "comments": r[4] or 0,
            "subreddit": r[5],
            "fecha_extraccion": r[6]
        })
    
    # Get LinkedIn content
    cur.execute("""
        SELECT id, titulo, likes, comments, shares, fecha_extraccion
        FROM content_tracking_linkedin
        ORDER BY fecha_extraccion DESC LIMIT %s
    """, (limit,))
    for r in cur.fetchall():
        content.append({
            "source_table": "linkedin",
            "id": str(r[0]),
            "title": r[1],
            "url": r[4],
            "score": r[2] or 0,
            "comments": r[3] or 0,
            "shares": r[4] or 0,
            "fecha_extraccion": r[5]
        })
    
    # Get TikTok content
    cur.execute("""
        SELECT id, titulo, views, likes, video_url, fecha_extraccion
        FROM content_tracking
        ORDER BY fecha_extraccion DESC LIMIT %s
    """, (limit,))
    for r in cur.fetchall():
        content.append({
            "source_table": "tiktok",
            "id": str(r[0]),
            "title": r[1],
            "url": r[3],
            "score": r[2] or 0,
            "likes": r[3] or 0,
            "fecha_extraccion": r[5]
        })
    
    # Get YouTube content
    cur.execute("""
        SELECT id, titulo, views, likes, video_url, fecha_extraccion
        FROM content_tracking_yt
        ORDER BY fecha_extraccion DESC LIMIT %s
    """, (limit,))
    for r in cur.fetchall():
        content.append({
            "source_table": "youtube",
            "id": str(r[0]),
            "title": r[1],
            "url": r[3],
            "score": r[2] or 0,
            "likes": r[3] or 0,
            "fecha_extraccion": r[5]
        })
    
    cur.close()
    conn.close()
    
    # Sort by score and take top 10
    content.sort(key=lambda x: x.get('score', 0), reverse=True)
    return content[:10]

def analyze_with_minimax(content_list: List[Dict]) -> List[Dict]:
    """Use MiniMax M2.7 to analyze and classify content."""
    
    if not MINIMAX_API_KEY:
        print("❌ No MINIMAX_API_KEY found")
        return []
    
    # Build the analysis prompt
    content_text = "\n".join([
        f"- [{c['source_table'].upper()}] {c['title'][:100]} (score: {c.get('score', 0)})"
        for c in content_list
    ])
    
    prompt = f"""You are a content analyzer for an AI-focused system.

Analyze these top content items and classify them by importance and applicability to an AI/LLM development system:

{content_text}

For each content, provide:
1. Importance score (1-10) - how significant is this news
2. Applicability score (1-10) - how applicable is this to building AI systems
3. Classification: HIGH (7+ applicability), MEDIUM (4-6), LOW (1-3)
4. Brief reason for selection
5. Key insights or action points

Format your response as JSON array:
```json
[
  {{
    "title": "exact title from the list",
    "importance_score": 8,
    "applicability_score": 9,
    "classification": "HIGH",
    "selection_reason": "Why this matters",
    "key_insights": "What makes it valuable"
  }}
]
```

Only include items with classification HIGH or MEDIUM. Return top 3-5 items maximum. Be critical - only the best content matters."""

    try:
        response = requests.post(
            f"{MINIMAX_API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            },
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return []
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Extract JSON from response
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_str = content.split("```")[1]
        else:
            json_str = content
        
        analyzed = json.loads(json_str.strip())
        return analyzed
        
    except Exception as e:
        print(f"❌ Error analyzing content: {e}")
        return []

def is_already_analyzed(source_table: str, source_id: str) -> bool:
    """Check if content was already analyzed."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id FROM analyzed_content 
        WHERE source_table = %s AND source_id = %s
        LIMIT 1
    """, (source_table, source_id))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

def save_to_db(analyzed: List[Dict], original_content: List[Dict]):
    """Save analyzed content to PostgreSQL."""
    conn = get_db()
    cur = conn.cursor()
    
    saved = 0
    skipped = 0
    
    for item in analyzed:
        # Find original content
        orig = next((c for c in original_content if c['title'][:50] in item.get('title', '') or item.get('title', '') in c['title'][:50]), None)
        
        if orig:
            # Check if already analyzed
            if is_already_analyzed(orig['source_table'], orig['id']):
                skipped += 1
                print(f"  ⏭️ Already analyzed: {orig['title'][:50]}...")
                continue
                
            cur.execute("""
                INSERT INTO analyzed_content 
                (source_table, source_id, original_title, original_url, importance_score, applicability_score, classification, selection_reason, analysis_full, tags, fecha_extraccion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                orig['source_table'],
                orig['id'],
                item['title'],
                orig.get('url'),
                item.get('importance_score', 5),
                item.get('applicability_score', 5),
                item.get('classification', 'MEDIUM').lower(),
                item.get('selection_reason', ''),
                item.get('key_insights', ''),
                [],
                orig.get('fecha_extraccion')
            ))
            saved += 1
    
    conn.commit()
    cur.close()
    conn.close()
    return saved, skipped

def save_to_obsidian(analyzed: List[Dict]):
    """Save analyzed content to Obsidian."""
    obsidian_dir = "/root/.obsidian/Research/ContentAnalysis"
    os.makedirs(obsidian_dir, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(obsidian_dir, f"analysis_{today}.md")
    
    content = f"""# Content Analysis - {today}

## Summary
- Items analyzed: {len(analyzed)}
- HIGH priority: {len([a for a in analyzed if a.get('classification') == 'HIGH'])}
- MEDIUM priority: {len([a for a in analyzed if a.get('classification') == 'MEDIUM'])}

---

"""
    
    for i, item in enumerate(analyzed, 1):
        importance = item.get('importance_score', 5)
        applicability = item.get('applicability_score', 5)
        cls = item.get('classification', 'MEDIUM')
        
        emoji = "🔴" if cls == "HIGH" else "🟡"
        
        content += f"""## {emoji} {item.get('title', 'Untitled')}

| Metric | Score |
|--------|-------|
| Importance | {importance}/10 |
| Applicability | {applicability}/10 |
| Classification | {cls} |

**Reason:** {item.get('selection_reason', 'N/A')}

**Key Insights:**
{item.get('key_insights', 'N/A')}

---

"""
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Saved to Obsidian: {filepath}")
    return filepath

def send_to_telegram(analyzed: List[Dict]):
    """Send summary to Telegram."""
    # Get Telegram config from .env file
    env_file = "/root/.openclaw/.env"
    telegram_token = ""
    telegram_chat = "291245843"
    
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    telegram_token = line.split("=", 1)[1].strip()
                    break
    
    if not telegram_token:
        print("⚠️ No Telegram token configured")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    message = f"📊 *Content Analysis - {today}*\n\n"
    message += f"📈 {len(analyzed)} items analyzed\n\n"
    
    for i, item in enumerate(analyzed[:5], 1):
        cls = item.get('classification', 'MEDIUM')
        emoji = "🔴" if cls == "HIGH" else "🟡"
        importance = item.get('importance_score', 5)
        applicability = item.get('applicability_score', 5)
        
        title = item.get('title', 'Untitled')[:60]
        message += f"{i}. {emoji} *{title}*\n"
        message += f"   📊 Imp: {importance} | 📱 Apl: {applicability}\n"
        message += f"   💡 {item.get('selection_reason', '')[:80]}...\n\n"
    
    message += "\n _Full analysis in Content Analysis folder_"
    
    try:
        requests.post(
            f"https://api.telegram.org/bot{telegram_token}/sendMessage",
            json={
                "chat_id": telegram_chat,
                "text": message,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        print("✅ Sent to Telegram")
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

def main():
    print(f"🌟 Content Analyzer started at {datetime.now()}")
    
    # Step 1: Get latest content
    print("📥 Fetching latest content...")
    content = get_latest_content(limit=15)
    print(f"   Found {len(content)} items")
    
    if not content:
        print("❌ No content to analyze")
        return
    
    # Step 2: Analyze with MiniMax
    print("🤖 Analyzing with MiniMax M2.7...")
    analyzed = analyze_with_minimax(content)
    print(f"   Selected {len(analyzed)} items for deep analysis")
    
    if not analyzed:
        print("❌ No items passed analysis filter")
        return
    
    # Step 3: Save to PostgreSQL
    print("💾 Saving to PostgreSQL...")
    saved_db, skipped = save_to_db(analyzed, content)
    print(f"   Saved {saved_db} items to DB")
    if skipped > 0:
        print(f"   Skipped {skipped} already analyzed items")
    
    # Step 4: Save to Obsidian
    print("📓 Saving to Obsidian...")
    obsidian_path = save_to_obsidian(analyzed)
    
    # Step 5: Send to Telegram
    print("📱 Sending Telegram notification...")
    send_to_telegram(analyzed)
    
    print(f"\n✅ Analysis complete!")
    print(f"   - Items analyzed: {len(analyzed)}")
    print(f"   - DB records: {saved_db}")
    print(f"   - Obsidian: {obsidian_path}")
    
    return analyzed

if __name__ == "__main__":
    main()

# ============================================================================
# STANDALONE RUN WITH REPORTING
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("📊 Content Analyzer - Starting analysis...")
    print("="*60)
    
    # Get content
    print("\n📥 Fetching latest content...")
    content = get_latest_content(limit=20)
    print(f"   Found {len(content)} items")
    
    # Filter out already analyzed
    new_content = []
    for c in content:
        if not is_already_analyzed(c['source_table'], c['id']):
            new_content.append(c)
    
    skipped = len(content) - len(new_content)
    print(f"   📊 {skipped} already analyzed, {len(new_content)} new")
    
    if len(new_content) == 0:
        print("\n✅ No new content to analyze today!")
        print("   All recent content has already been analyzed.")
        sys.exit(0)
    
    content = new_content
    
    print(f"\n🤖 Analyzing {len(content)} new items...")
    analyzed = analyze_with_minimax(content)
    print(f"   Selected {len(analyzed)} items for deep analysis")
    
    if not analyzed:
        print("\n❌ No items passed analysis filter")
        sys.exit(0)
    
    print("\n💾 Saving to PostgreSQL...")
    saved_db, skipped = save_to_db(analyzed, content)
    print(f"   Saved {saved_db} items to DB")
    if skipped > 0:
        print(f"   Skipped {skipped} already analyzed")
    
    print("\n📓 Saving to Obsidian...")
    obsidian_path = save_to_obsidian(analyzed)
    
    print("\n📱 Sending Telegram notification...")
    send_to_telegram(analyzed)
    
    print(f"\n✅ Analysis complete!")
    print(f"   - Items analyzed: {len(analyzed)}")
    print(f"   - DB records: {saved_db}")
    print(f"   - Obsidian: {obsidian_path}")
