"""Load authority JSONL into models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from pakketadvies.core.exceptions import PakketIncompleteError, PakketInvalidError
from pakketadvies.core.paths import authority_dir, data_root
from pakketadvies.models.argument import (
    SCHEMA_VERSION,
    Argument,
    AuthorityMeta,
    Codebook,
    Dossier,
    SourceDoc,
)

__all__ = (
    "Corpus",
    "list_authorities",
    "load_corpus",
)

T = TypeVar("T", bound=BaseModel)


def list_authorities() -> list[str]:
    root = data_root()
    if not root.is_dir():
        return []
    found: list[str] = []
    for path in sorted(root.iterdir()):
        if not path.is_dir():
            continue
        meta = path / "v1" / "authority.json"
        if meta.is_file():
            found.append(path.name)
    return found


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise PakketIncompleteError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise PakketInvalidError(f"invalid JSON in {path}: {exc}") from exc


def _read_jsonl(path: Path, model_cls: type[T]) -> list[T]:
    if not path.is_file():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise PakketIncompleteError(f"cannot read {path}: {exc}") from exc
    out: list[T] = []
    for i, line in enumerate(lines, 1):
        text = line.strip()
        if not text:
            continue
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            raise PakketInvalidError(f"{path}:{i}: {exc}") from exc
        if not isinstance(raw, dict):
            raise PakketInvalidError(f"{path}:{i}: expected object")
        ver = raw.get("schema_version")
        if ver != SCHEMA_VERSION:
            continue
        out.append(model_cls.model_validate(raw))
    return out


class Corpus:
    def __init__(
        self,
        meta: AuthorityMeta,
        codebook: Codebook,
        arguments: list[Argument],
        dossiers: list[Dossier],
        sources: list[SourceDoc],
    ) -> None:
        self.meta = meta
        self.codebook = codebook
        self.arguments = arguments
        self.dossiers = dossiers
        self.sources = sources


def load_corpus(authority: str) -> Corpus:
    base = authority_dir(authority)
    if not base.is_dir():
        raise PakketIncompleteError(f"authority not found: {authority}")
    meta_raw = _read_json(base / "authority.json")
    if not isinstance(meta_raw, dict):
        raise PakketInvalidError("authority.json must be an object")
    meta = AuthorityMeta.model_validate(meta_raw)
    if meta.reserved:
        raise PakketIncompleteError(f"authority {authority} is reserved and empty")
    code_raw = _read_json(base / "codebook.json")
    if not isinstance(code_raw, dict):
        raise PakketInvalidError("codebook.json must be an object")
    codebook = Codebook.model_validate(code_raw)
    return Corpus(
        meta=meta,
        codebook=codebook,
        arguments=_read_jsonl(base / "arguments.jsonl", Argument),
        dossiers=_read_jsonl(base / "dossiers.jsonl", Dossier),
        sources=_read_jsonl(base / "sources.jsonl", SourceDoc),
    )
