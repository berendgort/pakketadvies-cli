# STATE — 25 September 2026

## Counts (database `db/ZIN_pakketadviezen_database.xlsx`)
| Sheet | Rows | Argumenten volledig | Basisgegevens | Index (ongoing) |
|---|---|---|---|---|
| Intramuraal | 174 | 163 | 0 | 11 |
| GVS | 315 | 260 | 27 | 28 |
| Argumenten | 1,372 rows (776 INT, 596 GVS) | | | |

## Remaining GVS dossiers with status "Basisgegevens" (27)
See `STATE_remaining.txt` (ID | datum | titel). They are all 2025–2026 advices:
GVS-350 CGRP-remmers EM · 352 methylprednisolon · 353 berotralstat · 354 deflazacort · 356 setmelanotide BBS (afgewezen) · 357 vibegron ·
358 maralixibat PFIC · 359 benralizumab EGPA · 360 PCV20 · 361 Acarizax voorwaarden · 366 eplontersen · 367 garadacimab · 368 nirsevimab ·
369 danicopan · 370 Ryeqo vervallen voorwaarden · 371 ofatumumab niet wijzigen · 372 odevixibat Kayfanda · 373 sildenafil/tadalafil ·
374 atogepant EM · 377 enalapril kinderen · 378 bempedoïnezuur · 380 abaloparatide · 381 olezarsen · 382 levodopa inhalatie · 384 tirzepatide obesitas · 387 fezolinetant.

## In progress (not applied)
- `batch94_body.py` (GVS-350, 352, 353, 354, 356, 357) is fully drafted from the letters; the argument file `batch94_args.py` still has to be written, then `validate.py batch94 && fill_db.py batch94`. Not included in this package to avoid confusion; the analyst can finish it in the current session.

## Corrections applied to the ZIN index during extraction (examples; all logged in `Opmerkingen`)
GVS-301 Sibnayal → Niet opnemen (bijlage 3A) · GVS-305 midazolam → 1B · GVS-250 fostemsavir → 1B · GVS-291 mifepriston type → Initieel ·
GVS-330 zilucoplan → Opnemen na prijsonderhandeling · GVS-342 Kaftrio 2–5 → Opnemen na prijsonderhandeling · GVS-353 berotralstat → 1B ·
GVS-356 setmelanotide BBS → Niet opnemen · GVS-324 Yescarta = sluisadvies in GVS-index (registratiehouder Kite/Gilead aangevuld) ·
GVS-388/399/113/142/175 (earlier sessions).

## Known gaps
- GVS-194 racecadotril, GVS-385 linzagolix, GVS-386 donidalorsen: no PDF found.
- Index snapshot 09-09-2026; anything ZIN published later is not indexed.
- `nld` tesseract model was not available; OCR done with `eng`.
