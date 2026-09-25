"""Human render for cite (verdict first, then source block)."""

from __future__ import annotations

from rich.panel import Panel
from rich.table import Table

from pakketadvies.cli.console import console
from pakketadvies.models.verdict import (
    CiteReport,
    ShowArgument,
    ShowDossier,
    SourceRef,
)

__all__ = ("render_cite", "render_show")


def _print_source(src: SourceRef) -> None:
    console.print(
        f"[bold]document[/bold]: {src.document or '—'}  "
        f"[bold]locator[/bold]: {src.locator or '—'}"
    )
    if src.url:
        console.print(f"[bold]official URL[/bold]: {src.url}")
    if src.pdf:
        console.print(f"[bold]local PDF[/bold]: {src.pdf}")
    if src.extract:
        console.print(f"[bold]text extract[/bold]: {src.extract}")
    if src.quotation:
        console.print(f"[bold]quotation (sheet)[/bold]:\n{src.quotation}")
    if src.verbatim:
        console.print("[bold]verbatim extract[/bold]:")
        console.print(src.verbatim)
    elif src.note:
        console.print(f"[bold]source note[/bold]: {src.note}")
    if src.paraphrase:
        console.print(
            "[bold]analyst paraphrase[/bold] "
            "[dim](not a quotation from ZIN)[/dim]:"
        )
        console.print(src.paraphrase)


def render_cite(report: CiteReport) -> None:
    style = {
        "cite": "bold green",
        "thin": "bold yellow",
        "none": "bold red",
        "ambiguous": "bold magenta",
    }.get(report.verdict, "bold")
    console.print(
        Panel(
            f"[{style}]{report.verdict.upper()}[/{style}]\n{report.why}",
            title="pakket cite",
            subtitle=f"as_of {report.as_of} · {report.preset}",
        )
    )
    if not report.shortlist:
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", style="dim")
    table.add_column("id")
    table.add_column("dossier")
    table.add_column("date")
    table.add_column("weight")
    table.add_column("theme")
    for i, row in enumerate(report.shortlist[:12], 1):
        table.add_row(
            str(i),
            row.id,
            row.dossier_id,
            row.advice_date or "-",
            row.weight or "-",
            row.theme or "-",
        )
    console.print(table)
    top = report.shortlist[0]
    console.print(
        f"[bold]{top.id}[/bold] · {top.dossier_id} · "
        f"{top.advice_date or 'no date'} · {top.weight or '—'}"
    )
    if top.precedent:
        console.print(f"[bold]precedent[/bold]: {top.precedent}")
    if top.source:
        _print_source(top.source)


def render_show(obj: ShowArgument | ShowDossier) -> None:
    if isinstance(obj, ShowArgument):
        console.print(
            Panel(
                f"[bold]{obj.id}[/bold]\n"
                f"{obj.dossier_id} · {obj.advice_date or 'no date'} · "
                f"{obj.weight}\n{obj.theme}\n\n"
                f"[bold]precedent[/bold]: {obj.precedent}",
                title="argument",
            )
        )
        _print_source(obj.source)
        return
    console.print(
        Panel(
            f"[bold]{obj.id}[/bold]\n"
            f"{obj.substance} ({obj.brand})\n"
            f"{obj.indication}\n"
            f"{obj.title}",
            title="dossier",
        )
    )
    _print_source(obj.source)
