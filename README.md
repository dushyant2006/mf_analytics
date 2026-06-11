Let's go! Day 7 is the final day. Let's start with the README.md since it's quickest.

Run this in CMD:

```
cd C:\Users\ASUS\Documents\mf_analytics
venv\Scripts\activate
```

Then create README:

```
type nul > README.md
code README.md
```

Paste this in VS Code and save:

```markdown
# 🏦 Bluestock Fintech — Mutual Fund Analytics Platform
> Capstone Project | Individual Submission | 7 Days

## 📌 Project Overview
A full-stack Mutual Fund Analytics Platform built using real Indian mutual fund data from AMFI India and mfapi.in. Covers complete data pipeline from raw NAV ingestion to interactive Power BI dashboard.

## 🔧 Tech Stack
Python 3.13 · Pandas · NumPy · Matplotlib · Seaborn · Plotly · SQLite · SciPy · Jupyter · Power BI Desktop · Git + GitHub

## 📁 Project Structure
```
mf_analytics/
├── data/
│   ├── raw/           ← original CSV files
│   ├── processed/     ← cleaned CSVs
│   └── db/            ← bluestock_mf.db (SQLite)
├── notebooks/
│   ├── EDA_Analysis.ipynb
│   ├── Performance_Analytics.ipynb
│   └── Advanced_Analytics.ipynb
├── scripts/
│   └── recommender.py
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── dashboard/
│   └── bluestock_mf_dashboard.pbix
├── reports/
│   └── charts/
├── data_ingestion.py
├── data_cleaning.py
├── db_builder.py
└── README.md
```

## 🚀 How to Run

### 1. Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run ETL Pipeline
```bash
python data_ingestion.py
python data_cleaning.py
python db_builder.py
python live_nav_fetch.py
```

### 3. Run SQL Queries
```bash
python run_queries.py
```

### 4. Open Notebooks
```bash
jupyter notebook
```
Open `notebooks/` folder and run cells in order.

### 5. Fund Recommender
```bash
python scripts/recommender.py
```

### 6. Open Dashboard
Open `dashboard/bluestock_mf_dashboard.pbix` in Power BI Desktop.

## 📊 Datasets
| File | Rows | Description |
|---|---|---|
| 01_fund_master.csv | 40 | 40 AMFI schemes |
| 02_nav_history.csv | 46,000 | Daily NAV 2022–2026 |
| 03_aum_by_fund_house.csv | 90 | Quarterly AUM |
| 04_monthly_sip_inflows.csv | 48 | Monthly SIP data |
| 05_category_inflows.csv | 144 | Category inflows |
| 06_industry_folio_count.csv | 21 | Folio counts |
| 07_scheme_performance.csv | 40 | Risk metrics |
| 08_investor_transactions.csv | 32,778 | Transactions |
| 09_portfolio_holdings.csv | 322 | Stock holdings |
| 10_benchmark_indices.csv | 8,050 | Benchmark data |

## 🎯 Key Findings
- SBI MF leads industry AUM at ₹12.5 lakh crore (106% growth since 2022)
- SIP inflows hit all-time high of ₹31,002 crore in December 2025
- Total MF folios doubled from 13.26 Cr to 26.12 Cr in 4 years
- Small cap funds deliver highest 3Y returns (23%+) but carry highest VaR
- Banking sector dominates equity fund portfolios (₹62,840 Cr combined)

## 👤 Author
Dushyant Sharma | Bluestock Fintech Internship Capstone | 2026
```

