# PROJECT BRIEF — "ZIN Pakketadviezen Knowledge Base" (hand-over to CLI/agent engineer)

*Version 1.0 · 25 September 2026 · written as a self-contained prompt. Everything a builder needs to design a reusable CLI that ingests new Zorginstituut documents, extracts them into our structured schema, validates them, writes them into the knowledge base, and makes the base queryable for precedent research.*

---

## 0. TL;DR

We have built, over ~90 LLM-assisted "batches", a structured database of **every Dutch drug reimbursement advice** published by **Zorginstituut Nederland (ZIN)** since 2015: 174 intramural ("sluis") dossiers and 315 extramural ("GVS") dossiers, with **1,372 coded argument rows** describing *how ZIN reasons*. It lives in one Excel workbook (`db/ZIN_pakketadviezen_database.xlsx`) with a controlled vocabulary (Codeboek). The extraction was done by reading the PDF bundles (letter to the minister + pharmacotherapeutic report + health-economic report + budget impact analysis + ACP advice) and writing Python "batch files" that a small script applies to the workbook.

The manual pipeline works but is not reusable: every batch is hand-written, provenance is loose, there is no query layer, and adding a newly published ZIN advice requires a human-in-the-loop LLM session. **We want a CLI + knowledge base** that makes this repeatable: `ingest → extract → validate → review → commit → query`, with the existing 423 completed dossiers as a gold standard for regression-testing extraction prompts.

Everything below is context, schema, rules, pitfalls and requirements. Section 9 is the concrete ask.

---

## 1. Domain background (what these documents are)

**Zorginstituut Nederland (ZIN)** advises the Dutch Minister of Health on whether a medicine should be reimbursed from the basic health insurance package. Two tracks:

| Track | Dutch term | What it is | Our sheet |
|---|---|---|---|
| **Extramural** | **GVS** (Geneesmiddelenvergoedingssysteem) | Outpatient/pharmacy drugs. A new drug is either **clustered** with interchangeable drugs on **bijlage 1A** (reimbursement limit = cluster price, possible co-payment), placed as a unique drug on **bijlage 1B** (full reimbursement), and/or restricted by **bijlage 2** conditions (indication text, prior therapy, prescriber, stop rules). Since ~2020 also price negotiation advice and class-wide reviews ("herbeoordeling", "uitstroom"). | `GVS` (IDs `GVS-101…GVS-399`; `GVS-001…016` = ongoing agenda) |
| **Intramural** | **sluis / pakketadvies** specialistische geneesmiddelen | Expensive hospital drugs placed in the "sluis" (lock). ZIN assesses the four package criteria and advises the minister to negotiate a price (often a required % reduction). | `Intramuraal` (IDs `INT-001…`) |

**The four pakketcriteria** ZIN applies: *effectiviteit* (stand van de wetenschap en praktijk, SWP — is it proven effective vs. Dutch standard care?), *kosteneffectiviteit* (ICER vs. a reference value tied to disease burden: €20k / €50k / €80k per QALY), *noodzakelijkheid* (disease burden, necessity to insure), *uitvoerbaarheid* (budget impact, feasibility, appropriate use). Two advisory bodies: **WAR** (scientific council — evidence) and **ACP** (Adviescommissie Pakket — societal weighing/appraisal).

**A dossier bundle** (one folder of PDFs per advice) typically contains:
- **Brief aan de minister** (the advice letter, 2–6 pages) — *authoritative source for the outcome and conditions*;
- **GVS-rapport** (interchangeability/cluster test, standard dose) — GVS only;
- **Farmacotherapeutisch rapport (FT)** — clinical evidence, GRADE, comparator, therapeutic value;
- **Farmaco-economisch rapport (FE)** — cost-effectiveness model review, ICERs, required price reduction;
- **Budgetimpactanalyse (BIA)** — patient numbers, €/year, substitution;
- **ACP-advies / verslag** — appraisal, inspraak (stakeholder input);
- occasionally **WAR-verslag**, **kostenconsequentieraming (KCR)**, consultation responses.

