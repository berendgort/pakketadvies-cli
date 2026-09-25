"""Exit codes from classified errors."""

from __future__ import annotations

import json
import sys

from pakketadvies.core.envelope import error_payload
from pakketadvies.core.errors import classify_error

__all__ = ("emit_error",)


def emit_error(exc: BaseException, *, as_json: bool) -> int:
    payload = error_payload(exc)
    classified = classify_error(exc)
    if as_json:
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stderr.write(f"error: {exc}\n")
        if payload.get("candidates"):
            sys.stderr.write("candidates:\n")
            for c in payload["candidates"]:
                sys.stderr.write(f"  - {c.get('id', c)}\n")
    return 2 if classified.retryable else 1
