"""Attach SourceRef (URL, PDF, extract, verbatim) onto cite/show rows."""

from __future__ import annotations

import re
from collections import defaultdict

from pakketadvies.data.zip_member import read_zip_member
from pakketadvies.models.argument import Argument, Dossier, SourceDoc
from pakketadvies.models.verdict import CiteReport, CiteRow, SourceRef

__all__ = (
    "attach_sources_to_report",
    "attach_sources_to_rows",
    "source_for_argument",
    "source_for_dossier",
)

_MISSING_EXTRACT = (
    "No text extract on disk for this dossier; use source.url and source.pdf."
)


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def _tokens(text: str) -> set[str]:
    return {t for t in _norm(text).split() if len(t) > 2}


def _score_label(label: str, path: str) -> int:
    if not label:
        return 0
    name = path.rsplit("#", 1)[-1]
    name = name.rsplit("/", 1)[-1]
    label_n = _norm(label)
    name_n = _norm(name)
    if not label_n or not name_n:
        return 0
    if label_n in name_n or name_n in label_n:
        return 100
    lt, nt = _tokens(label), _tokens(name)
    if not lt or not nt:
        return 0
    return len(lt & nt)


def _pick_path(
    candidates: list[SourceDoc],
    label: str,
) -> tuple[str | None, str | None]:
    """Return (chosen_path, note_if_ambiguous_or_empty)."""
    if not candidates:
        return None, None
    if len(candidates) == 1:
        return candidates[0].path or None, None
    scored = sorted(
        ((_score_label(label, s.path), s.path) for s in candidates),
        key=lambda x: (-x[0], x[1]),
    )
    best_score = scored[0][0]
    winners = [p for sc, p in scored if sc == best_score and sc > 0]
    if len(winners) == 1:
        return winners[0], None
    paths = [s.path for s in candidates if s.path]
    return None, "Multiple local files; no unique match for source_label: " + "; ".join(
        paths
    )

def _index_sources(
    sources: list[SourceDoc],
) -> dict[str, dict[str, list[SourceDoc]]]:
    out: dict[str, dict[str, list[SourceDoc]]] = defaultdict(
        lambda: {"pdf": [], "txt": []}
    )
    for src in sources:
        kind = "txt" if ":txt:" in src.id else "pdf" if ":pdf:" in src.id else ""
        if not kind:
            continue
        out[src.dossier_id][kind].append(src)
    return out


def _dossier_url(dossier: Dossier | None) -> str | None:
    if dossier is None:
        return None
    url = dossier.extra.get("source_url")
    if isinstance(url, str) and url.strip():
        return url.strip()
    return None


def _quotation(arg: Argument) -> str | None:
    raw = arg.extra.get("quote")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def source_for_argument(
    arg: Argument,
    *,
    dossier: Dossier | None,
    sources: list[SourceDoc],
    include_verbatim: bool,
) -> SourceRef:
    by_dos = _index_sources(sources)
    bucket = by_dos.get(arg.dossier_id, {"pdf": [], "txt": []})
    label = arg.source_label
    pdf, pdf_note = _pick_path(bucket["pdf"], label)
    extract, ext_note = _pick_path(bucket["txt"], label)

    notes: list[str] = []
    if pdf_note:
        notes.append(pdf_note)
    if ext_note:
        notes.append(ext_note)

    verbatim: str | None = None
    if include_verbatim:
        if extract:
            verbatim = read_zip_member(extract)
            if verbatim is None:
                notes.append(
                    "Text extract path is registered but the zip member is missing "
                    f"on disk: {extract}"
                )
        elif not bucket["txt"]:
            notes.append(_MISSING_EXTRACT)
        elif not ext_note:
            notes.append(_MISSING_EXTRACT)
    elif not bucket["txt"]:
        # Later rows skip zip reads; still surface missing-extract (field-test).
        notes.append(_MISSING_EXTRACT)

    note = " ".join(notes) if notes else None
    paraphrase = arg.text.strip() or None
    return SourceRef(
        document=arg.source_label,
        locator=arg.source_locator,
        url=_dossier_url(dossier),
        pdf=pdf,
        extract=extract,
        quotation=_quotation(arg),
        paraphrase=paraphrase,
        verbatim=verbatim,
        note=note,
    )


def source_for_dossier(
    dossier: Dossier,
    sources: list[SourceDoc],
) -> SourceRef:
    by_dos = _index_sources(sources)
    bucket = by_dos.get(dossier.native_id, {"pdf": [], "txt": []})
    # Prefer native_id; also try full id suffix
    if not bucket["pdf"] and not bucket["txt"]:
        bucket = by_dos.get(dossier.id.split(":")[-1], {"pdf": [], "txt": []})

    notes: list[str] = []
    pdf: str | None = None
    extract: str | None = None
    if len(bucket["pdf"]) == 1:
        pdf = bucket["pdf"][0].path or None
    elif len(bucket["pdf"]) > 1:
        notes.append(
            "Multiple PDF members: "
            + "; ".join(s.path for s in bucket["pdf"] if s.path)
        )
    if len(bucket["txt"]) == 1:
        extract = bucket["txt"][0].path or None
    elif len(bucket["txt"]) > 1:
        notes.append(
            "Multiple text extracts: "
            + "; ".join(s.path for s in bucket["txt"] if s.path)
        )
    if not bucket["pdf"] and not bucket["txt"]:
        notes.append("No local PDF or text extract registered for this dossier.")

    return SourceRef(
        document="",
        locator="",
        url=_dossier_url(dossier),
        pdf=pdf,
        extract=extract,
        quotation=None,
        paraphrase=None,
        verbatim=None,
        note=" ".join(notes) if notes else None,
    )


def attach_sources_to_rows(
    rows: list[CiteRow],
    *,
    arguments: list[Argument],
    dossiers: list[Dossier],
    sources: list[SourceDoc],
    verbatim_on_first: bool = True,
) -> list[CiteRow]:
    """Attach SourceRef onto cite rows or ambiguous candidates."""
    if not rows:
        return rows
    args_by_id = {a.id: a for a in arguments}
    dos_by_native = {d.native_id: d for d in dossiers}
    enriched: list[CiteRow] = []
    for i, row in enumerate(rows):
        arg = args_by_id.get(row.id)
        if arg is None:
            enriched.append(row)
            continue
        dossier = dos_by_native.get(arg.dossier_id)
        include_verbatim = bool(verbatim_on_first and i == 0)
        src = source_for_argument(
            arg,
            dossier=dossier,
            sources=sources,
            include_verbatim=include_verbatim,
        )
        enriched.append(row.model_copy(update={"source": src}))
    return enriched


def attach_sources_to_report(
    report: CiteReport,
    *,
    arguments: list[Argument],
    dossiers: list[Dossier],
    sources: list[SourceDoc],
) -> CiteReport:
    if not report.shortlist:
        return report
    enriched = attach_sources_to_rows(
        report.shortlist,
        arguments=arguments,
        dossiers=dossiers,
        sources=sources,
        verbatim_on_first=True,
    )
    return report.model_copy(update={"shortlist": enriched})