Key vocabulary you will see everywhere: *meerwaarde / gelijke waarde / minderwaarde* (added / equal / lesser therapeutic value), *onderling vervangbaar* (interchangeable → cluster), *standaarddosis* (defined daily dose used for the cluster limit), *bijlage 2-voorwaarde* (reimbursement condition text), *FE-vrijstelling* (exemption from health-economic analysis when budget impact < €10 mln, before 2020 < €2.5 mln), *referentiewaarde*, *ziektelast*, *marginale toets* (light-touch cluster test), *briefrapport* (short letter-only advice), *parallelle procedure CBG-ZIN* (registration and reimbursement in parallel), *voorwaardelijke toelating (VT)* (conditional admission with registry), *status aparte* (HIV drugs and immunoglobulins go to 1B without assessment), *bereiding / apotheekbereiding* (pharmacy compounding — often the de-facto comparator and price anchor), *arrangement* (confidential price agreement between VWS and manufacturer).

Source of truth: ZIN publishes every advice at `https://www.zorginstituutnederland.nl/publicaties/adviezen/...`; content is CC0. Overview pages: sluis index, "werkagenda overzicht pakketadviezen", "werkagenda overzicht GVS-adviezen" (URLs in `docs/leeswijzer_database.md`). Each row of our index has the document-page URL (`db/index_dossiers.csv`).

---

## 2. What we have built (the deliverable so far)

`db/ZIN_pakketadviezen_database.xlsx` — six sheets:

| Sheet | Rows | Purpose |
|---|---|---|
| **Leeswijzer** | – | Reading guide, column legend, fill-in examples, sources, limitations (exported as `docs/leeswijzer_database.md`) |
| **Intramuraal** | 174 dossiers | Register of sluis advices; 39 columns; 163 = "Argumenten volledig", 11 = ongoing ("Index") |
| **GVS** | 315 dossiers | Register of GVS advices; 39 columns; 260 = "Argumenten volledig", 27 = "Basisgegevens" (still to deepen), 28 = ongoing |
| **Argumenten** | 1,372 rows | **The core**: one row per argument ZIN uses, coded by pakketcriterium + thema, with paraphrase, ZIN's position vs. the manufacturer's claim, weight, precedent value, source document, section, keywords |
| **Codeboek** | 23 lists + 19 definitions | Controlled vocabulary behind all dropdowns (exported as `db/codeboek.json`) |
| **Overzicht** | formulas | Live counts per year / outcome / criterion / therapeutic area |

Column names are exact and are the contract for any writer (`db/schema_columns.json`). Grey-header columns come from the ZIN index (title-derived, marked `*`), yellow-header columns are extracted from the dossier, green are formulas.

**GVS register — the extracted fields per dossier** (Dutch names verbatim; the `*`-fields are dropdowns validated against the Codeboek):

`Type advies*` · `Indicatiegroep (ziekte)*` · `Behandellijn*` · `Registratiehouder` · `Weesgeneesmiddel` · `Aanvraag (1A / 1B / bijlage 2)` · `Cluster / vergelijkbare middelen (1A)` · `Stand van wetenschap en praktijk (ZIN)` · `SW&P: kernreden oordeel (categorie)` · `SW&P: waarom positief/negatief (onderbouwing)` · `Therapeutische waarde t.o.v. standaardbehandeling (ZIN)` · `Comparator (ZIN)` · `Bijlage 2-voorwaarden (tekst)` · `FE-rapport beoordeeld` · `Ziektelast (0–1)` · `Referentiewaarde (€/QALY)` · `ICER fabrikant (€/QALY)` · `ICER ZIN basecase (€/QALY)` · `Kosteneffectief volgens ZIN` · `Geadviseerde prijsreductie (%)` · `Budgetimpact ZIN (€ mln/jaar)` · `Aantal patiënten/jaar (ZIN)` · `ACP-advies (kern)` · `Kernargumenten ZIN (samenvatting)` · `Besluit minister / opname GVS (datum, Stcrt.)` · `Uitkomst advies` · `Status extractie` · `Opmerkingen`

(The Intramuraal register has the same skeleton with `Claim fabrikant`, `Datum sluisplaatsing`, `Voorwaarden / gepast gebruik`, `Datum opname basispakket` instead of the GVS-specific cluster/bijlage-2 fields.)

