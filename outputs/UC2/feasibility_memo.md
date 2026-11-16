## 1. Executive summary

**Overall verdict: not feasible as scoped.** The must-need N2 (mapping of product codes across the 2024 code change) is unmet, so under the must-need rule the use case cannot proceed to profiling at product level. Total-level analysis across the break may still be possible once the access and licence conditions below are cleared. This is a decision for the analytics lead.

Facts that drive the verdict:

1. **N2 is unmet.** The wiki page product_codes_2024 (last edited 2024-04-02) says codes changed on 2024-04-01, no mapping table exists, and old and new codes can only be matched by product name, which is not unique. `internal.sales.products` holds only current codes, so it cannot fill the gap.
2. **Product-level history is limited.** Because the codes cannot be linked, product-level series cannot be stitched across 2024-04-01. Only per-era or total-level analysis is possible for the history window.
3. **The shop's own sales data is restricted and not yet accessed.** `internal.sales.daily_by_product` is classed confidential and needs a Retail Operations request. No probe was made. The till gap 2024-02-05 to 2024-03-10 must be treated as missing, not zero.
4. **Temperature is available but not on the free terms.** `api.open_meteo_archive` covers the history window from 1940 onward. Its free tier is non-commercial only, and the publisher's terms require a paid plan for business use. The register lists production approval, which conflicts with those terms.
5. **Holidays and calendar are workable with conditions.** The holiday API has no licence statement beyond MIT for the repository code. The shop calendar's row count (about 1,500) does not match the roughly 1,744 calendar days to its last refresh, and its `is_open` and `event_name` fields are undocumented.

## 2. Need coverage

| Need ID | Need | Priority | Status | Best source(s) | Gap |
|---|---|---|---|---|---|
| N1 | Daily ice-cream sales by product | must | partially met | internal.sales.daily_by_product | Access not granted (confidential). Product series cannot be linked across 2024-04-01. Till gap 2024-02-05 to 2024-03-10 treated as missing. Primary measure (units vs revenue) not confirmed. |
| N2 | Mapping of product codes before and after the 2024 code change | must | **unmet** | internal.sales.products; internal.sales.daily_by_product | No mapping table exists (wiki). Name matching is not reliable because names are not unique. |
| N3 | Daily maximum temperature | must | met with conditions | api.open_meteo_archive | Paid commercial plan and Legal approval needed. Only 2026-03-25 to 2026-03-31 was probed for the recent window. Grid point (45.448154 N, 11.003136 E, probe result) must be justified as the shop location. The shop city is not named in any source. |
| N4 | Public holidays in Italy | should | met with conditions | api.nager_public_holidays | Data licence unknown beyond MIT for the repository code. National calendar only; local feasts not covered. |
| N5 | Shop opening days and local events | should | met with conditions | internal.store.calendar | Row count mismatch (~1,500 vs ~1,744 days). `is_open` and `event_name` undocumented. Completeness unverified. |

## 3. Source assessments

**Order: feasible, then with conditions, then not feasible.** No source in this set is rated plainly feasible. Sources are grouped by verdict.

### api.nager_public_holidays (with conditions)
- **What it is:** Public REST API returning Italy's national public holidays by year, with date, names, a global flag and a counties field. Probed for 2023 to 2026, each year returned HTTP 200 with 13 or 14 records.
- **Verdict:** feasible with conditions. Serves N4 (should) for both windows.
- **Key flags:** LIC-UNKNOWN (blocker, rule-raised). The register lists agreement status not_required_open_data and approved purposes prototyping and production. The only terms page (the repository) shows MIT for code only. No licence for the data or API output was found.
- **Conditions:** Legal confirms the data terms. Analytics confirms no county-scoped entries in the full year lists (only first and last records were probed). Legal records the register entry alongside its outcome.

