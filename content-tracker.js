#!/usr/bin/env node
/**
 * 📡 Content Tracker - Deduplicated
 */

const { spawn } = require('child_process');
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'knowledge_base',
  user: 'postgres',
  password: 'postgres'
});

function log(msg) {
  console.log(`[${new Date().toISOString()}] ${msg}`);
}

function runCmd(cmd) {
  return new Promise((resolve, reject) => {
    const child = spawn('/bin/bash', ['-c', cmd], { 
      cwd: '/root/.openclaw/workspace',
      timeout: 90000 
    });
    
    let stdout = '';
    let stderr = '';
    
    child.stdout.on('data', (data) => { stdout += data.toString(); });
    child.stderr.on('data', (data) => { stderr += data.toString(); });
    
    child.on('close', (code) => {
      if (code === 0) resolve(stdout);
      else reject(new Error(stderr || `Exit code ${code}`));
    });
    
    child.on('error', reject);
    
    setTimeout(() => {
      child.kill();
      reject(new Error('Timeout'));
    }, 90000);
  });
}

// YouTube extraction
async function extractYouTubeContent(username, limit = 5) {
  log(`📺 Extracting YouTube: @${username}`);
  
  try {
    const cmd = `yt-dlp --flat-playlist --playlist-end ${limit} "https://www.youtube.com/@${username}/videos" --print "%(title)s|%(upload_date)s|%(view_count)s|%(like_count)s|%(id)s|%(thumbnail)s" 2>/dev/null`;
    const output = await runCmd(cmd);
    
    const videos = output.split('\n')
      .filter(line => line.includes('|'))
      .map(line => {
        const [title, date, views, likes, id, thumb] = line.split('|');
        return {
          title: title?.trim(),
          fecha_publicacion: date?.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3') || null,
          views: parseInt(views) || 0,
          likes: parseInt(likes) || 0,
          video_id: id?.trim(),
          thumbnail: thumb?.trim(),
          video_url: `https://www.youtube.com/watch?v=${id?.trim()}`
        };
      })
      .filter(v => v.video_id);
    
    log(`   Found ${videos.length} videos`);
    return videos;
  } catch(e) {
    log(`   Error: ${e.message}`);
    return [];
  }
}

// TikTok extraction
async function extractTikTokContent(username, limit = 5) {
  log(`🎵 Extracting TikTok: @${username}`);
  
  try {
    const cmd = `yt-dlp --flat-playlist --playlist-end ${limit} "https://www.tiktok.com/@${username}" --print "%(title)s|%(upload_date)s|%(view_count)s|%(like_count)s|%(id)s|%(thumbnail)s" 2>/dev/null`;
    const output = await runCmd(cmd);
    
    const videos = output.split('\n')
      .filter(line => line.includes('|'))
      .map(line => {
        const [title, date, views, likes, id, thumb] = line.split('|');
        return {
          title: title?.trim(),
          fecha_publicacion: date?.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3') || null,
          views: parseInt(views) || 0,
          likes: parseInt(likes) || 0,
          video_id: id?.trim(),
          thumbnail: thumb?.trim(),
          video_url: `https://www.tiktok.com/@${username}/video/${id?.trim()}`
        };
      })
      .filter(v => v.video_id);
    
    log(`   Found ${videos.length} videos`);
    return videos;
  } catch(e) {
    log(`   Error: ${e.message}`);
    return [];
  }
}

// Save with ON CONFLICT DO NOTHING
async function saveContent(creatorId, plataforma, videos) {
  if (videos.length === 0) return 0;
  
  let saved = 0;
  
  for (const video of videos) {
    try {
      if (plataforma === 'youtube') {
        await pool.query(
          `INSERT INTO content_tracking_yt (creator_id, plataforma, titulo, fecha_publicacion, views, likes, video_url, thumbnail_url)
           VALUES ($1, 'youtube', $2, $3, $4, $5, $6, $7)
           ON CONFLICT DO NOTHING`,
          [creatorId, video.title, video.fecha_publicacion, video.views, video.likes, video.video_url, video.thumbnail]
        );
      } else {
        await pool.query(
          `INSERT INTO content_tracking (creator_id, plataforma, titulo, fecha_publicacion, views, likes, video_url, thumbnail_url)
           VALUES ($1, 'tiktok', $2, $3, $4, $5, $6, $7)
           ON CONFLICT DO NOTHING`,
          [creatorId, video.title, video.fecha_publicacion, video.views, video.likes, video.video_url, video.thumbnail]
        );
      }
      saved++;
    } catch(e) {
      log(`   Save error: ${e.message}`);
    }
  }
  
  return saved;
}

async function main() {
  const plataforma = process.argv[2] || 'tiktok';
  const limit = parseInt(process.argv[3]) || 5;
  
  log(`🚀 Starting content tracking (deduplicated)...`);
  
  // Get creators from tracking_config
  const result = await pool.query(`
    SELECT tc.creator_id, tc.plataforma, tc.activo,
           tiktok.username, yt.username as yt_username
    FROM tracking_config tc
    LEFT JOIN tiktok_creators tiktok ON tc.creator_id = tiktok.id
    LEFT JOIN youtube_creators yt ON tc.creator_id = yt.id
    WHERE tc.activo = true AND tc.plataforma = $1
  `, [plataforma]);
  
  log(`Found ${result.rows.length} ${plataforma} creators`);
  
  for (const row of result.rows) {
    const username = plataforma === 'youtube' ? row.yt_username : row.username;
    if (!username) continue;
    
    let videos = [];
    
    if (plataforma === 'youtube') {
      videos = await extractYouTubeContent(username, limit);
    } else {
      videos = await extractTikTokContent(username, limit);
    }
    
    if (videos.length > 0) {
      const saved = await saveContent(row.creator_id, plataforma, videos);
      log(`   Saved ${saved} videos`);
    }
  }
  
  log(`✅ Content tracking completed`);
  await pool.end();
}

main().catch(e => {
  log(`Fatal error: ${e.message}`);
  process.exit(1);
});
