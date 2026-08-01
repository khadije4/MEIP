"""Shared response envelopes for structured API errors."""

from __future__ import annotations

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message_en: str
    message_ar: str | None = None
    message_fr: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
