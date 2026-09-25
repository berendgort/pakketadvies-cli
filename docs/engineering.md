# Engineering

Korotkevich / Tourist bar for code. Gray / Stonebraker bar for data.
Rewritten for a local archive CLI. No PHI, no second warehouse, no server.

## Layers

```text
[10] models              Pydantic DTOs. No disk, no clock, no paths.
[12] core.exceptions · paths
[20] data                Load JSONL. Return models.
[30] core                Envelope, error classification.
[40] decide              Pure cite policy and instruct payload.
[50] cli · mcp           Typer / stdio MCP. Call decide, render.
```

Downward imports only. No work at import time. No file over 250 lines.
`__all__` on every library module. `mypy --strict`. No `print` outside CLI
and MCP entry. No em-dash or en-dash in agent-facing strings.

## Data

JSONL under `data/<authority>/v1/` is the basket. One writer:
`scripts/ingest_zin.py`. The CLI only reads. No SQLite copy. Advice date is
the domain clock. `as_of` is the corpus snapshot date.

Envelope keys are shared. Authority-only facts live in allowlisted `extra`.
Unknown keys raise at ingest. Old `schema_version` values are ignored.

## Left out on purpose

AES-GCM, gold buckets, Postgres leases, and Safe Harbor gates belong to
clinic notes. This corpus is public advice paraphrases. Encrypting it would
hide it from the agent that must search it. Postgres or a queue would be a
second system around a file that loads in memory.

## Checks

```bash
python scripts/check_code_quality.py
ruff check .
mypy --strict pakketadvies scripts/check_code_quality.py
pytest -q
```
