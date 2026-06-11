#!/usr/bin/env python3
"""
recommender.py
==============
Simple fund recommender based on risk appetite.
Usage: python scripts/recommender.py
"""
import pandas as pd
from pathlib import Path

ROOT     = Path(__file__).resolve().parent.parent
PERF     = ROOT / "data" / "processed" / "scheme_performance.csv"
perf_df  = pd.read_csv(PERF)

MAPPING = {
    "1": ("Low",      ["Low"]),
    "2": ("Moderate", ["Moderate", "Moderately High"]),
    "3": ("High",     ["High", "Very High"]),
}

def recommend(risk_appetite: str) -> pd.DataFrame:
    grades   = MAPPING[risk_appetite][1]
    filtered = perf_df[perf_df["risk_grade"].isin(grades)]
    top3     = filtered.nlargest(3, "sharpe_ratio")
    return top3[["scheme_name","fund_house","risk_grade",
                 "sharpe_ratio","return_3yr_pct","expense_ratio_pct"]]

def main():
    print("\n🎯 Mutual Fund Recommender")
    print("="*40)
    print("Select your risk appetite:")
    print("  1 — Low")
    print("  2 — Moderate")
    print("  3 — High")
    choice = input("\nEnter 1, 2 or 3: ").strip()
    if choice not in MAPPING:
        print("Invalid choice.")
        return
    label, _ = MAPPING[choice]
    print(f"\n✅ Top 3 funds for {label} risk appetite:\n")
    print(recommend(choice).to_string(index=False))

if __name__ == "__main__":
    main()