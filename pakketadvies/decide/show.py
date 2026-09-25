"""Resolve one argument or dossier by id (pure over loaded rows)."""

from __future__ import annotations

from pakketadvies.core.exceptions import (
    PakketAmbiguousError,
    PakketInvalidError,
    PakketNotFoundError,
)
from pakketadvies.models.argument import Argument, Dossier
from pakketadvies.models.verdict import CiteRow

__all__ = ("parse_id", "show_argument", "show_dossier")


def parse_id(raw: str) -> tuple[str | None, str]:
    text = raw.strip()
    if not text:
        raise PakketInvalidError("id must not be empty")
    if ":" in text:
        auth, native = text.split(":", 1)
        if not auth or not native:
            raise PakketInvalidError(f"invalid id: {raw}")
        return auth.casefold(), native
    return None, text


def _arg_matches(arg: Argument, authority: str | None, native: str) -> bool:
    if arg.native_id == native or arg.id == native or arg.id.endswith(":" + native):
        if authority is None or arg.authority == authority:
            return True
    return False


def _dos_matches(dos: Dossier, authority: str | None, native: str) -> bool:
    if dos.native_id == native or dos.id == native or dos.id.endswith(":" + native):
        if authority is None or dos.authority == authority:
            return True
    return False


def show_argument(
    rows: list[Argument],
    raw_id: str,
) -> Argument:
    authority, native = parse_id(raw_id)
    hits = [a for a in rows if _arg_matches(a, authority, native)]
    if not hits:
        raise PakketNotFoundError(f"argument not found: {raw_id}")
    if len(hits) > 1:
        raise PakketAmbiguousError(
            f"ambiguous argument id: {raw_id}",
            candidates=[CiteRow.from_argument(a) for a in hits],
        )
    return hits[0]


def show_dossier(
    rows: list[Dossier],
    raw_id: str,
) -> Dossier:
    authority, native = parse_id(raw_id)
    hits = [d for d in rows if _dos_matches(d, authority, native)]
    if not hits:
        raise PakketNotFoundError(f"dossier not found: {raw_id}")
    if len(hits) > 1:
        raise PakketAmbiguousError(
            f"ambiguous dossier id: {raw_id}",
            candidates=[
                CiteRow(
                    id=d.id,
                    dossier_id=d.native_id,
                    advice_date=d.advice_date,
                    substance=d.substance,
                    brand=d.brand,
                    authority=d.authority,
                    text=d.title,
                )
                for d in hits
            ],
        )
    return hits[0]
