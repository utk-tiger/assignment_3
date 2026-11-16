# Memo review: UC2 (Valdena Gelato Shop, sales, weather and holidays)

## 1. Provenance

Memo review and sign-off for UC2, by utkarshyogeshsaxena, **2026-11-16**. The matching sign-off is `outputs/UC2/signoff.json`. No file under `outputs/UC2/` other than `signoff.json` was changed, and the LLM pipeline was not re-run.

## 2. What I checked and how

- **Memo:** `outputs/UC2/feasibility_memo.md`. All 7 required sections and the review gate are present (`python -m discovery_agent check UC2`).
- **Against the evidence:** `discovery_results.json`, `risk_assessment.json`, `rule_flags.json`, all 5 files in `records/`, `candidates.json` (`unmet_needs`, empty `rejected_without_profiling`), `run_history.jsonl`, and every `"kind": "http"` line in `trace.jsonl`:
  - line 38: Open-Meteo data probe
  - lines 43, 45 and 48: licence, docs and terms pages
  - lines 58, 63, 65 and 72: Nager 2024, 2023, 2026 and 2025
  - line 67: the Nager GitHub page
- **Client estate:** `internal/UC2_valdena_gelato/catalog_export.json` and the wiki pages `product_codes_2024` and `till_migration_2024`.
- **Use case and log:** `use_cases/UC2_ice_cream.json` and `.md` (`links_expected: false`), `config/external_sources_register.json`, and `outputs/artifacts/decisions.md` (G5 v2, the G7 related check, Open-Meteo location).
- **Live check with the no-LLM tool:** `probe_url https://open-meteo.com/en/terms` confirmed "You may only use the free API services for non-commercial purposes", and that commercial use should go through the API plans on the pricing page.

## 3. Where I agree with the agent, and why

1. **Overall `not_feasible`, decided by N2.** Wiki `product_codes_2024` (Retail Operations, 2024-04-02) says "No mapping table exists between the old and new codes" and "some names are not unique". The record `internal.sales.products` has `schema.notes` = "no legacy code column and no effective-dating fields", and its `documentation_excerpts` quote the wiki. N2 is a must need, so calibration rule 7 applies to a documented impossibility, quoted with its page id. This is the case G7 was careful to keep distinct from UC1's mere absence of documentation. The G7 related check in decisions.md re-ran UC2 and kept the result.
2. **N1 is only `partially_met`, and that is right.** Daily sales exist (`internal.sales.daily_by_product`, catalog coverage from 2022-01-01), but N1 asks for sales **by product**. The history window (2023-06-01..2025-05-31) straddles the 2024-04-01 code change, so product series cannot be stitched across it. On top of that, wiki `till_migration_2024` documents no rows for 2024-02-05..2024-03-10. That loss is 35 days inside the history window, in the low season.
3. **The till gap is treated as missing, not zero.** The wiki says "Treat those days as missing, not as zero sales", and the record's `quality_notes` and the memo's conditions repeat it. This is correct.
4. **`api.open_meteo_archive`: `LIC-NONCOMMERCIAL` is resolvable only by a paid plan.** The record's `licence.evidence` quotes the terms page ("You may only use the free API services for non-commercial purposes", "Commercial products or promotional activities"). A gelato shop is commercial. Under calibration v2, rule 2(b), the publisher's own terms point to paid plans, so `feasible_with_conditions` holds, with "client buys the plan, Legal approves". The register's "production approved" conflicts with the terms, and the memo rightly asks Legal to reconcile it.
5. **`api.nager_public_holidays`: `LIC-UNKNOWN` is kept.** The record says the GitHub page shows "MIT license" for the repository (code). No data licence was found, so `licence.name` is null. The agent did not mistake MIT for the data licence. The register entry (`not_required_open_data`, production approved) makes it resolvable by Legal under rule 2 v2. The probes for 2023 to 2026 (trace lines 58, 63, 65, 72) cover both windows.
6. **`internal.store.calendar`: the row-count doubt is real.** About 1,500 rows against about 1,744 days from 2022-01-01 to 2026-10-10 (record `quality_notes`). With `is_open` and `event_name` undocumented, `feasible_with_conditions` with Store Operations as owner is right.

## 4. Where I overrule the agent, and what it missed