### internal.store.calendar (with conditions)
- **What it is:** Internal Operations table with one row per calendar day, recording whether the shop was open and an optional local event name. Catalog coverage starts 2022-01-01, open-ended, weekly refresh, last refresh 2026-10-10. Not sampled.
- **Verdict:** feasible with conditions. Serves N5 (should) for both windows. It is the only source for N5.
- **Key flags:** DQ-METADATA-CONTRADICTION (major, judgement): stated row count about 1,500 against about 1,744 calendar days. DQ-UNDOCUMENTED-SCHEMA (major, judgement): no rule for `is_open` on closed days, holidays or missing rows, and no source for `event_name`. No wiki page or schema document was found.
- **Conditions:** Store Operations confirms row count and completeness for 2023-06-01 to 2026-03-31, documents the `is_open` and `event_name` rules, and confirms the 2026-10-10 refresh loaded data through 2026-03-31.

### api.open_meteo_archive (with conditions)
- **What it is:** Gridded historical weather API giving daily maximum 2 m temperature for any latitude and longitude, from reanalysis (ERA5 and ERA5-Land, with ECMWF IFS from 2017). Start 1940, open-ended, metadata last updated 2026-11-15.
- **Verdict:** feasible with conditions. Serves N3 (must) for both windows. The history window is covered. The recent window is only sampled for 2026-03-25 to 2026-03-31.
- **Key flags:**
  - LIC-NONCOMMERCIAL (blocker, rule-raised): the data is CC BY 4.0 per the licence page, but the terms page limits free API use to non-commercial use. A paid plan (Standard, Professional or Enterprise) is needed for Valdena's business use. The verdict is conditional only because the publisher offers that paid plan.
  - LIC-MIXED (major, rule-raised): upstream sources carry different terms.
  - GOV-CATALOG-WIKI-CONFLICT (major, judgement): register says not_required_open_data with production approved. Terms page says commercial use of the free API is not permitted.
  - FRS-METADATA-DATE-MISLEADING (minor, judgement): metadata date is later than the as-of date (2026-10-15) and does not describe the data period.
- **Conditions:** Client buys a commercial plan and Legal approves its terms. Legal confirms terms for each upstream model and the attribution requirement. Legal reconciles the register entry. Analytics documents the grid point and shop location rationale. Analytics confirms reanalysis lag and revision policy, and samples summer 2023 to 2025 values.

### internal.sales.daily_by_product (with conditions)
- **What it is:** Daily units sold and revenue in euros per till product code, from the till system. About 310,000 rows, catalog coverage from 2022-01-01, open-ended, daily refresh, last updated 2026-10-14. Owned by Retail Operations.
- **Verdict:** feasible with conditions for N1 only. Not feasible for N2. The source is conditional because N1 can be served at total level or per code era.
- **Key flags:**
  - ACC-RESTRICTED (major, rule-raised): auth required, confidential, request to Retail Operations. Not probed, reachability unknown.
  - INT-JOIN-KEY-MISMATCH (major, judgement): codes changed 2024-04-01 with no mapping table.
  - DQ-UNDOCUMENTED-SCHEMA (minor, judgement): primary measure not stated (units or revenue). No open/closed flag. Closed days may appear only as missing rows.
  - Documented till gap 2024-02-05 to 2024-03-10 with no rows (wiki till_migration_2024).
- **Conditions:** Retail Operations grants access. The till gap is treated as missing, not zero. Product codes are not linked across 2024-04-01, and no name-based crosswalk is used. Retail Operations confirms the primary measure and that no mapping table exists. Analytics joins to the shop calendar. Retail Operations verifies row completeness for both windows.

### internal.sales.products (not feasible)
- **What it is:** Static product master listing current codes, names and categories, about 64 rows. Owned by Retail Operations. Last refreshed 2025-03-31, refresh on change.
- **Verdict:** not feasible. It is the only source proposed for N2, and N2 cannot be met by it.
- **Key flags:**
  - INT-JOIN-KEY-MISMATCH (major, judgement): no legacy codes and no effective dating. Name matching is ruled out as a reliable key by the wiki.
  - DQ-METADATA-CONTRADICTION (minor, judgement): temporal coverage is null, and it is not documented whether pre-2024 rows were removed. Currency as of 2026-10-15 is unknown.
