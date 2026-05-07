#!/bin/bash
# Daily financial summary - 3AM

cd /root/.openclaw/workspace/data

# Generate summary
SUMMARY=$(node morning-summary.js 2>&1)

# Extract first 1000 chars for Telegram
SUMMARY_SHORT=$(echo "$SUMMARY" | head -c 1500)

# Send to Telegram
TOKEN="7653978502:AAEVOBH3Z1tLlzVxEaFUeTWcFZcUyemVZtI"
CHAT_ID="291245843"

curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -d chat_id=${CHAT_ID} \
  -d text="$(echo -e '📊 *RESUMEN FINANCIERO*'"$SUMMARY_SHORT")" \
  -d parse_mode="Markdown" > /tmp/telegram-cron.log 2>&1

echo "$(date): Sent" >> /tmp/telegram-cron.log
