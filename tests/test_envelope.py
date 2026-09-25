"""Error classification and JSON envelope contract."""

from __future__ import annotations

from pakketadvies.core.envelope import error_payload
from pakketadvies.core.errors import classify_error
from pakketadvies.core.exceptions import (
    PakketAmbiguousError,
    PakketIncompleteError,
    PakketInvalidError,
    PakketNotFoundError,
)
from pakketadvies.models.verdict import CiteRow


def test_classify_ambiguous() -> None:
    c = classify_error(
        PakketAmbiguousError("tie", candidates=[CiteRow(id="a", dossier_id="d")])
    )
    assert c.error_type == "ambiguous"
    assert c.retryable is False


def test_classify_not_found_invalid_incomplete() -> None:
    assert classify_error(PakketNotFoundError("x")).error_type == "not_found"
    assert classify_error(PakketInvalidError("x")).error_type == "invalid"
    assert classify_error(PakketIncompleteError("x")).error_type == "incomplete"
    assert classify_error(ValueError("x")).error_type == "invalid"


def test_error_payload_ambiguous_includes_candidates() -> None:
    row = CiteRow(id="zin:ARG-1", dossier_id="INT-1", authority="zin")
    payload = error_payload(PakketAmbiguousError("tie", candidates=[row]))
    assert payload["ok"] is False
    assert payload["api_version"] == 1
    assert payload["error_type"] == "ambiguous"
    assert payload["candidates"] == [row.model_dump(mode="json")]


def test_error_payload_not_found() -> None:
    payload = error_payload(PakketNotFoundError("missing"))
    assert payload["ok"] is False
    assert payload["error_type"] == "not_found"
    assert "candidates" not in payload


def test_error_payload_value_error() -> None:
    payload = error_payload(ValueError("bad"))
    assert payload["error_type"] == "invalid"
    assert payload["error"] == "bad"
