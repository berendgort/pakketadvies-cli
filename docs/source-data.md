# Source data layout

## Drop workflow

1. Put new zips or xlsx in [`assets/drop/`](../assets/drop/).
2. Run `python scripts/ingest_assets.py`.
3. `./pakket cite` reads the refreshed `data/zin/v1/`.

Classification is automatic from zip contents (INT folders, GVS folders,
workbook, text extracts, handover pack). Unknown files stay in `drop/`.

## INT vs GVS

**ZIN** is the institute. Inside it:

| | Intramuraal (`INT-*`) | GVS (`GVS-*`) |
|---|---|---|
| Meaning | Sluis / hospital drugs | Pharmacy reimbursement system |
| Filter | `--traject Intramuraal` | `--traject GVS` |
| Bundles | `assets/zin/bundles/int/` | `assets/zin/bundles/gvs/` |

## Tree

```text
assets/
  drop/
  zin/
    workbook/ZIN_pakketadviezen_database.xlsx
    bundles/int/*.zip
    bundles/gvs/*.zip
    extracts/*.zip
    brief/PROJECT_BRIEF.md
    meta/*_bundle_manifest.json
data/zin/v1/          # projection for the CLI (arguments, dossiers, sources)
```

## Gold counts (as_of 2026-09-24)

Intramuraal 174 (163 fully argued). GVS 315 (260 fully argued, 27 basisgegevens).
Arguments 1,372. See `assets/zin/brief/STATE.md`.

## Agent rule

Do not scrape ZIN. Prefer files already under `assets/zin/`. Maintainers only
run `scripts/ingest_assets.py` after dropping files.
