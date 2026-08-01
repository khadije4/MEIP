"""Idempotent import of the two fixed national-accounts workbooks into the
database, plus a JSON-serializable validation report and cleaned CSV
output under data/processed/ for provenance. Used by both the API
(POST /api/data/import) and scripts/import_national_accounts.py."""

from __future__ import annotations

import csv
import json
import datetime as dt
from pathlib import Path

from sqlalchemy.orm import Session

from app.analytics.reconciliation import compute_gdp_reconciliation
from app.ingestion.datasets_config import DATASET_SPECS, DatasetImportSpec
from app.ingestion.seed import seed_indicators
from app.ingestion.workbook_reader import WorkbookReadResult, read_workbook
from app.models.dataset import Dataset
from app.models.economic_value import EconomicValue
from app.models.indicator import Indicator

UNIT_MILLIONS_MRU = "Millions de MRU"


def _upsert_dataset(db: Session, spec: DatasetImportSpec, result: WorkbookReadResult) -> Dataset:
    dataset = db.query(Dataset).filter(Dataset.code == spec.code).first()
    if dataset is None:
        dataset = Dataset(code=spec.code)
        db.add(dataset)

    dataset.name_fr = spec.name_fr
    dataset.name_ar = spec.name_ar
    dataset.original_filename = spec.filename
    dataset.worksheet_name = result.worksheet_name
    dataset.table_number = spec.table_number
    dataset.source_name = "ANSADE/CN"
    dataset.unit = UNIT_MILLIONS_MRU
    dataset.price_type = "current"
    dataset.frequency = "annual"
    dataset.geographic_level = "national"
    dataset.start_year = result.start_year
    dataset.end_year = result.end_year
    dataset.imported_at = dt.datetime.utcnow()
    dataset.validation_status = "imported"
    db.flush()
    return dataset


def _upsert_values(db: Session, dataset: Dataset, result: WorkbookReadResult) -> dict[str, Indicator]:
    indicator_cache: dict[str, Indicator] = {}
    for row in result.rows:
        indicator = db.query(Indicator).filter(Indicator.code == row.spec.code).first()
        if indicator is None:
            raise RuntimeError(
                f"Indicator '{row.spec.code}' not found — run seed_indicators() before import."
            )
        # Capture the real, as-observed raw label for provenance (may
        # include source typos/indentation that the hand-written taxonomy
        # fragment deliberately does not reproduce).
        indicator.original_label = row.raw_label
        indicator_cache[row.spec.code] = indicator

        for cell in row.cells:
            existing = (
                db.query(EconomicValue)
                .filter(
                    EconomicValue.dataset_id == dataset.id,
                    EconomicValue.indicator_id == indicator.id,
                    EconomicValue.year == cell.year,
                )
                .first()
            )
            if existing is None:
                existing = EconomicValue(
                    dataset_id=dataset.id, indicator_id=indicator.id, year=cell.year
                )
                db.add(existing)

            existing.value = cell.value
            existing.original_value = cell.original_value
            existing.is_missing = cell.is_missing
            existing.quality_flag = cell.quality_flag
            existing.source_row = row.source_row
            existing.source_column = cell.column_letter

    db.commit()
    return indicator_cache


def import_dataset(db: Session, spec: DatasetImportSpec, raw_dir: Path) -> tuple[Dataset, WorkbookReadResult]:
    file_path = raw_dir / spec.filename
    if not file_path.exists():
        raise FileNotFoundError(f"Expected source file not found: {file_path}")

    result = read_workbook(file_path, spec.sheet_name, spec.row_specs)
    dataset = _upsert_dataset(db, spec, result)
    _upsert_values(db, dataset, result)
    return dataset, result


def import_all(db: Session, raw_dir: Path, processed_dir: Path) -> dict:
    """Seeds the indicator taxonomy, imports both fixed workbooks
    idempotently, writes cleaned CSVs to processed_dir, and returns a
    JSON-serializable validation report."""
    seed_created = seed_indicators(db)

    report: dict = {
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "indicators_seeded_new": seed_created,
        "datasets": [],
    }

    for spec in DATASET_SPECS:
        dataset, result = import_dataset(db, spec, raw_dir)

        total_cells = sum(len(r.cells) for r in result.rows)
        missing_cells = sum(1 for r in result.rows for c in r.cells if c.is_missing)
        nonnumeric_cells = sum(
            1 for r in result.rows for c in r.cells if c.quality_flag == "nonnumeric"
        )
        label_mismatches = [r.spec.code for r in result.rows if not r.label_matches_expected]

        report["datasets"].append(
            {
                "code": spec.code,
                "table_number": spec.table_number,
                "filename": spec.filename,
                "worksheet_name": result.worksheet_name,
                "start_year": result.start_year,
                "end_year": result.end_year,
                "indicator_count": len(result.rows),
                "observation_count": total_cells,
                "missing_count": missing_cells,
                "nonnumeric_count": nonnumeric_cells,
                "completeness_pct": round(100 * (1 - missing_cells / total_cells), 2)
                if total_cells
                else 0.0,
                "label_mismatches": label_mismatches,
                "warnings": result.warnings,
            }
        )

        _write_processed_csv(processed_dir, spec.code, result)

    reconciliation_rows = compute_gdp_reconciliation(db)
    report["reconciliation_rows"] = reconciliation_rows

    report_path = Path(processed_dir) / "validation_report.json"
    Path(processed_dir).mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return report


def _write_processed_csv(processed_dir: Path, dataset_code: str, result: WorkbookReadResult) -> None:
    out_dir = Path(processed_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{dataset_code}.csv"
    fieldnames = [
        "year", "indicator_code", "indicator_name_fr", "value", "unit",
        "quality_flag", "source_row", "source_column",
    ]
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in result.rows:
            for cell in row.cells:
                writer.writerow(
                    {
                        "year": cell.year,
                        "indicator_code": row.spec.code,
                        "indicator_name_fr": row.spec.name_fr,
                        "value": cell.value if cell.value is not None else "",
                        "unit": UNIT_MILLIONS_MRU,
                        "quality_flag": cell.quality_flag,
                        "source_row": row.source_row,
                        "source_column": cell.column_letter,
                    }
                )
