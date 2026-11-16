# Memo review: UC1 (Valdena Civic Health Office, air quality and clinic warnings)

## 1. Provenance

Memo review and sign-off for UC1, by utkarshyogeshsaxena, **2026-11-16**. The matching sign-off is `outputs/UC1/signoff.json`. No file under `outputs/UC1/` other than `signoff.json` was changed, and the LLM pipeline was not re-run.

## 2. What I checked and how

- **Memo:** `outputs/UC1/feasibility_memo.md`, all 7 required sections plus the review gate. All headings are present and in order (`python -m discovery_agent check UC1`).
- **Against the evidence:** `discovery_results.json`, `risk_assessment.json`, `rule_flags.json`, all 8 files in `records/`, `candidates.json` (including `rejected_without_profiling`), `gate_decisions.json`, `links.json`, `run_history.jsonl`, and `trace.jsonl` (the http and tool_call lines named below). I also read the profiler transcripts for Open-Meteo and Eurostat.
- **Client estate:** `internal/UC1_valdena_health/catalog_export.json` and the wiki pages `station_network`, `counter_replacement_2024` and `clinic_data_policy`.
- **Config and log:** `config/external_sources_register.json`, `config/red_flags.json`, and `outputs/artifacts/decisions.md` (Step 2b, G1/G3, G4–G5, G6, G5 v1/v2, G7, gate decisions, Open-Meteo location).
- **Live checks with the no-LLM tool** (`discovery_agent tool probe_url`, allowlisted hosts only, metadata only):
  - `https://ec.europa.eu/eurostat/web/main/help/copyright-notice` returned 200 with the text "Reuse of statistical data, metadata, publications … for commercial or non-commercial purposes is authorised provided the source is acknowledged".
  - `https://open-meteo.com/en/terms` returned the text "You may only use the free API services for non-commercial purposes". Its list of non-commercial examples includes "Public research conducted at public institutions".

## 3. Where I agree with the agent, and why

1. **Overall verdict `feasible_with_conditions` (after the G7 fix).** Every must need (N1, N2, N3) has at least one source, and no blocker is unresolvable. I checked that the traffic source is no longer wrongly `not_feasible`. Its `INT-NO-JOIN-KEY` evidence now quotes `quality_notes` ("No documented mapping from counter_id …"), which is "unknown", not "documented impossible". Neither the catalog entry `traffic.hourly_counts` nor wiki `counter_replacement_2024` says a mapping cannot exist.
2. **`internal.traffic.hourly_counts`: the 2024-03-18 counter change.** Wiki `counter_replacement_2024` says that before 2024-03-18 counts were per direction and from that date both directions combined, and the catalog has no note. The memo raises `GOV-CATALOG-WIKI-CONFLICT` with the condition "adjust or model the break". This is correct. The change falls inside the production window (2024-01-01..2025-12-31), so it cannot be ignored. `DQ-DST-ARTEFACTS` is also correct: the catalog column `ts_local` is described as "Hour start, local time", while station readings are `ts_utc`.
3. **`internal.airq.station_readings`: VR-03.** Wiki `station_network` (2024-07-01) says "Station VR-03 (Via Roma) was switched off on 2024-06-30". The catalog still says `status: active` with `temporal_coverage.end: null`. The memo raises `GOV-CATALOG-WIKI-CONFLICT` and the condition "exclude VR-03 after 2024-06-30". This is correct: VR-03 can supply only 6 of the 24 production months.
4. **`link.uci_360`: licence conflict and sentinels.**
   - The record's `licence.evidence` quotes both the CC BY 4.0 link and the note "This dataset can be used exclusively for research purposes. Commercial purposes are fully excluded". Raising `LIC-NONCOMMERCIAL` as a blocker and confining the file to a prototype benchmark under Legal review is the right reading. G1 alone reads only the link, and the profiler caught the note.
   - The memo's `DQ-SENTINEL-VALUES` and `DQ-METADATA-CONTRADICTION` follow `declared_metadata.has_missing_values: "no"` against the excerpt "Missing values are tagged with -200 value".
   - The memo and the Risk Assessor condition explicitly include C6H6(GT). The record's `quality_notes` say the sampler reported it "100% non-missing" although "366 values equal -200". The G7 note in decisions.md (option B) confirms this sampler bug.
