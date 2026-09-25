"""Shared JSON envelope for CLI and MCP."""

from __future__ import annotations

from typing import Any

from pakketadvies.core.errors import classify_error
from pakketadvies.core.exceptions import PakketAmbiguousError

__all__ = (
    "API_VERSION",
    "dump_model",
    "error_payload",
    "success_payload",
)

API_VERSION = 1


def success_payload(data: Any) -> dict[str, Any]:
    return {"ok": True, "api_version": API_VERSION, "data": data}


def error_payload(exc: BaseException) -> dict[str, Any]:
    classified = classify_error(exc)
    payload: dict[str, Any] = {
        "ok": False,
        "api_version": API_VERSION,
        "error": str(exc),
        **classified.as_fields(),
    }
    if isinstance(exc, PakketAmbiguousError):
        payload["candidates"] = [c.model_dump(mode="json") for c in exc.candidates]
    return payload


def dump_model(model: Any) -> Any:
    return model.model_dump(mode="json")
