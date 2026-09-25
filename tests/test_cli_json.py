"""CLI envelope smoke tests against the real ZIN corpus."""

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
    assert body["data"]["verdict"] == "cite"
    assert "as_of" in body["data"]
    shortlist = body["data"]["shortlist"]
    assert shortlist
    top = shortlist[0]
    assert top["source"] is not None
    assert top["source"]["url"]
    verbatim = top["source"].get("verbatim")
    paraphrase = top["source"].get("paraphrase")
    if verbatim is not None:
        assert verbatim != paraphrase


def test_cite_none_for_nonsense_query() -> None:
    result = runner.invoke(app, ["cite", "zzzz-no-such-topic-xyzzy", "--json"])
    assert result.exit_code == 0, result.stdout + result.stderr
    body = json.loads(result.stdout)
    assert body["ok"] is True
    assert body["data"]["verdict"] == "none"
    assert body["data"]["shortlist"] == []


def test_cite_pembrolizumab_is_ambiguous() -> None:
    result = runner.invoke(app, ["cite", "pembrolizumab", "--json"])
    assert result.exit_code != 0
    body = json.loads(result.stdout)
    assert body["ok"] is False
    assert body["error_type"] == "ambiguous"
    assert len(body["candidates"]) > 1
    # Field-test: candidates must carry source so writers need no extra show.
    assert body["candidates"][0]["source"] is not None
    assert body["candidates"][0]["source"]["url"]


def test_cite_nivolumab_does_not_call_unrelated_drug() -> None:
    result = runner.invoke(app, ["cite", "nivolumab", "--json"])
    body = json.loads(result.stdout)
    if body.get("ok"):
        top = body["data"]["shortlist"][0]
        assert top["substance"].casefold() == "nivolumab"
    else:
        assert body["error_type"] == "ambiguous"
        assert all(
            c["substance"].casefold() == "nivolumab" for c in body["candidates"]
        )


def test_cite_single_char_invalid() -> None:
    result = runner.invoke(app, ["cite", "a", "--json"])
    assert result.exit_code != 0
    body = json.loads(result.stdout)
    assert body["ok"] is False
    assert body["error_type"] == "invalid"


def test_cite_gvs_shortlist_capped() -> None:
    result = runner.invoke(app, ["cite", "GVS", "--traject", "GVS", "--json"])
    assert result.exit_code == 0, result.stdout + result.stderr
    body = json.loads(result.stdout)
    assert body["data"]["verdict"] == "cite"
    assert len(body["data"]["shortlist"]) <= 25
    assert "Showing top" in body["data"]["why"]


def test_show_prefixed_and_bare_arg() -> None:
    prefixed = runner.invoke(app, ["show", "zin:ARG-0326", "--json"])
    bare = runner.invoke(app, ["show", "ARG-0326", "--json"])
    assert prefixed.exit_code == 0, prefixed.stdout + prefixed.stderr
    assert bare.exit_code == 0, bare.stdout + bare.stderr
    p = json.loads(prefixed.stdout)["data"]
    b = json.loads(bare.stdout)["data"]
    assert p["id"] == b["id"] == "zin:ARG-0326"
    assert p["source"]["quotation"] is None


def test_show_missing_id_not_found() -> None:
    result = runner.invoke(app, ["show", "ARG-999999", "--json"])
    assert result.exit_code != 0
    body = json.loads(result.stdout)
    assert body["ok"] is False
    assert body["error_type"] == "not_found"


def test_cite_empty_query_invalid() -> None:
    result = runner.invoke(app, ["cite", "   ", "--json"])
    assert result.exit_code != 0
    body = json.loads(result.stdout)
    assert body["ok"] is False
    assert body["error_type"] == "invalid"


def test_cite_thema_no_match_is_none() -> None:
    result = runner.invoke(
        app,
        ["cite", "pembrolizumab", "--thema", "zzzz-no-such-theme", "--json"],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    body = json.loads(result.stdout)
    assert body["ok"] is True
    assert body["data"]["verdict"] == "none"
    assert body["data"]["shortlist"] == []


def test_human_cite_prints_verdict() -> None:
    result = runner.invoke(app, ["cite", "extern controlecohort"])
    assert result.exit_code == 0, result.stdout + result.stderr
    assert "CITE" in result.stdout


def test_human_show_prints_id() -> None:
    result = runner.invoke(app, ["show", "zin:ARG-0326"])
    assert result.exit_code == 0, result.stdout + result.stderr
    assert "zin:ARG-0326" in result.stdout
