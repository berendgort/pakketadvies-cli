"""Second-authority fixture: cite refuses to mix without --authority."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pakketadvies.core.exceptions import PakketAmbiguousError
from pakketadvies.decide.service import resolve_authority


def test_multi_authority_requires_flag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "data"
    for auth in ("zin", "nice"):
        d = root / auth / "v1"
        d.mkdir(parents=True)
        (d / "authority.json").write_text(
            json.dumps(
                {
                    "id": auth,
                    "name": auth,
                    "as_of": "2026-01-01",
                    "schema_version": 1,
                    "reserved": False,
                }
            ),
            encoding="utf-8",
        )
        (d / "codebook.json").write_text(
            json.dumps({"authority": auth, "weight_order": ["A", "B"]}),
            encoding="utf-8",
        )
        (d / "arguments.jsonl").write_text("", encoding="utf-8")
        (d / "dossiers.jsonl").write_text("", encoding="utf-8")
        (d / "sources.jsonl").write_text("", encoding="utf-8")
    monkeypatch.setattr("pakketadvies.data.load.data_root", lambda: root)
    monkeypatch.setattr(
        "pakketadvies.data.load.authority_dir",
        lambda a, version="v1": root / a / version,
    )
    with pytest.raises(PakketAmbiguousError) as exc:
        resolve_authority(None)
    assert {c.authority for c in exc.value.candidates} == {"nice", "zin"}
