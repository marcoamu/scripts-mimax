#!/bin/bash
# Telegram sender script

TOKEN="7653978502:AAEVOBH3Z1tLlzVxEaFUeTWcFZcUyemVZtI"
CHAT_ID="291245843"

send_message() {
  local text="$1"
  curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
    -d chat_id=${CHAT_ID} \
    -d text="$text" \
    -d parse_mode="Markdown"
}

# Test
if [ "$1" = "test" ]; then
  send_message "🧪 Test desde script"
fi
