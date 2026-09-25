"""Load corpus then run pure decide (rank 40)."""

from __future__ import annotations

from pakketadvies.core.exceptions import (
    PakketAmbiguousError,
    PakketIncompleteError,
    PakketNotFoundError,
)
from pakketadvies.data.load import Corpus, list_authorities, load_corpus
from pakketadvies.decide.cite import cite as cite_pure
from pakketadvies.decide.show import show_argument, show_dossier
from pakketadvies.decide.source_attach import (
    attach_sources_to_report,
    attach_sources_to_rows,
    source_for_argument,
    source_for_dossier,
)
from pakketadvies.models.argument import Argument, Dossier
from pakketadvies.models.verdict import (
    CiteReport,
    CiteRow,
    ShowArgument,
    ShowDossier,
)

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
    try:
        report = cite_pure(
            corpus.arguments,
            corpus.codebook,
            corpus.meta,
            query,
            theme=theme,
            line=line,
            traject=traject,
        )
    except PakketAmbiguousError as exc:
        # Field-test: ambiguous candidates must carry source blocks so writers
        # can pick without a second show.
        enriched = attach_sources_to_rows(
            list(exc.candidates),
            arguments=corpus.arguments,
            dossiers=corpus.dossiers,
            sources=corpus.sources,
            verbatim_on_first=False,
        )
        raise PakketAmbiguousError(str(exc), candidates=enriched) from exc
    return attach_sources_to_report(
        report,
        arguments=corpus.arguments,
        dossiers=corpus.dossiers,
        sources=corpus.sources,
    )


def show_record(
    raw_id: str,
    *,
    authority: str | None = None,
) -> ShowArgument | ShowDossier:
    corpus = resolve_authority(authority)
    native = raw_id.split(":", 1)[-1]
    upper = native.upper()
    dos_by_native = {d.native_id: d for d in corpus.dossiers}

    def as_show_arg(arg: Argument) -> ShowArgument:
        dossier = dos_by_native.get(arg.dossier_id)
        src = source_for_argument(
            arg,
            dossier=dossier,
            sources=corpus.sources,
            include_verbatim=True,
        )
        return ShowArgument(**arg.model_dump(), source=src)

    def as_show_dos(dos: Dossier) -> ShowDossier:
        src = source_for_dossier(dos, corpus.sources)
        return ShowDossier(**dos.model_dump(), source=src)

    if upper.startswith("ARG-"):
        return as_show_arg(show_argument(corpus.arguments, raw_id))
    if upper.startswith(("INT-", "GVS-")):
        try:
            return as_show_dos(show_dossier(corpus.dossiers, raw_id))
        except PakketNotFoundError:
            pass
    try:
        return as_show_arg(show_argument(corpus.arguments, raw_id))
    except PakketNotFoundError:
        return as_show_dos(show_dossier(corpus.dossiers, raw_id))
