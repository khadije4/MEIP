"""Fixed configuration for the two real ANSADE/CN source files. These are
the only two datasets the platform imports — see docs/DATA_DICTIONARY.md."""

from __future__ import annotations

from dataclasses import dataclass

from app.ingestion.taxonomy import ACTIVITY_ROWS, EXPENDITURE_ROWS, IndicatorRowSpec


@dataclass(frozen=True)
class DatasetImportSpec:
    table_number: str
    code: str
    filename: str
    sheet_name: str
    name_fr: str
    name_ar: str
    row_specs: tuple[IndicatorRowSpec, ...]


DATASET_SPECS: tuple[DatasetImportSpec, ...] = (
    DatasetImportSpec(
        table_number="4.9.1",
        code="gdp_by_expenditure",
        filename="comptes_nationaux_4.9.1.xlsx",
        sheet_name="Emplos du PIB courant ",
        name_fr="Évolution des emplois du PIB à prix courants",
        name_ar="تطور استخدامات الناتج المحلي الإجمالي بالأسعار الجارية",
        row_specs=EXPENDITURE_ROWS,
    ),
    DatasetImportSpec(
        table_number="4.9.2",
        code="gdp_by_activity",
        filename="comptes_nationaux_4.9.2.xlsx",
        sheet_name="PIB Courant (2)",
        name_fr="PIB courant par branche d'activité",
        name_ar="الناتج المحلي الإجمالي الجاري حسب فرع النشاط",
        row_specs=ACTIVITY_ROWS,
    ),
)
