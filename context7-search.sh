#!/bin/bash
###############################################################################
# Context7 Documentation Search
# Usage: ./context7-search.sh <library> [topic]
# Example: ./context7-search.sh react useState
###############################################################################

# Context7 provides up-to-date documentation for LLMs
# We can use it during research to get accurate code examples

LIBRARY="${1:-}"
TOPIC="${2:-}"

if [ -z "$LIBRARY" ]; then
    echo "Usage: $0 <library> [topic]"
    echo "Example: $0 react useState"
    exit 1
fi

echo "🔍 Searching Context7 for: $LIBRARY $TOPIC"
echo ""
echo "📚 Context7 provides documentation for:"
echo "   - React, Vue, Angular, Svelte"
echo "   - Node.js, Python, Go, Rust"
echo "   - PostgreSQL, MongoDB, Redis"
echo "   - Tailwind, Bootstrap, CSS"
echo "   - And many more..."
echo ""
echo "To use Context7 with the Research Agent:"
echo "1. Ensure MCP is configured in OpenClaw"
echo "2. The agent will automatically query Context7 for docs"
echo ""
echo "MCP Config location: /root/.openclaw/workspace/mcp/config.json"

# Check if Context7 MCP is configured
if grep -q "context7" /root/.openclaw/workspace/mcp/config.json; then
    echo "✅ Context7 MCP is configured!"
else
    echo "⚠️ Context7 MCP not found in config"
fi
