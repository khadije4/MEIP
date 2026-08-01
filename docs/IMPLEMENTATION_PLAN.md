# MEIP Implementation Plan

## Status (2026-08-01)

Both real source files are present in `data/raw/`:
- `comptes_nationaux_4.9.1.xlsx` — sheet `Emplos du PIB courant ` (expenditure)
- `comptes_nationaux_4.9.2.xlsx` — sheet `PIB Courant (2)` (activity)

Their exact structure was inspected directly (openpyxl) and verified: year
header row, indentation/numbering scheme, decimal-comma text values, `NA`
missing markers, and the full parent→child hierarchy (values sum exactly).
The dual-GDP divergence for 2018–2020 and agreement in 2024 was confirmed
against the real cells. Full detail in `docs/DATA_DICTIONARY.md`.

An initial generic scaffold (config, DB session, a first-pass Dataset/
Indicator/EconomicValue model, a generic wide-CSV ingestion pipeline with
its own tests) was built before the real files arrived and is being
superseded by a rebuild that matches the actual two-file structure and the
full Section 1–21 spec (models, canonical codes, reconciliation, identities,
mining breakdown, assistant, forecasting, reports, 12 frontend pages).

## Phases

### Phase 1 — Data layer + real importer (complete)
- Rebuild models: `Dataset`, `Indicator` (hierarchy_level, is_aggregate,
  is_alias/alias_of, source_side), `EconomicValue` (is_missing,
  source_row/column), new `ReconciliationIssue`, `Forecast` (+baseline_model,
  reliability), `EconomicAlert` (+percentage_change).
- Rebuild `ingestion/taxonomy.py` with the ~40 canonical codes from
  Section 7, hierarchy, and alias flag, matching the verified real
  structure.
- Rebuild `ingestion/` to: open each workbook by exact sheet name (trimmed
  match), read the year header row, walk rows column A for labels,
  strip nbsp/numbering into a clean `name_fr` while preserving
  `original_label`, parse decimal-comma values, treat literal `NA` as
  `is_missing` (never 0), build parent/child links from indentation depth,
  and flag `agriculture_fishing_forestry` as an alias of `primary_sector`.
- `scripts/import_national_accounts.py`: idempotent CLI importer (upsert by
  dataset/indicator/year), writes `data/processed/*.csv` + a JSON
  validation report, logs warnings.
- Tests assert the **exact real values** from Section 18 (2024 activity GDP
  429701.30, primary 83568.90, secondary 130730.50, tertiary 181529.80,
  factor-cost 395829.20, net taxes 33872.10, exports 169986.60, imports
  226907.10, trade balance −56920.50; 2018 reconciliation: activity
  266637.60, expenditure 262320.02, difference 4317.58) plus idempotency
  (running the importer twice does not duplicate rows).
- Run `pytest`, report results.

### Phase 2 — Analytics + accounting identities + core API (complete)
- `analytics/growth.py`, `contribution.py`, `ratios.py` (trade balance,
  investment rate, consumption rate, export/import ratio, trade openness,
  extractive dependence, mining composition), `identities.py` (the three
  accounting checks, partial-when-NA behavior), `reconciliation.py`
  (writes `ReconciliationIssue` rows), `anomalies.py`, `forecasting.py`.
- Routers: datasets/indicators/dashboard/activity/expenditure/analytics/
  forecast per Section 11.
- Tests per calculation, edge cases, and the exact real-value checks.

Checkpoint completed 2026-08-01. Activity, expenditure, and forecast APIs now include summaries, source metadata, composition ratios, anomaly results, missing-data warnings, strict forecast validation, chronological backtesting, and explicit experimental-forecast disclaimers.

### Phase 3 — Assistant + reports (complete)
- Deterministic AR/FR assistant covering the Section 15 example questions,
  built on Phase 2 services.
- `POST /api/assistant/query`.
- ReportLab bilingual PDF + CSV export, `POST /api/reports/generate`.
- Tests: the Arabic and French example-question sets.

Completed 2026-08-01. The assistant is deterministic and database-grounded, returns calculation/source provenance, and refuses unsupported information. Reports support French/Arabic PDF (with Arabic shaping and RTL text) and UTF-8 CSV for selected indicators and periods.

### Phase 4 — Frontend foundation (complete)
- Vite + React + TS + Tailwind, Router, i18next, language/direction
  context, Axios client, layout/nav, error boundary, Home page.

Completed 2026-08-01. The responsive Home experience, shared navigation,
French/Arabic language persistence, document-level RTL/LTR switching,
typed Axios foundation, error boundary, accessible Phase 5 placeholders,
component tests, lint checks, and production build all pass.

### Phase 5 — Frontend feature pages
- Overview Dashboard, Activity Analysis, Mining Analysis, Expenditure
  Analysis, Compare, Data Reconciliation, Alerts, Forecast, Economic
  Assistant, Reports, Data Catalogue — per Section 12.

### Phase 6 — Testing, docs, polish
- Frontend tests (Vitest + Testing Library).
- Full README, `docs/METHODOLOGY.md`, `docs/DATA_QUALITY.md`,
  `docs/DEMO_SCRIPT.md`, `run-dev.ps1`.
- Full pass against the Section 21 acceptance criteria.

## 2026-08-01 continuation checkpoints

- Checkpoint A: stress-test accounting, hierarchy/alias conflict prevention,
  ranking, dependency, concentration, deterministic recommendations and
  alternative-sector ranking implemented.
- Checkpoints B/C: real-API Dashboard, Activity, Mining, Expenditure, Compare,
  Reconciliation, Alerts, Forecast, Assistant, Stress Test, Recommendations,
  Reports and Data Catalogue interfaces implemented.
- Production values are never hard-coded; missing observations remain explicit.

## Working agreement

- Report progress and test results at each phase checkpoint; the real-value
  assertions in Phase 1 are the load-bearing check that the whole pipeline
  is trustworthy, so they gate everything after.
- No fabricated economic values are ever shown in the running app.
