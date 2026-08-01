# MEIP Data Quality

Source workbooks remain unchanged in `data/raw/`. Import normalizes decimal commas, preserves labels and cell provenance, and stores literal `NA` as missing rather than zero.

- `agriculture_fishing_forestry` is an alias of `primary_sector` and is not counted separately.
- Petroleum/gas and net acquisition of valuables contain unavailable years; APIs warn instead of zero-filling.
- Activity and expenditure GDP remain separate. In 2018 they are 266,637.60 and 262,320.02 million MRU, a difference of 4,317.58.
- In 2024, the three main sectors total factor-cost GDP of 395,829.20; factor-cost GDP plus net taxes equals market-price GDP of 429,701.30 million MRU.
- Current-price data cannot support claims about real GDP, inflation, unemployment, poverty, per-capita, or regional GDP.

Partial accounting identities never receive an exact-reconciliation claim.
