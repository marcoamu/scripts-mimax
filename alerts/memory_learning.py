#!/usr/bin/env python3
"""
Memory Learning System - Usa M2.7 para aprender de interacciones
Analiza patrones y genera insights automáticamente
"""
import psycopg2
import json
from datetime import datetime, timedelta
from collections import defaultdict

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "postgres",
    "database": "knowledge_base"
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def analyze_spending_patterns():
    """Analiza patrones de gasto por día de la semana, hora, categoría"""
    patterns = {
        "by_day_of_week": defaultdict(float),
        "by_category_trend": {},
        "anomalies": [],
        "insights": []
    }
    
    conn = get_db()
    cur = conn.cursor()
    
    # Gastos por día de la semana
    cur.execute("""
        SELECT EXTRACT(DOW FROM fecha) as dow, SUM(ABS(monto)) as total
        FROM transacciones
        WHERE tipo = 'egreso' AND fecha >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY EXTRACT(DOW FROM fecha)
        ORDER BY dow
    """)
    
    days = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    dow_totals = {}
    for row in cur.fetchall():
        dow_totals[int(row[0])] = float(row[1])
    
    # Encontrar día con más gastos
    max_day = max(dow_totals, key=dow_totals.get)
    min_day = min(dow_totals, key=dow_totals.get)
    
    patterns["by_day_of_week"] = {days[k]: v for k, v in dow_totals.items()}
    patterns["insights"].append(f"📊 Días de más gasto: {days[max_day]} (€{dow_totals[max_day]:.0f})")
    patterns["insights"].append(f"📉 Días de menos gasto: {days[min_day]} (€{dow_totals[min_day]:.0f})")
    
    # Tendencia por categoría (último mes vs anterior)
    cur.execute("""
        SELECT categoria, 
               SUM(CASE WHEN fecha >= DATE_TRUNC('month', CURRENT_DATE) THEN ABS(monto) ELSE 0 END) as this_month,
               SUM(CASE WHEN fecha >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') 
                        AND fecha < DATE_TRUNC('month', CURRENT_DATE) THEN ABS(monto) ELSE 0 END) as last_month
        FROM transacciones
        WHERE tipo = 'egreso' AND categoria IS NOT NULL
        GROUP BY categoria
        HAVING SUM(CASE WHEN fecha >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') THEN ABS(monto) ELSE 0 END) > 0
    """)
    
    for row in cur.fetchall():
        cat = row[0]
        this_month = float(row[1])
        last_month = float(row[2])
        change = ((this_month - last_month) / last_month * 100) if last_month > 0 else 0
        
        if abs(change) > 20:  # Cambio significativo
            direction = "📈" if change > 0 else "📉"
            patterns["insights"].append(f"{direction} {cat}: {change:+.1f}% vs mes anterior")
    
    # Top gastos del mes
    cur.execute("""
        SELECT categoria, SUM(ABS(monto)) as total
        FROM transacciones
        WHERE tipo = 'egreso' AND fecha >= DATE_TRUNC('month', CURRENT_DATE)
        GROUP BY categoria
        ORDER BY total DESC
        LIMIT 5
    """)
    
    patterns["insights"].append("💰 Top gastos este mes:")
    for i, row in enumerate(cur.fetchall(), 1):
        patterns["insights"].append(f"   {i}. {row[0]}: €{row[1]:.0f}")
    
    cur.close()
    conn.close()
    
    return patterns

def analyze_income_patterns():
    """Analiza patrones de ingreso"""
    patterns = {
        "total_income": 0,
        "income_sources": [],
        "insights": []
    }
    
    conn = get_db()
    cur = conn.cursor()
    
    # Ingresos totales últimos 3 meses
    cur.execute("""
        SELECT SUM(monto) as total
        FROM transacciones
        WHERE tipo = 'ingreso' AND fecha >= CURRENT_DATE - INTERVAL '90 days'
    """)
    total = cur.fetchone()[0]
    patterns["total_income"] = float(total or 0)
    
    # Fuentes de ingreso
    cur.execute("""
        SELECT categoria, SUM(monto) as total
        FROM transacciones
        WHERE tipo = 'ingreso' AND fecha >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY categoria
        ORDER BY total DESC
    """)
    
    for row in cur.fetchall():
        patterns["income_sources"].append({"source": row[0], "amount": float(row[1])})
    
    patterns["insights"].append(f"💵 Ingresos 3 meses: €{patterns['total_income']:.0f}")
    
    cur.close()
    conn.close()
    
    return patterns

def generate_weekly_summary():
    """Genera resumen semanal completo"""
    spending = analyze_spending_patterns()
    income = analyze_income_patterns()
    
    # Calcular balance
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END), 0) as income,
            COALESCE(SUM(CASE WHEN tipo = 'egreso' THEN ABS(monto) ELSE 0 END), 0) as expense
        FROM transacciones
        WHERE fecha >= CURRENT_DATE - INTERVAL '30 days'
    """)
    row = cur.fetchone()
    monthly_income = float(row[0])
    monthly_expense = float(row[1])
    balance = monthly_income - monthly_expense
    
    cur.close()
    conn.close()
    
    return {
        "date": datetime.now().isoformat(),
        "monthly_balance": balance,
        "spending_analysis": spending,
        "income_analysis": income,
        "recommendations": []
    }

if __name__ == "__main__":
    result = generate_weekly_summary()
    print(json.dumps(result, indent=2, default=str))
