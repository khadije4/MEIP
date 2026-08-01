# MEIP Methodology

## Sector stress testing

For sector value `S`, activity-side GDP `Y`, and shock from 0 to 1, direct
loss is `S × shock`, simulated GDP is `Y − direct loss`, and direct impact is
`direct loss / Y × 100`. This current-price accounting scenario is not a
causal macroeconomic model and estimates no indirect employment, supplier,
trade, consumption or fiscal effects. Parent/child and alias/canonical
combinations are rejected before multi-sector addition.

Dependency is `sector / activity GDP × 100`. Nominal-growth contribution is
`(sector_t − sector_t-1) / activity_GDP_t-1 × 100`; it does not prove
causality. Experimental accounting concentration sums squared decimal shares
for a mutually exclusive group. Platform labels are relatively diversified
below 0.15, moderately concentrated below 0.25, and highly concentrated from
0.25. This is not a complete resilience measure.

## Deterministic recommendations

Base direct-impact thresholds are low below 2%, moderate from 2% to below 5%,
high from 5% to below 10%, and critical at 10% or more. Several corroborating
factors—duration, combined shocks, sector share, volatility, recent negative
direction, shock size and concentration—may raise risk one level. These are
experimental platform rules, not government standards.

Alternative sectors balance GDP share, historical/recent growth, volatility
and completeness rather than growth alone. The ranking does not measure jobs,
profitability, investment cost, environmental feasibility or regional
feasibility.

MEIP analyses annual Mauritanian national accounts at current prices, in millions of MRU, from ANSADE/CN for 1998–2024. Results describe nominal evolution, not real growth, inflation, per-capita output, or official forecasts.

Activity-side GDP is the denominator for sector contributions. Expenditure-side GDP is the denominator for consumption, investment, export, import, and trade-openness ratios. The two GDP series remain distinct. Missing observations remain missing; aliases and parent aggregates are excluded from additive rankings.

Annual growth uses only calendar-consecutive valid observations. CAGR uses elapsed calendar years. Ratios return unavailable when an input is missing or the denominator is zero. Accounting checks return `valid`, `valid_with_rounding`, `partial`, or `discrepancy`; a missing expenditure component produces a partial result.

Anomalies use annual growth, median, median absolute deviation, and robust Z-score. Isolation Forest is a deterministic secondary signal only. Forecast candidates are naive last value, naive drift, linear trend, Holt, and ARIMA when available. Selection uses chronological rolling-origin backtesting against the naive baseline. Forecasts require eight observations, cover one to three years, and are experimental estimates rather than official ANSADE statistics.
