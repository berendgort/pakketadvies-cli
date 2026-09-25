"""Pure FIRST_USE cite policy."""

from __future__ import annotations

from pakketadvies.core.exceptions import PakketAmbiguousError, PakketInvalidError
from pakketadvies.decide.rank import (
    filter_arguments,
    rank_arguments,
    top_weight,
)
from pakketadvies.models.argument import Argument, AuthorityMeta, Codebook
from pakketadvies.models.verdict import CiteReport, CiteRow

__all__ = ("SHORTLIST_CAP", "cite")

# Cap JSON/MCP shortlists (field-test: cite "GVS" returned 596 rows).
SHORTLIST_CAP = 25


def _rows(args: list[Argument]) -> list[CiteRow]:
    return [CiteRow.from_argument(a) for a in args]


def _cap_shortlist(ranked: list[Argument], why: str) -> tuple[list[CiteRow], str]:
    total = len(ranked)
    shortlist = _rows(ranked[:SHORTLIST_CAP])
    if total > SHORTLIST_CAP:
        why = f"{why} Showing top {SHORTLIST_CAP} of {total} matches."
    return shortlist, why


def cite(
    rows: list[Argument],
    codebook: Codebook,
    meta: AuthorityMeta,
    query: str,
    *,
    theme: str | None = None,
    line: str | None = None,
    traject: str | None = None,
) -> CiteReport:
    try:
        matched = filter_arguments(
            rows, query, theme=theme, line=line, traject=traject
        )
    except ValueError as exc:
        raise PakketInvalidError(str(exc)) from exc

    if not matched:
        return CiteReport(
            verdict="none",
            why="No argument matches that query.",
            as_of=meta.as_of,
            authority=meta.id,
            shortlist=[],
        )

    ranked = rank_arguments(matched, codebook)
    top = ranked[0]
    best = top_weight(codebook)

    same_date_top = [
        a
        for a in ranked
        if a.weight == best
        and a.advice_date is not None
        and a.advice_date == top.advice_date
    ]
    if top.weight == best and top.advice_date is not None and len(same_date_top) > 1:
        cands = _rows(same_date_top)
        raise PakketAmbiguousError(
            "Tied top-weight arguments on the same advice date.",
            candidates=cands,
        )

    if top.weight == best and top.advice_date is not None:
        why = (
            f"Earliest {best} match is {top.id} "
            f"({top.dossier_id}, {top.advice_date})."
        )
        shortlist, why = _cap_shortlist(ranked, why)
        return CiteReport(
            verdict="cite",
            why=why,
            as_of=meta.as_of,
            authority=meta.id,
            shortlist=shortlist,
        )

    why = (
        "Best match is not a unique top-weight citation "
        f"(weight={top.weight or 'empty'}, date={top.advice_date or 'missing'})."
    )
    shortlist, why = _cap_shortlist(ranked, why)
    return CiteReport(
        verdict="thin",
        why=why,
        as_of=meta.as_of,
        authority=meta.id,
        shortlist=shortlist,
    )
