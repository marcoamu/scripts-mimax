#!/usr/bin/env python3
"""BTC Price Scraper - Multiple sources"""
import requests

def get_btc_price():
    # Try Yahoo Finance API first
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/BTC-USD"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data["chart"]["result"][0]["meta"]["regularMarketPrice"], "Yahoo Finance"
    except:
        pass
    
    # Fallback to CoinGecko
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin", "vs_currencies": "usd"}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data["bitcoin"]["usd"], "CoinGecko"
    except:
        pass
    
    return None, None

if __name__ == "__main__":
    price, source = get_btc_price()
    if price:
        print(f"✅ BTC Price: ${price:,.2f} ({source})")
    else:
        print("❌ Error getting BTC price")
