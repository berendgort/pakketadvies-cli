"""Minimal stdio MCP (stdlib JSON-RPC). Same functions as the CLI."""

from __future__ import annotations

import json
import sys
from typing import Any

from pakketadvies.core.envelope import dump_model, error_payload, success_payload
from pakketadvies.decide.instruct import instruct_payload
from pakketadvies.decide.service import cite_query, show_record

__all__ = ("run_stdio",)

TOOLS = [
    {
        "name": "instruct",
        "description": "Agent recipe for pakket. Run first every session.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "cite",
        "description": "Citation call: which ZIN argument to reuse.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "authority": {"type": "string"},
                "theme": {"type": "string"},
                "line": {"type": "string"},
                "traject": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "show",
        "description": "Show one argument or dossier by id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "authority": {"type": "string"},
            },
            "required": ["id"],
        },
    },
]


def _result(payload: dict[str, Any]) -> dict[str, Any]:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    return {"content": [{"type": "text", "text": text}], "isError": not payload.get("ok", True)}


def _call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        if name == "instruct":
            return _result(success_payload(instruct_payload()))
        if name == "cite":
            report = cite_query(
                str(arguments.get("query", "")),
                authority=arguments.get("authority"),
                theme=arguments.get("theme") or arguments.get("thema"),
                line=arguments.get("line") or arguments.get("lijn"),
                traject=arguments.get("traject"),
            )
            return _result(success_payload(dump_model(report)))
        if name == "show":
            obj = show_record(
                str(arguments.get("id", "")),
                authority=arguments.get("authority"),
            )
            return _result(success_payload(dump_model(obj)))
        return _result(error_payload(ValueError(f"unknown tool: {name}")))
    except Exception as exc:  # noqa: BLE001
        return _result(error_payload(exc))


def _handle(msg: dict[str, Any]) -> dict[str, Any] | None:
    method = msg.get("method")
    req_id = msg.get("id")
    params = msg.get("params") or {}
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "pakketadvies", "version": "0.1.0"},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments") or {}
        return {"jsonrpc": "2.0", "id": req_id, "result": _call_tool(name, args)}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if req_id is None:
        return None
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def run_stdio() -> None:
    for line in sys.stdin:
        text = line.strip()
        if not text:
            continue
        try:
            msg = json.loads(text)
        except json.JSONDecodeError:
            continue
        resp = _handle(msg)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
