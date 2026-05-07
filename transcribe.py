#!/usr/bin/env python3
import sys
import whisper
import os

video_url = sys.argv[1] if len(sys.argv) > 1 else ""
output_id = sys.argv[2] if len(sys.argv) > 2 else "temp"

print(f"Downloading: {video_url}")

# Download audio
os.system(f'yt-dlp -x --audio-format mp3 -o "/tmp/{output_id}.mp3" "{video_url}" --quiet 2>&1')

# Transcribe
print("Transcribing...")
model = whisper.load_model("base")
result = model.transcribe(f"/tmp/{output_id}.mp3")

# Save transcript
with open(f"/tmp/{output_id}.txt", "w") as f:
    f.write(result["text"])

print("Done!")
os.system(f"rm -f /tmp/{output_id}.mp3")