1. **The shop location is recorded, not unknown.** The memo says "The shop city is not named in any source" (open question 4) and asks for the grid point to be justified. decisions.md ("Open-Meteo location") records that the learner chose **Verona (45.44, 10.99)** on 2026-11-16 as a stated assumption. The client is fictional and no source names the city. The probe used exactly that point (trace line 38: `latitude=45.44&longitude=10.99`, snapped to 45.448154/11.003136). So the location question is "client confirms Verona", not "choose a location".
2. **The history window was not probed.** The memo's executive summary says Open-Meteo "covers the history window from 1940 onward". That rests on the docs page (record `temporal.start` 1940-01-01 from the docs), not on data. The only data probe is trace line 38, for **2026-03-25..2026-03-31** (recent window). No request touched 2023-06-01..2025-05-31. The claim is plausible but unverified. A short summer-2023 probe at the Verona point is needed. The memo's own condition, "samples summer 2023 to 2025", covers this, but its summary overstates.
3. **`FRS-METADATA-DATE-MISLEADING` on Open-Meteo should be dropped.** `temporal.metadata_last_updated` 2026-11-15 is the web page's fetch-time date (the run was on 2026-11-15, `run_history.jsonl`), not a dataset date. The memo's open question 9 ("catalog error?") has an answer: neither. It is a header of a page read on the run day.
4. **Flag code choice:** the register vs terms-page conflict is filed as `GOV-CATALOG-WIKI-CONFLICT`. The substance is right, but this is the register against the publisher's terms, not catalog against wiki. It does not change any verdict.
5. **`DQ-METADATA-CONTRADICTION` on `internal.sales.products` is weak.** A null `temporal_coverage` on a static product master is missing metadata, not a contradiction. It is minor and changes nothing.
6. **Missed for the reopening path:**
   - The wiki says only that "some" names are not unique. A name-based crosswalk for the unique names, reviewed and signed by Retail Operations, would be a new source that could partly meet N2. The memo rules out any name-based crosswalk.
   - I do not claim how many names are unique. No source states it.

## 5. Dataset links

**UC2 had no dataset links.** `discovery_results.json` has `dataset_links: []`, and the use case sets `links_expected: false` ("No dataset links are needed. Weather and holiday data come from the APIs in the register"). No Step 2b suggestion was accepted for UC2. All five Step 2b suggestions in decisions.md (S1–S5) were UC1 needs, and only S3 (ARPA Lombardia, UC1 N3) was accepted. So there is no link verdict to give.

## 6. Gate decision

**None needed.** With no dataset links, UC2 has no `gate_decisions.json` and `check` does not require one.

## 7. One traced conclusion

**`internal.sales.products` → `schema.notes` = "Catalog lists 3 columns; no legacy code column and no effective-dating fields."**
1. *Source information:* catalog entry `sales.products` ("Current product codes, names and categories", 3 columns), plus wiki `product_codes_2024`: "No mapping table exists between the old and new codes … some names are not unique" and "`sales.products` lists only the current codes".
2. *Record field:* `schema.notes`, with `documentation_excerpts` quoting the wiki.
3. *Flag and rule:* `INT-JOIN-KEY-MISMATCH` (judgement) leads to calibration rule 7, because the documentation explicitly says the keys cannot be mapped, with the quote and page id.
4. *Source verdict:* `not_feasible`, which makes N2 (must) `unmet`. The must-need rule then makes the overall verdict `not_feasible`.

**What could change it:**
- Retail Operations finds a pre-2024 product master or an old-to-new mapping.
- Retail Operations signs off a reviewed crosswalk for the uniquely named products.
- The client re-scopes so that product-level linkage across 2024-04-01 is no longer a must. For example, N2 is demoted to could, with total-level or per-era analysis.

## 8. Sign-off verdict and conditions

**Verdict: stop (as scoped).** I agree with the agent: a must need is documented as impossible, so the project cannot proceed to profiling at product level as briefed. The other needs are workable with conditions, so this is a stop pending re-scoping, not an abandonment. Conditions to **reopen** it:

| # | Condition to reopen | Owner | Due |
|---|---|---|---|
| 1 | Client decides whether total-level or per-code-era analysis is acceptable (N2 demoted from must), and records it in decisions.md | Valdena Gelato Shop (analytics lead) | 2026-12-11 |
| 2 | Retail Operations confirms whether any pre-2024 product master or code mapping exists, or signs off a reviewed name crosswalk for uniquely named products | Retail Operations | 2026-12-11 |
| 3 | If reopened: buy the Open-Meteo commercial plan and have Legal approve it. Legal reconciles the register entry with open-meteo.com/en/terms and confirms the Nager.Date data terms (MIT covers the code only) | Client procurement; Legal | 2027-01-15 |
| 4 | If reopened: client confirms the Verona (45.44, 10.99) location assumption. Probe the history window (summer 2023) at that point | Valdena Gelato Shop; analyst team | 2026-12-18 |
| 5 | If reopened: grant sales access. Treat 2024-02-05..2024-03-10 as missing. Confirm the primary measure and the calendar row-count and `is_open` rules | Retail Operations; Store Operations | 2027-01-15 |
