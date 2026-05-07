#!/usr/bin/env node
/**
 * 🔍 Research URL - Fetch and analyze a URL using Jina AI
 */

const url = process.argv[2] || process.env.URL;

if (!url) {
  console.log("Usage: node research-url.js <url>");
  process.exit(1);
}

async function research() {
  console.log("📡 Fetching:", url);
  
  try {
    // Use Jina AI to fetch and summarize
    const res = await fetch('https://r.jina.ai/' + url, {
      headers: { 'Accept': 'application/json' }
    });
    
    if (!res.ok) throw new Error('Fetch failed: ' + res.status);
    
    const data = await res.json();
    
    console.log("✅ Success!");
    console.log("---");
    console.log("Title:", data.title || 'N/A');
    console.log("Content:", (data.content || '').substring(0, 1000));
    console.log("---");
    
    return data;
  } catch(e) {
    console.error("❌ Error:", e.message);
    return null;
  }
}

research();
