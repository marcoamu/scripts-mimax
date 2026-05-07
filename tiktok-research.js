#!/usr/bin/env node
/**
 * 🎵 TikTok Research Agent v2
 */

const { execSync } = require('child_process');
const https = require('https');

const API = 'http://localhost:3001';
const TIKTOK_USERS = ['arturo.coder'];

function fetchVideos(username) {
  console.log(`🎵 Fetching @${username}...`);
  
  try {
    const output = execSync(
      `yt-dlp "https://www.tiktok.com/@${username}" --dump-json --flat-playlist --max-downloads 3 2>/dev/null`,
      { encoding: 'utf8', maxBuffer: 50 * 1024 * 1024 }
    );
    
    const videos = output.split('\n')
      .filter(Boolean)
      .map(line => {
        try { return JSON.parse(line); } catch(e) { return null; }
      })
      .filter(Boolean);
    
    return videos.map(v => ({
      id: v.id,
      title: v.title,
      description: v.description,
      upload_date: v.upload_date, // 20260304
      date_formatted: v.upload_date ? `${v.upload_date.substring(4,6)}/${v.upload_date.substring(2,4)}/20${v.upload_date.substring(0,2)}` : '',
      timestamp: v.timestamp,
      duration: v.duration,
      duration_string: v.duration_string,
      view_count: v.view_count,
      like_count: v.like_count,
      comment_count: v.comment_count,
      uploader: v.uploader,
      channel_url: v.channel_url,
      webpage_url: v.webpage_url,
      thumbnail: v.thumbnail
    }));
    
  } catch(e) {
    console.log(`Error: ${e.message}`);
    return [];
  }
}

async function saveToResearch(videos, username) {
  for (const v of videos) {
    const task = {
      title: `TikTok @${username}: ${v.title.substring(0, 50)}`,
      description: `
📺 **Video de @${username}**

**Título:** ${v.title}
**Fecha:** ${v.date_formatted}
**Duración:** ${v.duration_string}
**Vistas:** ${v.view_count}
**Likes:** ${v.like_count}
**Comentarios:** ${v.comment_count}

**Descripción:** ${v.description}

**URL:** ${v.webpage_url}
      `.trim(),
      agent: 'research',
      priority: v.view_count > 500 ? 'high' : 'medium',
      status: 'todo',
      notes: `tiktok|${username}|${v.id}|${v.view_count}`
    };
    
    try {
      await fetch(API + '/api/tasks', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(task)
      });
      console.log(`✅ Saved: ${v.title.substring(0,40)}... (${v.date_formatted}) 👁️ ${v.view_count}`);
    } catch(e) {
      console.log(`Save error: ${e.message}`);
    }
  }
}

async function main() {
  console.log('🎵 TikTok Research v2\n');
  
  for (const user of TIKTOK_USERS) {
    const videos = fetchVideos(user);
    
    if (videos.length > 0) {
      console.log(`📊 ${videos.length} videos found\n`);
      await saveToResearch(videos, user);
    }
  }
  
  console.log('\n✅ Complete!');
}

main();
