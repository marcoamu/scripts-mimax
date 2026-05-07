/**
 * Sentiment Analysis - Analyze tone of content
 * Uses a simple rule-based approach + keyword matching
 */

// Spanish sentiment keywords
const POSITIVE_WORDS = [
  'excelente', 'increíble', 'fantástico', 'genial', 'maravilloso', 'perfecto',
  'gracias', 'feliz', 'éxito', 'ganar', 'mejor', 'bien', 'amor', 'happy',
  'awesome', 'amazing', 'great', 'love', 'best', 'win', 'success'
];

const NEGATIVE_WORDS = [
  'malo', 'terrible', 'horrible', 'pésimo', 'odio', 'fracaso', 'perder',
  'problema', 'error', 'fallo', 'crisis', 'peligro', 'war', 'death',
  'bad', 'hate', 'fail', 'wrong', 'crisis', 'danger', 'die', 'kill'
];

const NEUTRAL_WORDS = [
  'información', 'dato', 'hecho', 'noticia', 'actualización', 'nuevo',
  'video', 'tiktok', 'youtube', 'contenido', 'post', 'article', 'news'
];

function analyzeSentiment(text) {
  if (!text) return { sentiment: 'neutral', score: 0, confidence: 0 };
  
  const words = text.toLowerCase().split(/\s+/);
  let positive = 0;
  let negative = 0;
  let neutral = 0;
  
  words.forEach(word => {
    if (POSITIVE_WORDS.some(w => word.includes(w))) positive++;
    else if (NEGATIVE_WORDS.some(w => word.includes(w))) negative++;
    else neutral++;
  });
  
  const total = positive + negative + neutral;
  const score = total > 0 ? ((positive - negative) / total) : 0;
  
  let sentiment = 'neutral';
  if (score > 0.1) sentiment = 'positive';
  else if (score < -0.1) sentiment = 'negative';
  
  return {
    sentiment,
    score: Math.round(score * 100) / 100,
    confidence: total > 0 ? Math.round((total / words.length) * 100) : 0,
    positive,
    negative,
    neutral
  };
}

// Analyze TikTok content
async function analyzeTikTokContent(db) {
  const results = await db.all(`
    SELECT id, titulo, descripcion 
    FROM tiktok_videos 
    WHERE sentiment IS NULL 
    LIMIT 50
  `);
  
  for (const video of results) {
    const text = `${video.titulo} ${video.descripcion}`;
    const analysis = analyzeSentiment(text);
    
    await db.run(`
      UPDATE tiktok_videos 
      SET sentiment = ?, sentiment_score = ?
      WHERE id = ?
    `, [analysis.sentiment, analysis.score, video.id]);
  }
  
  return results.length;
}

// Analyze YouTube content
async function analyzeYouTubeContent(db) {
  const results = await db.all(`
    SELECT id, title, description 
    FROM youtube_videos 
    WHERE sentiment IS NULL 
    LIMIT 50
  `);
  
  for (const video of results) {
    const text = `${video.title} ${video.description}`;
    const analysis = analyzeSentiment(text);
    
    await db.run(`
      UPDATE youtube_videos 
      SET sentiment = ?, sentiment_score = ?
      WHERE id = ?
    `, [analysis.sentiment, analysis.score, video.id]);
  }
  
  return results.length;
}

// Get sentiment stats
async function getSentimentStats(db) {
  const tiktok = await db.get(`
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive,
      SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative,
      SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral
    FROM tiktok_videos WHERE sentiment IS NOT NULL
  `);
  
  const youtube = await db.get(`
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive,
      SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative,
      SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral
    FROM youtube_videos WHERE sentiment IS NOT NULL
  `);
  
  return { tiktok, youtube };
}

module.exports = { analyzeSentiment, analyzeTikTokContent, analyzeYouTubeContent, getSentimentStats };
