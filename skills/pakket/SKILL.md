---
name: pakket
description: >
  When the user pastes github.com/berendgort/pakketadvies or asks about ZIN
  pakketadviezen, arguments, or precedents: YOU run ./pakket (install Python
  yourself if needed; never ask the human). Then instruct and cite. Never
  scrape ZIN. Never open the xlsx.
---

# pakket - agent skill

Humans are often non-technical. They only paste the repo link. YOU own the
runtime and the citation call.

## Every session

```bash
./pakket instruct --json
./pakket cite "<what they would search the sheet for>" --json
```

If `python3` is missing: install it yourself (apt/brew), then retry. Follow
`agent_fix` on incomplete errors. Never ask the human to install software.

Trust `instruct` over this file if they disagree.

## Narrate

Lead with `data.verdict` in plain language. Then dossier id, advice date, and
the precedent sentence. Do not dump the full shortlist table to the human.

## Never

- scrape zorginstituutnederland.nl
- open the xlsx to answer
- silent first-match on ambiguous ids
- invent dates, ICERs, or budget figures
- ask the human to install Python, pip, or a venv
