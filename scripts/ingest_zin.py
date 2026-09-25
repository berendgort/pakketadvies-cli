#!/usr/bin/env python3
"""Deprecated. Prefer: python scripts/ingest_assets.py"""

from __future__ import annotations

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("ingest_assets.py")), run_name="__main__")
