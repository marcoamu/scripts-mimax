#!/usr/bin/env python3
"""
Price Tracker - Multi-asset (Yahoo Finance)
Gold, Oil, Crypto Top 10
"""
import requests
import psycopg2
from datetime import datetime
import time

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'knowledge_base'
}

def init_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS asset_prices (
            id SERIAL PRIMARY KEY,
            asset VARCHAR(20) NOT NULL,
            price FLOAT,
            change_24h FLOAT,
            currency VARCHAR(10),
            source VARCHAR(20),
            fetched_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_price(symbol, name):
    """Get price from Yahoo Finance"""
    try:
        # Handle special symbols
        yahoo_sym = symbol.replace('BTC', 'BTC-USD').replace('ETH', 'ETH-USD')
        if not '-' in yahoo_sym and symbol not in ['GOLD', 'OIL']:
            yahoo_sym += '-USD'
        
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_sym}?interval=1d'
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if 'chart' in data and data['chart']['result']:
                result = data['chart']['result'][0]
                price = result['meta']['regularMarketPrice']
                prev = result['meta']['chartPreviousClose']
                change = ((price - prev) / prev) * 100 if prev else 0
                return {'price': price, 'change': change}
    except Exception as e:
        print(f"Error {name}: {e}")
    return None

def store_price(asset, price, change, currency='USD'):
    if price:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO asset_prices (asset, price, change_24h, currency, source)
            VALUES (%s, %s, %s, %s, %s)
        """, (asset, price, change, currency, 'Yahoo'))
        conn.commit()
        cur.close()
        conn.close()

def main():
    init_db()
    print(f"\n📊 Prices at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)
    
    # Commodities
    commodities = [
        ('GC=F', 'GOLD', 'Gold'),
        ('CL=F', 'OIL', 'Oil'),
    ]
    for symbol, asset, name in commodities:
        result = get_price(symbol, name)
        if result:
            store_price(asset, result['price'], result['change'])
            arrow = "📈" if result['change'] > 0 else "📉" if result['change'] < 0 else "➡️"
            print(f"{name:8} ${result['price']:>8,.2f}  {result['change']:>+6.2f}% {arrow}")
        time.sleep(0.8)
    
    # Crypto
    print("-" * 55)
    cryptos = [
        ('BTC-USD', 'BTC', 'Bitcoin'),
        ('ETH-USD', 'ETH', 'Ethereum'),
        ('SOL-USD', 'SOL', 'Solana'),
        ('BNB-USD', 'BNB', 'BNB'),
        ('XRP-USD', 'XRP', 'XRP'),
        ('DOGE-USD', 'DOGE', 'Dogecoin'),
        ('ADA-USD', 'ADA', 'Cardano'),
        ('AVAX-USD', 'AVAX', 'Avalanche'),
    ]
    for yahoo_sym, asset, name in cryptos:
        result = get_price(yahoo_sym, name)
        if result:
            store_price(asset, result['price'], result['change'])
            arrow = "📈" if result['change'] > 0 else "📉" if result['change'] < 0 else "➡️"
            print(f"{name:10} ${result['price']:>10,.2f}  {result['change']:>+6.2f}% {arrow}")
        time.sleep(0.8)
    
    print("=" * 55)
    print("✅ Saved to database (table: asset_prices)")

if __name__ == "__main__":
    main()

# ==================== PLAYWRIGHT PRICE SCRAPER (FALLBACK) ====================

def get_price_playwright(page, symbol):
    """Get price using Playwright - more reliable for some sources"""
    try:
        # Try Yahoo Finance via browser
        url = f"https://finance.yahoo.com/quote/{symbol}"
        page.goto(url, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(2000)
        
        price_elem = page.query_selector('[data-testid="qsp-price"]')
        if price_elem:
            price = price_elem.inner_text().replace(',', '')
            return float(price)
        
        # Try CoinMarketCap style
        price_elem = page.query_selector('.price')
        if price_elem:
            return float(price_elem.inner_text().replace('$', '').replace(',', ''))
            
    except Exception as e:
        print(f"Playwright error for {symbol}: {e}")
    return None

def scrape_prices_with_playwright():
    """Fallback: scrape prices using Playwright browser"""
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        symbols = {
            'BTC-USD': 'Bitcoin',
            'ETH-USD': 'Ethereum', 
            'GC=F': 'Gold',
            'CL=F': 'Oil'
        }
        
        for symbol, name in symbols.items():
            price = get_price_playwright(page, symbol)
            if price:
                results[name] = price
                print(f"📈 {name}: ${price:,.2f} (Playwright)")
            
        browser.close()
    return results
