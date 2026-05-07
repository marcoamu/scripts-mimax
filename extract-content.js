#!/usr/bin/env node
const { execSync } = require('child_process');
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost', port: 5432, database: 'knowledge_base',
  user: 'postgres', password: 'postgres'
});

async function extract(plataforma, limit) {
  console.log(`Extracting ${limit} videos from ${plataforma}...`);
  
  const creators = plataforma === 'youtube'
    ? (await pool.query(`SELECT y.id, y.username FROM tracking_config tc JOIN youtube_creators y ON tc.creator_id = y.id WHERE tc.activo = true AND tc.plataforma = 'youtube'`)).rows
    : (await pool.query(`SELECT t.id, t.username FROM tracking_config tc JOIN tiktok_creators t ON tc.creator_id = t.id WHERE tc.activo = true AND tc.plataforma = 'tiktok'`)).rows;

  console.log(`Found ${creators.length} creators`);
  
  let extracted = 0;
  
  for (const c of creators) {
    try {
      const url = plataforma === 'youtube' 
        ? `https://www.youtube.com/@${c.username}/videos`
        : `https://www.tiktok.com/@${c.username}`;
      
      const cmd = `yt-dlp --flat-playlist --playlist-end ${limit} "${url}" --print "%(title)s|%(upload_date)s|%(view_count)s|%(like_count)s|%(id)s|%(thumbnail)s" 2>/dev/null`;
      
      const output = execSync(cmd, { encoding: 'utf8', timeout: 45 });
      
      const videos = output.split('\n').filter(l => l.includes('|')).map(l => {
        const [title, date, views, likes, vid, thumb] = l.split('|');
        return {
          title: title?.trim(),
          fecha_publicacion: date?.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3'),
          views: parseInt(views) || 0,
          likes: parseInt(likes) || 0,
          video_id: vid?.trim(),
          thumbnail: thumb?.trim(),
          video_url: plataforma === 'youtube' ? `https://www.youtube.com/watch?v=${vid?.trim()}` : `https://www.tiktok.com/@${c.username}/video/${vid?.trim()}`
        };
      }).filter(v => v.video_id);
      
      const table = plataforma === 'youtube' ? 'content_tracking_yt' : 'content_tracking';
      
      for (const v of videos) {
        try {
          const r = await pool.query(`INSERT INTO ${table} (creator_id, plataforma, titulo, transcripcion, fecha_publicacion, views, likes, video_url, thumbnail_url, fecha_extraccion) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,NOW()) ON CONFLICT(video_url) DO NOTHING`, [c.id, plataforma, v.title, '', v.fecha_publicacion, v.views, v.likes, v.video_url, v.thumbnail]);
          if (r.rowCount > 0) { extracted++; console.log(`+ ${v.title?.substring(0,30)}`); }
        } catch(e) {}
      }
    } catch(e) { console.log(`Error ${c.username}: ${e.message}`); }
  }
  
  console.log(`Done! ${extracted} videos extracted`);
  await pool.end();
}

extract(process.argv[2] || 'tiktok', parseInt(process.argv[3]) || 5);
