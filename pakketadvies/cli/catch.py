"""CLI exception catch set."""

from __future__ import annotations

from pakketadvies.core.exceptions import PakketError

__all__ = ("CATCH",)

CATCH = (PakketError, ValueError, OSError)
