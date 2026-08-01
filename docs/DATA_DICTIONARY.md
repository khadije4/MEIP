# MEIP Data Dictionary

Canonical indicator taxonomy for the two real ANSADE/CN source files. This
is the single source of truth used both to seed the `indicators` table and
to map raw row labels during ingestion. Verified directly against the
actual workbook contents (`data/raw/comptes_nationaux_4.9.1.xlsx`,
`data/raw/comptes_nationaux_4.9.2.xlsx`) on 2026-08-01.

## Source files

| file | sheet (exact name) | title | period | unit | price basis |
|---|---|---|---|---|---|
| `comptes_nationaux_4.9.1.xlsx` | `Emplos du PIB courant ` (note: source typo "Emplos", trailing space — preserved verbatim, matched trimmed) | Tableau 4.9.1 : Évolution des emplois du PIB à prix courants | 1998–2024 | Millions de MRU | current (nominal) prices |
| `comptes_nationaux_4.9.2.xlsx` | `PIB Courant (2)` | Tableau 4.9.2 : PIB courant par branche d'activité | 1998–2024 | Millions de MRU | current (nominal) prices |

Both files store years across columns (row 3, 1998→2024, left→right) and
indicators down rows (column A), i.e. **wide-form, transposed**: year is a
column header repeated across the sheet, not a single "year column" as in a
typical long-form-ready table. The importer reads this layout directly
(see `docs/ARCHITECTURE.md`).

Row 1 is the table title, row 2 blank, row 3 is the year header, and the
last populated row is `Source : ANSADE/CN`. Numeric cells are stored as
**text** using a French decimal comma (e.g. `"429701,30"`) with no
thousands separators in either file. The literal string `"NA"` marks a
missing observation.

## Indicator labels: raw formatting

Row labels in `comptes_nationaux_4.9.2.xlsx` are indented with repeated
**non-breaking spaces (U+00A0)** in multiples of 4, and prefixed with
inconsistent numbering (e.g. `"2. 1"`, `"2.2."`, `"2. 2.1"`). Indent depth
(nbsp-count ÷ 4) reflects the real hierarchy depth and was verified to be
internally consistent: child rows sum exactly to their parent row's values
in every year. `comptes_nationaux_4.9.1.xlsx` labels have no indentation
(flat list). The importer strips numbering/indentation to produce a clean
`name_fr`, while `original_label` preserves the raw cell text verbatim
(including nbsp and numbering) for provenance.

## Expenditure-side indicators (source: 4.9.1, `source_side="expenditure"`)

| code | raw label (as in file) | category | parent | notes |
|---|---|---|---|---|
| `imports` | Importation | flow | — | subtracted in the GDP identity |
| `gdp_expenditure` | PIB | aggregate | — | GDP by expenditure/use |
| `final_consumption` | Consommation Finale | aggregate | — | = household + government + ISBLM |
| `household_final_consumption` | Consommation Finale Ménage | subcomponent | `final_consumption` | = nonmarket + market |
| `household_nonmarket_consumption` | Consommation Finale Ménage non marchande | subcomponent | `household_final_consumption` | |
| `household_market_consumption` | Consommation Finale Ménage marchande | subcomponent | `household_final_consumption` | |
| `government_final_consumption` | Consommation Finale des Administations Publiques *(source spelling; "Administrations" is the corrected display label)* | subcomponent | `final_consumption` | |
| `isblm_final_consumption` | Consommation Finale des ISBLM | subcomponent | `final_consumption` | |
| `gross_fixed_capital_formation` | Formation brut de capital fixe *(source spelling; "brute" is the corrected display label)* | flow | — | |
| `inventory_changes` | Variations de stock | flow | — | can be negative |
| `net_acquisition_valuables` | Acquisitions nettes en objets de valeur | flow | — | **mostly `NA`** (1998–2016, 2020); real values 2017–2019; `0,00` 2021–2024. Never assumed zero when NA — see `docs/METHODOLOGY.md`. |
| `exports` | Exportation | flow | — | |

Accounting identity (verified exactly for 2024, where `net_acquisition_valuables = 0`):
`final_consumption + gross_fixed_capital_formation + inventory_changes + net_acquisition_valuables + exports − imports = gdp_expenditure`

## Activity-side indicators (source: 4.9.2, `source_side="activity"`)

