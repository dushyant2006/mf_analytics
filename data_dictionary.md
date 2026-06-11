# Data Dictionary
## Bluestock Fintech Capstone — Mutual Fund Analytics Platform
_Last updated: Day 2_

---

## 1. dim_fund
**Source:** `01_fund_master.csv`
**Description:** Dimension table containing master information for all 40 AMFI schemes.

| Column | Type | Description |
|---|---|---|
| amfi_code | INTEGER (PK) | Unique AMFI scheme code assigned per plan (Regular vs Direct get different codes) |
| fund_house | TEXT | Name of the Asset Management Company (AMC) e.g. SBI Mutual Fund |
| scheme_name | TEXT | Full official scheme name including plan and option |
| category | TEXT | Broad category: Equity or Debt |
| sub_category | TEXT | SEBI sub-category e.g. Large Cap, Small Cap, Gilt, Liquid |
| plan | TEXT | Regular or Direct plan |
| launch_date | TEXT | Date the scheme was launched (YYYY-MM-DD) |
| benchmark | TEXT | Index used to benchmark the fund e.g. NIFTY 100 TRI |
| expense_ratio_pct | REAL | Annual expense ratio as % of AUM. Range: 0.1% – 2.5% |
| exit_load_pct | REAL | Exit load charged on redemption before lock-in period |
| min_sip_amount | INTEGER | Minimum SIP instalment amount in INR |
| min_lumpsum_amount | INTEGER | Minimum one-time investment amount in INR |
| fund_manager | TEXT | Name of the fund manager responsible for the scheme |
| risk_category | TEXT | SEBI risk grade: Low / Moderate / Moderately High / High / Very High |
| sebi_category_code | TEXT | SEBI classification code e.g. EC01 (Equity Large Cap), DC02 (Debt Gilt) |

---

## 2. dim_date
**Source:** Derived from `02_nav_history.csv` date range
**Description:** Date dimension table for time-based analysis.

| Column | Type | Description |
|---|---|---|
| date_id | TEXT (PK) | Date in YYYY-MM-DD format (primary key) |
| year | INTEGER | Calendar year e.g. 2024 |
| quarter | INTEGER | Quarter number 1–4 |
| month | INTEGER | Month number 1–12 |
| month_name | TEXT | Full month name e.g. January |
| week | INTEGER | ISO week number of the year |
| day_of_week | INTEGER | 0=Monday, 6=Sunday |
| is_weekend | INTEGER | 1 if Saturday or Sunday, else 0 |

---

## 3. fact_nav
**Source:** `02_nav_history.csv` (cleaned + forward-filled)
**Description:** Daily NAV values for all 40 schemes. Forward-filled for weekends and market holidays.

| Column | Type | Description |
|---|---|---|
| nav_id | INTEGER (PK) | Auto-increment surrogate key |
| amfi_code | INTEGER (FK) | References dim_fund.amfi_code |
| date_id | TEXT (FK) | References dim_date.date_id |
| nav | REAL | Net Asset Value in INR per unit. Always > 0 |

**Notes:**
- Original 46,000 rows expanded to 64,320 after forward-filling weekends/holidays
- NAV anchored to real mfapi.in values e.g. HDFC Top 100 Direct (125497)

---

## 4. fact_transactions
**Source:** `08_investor_transactions.csv`
**Description:** Individual investor transactions including SIP, Lumpsum, and Redemptions.

| Column | Type | Description |
|---|---|---|
| txn_id | INTEGER (PK) | Auto-increment surrogate key |
| investor_id | TEXT | Unique investor identifier e.g. INV003054 |
| transaction_date | TEXT | Date of transaction (YYYY-MM-DD) |
| amfi_code | INTEGER (FK) | References dim_fund.amfi_code |
| transaction_type | TEXT | SIP / Lumpsum / Redemption |
| amount_inr | REAL | Transaction amount in INR. Always > 0 |
| state | TEXT | Indian state of investor e.g. Maharashtra |
| city | TEXT | City of investor |
| city_tier | TEXT | T30 (Top 30 cities) or B30 (Beyond Top 30) |
| age_group | TEXT | Age band: 18-25 / 26-35 / 36-45 / 46-55 / 56+ |
| gender | TEXT | Male or Female |
| annual_income_lakh | REAL | Annual income in lakh INR |
| payment_mode | TEXT | UPI / Net Banking / Mandate / Cheque |
| kyc_status | TEXT | Verified / Pending / Rejected |

