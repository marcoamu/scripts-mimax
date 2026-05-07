const { execSync } = require('child_process');
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost', port: 5432, database: 'knowledge_base',
  user: 'postgres', password: 'postgres'
});

async function run() {
  const videoUrl = process.argv[2];
  const outputId = process.argv[3];
  
  console.log("Downloading:", videoUrl);
  
  try {
    execSync(`yt-dlp -x --audio-format mp3 -o "/tmp/${outputId}.mp3" "${videoUrl}" --quiet 2>&1`, { timeout: 120 });
  } catch(e) {
    console.log("Download error:", e.message);
    process.exit(1);
  }
  
  console.log("Transcribing...");
  
  try {
    const result = execSync(`python3 -c "
import whisper
model = whisper.load_model('base')
result = model.transcribe('/tmp/${outputId}.mp3')
print(result['text'][:8000])
"`, { encoding: 'utf8', timeout: 300 });
    
    const transcripcion = result.trim();
    const table = videoUrl.includes('tiktok') ? 'content_tracking' : 'content_tracking_yt';
    
    await pool.query(`UPDATE ${table} SET transcripcion = $1, transcripcion_status = 'completed' WHERE video_url = $2`, [transcripcion, videoUrl]);
    console.log("Saved!");
  } catch(e) {
    console.log("Error:", e.message);
  }
  
  execSync(`rm -f /tmp/${outputId}.mp3`);
  await pool.end();
}

run();
