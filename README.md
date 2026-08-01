# Mauritania Economic Intelligence Platform (MEIP)

French: **Plateforme d’intelligence économique de la Mauritanie**  
Arabic: **منصة الذكاء الاقتصادي الموريتاني**

MEIP converts Mauritania’s national-accounts workbooks into traceable economic analysis, reconciliation checks, anomaly alerts, experimental forecasts, deterministic Arabic/French answers, and bilingual reports.

## Current status

| Phase | Status | Result |
|---|---|---|
| Phase 1 — Data layer and importer | Complete | Both real Excel workbooks import into normalized SQLite/CSV data |
| Phase 2 — Analytics and core API | Complete | Analytics, accounting identities, reconciliation, anomalies, forecasts, and API routers |
| Phase 3 — Assistant and reports | Complete | Deterministic Arabic/French assistant and Arabic/French PDF/CSV reports |
| Phase 4 — Frontend foundation | Complete | React/Vite/TypeScript/Tailwind foundation, bilingual Home, navigation, RTL, tests, and build |
| Phase 5 — Frontend feature pages | **Not started** | Main work remaining |
| Phase 6 — Final testing and polish | **Not started** | Final acceptance, demo documentation, and deployment polish |

The Home page and shared frontend foundation work. The analytical frontend routes currently show clearly labeled Phase 5 placeholders; they do not display invented dashboard values.

## Data used

MEIP uses only these two real files:

- `data/raw/comptes_nationaux_4.9.1.xlsx`
  - Table 4.9.1
  - Worksheet: `Emplos du PIB courant `
  - GDP by expenditure/use
- `data/raw/comptes_nationaux_4.9.2.xlsx`
  - Table 4.9.2
  - Worksheet: `PIB Courant (2)`
  - GDP by economic activity

Source: **ANSADE/CN**  
Period: **1998–2024**  
Frequency: **Annual**  
Unit: **Millions of MRU**  
Price basis: **Current prices**

The platform therefore describes nominal economic evolution. It does not calculate real GDP, inflation, unemployment, poverty, GDP per capita, or regional GDP.

### Latest import result

| Dataset | Indicators | Stored rows | Missing | Completeness |
|---|---:|---:|---:|---:|
| GDP by expenditure | 12 | 324 | 20 | 93.83% |
| GDP by activity | 27 | 729 | 1 | 99.86% |
| **Total** | **39** | **1,053** | **21** | — |

- Valid numeric observations: **1,032**
- Nonnumeric observations: **0**
- GDP reconciliation years generated: **27**
- Structural alias detected: `agriculture_fishing_forestry` aliases `primary_sector`
- Original workbooks remain unchanged.
- Literal `NA` values remain missing and are never silently replaced with zero.
- The importer is idempotent; repeated imports do not duplicate observations.

## Completed work

### Phase 1 — Data ingestion and persistence

- Created SQLAlchemy models for datasets, indicators, economic values, reconciliation issues, forecasts, and alerts.
- Created the canonical 39-indicator Arabic/French taxonomy and activity hierarchy.
- Preserved original labels, original cell values, worksheet, row, and column provenance.
- Implemented decimal-comma parsing and strict `NA` preservation.
- Implemented exact worksheet matching and automatic year-header extraction.
- Normalized wide Excel tables into long-form economic observations.
- Detected aliases and hierarchical aggregates to prevent double counting.
- Added an idempotent CLI importer.
- Generated normalized CSV files and `data/processed/validation_report.json`.
- Added isolated real-workbook tests for import accuracy and idempotency.

### Phase 2 — Analytics and API

Implemented pure analytics for:

- Nominal annual growth and CAGR
- Minimum, maximum, average, median, total change, and volatility
- Largest annual increase and decrease
- Sector and parent-sector contribution
- Trade balance
- Investment and final-consumption rates
- Export and import ratios
- Trade openness
- Extractive-sector dependence and mining composition
- Accounting identities with `valid`, `valid_with_rounding`, `partial`, and `discrepancy` states
- Activity/expenditure GDP reconciliation
- Robust anomaly detection using median, MAD, robust Z-score, and optional Isolation Forest signal
- Experimental forecasts using naive last value, naive drift, linear trend, Holt, and ARIMA
- Chronological walk-forward validation against a naive baseline using MAE and MAPE

Completed API areas:

