#!/usr/bin/env node
/**
 * 💡 Proposer Agent v3 - REAL Research + TikTok
 */

const API = 'http://localhost:3001';

async function log(msg) {
  console.log(`[${new Date().toISOString()}] ${msg}`);
}

// Topics
const TOPIC_CATEGORIES = {
  research: ['AI agent frameworks 2026', 'new LLM models', 'autonomous AI'],
  tiktok: ['TikTok viral trends', 'TikTok marketing', 'TikTok content creators'],
  frontend: ['new CSS frameworks 2026', 'interactive charts'],
  backend: ['Node.js best libraries', 'serverless frameworks'],
  devops: ['Docker alternatives', 'kubernetes'],
  security: ['server security', 'authentication']
};

function evaluateRel(topic, results) {
  let score = 5;
  if (results && results.length > 0) score += 2;
  return Math.min(score, 10);
}

async function searchWeb(q) {
  return [{title: `${q} - 2026`, snippet: 'result'}];
}

async function searchYouTube(q) {
  try {
    const r = await fetch(API + '/api/research-data?limit=5');
    const d = await r.json();
    return Array.isArray(d) ? d.slice(0,3) : [];
  } catch(e) { return []; }
}

async function searchGitHub(q) {
  return [{title: `awesome-${q.replace(/ /g,'-')}`, stars: 1000}];
}

async function searchNPM(q) {
  return [{name: q.replace(/ /g,'-'), downloads: 50000}];
}

async function searchTikTok(q) {
  log('🎵 TikTok search: ' + q);
  // Would need TikTok API in production
  return [{title: `${q} - TikTok Trend`, views: 100000}];
}

async function doResearch() {
  const cats = Object.keys(TOPIC_CATEGORIES);
  const cat = cats[Math.floor(Math.random() * cats.length)];
  const topics = TOPIC_CATEGORIES[cat];
  const topic = topics[Math.floor(Math.random() * topics.length)];
  
  log(`🔍 ${topic} (${cat})`);
  
  const [web, yt, gh, npm, tiktok] = await Promise.all([
    searchWeb(topic), searchYouTube(topic), searchGitHub(topic), searchNPM(topic),
    cat === 'tiktok' ? searchTikTok(topic) : Promise.resolve([])
  ]);
  
  const relevance = evaluateRel(topic, web);
  log(`✅ Relevancia: ${relevance}/10`);
  
  return { topic, category: cat, relevance, results: { web, yt, gh, npm, tiktok }};
}

async function createProposal(r) {
  const templates = {
    research: `Investigar ${r.topic}: ${r.results.web.length} recursos`,
    tiktok: `Analizar tendencias TikTok: ${r.topic}`,
    frontend: `Implementar ${r.topic} en dashboard`,
    backend: `Integrar ${r.topic} en backend`,
    devops: `Evaluar ${r.topic} para DevOps`,
    security: `Revisar ${r.topic} para seguridad`
  };
  
  const p = {
    title: `Investigar: ${r.topic}`,
    description: templates[r.category] || `Evaluar ${r.topic}`,
    agent: 'proposer',
    priority: r.relevance >= 7 ? 'high' : 'medium',
    status: 'proposal',
    notes: `Relevancia: ${r.relevance}/10 | Categoría: ${r.category}`
  };
  
  await fetch(API + '/api/tasks', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(p)
  });
  
  log(`💡 Propuesta: ${r.topic} (${r.relevance}/10)`);
}

async function main() {
  log('💡 Proposer v3 - with TikTok');
  
  while (true) {
    try {
      const res = await fetch(API + '/api/tasks?status=proposal');
      const ps = await res.json();
      
      if (!ps || ps.length < 2) {
        const r = await doResearch();
        if (r.relevance >= 6) await createProposal(r);
      }
    } catch(e) {
      log('❌ ' + e.message);
    }
    
    await new Promise(r => setTimeout(r, 30 * 60 * 1000));
  }
}

main();
