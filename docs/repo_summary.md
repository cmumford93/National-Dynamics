# Repository State Summary

## Overview
- **Project focus:** Streamlit-based dashboard exploring U.S. social, economic, religious, family, crime, and mental health indicators using demo CSVs that will be replaced by real datasets. The README outlines the high-level structure and the Variable Comparison explorer feature. 【F:README.md†L1-L23】
- **App entry point:** `app/app.py` configures the Streamlit layout, loads datasets from `data/`, and renders sections such as Overview, Family Structure, Economics, Crime & Safety, Religion & Culture, Mental Health, and About. 【F:app/app.py†L13-L195】【F:app/app.py†L336-L404】

## Data
- **Demo CSVs in `data/`:** synthetic indicators for marriage, income, unemployment, CPI, violent crime, mass incidents, household composition, religion, and mental health. These power most app visuals while awaiting real sources. 【F:app/app.py†L42-L118】【F:app/app.py†L238-L332】
- **Real data fallback:** `marriage_rate_real.csv` is loaded when present; otherwise the app uses `marriage_rate_demo.csv`. Similar logic applies to unemployment data. 【F:app/app.py†L21-L76】【F:app/app.py†L218-L238】

## Application Pages
- **Overview:** KPI cards and line charts for marriage, income, violent crime, and suicide demo series; shows placeholder messaging when data is missing. 【F:app/app.py†L83-L211】
- **Family Structure:** Prioritizes real CDC marriage data when available; includes household composition area chart from demo data. 【F:app/app.py†L268-L333】
- **Economics:** Metrics and line charts for unemployment, median income, and CPI demo series with source notes on real vs. demo unemployment data. 【F:app/app.py†L215-L266】
- **Crime & Safety:** Metrics and charts for violent crime and mass incident demo series. 【F:app/app.py†L245-L266】【F:app/app.py†L334-L398】
- **Religion & Culture:** Demo KPIs and trend lines for Christian, Catholic, and unaffiliated identification. 【F:app/app.py†L400-L472】
- **Mental Health:** Demo KPIs and trend lines for depression, anxiety, and suicide rates. 【F:app/app.py†L474-L541】
- **Variable Comparison (Beta):** Streamlit page (`app/pages/03_variable_comparison.py`) that loads numeric columns from all CSVs, lets users pick any two variables, aligns data (by year when possible), plots scatter with regression, highlights outliers, and auto-generates a correlation summary. 【F:app/pages/03_variable_comparison.py†L1-L152】【F:app/pages/03_variable_comparison.py†L154-L233】

## Data Generation & Ingestion Scripts
- **`scripts/fetch_marriage_data.py`:** Downloads the CDC marriage-rate PDF when possible, attempts table extraction with `pdfplumber` if installed, and falls back to manually transcribed 2000–2020 national rates before writing `data/marriage_rate_real.csv`. 【F:scripts/fetch_marriage_data.py†L1-L92】【F:scripts/fetch_marriage_data.py†L94-L162】
- **`scripts/regenerate_demo_data.py`:** Uses seeded NumPy random streams to synthesize economic, social, and cultural drivers, then generates demo CSVs for marriage rates, income, unemployment, CPI, crime, mass incidents, mental health, household types, and religion trends in `data/`. 【F:scripts/regenerate_demo_data.py†L1-L24】【F:scripts/regenerate_demo_data.py†L90-L157】

## Testing
- **`tests/test_imports.py`:** Smoke test ensuring the Streamlit app module imports without errors. 【F:tests/test_imports.py†L1-L6】

## Notable Next Steps
- Replace demo CSVs with documented real datasets (CDC, BLS, FBI, Census) and expand tests beyond import checks.
- Harden data loaders with clearer error messages and add visual polish to charts for recruiter-facing readiness.
- Document how to run the Streamlit app and data regeneration scripts once the stack stabilizes.
