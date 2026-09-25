"""instruct command."""

from __future__ import annotations

import json

import typer

from pakketadvies.cli.catch import CATCH
from pakketadvies.cli.errors import emit_error
from pakketadvies.core.envelope import success_payload
from pakketadvies.decide.instruct import instruct_payload

__all__ = ("register",)


def register(app: typer.Typer) -> None:
    @app.command("instruct")
    def instruct_cmd(
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Agent recipe. Run every session before cite."""
        try:
            data = instruct_payload()
            if as_json:
                typer.echo(json.dumps(success_payload(data), ensure_ascii=False, indent=2))
            else:
                typer.echo(data["summary"])
                for step in data["steps"]:
                    cmd = step.get("command") or "(narrate)"
                    typer.echo(f"\n{step['step']}. {step['action']}\n  {cmd}")
        except CATCH as exc:
            raise typer.Exit(emit_error(exc, as_json=as_json)) from exc