5. **`link.uci_360`: FRS-STALE dismissed (rule 5).** `temporal.end` = 2005-04-04 and the source is proposed only for the prototype window (2004-03-10..2005-04-04), which is historical by design. The rule flag in `rule_flags.json` ("Data ends 2005-04-04, more than 5 years before as_of") is valid as computed, and the dismissal reason names the field and value. **This dismissal is valid.** No other flag was dismissed, and the guardrail flags on Chicago were kept (rule 11).
6. **`link.europa_sdg_11_52_099aa6`: coverage.** `temporal.start` 2005-01-01 and `temporal.end` 2023-12-31, and the rule `COV-PARTIAL-WINDOW` gives prototype 24% and production 0%. The record's `quality_notes` say "2006 is absent". I agree with "N6 partially met" and "treat 2006 as missing, not zero". The memo's open question 4 ("36 cells, no missing values, but 2006 absent: which is correct?") has an answer: both. 2006 is missing from the time dimension itself, so 18 years × 2 units = 36 cells are all filled (`TIME_GAPS`, see the G3 entry in decisions.md).
7. **`link.lombardia_6eu4_4tja_097de4`: coverage is unverified.** The record has `temporal.start: null`, and its `quality_notes` say the 2 MB sample covered only sensor 13 in 1987. The gate inspection also stopped in 1996, because the export is sorted by sensor. The memo does not claim coverage of 2004–05. It makes "confirm sensors report within 2004-03-10..2005-04-04 using nf78-nj6b" a condition, and it keeps the source as a temperature-only prototype benchmark (`GOV-PURPOSE-LIMITATION`). This is correct. The decisions.md G4–G5 entry confirms the coverage rule skips a null start.
8. **`internal.clinic.resp_visits_daily` and N5.** Wiki `clinic_data_policy` (owner: Data Protection Office, 2025-02-01) says "Only daily counts by district … may be used for this purpose" and forbids patient-level records. The agent correctly raised no purpose or consent flag on the aggregate table, kept N5 `unmet`, and rejected `internal.clinic.patient_visits` before profiling (`candidates.json` `rejected_without_profiling`). The vendor feed `vendor.atmosdata_pro` was also correctly rejected before profiling: its agreement expired 2025-12-31 and its key was revoked.
9. **Chicago is not feasible.** `trace.jsonl` line 75 shows `"refused": "DOMAIN_NOT_ALLOWLISTED"` for catalog.data.gov. The record has `access.reachable: false`, and the memo says "No alternative route was attempted, and none should be sought". `ACC-UNREACHABLE` and `LIC-UNKNOWN` were kept, not dismissed.

## 4. Where I overrule the agent, and what it missed

1. **Eurostat licence: wrong URL, so `LIC-UNKNOWN` is avoidable.**
   - *Evidence:* the profiler probed `https://ec.europa.eu/eurostat/about/policies/copyright` (`trace.jsonl` lines 72–73). That page redirected to EU Login, so the record's `licence.name` is null and the Risk Assessor condition tells Legal to check that same unreadable URL.
   - The correct page is `https://ec.europa.eu/eurostat/web/main/help/copyright-notice`. It is cited in the G6 section of decisions.md, and I re-read it today: it says CC BY 4.0 for editorial content and "Reuse of statistical data … for commercial or non-commercial purposes is authorised provided the source is acknowledged".
   - *My call:* the blocker is in practice resolved. What remains is attribution ("Source: Eurostat, sdg_11_52") and a short Legal note pointing to the correct URL. The memo's open question 3 ("should the source be used at all until Legal responds?") becomes: yes, as N6 context, with attribution. The record itself was not edited. A future re-run should fix the profiler's URL choice.
