"""Pure ranking helpers for FIRST_USE."""

from __future__ import annotations

from pakketadvies.models.argument import Argument, Codebook

__all__ = (
    "filter_arguments",
    "rank_arguments",
    "top_weight",
    "weight_rank",
)


def top_weight(codebook: Codebook) -> str:
    if not codebook.weight_order:
        raise ValueError("codebook.weight_order is empty")
    return codebook.weight_order[0]


def weight_rank(weight: str, codebook: Codebook) -> int:
    try:
        return codebook.weight_order.index(weight)
    except ValueError:
        return len(codebook.weight_order)


def _haystack(arg: Argument) -> str:
    parts = (
        arg.text,
        arg.precedent,
        arg.theme,
        arg.substance,
        arg.brand,
        arg.dossier_id,
        arg.native_id,
        arg.id,
        arg.indication,
        arg.criterion,
        arg.line,
    )
    return " ".join(p for p in parts if p).casefold()


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
    out: list[Argument] = []
    for arg in rows:
        if theme and theme.casefold() not in arg.theme.casefold():
            continue
        if line and line.casefold() not in arg.line.casefold():
            continue
        if traject:
            tr = str(arg.extra.get("traject", ""))
            if traject.casefold() not in tr.casefold():
                continue
        if q not in _haystack(arg):
            continue
        out.append(arg)
    return out


def rank_arguments(rows: list[Argument], codebook: Codebook) -> list[Argument]:
    def key(arg: Argument) -> tuple[int, str, str]:
        date = arg.advice_date or "9999-99-99"
        return (weight_rank(arg.weight, codebook), date, arg.id)

    return sorted(rows, key=key)
