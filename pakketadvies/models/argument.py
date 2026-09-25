"""Argument and dossier DTOs (no I/O)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

__all__ = (
    "SCHEMA_VERSION",
    "Argument",
    "AuthorityMeta",
    "Codebook",
    "Dossier",
    "SourceDoc",
)

SCHEMA_VERSION = 1


class Argument(BaseModel):
    schema_version: int = SCHEMA_VERSION
    authority: str
    id: str
    native_id: str
    dossier_id: str
    advice_date: str | None = None
    substance: str = ""
    brand: str = ""
    indication: str = ""
    line: str = ""
    criterion: str = ""
    theme: str = ""
    weight: str = ""
    position: str = ""
    text: str = ""
    precedent: str = ""
    source_label: str = ""
    source_locator: str = ""
    checked: bool = False
    extra: dict[str, Any] = Field(default_factory=dict)


class Dossier(BaseModel):
    schema_version: int = SCHEMA_VERSION
    authority: str
    id: str
    native_id: str
    advice_date: str | None = None
    substance: str = ""
    brand: str = ""
    indication: str = ""
    line: str = ""
    status: str = ""
    title: str = ""
    extra: dict[str, Any] = Field(default_factory=dict)


class SourceDoc(BaseModel):
    schema_version: int = SCHEMA_VERSION
    authority: str
    id: str
    dossier_id: str
    path: str = ""
    text: str = ""


class Codebook(BaseModel):
    authority: str
    weight_order: list[str]


class AuthorityMeta(BaseModel):
    id: str
    name: str
    as_of: str
    schema_version: int = SCHEMA_VERSION
    reserved: bool = False