---

## 5. fact_performance
**Source:** `07_scheme_performance.csv`
**Description:** Risk and return metrics for all 40 schemes.

| Column | Type | Description |
|---|---|---|
| perf_id | INTEGER (PK) | Auto-increment surrogate key |
| amfi_code | INTEGER (FK) | References dim_fund.amfi_code |
| scheme_name | TEXT | Full scheme name |
| fund_house | TEXT | AMC name |
| category | TEXT | Equity or Debt |
| plan | TEXT | Regular or Direct |
| return_1yr_pct | REAL | 1-year CAGR return in % |
| return_3yr_pct | REAL | 3-year CAGR return in % |
| return_5yr_pct | REAL | 5-year CAGR return in % |
| benchmark_3yr_pct | REAL | Benchmark 3-year CAGR return in % |
| alpha | REAL | Jensen's Alpha — excess return vs benchmark |
| beta | REAL | Beta vs Nifty 50 — market sensitivity (1.0 = market) |
| sharpe_ratio | REAL | Sharpe Ratio = (Return - RiskFree) / StdDev |
| sortino_ratio | REAL | Sortino Ratio = (Return - RiskFree) / Downside StdDev |
| std_dev_ann_pct | REAL | Annualised standard deviation of returns in % |
| max_drawdown_pct | REAL | Maximum peak-to-trough decline in % (negative value) |
| aum_crore | INTEGER | Assets Under Management in crore INR |
| expense_ratio_pct | REAL | Annual expense ratio in % |
| morningstar_rating | INTEGER | Morningstar star rating 1–5 |
| risk_grade | TEXT | Risk grade: Low / Moderate / High / Very High |

---

## 6. fact_aum
**Source:** `03_aum_by_fund_house.csv`
**Description:** Quarterly AUM figures for top 10 AMCs from 2022–2025.

| Column | Type | Description |
|---|---|---|
| aum_id | INTEGER (PK) | Auto-increment surrogate key |
| date_id | TEXT | Quarter end date in YYYY-MM-DD format |
| fund_house | TEXT | AMC name |
| aum_lakh_crore | REAL | AUM in lakh crore INR (e.g. 6.05 = ₹6.05 lakh crore) |
| aum_crore | INTEGER | AUM in crore INR (e.g. 605000 = ₹6.05 lakh crore) |
| num_schemes | INTEGER | Number of schemes managed by the AMC |

**Note:** aum_lakh_crore and aum_crore represent the same value in different units. Always check units before comparing.

---

## 7. fact_sip
**Source:** `04_monthly_sip_inflows.csv`
**Description:** Monthly SIP industry-level inflow data from AMFI Monthly Note.

| Column | Type | Description |
|---|---|---|
| sip_id | INTEGER (PK) | Auto-increment surrogate key |
| month | TEXT | Month in YYYY-MM format |
| sip_inflow_crore | INTEGER | Total SIP inflows in crore INR |
| active_sip_accounts_crore | REAL | Active SIP accounts in crore |
| new_sip_accounts_lakh | REAL | New SIP accounts registered in lakh |
| sip_aum_lakh_crore | REAL | SIP AUM in lakh crore INR |
| yoy_growth_pct | REAL | Year-over-year growth % (NULL for first 12 months — no prior year base) |

---

## 8. fact_category_inflows
**Source:** `05_category_inflows.csv`
**Description:** Monthly net inflows by fund category for FY 2024–25.

