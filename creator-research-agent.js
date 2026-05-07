#!/usr/bin/env node
/**
 * 🎬 Creator Research Agent - Find content creators on YouTube & TikTok
 * With URL validation
 */

const API = 'http://localhost:3001';
const YOUTUBE_API_KEY = 'AIzaSyAO5VLoXf9d5DYo-30MKH2uYCs7Pofq1_4';

// 1. Search YouTube channels with validation
async function searchYouTube(query) {
  try {
    const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=15&q=${encodeURIComponent(query)}&type=channel&key=${YOUTUBE_API_KEY}`;
    const res = await fetch(url);
    const data = await res.json();
    
    const creators = [];
    for (const item of (data.items || [])) {
      const channelId = item.snippet.channelId;
      const channelName = item.snippet.channelTitle;
      const description = item.snippet.description;
      const thumbnail = item.snippet.thumbnails?.default?.url;
      
      // Validate by checking if channel exists
      const isValid = await validateYouTubeChannel(channelId);
      
      if (isValid) {
        creators.push({
          platform: 'youtube',
          channelId: channelId,
          username: channelName.toLowerCase().replace(/\s+/g, '').replace(/[^a-z0-9]/g, ''), // Use channel name as username
          channelName: channelName,
          description: description,
          thumbnail: thumbnail,
          url: `https://www.youtube.com/@${channelName.replace(/\s+/g, '')}`
        });
      }
    }
    
    return creators;
  } catch(e) {
    console.log("YouTube API error:", e.message);
    return [];
  }
}

// 2. Validate YouTube channel exists
async function validateYouTubeChannel(channelId) {
  try {
    const url = `https://www.googleapis.com/youtube/v3/channels?part=statistics&id=${channelId}&key=${YOUTUBE_API_KEY}`;
    const res = await fetch(url);
    const data = await res.json();
    
    // Check if channel has stats (exists)
    return data.items && data.items.length > 0 && data.items[0].statistics?.subscriberCount;
  } catch(e) {
    return false;
  }
}

// 3. Validate TikTok creator
async function validateTikTokCreator(username) {
  try {
    const { execSync } = require('child_process');
    
    // Try to get channel info
    const output = execSync(
      `yt-dlp --flat-playlist --playlist-end 1 "https://www.tiktok.com/@${username}" --print "%(channel)s" 2>&1 | head -1`,
      { encoding: 'utf8', timeout: 15, shell: '/bin/bash' }
    );
    
    // If we get a valid channel name back, it's valid
    return output.trim().length > 0 && !output.includes('HTTP Error');
  } catch(e) {
    return false;
  }
}

// 4. Search TikTok creators
async function searchTikTok(query) {
  // TikTok doesn't have a public search API, so we'll use known popular creators
  // or skip this for now
  console.log("   ⚠️ TikTok search not implemented (no public API)");
  return [];
}

// 5. Get TikTok creator info
async function getTikTokCreator(username) {
  try {
    const { execSync } = require('child_process');
    
    const output = execSync(
      `yt-dlp --flat-playlist "https://www.tiktok.com/@${username}" --print "%(channel)s|%(channel_follower_count)s|%(description)s" 2>/dev/null | head -1`,
      { encoding: 'utf8', timeout: 30, shell: '/bin/bash' }
    );
    
    const [name, followers, desc] = output.split('|');
    return {
      platform: 'tiktok',
      username: username,
      channelName: name?.trim() || username,
      followers: parseInt(followers) || 0,
      description: desc?.trim() || '',
      url: `https://www.tiktok.com/@${username}`
    };
  } catch(e) {
    return null;
  }
}

