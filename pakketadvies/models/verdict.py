"""Cite verdict DTOs (no I/O)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from pakketadvies.models.argument import Argument

__all__ = (
    "CiteReport",
    "CiteRow",
    "Verdict",
)

Verdict = Literal["cite", "thin", "none", "ambiguous"]


class CiteRow(BaseModel):
    id: str
    dossier_id: str
    advice_date: str | None = None
    substance: str = ""
    brand: str = ""
    theme: str = ""
    weight: str = ""
    text: str = ""
    precedent: str = ""
    source_label: str = ""
    source_locator: str = ""
    authority: str = ""

    @classmethod
    def from_argument(cls, arg: Argument) -> CiteRow:
        return cls(
            id=arg.id,
            dossier_id=arg.dossier_id,
            advice_date=arg.advice_date,
            substance=arg.substance,
            brand=arg.brand,
            theme=arg.theme,
            weight=arg.weight,
            text=arg.text,
            precedent=arg.precedent,
            source_label=arg.source_label,
            source_locator=arg.source_locator,
            authority=arg.authority,
        )


class CiteReport(BaseModel):
    verdict: Verdict
    why: str
    as_of: str
    authority: str | None = None
    preset: str = "FIRST_USE"
    shortlist: list[CiteRow] = Field(default_factory=list)
    candidates: list[CiteRow] = Field(default_factory=list)