2. **Open-Meteo: the probe was in the wrong place.**
   - *Evidence:* `trace.jsonl` lines 40–43 show both probes at `latitude=45.46&longitude=9.19` (Milan). The record's own `provenance[0]` says the register default is 45.44/10.99.
   - decisions.md ("Open-Meteo location") records that the learner chose **Verona (45.44, 10.99)** on 2026-11-16 as a stated assumption.
   - So the memo's "Valdena location not set … do not set coordinates" and "COV-GEO-MISMATCH: the register default is not a Valdena assumption" are wrong. The assumption is set and recorded. It still needs the client's confirmation. The memo's open question 1 (Lisbon) is also answered in decisions.md: the register's Lisbon point (38.72, -9.14) was replaced by Verona, so the candidate note quoting Lisbon is stale.
   - *My call:* re-probe at 45.44/10.99 before use. Keep `COV-GEO-MISMATCH` only as "Verona is an assumption, to be confirmed by the client".
3. **Open-Meteo: commercial use is not established.**
   - *Evidence:* the UC1 profiler read only `/en/licence` (`trace.jsonl` line 77), never `/en/terms`, yet the record says `licence.commercial_use: "yes"`. The UC2 profiler did read the terms ("You may only use the free API services for non-commercial purposes"), and I confirmed that text today.
   - A public health office's warning service may count as non-commercial (the terms list "Public research conducted at public institutions" as non-commercial), but that is for Legal to decide, not the agent.
   - The memo misses the free-API term entirely. It only says LIC-MIXED/C3S. *My call:* add a condition that Legal confirms the UC1 use is non-commercial under `/en/terms`, or that a paid plan is bought.
4. **Open-Meteo prototype coverage is already shown.** The memo says Open-Meteo serves N3 prototype only "if start confirmed". But `trace.jsonl` line 40 returned 200 with 72 hourly values for 2004-03-10..2004-03-12, the first days of the prototype window. Start is confirmed for the window (at the wrong point; see item 2).
5. **"Last-modified 15 Nov 2026 later than the as-of date" is not a data problem.** That is the HTTP header of the licence web page fetched during the run (`provenance[3]`; `run_history.jsonl` shows the run on 2026-11-15). It is not a dataset date. I drop memo step 8 and open question 11's premise.
6. **Clinic: written Data Protection Office sign-off.** The DPO's own page `clinic_data_policy` already permits the daily district counts "for this purpose". I downgrade "written DPO confirmation" from a gate item to a request: confirm the 2025-02-01 policy is still current and set the **small-cell suppression rule**. The memo lists that rule only in passing. It is the real open privacy item (`candidates.json` `unmet_needs` N4, and the record's `unknowns`).
7. **Missed details:**
   - *UCI 360 N1 is NO2 only:* the file has no PM2.5 (record `quality_notes`), so a prototype PM2.5 model is not possible.
   - *UCI 360 CO(GT) negatives:* 91 values are negative but not -200 (`quality_notes`). The memo does not list these.
   - *UCI DQ-DST-ARTEFACTS:* the memo says it was "raised then not raised", but `discovery_results.json` still lists it in `red_flags`. I keep it as a minor note (the timestamp timezone is undocumented).
   - *Sampler bug:* the C6H6(GT) sentinel bug in `discovery_agent/tools/` is still unfixed (G7 option B). Until it is fixed, manual recoding is the only guard.
   - *Station row count:* about 4.2 million rows over about 33,000 hours (record `quality_notes`) implies about 125 station-hours per hour. That does not fit a small city network, so the count needs checking.

## 5. My verdict on each dataset link

| Link | Gate decision | My verdict | Why |
|---|---|---|---|
| UCI 360 (`link.uci_360`) | accept | **Uphold. Usable for the prototype only.** | Covers the prototype window 100% (`temporal.start/end`). Use is research and benchmark only (research-only note), with -200 recoded in every column including C6H6(GT). NO2 only, single unnamed site. Never production. |
| Eurostat sdg_11_52 (`link.europa_sdg_11_52_099aa6`) | accept | **Uphold. N6 context, with attribution.** | Licence is resolvable at the correct copyright-notice URL (see 4.1). 2005 only in the prototype window, 2006 missing, no 2024–25 values. |
| Chicago (`link.data_open_air_chicago_hour_aggre_d4970b`) | accept (deliberate) | **Uphold the refusal. Not usable.** | DOMAIN_NOT_ALLOWLISTED (trace line 75). It is a US site for an Italian client. catalog.data.gov stays off the allowlist. |
| ARPA Lombardia 6eu4-4tja (`link.lombardia_6eu4_4tja_097de4`) | accept | **Uphold. Temperature benchmark for the prototype only.** | CC0 1.0 from JSON-LD. Window coverage is not yet shown by the pipeline (`temporal.start` null, sample stops in the 1980s–90s). Confirm with a small filtered query before use. It is a Lombardy benchmark, not the client's site (Verona is in Veneto, the assumed location). |