| code | raw label | hierarchy_level | parent | is_alias | notes |
|---|---|---|---|---|---|
| `primary_sector` | Secteur primaire | 1 | — | no | |
| `agriculture_fishing_forestry` | 1. Agriculture, pêche, exploitation forestière | 2 | `primary_sector` | **yes**, alias of `primary_sector` | value is identical to `primary_sector` in every year — same node, not an additional component; excluded from sums/rankings to avoid double counting |
| `agriculture_forestry` | 1. 1 Agriculture, Sylviculture et Exploit. Forestière | 3 | `agriculture_fishing_forestry` | no | |
| `livestock_hunting` | 1. 2 Elevage et chasse | 3 | `agriculture_fishing_forestry` | no | |
| `fishing` | 1. 3 Pêche | 3 | `agriculture_fishing_forestry` | no | |
| `secondary_sector` | Secteur secondaire | 1 | — | no | = extractive + manufacturing + construction |
| `extractive_activities` | 2. Activités extractives | 2 | `secondary_sector` | no | = oil/gas + non-oil |
| `oil_gas_extraction` | 2. 1 Extraction de produits pétroliers et gaziers | 3 | `extractive_activities` | no | zero most years; `NA` in 2023 |
| `non_oil_extractive_activities` | 2.2. Industries extractives autre que produits petroliers et gaziers | 3 | `extractive_activities` | no | = metallic minerals + other |
| `metallic_mineral_extraction` | 2. 2.1 Extraction des minerais métaliques | 4 | `non_oil_extractive_activities` | no | = SNIM iron + gold/copper |
| `snim_iron` | Fer_SNIM | 5 | `metallic_mineral_extraction` | no | |
| `gold_copper` | Or et Cuivre | 5 | `metallic_mineral_extraction` | no | |
| `other_extractive_activities` | 2. 2.2 Autres activités extractives | 4 | `non_oil_extractive_activities` | no | |
| `manufacturing` | 3. Activités manufacturières | 2 | `secondary_sector` | no | = manufacturing-excl-water/elec + water/elec |
| `manufacturing_excluding_water_electricity` | 3. 1 Activités manufacturières hors eau et éléctricité | 3 | `manufacturing` | no | |
| `water_electricity` | 3. 2 Production et distribution d'eau et d'électricité | 3 | `manufacturing` | no | |
| `construction_public_works` | 4. Bâtiment et travauxpublics | 2 | `secondary_sector` | no | |
| `tertiary_sector` | Secteur tertiaire | 1 | — | no | = transport/info-comm + commerce + other services + public admin |
| `transport_information_communication` | 5. Transport, Information et communication | 2 | `tertiary_sector` | no | = transport + info/comm |
| `transport` | 5. 1 Transport | 3 | `transport_information_communication` | no | |
| `information_communication` | 5. 2 Information et communication | 3 | `transport_information_communication` | no | |
| `commerce` | 8. Commerce | 2 | `tertiary_sector` | no | |
| `other_services` | 9. Autres services | 2 | `tertiary_sector` | no | |
| `public_administration` | 10. Administrations publiques | 2 | `tertiary_sector` | no | |
| `gdp_factor_cost` | P.I.B. au cout des facteurs | 1 (aggregate) | — | no | = `primary_sector + secondary_sector + tertiary_sector` |
| `net_taxes_products` | Taxes nettes sur les produits | 1 (aggregate) | — | no | |
| `gdp_activity_market_prices` | P.I.B. aux prix du marché | 1 (aggregate) | — | no | = `gdp_factor_cost + net_taxes_products` |

All parent/child sums above were checked exactly against the 2024 column
(and spot-checked against 2018) and hold to the reported decimal precision.

## Dual GDP series — reconciliation

`gdp_expenditure` (4.9.1, row "PIB") and `gdp_activity_market_prices`
(4.9.2, row "P.I.B. aux prix du marché") are **two independently reported
series that agree in most years but diverge in 2018–2020**:

| year | gdp_expenditure | gdp_activity_market_prices | absolute difference |
|---|---|---|---|
| 2018 | 262320.02 | 266637.60 | 4317.58 |
| 2019 | 289478.03 | 289665.50 | 187.47 |
| 2020 | 294388.90 | 307210.50 | 12821.60 |
| 2024 | 429701.30 | 429701.30 | 0.00 |

They are never merged or silently reconciled. Both are stored as distinct
indicators; the Reconciliation page and `ReconciliationIssue` table surface
the divergence explicitly. Sector-contribution calculations use
`gdp_activity_market_prices`; expenditure ratios (investment rate,
consumption rate, trade openness) use `gdp_expenditure`.

## Quality flags

- `ok` — numeric, parsed cleanly (French decimal comma → float).
- `missing` — source cell was the literal string `NA`; `value` stays
  `NULL`, never `0`.
- `nonnumeric` — cell had text that was neither a clean decimal-comma
  number nor `NA` (defensive case; not expected in the two known files).

## Units and prices

Both files are explicitly "Millions de MRU" at **current prices**
(nominal). The platform never computes or displays real (inflation
-adjusted) GDP, inflation, GDP per capita, unemployment, poverty, or
regional GDP — none of these are present in the source data, and every
growth/trend figure is labeled as nominal.
