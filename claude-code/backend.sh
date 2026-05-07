#!/bin/bash
# Backend Expert - Claude Code
# Usage: ./backend.sh "tu prompt aquí"

CLAUDE_PROMPT="$1"
cd /root/.openclaw/workspace/mibimax-app/backend

claude -p "Eres un experto en desarrollo Backend con Python, FastAPI, Node.js, PostgreSQL y Docker. Working directory: $(pwd). $CLAUDE_PROMPT" \
  --allowed-tools "Bash,Read,Edit,Write,Glob,Grep" \
  --effort high
