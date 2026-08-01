# MEIP Architecture

## Overview

MEIP is a monorepo with a Python/FastAPI backend (`apps/api`) and a
React/Vite/TypeScript frontend (`apps/web`), backed by SQLite for the MVP
(SQLAlchemy ORM, schema written so swapping to PostgreSQL later is a
connection-string change, not a rewrite).

The platform is driven by exactly two real source files
(`data/raw/comptes_nationaux_4.9.1.xlsx`, `comptes_nationaux_4.9.2.xlsx`),
described fully in `docs/DATA_DICTIONARY.md`. No other economic data is
invented or synthesized anywhere in the running app.

```
Browser (React SPA)
   │  Axios (JSON over HTTPS/HTTP)
   ▼
FastAPI app (apps/api)
   ├── routers/         HTTP layer: request validation (Pydantic), response shaping
   ├── services/         business logic: dataset/indicator lookups, dashboard aggregation
   ├── analytics/        growth, contribution, ratios, reconciliation, anomalies, forecasting
   ├── assistant/         deterministic bilingual intent router (built on services/analytics)
   ├── reports/           ReportLab bilingual PDF + CSV export
   ├── ingestion/          exact-worksheet reader, label cleaning, hierarchy, validation report
   ├── models/             SQLAlchemy ORM models
   ├── schemas/            Pydantic request/response schemas
   ├── translations/       static AR/FR string tables for backend-generated text
   └── main.py / config.py / database.py
   ▼
SQLite file (data-layer; PostgreSQL-compatible via SQLAlchemy)

scripts/import_national_accounts.py
   — idempotent CLI: reads both fixed files from data/raw, imports via the
     same ingestion package the API uses, writes data/processed/*.csv and a
     JSON validation report.
```

## Backend layering rules

Stress testing follows `routers/stress_test.py → services/stress_test.py →
analytics/stress_test.py`. Recommendations consume the unchanged stress-test
result through their own router/service and pure rules. Database access stays
out of calculations and recommendation wording cannot alter accounting output.

- **Routers** never touch calculation logic — they call **services**, which
  call **analytics** for any number-crunching. This keeps growth/
  contribution/reconciliation/anomaly/forecast math unit-testable without
  spinning up HTTP.
- **Analytics** functions are pure where possible: given `(year, value)`
  series (with explicit gaps for missing years, never densified with 0),
  return a result object. No DB session parameter.
- **Ingestion** is `read fixed worksheet → detect year row → clean labels →
  map to canonical indicator codes → build hierarchy → parse decimal-comma
  values / NA → validate → (on confirm) persist`. It is idempotent:
  re-running the importer against the same two files upserts by
  `(dataset_id, indicator_id, year)` rather than duplicating rows.
- **Never invent values**: any code path that would need to fabricate a
  number (an `NA` cell, an unresolved accounting identity, insufficient
  forecast observations) returns an explicit "not available" / "partial"
  state that the frontend renders — never a zero, never a guess.
- **Two GDP series are never merged.** `gdp_expenditure` (4.9.1) and
  `gdp_activity_market_prices` (4.9.2) are stored, displayed, and reasoned
  about as distinct indicators; `ReconciliationIssue` rows record their
  divergence per year rather than resolving it.

## Database model

See inline SQLAlchemy models for exact columns; entities:

- `Dataset` — one row per source table (`4.9.1` expenditure,
  `4.9.2` activity), including `worksheet_name`/`table_number` for
  provenance back to the exact source cell range.
- `Indicator` — the taxonomy from `docs/DATA_DICTIONARY.md`, self
  -referencing via `parent_indicator_id` for the real branch hierarchy
  (up to 5 levels deep on the activity side), with `is_aggregate`,
  `is_alias`/`alias_of_indicator_id` (e.g. `agriculture_fishing_forestry`
  is an alias of `primary_sector`, not an additional sibling), and
  `source_side` (`expenditure` | `activity`).
- `EconomicValue` — the long-form fact table: one row per
  (dataset, indicator, year). `value` is nullable; `is_missing` is set
  when the source cell was the literal `"NA"`; `original_value` and
  `source_row`/`source_column` preserve provenance.
- `ReconciliationIssue` — one row per year where two indicators that
  should agree (chiefly the two GDP series) diverge beyond a rounding
  tolerance, with bilingual explanations.
- `Forecast` — persisted model output per indicator/target_year, including
  the selected model, the naive baseline's error, MAE/MAPE, and a
  `reliability` label.
