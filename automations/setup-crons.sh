#!/bin/bash
###############################################################################
# CRON SETUP FOR CONTENT EXTRACTION
###############################################################################

CRON_FILE="/root/.openclaw/workspace/scripts/automations/crontab.txt"
EXTRACTION_SCRIPT="/root/.openclaw/workspace/scripts/automations/content-extractor.sh"

cat > "$CRON_FILE" << 'CRONENTRY'
# Content Extraction Automation - OpenClaw
# Mañana (8:00 AM)
0 8 * * * /root/.openclaw/workspace/scripts/automations/content-extractor.sh all 3 >> /root/.openclaw/workspace/logs/cron-extraction.log 2>&1
# Tarde (8:00 PM)
0 20 * * * /root/.openclaw/workspace/scripts/automations/content-extractor.sh all 3 >> /root/.openclaw/workspace/logs/cron-extraction.log 2>&1
# Cada 4 horas - TikTok
0 */4 * * * /root/.openclaw/workspace/scripts/automations/content-extractor.sh tiktok 5 >> /root/.openclaw/workspace/logs/cron-extraction.log 2>&1
CRONENTRY

chmod +x /root/.openclaw/workspace/scripts/automations/setup-crons.sh
echo "✅ Cron setup script created!"

# Install crons
crontab /root/.openclaw/workspace/scripts/automations/crontab.txt
echo "✅ Crons installed!"

# Show active crons
crontab -l
