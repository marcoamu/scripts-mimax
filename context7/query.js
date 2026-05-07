#!/usr/bin/env node
/**
 * Context7 Documentation Query Tool
 * Usage: node query.js <library> [topic]
 * Example: node query.js react hooks
 */

const args = process.argv.slice(2);
if (args.length === 0) {
  console.log('Usage: node query.js <library> [topic]');
  console.log('Example: node query.js react hooks');
  process.exit(1);
}

const library = args[0];
const topic = args[1] || '';

// Context7 MCP HTTP endpoint (running on port 3000)
const CONTEXT7_URL = 'http://localhost:3000';

async function queryContext7() {
  try {
    // First, list available tools
    const toolsResponse = await fetch(`${CONTEXT7_URL}/tools/list`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    
    const tools = await toolsResponse.json();
    console.log('Context7 MCP running!');
    console.log('Available tools:', JSON.stringify(tools, null, 2));
  } catch(e) {
    console.log('Context7 MCP not running on port 3000');
    console.log('Starting Context7 MCP server...');
    
    // Start Context7 MCP in background
    const { spawn } = require('child_process');
    const proc = spawn('npx', ['@upstash/context7-mcp', '--transport', 'http', '--port', '3000'], {
      detached: true,
      stdio: 'ignore'
    });
    proc.unref();
    
    console.log('Started Context7 MCP on port 3000');
  }
}

queryContext7();
