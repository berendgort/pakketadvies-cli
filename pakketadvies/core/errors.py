"""Map exceptions to stable error_type + retryable."""

from __future__ import annotations

from dataclasses import dataclass

from pakketadvies.core.exceptions import (
    PakketAmbiguousError,
    PakketIncompleteError,
    PakketInvalidError,
    PakketNotFoundError,
)

__all__ = ("ErrorClassification", "classify_error")


@dataclass(frozen=True)
class ErrorClassification:
    error_type: str
    retryable: bool

    def as_fields(self) -> dict[str, object]:
        return {
            "error_type": self.error_type,
            "retryable": self.retryable,
        }


def classify_error(exc: BaseException) -> ErrorClassification:
    if isinstance(exc, PakketAmbiguousError):
        return ErrorClassification("ambiguous", retryable=False)
    if isinstance(exc, PakketNotFoundError):
        return ErrorClassification("not_found", retryable=False)
    if isinstance(exc, PakketIncompleteError):
        return ErrorClassification("incomplete", retryable=False)
    if isinstance(exc, PakketInvalidError):
        return ErrorClassification("invalid", retryable=False)
    if isinstance(exc, ValueError):
        return ErrorClassification("invalid", retryable=False)
    if isinstance(exc, PermissionError):
        return ErrorClassification("incomplete", retryable=True)
    if isinstance(exc, OSError):
        # Locked or busy local file can succeed on retry.
        return ErrorClassification("incomplete", retryable=True)
    return ErrorClassification("invalid", retryable=False)