**Argumenten — one row per argument** (columns): `Argument-ID` (formula) · `Dossier-ID` · `Traject` · `Geneesmiddel` · `Datum advies` · `Therapeutisch gebied` · `Indicatiegroep` · `Behandellijn` (the last five are looked up from the register) · **`Pakketcriterium`** (7 values) · **`Thema`** (22 values) · **`Argument ZIN (parafrase in eigen woorden)`** · **`Positie ZIN t.o.v. claim fabrikant`** (Ondersteunt / Verwerpt / Nuanceert-voorwaardelijk / Eigen initiatief ZIN) · **`Gewicht in advies`** (Doorslaggevend / Ondersteunend / Zijdelings) · **`Precedentwaarde / herbruikbaar voor`** · **`Brondocument`** · **`Pagina / sectie`** · `Citaat (kort, optioneel)` · **`Trefwoorden`** · `Ingevoerd door` · `Datum invoer` · `Gecontroleerd`.

The 22 **thema's** are the taxonomy of ZIN reasoning we settled on: Comparator / gebruikelijke zorg · Indirecte vergelijking / NMA · Single-arm / ongecontroleerde data · Surrogaat-eindpunt vs. harde uitkomst · Extrapolatie / tijdshorizon / overlevingscurves · Kwaliteit van leven / utiliteiten · Cross-over / treatment switching · Subgroep / indicatiebeperking · Onzekerheid / GRADE / bewijskracht · Klinische relevantie / MCID · Ziektelast / proportional shortfall · Weesgeneesmiddel / kleine populatie · Prijs / kortingsadvies / ICER-drempel · Budgetimpact / patiëntaantallen / verdringing · Pay-for-performance / uitkomstafspraken / registratie · Start- en stopcriteria / gepast gebruik · Combinatietherapie / prijsverdeling · Dosering / verspilling / toediening · Bijlage 2-voorwaarden (GVS) · Clusterindeling / vergoedingslimiet (GVS) · Registratie / off-label / EMA-status · Overig.

---

## 3. The purpose — why this knowledge base exists

The users are people who prepare or evaluate reimbursement dossiers (pharma market access, HTA consultants, policy researchers). They need to answer questions like:

- *"Has ZIN ever accepted single-arm data as proof of added value? Under what conditions?"* → filter Argumenten on thema *Single-arm* + positie *Ondersteunt*, read precedents (e.g. asfotase alfa, setmelanotide POMC/LEPR, risdiplam 0–2 months) and the counter-examples (setmelanotide BBS rejected, GVS-356).
- *"What price reduction does ZIN ask when the ICER is 1.3× the reference value?"* → structured fields ICER/referentiewaarde/prijsreductie.
- *"How does ZIN treat a new oral variant of an injectable class?"* → pattern: toedieningsweg blocks clustering → 1B with mirrored bijlage-2 (Rybelsus, atogepant, roxadustat).
- *"Which conditions did ZIN attach to expensive orphan drugs without an FE?"* → expertisecentrum-eis, indicatiecommissie, stop rules.
- *"What did the ACP say about drugs with low disease burden?"*
- *"When a new advice is published tomorrow, what precedents does it cite or contradict?"*

So the base must support (a) **structured filtering** over the register fields, (b) **semantic/precedent search** over paraphrased arguments with provenance back to the PDF section, and (c) **incremental growth** as ZIN publishes ~40–60 new advices per year and amends conditions of existing ones.

---

## 4. How the extraction was done (the methodology to automate)

Per dossier, the analyst (Claude in a sandbox) did the following; this is effectively the extraction prompt:

