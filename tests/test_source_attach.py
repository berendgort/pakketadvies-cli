"""Source attachment on cite shortlist."""

from __future__ import annotations

from pakketadvies.decide.cite import cite
from pakketadvies.decide.source_attach import attach_sources_to_report, source_for_argument
from pakketadvies.models.argument import (
    Argument,
    AuthorityMeta,
    Codebook,
    Dossier,
    SourceDoc,
)

META = AuthorityMeta(id="zin", name="ZIN", as_of="2026-09-24")
CODE = Codebook(
    authority="zin",
    weight_order=["Doorslaggevend", "Ondersteunend", "Zijdelings"],
)


def _arg(
    native: str,
    *,
    dossier: str = "GVS-999",
    text: str = "extern controlecohort",
    label: str = "brief",
    quote: str = "",
) -> Argument:
    extra = {"quote": quote} if quote else {}
    return Argument(
        authority="zin",
        id=f"zin:{native}",
        native_id=native,
        dossier_id=dossier,
        advice_date="2020-01-15",
        substance="drug",
        theme="Indirecte vergelijking / NMA",
        weight="Doorslaggevend",
        text=text,
        precedent=text,
        source_label=label,
        source_locator="brief p.2",
        extra=extra,
    )


def test_cite_top_row_gets_url_and_paraphrase_not_quotation() -> None:
    arg = _arg("ARG-1", text="extern controlecohort — analyst restatement of ZIN")
    dossier = Dossier(
        authority="zin",
        id="zin:GVS-999",
        native_id="GVS-999",
        title="Test advice",
        extra={"source_url": "https://www.zorginstituutnederland.nl/example"},
    )
    sources = [
        SourceDoc(
            authority="zin",
            id="zin:pdf:GVS-999:a.pdf",
            dossier_id="GVS-999",
            path="assets/zin/bundles/gvs/fake.zip#GVS-999/a.pdf",
        )
    ]
    report = cite([arg], CODE, META, "extern controlecohort")
    enriched = attach_sources_to_report(
        report,
        arguments=[arg],
        dossiers=[dossier],
        sources=sources,
    )
    top = enriched.shortlist[0]
    assert top.source is not None
    assert top.source.url == "https://www.zorginstituutnederland.nl/example"
    assert top.source.pdf == "assets/zin/bundles/gvs/fake.zip#GVS-999/a.pdf"
    assert top.source.paraphrase == "extern controlecohort — analyst restatement of ZIN"
    assert top.source.quotation is None
    assert top.source.verbatim is None
    assert top.source.note is not None
    assert "No text extract" in top.source.note


def test_missing_extract_sets_note_and_null_verbatim() -> None:
    arg = _arg("ARG-2")
    dossier = Dossier(
        authority="zin",
        id="zin:GVS-999",
        native_id="GVS-999",
        extra={"source_url": "https://example.nl/doc"},
    )
    src = source_for_argument(
        arg,
        dossier=dossier,
        sources=[],
        include_verbatim=True,
    )
    assert src.verbatim is None
    assert src.quotation is None
    assert src.url == "https://example.nl/doc"
    assert src.note is not None
    assert "No text extract" in src.note


def test_later_shortlist_rows_skip_verbatim_read() -> None:
    a1 = Argument(
        authority="zin",
        id="zin:ARG-1",
        native_id="ARG-1",
        dossier_id="GVS-1",
        advice_date="2019-01-01",
        substance="drug",
        theme="Indirecte vergelijking / NMA",
        weight="Doorslaggevend",
        text="extern controlecohort early",
        precedent="early",
        source_label="brief",
        source_locator="brief p.2",
    )
    a2 = Argument(
        authority="zin",
        id="zin:ARG-2",
        native_id="ARG-2",
        dossier_id="GVS-1",
        advice_date="2021-01-01",
        substance="drug",
        theme="Indirecte vergelijking / NMA",
        weight="Doorslaggevend",
        text="extern controlecohort later",
        precedent="later",
        source_label="brief",
        source_locator="brief p.3",
    )
    dossier = Dossier(
        authority="zin",
        id="zin:GVS-1",
        native_id="GVS-1",
        extra={"source_url": "https://example.nl/gvs-1"},
    )
    sources = [
        SourceDoc(
            authority="zin",
            id="zin:txt:GVS-1:x.txt",
            dossier_id="GVS-1",
            path="assets/zin/extracts/missing.zip#GVS-1__x.txt",
        )
    ]
    report = cite([a1, a2], CODE, META, "extern")
    enriched = attach_sources_to_report(
        report,
        arguments=[a1, a2],
        dossiers=[dossier],
        sources=sources,
    )
    assert enriched.shortlist[0].id == "zin:ARG-1"
    assert enriched.shortlist[0].source is not None
    assert enriched.shortlist[0].source.extract is not None
    assert enriched.shortlist[0].source.verbatim is None
    assert enriched.shortlist[0].source.note is not None
    assert "missing" in enriched.shortlist[0].source.note
    assert enriched.shortlist[1].source is not None
    assert enriched.shortlist[1].source.extract is not None
    assert enriched.shortlist[1].source.verbatim is None
    assert enriched.shortlist[1].source.note is None
