"""Typer CLI entry."""

from __future__ import annotations

import typer

from pakketadvies.cli import cmd_cite, cmd_mcp, cmd_ops

__all__ = ("app", "cli")

app = typer.Typer(
    name="pakket",
    help=(
        "Cite the ZIN argument to reuse. "
        "Happy path: ./pakket instruct --json then ./pakket cite \"...\" --json."
    ),
    no_args_is_help=True,
    add_completion=False,
)

cmd_ops.register(app)
cmd_cite.register(app)
cmd_mcp.register(app)


def cli() -> None:
    app()


if __name__ == "__main__":
    cli()
