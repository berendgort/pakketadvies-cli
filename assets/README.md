# assets/

Drop new files in **`drop/`**, then run:

```bash
python scripts/ingest_assets.py
```

That classifies each zip/xlsx, files it under `zin/`, rebuilds manifests, and
projects `data/zin/v1/` for `./pakket`.

## Layout

```text
assets/
  drop/                 <- put new zips/xlsx here
  zin/
    workbook/           gold Excel + codebook (one writer)
    bundles/
      int/              intramural PDF zips (INT-* folders inside)
      gvs/              GVS PDF zips (GVS-* folders inside)
    extracts/           section text zips (GVS-NNN__*.txt)
    brief/              PROJECT_BRIEF + STATE
    meta/               generated manifests (do not edit)
```

## Auto categories

| Content of the zip | Lands in |
|---|---|
| folders `INT-123/...` | `zin/bundles/int/` |
| folders `GVS-123/...` | `zin/bundles/gvs/` |
| `ZIN_pakketadviezen_database.xlsx` or handover pack | `zin/workbook/` (+ brief/extracts) |
| many `GVS-*__*.txt` | `zin/extracts/` |

Unknown files stay in `drop/` with a log line.

PDF bundles under `zin/bundles/` stay on disk only (gitignored; GitHub
file limit). The searchable corpus in `data/zin/v1/` is what gets committed.

**ZIN** = the institute. **INT** = hospital track. **GVS** = pharmacy track.
Details: [docs/source-data.md](../docs/source-data.md).
