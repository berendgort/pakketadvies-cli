"""CLI envelope smoke tests."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from pakketadvies.cli.main import app

runner = CliRunner()


def test_instruct_json() -> None:
    result = runner.invoke(app, ["instruct", "--json"])
    assert result.exit_code == 0
    body = json.loads(result.stdout)
    assert body["ok"] is True
    assert body["api_version"] == 1
    assert "cite" in body["data"]["verbs"]


def test_cite_json_real_corpus() -> None:
    result = runner.invoke(app, ["cite", "extern controlecohort", "--json"])
    assert result.exit_code == 0, result.stdout + result.stderr
    body = json.loads(result.stdout)
    assert body["ok"] is True
    assert body["data"]["verdict"] in {"cite", "thin", "none", "ambiguous"}
    assert "as_of" in body["data"]
