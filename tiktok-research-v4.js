#!/usr/bin/env node
/**
 * 🎵 TikTok Research Agent v4 - Smart + Classification
 * - Tracks processed channels
 * - Only fetches new videos
 * - Classifies by content type
 */

const { execSync } = require('child_process');
const https = require('https');

const API = 'http://localhost:3001';

// Content type classifiers
const CONTENT_CLASSIFIERS = {
  'openclaw': ['openclaw', 'claude code', 'claude'],
  'n8n': ['n8n', 'automatizacion', 'workflow', 'automate', 'automatizar', 'nodo'],
  'ai': ['ai', 'inteligencia artificial', 'ia ', ' ia,', 'machine learning'],
  'python': ['python', 'programacion', 'coding', 'desarrollo'],
  'javascript': ['javascript', 'js ', ' node.', 'react', 'typescript'],
  'architecture': ['arquitectura', 'design patterns', 'software', 'system design'],
  'gemini': ['gemini', 'google ai'],
  'gpt': ['gpt', 'chatgpt', 'openai'],
  'automation': ['automatiz', 'workflow', 'bot', 'integration'],
  'tutorial': ['tutorial', 'how to', 'como hacer', 'aprende', 'learn'],
  'business': ['negocio', 'emprender', 'empresa', 'cliente', 'venta', 'dinero'],
  'games': ['game', 'juego', 'gaming']
};

// Track processed channels
async function markChannelProcessed(platform, username, count) {
  try {
    await fetch(API + '/api/tasks', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        title: `_track_${platform}_${username}`,
        description: 'Internal tracking',
        agent: 'system',
        priority: 'low',
        status: 'done',
        notes: `channel_tracking|${username}|${count}`
      })
    });
  } catch(e) {}
}

// Check if channel was already processed
async function isChannelProcessed(username) {
  try {
    const res = await fetch(API + '/api/tasks?status=done&agent=system');
    const tasks = await res.json();
    return tasks.some(t => t.notes && t.notes.includes(`|${username}|`));
  } catch(e) { return false; }
}

// Classify content type
function classifyContent(title, description) {
  const text = (title + ' ' + (description || '')).toLowerCase();
  const types = [];
  
  for (const [type, keywords] of Object.entries(CONTENT_CLASSIFIERS)) {
    for (const kw of keywords) {
      if (text.includes(kw)) {
        types.push(type);
        break;
      }
    }
  }
  
  return types.length > 0 ? types.join(',') : 'general';
}

// Fetch only last 5 most relevant videos
function fetchTikTokVideos(username, limit = 5) {
  try {
    const output = execSync(
      `yt-dlp "https://www.tiktok.com/@${username}" --dump-json --flat-playlist --max-downloads 50 2>/dev/null`,
      { encoding: 'utf8', maxBuffer: 50 * 1024 * 1024 }
    );
    
    const allVideos = output.split('\n')
      .filter(Boolean)
      .map(line => { try { return JSON.parse(line); } catch(e) { return null; } })
      .filter(Boolean)
      .map(v => ({
        id: v.id,
        title: v.title,
        description: v.description,
        upload_date: v.upload_date,
        view_count: v.view_count || 0,
        like_count: v.like_count || 0,
        uploader: v.uploader,
        webpage_url: v.webpage_url,
        timestamp: v.timestamp || 0
      }));
    
    // Sort by date (newest first) and filter last 30 days
    const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
    const recentVideos = allVideos
      .filter(v => v.timestamp * 1000 > thirtyDaysAgo)
      .slice(0, 5);
    
    return recentVideos;
  } catch(e) {
    return [];
  }
}

// Main
async function main() {
  const users = process.argv.slice(2) || ['arturo.coder'];
  
  for (const user of users) {
    console.log(`\n🎵 @${user}`);
    
    // Check if already processed
    const processed = await isChannelProcessed(user);
    if (processed) {
      console.log(`  ⏭️ Already processed, skipping...`);
      continue;
    }
    
    // Fetch videos
    const videos = fetchTikTokVideos(user, 20);
    
    if (videos.length === 0) {
      console.log(`  ❌ No videos found`);
      continue;
    }
    
    // Save new videos only
    let saved = 0;
    for (const v of videos) {
      const contentType = classifyContent(v.title, v.description);
      const priority = v.view_count > 10000 ? 'high' : v.view_count > 1000 ? 'medium' : 'low';
      
      const task = {
        title: `TikTok @${user}: ${(v.title || '').substring(0, 50)}`,
        description: `Fecha: ${v.upload_date} | 👁️ ${v.view_count} | ❤️ ${v.like_count}\n\n${v.description || ''}`,
        agent: 'research',
        priority: priority,
        status: 'todo',
        source: 'tiktok',
        content_type: contentType,
        views: v.view_count
      };
      
      await fetch(API + '/api/tasks', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(task)
      });
      saved++;
    }
    
    // Mark as processed
    await markChannelProcessed('tiktok', user, saved);
    console.log(`  ✅ ${saved} videos saved (${videos.length} found)`);
  }
}

main();
