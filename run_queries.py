#!/usr/bin/env python3
"""
run_queries.py
==============
Day 2 — Runs all 10 analytical SQL queries against bluestock_mf.db
and prints results in a readable format.

Usage:  python run_queries.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

ROOT    = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "db" / "bluestock_mf.db"

QUERIES = {
    "Q1 — Top 5 funds by AUM": """
        SELECT f.scheme_name, f.fund_house, f.category, p.aum_crore
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        ORDER BY p.aum_crore DESC LIMIT 5
    """,
    "Q2 — Avg monthly NAV (SBI Bluechip Regular)": """
        SELECT d.year, d.month_name, ROUND(AVG(n.nav),4) AS avg_nav
        FROM fact_nav n
        JOIN dim_date d ON n.date_id = d.date_id
        WHERE n.amfi_code = 119551
        GROUP BY d.year, d.month ORDER BY d.year, d.month LIMIT 12
    """,
    "Q3 — SIP YoY growth": """
        SELECT month, sip_inflow_crore, ROUND(yoy_growth_pct,2) AS yoy_pct
        FROM fact_sip WHERE yoy_growth_pct IS NOT NULL
        ORDER BY month LIMIT 10
    """,
    "Q4 — Transactions by state (top 10)": """
        SELECT state, COUNT(*) AS txns,
               ROUND(SUM(amount_inr)/1e7,2) AS total_crore
        FROM fact_transactions
        GROUP BY state ORDER BY txns DESC LIMIT 10
    """,
    "Q5 — Funds with expense ratio < 1%": """
        SELECT scheme_name, fund_house, plan, expense_ratio_pct
        FROM dim_fund WHERE expense_ratio_pct < 1.0
        ORDER BY expense_ratio_pct LIMIT 10
    """,
    "Q6 — Top 5 funds by 3Y return": """
        SELECT f.scheme_name, p.return_3yr_pct, p.benchmark_3yr_pct,
               ROUND(p.return_3yr_pct - p.benchmark_3yr_pct,2) AS excess
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
        ORDER BY p.return_3yr_pct DESC LIMIT 5
    """,
    "Q7 — Transactions by type and city tier": """
        SELECT transaction_type, city_tier, COUNT(*) AS count,
               ROUND(SUM(amount_inr)/1e7,2) AS total_crore
        FROM fact_transactions
        GROUP BY transaction_type, city_tier
        ORDER BY transaction_type, city_tier
    """,
    "Q8 — AUM growth by fund house": """
        SELECT fund_house,
               MIN(aum_crore) AS earliest,
               MAX(aum_crore) AS latest,
               ROUND((MAX(aum_crore)-MIN(aum_crore))*100.0/MIN(aum_crore),1) AS growth_pct
        FROM fact_aum GROUP BY fund_house ORDER BY growth_pct DESC
    """,
    "Q9 — Top sectors by portfolio weight": """
        SELECT sector, COUNT(DISTINCT amfi_code) AS num_funds,
               ROUND(AVG(weight_pct),2) AS avg_weight,
               ROUND(SUM(market_value_cr),0) AS total_mkt_val_cr
        FROM fact_portfolio_holdings
        GROUP BY sector ORDER BY total_mkt_val_cr DESC
    """,
    "Q10 — Age group vs avg SIP amount": """
        SELECT age_group, transaction_type, COUNT(*) AS count,
               ROUND(AVG(amount_inr),0) AS avg_inr
        FROM fact_transactions
        GROUP BY age_group, transaction_type
        ORDER BY age_group, transaction_type
    """,
}

def main():
    con = sqlite3.connect(DB_PATH)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 120)
    pd.set_option("display.max_colwidth", 40)

    for title, sql in QUERIES.items():
        print(f"\n{'='*65}")
        print(f"  {title}")
        print("="*65)
        df = pd.read_sql_query(sql.strip(), con)
        print(df.to_string(index=False))

    con.close()
    print("\n✓ All 10 queries executed successfully.")

if __name__ == "__main__":
    main()
