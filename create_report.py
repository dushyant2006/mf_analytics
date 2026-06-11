#!/usr/bin/env python3
"""
create_report.py
================
Generates Final_Report.pdf for Bluestock MF Capstone
Usage: python create_report.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, PageBreak, Image)
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from pathlib import Path
import os

ROOT    = Path(__file__).resolve().parent
CHARTS  = ROOT / "reports" / "charts"
OUT     = ROOT / "reports" / "Final_Report.pdf"

# Colors
NAVY  = HexColor("#0F1B2D")
TEAL  = HexColor("#00D4AA")
LGRAY = HexColor("#F5F5F5")
DGRAY = HexColor("#333333")

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle("Title",
    fontSize=28, textColor=TEAL, spaceAfter=6,
    alignment=TA_CENTER, fontName="Helvetica-Bold")

h1_style = ParagraphStyle("H1",
    fontSize=18, textColor=NAVY, spaceAfter=6, spaceBefore=16,
    fontName="Helvetica-Bold", borderPad=4)

h2_style = ParagraphStyle("H2",
    fontSize=14, textColor=TEAL, spaceAfter=4, spaceBefore=10,
    fontName="Helvetica-Bold")

body_style = ParagraphStyle("Body",
    fontSize=11, textColor=DGRAY, spaceAfter=6,
    leading=16, alignment=TA_JUSTIFY, fontName="Helvetica")

bullet_style = ParagraphStyle("Bullet",
    fontSize=11, textColor=DGRAY, spaceAfter=4,
    leftIndent=20, leading=15, fontName="Helvetica")

sub_style = ParagraphStyle("Sub",
    fontSize=10, textColor=HexColor("#666666"),
    alignment=TA_CENTER, fontName="Helvetica-Oblique")

def h(text, style): return Paragraph(text, style)
def sp(n=6):        return Spacer(1, n)
def pb():           return PageBreak()

def chart(name, width=5.5, height=3.0):
    path = CHARTS / name
    if path.exists():
        return Image(str(path), width=width*inch, height=height*inch)
    return Paragraph(f"[Chart: {name}]", sub_style)

def table(data, col_widths=None):
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), NAVY),
        ("TEXTCOLOR",   (0,0), (-1,0), white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[LGRAY, white]),
        ("GRID",        (0,0), (-1,-1), 0.3, HexColor("#CCCCCC")),
        ("ALIGN",       (0,0), (-1,-1), "LEFT"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("PADDING",     (0,0), (-1,-1), 5),
    ]))
    return t

# ── Build document ──────────────────────────────────────────
story = []

# Cover
story += [
    sp(60),
    h("Bluestock Fintech Pvt. Ltd.", title_style),
    sp(8),
    h("Mutual Fund Analytics Platform", ParagraphStyle("CT",
        fontSize=22, textColor=NAVY, alignment=TA_CENTER,
        fontName="Helvetica-Bold")),
    sp(8),
    h("Capstone Project — Final Report", sub_style),
    sp(4),
    h("Dushyant Sharma  |  2026", sub_style),
    pb(),
]

# 1. Executive Summary
story += [
    h("1. Executive Summary", h1_style), sp(),
    h("""This report documents the design and implementation of a full-stack 
    Mutual Fund Analytics Platform built for Bluestock Fintech Pvt. Ltd. 
    The platform ingests real Indian mutual fund data from AMFI India and 
    mfapi.in, processes it through a Python ETL pipeline, stores it in a 
    normalised SQLite database, and presents insights through interactive 
    Power BI dashboards.""", body_style), sp(),
    h("""The platform covers 40 AMFI schemes across 10 fund houses, 46,000+ 
    daily NAV records, 32,778 investor transactions, and benchmark indices 
    spanning January 2022 to May 2026. Key findings include SIP inflows 
    hitting an all-time high of ₹31,002 crore in December 2025, total MF 
    folios doubling to 26.12 crore, and SBI Mutual Fund leading industry 
    AUM at ₹12.5 lakh crore.""", body_style),
    pb(),
]

# 2. Data Sources
story += [
    h("2. Data Sources", h1_style), sp(),
    h("2.1 Datasets Used", h2_style), sp(),
    table([
        ["Dataset", "Rows", "Description"],
        ["01_fund_master.csv", "40", "40 AMFI schemes with codes, AMC, risk grade"],
        ["02_nav_history.csv", "46,000", "Daily NAV Jan 2022–May 2026"],
        ["03_aum_by_fund_house.csv", "90", "Quarterly AUM for top 10 AMCs"],
        ["04_monthly_sip_inflows.csv", "48", "Monthly SIP inflows — ₹31,002 Cr milestone"],
        ["05_category_inflows.csv", "144", "Net inflows by fund category FY24-25"],
        ["06_industry_folio_count.csv", "21", "Total MF folios (crore) quarterly"],
        ["07_scheme_performance.csv", "40", "Risk metrics: Sharpe, Alpha, Beta, VaR"],
        ["08_investor_transactions.csv", "32,778", "SIP/Lumpsum/Redemption across 12 states"],
        ["09_portfolio_holdings.csv", "322", "Top stock holdings per equity fund"],
        ["10_benchmark_indices.csv", "8,050", "Nifty 50, Nifty 100, BSE SmallCap"],
    ], [2.2*inch, 0.8*inch, 3.5*inch]),
    sp(),
    h("2.2 Data Sources", h2_style), sp(),
    h("• AMFI India — Association of Mutual Funds in India (amfiindia.com)", bullet_style),
    h("• mfapi.in — Free REST API for Indian mutual fund NAV data", bullet_style),
    h("• NSE/BSE — National Stock Exchange and Bombay Stock Exchange public data", bullet_style),
    pb(),
]

# 3. ETL Design
story += [
    h("3. ETL Pipeline Design", h1_style), sp(),
    h("3.1 Extract", h2_style), sp(),
    h("""Data was extracted from two sources: (1) 10 CSV files provided by 
    AMFI India containing fund master, NAV history, AUM, SIP inflows, 
    category inflows, folio counts, scheme performance, investor transactions, 
    portfolio holdings, and benchmark indices; (2) Live NAV data fetched from 
    the mfapi.in REST API for 6 key schemes.""", body_style), sp(),
    h("3.2 Transform", h2_style), sp(),
    h("The following cleaning operations were performed:", body_style), sp(),
    h("• NAV History: parsed dates, sorted by fund+date, forward-filled weekends/holidays (46,000 → 64,320 rows), removed duplicates, validated NAV > 0", bullet_style),
    h("• Investor Transactions: standardised transaction types (SIP/Lumpsum/Redemption), validated amount > 0, checked KYC enum values", bullet_style),
    h("• Scheme Performance: validated all numeric columns, checked expense ratio range (0.1%–2.5%), flagged anomalies", bullet_style),
    sp(),
    h("3.3 Load", h2_style), sp(),
    h("""All cleaned datasets were loaded into a SQLite database 
    (bluestock_mf.db, 5.5 MB) using a normalised star schema with 11 tables. 
    The schema includes dimension tables (dim_fund, dim_date) and fact tables 
    (fact_nav, fact_transactions, fact_performance, fact_aum, fact_sip, 
    fact_category_inflows, fact_folio_count, fact_portfolio_holdings, 
    fact_benchmark).""", body_style),
    pb(),
]

# 4. EDA Findings
story += [
    h("4. EDA Findings", h1_style), sp(),
    h("4.1 SIP Inflow Trend", h2_style), sp(),
    chart("03_sip_trend.png", 6.0, 3.0), sp(),
    h("Monthly SIP inflows grew from ₹11,517 crore in January 2022 to an all-time high of ₹31,002 crore in December 2025 — a 169% increase over 4 years, reflecting massive growth in retail investor participation.", body_style),
    sp(12),
    h("4.2 AUM Growth by Fund House", h2_style), sp(),
    chart("02_aum_growth.png", 6.0, 3.0), sp(),
    h("SBI Mutual Fund leads with ₹12.5 lakh crore AUM (106% growth). Mirae Asset showed the highest growth rate at 176%, followed by Nippon India at 159%.", body_style),
    pb(),
    h("4.3 Folio Count Growth", h2_style), sp(),
    chart("07_folio_growth.png", 6.0, 3.0), sp(),
    h("Total MF folios doubled from 13.26 crore in January 2022 to 26.12 crore in December 2025, indicating successful financial inclusion across India.", body_style),
    sp(12),
    h("4.4 Sector Allocation", h2_style), sp(),
    chart("09_sector_donut.png", 4.5, 3.5), sp(),
    h("Banking dominates sector allocation with ₹62,840 crore in combined market value across all equity funds, followed by IT (₹38,477 Cr) and Pharma (₹34,606 Cr).", body_style),
    pb(),
]

# 5. Performance Analysis
story += [
    h("5. Performance Analysis", h1_style), sp(),
    h("5.1 Sharpe Ratio Rankings", h2_style), sp(),
    chart("12_sharpe_ratio.png", 6.0, 3.5), sp(),
    h("Funds with Sharpe ratio above 1.0 demonstrate superior risk-adjusted returns. Direct plan funds consistently outperform their Regular counterparts due to lower expense ratios.", body_style),
    sp(12),
    h("5.2 Maximum Drawdown", h2_style), sp(),
    chart("13_max_drawdown.png", 6.0, 3.5), sp(),
    h("Small cap funds show the worst maximum drawdowns exceeding -24%, while debt funds (Gilt, Liquid) show minimal drawdowns below -5%. Investors should align fund selection with their risk tolerance and investment horizon.", body_style),
    pb(),
    h("5.3 Fund Scorecard", h2_style), sp(),
    chart("14_fund_scorecard.png", 6.0, 3.5), sp(),
    h("The composite scorecard (weighted: 30% 3Y return + 25% Sharpe + 20% Alpha + 15% expense ratio + 10% drawdown) provides a holistic ranking. Direct plan funds with low expense ratios and consistent alpha dominate the top rankings.", body_style),
    sp(12),
    h("5.4 Benchmark Comparison", h2_style), sp(),
    chart("15_benchmark_comparison.png", 6.0, 3.0), sp(),
    h("Top 5 funds outperformed both Nifty 50 and Nifty 100 on a normalised basis over the 3-year period, validating active fund management value for select schemes.", body_style),
    pb(),
]

# 6. Advanced Analytics
story += [
    h("6. Advanced Analytics", h1_style), sp(),
    h("6.1 Value at Risk (VaR 95%)", h2_style), sp(),
    chart("16_var_chart.png", 6.0, 3.5), sp(),
    h("Historical VaR at 95% confidence shows small cap funds carry daily tail risk exceeding -2.5%, while liquid and gilt funds show near-zero VaR. Investors should size positions accordingly.", body_style),
    sp(12),
    h("6.2 Rolling Sharpe Ratio", h2_style), sp(),
    chart("17_rolling_sharpe.png", 6.0, 3.0), sp(),
    h("The 90-day rolling Sharpe ratio reveals that all selected funds experienced a sharp spike in mid-2023 (bull run) followed by compression in late 2024 (market correction).", body_style),
    pb(),
    h("6.3 Investor Cohort Analysis", h2_style), sp(),
    chart("18_cohort_analysis.png", 5.0, 3.0), sp(),
    h("Investors who joined in 2024 show the highest average SIP amounts, suggesting newer investors enter with larger ticket sizes driven by increased financial literacy.", body_style),
    sp(12),
    h("6.4 SIP Continuity", h2_style), sp(),
    chart("19_sip_continuity.png", 4.0, 3.0), sp(),
    h("Over 75% of investors with 6+ SIP transactions maintain strong continuity (avg gap ≤ 35 days). The 25% at-risk segment represents an opportunity for AMC retention campaigns.", body_style),
    pb(),
]

# 7. Recommendations
story += [
    h("7. Recommendations", h1_style), sp(),
    h("Based on the analysis, the following recommendations are made:", body_style), sp(),
    h("1. For Conservative Investors (Low Risk)", h2_style), sp(),
    h("Recommend Gilt and Liquid funds with VaR < -0.5%/day. SBI Magnum Gilt and Kotak Liquid Fund offer stable returns with minimal drawdown.", bullet_style), sp(),
    h("2. For Moderate Risk Investors", h2_style), sp(),
    h("HDFC Top 100, Mirae Asset Large Cap, and ICICI Prudential Bluechip offer Sharpe ratios above 1.0 with 3Y CAGR of 14%+. Direct plans save 0.7–0.9% in annual expense ratio.", bullet_style), sp(),
    h("3. For Aggressive Investors (High Risk)", h2_style), sp(),
    h("Small cap funds deliver 20–23% 3Y CAGR but carry VaR exceeding -2.5%/day. Only suitable for 5+ year horizon with monthly SIP discipline.", bullet_style), sp(),
    h("4. SIP Continuity", h2_style), sp(),
    h("AMCs should implement automated reminders for the 25% at-risk investors showing SIP gaps > 35 days to reduce churn and improve long-term returns.", bullet_style), sp(),
    h("5. Diversification", h2_style), sp(),
    h("Funds with HHI > 2000 are overly concentrated in Banking/IT. Investors seeking true diversification should prefer funds with HHI < 1000.", bullet_style),
    pb(),
]

# 8. Limitations
story += [
    h("8. Limitations", h1_style), sp(),
    h("• Dataset covers only 40 out of 1,908+ AMFI-registered schemes", bullet_style),
    h("• Investor transaction data is synthetic (based on real AMFI demographic patterns)", bullet_style),
    h("• VaR calculations use historical simulation — does not account for fat-tail events", bullet_style),
    h("• Power BI dashboard requires desktop installation — not web-accessible without Power BI Pro", bullet_style),
    h("• NAV forward-filling assumes no trading on weekends/holidays — may introduce minor bias", bullet_style),
    pb(),
]

# 9. Conclusion
story += [
    h("9. Conclusion", h1_style), sp(),
    h("""This capstone project successfully demonstrates a complete end-to-end 
    mutual fund analytics pipeline. From raw AMFI CSV ingestion to a 
    professional Power BI dashboard, every stage of the data lifecycle was 
    implemented using industry-standard tools and best practices.""", body_style), sp(),
    h("""Key achievements include: processing 64,320+ NAV records, computing 
    8 risk metrics for 40 funds, building an 11-table star schema database, 
    creating 20+ analytical charts, and delivering a 4-page interactive 
    dashboard. The fund recommender system provides actionable investment 
    guidance based on risk appetite.""", body_style), sp(),
    h("""The Indian mutual fund industry's explosive growth — SIP inflows 
    tripling to ₹31,002 crore and folios doubling to 26.12 crore — underscores 
    the critical importance of accessible analytics platforms for retail 
    investors.""", body_style),
]

# Build PDF
doc = SimpleDocTemplate(str(OUT), pagesize=A4,
                         rightMargin=0.75*inch, leftMargin=0.75*inch,
                         topMargin=0.75*inch, bottomMargin=0.75*inch)
doc.build(story)
print(f"✓ Final Report saved: {OUT}")