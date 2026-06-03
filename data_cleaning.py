#!/usr/bin/env python3
"""
data_cleaning.py
================
Day 2 — Indian Mutual Fund Analytics project.

Cleans three key datasets:
  1. nav_history.csv        — dates, sorting, forward-fill, duplicates, NAV > 0
  2. investor_transactions  — transaction types, amounts, dates, KYC enum
  3. scheme_performance     — numeric validation, expense ratio range check

Writes 10 cleaned CSVs to data/processed/

Usage
-----
    python data_cleaning.py

Author: Dushyant
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
ROOT      = Path(__file__).resolve().parent
RAW       = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "fund_master":           "01_fund_master.csv",
    "nav_history":           "02_nav_history.csv",
    "aum_by_fund_house":     "03_aum_by_fund_house.csv",
    "monthly_sip_inflows":   "04_monthly_sip_inflows.csv",
    "category_inflows":      "05_category_inflows.csv",
    "industry_folio_count":  "06_industry_folio_count.csv",
    "scheme_performance":    "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings":    "09_portfolio_holdings.csv",
    "benchmark_indices":     "10_benchmark_indices.csv",
}


def banner(text: str) -> None:
    print("\n" + "=" * 65)
    print(text)
    print("=" * 65)


# --------------------------------------------------------------------------- #
# Task 1 — Clean nav_history
# --------------------------------------------------------------------------- #
def clean_nav_history(df: pd.DataFrame) -> pd.DataFrame:
    banner("TASK 1 — Cleaning nav_history")

    before = len(df)

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Drop rows where date or nav is null
    df = df.dropna(subset=["date", "nav"])

    # Remove duplicates
    df = df.drop_duplicates(subset=["amfi_code", "date"])

    # Remove non-positive NAVs
    invalid_nav = (df["nav"] <= 0).sum()
    if invalid_nav:
        print(f"  Removed {invalid_nav} rows with NAV <= 0")
    df = df[df["nav"] > 0]

    # Sort
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Forward-fill missing NAVs for each fund (weekends/holidays)
    # Create a full date range per fund and ffill
    all_dates = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    codes = df["amfi_code"].unique()
    filled_frames = []
    for code in codes:
        sub = df[df["amfi_code"] == code].set_index("date")
        sub = sub.reindex(all_dates)
        sub["amfi_code"] = code
        sub["nav"] = sub["nav"].ffill()
        sub = sub.dropna(subset=["nav"])
        sub.index.name = "date"
        sub = sub.reset_index()
        filled_frames.append(sub)

    df = pd.concat(filled_frames, ignore_index=True)
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    after = len(df)
    print(f"  Rows before : {before:,}")
    print(f"  Rows after  : {after:,}  (includes forward-filled weekend/holiday NAVs)")
    print(f"  Date range  : {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"  Unique funds: {df['amfi_code'].nunique()}")
    print("  NAV > 0     : ALL ✓")
    return df


# --------------------------------------------------------------------------- #
# Task 2 — Clean investor_transactions
# --------------------------------------------------------------------------- #
VALID_TXN_TYPES = {"SIP", "Lumpsum", "Redemption", "SWP", "Switch"}
VALID_KYC       = {"Verified", "Pending", "Rejected"}

def clean_investor_transactions(df: pd.DataFrame) -> pd.DataFrame:
    banner("TASK 2 — Cleaning investor_transactions")

    before = len(df)

    # Parse dates
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")

    # Standardise transaction_type — strip whitespace, title-case
    df["transaction_type"] = (
        df["transaction_type"]
        .astype(str)
        .str.strip()
        .str.title()
        .replace({"Sip": "SIP", "Swp": "SWP"})
    )

    # Flag unknown transaction types
    unknown_types = df[~df["transaction_type"].isin(VALID_TXN_TYPES)]["transaction_type"].unique()
    if len(unknown_types):
        print(f"  Unknown transaction types found: {unknown_types}")
    else:
        print("  All transaction types valid ✓")

    # Validate amount > 0
    invalid_amt = (df["amount_inr"] <= 0).sum()
    if invalid_amt:
        print(f"  Removed {invalid_amt} rows with amount <= 0")
    df = df[df["amount_inr"] > 0]

    # Validate KYC status
    invalid_kyc = df[~df["kyc_status"].isin(VALID_KYC)]["kyc_status"].unique()
    if len(invalid_kyc):
        print(f"  Unknown KYC values: {invalid_kyc}")
    else:
        print("  All KYC status values valid ✓")

    # Drop rows with null dates
    df = df.dropna(subset=["transaction_date"])

    # Remove duplicates
    df = df.drop_duplicates()

    after = len(df)
    print(f"  Rows before : {before:,}")
    print(f"  Rows after  : {after:,}")
    print(f"  Transaction types: {sorted(df['transaction_type'].unique())}")
    print(f"  KYC statuses     : {sorted(df['kyc_status'].unique())}")
    return df


# --------------------------------------------------------------------------- #
# Task 3 — Clean scheme_performance
# --------------------------------------------------------------------------- #
NUMERIC_COLS = [
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio",
    "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct",
    "expense_ratio_pct",
]

def clean_scheme_performance(df: pd.DataFrame) -> pd.DataFrame:
    banner("TASK 3 — Cleaning scheme_performance")

    # Force numeric columns
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flag non-numeric / null values
    for col in NUMERIC_COLS:
        n_null = df[col].isna().sum()
        if n_null:
            print(f"  WARNING: {col} has {n_null} null/non-numeric value(s)")

    # Validate expense_ratio range 0.1% – 2.5%
    if "expense_ratio_pct" in df.columns:
        out_of_range = df[
            (df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)
        ]
        if len(out_of_range):
            print(f"\n  WARNING: {len(out_of_range)} scheme(s) with expense_ratio outside 0.1%-2.5%:")
            print(out_of_range[["scheme_name", "expense_ratio_pct"]].to_string())
        else:
            print("  Expense ratio range 0.1%-2.5% : ALL PASS ✓")

    # Flag anomalies — returns > 100% or < -100%
    for col in ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct"]:
        if col in df.columns:
            anomalies = df[(df[col] > 100) | (df[col] < -100)]
            if len(anomalies):
                print(f"  ANOMALY: {col} has {len(anomalies)} extreme value(s)")
            else:
                print(f"  {col}: range OK ✓")

    print(f"\n  Rows: {len(df)} | Columns: {len(df.columns)}")
    return df


# --------------------------------------------------------------------------- #
# Light clean for remaining datasets
# --------------------------------------------------------------------------- #
def light_clean(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates and strip string whitespace for datasets not needing deep cleaning."""
    df = df.drop_duplicates()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()
    return df


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> int:
    banner("LOADING ALL RAW DATASETS")
    frames: dict[str, pd.DataFrame] = {}
    for name, fname in DATASETS.items():
        path = RAW / fname
        if not path.exists():
            print(f"  MISSING: {path}", file=sys.stderr)
            continue
        frames[name] = pd.read_csv(path)
        print(f"  loaded {name:<25} {frames[name].shape}")

    # Deep clean the three key datasets
    frames["nav_history"]           = clean_nav_history(frames["nav_history"])
    frames["investor_transactions"] = clean_investor_transactions(frames["investor_transactions"])
    frames["scheme_performance"]    = clean_scheme_performance(frames["scheme_performance"])

    # Light clean everything else
    banner("LIGHT CLEANING REMAINING DATASETS")
    for name in [
        "fund_master", "aum_by_fund_house", "monthly_sip_inflows",
        "category_inflows", "industry_folio_count",
        "portfolio_holdings", "benchmark_indices",
    ]:
        if name in frames:
            before = len(frames[name])
            frames[name] = light_clean(name, frames[name])
            after  = len(frames[name])
            print(f"  {name:<25} {before:,} -> {after:,} rows")

    # Save all cleaned CSVs
    banner("SAVING CLEANED DATASETS TO data/processed/")
    for name, df in frames.items():
        out = PROCESSED / f"{name}.csv"
        df.to_csv(out, index=False)
        print(f"  saved {name:<25} -> {out.name}  ({len(df):,} rows)")

    banner("DATA CLEANING COMPLETE ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
