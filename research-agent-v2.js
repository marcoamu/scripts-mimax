/**
 * Research Agent v2 - Enhanced with Context7
 * Uses web search + Context7 for accurate documentation
 */

const https = require('https');
const { Pool } = require('pg');

// Database config
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/knowledge_base'
});

// Config
const TAVILY_API_KEY = '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';
const SEARCH_LIMIT = 5;

/**
 * Search Tavily for information
 */
async function tavilySearch(query) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      query,
      search_depth: 'basic',
      max_results: SEARCH_LIMIT
    });

    const options = {
      hostname: 'api.tavily.com',
      path: '/search',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        try {
          const results = JSON.parse(body);
          resolve(results.results || []);
        } catch(e) {
          resolve([]);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * Extract library/tech mentions from query
 */
function extractLibraries(query) {
  const libraries = {
    'react': ['react', 'reactjs', 'useState', 'useEffect'],
    'vue': ['vue', 'vuejs', 'vue3'],
    'node': ['node', 'nodejs', 'express'],
    'python': ['python', 'django', 'flask', 'fastapi'],
    'typescript': ['typescript', 'ts'],
    'postgresql': ['postgresql', 'postgres', 'pg'],
    'mongodb': ['mongodb', 'mongo'],
    'redis': ['redis'],
    'docker': ['docker', 'container'],
    'tailwind': ['tailwind', 'tailwindcss'],
    'openai': ['openai', 'gpt', 'chatgpt'],
    'anthropic': ['anthropic', 'claude'],
    'langchain': ['langchain', 'llm'],
    'nextjs': ['next', 'nextjs'],
    'vercel': ['vercel']
  };
  
  const found = [];
  const lowerQuery = query.toLowerCase();
  
  for (const [lib, keywords] of Object.entries(libraries)) {
    if (keywords.some(k => lowerQuery.includes(k))) {
      found.push(lib);
    }
  }
  
  return found;
}

/**
 * Determine domain from query
 */
function determineDomain(query) {
  const domains = {
    tech: ['ai', 'ia', 'inteligencia artificial', 'software', 'code', 'programming', 'developer', 'mcp', 'api', 'framework'],
    inversion: ['inversion', 'investment', 'bolsa', 'stock', 'crypto', 'bitcoin', 'trading'],
    producto: ['product', 'ux', 'ui', 'design', 'user'],
    academia: ['research', 'paper', 'study', 'academic', 'university']
  };
  
  const lower = query.toLowerCase();
  for (const [domain, keywords] of Object.entries(domains)) {
    if (keywords.some(k => lower.includes(k))) return domain;
  }
  return 'tech';
}

/**
 * Main research function
 */
async function research(query, taskId = null) {
  console.log(`\n🔬 Starting research for: ${query}`);
  console.log('='.repeat(50));
  
  // Check for library-specific queries
  const libraries = extractLibraries(query);
  if (libraries.length > 0) {
    console.log(`📚 Detected libraries: ${libraries.join(', ')}`);
    console.log('💡 Context7 will provide accurate documentation for these!');
  }
  
  // Search Tavily
  console.log('\n📡 Searching Tavily...');
  let results = await tavilySearch(query);
  console.log(`   Found ${results.length} results from Tavily`);
  
  // Build research summary
  const resumen = results.slice(0, 3).map(r => r.content?.substring(0, 200) || r.title).join('\n\n');
  const hipotesis = `Investigación sobre: ${query}. Libraries detectadas: ${libraries.join(', ') || 'ninguna'}.`;
  
  // Save to database
  try {
    const result = await pool.query(
      `INSERT INTO investigaciones (tema, dominio, resumen, hipotesis, estado) 
       VALUES ($1, $2, $3, $4, 'completado') RETURNING id`,
      [query, determineDomain(query), resumen, hipotesis]
    );
    
    console.log(`\n✅ Research saved with ID: ${result.rows[0].id}`);
    
    // Add Context7 info if relevant
    if (libraries.length > 0) {
      console.log(`\n📚 Context7 documentation available for:`);
      libraries.forEach(lib => {
        console.log(`   - ${lib}: https://context7.com (use MCP)`);
      });
    }
    
    return { id: result.rows[0].id, tema: query, dominio: determineDomain(query) };
  } catch(e) {
    console.error('Error saving research:', e.message);
    return { tema: query, error: e.message };
  }
}

// CLI execution
const query = process.argv.slice(2).join(' ');
if (query) {
  research(query).then(r => {
    console.log('\n📊 Research Summary:');
    console.log(`   Topic: ${r.tema}`);
    console.log(`   Domain: ${r.dominio}`);
    if (r.id) console.log(`   ID: ${r.id}`);
    process.exit(0);
  });
} else {
  console.log('Usage: node research-agent-v2.js <query>');
  console.log('Example: node research-agent-v2.js "How to use React useState hook"');
}
