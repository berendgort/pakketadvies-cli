"""Human render for cite (verdict first)."""

from __future__ import annotations

from rich.panel import Panel
from rich.table import Table

from pakketadvies.cli.console import console
from pakketadvies.models.argument import Argument, Dossier
from pakketadvies.models.verdict import CiteReport

__all__ = ("render_cite", "render_show")


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
    if top.precedent:
        console.print(f"[bold]precedent[/bold]: {top.precedent}")
    if top.text:
        console.print(f"[dim]{top.text[:400]}{'...' if len(top.text) > 400 else ''}[/dim]")


def render_show(obj: Argument | Dossier) -> None:
    if isinstance(obj, Argument):
        console.print(
            Panel(
                f"[bold]{obj.id}[/bold]\n"
                f"{obj.dossier_id} · {obj.advice_date or 'no date'} · {obj.weight}\n"
                f"{obj.theme}\n\n{obj.precedent}\n\n{obj.text}",
                title="argument",
            )
        )
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
