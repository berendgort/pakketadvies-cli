"""Shared error types."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pakketadvies.models.verdict import CiteRow

__all__ = (
    "PakketAmbiguousError",
    "PakketError",
    "PakketIncompleteError",
    "PakketInvalidError",
    "PakketNotFoundError",
)


class PakketError(Exception):
    """Base."""


class PakketNotFoundError(PakketError):
    pass


class PakketIncompleteError(PakketError):
    pass


class PakketInvalidError(PakketError):
    pass


class PakketAmbiguousError(PakketError):
    def __init__(self, message: str, *, candidates: list[CiteRow]) -> None:
        super().__init__(message)
        self.candidates = candidates
