#!/usr/bin/env node
const { execSync } = require('child_process');
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost', port: 5432, database: 'knowledge_base',
  user: 'postgres', password: 'postgres'
});

const videoUrl = process.argv[2];
const outputId = process.argv[3];

console.log("Downloading:", videoUrl);

// Download audio
try {
  execSync(`yt-dlp -x --audio-format mp3 -o "/tmp/${outputId}.mp3" "${videoUrl}" --quiet 2>&1`, { timeout: 120 });
} catch(e) {
  console.log("Download error:", e.message);
  process.exit(1);
}

console.log("Transcribing with Whisper...");

// Transcribe
const result = execSync(`python3 -c "
import whisper
model = whisper.load_model('base')
result = model.transcribe('/tmp/${outputId}.mp3')
print(result['text'][:8000])
"`, { encoding: 'utf8', timeout: 300 });

const transcripcion = result.trim();

// Find the video by URL and update
const table = videoUrl.includes('tiktok') ? 'content_tracking' : 'content_tracking_yt';

try {
  await pool.query(`UPDATE ${table} SET transcripcion = $1, transcripcion_status = 'completed' WHERE video_url = $2`, [transcripcion, videoUrl]);
  console.log("Saved to DB!");
} catch(e) {
  console.log("Error saving:", e.message);
}

// Cleanup
execSync(`rm -f /tmp/${outputId}.mp3`);

pool.end();
