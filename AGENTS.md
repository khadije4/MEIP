# AGENTS.md

Guidance for AI coding agents (and humans) working in this repository.

## Ground rules

1. **Never invent economic values.** No feature may fabricate, guess, or
   silently zero-fill a number that isn't in the imported data. Missing data
   must render as "not available" / "unit not confirmed" states, never as 0
   or an interpolated guess (unless an explicit, documented imputation
   feature is built and clearly labeled).
2. **Demo/seed data must be labeled `DEMO DATA`** wherever it is defined and
   wherever it appears in the UI. It must never be presented as if it were
   the real Mauritanian national accounts data.
3. **Indicator codes are canonical.** `docs/DATA_DICTIONARY.md` is the single
   source of truth for indicator taxonomy. Do not invent new codes ad hoc —
   extend the dictionary and the ingestion alias table together.
4. **Time series are never shuffled.** Forecast backtesting and any
   train/test split must respect chronological order.
5. **Calculations live in `analytics/`**, as pure functions independent of
   the DB session, so they stay unit-testable. Routers and services call
   into `analytics/`; they do not reimplement math inline.
6. **Bilingual by construction.** Any user-facing string added to a model,
   schema, or generated report needs both `_ar` and `_fr` variants (or a
   `locales/*.json` key in the frontend). Don't add an English-only label to
   a page users will see.

## Repo layout

See `docs/ARCHITECTURE.md` for the full breakdown of `apps/api` and
`apps/web`, and `docs/DATA_DICTIONARY.md` for the indicator taxonomy and
normalization rules used by the ingestion pipeline.

## Workflow

- Follow `docs/IMPLEMENTATION_PLAN.md` phase by phase; run tests after each
  phase before moving to the next.
- Backend: `pytest` from `apps/api`. Frontend: `npm test` from `apps/web`
  (once scaffolded in Phase 4).