- `/api/health`
- `/api/data/import`, `/api/data/status`, `/api/data/quality`, `/api/data/reconciliation`
- `/api/datasets` and dataset detail
- `/api/indicators` plus series and summaries
- `/api/dashboard/overview` and year snapshots
- `/api/activity/sectors`, sector detail, and mining analysis
- `/api/expenditure/overview`, trade, consumption, and investment
- `/api/analytics/growth`, contribution, comparison, and anomalies
- `/api/forecast`

Forecast rules include a one-to-three-year horizon, at least eight observations, chronological ordering, explicit missing-year warnings, non-negative protection where structurally required, reliability classification, and a non-official experimental disclaimer.

### Phase 3 — Assistant and reports

- Added `POST /api/assistant/query`.
- Implemented deterministic Arabic/French language and intent detection without an external LLM or API key.
- Covered the specified questions about GDP, GDP reconciliation, largest sector, fishing/extractive comparison, gold/copper evolution, trade balance, investment rate, largest fishing decline, volatility, and GDP forecasts.
- Answers include the real database values used, year, indicator, unit, source side, source filename, worksheet, and calculation.
- Unsupported questions, such as unemployment, are refused without inventing values.
- Added `POST /api/reports/generate`.
- Added French and Arabic PDF reports with Arabic shaping and right-to-left text.
- Added UTF-8 CSV report export.
- Reports support indicator, period, language, format, and optional forecast selection.
- Reports include source, unit, current-price warning, summary statistics, history, nominal growth, anomalies, methodology, limitations, forecast reliability, and generation date.

### Phase 4 — Frontend foundation

- Scaffolded Vite, React, TypeScript, and Tailwind CSS.
- Added React Router and routes for all planned pages.
- Added i18next French and Arabic locale files.
- Added persistent language switching and document-level `lang`/`dir` updates.
- Added correct Arabic RTL and French LTR layouts.
- Added a responsive shared header, mobile navigation, footer, and language switcher.
- Added a global React error boundary.
- Added a typed Axios API client and initial health hook.
- Built the responsive bilingual Home page with source, period, two-GDP-series explanation, and current-price limitation.
- Added honest Phase 5 placeholders for unfinished analytical pages.
- Added accessibility focus states and reduced-motion support.
- Added Docker frontend configuration.
- Added Vitest and Testing Library tests for the French Home page, Arabic switching/RTL, and unfinished feature placeholders.

## Verified real-data checks

Tests calculate these values from the imported files rather than hard-coding them into the production UI:

### 2024

- Activity-side GDP: **429,701.30**
- Expenditure-side GDP: **429,701.30**
- Primary sector: **83,568.90**
- Secondary sector: **130,730.50**
- Tertiary sector: **181,529.80**
- GDP at factor cost: **395,829.20**
- Net taxes on products: **33,872.10**
- Exports: **169,986.60**
- Imports: **226,907.10**
- Trade balance: **−56,920.50**

The activity identities also verify that the three main sectors total GDP at factor cost and that factor-cost GDP plus net taxes equals activity-side market-price GDP.

### 2018 reconciliation

- Activity-side GDP: **266,637.60**
- Expenditure-side GDP: **262,320.02**
- Activity minus expenditure: **4,317.58**

The two GDP series remain separate throughout the database, analytics, API, assistant, and frontend design.

## Test and build status

Latest completed checks:

- Backend: **96 passed, 0 failed**
- Backend compilation: passed
- Frontend: **3 passed, 0 failed**
- Frontend ESLint: **0 errors, 0 warnings**
- Frontend TypeScript/Vite production build: passed
- Production frontend bundle: approximately **353.68 kB JavaScript / 114.26 kB gzip**

Known non-blocking warnings:

- FastAPI startup-event and Python UTC helper deprecation warnings remain for later cleanup.
- Some ARIMA fits emit convergence warnings; model selection safely falls back when candidates fail.
- npm currently reports a high-severity advisory in React Router’s server/RSC action mode. MEIP is a client-only Vite SPA and does not enable RSC or server actions, but the dependency should continue to be monitored and upgraded when a release resolves the conflicting advisory ranges.

## What remains

### Phase 5 — Frontend feature pages

The main remaining implementation work is connecting the completed APIs to real interactive pages:

1. Overview Dashboard
   - KPI cards
   - Both GDP series
   - Main sectors and contribution charts
   - Nominal GDP growth
   - Exports/imports and recent alerts
