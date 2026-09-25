"""Pure show / parse_id contract."""

from __future__ import annotations

import pytest

from pakketadvies.core.exceptions import (
    PakketAmbiguousError,
    PakketInvalidError,
    PakketNotFoundError,
)
from pakketadvies.decide.show import parse_id, show_argument, show_dossier
from pakketadvies.models.argument import Argument, Dossier


def _arg(native: str, *, authority: str = "zin") -> Argument:
    return Argument(
        authority=authority,
        id=f"{authority}:{native}",
        native_id=native,
        dossier_id="INT-1",
        advice_date="2020-01-01",
        substance="drug",
        theme="theme",
        weight="Doorslaggevend",
        text="text",
        precedent="precedent",
    )


def _dos(native: str, *, authority: str = "zin") -> Dossier:
    return Dossier(
        authority=authority,
        id=f"{authority}:{native}",
        native_id=native,
        advice_date="2020-01-01",
        substance="drug",
        title="title",
    )


def test_parse_id_bare_and_prefixed() -> None:
    assert parse_id("ARG-1") == (None, "ARG-1")
    assert parse_id("zin:ARG-1") == ("zin", "ARG-1")
    assert parse_id("ZIN:ARG-1") == ("zin", "ARG-1")


def test_parse_id_empty_and_invalid() -> None:
    with pytest.raises(PakketInvalidError):
        parse_id("  ")
    with pytest.raises(PakketInvalidError):
        parse_id(":ARG-1")
    with pytest.raises(PakketInvalidError):
        parse_id("zin:")


def test_show_argument_bare_and_prefixed() -> None:
    rows = [_arg("ARG-1")]
    assert show_argument(rows, "ARG-1").id == "zin:ARG-1"
    assert show_argument(rows, "zin:ARG-1").id == "zin:ARG-1"


def test_show_argument_not_found() -> None:
    with pytest.raises(PakketNotFoundError):
        show_argument([_arg("ARG-1")], "ARG-999")


def test_show_argument_ambiguous_same_native() -> None:
    rows = [_arg("ARG-1", authority="zin"), _arg("ARG-1", authority="nice")]
    with pytest.raises(PakketAmbiguousError) as exc:
        show_argument(rows, "ARG-1")
    assert {c.authority for c in exc.value.candidates} == {"zin", "nice"}


def test_show_dossier_ambiguous_same_native() -> None:
    rows = [_dos("INT-1", authority="zin"), _dos("INT-1", authority="nice")]
    with pytest.raises(PakketAmbiguousError) as exc:
        show_dossier(rows, "INT-1")
    assert len(exc.value.candidates) == 2


def test_show_dossier_not_found() -> None:
    with pytest.raises(PakketNotFoundError):
        show_dossier([_dos("INT-1")], "INT-999")
