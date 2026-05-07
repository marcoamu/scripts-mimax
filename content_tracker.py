#!/usr/bin/env python3
import subprocess
import requests
from datetime import datetime

API = "http://localhost:3001"

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    return result.stdout

def extract_youtube(channel):
    print(f"  📺 YouTube: @{channel}")
    # Use publish date instead of upload date
    cmd = f'yt-dlp --flat-playlist --playlist-end 3 "https://www.youtube.com/@{channel}/videos" --print "%(title)s|%(publish_date)s|%(view_count)s|%(like_count)s|%(id)s" 2>/dev/null'
    output = run_cmd(cmd)
    
    videos = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    for line in output.strip().split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 5:
                title = parts[0].strip()
                date = parts[1].strip() if len(parts) > 1 else today
                views = parts[2].strip() if len(parts) > 2 else '0'
                likes = parts[3].strip() if len(parts) > 3 else '0'
                vid_id = parts[4].strip() if len(parts) > 4 else ''
                
                # Handle NA or invalid dates
                if date == 'NA' or len(date) != 10:
                    date = today
                
                if vid_id:
                    videos.append({'title': title, 'fecha': date, 'views': views, 'likes': likes, 'id': vid_id})
    
    return videos

def extract_tiktok(username):
    print(f"  🎵 TikTok: @{username}")
    cmd = f'yt-dlp --flat-playlist --playlist-end 3 "https://www.tiktok.com/@{username}" --print "%(title)s|%(upload_date)s|%(view_count)s|%(like_count)s|%(id)s" 2>/dev/null'
    output = run_cmd(cmd)
    
    videos = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    for line in output.strip().split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 5:
                title = parts[0].strip()
                date = parts[1].strip() if len(parts) > 1 else today
                views = parts[2].strip() if len(parts) > 2 else '0'
                likes = parts[3].strip() if len(parts) > 3 else '0'
                vid_id = parts[4].strip() if len(parts) > 4 else ''
                
                # Convert TikTok date YYYYMMDD to YYYY-MM-DD
                if len(date) == 8 and date.isdigit():
                    date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
                
                if vid_id:
                    videos.append({'title': title, 'fecha': date, 'views': views, 'likes': likes, 'id': vid_id})
    
    return videos

def save_content(creator, plataforma, video):
    url = f"https://www.youtube.com/watch?v={video['id']}" if plataforma == 'youtube' else f"https://www.tiktok.com/@{creator}/video/{video['id']}"
    
    data = {
        "creator_username": creator,
        "plataforma": plataforma,
        "titulo": video['title'][:200],
        "views": int(video['views']) if str(video['views']).isdigit() else 0,
        "likes": int(video['likes']) if str(video['likes']).isdigit() else 0,
        "video_url": url,
        "fecha_publicacion": video['fecha']
    }
    
    try:
        r = requests.post(f"{API}/api/content", json=data, timeout=10)
        print(f"    ✓ {video['title'][:40]}")
    except Exception as e:
        print(f"    ✗ {e}")

if __name__ == "__main__":
    print("=== Content Tracker ===\n")
    
    creators = [
        ('lexfridman', 'youtube'),
        ('matthewdavidson', 'youtube'),
        ('rileybrown.ai', 'tiktok'),
        ('gazi.ai', 'tiktok')
    ]
    
    for creator, plataforma in creators:
        try:
            videos = extract_youtube(creator) if plataforma == 'youtube' else extract_tiktok(creator)
            for video in videos:
                save_content(creator, plataforma, video)
        except Exception as e:
            print(f"  ✗ {e}")
    
    print("\n=== Done! ===")