1. **Locate sections** in the extracted text: `## BRIEF (volledig)`, `## FT – SAMENVATTING`, `## FT – CONCLUSIE`, `## FE – SAMENVATTING/DISCUSSIE/CONCLUSIE`, `## BIA – CONCLUSIE`, `## ACP …`, `## WAR …`, `## OVERIG` (produced by `tools/zin_extract.py`). Read the **letter fully**; read FT/FE/BIA conclusions; read the ACP section fully when present. For GVS: the letter follows a fixed order — onderlinge vervangbaarheid → therapeutische waarde → (kosteneffectiviteit) → budgetimpact → advies + bijlage-2 text → (voorwaardelijke toelating).
2. **Fill the register fields.** Rules that emerged:
   - The **letter's advice paragraph is authoritative** for `Uitkomst advies`; the ZIN-index title is often wrong or coarse (we corrected ~25 outcomes, e.g. Sibnayal "Opnemen met bijlage 2" → "Niet opnemen"; zilucoplan → "Opnemen na prijsonderhandeling" because ZIN explicitly advised negotiations). Every correction is logged in `Opmerkingen`.
   - **Bijlage-2 text is copied literally** (quoted), not paraphrased — users need the exact wording.
   - Numbers as numbers where a numeric column exists (ICER, referentiewaarde, budgetimpact in € mln, patients); ranges and scenarios go into text with the base case first.
   - `SW&P: kernreden oordeel` is a **13-value category** (e.g. *Directe RCT met klinisch relevant effect*, *Indirecte vergelijking geaccepteerd*, *Alleen subgroep onderbouwd (deels)*, *Single-arm geaccepteerd (natuurlijk beloop als controle)*, *Niet beoordeeld (procedureel)*) — pick the one that explains the verdict.
   - `SW&P: waarom positief/negatief` is a dense paragraph: verdict first, then trials (names, n, effect sizes with CIs), comparator, GRADE/uncertainty remarks, safety, and any explicit ZIN caveats — in ZIN's voice.
   - `Kernargumenten ZIN (samenvatting)` = 2–3 numbered *patterns* — what is generalisable about this dossier (precedent value), cross-referenced to related dossiers by ID.
   - `ACP-advies (kern)`: "Geen ACP-advies." unless the bundle has one; when it does, summarise the commission's considerations and inspraak.
   - Provenance in `Opmerkingen`: which documents were read, page counts, OCR used, corrections made.
3. **Write 1–3 (sometimes up to 7) argument rows.** Completeness = everything the source supports, not a fixed count. A short *marginale toets* letter legitimately yields one argument (clustering + standard dose); a sluis dossier with FE and ACP yields 3–7. Each row: paraphrase in our own words *with the numbers*, ZIN's position vs. the claim, weight, a one-sentence precedent statement ("what this dossier establishes"), source document + section, keywords (drug, brand, indication, trial names, key numbers, concepts).
4. **Validate against the Codeboek** (`tools/validate.py`), **apply** (`tools/fill_db.py batchNN`), **recalculate** formulas (`tools/recalc.py`, needs LibreOffice), back up the workbook, and record the batch in the journal.

Quality bar we held ourselves to: *compleetheid gaat vóór tempo*; never invent numbers; when the letter and the FT disagree, the letter wins for outcome and the FT for evidence detail; when a value is not in the dossier, write "Niet geraamd / Niet exact vermeld", not a guess.

---

## 5. Existing tooling (what can be reused vs. rewritten)

