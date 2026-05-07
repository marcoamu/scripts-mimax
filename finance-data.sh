#!/bin/bash
# Finance data fetcher using Yahoo Finance (free, no API key)

echo "=== 📈 Bolsa & Crypto - $(date '+%d/%m/%Y %H:%M') ==="
echo ""

# Crypto
echo "💰 CRYPTO:"
for pair in BTC-USD ETH-USD SOL-USD; do
    price=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/$pair" -H "User-Agent: Mozilla" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['chart']['result'][0]['meta']['regularMarketPrice'])" 2>/dev/null)
    echo "  $pair: \$$price"
done

echo ""
echo "📊 ÍNDICES:"
for idx in "^GSPC" "^IXIC" "^DJI"; do
    name=$(echo $idx | sed 's/\^GSPC/S&P 500/; s/\^IXIC/NASDAQ/; s/\^DJI/Dow Jones/')
    price=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/$idx" -H "User-Agent: Mozilla" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['chart']['result'][0]['meta']['regularMarketPrice'])" 2>/dev/null)
    echo "  $name: $price"
done

echo ""
echo "🎯 ACCIONES TOP:"
for stock in NVDA AAPL MSFT GOOGL; do
    price=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/$stock" -H "User-Agent: Mozilla" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['chart']['result'][0]['meta']['regularMarketPrice'])" 2>/dev/null)
    echo "  $stock: \$$price"
done
