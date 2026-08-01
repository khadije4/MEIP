"""Seed the Indicator table from the canonical taxonomy (idempotent)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.ingestion.taxonomy import all_rows
from app.models.indicator import Indicator

UNIT_MILLIONS_MRU = "Millions de MRU"


def seed_indicators(db: Session) -> int:
    existing = {i.code: i for i in db.query(Indicator).all()}
    created = 0

    for spec in all_rows():
        row = existing.get(spec.code)
        if row is None:
            row = Indicator(
                code=spec.code,
                original_label=spec.name_fr,
                name_fr=spec.name_fr,
                name_ar=spec.name_ar,
                category=spec.category,
                hierarchy_level=spec.hierarchy_level,
                unit=UNIT_MILLIONS_MRU,
                source_side=spec.source_side,
                is_aggregate=spec.is_aggregate,
                is_alias=spec.is_alias,
            )
            db.add(row)
            existing[spec.code] = row
            created += 1
        else:
            row.name_fr = spec.name_fr
            row.name_ar = spec.name_ar
            row.category = spec.category
            row.hierarchy_level = spec.hierarchy_level
            row.source_side = spec.source_side
            row.is_aggregate = spec.is_aggregate
            row.is_alias = spec.is_alias
    db.flush()

    for spec in all_rows():
        row = existing[spec.code]
        if spec.parent_code is not None:
            row.parent_indicator_id = existing[spec.parent_code].id
        if spec.alias_of_code is not None:
            row.alias_of_indicator_id = existing[spec.alias_of_code].id
    db.commit()
    return created