- **Conditions:** None that would make it meet N2. A pre-2024 product master or a documented old-to-new mapping would be a new source.

## 4. Red-flag register

| Source ID | Code | Severity | Evidence | Raised by |
|---|---|---|---|---|
| api.nager_public_holidays | LIC-UNKNOWN | blocker | Licence null. Repository page shows MIT for code only. No data licence found. Register: not_required_open_data, prototyping and production approved. | rule |
| api.open_meteo_archive | LIC-NONCOMMERCIAL | blocker | Free API non-commercial only. Paid plan needed for business use. | rule |
| api.open_meteo_archive | LIC-MIXED | major | Upstream sources under different terms. | rule |
| api.open_meteo_archive | GOV-CATALOG-WIKI-CONFLICT | major | Register production approval conflicts with the terms page. | judgement |
| api.open_meteo_archive | FRS-METADATA-DATE-MISLEADING | minor | Metadata date 2026-11-15 is after the as-of date. End date open. | judgement |
| internal.sales.daily_by_product | ACC-RESTRICTED | major | Confidential, auth required. Not probed. | rule |
| internal.sales.daily_by_product | INT-JOIN-KEY-MISMATCH | major | No mapping table for 2024-04-01 code change. Names not unique. | judgement |
| internal.sales.daily_by_product | DQ-UNDOCUMENTED-SCHEMA | minor | Primary measure not stated. No open/closed flag. | judgement |
| internal.sales.products | INT-JOIN-KEY-MISMATCH | major | Current codes only. No legacy codes or effective dates. | judgement |
| internal.sales.products | DQ-METADATA-CONTRADICTION | minor | Temporal coverage null. Last refresh 2025-03-31. | judgement |
| internal.store.calendar | DQ-METADATA-CONTRADICTION | major | Row count ~1,500 vs ~1,744 days. | judgement |
| internal.store.calendar | DQ-UNDOCUMENTED-SCHEMA | major | No rules for `is_open` or `event_name`. No documentation found. | judgement |

Note: the severity of the Nager and Open-Meteo blockers is set by rule. Each is treated as resolvable, which is why neither source is rated not feasible. Resolution depends on outside parties.

## 5. Conditions and owners

| Condition | Source(s) | Who can resolve | Blocking which need |
|---|---|---|---|
| Confirm no mapping table exists. Restrict product-level analysis to each code era or total level. | internal.sales.daily_by_product; internal.sales.products | Retail Operations; analytics team | N2 (blocking, no fix in scope), N1 product level |
| Grant analytics access under confidential classification | internal.sales.daily_by_product | Retail Operations | N1 |
| Treat 2024-02-05 to 2024-03-10 as missing, not zero | internal.sales.daily_by_product | Analytics team | N1 |
| Confirm primary sales measure (units or revenue) | internal.sales.daily_by_product | Retail Operations | N1 |
| Verify row completeness for both windows | internal.sales.daily_by_product; internal.store.calendar | Retail Operations; Store Operations | N1, N5 |
| Buy commercial Open-Meteo plan; Legal approves terms | api.open_meteo_archive | Client procurement; Legal | N3 |
| Legal confirms upstream model terms and attribution | api.open_meteo_archive | Legal | N3 |
| Legal reconciles register entry with terms page | api.open_meteo_archive; api.nager_public_holidays | Legal | N3, N4 |
| Justify grid point and shop location | api.open_meteo_archive | Analytics team with client | N3 |
| Sample recent-window temperature and confirm reanalysis lag | api.open_meteo_archive | Analytics team | N3 |
| Confirm holiday data licence | api.nager_public_holidays | Legal | N4 |
| Confirm no county-scoped entries in full year lists | api.nager_public_holidays | Analytics team | N4 |
| Confirm row count, completeness and `is_open` / `event_name` rules | internal.store.calendar | Store Operations | N5 |