| File | Role | Reuse? |
|---|---|---|
| `tools/zin_extract.py` | PyMuPDF-based. Recursively reads `zips/<DOSSIER-ID>/*.pdf`, classifies pages (letter / FT / FE / BIA / ACP / WAR / KCR), writes one `<ID>__<file>.txt` per PDF with the letter in full and only *samenvatting/discussie/conclusie* of the reports, plus a rule-based `zin_metadata.csv` (dates, ICERs, budget impact, patient numbers, `needs_ocr` flag). Idempotent via state file. | Yes — good starting point; section detection is heuristic and sometimes mislabels (GVS-rapport + letter in one PDF → "BRIEF:17p"); OCR path exists but only `eng` tesseract model was available (Dutch `nld` missing). |
| `tools/pdftext.py` | Dumps full text per page (`fulltext/<ID>__k.txt`) for deep reading. | Yes |
| `tools/readletter.sh`, `gvskey.sh`, `gvsadv.sh`, `gvsq.sh` | grep/sed helpers to strip ZIN letterhead boilerplate and pull key sentences. | Replace by proper text cleaning |
| `tools/batch_header.py` + `batch_argdef.py` | Constants mapping short names to exact column names / codebook values; the `A(...)` helper that builds argument dicts. | Encode as a JSON Schema instead |
| `tools/fill_db.py` | Applies a batch module's `DOSSIERS` (dict ID → {column: value}) and `ARGUMENTEN` (list of dicts) to the workbook: finds the row by ID, writes fields, appends arguments, restores all dropdown validations. Only accepts codebook values for dropdown columns. | Keep as the xlsx writer, or re-implement in the CLI |
| `tools/validate.py` | Pre-flight check of a batch module against the Codeboek lists and column names. | Fold into schema validation |
| `tools/recalc.py` | LibreOffice headless recalculation + formula error scan (from Anthropic's xlsx skill). | Optional |
| `examples/batch*.py` | Worked examples of the target output for GVS (87, 90, 93) and intramural (45). **These show exactly what a good extraction looks like** — use them as few-shot examples and as test oracles. | Yes |
| `data/zin_text_extracts_295.zip` | The 295 section-structured text extracts for all GVS PDFs (the input the analyst read). The raw PDFs (663 MB) are not included; re-download via the URLs in `db/index_dossiers.csv` if needed. | Yes — test corpus |
| `db/argumenten_export.csv`, `db/index_dossiers.csv`, `db/codeboek.json`, `db/schema_columns.json` | Flat exports for KB bootstrapping. | Yes |

---

## 6. Known pitfalls (learned the hard way)

1. **Duplicate index entries** (same PDF under two URLs): GVS-109/110, 144/145, 171/172, 186/187, 241/242, 248/251, 267/268, 273/289, 304/311, 383/387. The second is marked; don't process twice. Dedup by content hash.
2. **Scanned PDFs** need OCR: GVS-207, 217, 282, 341; INT-032. Tesseract `eng` works acceptably on Dutch; install `nld`.
3. **Misclassified items**: GVS-324 (Yescarta) is a sluis advice living in the GVS index; GVS-350 has two letters (pakketadvies + later bijlage-2 text); several dossiers have a *gecorrigeerde versie* (corrected letter) — keep both, mark superseded.
4. **Section detection is fragile** in short GVS letters (letter + GVS-rapport in one PDF; "Advies" heading appears twice; OVERIG fallback). A robust approach: classify by page (letterhead, "Geachte", report title pages) then by heading regex, and keep page numbers for provenance.
5. **Index titles lie about outcomes** (see §4). Always derive `Uitkomst advies` from the letter's *Advies* paragraph; flag disagreements for review rather than auto-overwrite.
6. **Defaults that were wrong**: `ACP-advies (kern)` = "Geen ACP." while an ACP section existed; `FE-rapport beoordeeld` = "Nee" while the bundle contained an FE. Derive these from the detected document types.
7. **Numbers**: ICERs appear as "€ 65.910 per QALY" (Dutch thousands separator), percentages as "ten minste 20%", budget impact as "€ 4,7 tot € 9,3 miljoen in jaar 3". Normalise carefully; keep the original string.
8. **Two-step advices**: some dossiers span two letters months apart (tezepelumab Aug/Dec 2023; CGRP March/June 2025; Ryeqo 2022 + 2024). Model "advice events" per dossier, not one letter per dossier.
9. **Codebook drift**: lists were extended a few times during the project (e.g. added *Single-arm geaccepteerd (natuurlijk beloop als controle)*). The KB must version the vocabulary and validate against it.

---

## 7. Recurring ZIN reasoning patterns (useful for KB taxonomy, evals and retrieval tests)

A non-exhaustive list of patterns the 1,372 arguments encode — good candidates for tagged "concept" nodes in the KB:

- *Toedieningsweg blokkeert clustering → 1B als functioneel cluster-equivalent met gespiegelde bijlage 2* (Rybelsus GVS-202, roxadustat 240, atogepant 340).
- *Klasse-toetreder herreguleert de zittende*: a new entrant triggers a cluster, moving the incumbent from 1B to 1A with a limit and sometimes adding a bijlage 2 (Acarizax/Actair 279, ofatumumab/natalizumab-SC 277, tezepelumab/benralizumab/omalizumab 311/322/329, odevixibat/maralixibat 334, naloxegol/naldemedine 325).
- *Bereidingsprijs als anker* — the pharmacy compounding is the comparator and the price anchor; a registered product without added value at a much higher price is rejected on solidarity grounds (CDCA GVS-166, mexiletine 216, **Sibnayal 301 → bijlage 3A**), but inconsistently applied (Nasolam 323, Alkindi 192).
- *Gebruiksgemak is geen meerwaarde* … except when lay persons administer in emergencies (glucagon nasal/SC 209/302).
- *Single-arm evidence accepted when natural history is a valid control* (asfotase alfa 175, risdiplam 0–2 m 315, Orkambi/Kaftrio leeftijdsuitbreidingen), *rejected when blinded phase is short and open-label extension carries the effect* (setmelanotide BBS 356).
- *Arrangement-automatiek* for indication/age extensions under a portfolio price agreement (Kaftrio 257/266) — and its reversal (Kaftrio 2–5 yr 342: ≥75% reduction demanded; niet-F508del 375 "maatschappelijk onverantwoord").
- *FE-vrijstelling by patient numbers despite very high cost per patient* — repeated system signal (volanesorsen 252, setmelanotide 270, odevixibat 284) → "casus voor evaluatie van de FE-criteria".
- *"Gelijke waarde = gelijke prijs" bestendigt niet-kosteneffectieve prijzen* — explicit signal (zilucoplan 330, rozanolixizumab 347, berotralstat 353).
- *Bijlage 2 life-cycle*: introduced → practice crystallises → condition dropped (TPO-RA splenectomy rule 229, patiromeer 288, fampridine looptest 275, SGLT2 all conditions 2025).
- *Conditional FE exemption with spending monitor* (baricitinib 327, Palforzia 344).
- *Expertisecentrum / indicatiecommissie as gatekeeper* for ultra-expensive drugs (setmelanotide 270, zilucoplan 330, solriamfetol-OSA 316).
- *Domain anomaly extramuraal/intramuraal via afbakeningsbrief 2014* → dubbele bekostiging (biologicals for asthma; gMG drugs).
- *Afwegingskader "noodzakelijk te verzekeren"* for cheap drugs with OTC alternatives (codeïne 320 partial uitstroom; allergiemiddelen 399 no uitstroom).
- *Declaratiedata as correction on BIA and appraisal* (CGRP 350: spending €31 mln vs. €15.7 mln forecast → ACP demands appropriate-use enforcement).

---

## 8. Current state and open work

- Intramuraal: complete for all published advices (163 "Argumenten volledig"; 11 ongoing).
- GVS: 260 complete, **27 remaining** with status "Basisgegevens" (list in `STATE.md`), all 2025–2026 advices; a drafted-but-unapplied batch (`batch94_body.py`, six dossiers GVS-350/352/353/354/356/357) is described in `STATE.md`.
- Ongoing ZIN agenda items (status "Index", 39 rows) become dossiers when published.
- ZIN publishes continuously; the index snapshot dates from 09-09-2026 — new items since then are missing.

---

## 9. The ask — a reusable CLI and knowledge base

Design goals: **reproducible, incremental, provenance-first, human-reviewable, testable against the existing corpus.** Suggested command surface (names indicative):

```
zin sync        # scrape ZIN overview pages / RSS → detect new or changed advices → add index rows (ID, date, title, URL)
zin fetch ID    # download the PDF bundle for a dossier (document page → all attachments), hash, store under data/raw/<ID>/
zin extract ID  # PDF → text (PyMuPDF; OCR fallback with tesseract nld) → page/section segmentation → data/text/<ID>.json (sections with page refs)
zin draft ID    # LLM extraction → data/draft/<ID>.json conforming to schema (register fields + argument rows), with per-field source spans; few-shot from examples/
zin review ID   # show draft vs. schema/codebook validation, diffs vs. existing row (for amendments), flags (outcome ≠ index title, missing ACP/FE detection, low-confidence fields); accept/edit/reject
zin commit ID   # write to the canonical store (SQLite/Parquet), append to journal, export xlsx (fill_db-compatible) and CSVs; recalc formulas
zin query ...   # structured filters (--thema, --criterium, --positie, --uitkomst, --jaar, --gebied) + semantic search over paraphrases/citations with citations back to ID + section + page
zin eval        # run the extraction prompt on N already-completed dossiers and score field agreement / argument recall vs. the gold rows
```

Requirements and preferences:

1. **Canonical store ≠ Excel.** Keep a proper store (SQLite is fine; one table per sheet + documents/sections/provenance tables) and treat the xlsx as an *export* that stays byte-compatible with the current workbook (same sheets, columns, dropdowns via Codeboek, formulas in Overzicht). Analysts will keep using Excel.
2. **Schema as code.** Turn `db/schema_columns.json` + `db/codeboek.json` into a versioned JSON Schema / Pydantic model. Dropdown fields must validate against the codebook; the codebook must be editable with migration notes.
3. **Provenance.** Every extracted field and argument carries `{doc, page, span}`; the stored section text allows re-display of the supporting passage. Corrections to index metadata are recorded as events, never silent overwrites.
4. **Advice events.** A dossier can have several letters over time (initial, aanvullend, gecorrigeerd, herbeoordeling). Model documents → events → current state.
5. **Human-in-the-loop by default.** `draft` is cheap and repeatable; `commit` requires review (or an explicit `--auto` for low-risk marginale toetsen). Show confidence and the flags in §6.
6. **Evaluation harness.** The 423 completed dossiers are the gold standard. `zin eval` should report: exact-match rate on dropdown fields, numeric agreement on ICER/BIA/patients, and an argument-level recall/precision (embedding or LLM-judged) against our paraphrases. Use it to iterate on prompts and to catch regressions when models change.
7. **Retrieval.** Hybrid: SQL filters + embeddings over paraphrase + citaat + trefwoorden, chunk = one argument row (plus dossier context). Return precedents grouped by thema with the ID, drug, year, position and weight. Nice-to-have: "compare this new dossier to its nearest precedents".
8. **Dutch first.** Source text is Dutch; keep field values Dutch (users are Dutch). Prompts can be English; outputs must follow the Dutch conventions in `examples/`.
9. **Idempotent, resumable, offline-capable** for the LLM step where possible (cache by content hash). Config for model/provider. No scraping beyond ZIN's CC0 pages; be polite (rate limit, cache).
10. **Packaging.** Python ≥3.11, `pipx`/`uv` installable, one `pyproject.toml`, `zin --help` self-documenting, tests runnable without network on `data/zin_text_extracts_295.zip`.

Acceptance criteria for v1: (a) `zin sync && zin fetch && zin extract && zin draft && zin review && zin commit` on one newly published GVS advice produces a valid new row + arguments that a domain reviewer accepts with ≤ 3 edits; (b) `zin eval` on 30 random completed dossiers ≥ 85 % agreement on dropdown fields and ≥ 70 % argument recall; (c) `zin query --thema "Single-arm / ongecontroleerde data" --positie "Ondersteunt claim fabrikant"` returns the known precedents with page references; (d) the xlsx export opens in Excel with intact dropdowns and Overzicht formulas.

---

## 10. Appendix A — record example (abridged, GVS-301 Sibnayal, a rejection)

```
GVS-301 | 19-07-2023 | Advicenne | weesgeneesmiddel Ja
Aanvraag: Bijlage 1B (uniek) | Uitkomst: Niet opnemen (index said "Opnemen met bijlage 2" → corrected)
SWP: Voldoet | kernreden: Niet-inferioriteit / gelijke waarde aangetoond | TW: Gelijke waarde
Comparator: alkalitherapie via apotheekbereidingen (kaliumcitraat, magnesiumcitraat)
Prijs: €2,30/sachet vs €0,16/capsule bereiding; ~€14.000 vs ~€120 per patiënt/jaar
BIA: €4,2 mln jaar 3 (378 pat.), 6,6–9,0 bij 50–100 % overstap volwassenen
Kern: (1) bereidingsprijs als anker → afwijzing op 'onnodig hoge prijsstelling' en 'behoud van solidariteit';
      (2) bijlage 3A als beschermingsconstructie voor de bereiding; (3) 'passend onderzoek': RCT haalbaar maar niet gedaan.
Argument 1 | Kosteneffectiviteit | Prijs / kortingsadvies | Eigen initiatief ZIN | Doorslaggevend | bron: brief p. 2-4
Argument 2 | Effectiviteit | Comparator / gebruikelijke zorg | Nuanceert | Ondersteunend | bron: FT-conclusie
```

## 11. Appendix B — glossary of IDs and files

- `GVS-###`, `INT-###`: our dossier IDs (not ZIN's). `GVS-001…016` ongoing agenda; `GVS-101+` published, roughly chronological 2015→2026.
- `Status extractie`: Index → Basisgegevens → Argumenten volledig → Gecontroleerd.
- `batchNN_body.py` (DOSSIERS dict) + `batchNN_args.py` (A(...) calls) concatenated with `batch_header.py`/`batch_argdef.py` = one batch module for `fill_db.py`.
- Backups: `.backup_db_after_batchNN.xlsx` after every applied batch (not included).
- Session transcripts (three, ~MBs) exist on the analyst's side and can be shared on request; they contain the full reasoning per dossier.

*End of brief.*
