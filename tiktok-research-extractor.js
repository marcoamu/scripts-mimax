#!/usr/bin/env node
/**
 * 🎵 TikTok Content Extractor - Gets actual video content
 */

const { execSync } = require('child_process');

function getTikTokVideos(username) {
  try {
    const output = execSync(
      `yt-dlp --flat-playlist --playlist-end 10 "https://www.tiktok.com/@${username}" --print "%(title)s|%(view_count)s|%(description)s" 2>/dev/null`,
      { encoding: 'utf8', timeout: 60 }
    );
    
    const videos = output.split('\n').filter(l => l.includes('|')).map(line => {
      const [title, views, desc] = line.split('|');
      return {
        title: title?.substring(0, 100) || '',
        views: parseInt(views) || 0,
        description: desc?.substring(0, 200) || ''
      };
    }).filter(v => v.views > 0);
    
    return videos;
  } catch(e) {
    console.log("Error:", e.message);
    return [];
  }
}

// Test
const test = getTikTokVideos('bio_makers1');
console.log("=== @bio_makers1 - Últimos videos ===");
test.forEach(v => {
  console.log(`\n👁️ ${v.views.toLocaleString()} vistas`);
  console.log(`   ${v.title}`);
  console.log(`   ${v.description.substring(0,80)}...`);
});
