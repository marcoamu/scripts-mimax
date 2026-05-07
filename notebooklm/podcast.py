#!/usr/bin/env python3
"""
NotebookLM-style Podcast Generator
=================================
Uses Ollama API + gTTS to create audio summaries from URLs
"""

import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from datetime import datetime

# Config
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"
OUTPUT_DIR = "/root/.openclaw/workspace/data/podcasts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_text_from_url(url):
    """Extract clean text from URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        text = ' '.join(text.split())
        return text[:8000]
    except Exception as e:
        return f"Error: {e}"

def summarize_with_ollama(text):
    """Create summary using Ollama API"""
    prompt = f"""Eres un presentador de podcast interesante.
Crea un resumen de 2-3 párrafos del siguiente contenido.
Usa tono amigable y conversacional:

Contenido: {text[:5000]}"""
    
    try:
        resp = requests.post(OLLAMA_API, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 300}
        }, timeout=180)
        
        result = resp.json()
        return result.get('response', 'Error getting response')
    except Exception as e:
        return f"Error: {e}"

def create_audio(text, filename, lang="es"):
    """Create audio file"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)
        return filename
    except Exception as e:
        return f"Error: {e}"

def generate_podcast(url, title=None, lang="es"):
    """Main function"""
    print(f"🎧 Generando podcast: {url}")
    
    # 1. Extract
    print("📥 Extrayendo contenido...")
    content = extract_text_from_url(url)
    if content.startswith("Error:"):
        return {"error": content}
    
    # 2. Summarize
    print("📝 Creando resumen con IA...")
    summary = summarize_with_ollama(content)
    
    # 3. Audio
    print("🎤 Generando audio...")
    if not title:
        title = f"Podcast_{datetime.now().strftime('%Y%m%d_%H%M')}"
    
    safe_name = "".join(c for c in title if c.isalnum() or c in " -_")[:40]
    audio_file = f"{OUTPUT_DIR}/{safe_name}.mp3"
    
    create_audio(summary, audio_file, lang)
    
    size = os.path.getsize(audio_file) if os.path.exists(audio_file) else 0
    
    return {
        "success": True,
        "title": title,
        "url": url,
        "audio_file": audio_file,
        "size_kb": round(size/1024, 1),
        "summary": summary[:300] + "..."
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python podcast.py <url> [title]")
        sys.exit(1)
    
    url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = generate_podcast(url, title)
    print("\n" + "="*50)
    print(json.dumps(result, indent=2, ensure_ascii=False))
