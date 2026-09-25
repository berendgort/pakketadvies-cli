"""Pure ranking helpers for FIRST_USE."""

from __future__ import annotations

import re

from pakketadvies.models.argument import Argument, Codebook

__all__ = (
    "MIN_QUERY_LEN",
    "filter_arguments",
    "rank_arguments",
    "top_weight",
    "weight_rank",
)

# Reject single-character floods like cite "a" (field-test lane: misses/thin).
MIN_QUERY_LEN = 2


def top_weight(codebook: Codebook) -> str:
    if not codebook.weight_order:
        raise ValueError("codebook.weight_order is empty")
    return codebook.weight_order[0]


def weight_rank(weight: str, codebook: Codebook) -> int:
    try:
        return codebook.weight_order.index(weight)
    except ValueError:
        return len(codebook.weight_order)


def _identity_haystack(arg: Argument) -> str:
    parts = (
        arg.substance,
        arg.brand,
        arg.dossier_id,
        arg.native_id,
        arg.id,
    )
    return " ".join(p for p in parts if p).casefold()


def _content_haystack(arg: Argument) -> str:
    parts = (
        arg.text,
        arg.precedent,
        arg.theme,
        arg.indication,
        arg.criterion,
        arg.line,
    )
    return " ".join(p for p in parts if p).casefold()


def _contains(hay: str, q: str) -> bool:
    """Substring match; alphanumeric tokens require word boundaries.

    Stops false cites like NMAA inside 'traanaanmaakdeficiëntie'.
    """
    if not q or not hay:
        return False
    if re.fullmatch(r"[a-z0-9]+", q):
        return re.search(rf"(?<![a-z0-9]){re.escape(q)}(?![a-z0-9])", hay) is not None
    return q in hay


def filter_arguments(
    rows: list[Argument],
    query: str,
    *,
    theme: str | None = None,
    line: str | None = None,
    traject: str | None = None,
) -> list[Argument]:
    q = query.strip().casefold()
    if not q:
        raise ValueError("query must not be empty")
    if len(q) < MIN_QUERY_LEN:
        raise ValueError(
            f"query must be at least {MIN_QUERY_LEN} characters "
            "(single-character queries flood the corpus)"
        )
    identity_hits: list[Argument] = []
    content_hits: list[Argument] = []
    for arg in rows:
        if theme and theme.casefold() not in arg.theme.casefold():
            continue
        if line and line.casefold() not in arg.line.casefold():
            continue
        if traject:
            tr = str(arg.extra.get("traject", ""))
            if traject.casefold() not in tr.casefold():
                continue
        if _contains(_identity_haystack(arg), q):
            identity_hits.append(arg)
        elif _contains(_content_haystack(arg), q):
            content_hits.append(arg)
    # Prefer substance/brand/id hits over incidental precedent mentions
    # (field-test: cite "nivolumab" must not call panitumumab).
    if identity_hits:
        return identity_hits
    return content_hits


def rank_arguments(rows: list[Argument], codebook: Codebook) -> list[Argument]:
    def key(arg: Argument) -> tuple[int, str, str]:
        date = arg.advice_date or "9999-99-99"
        return (weight_rank(arg.weight, codebook), date, arg.id)

    return sorted(rows, key=key)
