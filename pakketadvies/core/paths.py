"""Repo root and data paths (no I/O beyond Path)."""

from __future__ import annotations

from pathlib import Path

__all__ = ("authority_dir", "data_root", "repo_root", "venv_python")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_root() -> Path:
    return repo_root() / "data"


def authority_dir(authority: str, *, version: str = "v1") -> Path:
    return data_root() / authority / version


def venv_python() -> Path:
    return repo_root() / ".venv" / "bin" / "python"
