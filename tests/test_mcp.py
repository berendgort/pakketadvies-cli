"""MCP stdio handler contract (no subprocess)."""

from __future__ import annotations

import json

from pakketadvies.mcp.server import TOOLS, _handle


def test_initialize() -> None:
    resp = _handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp is not None
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "pakketadvies"
    assert "tools" in resp["result"]["capabilities"]


def test_tools_list_includes_core_verbs() -> None:
    resp = _handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    assert resp is not None
    names = {t["name"] for t in resp["result"]["tools"]}
    assert names == {"instruct", "cite", "show"}
    assert {t["name"] for t in TOOLS} == names


def test_tools_call_cite_verdict_shape() -> None:
    resp = _handle(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "cite",
                "arguments": {"query": "extern controlecohort"},
            },
        }
    )
    assert resp is not None
    content = resp["result"]["content"][0]["text"]
    body = json.loads(content)
    assert body["ok"] is True
    assert body["data"]["verdict"] in {"cite", "thin", "none", "ambiguous"}
    assert "shortlist" in body["data"]
    assert resp["result"]["isError"] is False


def test_unknown_tool_is_error_envelope() -> None:
    resp = _handle(
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "nope", "arguments": {}},
        }
    )
    assert resp is not None
    body = json.loads(resp["result"]["content"][0]["text"])
    assert body["ok"] is False
    assert resp["result"]["isError"] is True


def test_unknown_method_returns_jsonrpc_error() -> None:
    resp = _handle({"jsonrpc": "2.0", "id": 5, "method": "no/such", "params": {}})
    assert resp is not None
    assert resp["error"]["code"] == -32601
