"""Pure filter and rank contract."""

from __future__ import annotations

import pytest

from pakketadvies.decide.rank import filter_arguments, rank_arguments, weight_rank
from pakketadvies.models.argument import Argument, Codebook

CODE = Codebook(
    authority="zin",
    weight_order=["Doorslaggevend", "Ondersteunend", "Zijdelings"],
)


def _arg(
    native: str,
    *,
    text: str = "nma",
    weight: str = "Doorslaggevend",
    date: str | None = "2020-01-01",
    theme: str = "Indirecte vergelijking / NMA",
    line: str = "1e lijn",
    traject: str = "Intramuraal",
) -> Argument:
    return Argument(
        authority="zin",
        id=f"zin:{native}",
        native_id=native,
        dossier_id="INT-1",
        advice_date=date,
        substance="drug",
        theme=theme,
        weight=weight,
        text=text,
        precedent=text,
        line=line,
        extra={"traject": traject},
    )


def test_empty_query_raises() -> None:
    with pytest.raises(ValueError, match="query must not be empty"):
        filter_arguments([_arg("ARG-1")], "  ")


def test_case_insensitive_substring() -> None:
    rows = [_arg("ARG-1", text="Extern ControleCohort accepted")]
    hits = filter_arguments(rows, "extern controlecohort")
    assert [a.id for a in hits] == ["zin:ARG-1"]


def test_theme_line_traject_filters() -> None:
    rows = [
        _arg("ARG-1", theme="Prijs", line="1e lijn", traject="Intramuraal"),
        _arg("ARG-2", theme="Prijs", line="2e lijn", traject="Intramuraal"),
        _arg("ARG-3", theme="Prijs", line="1e lijn", traject="GVS"),
    ]
    by_theme = filter_arguments(rows, "drug", theme="Prijs")
    assert {a.native_id for a in by_theme} == {"ARG-1", "ARG-2", "ARG-3"}
    by_line = filter_arguments(rows, "drug", line="2e")
    assert [a.native_id for a in by_line] == ["ARG-2"]
    by_traject = filter_arguments(rows, "drug", traject="gvs")
    assert [a.native_id for a in by_traject] == ["ARG-3"]


def test_unknown_weight_sorts_after_codebook() -> None:
    rows = [
        _arg("ARG-2", weight="Mystery", date="2018-01-01"),
        _arg("ARG-1", weight="Ondersteunend", date="2022-01-01"),
    ]
    ranked = rank_arguments(rows, CODE)
    assert [a.id for a in ranked] == ["zin:ARG-1", "zin:ARG-2"]
    assert weight_rank("Mystery", CODE) == len(CODE.weight_order)


def test_missing_date_sorts_after_real_dates() -> None:
    rows = [
        _arg("ARG-2", date=None, weight="Doorslaggevend"),
        _arg("ARG-1", date="2021-06-01", weight="Doorslaggevend"),
    ]
    ranked = rank_arguments(rows, CODE)
    assert [a.id for a in ranked] == ["zin:ARG-1", "zin:ARG-2"]


def test_id_is_final_tiebreak() -> None:
    rows = [
        _arg("ARG-2", date="2020-01-01", weight="Doorslaggevend"),
        _arg("ARG-1", date="2020-01-01", weight="Doorslaggevend"),
    ]
    ranked = rank_arguments(rows, CODE)
    assert [a.id for a in ranked] == ["zin:ARG-1", "zin:ARG-2"]
