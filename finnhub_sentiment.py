#!/usr/bin/env python3
"""
Finnhub News Sentiment Analyzer
Fetches news from Finnhub and performs basic sentiment analysis
"""

import os
import re
import json
import requests
from datetime import datetime, timedelta
from collections import defaultdict

# Finnhub API Key
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "d7mt50pr01qngrvpbpp0d7mt50pr01qngrvpbppg")

# Sentiment keywords (expandable)
POSITIVE_WORDS = [
    'surge', 'soar', 'rally', 'gain', 'rise', 'jump', 'boost', 'beat', 'exceed', 
    'growth', 'profit', 'success', 'bullish', 'upgrade', 'outperform', 'buy', 'long',
    'optimism', 'recovery', 'rebound', 'breakthrough', 'innovation', 'record high',
    'strong', 'growth', 'expanding', 'positive', '蓓', '荣', '涨', '突破'  # Chinese chars sometimes
]

NEGATIVE_WORDS = [
    'fall', 'drop', 'plunge', 'crash', 'sink', 'decline', 'loss', 'miss', 'warn',
    'bearish', 'downgrade', 'sell', 'short', 'pessimism', 'recession', 'risk',
    'fear', 'uncertainty', 'volatile', 'crisis', 'war', 'sanction', 'tension',
    '跌', '降', '危机', '战', '制裁'  # Chinese chars sometimes
]

def get_general_news():
    """Fetch general market news from Finnhub"""
    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_API_KEY}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching news: {e}")
    return []

def get_company_news(symbol):
    """Fetch company-specific news from Finnhub"""
    # Convert symbol to FINNHUB format (e.g., AAPL -> US-AAPL)
    finhub_symbol = f"US-{symbol}" if not symbol.startswith('US-') else symbol
    url = f"https://finnhub.io/api/v1/news?category=company&token={FINNHUB_API_KEY}&symbol={finhub_symbol}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching company news: {e}")
    return []

def analyze_sentiment(text):
    """Simple keyword-based sentiment analysis"""
    if not text:
        return 0
    
    text_lower = text.lower()
    positive_count = sum(1 for word in POSITIVE_WORDS if word.lower() in text_lower)
    negative_count = sum(1 for word in NEGATIVE_WORDS if word.lower() in text_lower)
    
    if positive_count + negative_count == 0:
        return 0  # Neutral
    
    # Return score from -1 (very bearish) to 1 (very bullish)
    total = positive_count + negative_count
    return (positive_count - negative_count) / total

def get_news_sentiment(symbol=None, hours=24):
    """
    Get sentiment for a symbol or general market
    Returns dict with sentiment score and news
    """
    if symbol:
        news = get_company_news(symbol)
    else:
        news = get_general_news()
    
    if not news:
        return {"error": "No news found", "sentiment": 0, "news": []}
    
    # Filter news from last N hours
    cutoff = datetime.now() - timedelta(hours=hours)
    recent_news = []
    
    for item in news:
        try:
            # Finnhub uses Unix timestamps
            news_time = datetime.fromtimestamp(item.get('datetime', 0))
            if news_time >= cutoff:
                recent_news.append(item)
        except:
            pass
    
    if not recent_news:
        # If no recent news, use all news (up to 20)
        recent_news = news[:20]
    
    # Analyze sentiment for each headline
    total_sentiment = 0
    analyzed = []
    
    for item in recent_news:
        headline = item.get('headline', '')
        summary = item.get('summary', '')
        text = f"{headline} {summary}"
        
        sentiment = analyze_sentiment(text)
        total_sentiment += sentiment
        
        analyzed.append({
            'headline': headline,
            'sentiment': sentiment,
            'source': item.get('source', ''),
            'url': item.get('url', ''),
            'datetime': item.get('datetime', 0)
        })
    
    avg_sentiment = total_sentiment / len(analyzed) if analyzed else 0
    
    # Classify sentiment
    if avg_sentiment > 0.2:
        label = "BULLISH"
    elif avg_sentiment < -0.2:
        label = "BEARISH"
    else:
        label = "NEUTRAL"
    
    return {
        "symbol": symbol or "MARKET",
        "sentiment": round(avg_sentiment, 3),
        "label": label,
        "news_count": len(analyzed),
        "news": analyzed[:10],  # Top 10 news with sentiment
        "positive_count": sum(1 for n in analyzed if n['sentiment'] > 0.2),
        "negative_count": sum(1 for n in analyzed if n['sentiment'] < -0.2),
    }

def get_multiple_assets_sentiment(assets):
    """Get sentiment for multiple assets"""
    results = {}
    for asset in assets:
        results[asset] = get_news_sentiment(asset, hours=48)
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Get sentiment for specific symbol
        symbol = sys.argv[1]
        result = get_news_sentiment(symbol)
        print(json.dumps(result, indent=2))
    else:
        # Get general market sentiment
        result = get_news_sentiment()
        print(json.dumps(result, indent=2))