## 6. Recommended next steps

1. **Decide on N2 first.** Decide whether the analysis may proceed at total level across the 2024 break, with product-level analysis limited to each code era. Record the decision in `decisions.md`.
2. **Ask Retail Operations to confirm there is no pre-2024 product master or code mapping.** If one exists, it becomes a new source and N2 may change status.
3. **Raise the access request** with Retail Operations for `internal.sales.daily_by_product` under the confidential classification.
4. **Raise the commercial weather plan** with client procurement and Legal, and ask Legal to reconcile the register entry with the terms page.
5. **Raise the licence check** for the holiday API with Legal.
6. **Raise the calendar check** with Store Operations on row count, completeness and field rules.
7. **Record the shop location** and its justification as an assumption, then confirm the grid point.
8. **Once the gate is passed, profile first:**
   - Completeness and the primary measure in the sales table, excluding the till gap.
   - Calendar completeness against the 2023-06-01 to 2026-03-31 window.
   - A sample of summer 2023 to 2025 maximum temperatures, and the recent-window temperature values beyond the probe.

## 7. Open questions for the human reviewer

1. Is total-level analysis across the 2024 code change acceptable for the business question, or must product-level results be delivered? If product-level results are required, UC2 cannot proceed.
2. Does a pre-2024 product master or old-to-new code mapping exist outside the sources reviewed? Only Retail Operations can confirm this.
3. Will the client buy the commercial Open-Meteo plan, and who signs for it?
4. Which city or location does the shop occupy? No source names it, and the grid point needs a justified location.
5. Does the register's "production approved" status for Open-Meteo and Nager.Date reflect a Legal decision, or was it entered without review?
6. Which measure drives the business decision, units sold or revenue in euros?
7. Does a missing calendar row mean the shop was closed, or that the day is unknown?
8. Does the client accept that local feasts and events are not covered by any holiday source?
9. Is the Open-Meteo metadata date of 2026-11-15 (after the as-of date) a catalog error, and should the source be re-checked before Legal review?

---

## Human review gate

Draft generated by the discovery agents for UC2 on 2026-11-15T21:47:55Z (model claude-haiku-5-5). It is a draft for review, not a decision.

Before any profiling or pipeline work, the reviewer confirms:

- [ ] Each verdict is supported by the evidence cited
- [ ] Every licence was read at its source, and the attribution text is recorded
- [ ] Access requests for the feasible-with-conditions sources are raised with the named owners
- [ ] Consent and purpose limits are understood, and the target population is filtered accordingly

**Blocker flags on sources not rejected (resolve or justify):**

- api.nager_public_holidays: LIC-UNKNOWN
- api.open_meteo_archive: LIC-NONCOMMERCIAL

**Open questions:**

1. Is total-level analysis across the 2024 code change acceptable, or must product-level results be delivered? If the latter, UC2 cannot proceed.
2. Does a pre-2024 product master or old-to-new code mapping exist outside the reviewed sources? Only Retail Operations can confirm.
3. Will the client buy the commercial Open-Meteo plan, and who signs for it?
4. Which city or location does the shop occupy? No source names it, and the grid point needs a justified location.
5. Does the register's 'production approved' status for Open-Meteo and Nager.Date reflect a Legal decision, or was it entered without review?
6. Which sales measure drives the decision: units sold or revenue in euros?
7. Does a missing calendar row mean the shop was closed, or that the day is unknown?
8. Does the client accept that local feasts and events are not covered by any holiday source?
9. Is the Open-Meteo metadata date of 2026-11-15 (after the as-of date) a catalog error, and should the source be re-checked before Legal review?

Reviewer: ____________________   Date: __________   Decision: proceed / proceed with conditions / stop
