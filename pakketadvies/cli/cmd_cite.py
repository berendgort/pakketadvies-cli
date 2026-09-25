"""cite and show commands."""

from __future__ import annotations

import json

import typer

from pakketadvies.cli.catch import CATCH
from pakketadvies.cli.errors import emit_error
from pakketadvies.cli.render import render_cite, render_show
from pakketadvies.core.envelope import dump_model, success_payload
from pakketadvies.decide.service import cite_query, show_record

__all__ = ("register",)


def register(app: typer.Typer) -> None:
    @app.command("cite")
    def cite_cmd(
        query: str = typer.Argument(..., help="What you would search the sheet for"),
        as_json: bool = typer.Option(False, "--json"),
        authority: str | None = typer.Option(None, "--authority"),
        thema: str | None = typer.Option(None, "--thema", "--theme"),
        lijn: str | None = typer.Option(None, "--lijn", "--line"),
        traject: str | None = typer.Option(None, "--traject"),
    ) -> None:
        """Citation call: which argument to reuse."""
        try:
            report = cite_query(
                query,
                authority=authority,
                theme=thema,
                line=lijn,
                traject=traject,
            )
            if as_json:
                typer.echo(
                    json.dumps(
                        success_payload(dump_model(report)),
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                render_cite(report)
        except CATCH as exc:
            raise typer.Exit(emit_error(exc, as_json=as_json)) from exc

    @app.command("show")
    def show_cmd(
        record_id: str = typer.Argument(..., metavar="ID"),
        as_json: bool = typer.Option(False, "--json"),
        authority: str | None = typer.Option(None, "--authority"),
    ) -> None:
        """Show one argument or dossier by id."""
        try:
            obj = show_record(record_id, authority=authority)
            if as_json:
                typer.echo(
                    json.dumps(
                        success_payload(dump_model(obj)),
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                render_show(obj)
        except CATCH as exc:
            raise typer.Exit(emit_error(exc, as_json=as_json)) from exc
