# Day 1 — Data Quality Summary
_Generated 2026-06-02 21:13_

## 1. Datasets loaded

| Dataset | Rows | Cols |
| --- | ---: | ---: |
| fund_master | 40 | 15 |
| nav_history | 46,000 | 3 |
| aum_by_fund_house | 90 | 5 |
| monthly_sip_inflows | 48 | 6 |
| category_inflows | 144 | 3 |
| industry_folio_count | 21 | 6 |
| scheme_performance | 40 | 19 |
| investor_transactions | 32,778 | 13 |
| portfolio_holdings | 322 | 8 |
| benchmark_indices | 8,050 | 3 |

## 2. AMFI code validation

- fund_master codes: 40; nav_history codes: 40
- missing (master without NAV): none
- orphan (NAV without master): none
- PASS — perfect 1:1 referential integrity between fund_master and nav_history.

## 3. Fund master exploration

- Fund houses (10): Aditya Birla Sun Life MF, Axis Mutual Fund, DSP Mutual Fund, HDFC Mutual Fund, ICICI Prudential MF, Kotak Mahindra MF, Mirae Asset MF, Nippon India MF, SBI Mutual Fund, UTI Mutual Fund
- Categories (2): Debt, Equity
- Sub-categories (12): ELSS, Flexi Cap, Gilt, Index, Index/ETF, Large & Mid Cap, Large Cap, Liquid, Mid Cap, Short Duration, Small Cap, Value
- Risk categories (5): High, Low, Moderate, Moderately High, Very High
- Plans (2): Direct, Regular
- SEBI category codes (9): DC01, DC02, EC01, EC02, EC03, EC04, EC05, EC06, EI01
- AMFI codes are numeric (6-6 digits); one unique code per scheme-plan (Regular vs Direct differ).

## 4. Anomalies & notes

- [monthly_sip_inflows] nulls -> yoy_growth_pct=12
- [nav_history] date range 2022-01-03 -> 2026-05-29
- [monthly_sip_inflows] 12 null yoy_growth_pct (expected: first ~12 months have no prior-year base)

## 5. Overall assessment

The provided datasets are clean and internally consistent. All 40 scheme codes in `fund_master` have matching NAV history. The only nulls are the leading `yoy_growth_pct` values in the SIP file, which are expected because year-over-year growth cannot be computed for the first 12 months of the series. No duplicate keys, no non-positive NAVs. Data is fit for downstream analysis.
