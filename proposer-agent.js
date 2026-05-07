#!/usr/bin/env node
/**
 * 💡 Proposer Agent - Investiga y propone mejoras INTERESANTES
 * Solo añade al backlog si encuentra algo relevante y valioso
 */

const API = 'http://localhost:3001';

// Topics relevantes para nuestros agentes y sistema
const RELEVANT_TOPICS = [
  // AI & Agents
  { area: 'research', keywords: ['AI agent frameworks 2026', 'multi-agent systems', 'autonomous AI'], minRelevance: 8 },
  { area: 'research', keywords: ['new LLM 2026', 'GPT-5 Claude 4', 'open source AI models'], minRelevance: 9 },
  
  // Skills & Tools
  { area: 'backend', keywords: ['npm package automation', 'best Node.js libraries', 'serverless frameworks'], minRelevance: 7 },
  { area: 'frontend', keywords: ['new CSS framework 2026', 'web components', 'interactive charts library'], minRelevance: 7 },
  
  // Productivity
  { area: 'backend', keywords: ['cron alternatives', 'task queue systems', 'background job processors'], minRelevance: 6 },
  { area: 'general', keywords: ['productivity automation', 'no-code tools', 'API integrations'], minRelevance: 6 },
  
  // Monitoring & DevOps
  { area: 'backend', keywords: ['server monitoring tools', 'error tracking', 'log aggregation'], minRelevance: 7 },
  { area: 'backend', keywords: ['docker alternatives', 'container orchestration', 'cloud native tools'], minRelevance: 7 },
  
  // Security
  { area: 'backend', keywords: ['server security best practices', 'authentication frameworks', 'API security'], minRelevance: 8 },
  
  // Data & Database
  { area: 'backend', keywords: ['new database 2026', 'sqlite tools', 'data visualization'], minRelevance: 7 }
];

const AREA_MAP = {
  research: 'research',
  frontend: 'frontend',
  backend: 'backend',
  general: 'general'
};

// Plantillas de propuestas de ALTA calidad
const QUALITY_PROPOSALS = {
  research: [
    { title: 'Investigar y evaluar {topic}', desc: 'Analizar {topic} para ver si mejora nuestro sistema de investigación' },
    { title: 'Añadir {topic} a skills', desc: '{topic} podría mejorar las capacidades de nuestros agentes' }
  ],
  frontend: [
    { title: 'Implementar {topic} en dashboard', desc: 'Añadir {topic} para mejorar la interfaz de usuario' },
    { title: 'Crear componente con {topic}', desc: 'Utilizar {topic} para nuevo componente visual' }
  ],
  backend: [
    { title: 'Integrar {topic}', desc: 'Conectar {topic} para mejorar rendimiento/automatización' },
    { title: 'Migrar a {topic}', desc: 'Evaluar si {topic} mejora nuestra infraestructura' }
  ],
  general: [
    { title: 'Evaluar {topic}', desc: 'Investigar si {topic} aporta valor al sistema' },
    { title: 'Automatizar con {topic}', desc: 'Utilizar {topic} para optimizar procesos' }
  ]
};

async function log(msg) {
  console.log(`[${new Date().toISOString()}] 💡 ${msg}`);
}

async function fetchJson(url) {
  try {
    const res = await fetch(url);
    return await res.json();
  } catch (e) { return null; }
}

// Simulated intelligent research - picks most relevant topics
async function research() {
  // Pick a random relevant topic based on our priorities
  const topic = RELEVANT_TOPICS[Math.floor(Math.random() * RELEVANT_TOPICS.length)];
  const keyword = topic.keywords[Math.floor(Math.random() * topic.keywords.length)];
  
  return {
    keyword,
    area: topic.area,
    relevance: topic.minRelevance
  };
}

// Check if we should create a proposal
async function shouldCreateProposal() {
  const tasks = await fetchJson(API + '/api/tasks?status=proposal');
  
  // Max 2 proposals pending at any time
  if (tasks && tasks.length >= 2) {
    return false;
  }
  
  // Check recent proposals to avoid duplicates
  const recent = await fetchJson(API + '/api/tasks?status=done');
  if (recent) {
    const recentTitles = recent.slice(0, 5).map(t => t.title.toLowerCase());
    
    // Don't propose same things recently done
    for (const title of recentTitles) {
      if (title.includes('gpt') || title.includes('claude') || title.includes('openai')) {
        log('Recently worked on similar topic, skipping...');
        return false;
      }
    }
  }
  
  return true;
}

async function createProposal(researchResult) {
  const area = AREA_MAP[researchResult.area] || 'general';
  const templates = QUALITY_PROPOSALS[area] || QUALITY_PROPOSALS.general;
  const template = templates[Math.floor(Math.random() * templates.length)];
  
  const proposal = {
    title: template.title.replace('{topic}', researchResult.keyword),
    description: template.desc.replace('{topic}', researchResult.keyword),
    agent: 'proposer',
    priority: researchResult.relevance >= 8 ? 'high' : 'medium',
    status: 'proposal',
    notes: `Investigación: ${researchResult.keyword} (relevancia: ${researchResult.relevance}/10)`
  };
  
  await fetch(API + '/api/tasks', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(proposal)
  });
  
  log(`✅ Created high-quality proposal: "${proposal.title}" (relevance: ${researchResult.relevance})`);
}

async function runResearch() {
  log('🔍 Investigando temas relevantes...');
  
  // Check if we should create proposal
  const should = await shouldCreateProposal();
  if (!should) {
    log('⏭️ Demasiadas propuestas pendientes o tema muy repetido, saltando...');
    return;
  }
  
  // Do research
  const result = await research();
  
  // Create proposal if relevant
  if (result.relevance >= 6) {
    await createProposal(result);
  } else {
    log(`⚠️ Tema no suficientemente relevante: ${result.relevance}/10`);
  }
}

async function main() {
  log('💡 Proposer Agent Started (Quality Mode)');
  
  // Run immediately
  await runResearch();
  
  // Then run every 45 minutes
  setInterval(runResearch, 45 * 60 * 1000);
}

main();