- `EconomicAlert` — persisted anomaly detections with bilingual
  explanations and `percentage_change`.

## Accounting-identity checks

`analytics/identities.py` verifies, per year, with a small rounding
tolerance:

- Activity side: `gdp_factor_cost + net_taxes_products == gdp_activity_market_prices`,
  and `primary_sector + secondary_sector + tertiary_sector == gdp_factor_cost`.
- Expenditure side: `final_consumption + gross_fixed_capital_formation +
  inventory_changes + net_acquisition_valuables + exports - imports ==
  gdp_expenditure`. When `net_acquisition_valuables` is `NA` for that year,
  the check is marked **partial** (computed from known components only,
  with the missing component surfaced explicitly) rather than silently
  treating it as zero.

## Assistant design

The assistant is **not** an LLM by default. It is a deterministic
intent-router:

1. Language detection (Arabic script vs. Latin/French heuristic).
2. Intent classification via keyword/regex matching (value lookup, GDP
   -series difference, leading-sector, comparison, biggest-drop/rise,
   trend-over-time, trade balance, investment/consumption rate, forecast
   request, volatility ranking).
3. Entity extraction: indicator code (fuzzy-matched against
   `Indicator.name_fr`/`name_ar`/aliases and the canonical code list), year
   or year range.
4. The matched intent dispatches to the **same services/analytics layer**
   used by the REST endpoints, then fills a bilingual response template
   with the real numbers, years, source table (expenditure vs. activity),
   and unit — and states explicitly when a figure is nominal, not real.
5. Unresolved intent/entities, or a requested year/indicator with no data,
   returns an explicit "not available in the imported data" message in the
   detected language.
6. An `LLMAdapter` interface is defined so an optional external LLM can
   later be plugged in for phrasing/paraphrase only — never to originate
   numbers.

## Forecasting design

`analytics/forecasting.py` implements naive-last-value and naive-drift
baselines, linear trend, Holt exponential smoothing, and ARIMA only when
enough valid observations exist — selected by chronological walk-forward
backtest (never shuffled), always compared against the naive baseline,
using MAE/MAPE. Requires ≥8 valid observations; forecasts default to a
3-year horizon; series that are structurally non-negative are clamped at 0
with a note rather than allowed to go negative; every forecast is labeled
an experimental estimate, never an official ANSADE statistic.

## Frontend structure

- `pages/` — Home, Overview Dashboard, Activity Analysis, Mining Analysis,
  Expenditure Analysis, Compare, Data Reconciliation, Alerts, Forecast,
  Economic Assistant, Reports, Data Catalogue.
- `components/` — shared building blocks (charts, KPI cards, language
  switcher, severity badges, GDP-source selector, empty/error/loading
  states).
- `services/` — Axios client + typed functions per API endpoint.
- `contexts/` — language/direction context (drives i18next + `dir="rtl"`).
- `hooks/` — data-fetching hooks wrapping `services/` with loading/error
  state.
- `locales/` — `ar.json` / `fr.json` for i18next UI chrome; economic data
  labels come from the backend's AR/FR fields directly.

## Environments & config

- Backend reads `DATABASE_URL`, `CORS_ORIGINS`, `UPLOAD_DIR`,
  `MAX_UPLOAD_MB`, `DATA_RAW_DIR`, `DATA_PROCESSED_DIR` from environment
  (`.env`, see `.env.example`) via `app/config.py` (Pydantic
  `BaseSettings`). Default `DATABASE_URL` is a local SQLite file under a
  git-ignored `apps/api/var/` directory.
- Frontend reads `VITE_API_BASE_URL` from `.env`.

## Testing strategy

- Backend: `pytest` unit tests for `ingestion/` (worksheet reading, label
  cleaning, decimal-comma + NA parsing, hierarchy construction, alias
  detection) asserting against the **real, exact figures** from the source
  files (e.g. 2024 activity-side GDP = 429701.30; 2018 GDP reconciliation
  difference = 4317.58), plus `analytics/` unit tests (growth, contribution,
  trade balance, investment rate, reconciliation, anomaly detection,
  forecast minimum-observation rule) and assistant integration tests in
  both Arabic and French.
- Frontend: component tests (Vitest + Testing Library) for language
  switching/RTL, dashboard loading, empty/missing-value states, API error
  state, the GDP-source selector, and the reconciliation warning.
