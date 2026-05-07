#!/usr/bin/env python3
"""
Podcast Generator using Ollama + gTTS
=====================================
Genera resúmenes de audio tipo NotebookLM usando:
- Ollama para resumir contenido
- gTTS para convertir a audio
"""

import os
import sys
import json
import subprocess
import requests
from gtts import gTTS
import tempfile

# Configuration
OLLAMA_MODEL = "llama3.2:1b"
OUTPUT_DIR = "/root/.openclaw/workspace/data/podcasts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_url(url):
    """Fetch content from URL using jina"""
    try:
        # Use jina API if available, otherwise use simple request
        resp = requests.get(url, timeout=30)
        return resp.text[:10000]  # Limit content
    except Exception as e:
        return f"Error fetching: {e}"

def summarize_with_ollama(text, prompt=None):
    """Summarize text using Ollama"""
    if not prompt:
        prompt = """Eres un presentador de podcast experto. 
Resume el siguiente contenido de forma entretenida y clara.
Usa un tono conversacional, como si estuvieras explicando a un amigo.
Máximo 300 palabras:"""
    
    full_prompt = f"{prompt}\n\nContenido:\n{text[:4000]}"
    
    try:
        result = subprocess.run(
            ["ollama", "generate", "-m", OLLAMA_MODEL, "--prompt", full_prompt, "--stream", "false"],
            capture_output=True, text=True, timeout=120
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

def text_to_speech(text, output_file, lang="es"):
    """Convert text to speech using gTTS"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_file)
        return output_file
    except Exception as e:
        return f"Error: {e}"

def generate_podcast(url=None, text=None, title="Podcast", lang="es"):
    """Generate a podcast from URL or text"""
    
    print(f"🎧 Generando podcast: {title}")
    
    # 1. Get content
    if url:
        print(f"📥 Extrayendo contenido de: {url}")
        content = fetch_url(url)
    elif text:
        content = text
    else:
        return "Error: Necesitas URL o texto"
    
    # 2. Summarize with Ollama
    print("📝 Generando resumen...")
    summary = summarize_with_ollama(content)
    
    # 3. Convert to speech
    print("🎤 Generando audio...")
    safe_title = "".join(c for c in title if c.isalnum() or c in " -").strip()[:50]
    output_file = f"{OUTPUT_DIR}/{safe_title}_{lang}.mp3"
    
    audio_file = text_to_speech(summary, output_file, lang)
    
    return {
        "title": title,
        "summary": summary[:500],
        "audio": audio_file,
        "size": os.path.getsize(audio_file) if os.path.exists(audio_file) else 0
    }

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        url = sys.argv[1]
        title = sys.argv[2] if len(sys.argv) > 2 else "Mi Podcast"
        result = generate_podcast(url=url, title=title)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python podcast_generator.py <url> <title>")
        print("\nEjemplo:")
        print("  python podcast_generator.py 'https://example.com/article' 'Resumen de Artículo'")
