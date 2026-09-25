# Voor mensen zonder tech-achtergrond

## Wat dit is

Een hulpmiddel bij Zorginstituut Nederland (ZIN) pakketadviezen over
geneesmiddelen. Je vraagt iets in gewone taal. Je AI zoekt in deze
database en zegt welk argument je kunt hergebruiken, uit welk dossier,
op welke datum.

Je hoeft de Excel niet te openen. Je hoeft geen programma te installeren.

## Wat jij doet

1. Kopieer de link: `https://github.com/berendgort/pakketadvies`
2. Plak die in Cursor, Claude, of een andere AI die een GitHub-repo kan openen
3. Stel je vraag, bijvoorbeeld:
   - "Wanneer gebruikte ZIN voor het eerst een extern controlecohort?"
   - "Welk precedent past bij single-arm data in de derde lijn?"
   - "Laat ARG-0001 zien"
4. Lees het antwoord: eerst het oordeel (cite / thin / none), dan dossier en datum

## Wat jij niet doet

- Python installeren
- Een terminal openen (tenzij je AI dat zelf doet)
- `pip` of `venv` draaien
- De spreadsheet downloaden om te zoeken
- De ZIN-website scrapen

Als de AI jou vraagt om software te installeren, zeg: *doe dat zelf volgens
AGENTS.md / instruct*. Dat is het contract.

## Wat de AI moet doen

De AI volgt [AGENTS.md](../AGENTS.md) en `./pakket instruct --json`:
runtime regelen, daarna `cite`, daarna in mensentaal antwoorden.
