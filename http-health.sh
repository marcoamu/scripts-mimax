#!/bin/bash
# Health check for port 4000

if ! ss -tlnp | grep -q ":4000 "; then
    cd /root/.openclaw/workspace/ai-media-app/public
    python3 -m http.server 4000 >> /tmp/http4000.log 2>&1 &
    echo "$(date): Restarted port 4000" >> /tmp/http-health.log
fi
