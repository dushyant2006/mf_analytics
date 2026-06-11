-- ============================================================
-- queries.sql
-- Bluestock Fintech Capstone | Day 2
-- 10 Analytical SQL Queries on bluestock_mf.db
-- ============================================================

-- Q1: Top 5 funds by AUM (crore)
SELECT
    f.scheme_name,
    f.fund_house,
    f.category,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- ============================================================

-- Q2: Average NAV per month for SBI Bluechip Regular (amfi_code 119551)
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 4) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date_id = d.date_id
WHERE n.amfi_code = 119551
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- ============================================================

-- Q3: SIP inflow YoY growth (where available)
SELECT
    month,
    sip_inflow_crore,
    ROUND(yoy_growth_pct, 2) AS yoy_growth_pct
FROM fact_sip
WHERE yoy_growth_pct IS NOT NULL
ORDER BY month;

-- ============================================================

-- Q4: Total transactions by state (top 10)
SELECT
    state,
    COUNT(*)                        AS total_transactions,
    ROUND(SUM(amount_inr) / 1e7, 2) AS total_amount_crore
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC
LIMIT 10;

-- ============================================================

-- Q5: Funds with expense ratio below 1%
SELECT
    f.scheme_name,
    f.fund_house,
    f.plan,
    f.expense_ratio_pct
FROM dim_fund f
WHERE f.expense_ratio_pct < 1.0
ORDER BY f.expense_ratio_pct ASC;

-- ============================================================

-- Q6: Top 5 funds by 3-year return
SELECT
    f.scheme_name,
    f.fund_house,
    p.return_3yr_pct,
    p.benchmark_3yr_pct,
    ROUND(p.return_3yr_pct - p.benchmark_3yr_pct, 2) AS alpha_vs_benchmark
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_3yr_pct DESC
LIMIT 5;

-- ============================================================

-- Q7: Transaction breakdown by type and city tier
SELECT
    transaction_type,
    city_tier,
    COUNT(*)                         AS count,
    ROUND(SUM(amount_inr) / 1e7, 2)  AS total_crore
FROM fact_transactions
GROUP BY transaction_type, city_tier
ORDER BY transaction_type, city_tier;

-- ============================================================

-- Q8: AUM growth by fund house (latest vs earliest quarter)
SELECT
    fund_house,
    MIN(aum_crore) AS aum_earliest,
    MAX(aum_crore) AS aum_latest,
    ROUND(
        (MAX(aum_crore) - MIN(aum_crore)) * 100.0 / MIN(aum_crore),
        1
    ) AS growth_pct
FROM fact_aum
GROUP BY fund_house
ORDER BY growth_pct DESC;

-- ============================================================

-- Q9: Top sectors by total portfolio weight across all funds
SELECT
    sector,
    COUNT(DISTINCT amfi_code)           AS num_funds,
    ROUND(AVG(weight_pct), 2)           AS avg_weight_pct,
    ROUND(SUM(market_value_cr), 0)      AS total_market_value_cr
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_market_value_cr DESC;

-- ============================================================

-- Q10: Investor age group vs average SIP amount
SELECT
    age_group,
    transaction_type,
    COUNT(*)                            AS count,
    ROUND(AVG(amount_inr), 0)           AS avg_amount_inr,
    ROUND(SUM(amount_inr) / 1e7, 2)     AS total_crore
FROM fact_transactions
GROUP BY age_group, transaction_type
ORDER BY age_group, transaction_type;
