# Agents

This repo is a local citation CLI for Zorginstituut Nederland drug-reimbursement
advice. The corpus is already in `data/zin/v1/`.

[README.md](README.md) is the human front door (Path A). You are Path B: every
session starts with `instruct`, then `cite`.

Humans using this product are often non-technical. They only paste the GitHub
link into an AI. YOU own the runtime. Never ask them to install Python, pip,
a venv, or Cursor plugins.

Every session:

```bash
./pakket instruct --json
./pakket cite "<query>" --json
```

## Runtime (you fix it, not the human)

1. Prefer `./pakket` in this repo (shell over MCP).
2. If `python3` is missing, install it yourself (Linux:
   `sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip`;
   macOS: `brew install python`), then retry `./pakket`.
3. `./pakket` creates `.venv` and installs Typer/Rich/Pydantic on first run.
4. If bootstrap returns `error_type: incomplete` with `agent_fix`, follow
   `agent_fix.do`. Never surface that as a homework list for the human.

## Rules

- Narrate `data.verdict` first (`cite` / `thin` / `none` / `ambiguous`).
- Then the source block: quote only `source.verbatim` or `source.quotation`.
  Never present `source.paraphrase` as ZIN’s words.
- If `source.verbatim` is null, give `source.url` and the local path, and say
  the extract is absent (`source.note`).
- Never scrape zorginstituutnederland.nl.
- Never open the xlsx to answer.
- Never silent-match on ambiguous ids.
- Never invent dates, ICERs, or budget figures.
- If `instruct` and any skill disagree, trust `instruct`.

- Prefer files under `assets/zin/`. New drops go in `assets/drop/` then
  `python scripts/ingest_assets.py` (maintainer). Never scrape ZIN.
