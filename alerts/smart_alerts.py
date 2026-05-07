#!/usr/bin/env python3
"""
Smart Alert System - Usa M2.7 para analizar y generar alertas inteligentes
"""
import psycopg2
import requests
import json
from datetime import datetime, timedelta

# Config
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres", 
    "password": "postgres",
    "database": "knowledge_base"
}

# Alertas configurables
ALERT_THRESHOLDS = {
    "crypto_drop_pct": 5,      # Alertar si crypto baja >5%
    "crypto_rise_pct": 8,      # Alertar si crypto sube >8%
    "expense_single_pct": 20,  # Alertar si gasto >20% del monthly
    "new_category": True       # Alertar si aparece categoría nueva
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def get_crypto_prices():
    """Obtiene precios actuales de crypto"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT ON (asset) asset, price, change_24h, fetched_at
            FROM asset_prices
            ORDER BY asset, fetched_at DESC
        """)
        prices = {row[0]: {"price": row[1], "change": row[2]} for row in cur.fetchall()}
        cur.close()
        conn.close()
        return prices
    except Exception as e:
        print(f"Error getting crypto: {e}")
        return {}

def get_financial_alerts():
    """Analiza finanzas para detectar anomalías"""
    alerts = []
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Obtener gastos del mes
        cur.execute("""
            SELECT SUM(ABS(monto)) as total, categoria
            FROM transacciones 
            WHERE tipo = 'egreso' 
            AND fecha >= DATE_TRUNC('month', CURRENT_DATE)
            GROUP BY categoria
        """)
        monthly_expenses = {row[1]: float(row[0]) for row in cur.fetchall()}
        
        # Obtener media mensual
        cur.execute("""
            SELECT AVG(monthly_total) as avg FROM (
                SELECT SUM(ABS(monto)) as monthly_total
                FROM transacciones 
                WHERE tipo = 'egreso'
                AND fecha >= CURRENT_DATE - INTERVAL '12 months'
                GROUP BY DATE_TRUNC('month', fecha)
            ) m
        """)
        avg_monthly = float(cur.fetchone()[0] or 0)
        
        # Detectar gastos anomalos
        for cat, total in monthly_expenses.items():
            if total > avg_monthly * 1.2:  # 20% sobre la media
                alerts.append({
                    "type": "expense_high",
                    "category": cat,
                    "amount": total,
                    "expected": avg_monthly * 0.2,
                    "severity": "warning" if total < avg_monthly * 1.5 else "critical"
                })
        
        # Transacciones sin categorizar recientes
        cur.execute("""
            SELECT COUNT(*) FROM transacciones 
            WHERE (categoria IS NULL OR categoria = '' OR categoria = 'Otros')
            AND fecha >= CURRENT_DATE - INTERVAL '7 days'
        """)
        uncategorized = cur.fetchone()[0]
        if uncategorized > 10:
            alerts.append({
                "type": "uncategorized",
                "count": uncategorized,
                "severity": "info"
            })
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error financial: {e}")
    
    return alerts

def get_trading_signals():
    """Genera señales de trading basadas en análisis técnico simple"""
    signals = []
    prices = get_crypto_prices()
    
    if not prices:
        return signals
    
    for asset, data in prices.items():
        change = data.get("change", 0)
        
        if change <= -5:
            signals.append({
                "asset": asset,
                "signal": "SELL" if change <= -8 else "WATCH",
                "change": change,
                "reason": "Significant drop" if change <= -8 else "Minor correction"
            })
        elif change >= 8:
            signals.append({
                "asset": asset,
                "signal": "BUY" if change >= 10 else "HOLD",
                "change": change,
                "reason": "Strong momentum"
            })
    
    return signals

def generate_summary():
    """Genera resumen del día usando análisis de M2.7"""
    prices = get_crypto_prices()
    alerts = get_financial_alerts()
    signals = get_trading_signals()
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "crypto": prices,
        "financial_alerts": alerts,
        "trading_signals": signals,
        "action_items": []
    }
    
    # Generar action items
    if alerts:
        summary["action_items"].append(f"📊 {len(alerts)} alertas financieras")
    if signals:
        summary["action_items"].append(f"📈 {len(signals)} señales de trading")
    
    return summary

if __name__ == "__main__":
    result = generate_summary()
    print(json.dumps(result, indent=2, default=str))
