#!/bin/bash
# Memory search helper

echo "=== Búsqueda de memoria ==="
echo ""

# Search in all memory files
grep -r "$1" /root/.openclaw/workspace/memory/*.md 2>/dev/null | head -10

echo ""
echo "=== MEMORY.md ==="
grep -i "$1" /root/.openclaw/workspace/MEMORY.md 2>/dev/null | head -5
