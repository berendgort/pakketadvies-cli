"""MCP CLI entry: ./pakket mcp"""

from __future__ import annotations

import typer

from pakketadvies.cli.catch import CATCH
from pakketadvies.cli.errors import emit_error
from pakketadvies.mcp.server import run_stdio

__all__ = ("register",)


def register(app: typer.Typer) -> None:
    @app.command("mcp")
    def mcp_cmd() -> None:
        """Stdio MCP adapter (prefer ./pakket cite --json from the shell)."""
        try:
            run_stdio()
        except CATCH as exc:
            raise typer.Exit(emit_error(exc, as_json=True)) from exc
