"""Agent recipe text (CLI instruct + MCP)."""

from __future__ import annotations

from typing import Any

__all__ = (
    "INSTRUCT_STEPS",
    "INSTRUCT_SUMMARY",
    "instruct_payload",
)

INSTRUCT_SUMMARY = (
    "Humans only paste the GitHub link. YOU run ./pakket. Fix Python/venv "
    "yourself; never ask them to install anything. Then ./pakket cite "
    '"<query>" --json. Verdict first. Never scrape ZIN. Never open the xlsx. '
    "Never silent-match. Never invent a date or an ICER."
)

INSTRUCT_STEPS: list[dict[str, Any]] = [
    {
        "step": 0,
        "action": "runtime_for_non_technical_human",
        "command": "./pakket instruct --json",
        "detail": (
            "Audience is often non-technical. They opened this repo via a link. "
            "YOU own the machine: if python3 is missing, install it (apt/brew) "
            "without asking. ./pakket bootstraps .venv + Typer/Rich/Pydantic. "
            "On incomplete + agent_fix: follow agent_fix.do. Never tell the "
            "human to install Python, pip, or open a terminal tutorial."
        ),
    },
    {
        "step": 1,
        "action": "use_repo_cli",
        "command": "./pakket instruct --json",
        "detail": (
            "ONE PATH: ./pakket in this repo. No pipx for the human. "
            "Prefer the shell over MCP. Trust instruct over any stale skill."
        ),
    },
    {
        "step": 2,
        "action": "cite",
        "command": './pakket cite "<what they would search the sheet for>" --json',
        "detail": (
            "Main question: which argument to reuse. Read data.verdict first "
            "(cite / thin / none / ambiguous). Then dossier, date, precedent. "
            "data.shortlist is ordered: first row is the call, later rows are "
            "what followed. Answer in plain language. Do not dump the table."
        ),
    },
    {
        "step": 3,
        "action": "show_if_needed",
        "command": "./pakket show <id> --json",
        "detail": (
            "When you already have zin:ARG-0001 or INT-147. Bare ids work "
            "while only ZIN is loaded. Ambiguous ids return candidates."
        ),
    },
    {
        "step": 4,
        "action": "never",
        "command": None,
        "detail": (
            "Never scrape zorginstituutnederland.nl. Never open the xlsx to "
            "answer. Never pick the first ambiguous hit. Never invent numbers. "
            "Never ask the human to install software."
        ),
    },
]


def instruct_payload() -> dict[str, Any]:
    return {
        "summary": INSTRUCT_SUMMARY,
        "preset": "FIRST_USE",
        "audience": "non_technical_human_plus_any_ai",
        "human_path": (
            "Paste https://github.com/berendgort/pakketadvies-cli into any AI "
            "that can open a repo. Ask in plain language. Install nothing."
        ),
        "objective": (
            "Cite the ZIN argument to reuse so the writer never opens the sheet."
        ),
        "steps": INSTRUCT_STEPS,
        "verbs": {
            "cite": './pakket cite "<query>" --json',
            "show": "./pakket show <id> --json",
            "instruct": "./pakket instruct --json",
        },
        "narrate": (
            "Lead with verdict in plain language. Then the source block: "
            "quote only source.verbatim or source.quotation; never present "
            "source.paraphrase as ZIN's words. Give URL and local paths. "
            "Shortlist stays in JSON."
        ),
        "never": [
            "scrape ZIN HTML",
            "open the xlsx to answer",
            "silent first-match on ambiguous ids",
            "invent dates, ICERs, or budget figures",
            "ask the human to install Python, pip, or a venv",
        ],
        "agent_fix": {
            "python_missing_linux": (
                "sudo apt-get update && sudo apt-get install -y "
                "python3 python3-venv python3-pip"
            ),
            "python_missing_macos": "brew install python",
            "then": "./pakket instruct --json",
        },
    }
