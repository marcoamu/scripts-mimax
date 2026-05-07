#!/usr/bin/env python3
"""Video Reporter - Generate dynamic video reports"""

import os
import subprocess
from datetime import datetime

VIDEOS_DIR = "/root/.openclaw/workspace/mibimax-app/frontend/public/videos"
TEMPLATE_DIR = "/root/.openclaw/workspace/test-video"

def generate_report_video(title: str, stats: dict, output_name: str) -> str:
    """Generate a video report with stats"""
    
    # Create frame with stats
    frame_file = f"/tmp/frame_{output_name}.png"
    
    # Build stats text
    stats_text = ""
    for key, value in stats.items():
        stats_text += f"- {key}: {value}\n"
    
    # Create image
    cmd = f"""convert -size 1280x720 xc:#1a1a2e \
        -fill white -pointsize 48 -gravity center -annotate +0-100 "{title}" \
        -pointsize 28 -fill "#4ecdc4" -gravity center -annotate +0+50 "{stats_text}" \
        -fill "#888" -pointsize 18 -gravity south -annotate +0+50 "Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}" \
        {frame_file}"""
    
    os.system(cmd)
    
    # Generate video
    output_path = f"{VIDEOS_DIR}/{output_name}.mp4"
    cmd2 = f"ffmpeg -y -loop 1 -i {frame_file} -c:v libx264 -t 10 -pix_fmt yuv420p {output_path}"
    os.system(cmd2)
    
    os.remove(frame_file)
    return output_path

# Example: Generate finance report
if __name__ == "__main__":
    stats = {
        "Ingresos": "+15%",
        "Gastos": "-8%", 
        "Balance": "+624€",
        "Ahorro": "23%"
    }
    
    path = generate_report_video("📊 Informe Financiero", stats, "informe_financiero")
    print(f"✅ Video generated: {path}")
