# Walkthrough (written)

*Walkthrough by utkarshyogeshsaxena, 2026-11-16, citing the repo's own files.*

## 1. One rule explained: `rule_temporal_coverage`

**Code:** `discovery_agent/risk_rules.py`, lines 106–167.

**What it checks.** It compares the dates a source covers with the use case's windows:
- It skips a record when `temporal.grain` is `static` or `temporal.start` is unknown. Unknown stays unknown, and the record's `unknowns` field carries it.
- A null `temporal.end` means the source is still updating, so coverage is counted up to the use case's `as_of` date.
- For each of the candidate's `target_windows`, it computes the share of the window's days that the source covers. Both ends of the window count (line 143: `days = (we - ws).days + 1`).
  - If every window has 0% coverage, it raises `COV-OUT-OF-WINDOW`.
  - Otherwise, if any window is below `partial_window_threshold` (0.95 in `config/settings.json`), it raises `COV-PARTIAL-WINDOW`. The evidence names each window and its percentage.
- It raises `FRS-STALE` when the data ends more than `stale_after_years` (5) years before `as_of`.
- The rule only raises flags. The verdict belongs to the Risk Assessor's calibration rules.

**Effect on a real source: `link.uci_360`.**
- The record has `temporal.start` 2004-03-10 and `temporal.end` 2005-04-04 (`outputs/UC1/records/link.uci_360.json`, lines 118–120).
- Its only target window is `prototype`, 2004-03-10..2005-04-04 (`use_cases/UC1_*.json`). The source covers that window 100%, so the rule raises no coverage flag.
- `as_of` is 2026-10-15, so the cutoff is 2021-10-15. The data ends before it, so `outputs/UC1/rule_flags.json` (line 68) holds `FRS-STALE`: "Data ends 2005-04-04, more than 5 years before as_of 2026-10-15 (cutoff 2021-10-15)."
- In `outputs/UC1/risk_assessment.json`, the Risk Assessor dismissed that flag under calibration rule 5 (`dismissed_rule_flags`, about line 280): "target window 'prototype' … is itself historical; the source is proposed only for that window, so the staleness cut-off does not apply."
- The rule is right to flag the source, because the data is old. The dismissal is right too, because a 2004–05 window can only be served by 2004–05 data.
- decisions.md (G5) notes that this dismissal was not applied in one intermediate run. The verdict was the same in every run.

## 2. One claim in `signoff.json` traced to its record field

`outputs/UC1/signoff.json` → `traced_conclusion`: `source_id` is `link.uci_360` and `record_field` is `temporal.end`.

1. **Source evidence.** The record's `provenance` lists `sample_data_file` on `https://archive.ics.uci.edu/static/public/360/data.csv`. It read the whole file (about 741 KB, 9,357 rows), with dates from 2004-03-10 to 2005-04-04. The gate check found the same dates (decisions.md, "Gate decisions (UC1)").
2. **Record field.** `outputs/UC1/records/link.uci_360.json` → `temporal.end` is `"2005-04-04"`, and `open_ended` is `false`. A quality note records a conflict: the UCI notes say "March 2004 to February 2005", and the profiler chose the file's own dates as "the better guide".
3. **Rule flag.** No coverage flag (prototype is 100% covered). `FRS-STALE` is raised (section 1).
4. **Verdict.** `risk_assessment.json` and `discovery_results.json` give `feasible_with_conditions` for N1, prototype only. `FRS-STALE` was dismissed (rule 5). The verdict is conditional because of `LIC-NONCOMMERCIAL` (the page links CC BY 4.0, but its notes say "exclusively for research purposes"), the -200 sentinels, the metadata contradiction and the single unnamed site.
5. **Sign-off.** The review agreed: "temporal.start/end 2004-03-10/2005-04-04 cover the prototype window 100%; FRS-STALE dismissal under rule 5 is valid". The verdict is `proceed_with_conditions`.

**What could change it** (the signoff's `could_change_if`):
- Legal reads "exclusively for research purposes" as excluding the prototype work.
- The prototype window moves outside 2004-03-10..2005-04-04.
- After recoding the -200 sentinels (about 17.5% of NO2 hours), too little usable NO2 is left.

## 3. One rejected source: the Chicago link

- **Source:** `link.data_open_air_chicago_hour_aggre_d4970b` (`https://catalog.data.gov/dataset/open-air-chicago-hour-aggregations`), proposed for N1, prototype.
- **Gate:** it was accepted on purpose, so that the refusal would be recorded as a finding (`outputs/UC1/gate_decisions.json`; decisions.md, "Gate decisions (UC1)").
- **Guardrail:** `outputs/UC1/trace.jsonl` line 75 has `"kind": "http"`, `"url": "https://catalog.data.gov/…"` and `"refused": "DOMAIN_NOT_ALLOWLISTED"`. Line 76 shows the `inspect_dataset_link` call with `"ok": false`, and the run made no other attempt to reach the host.
- **Record:** `access.reachable` is `false`. `request_process` reads "… No alternative route was attempted." `licence.evidence` reads "No licence statement could be read …".
- **Rule flags** (`rule_flags.json`):
  - `ACC-UNREACHABLE`, raised by `rule_access` because `reachable is False`.
  - `LIC-UNKNOWN`, raised by `rule_licence`.
- **Verdict:** `not_feasible` (`risk_assessment.json`). Rule 1 applies: a refused host is an unresolvable blocker, and rule 11 says it is never dismissed. The assessment also adds `COV-GEO-MISMATCH`, because the source covers the US and the client is in Italy.
- **Allowlist:** `catalog.data.gov` was left off the allowlist on purpose (decisions.md, G6). The UC1 review upheld the refusal (`review_UC1.md`, item 9 and the links table).

## 4. One memo conclusion: UC2 is not feasible as scoped

- **Memo:** `outputs/UC2/feasibility_memo.md`, line 3: "Overall verdict: not feasible as scoped. The must-need N2 … is unmet." `discovery_results.json` line 6 has `overall_verdict` `not_feasible`.
- **Evidence chain:**
  1. The wiki page `internal/UC2_valdena_gelato/wiki/product_codes_2024.md`, line 9, says: "No mapping table exists between the old and new codes."
  2. The record `outputs/UC2/records/internal.sales.products.json` has `schema.notes` "Catalog lists 3 columns; no legacy code column and no effective-dating fields". Its `documentation_excerpts` quote the wiki, including "some names are not unique".
  3. `risk_assessment.json` (about line 115) decides it by calibration rule 7: "the wiki explicitly says no mapping table exists … so N2 (must) cannot be met". The source is `not_feasible`, and N2 coverage is `unmet`.
  4. A must-need that is unmet makes the overall verdict `not_feasible`.
- **Why this is not UC1's error:** after the G7 fix, rule 7 applies only when the documentation says the mapping is impossible, not when it is silent. The G7 related check re-ran UC2 and kept this verdict (decisions.md, G7).
- **Review:** `outputs/artifacts/review_UC2.md` **agreed** with the overall verdict, and `outputs/UC2/signoff.json` has verdict `stop` "as scoped". It listed conditions to reopen the project:
  - Retail Operations finds a mapping or signs off a crosswalk for uniquely named products.
  - The client demotes N2 from a must need.

  The review **overruled** the memo on side points only:
  - The Verona location is recorded, not unknown.
  - The history window was never probed for Open-Meteo.
  - `FRS-METADATA-DATE-MISLEADING` comes from the date a page was fetched, so it should be dropped.
