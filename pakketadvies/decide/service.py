"""Load corpus then run pure decide (rank 40)."""

from __future__ import annotations

from pakketadvies.core.exceptions import PakketAmbiguousError, PakketIncompleteError
from pakketadvies.data.load import Corpus, list_authorities, load_corpus
from pakketadvies.decide.cite import cite as cite_pure
from pakketadvies.decide.show import show_argument, show_dossier
from pakketadvies.models.argument import Argument, Dossier
from pakketadvies.models.verdict import CiteReport, CiteRow

__all__ = (
    "cite_query",
    "resolve_authority",
    "show_record",
)


def resolve_authority(authority: str | None) -> Corpus:
    known = list_authorities()
    if not known:
        raise PakketIncompleteError("no authority corpora under data/")
    if authority:
        return load_corpus(authority.casefold())
    if len(known) == 1:
        return load_corpus(known[0])
    raise PakketAmbiguousError(
        "multiple authorities loaded; pass --authority",
        candidates=[
            CiteRow(id=a, dossier_id="", authority=a, text=a) for a in known
        ],
    )


def cite_query(
    query: str,
    *,
    authority: str | None = None,
    theme: str | None = None,
    line: str | None = None,
    traject: str | None = None,
) -> CiteReport:
    corpus = resolve_authority(authority)
    return cite_pure(
        corpus.arguments,
        corpus.codebook,
        corpus.meta,
        query,
        theme=theme,
        line=line,
        traject=traject,
    )


def show_record(
    raw_id: str,
    *,
    authority: str | None = None,
) -> Argument | Dossier:
    corpus = resolve_authority(authority)
    native = raw_id.split(":", 1)[-1]
    upper = native.upper()
    if upper.startswith("ARG-"):
        return show_argument(corpus.arguments, raw_id)
    if upper.startswith(("INT-", "GVS-")):
        try:
            return show_dossier(corpus.dossiers, raw_id)
        except Exception:
            pass
        # Fall through: maybe only present as argument dossier_id.
    try:
        return show_argument(corpus.arguments, raw_id)
    except Exception:
        return show_dossier(corpus.dossiers, raw_id)
