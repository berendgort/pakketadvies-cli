"""Golden FIRST_USE cite policy."""

from __future__ import annotations

import pytest

from pakketadvies.core.exceptions import PakketAmbiguousError
from pakketadvies.decide.cite import cite
from pakketadvies.models.argument import Argument, AuthorityMeta, Codebook

META = AuthorityMeta(id="zin", name="ZIN", as_of="2026-09-24")
CODE = Codebook(
    authority="zin",
    weight_order=["Doorslaggevend", "Ondersteunend", "Zijdelings"],
)


def _arg(
    native: str,
    *,
    date: str | None,
    weight: str,
    text: str,
    dossier: str = "INT-1",
    theme: str = "Indirecte vergelijking / NMA",
) -> Argument:
    return Argument(
        authority="zin",
        id=f"zin:{native}",
        native_id=native,
        dossier_id=dossier,
        advice_date=date,
        substance="drug",
        theme=theme,
        weight=weight,
        text=text,
        precedent=text,
    )


def test_cite_earliest_doorslaggevend() -> None:
    rows = [
        _arg("ARG-2", date="2024-06-01", weight="Doorslaggevend", text="extern controlecohort"),
        _arg("ARG-1", date="2020-01-15", weight="Doorslaggevend", text="extern controlecohort"),
        _arg("ARG-3", date="2019-01-01", weight="Ondersteunend", text="extern controlecohort"),
    ]
    report = cite(rows, CODE, META, "extern controlecohort")
    assert report.verdict == "cite"
    assert report.shortlist[0].id == "zin:ARG-1"
    assert [r.id for r in report.shortlist] == ["zin:ARG-1", "zin:ARG-2", "zin:ARG-3"]


def test_thin_when_only_weak_weight() -> None:
    rows = [
        _arg("ARG-9", date="2021-01-01", weight="Zijdelings", text="extern controlecohort"),
    ]
    report = cite(rows, CODE, META, "extern")
    assert report.verdict == "thin"
    assert report.shortlist[0].id == "zin:ARG-9"


def test_none_when_no_match() -> None:
    rows = [_arg("ARG-1", date="2020-01-01", weight="Doorslaggevend", text="other topic")]
    report = cite(rows, CODE, META, "extern controlecohort")
    assert report.verdict == "none"
    assert report.shortlist == []


def test_tie_on_same_date_is_ambiguous() -> None:
    rows = [
        _arg("ARG-1", date="2020-01-01", weight="Doorslaggevend", text="nma", dossier="INT-1"),
        _arg("ARG-2", date="2020-01-01", weight="Doorslaggevend", text="nma", dossier="INT-2"),
    ]
    with pytest.raises(PakketAmbiguousError) as exc:
        cite(rows, CODE, META, "nma")
    assert len(exc.value.candidates) == 2


def test_missing_date_cannot_win_cite() -> None:
    rows = [
        _arg("ARG-1", date=None, weight="Doorslaggevend", text="nma"),
        _arg("ARG-2", date="2021-01-01", weight="Ondersteunend", text="nma"),
    ]
    report = cite(rows, CODE, META, "nma")
    assert report.verdict == "thin"
    assert report.shortlist[0].id == "zin:ARG-1"
    assert report.shortlist[0].advice_date is None
