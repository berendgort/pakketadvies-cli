"""Read one member from a path stored as relative_zip#member."""

from __future__ import annotations

import zipfile

from pakketadvies.core.paths import repo_root

__all__ = ("read_zip_member", "split_zip_path")


def split_zip_path(stored: str) -> tuple[str, str] | None:
    if "#" not in stored:
        return None
    zip_rel, member = stored.split("#", 1)
    if not zip_rel or not member:
        return None
    return zip_rel, member


def read_zip_member(stored: str) -> str | None:
    """Return UTF-8 text of zip#member, or None if missing/unreadable."""
    parts = split_zip_path(stored)
    if parts is None:
        return None
    zip_rel, member = parts
    path = repo_root() / zip_rel
    if not path.is_file():
        return None
    try:
        with zipfile.ZipFile(path) as zf:
            raw = zf.read(member)
    except (OSError, KeyError, zipfile.BadZipFile):
        return None
    return raw.decode("utf-8", errors="replace")
