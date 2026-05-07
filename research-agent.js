#!/usr/bin/env node
/**
 * 🔍 Research Agent - Smart Multi-Source Research
 * Uses: Tavily (limited) + DDG + Jina (unlimited)
 */

const TAVILY_KEY = "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";

// Use Tavily only for 1 query per research to save quota
async function searchTavily(query) {
  try {
    const res = await fetch("https://api.tavily.com/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        api_key: TAVILY_KEY,
        query: query,
        max_results: 5,
        include_answer: true
      })
    });
    const data = await res.json();
    console.log("📡 Tavily: OK");
    return data.results || [];
  } catch(e) {
    console.log("📡 Tavily: FALLBACK");
    return [];
  }
}

// DDG for web search (unlimited)
async function searchDDG(query) {
  try {
    const url = `https://lite.duckduckgo.com/lite/?q=${encodeURIComponent(query).replace(/%20/g, '+')}`;
    const res = await fetch(url);
    const text = await res.text();
    // Parse basic results
    const results = [];
    const regex = /<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)<\/a>.*?result__snippet[^>]*>([^<]+)/g;
    let match;
    while ((match = regex.exec(text)) && results.length < 5) {
      results.push({
        url: match[1].replace(/^\/\//, 'https://'),
        title: match[2],
        content: match[3].replace(/<[^>]+>/g, '')
      });
    }
    console.log("🔍 DDG: OK");
    return results;
  } catch(e) {
    console.log("🔍 DDG: ERROR");
    return [];
  }
}

// Jina for content extraction (unlimited)
async function fetchContent(url) {
  try {
    const res = await fetch(`https://r.jina.ai/http://${url.replace(/^https?:\/\//, '')}`);
    const text = await res.text();
    return text.substring(0, 8000); // Limit content
  } catch(e) {
    return "";
  }
}

// Main research function
async function research(query) {
  console.log(`\n🎯 Investigando: ${query}`);
  console.log("=".repeat(50));
  
  // Step 1: Use Tavily for initial results (limited)
  console.log("\n1️⃣ Tavily (principal)...");
  const tavilyResults = await searchTavily(query);
  
  // Step 2: Use DDG to supplement
  console.log("2️⃣ DDG (suplemento)...");
  const ddgResults = await searchDDG(query);
  
  // Combine results (avoid duplicates by URL domain)
  const allResults = [...tavilyResults];
  ddgResults.forEach(r => {
    if (!allResults.some(existing => existing.url.includes(new URL(r.url).hostname))) {
      allResults.push(r);
    }
  });
  
  console.log(`\n📊 Total fuentes encontradas: ${allResults.length}`);
  
  // Fetch content from top 3 sources using Jina
  console.log("\n3️⃣ Extrayendo contenido con Jina...");
  const sources = [];
  for (const r of allResults.slice(0, 3)) {
    const content = await fetchContent(r.url);
    if (content) {
      sources.push({
        url: r.url,
        title: r.title || r.content?.substring(0, 50),
        content: content.substring(0, 3000),
        autoridad_score: r.url.includes('anthropic') || r.url.includes('google') ? 0.95 : 
                        r.url.includes('microsoft') || r.url.includes('a16z') ? 0.90 : 0.80
      });
      console.log(`   ✅ ${new URL(r.url).hostname}`);
    }
  }
  
  return sources;
}

// CLI
const query = process.argv.slice(2).join(" ");
if (!query) {
  console.log("Uso: node research-agent.js 'tu pregunta de investigación'");
  process.exit(1);
}

research(query).then(sources => {
  console.log("\n✅ Investigación completada");
  console.log("\nFuentes:");
  sources.forEach((s, i) => console.log(`${i+1}. ${s.title} (${s.url})`));
});
