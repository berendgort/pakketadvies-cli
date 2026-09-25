"""Cite verdict DTOs (no I/O)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from pakketadvies.models.argument import Argument, Dossier

__all__ = (
    "CiteReport",
    "CiteRow",
    "ShowArgument",
    "ShowDossier",
    "SourceRef",
    "Verdict",
)

Verdict = Literal["cite", "thin", "none", "ambiguous"]


class SourceRef(BaseModel):
    """Pointers and labeled text for one argument or dossier hit."""

    document: str = ""
    locator: str = ""
    url: str | None = None
    pdf: str | None = None
    extract: str | None = None
    quotation: str | None = None
    paraphrase: str | None = None
    verbatim: str | None = None
    note: str | None = None


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
    source: SourceRef | None = None

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


class ShowArgument(Argument):
    source: SourceRef


class ShowDossier(Dossier):
    source: SourceRef
