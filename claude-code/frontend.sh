#!/bin/bash
# Frontend Expert - Claude Code
# Usage: ./frontend.sh "tu prompt aquí"

CLAUDE_PROMPT="$1"
cd /root/.openclaw/workspace/mibimax-app/frontend

claude -p "Eres un experto en desarrollo Frontend con Vue.js, React, TypeScript y Tailwind CSS. Working directory: $(pwd). $CLAUDE_PROMPT" \
  --allowed-tools "Bash,Read,Edit,Write,Glob,Grep" \
  --effort high