2. Activity Analysis
   - Sector hierarchy, contribution, growth, summary, volatility, and year ranking
3. Mining Analysis
   - Extractive, petroleum/gas, SNIM, gold/copper, composition, contribution, and alerts
4. Expenditure Analysis
   - Consumption, investment, inventories, exports/imports, trade balance, and ratios
5. Compare
   - Two-indicator selection, period filter, absolute/indexed/growth views, correlation warning, and CSV download
6. Data Reconciliation
   - Both GDP series, differences, accounting identities, partial checks, and missing components
7. Alerts
   - Severity, observed change, expected behavior, explanations, and chart links
8. Forecast
   - Historical series, prediction, bounds, model/baseline, MAE/MAPE, reliability, and disclaimer
9. Economic Assistant
   - Arabic/French question form, evidence values, calculation, provenance, and related visualization
10. Reports
    - Indicator, period, language, PDF, and CSV controls
11. Data Catalogue
    - Source files, worksheets, period, units, observation counts, missing values, and import date

Phase 5 also needs shared chart, KPI, loading, empty, error, missing-value, severity, and GDP-source-selector components. All user-facing additions must remain bilingual.

### Phase 6 — Final validation and polish

- Expand frontend tests for loading, API errors, missing values, GDP source selection, and reconciliation warnings.
- Run the complete backend and frontend suites together.
- Perform accessibility and responsive-layout checks.
- Verify Arabic RTL across every completed page and chart.
- Add `docs/DEMO_SCRIPT.md`.
- Add a root `run-dev.ps1` convenience launcher.
- Finalize deployment/Docker behavior.
- Review and resolve dependency/deprecation warnings where practical.
- Run the full acceptance checklist from the original specification.

## Run on Windows

### 1. Install and import the backend data

```powershell
cd C:\Users\Sosom\OneDrive\Desktop\Mauritania-Economic-Intelligence
python -m pip install -r apps\api\requirements.txt
python scripts\import_national_accounts.py
```

### 2. Start the API

```powershell
cd C:\Users\Sosom\OneDrive\Desktop\Mauritania-Economic-Intelligence\apps\api
python -m uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

### 3. Start the frontend in another PowerShell window

```powershell
cd C:\Users\Sosom\OneDrive\Desktop\Mauritania-Economic-Intelligence\apps\web
npm install
npm run dev
```

Frontend: `http://127.0.0.1:5173`

## Run quality checks

Backend:

```powershell
cd C:\Users\Sosom\OneDrive\Desktop\Mauritania-Economic-Intelligence\apps\api
pytest -q
pytest -v
pytest --cov=app --cov-report=term-missing
python -m compileall app
```

Frontend:

```powershell
cd C:\Users\Sosom\OneDrive\Desktop\Mauritania-Economic-Intelligence\apps\web
npm test
npm run lint
npm run build
```

## Repository structure

```text
apps/api/       FastAPI backend, ingestion, analytics, assistant, reports, tests
apps/web/       React frontend foundation and tests
data/raw/       Original Excel files
data/processed/ Normalized CSV files and validation report
docs/           Architecture, methodology, quality notes, dictionary, plan
scripts/        Import command
```

## Non-negotiable data rules

- Never fabricate, guess, interpolate, or silently zero-fill economic values.
- Label any future demo data as `DEMO DATA` where defined and displayed.
- Keep indicator codes synchronized with `docs/DATA_DICTIONARY.md`.
- Preserve chronological ordering in time-series analysis and forecasting.
- Keep calculations as pure functions under `apps/api/app/analytics/`.
- Add both Arabic and French variants for every user-facing string.
- Use activity-side GDP for sector contributions.
- Use expenditure-side GDP for expenditure ratios.
- Never silently merge the two GDP series.
- Never describe current-price nominal GDP growth as real economic growth.

## Documentation

- `docs/ARCHITECTURE.md` — system architecture and layering
- `docs/DATA_DICTIONARY.md` — canonical indicator taxonomy and source mappings
- `docs/METHODOLOGY.md` — calculations, anomalies, and forecasting methods
- `docs/DATA_QUALITY.md` — missing values, aliases, reconciliation, and limitations
- `docs/IMPLEMENTATION_PLAN.md` — phase-by-phase implementation plan

MEIP is an educational and decision-support platform. Its forecasts are experimental estimates and are not official ANSADE statistics or policy recommendations.
