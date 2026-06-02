#!/usr/bin/env python3
"""
live_nav_fetch.py
=================
Day 1 — Indian Mutual Fund Analytics project.

Fetches live NAV data from mfapi.in for 6 key schemes:
  - HDFC Top 100 Direct     (125497)
  - SBI Bluechip            (119551)
  - ICICI Bluechip          (120503)
  - Nippon Large Cap        (118632)
  - Axis Bluechip           (119092)
  - Kotak Bluechip          (120841)

Saves each scheme's NAV history as a CSV in data/raw/live_nav/

Usage
-----
    python live_nav_fetch.py

Requires: requests, pandas
"""

import time
from pathlib import Path

import requests
import pandas as pd

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
ROOT    = Path(__file__).resolve().parent
OUT_DIR = ROOT / "data" / "raw" / "live_nav"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://api.mfapi.in/mf/{code}"

SCHEMES = {
    125497: "HDFC Top 100 Direct",
    119551: "SBI Bluechip Regular",
    120503: "ICICI Bluechip Regular",
    118632: "Nippon Large Cap Regular",
    119092: "Axis Bluechip Regular",
    120841: "Kotak Bluechip Regular",
}

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def fetch_nav(code: int) -> dict | None:
    """Call mfapi.in and return the parsed JSON or None on failure."""
    url = BASE_URL.format(code=code)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"  ERROR fetching {code}: {e}")
        return None


def parse_to_dataframe(data: dict, code: int, name: str) -> pd.DataFrame:
    """Convert mfapi JSON response to a tidy DataFrame."""
    meta = data.get("meta", {})
    records = data.get("data", [])

    df = pd.DataFrame(records)                        # columns: date, nav
    df["amfi_code"]   = code
    df["scheme_name"] = name
    df["fund_house"]  = meta.get("fund_house", "")
    df["scheme_type"] = meta.get("scheme_type", "")
    df["scheme_category"] = meta.get("scheme_category", "")

    # Clean types
    df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df = df.sort_values("date").reset_index(drop=True)

    return df[["amfi_code", "scheme_name", "fund_house",
               "scheme_type", "scheme_category", "date", "nav"]]


def print_summary(df: pd.DataFrame, name: str) -> None:
    """Print a short summary of fetched NAV data."""
    latest = df.iloc[-1]
    print(f"  rows      : {len(df):,}")
    print(f"  date range: {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"  latest NAV: {latest['nav']:.4f}  (as of {latest['date'].date()})")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    print("=" * 60)
    print("Live NAV Fetch — mfapi.in")
    print("=" * 60)

    all_frames = []

    for code, name in SCHEMES.items():
        print(f"\nFetching [{code}] {name} ...")
        data = fetch_nav(code)

        if data is None:
            print("  Skipped (fetch failed).")
            continue

        df = parse_to_dataframe(data, code, name)
        print_summary(df, name)

        # Save individual CSV
        fname = OUT_DIR / f"live_nav_{code}.csv"
        df.to_csv(fname, index=False)
        print(f"  Saved -> {fname.relative_to(ROOT)}")

        all_frames.append(df)
        time.sleep(0.5)   # be polite to the free API

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined_path = OUT_DIR / "live_nav_all_schemes.csv"
        combined.to_csv(combined_path, index=False)
        print(f"\nCombined file saved -> {combined_path.relative_to(ROOT)}")
        print(f"Total rows fetched  : {len(combined):,}")

    print("\n" + "=" * 60)
    print("Done.")
    print("=" * 60)


if __name__ == "__main__":
    main()
