#!/bin/bash
# Add newsletter cron

crontab -l > /tmp/cron.txt 2>/dev/null

# Remove existing newsletter crons
grep -v "newsletter" /tmp/cron.txt > /tmp/cron2.txt

# Add new cron - daily at 8 AM
echo "0 8 * * * /root/.openclaw/workspace/scripts/newsletter/generate.sh >> /root/.openclaw/workspace/logs/newsletter.log 2>&1" >> /tmp/cron2.txt

crontab /tmp/cron2.txt
echo "✅ Newsletter cron configured (8:00 AM daily)"
crontab -l | grep newsletter
