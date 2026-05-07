#!/bin/bash

# Port 4000
if ! ss -tlnp | grep -q ":4000 "; then
    cd /root/.openclaw/workspace/ai-media-app/public
    python3 -m http.server 4000 >> /tmp/http4000.log 2>&1 &
    echo "$(date): Restarted port 4000" >> /tmp/health.log
fi

# Port 3001
if ! ss -tlnp | grep -q ":3001 "; then
    cd /root/.openclaw/workspace/ai-media-app
    node api/server.js >> /tmp/api.log 2>&1 &
    echo "$(date): Restarted port 3001" >> /tmp/health.log
fi

# Agent Runner
if ! pgrep -f "agent-runner-v2" > /dev/null; then
    cd /root/.openclaw/workspace/scripts
    node agent-runner-v2.js >> /tmp/agent.log 2>&1 &
    echo "$(date): Restarted agent-runner" >> /tmp/health.log
fi

# Proposer
if ! pgrep -f "proposer-agent-v3" > /dev/null; then
    cd /root/.openclaw/workspace/scripts
    node proposer-agent-v3.js >> /tmp/proposer.log 2>&1 &
    echo "$(date): Restarted proposer" >> /tmp/health.log
fi
