/**
 * Keyword Tracker - Track keywords in content
 */

const https = require('https');

// Popular tech/AI keywords to track
const DEFAULT_KEYWORDS = [
  'AI', 'GPT', 'OpenAI', 'Claude', 'Gemini', 'ChatGPT',
  'machine learning', 'deep learning', 'neural',
  'automation', 'productivity', 'coding', 'programming',
  'tiktok', 'youtube', 'social media', 'content',
  'crypto', 'bitcoin', 'ethereum', 'blockchain'
];

// Search for content matching keywords
async function searchContentByKeywords(keywords, limit = 20) {
  const { Pool } = require('pg');
  const pool = new Pool({ connectionString: 'postgresql://postgres:postgres@localhost:5432/knowledge_base' });
  
  const results = [];
  
  for (const keyword of keywords) {
    // Search in investigaciones
    const investigaciones = await pool.query(
      `SELECT id, titulo, resumen, fecha, 'investigacion' as type 
       FROM investigaciones 
       WHERE titulo ILIKE $1 OR resumen ILIKE $1
       LIMIT 5`,
      [`%${keyword}%`]
    );
    
    // Search in TikTok (SQLite)
    // Search in YouTube
  }
  
  await pool.end();
  return results;
}

// Get keyword stats
async function getKeywordStats(db) {
  const keywords = DEFAULT_KEYWORDS.map(k => k.toLowerCase());
  const stats = {};
  
  for (const keyword of keywords) {
    stats[keyword] = { count: 0, lastSeen: null };
  }
  
  return stats;
}

// Add custom keyword
async function addKeyword(keyword) {
  const { Pool } = require('pg');
  const pool = new Pool({ connectionString: 'postgresql://postgres:postgres@localhost:5432/knowledge_base' });
  
  try {
    await pool.query(
      `INSERT INTO keyword_tracking (keyword, created_at) 
       VALUES ($1, NOW()) 
       ON CONFLICT (keyword) DO NOTHING`,
      [keyword.toLowerCase()]
    );
    await pool.end();
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// Remove keyword
async function removeKeyword(keyword) {
  const { Pool } = require('pg');
  const pool = new Pool({ connectionString: 'postgresql://postgres:postgres@localhost:5432/knowledge_base' });
  
  try {
    await pool.query('DELETE FROM keyword_tracking WHERE keyword = $1', [keyword.toLowerCase()]);
    await pool.end();
    return { success: true };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// Get trending keywords
async function getTrending() {
  const { Pool } = require('pg');
  const pool = new Pool({ connectionString: 'postgresql://postgres:postgres@localhost:5432/knowledge_base' });
  
  const result = await pool.query(`
    SELECT keyword, mentions, last_seen 
    FROM keyword_stats 
    ORDER BY mentions DESC 
    LIMIT 10
  `);
  
  await pool.end();
  return result.rows;
}

module.exports = { 
  DEFAULT_KEYWORDS,
  searchContentByKeywords,
  getKeywordStats,
  addKeyword,
  removeKeyword,
  getTrending
};
