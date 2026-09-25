"""show_record must surface ambiguous dossier ids, not swallow them."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pakketadvies.core.exceptions import PakketAmbiguousError
from pakketadvies.decide.service import show_record


def _write_corpus(root: Path, *, dossiers: list[dict], arguments: list[dict]) -> None:
    d = root / "zin" / "v1"
    d.mkdir(parents=True)
    (d / "authority.json").write_text(
        json.dumps(
            {
                "id": "zin",
                "name": "ZIN",
                "as_of": "2026-01-01",
                "schema_version": 1,
                "reserved": False,
            }
        ),
        encoding="utf-8",
    )
    (d / "codebook.json").write_text(
        json.dumps({"authority": "zin", "weight_order": ["Doorslaggevend"]}),
        encoding="utf-8",
    )
    (d / "arguments.jsonl").write_text(
        "".join(json.dumps(a) + "\n" for a in arguments),
        encoding="utf-8",
    )
    (d / "dossiers.jsonl").write_text(
        "".join(json.dumps(x) + "\n" for x in dossiers),
        encoding="utf-8",
    )
    (d / "sources.jsonl").write_text("", encoding="utf-8")


def test_ambiguous_dossier_id_is_not_swallowed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "data"
    _write_corpus(
        root,
        dossiers=[
            {
                "schema_version": 1,
                "authority": "zin",
                "id": "zin:INT-1",
                "native_id": "INT-1",
                "title": "first",
            },
            {
                "schema_version": 1,
                "authority": "zin",
                "id": "zin:INT-1-dup",
                "native_id": "INT-1",
                "title": "second",
            },
        ],
        arguments=[
            {
                "schema_version": 1,
                "authority": "zin",
                "id": "zin:INT-1",
                "native_id": "INT-1",
                "dossier_id": "INT-9",
                "weight": "Doorslaggevend",
                "text": "decoy that must not win if dossier is ambiguous",
                "precedent": "decoy",
            }
        ],
    )
    monkeypatch.setattr("pakketadvies.data.load.data_root", lambda: root)
    monkeypatch.setattr(
        "pakketadvies.data.load.authority_dir",
        lambda a, version="v1": root / a / version,
    )
    with pytest.raises(PakketAmbiguousError) as exc:
        show_record("INT-1")
    assert len(exc.value.candidates) == 2
    assert all(c.dossier_id == "INT-1" for c in exc.value.candidates)