| Column | Type | Description |
|---|---|---|
| cat_id | INTEGER (PK) | Auto-increment surrogate key |
| month | TEXT | Month in YYYY-MM format |
| category | TEXT | Fund category e.g. Large Cap, Small Cap, ELSS |
| net_inflow_crore | REAL | Net inflows in crore INR (negative = net outflow) |

---

## 9. fact_folio_count
**Source:** `06_industry_folio_count.csv`
**Description:** Quarterly total MF folio counts by category.

| Column | Type | Description |
|---|---|---|
| folio_id | INTEGER (PK) | Auto-increment surrogate key |
| month | TEXT | Quarter in YYYY-MM format |
| total_folios_crore | REAL | Total folios across all categories in crore |
| equity_folios_crore | REAL | Equity fund folios in crore |
| debt_folios_crore | REAL | Debt fund folios in crore |
| hybrid_folios_crore | REAL | Hybrid fund folios in crore |
| others_folios_crore | REAL | Other category folios in crore |

---

## 10. fact_portfolio_holdings
**Source:** `09_portfolio_holdings.csv`
**Description:** Top stock holdings per equity fund as of portfolio date.

| Column | Type | Description |
|---|---|---|
| holding_id | INTEGER (PK) | Auto-increment surrogate key |
| amfi_code | INTEGER (FK) | References dim_fund.amfi_code |
| stock_symbol | TEXT | NSE/BSE stock ticker symbol e.g. HDFCBANK |
| stock_name | TEXT | Full company name |
| sector | TEXT | Sector classification e.g. Banking, IT, Pharma |
| weight_pct | REAL | Portfolio weight in % |
| market_value_cr | REAL | Market value of holding in crore INR |
| current_price_inr | REAL | Stock price in INR as of portfolio date |
| portfolio_date | TEXT | Date of portfolio snapshot (YYYY-MM-DD) |

---

## 11. fact_benchmark
**Source:** `10_benchmark_indices.csv`
**Description:** Daily closing values for major Indian market indices.

| Column | Type | Description |
|---|---|---|
| bench_id | INTEGER (PK) | Auto-increment surrogate key |
| date_id | TEXT | Date in YYYY-MM-DD format |
| index_name | TEXT | Index name e.g. NIFTY50, NIFTY100, BSE SmallCap |
| close_value | REAL | Closing index value on that date |

---

## Key Business Definitions

| Term | Definition |
|---|---|
| NAV | Net Asset Value — price per unit of a mutual fund scheme |
| AUM | Assets Under Management — total market value of assets managed |
| SIP | Systematic Investment Plan — fixed monthly investment |
| CAGR | Compound Annual Growth Rate — annualised return over a period |
| Alpha | Excess return generated by fund manager over benchmark |
| Beta | Sensitivity of fund returns to market movements (Nifty 50) |
| Sharpe Ratio | Risk-adjusted return = (Return − Risk-free rate) / Std Dev |
| Sortino Ratio | Like Sharpe but only penalises downside volatility |
| Max Drawdown | Largest peak-to-trough decline in fund NAV |
| Expense Ratio | Annual fee charged by AMC as % of AUM |
| T30 | Top 30 cities by mutual fund penetration |
| B30 | Beyond Top 30 cities — smaller/rural cities |
| AMFI | Association of Mutual Funds in India — industry regulator |
| SEBI | Securities and Exchange Board of India — market regulator |
| Direct Plan | Plan with no distributor commission — lower expense ratio |
| Regular Plan | Plan sold through distributors — higher expense ratio |

---

## Data Sources

| Dataset | Source |
|---|---|
| NAV history | mfapi.in REST API (public, no auth required) |
| Fund master | AMFI India scheme codes and details |
| AUM figures | AMFI Monthly Note (SBI ₹12.5L Cr anchor) |
| SIP inflows | AMFI Monthly SIP Report (₹31,002 Cr Dec 2025 milestone) |
| Benchmark indices | NSE/BSE public index data |
| Investor transactions | Synthetic data based on real AMFI demographic patterns |
