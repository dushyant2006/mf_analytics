#!/usr/bin/env python3
"""
db_builder.py
=============
Day 2 — Indian Mutual Fund Analytics project.
Builds SQLite star schema and loads all cleaned datasets.

Usage:  python db_builder.py
"""

from __future__ import annotations
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT      = Path(__file__).resolve().parent
PROCESSED = ROOT / "data" / "processed"
DB_DIR    = ROOT / "data" / "db"
SQL_DIR   = ROOT / "sql"
DB_DIR.mkdir(parents=True, exist_ok=True)
SQL_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH   = DB_DIR / "bluestock_mf.db"


def banner(text: str) -> None:
    print("\n" + "=" * 65)
    print(text)
    print("=" * 65)


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code           INTEGER PRIMARY KEY,
    fund_house          TEXT,
    scheme_name         TEXT,
    category            TEXT,
    sub_category        TEXT,
    plan                TEXT,
    launch_date         TEXT,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id     TEXT PRIMARY KEY,
    year        INTEGER,
    quarter     INTEGER,
    month       INTEGER,
    month_name  TEXT,
    week        INTEGER,
    day_of_week INTEGER,
    is_weekend  INTEGER
);

CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code   INTEGER,
    date_id     TEXT,
    nav         REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_id)   REFERENCES dim_date(date_id)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    txn_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT,
    transaction_date    TEXT,
    amfi_code           INTEGER,
    transaction_type    TEXT,
    amount_inr          REAL,
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    perf_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER,
    scheme_name         TEXT,
    fund_house          TEXT,
    category            TEXT,
    plan                TEXT,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           INTEGER,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id         TEXT,
    fund_house      TEXT,
    aum_lakh_crore  REAL,
    aum_crore       INTEGER,
    num_schemes     INTEGER
);

CREATE TABLE IF NOT EXISTS fact_sip (
    sip_id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    month                     TEXT,
    sip_inflow_crore          INTEGER,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh     REAL,
    sip_aum_lakh_crore        REAL,
    yoy_growth_pct            REAL
);

CREATE TABLE IF NOT EXISTS fact_category_inflows (
    cat_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    month            TEXT,
    category         TEXT,
    net_inflow_crore REAL
);

CREATE TABLE IF NOT EXISTS fact_folio_count (
    folio_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    month               TEXT,
    total_folios_crore  REAL,
    equity_folios_crore REAL,
    debt_folios_crore   REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);

CREATE TABLE IF NOT EXISTS fact_portfolio_holdings (
    holding_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code         INTEGER,
    stock_symbol      TEXT,
    stock_name        TEXT,
    sector            TEXT,
    weight_pct        REAL,
    market_value_cr   REAL,
    current_price_inr REAL,
    portfolio_date    TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_benchmark (
    bench_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    date_id     TEXT,
    index_name  TEXT,
    close_value REAL
);
"""


def build_dim_date(nav_df: pd.DataFrame) -> pd.DataFrame:
    dates = pd.to_datetime(nav_df["date"].unique())
    dim = pd.DataFrame({
        "date_id":     dates.strftime("%Y-%m-%d"),
        "year":        dates.year,
        "quarter":     dates.quarter,
        "month":       dates.month,
        "month_name":  dates.strftime("%B"),
        "week":        dates.isocalendar().week.values,
        "day_of_week": dates.dayofweek,
        "is_weekend":  (dates.dayofweek >= 5).astype(int),
    })
    return dim.drop_duplicates(subset=["date_id"])


def load_table(df: pd.DataFrame, table: str, con: sqlite3.Connection) -> None:
    df.to_sql(table, con=con, if_exists="replace", index=False)
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table:<30} {count:>8,} rows loaded")


def main() -> int:
    banner("BUILDING SQLite DATABASE")
    print(f"  DB path: {DB_PATH}")

    # Write schema.sql
    schema_path = SQL_DIR / "schema.sql"
    schema_path.write_text(SCHEMA_SQL)
    print(f"  schema.sql written -> {schema_path}")

    # Create DB and tables
    con = sqlite3.connect(DB_PATH)
    for stmt in SCHEMA_SQL.split(";"):
        stmt = stmt.strip()
        if stmt.upper().startswith("CREATE"):
            con.execute(stmt)
    con.commit()
    print("  All tables created ✓")

    # Load CSVs
    banner("LOADING CLEANED DATA INTO SQLITE")

    nav_df   = pd.read_csv(PROCESSED / "nav_history.csv",           parse_dates=["date"])
    fund_df  = pd.read_csv(PROCESSED / "fund_master.csv")
    txn_df   = pd.read_csv(PROCESSED / "investor_transactions.csv")
    perf_df  = pd.read_csv(PROCESSED / "scheme_performance.csv")
    aum_df   = pd.read_csv(PROCESSED / "aum_by_fund_house.csv")
    sip_df   = pd.read_csv(PROCESSED / "monthly_sip_inflows.csv")
    cat_df   = pd.read_csv(PROCESSED / "category_inflows.csv")
    folio_df = pd.read_csv(PROCESSED / "industry_folio_count.csv")
    hold_df  = pd.read_csv(PROCESSED / "portfolio_holdings.csv")
    bench_df = pd.read_csv(PROCESSED / "benchmark_indices.csv")

    # Prepare date_id columns
    nav_load          = nav_df.copy()
    nav_load["date_id"] = pd.to_datetime(nav_load["date"]).dt.strftime("%Y-%m-%d")
    nav_load          = nav_load[["amfi_code","date_id","nav"]]

    aum_load          = aum_df.copy()
    aum_load["date_id"] = pd.to_datetime(aum_load["date"]).dt.strftime("%Y-%m-%d")
    aum_load          = aum_load.drop(columns=["date"])

    bench_load          = bench_df.copy()
    bench_load["date_id"] = pd.to_datetime(bench_load["date"]).dt.strftime("%Y-%m-%d")
    bench_load          = bench_load.drop(columns=["date"])

    dim_date = build_dim_date(nav_df)

    load_table(fund_df,    "dim_fund",                con)
    load_table(dim_date,   "dim_date",                con)
    load_table(nav_load,   "fact_nav",                con)
    load_table(txn_df,     "fact_transactions",       con)
    load_table(perf_df,    "fact_performance",        con)
    load_table(aum_load,   "fact_aum",                con)
    load_table(sip_df,     "fact_sip",                con)
    load_table(cat_df,     "fact_category_inflows",   con)
    load_table(folio_df,   "fact_folio_count",        con)
    load_table(hold_df,    "fact_portfolio_holdings", con)
    load_table(bench_load, "fact_benchmark",          con)

    con.commit()
    con.close()

    banner("DATABASE BUILD COMPLETE ✓")
    print(f"  File : {DB_PATH}")
    print(f"  Size : {DB_PATH.stat().st_size / 1024 / 1024:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
