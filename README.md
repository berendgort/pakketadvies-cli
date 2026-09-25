![Pakketadvies](docs/banner.png)

# Pakketadvies

Welk ZIN-argument kun je hergebruiken, uit welk dossier, op welke datum?
Zonder zelf in de spreadsheet te zoeken.

## Voor jou (niet technisch)

1. Stuur deze link naar je AI (Cursor, Claude, ChatGPT met code, Copilot, …):
   **https://github.com/berendgort/pakketadvies**
2. Zeg bijvoorbeeld: *zoek wanneer ZIN voor het eerst een extern controlecohort accepteerde*
3. Klaar. Jij installeert niets. Geen Python, geen terminal, geen spreadsheet.

De AI opent deze repo en draait zelf `./pakket`. Als er iets ontbreekt (zoals
Python), lost de AI dat op. Vraag niet aan jou om software te installeren.
Meer uitleg: [docs/for-humans.md](docs/for-humans.md).

## Voor de AI

```bash
./pakket instruct --json
./pakket cite "extern controlecohort" --json
```

Voorbeeld: verdict **cite**, vroegste doorslaggevende treffer, daarna shortlist
zodat latere omkeringen zichtbaar blijven zonder de xlsx.

| Dekking | Stand (as_of 2026-09-24) |
|---|---|
| Intramuraal | 174 dossiers, 163 argumenten volledig |
| GVS | 315 dossiers, 260 argumenten volledig, 27 basisgegevens |
| Argumentrijen | **1.372** (776 INT, 596 GVS) |
| Bronnen | GVS PDF-delen + 295 tekstextracten + INT-sample |

Nieuwe zips: zet ze in `assets/drop/`, daarna `python scripts/ingest_assets.py`.
Bronlayout: [docs/source-data.md](docs/source-data.md) · [assets/README.md](assets/README.md).

Een ander agentschap is een map onder `data/`, niet een andere CLI.
Agents: [AGENTS.md](AGENTS.md). Paraphrases zijn geen citaten van ZIN.