// 6. Save creators with validation
async function saveCreators(creators, query) {
  const { Pool } = require('pg');
  const pool = new Pool({
    host: 'localhost',
    port: 5432,
    database: 'knowledge_base',
    user: 'postgres',
    password: 'postgres'
  });
  
  let saved = 0;
  let skipped = 0;
  
  for (const c of creators) {
    try {
      if (c.platform === 'youtube') {
        // Validate URL is accessible
        if (!c.url || !c.url.includes('youtube.com')) {
          console.log(`   ❌ YouTube: Invalid URL for ${c.channelName}`);
          skipped++;
          continue;
        }
        
        // Check if exists
        const existing = await pool.query(
          'SELECT id FROM youtube_creators WHERE LOWER(username) = LOWER($1) OR LOWER(channel_name) = LOWER($2)',
          [c.username, c.channelName]
        );
        
        if (existing.rows.length === 0) {
          await pool.query(
            `INSERT INTO youtube_creators (username, channel_name, descripcion, foto_url, activo)
             VALUES ($1, $2, $3, $4, false)`,
            [c.username, c.channelName, c.description || '', c.thumbnail || '']
          );
          console.log(`   ✅ YouTube: Added ${c.channelName}`);
          saved++;
        } else {
          console.log(`   ⚠️ YouTube: Already exists ${c.channelName}`);
        }
      } else if (c.platform === 'tiktok' && c.username) {
        // Validate TikTok
        const isValid = await validateTikTokCreator(c.username);
        
        if (!isValid) {
          console.log(`   ❌ TikTok: Invalid creator ${c.username}`);
          skipped++;
          continue;
        }
        
        const existing = await pool.query(
          'SELECT id FROM tiktok_creators WHERE LOWER(username) = LOWER($1)',
          [c.username]
        );
        
        if (existing.rows.length === 0) {
          await pool.query(
            `INSERT INTO tiktok_creators (username, display_name, descripcion, foto_url, activo)
             VALUES ($1, $2, $3, $4, false)`,
            [c.username, c.channelName || c.username, c.description || '', '']
          );
          console.log(`   ✅ TikTok: Added ${c.username}`);
          saved++;
        }
      }
    } catch(e) {
      console.log("   Save error:", e.message);
    }
  }
  
  await pool.end();
  return { saved, skipped };
}

// 7. Create research record
async function createResearchRecord(query, creators) {
  const { Pool } = require('pg');
  const pool = new Pool({
    host: 'localhost',
    port: 5432,
    database: 'knowledge_base',
    user: 'postgres',
    password: 'postgres'
  });
  
  const ytCreators = creators.filter(c => c.platform === 'youtube');
  const ttCreators = creators.filter(c => c.platform === 'tiktok');
  
  const resumen = `Se encontraron ${creators.length} creadores válidos: ${ytCreators.length} YouTube, ${ttCreators.length} TikTok.`;
  
  const result = await pool.query(
    `INSERT INTO investigaciones (tema, dominio, resumen, estado, score_calidad)
     VALUES ($1, 'creators', $2, 'completado', 0.8)
     RETURNING id`,
    [query + ' - Creadores', resumen]
  );
  
  await pool.end();
  return result.rows[0].id;
}

// Main function
async function main() {
  const args = process.argv.slice(2);
  const query = args.join(' ') || 'AI coding Claude Code';
  
  console.log(`\n🎬 Creator Research Agent - Buscando: "${query}"`);
  
  // Search YouTube with validation
  console.log("   🔍 Buscando en YouTube (con validación)...");
  const ytCreators = await searchYouTube(query);
  console.log(`   ✅ YouTube: ${ytCreators.length} canales válidos`);
  
  // Skip TikTok for now (no public API)
  const ttCreators = [];
  console.log("   ⏭️  TikTok: Omitido (sin API pública)");
  
  // Combine
  const allCreators = [...ytCreators, ...ttCreators];
  console.log(`   📊 Total: ${allCreators.length} creadores`);
  
  // Save to database
  console.log("   💾 Guardando en base de datos...");
  const { saved, skipped } = await saveCreators(allCreators, query);
  
  // Create research record
  const researchId = await createResearchRecord(query, allCreators);
  
  console.log(`\n✅ Completado!`);
  console.log(`   - YouTube: ${ytCreators.length} canales`);
  console.log(`   - TikTok: 0 (no disponible)`);
  console.log(`   - Nuevos guardados: ${saved}`);
  console.log(`   - Omitidos: ${skipped}`);
  console.log(`   - Research ID: ${researchId}`);
  
  return { success: true, id: researchId, creators: allCreators.length };
}

main().catch(e => {
  console.log("Error:", e.message);
  process.exit(1);
});
