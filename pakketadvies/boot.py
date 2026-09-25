#!/usr/bin/env python3
"""Boot: ensure venv + deps, then run the Typer CLI. Agent-facing only."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("PAKKET_ROOT", Path(__file__).resolve().parents[1]))
VENV = ROOT / ".venv"
VENV_PY = VENV / "bin" / "python"
REQ = ROOT / "requirements.lock"


def _ok_imports(py: Path) -> bool:
    try:
        subprocess.check_call(
            [str(py), "-c", "import typer, rich, pydantic"],
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, OSError):
        return False


def _ensure_venv() -> Path:
    if VENV_PY.is_file() and _ok_imports(VENV_PY):
        return VENV_PY
    base = Path(sys.executable).resolve()
    subprocess.check_call([str(base), "-m", "venv", str(VENV)], cwd=str(ROOT))
    pip = VENV / "bin" / "pip"
    subprocess.check_call(
        [str(pip), "install", "--upgrade", "pip"],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
    )
    if REQ.is_file():
        subprocess.check_call([str(pip), "install", "-r", str(REQ)], cwd=str(ROOT))
    else:
        subprocess.check_call(
            [str(pip), "install", "typer>=0.15.1", "rich>=13.8.0", "pydantic>=2.10.0"],
            cwd=str(ROOT),
        )
    return VENV_PY


def _fail(msg: str) -> int:
    import json

    sys.stdout.write(
        json.dumps(
            {
                "ok": False,
                "api_version": 1,
                "error": msg,
                "error_type": "incomplete",
                "retryable": False,
                "agent_fix": {
                    "do": [
                        "YOU fix the runtime. Do not ask the human to install anything.",
                        "Ensure python3 + venv works, then re-run ./pakket instruct --json",
                    ],
                    "never_ask_human": [
                        "install Python",
                        "run pip",
                        "create a venv",
                        "open a terminal tutorial",
                    ],
                },
            },
            ensure_ascii=False,
        )
        + "\n"
    )
    return 1


def main() -> int:
    if os.environ.get("PAKKET_BOOTSTRAPPED") == "1":
        sys.path.insert(0, str(ROOT))
        from pakketadvies.cli.main import cli

        cli()
        return 0
    try:
        py = _ensure_venv()
    except Exception as exc:  # noqa: BLE001
        return _fail(f"bootstrap failed: {exc}")
    env = os.environ.copy()
    env["PAKKET_BOOTSTRAPPED"] = "1"
    env["PAKKET_ROOT"] = str(ROOT)
    env["PYTHONPATH"] = str(ROOT) + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    return subprocess.call(
        [str(py), str(ROOT / "pakketadvies" / "boot.py"), *sys.argv[1:]],
        env=env,
        cwd=str(ROOT),
    )


if __name__ == "__main__":
    raise SystemExit(main())
