#!/usr/bin/env python3
import sys
import whisper
import os
import subprocess

video_url = sys.argv[1]
video_id = sys.argv[2] if len(sys.argv) > 2 else "temp"

print("Downloading audio...")

# Download
result = subprocess.run([
    'yt-dlp', '-x', '--audio-format', 'mp3',
    '-o', f'/tmp/{video_id}.mp3',
    video_url
], capture_output=True, timeout=120)

print("Transcribing...")

# Load model and transcribe
model = whisper.load_model("base")
result = model.transcribe(f"/tmp/{video_id}.mp3")
text = result["text"]

# Print to stdout
print(text[:8000])

# Cleanup
os.remove(f"/tmp/{video_id}.mp3")