## 6. Gate decision

`outputs/UC1/gate_decisions.json` accepts all four links: UCI 360 and Eurostat for N1 and N6, Lombardia as the N3 station benchmark, and Chicago deliberately so that its refusal is recorded. **I uphold all four.** Each reason is borne out by the records: the UCI licence conflict and sentinels, the Eurostat 2006 gap, the Chicago refusal, and the Lombardia sample never reaching 2004–05. Accepting Chicago did not loosen anything. The host stayed refused and no other route was tried.

## 7. One traced conclusion

**`link.uci_360` → `temporal.end` = "2005-04-04" (with `temporal.start` = "2004-03-10")**
1. *Source information:* `sample_data_file` read the whole CSV (`provenance`), and its dates run 2004-03-10 to 2005-04-04.
2. *Record field:* `temporal.start` and `temporal.end`.
3. *Rule:* `rule_temporal_coverage` (G4) gives 100% of the prototype window, so no coverage flag. It raises `FRS-STALE` ("Data ends 2005-04-04, more than 5 years before as_of 2026-10-15", `rule_flags.json`).
4. *Calibration:* rule 5 dismisses `FRS-STALE`, because the target window is itself historical. Rule 2(a) turns the research-only licence into a Legal condition for prototype use only.
5. *Verdict:* `feasible_with_conditions` for N1 and N3 in the prototype window, and nothing for production.

**What could change it:**
- Legal reads "exclusively for research purposes" as excluding the Health Office's method-building work, which would make it `not_feasible`.
- The prototype window is redefined to dates outside 2004-03-10..2005-04-04.
- The -200 recoding leaves too little NO2: about 1,640 of 9,357 hours are -200, about 17.5%.

## 8. Sign-off verdict and conditions

**Verdict: proceed_with_conditions.** Prototype work on UCI 360 can start once Legal clears the research-only note. Production profiling waits on the access requests.

| # | Condition | Owner | Due |
|---|---|---|---|
| 1 | Legal confirms UCI 360 may be used for non-commercial, research-style prototype method building only (research-only note vs CC BY 4.0), and never in production | Legal | 2026-12-04 |
| 2 | Recode -200 to missing in every UCI column, including C6H6(GT), whose -200 values the sampler missed. Check the 91 negative CO(GT) values. Use NO2 as the prototype pollutant (no PM2.5) | Analyst team | 2026-12-11 |
| 3 | Re-probe Open-Meteo at the recorded Verona assumption (45.44, 10.99), not Milan. Client confirms or replaces the location. Legal confirms the use is non-commercial under open-meteo.com/en/terms (or a paid plan is bought) and confirms the upstream C3S terms | Analyst team; Valdena Civic Health Office; Legal | 2026-12-11 |
| 4 | Record the Eurostat licence from https://ec.europa.eu/eurostat/web/main/help/copyright-notice (reuse authorised with source acknowledged). Use it as N6 context only, with 2006 missing | Analyst team (Legal to note) | 2026-11-30 |
| 5 | Raise access requests for station readings, traffic counts and clinic counts, with turnaround dates | Environment Monitoring Unit; Mobility Office; Clinical Analytics | 2026-12-18 |
| 6 | Supply the counter-to-station mapping and the ts_local timezone. Decide adjustment vs break-modelling for the 2024-03-18 counter change | Mobility Office with analyst team | 2027-01-15 |
| 7 | Confirm the VR-03 end date and which stations report through 2025-12-31. Reconcile the 4.2 million row count with the station count | Environment Monitoring Unit | 2027-01-15 |
| 8 | Confirm the clinic_data_policy (2025-02-01) is current, and set the small-cell suppression rule, district code list and respiratory definition | Data Protection Office; Clinical Analytics | 2027-01-15 |
| 9 | Confirm with a small filtered query that ARPA Lombardia sensors report within 2004-03-10..2005-04-04. Use it as a temperature benchmark only | Analyst team | 2026-12-11 |
