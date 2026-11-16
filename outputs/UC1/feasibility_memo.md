## 1. Executive summary

Overall verdict: **feasible with conditions.** No source is clean. Every must need (N1, N2, N3) can be met only after named conditions are cleared, and N5 cannot be met under the clinic data policy.

Facts that drive the verdict:

1. **Production window (2024-01-01 to 2025-12-31) relies on three internal sources, none yet approved.** The city station readings (N1), traffic counts (N2) and daily clinic counts (N4) all require access requests. Approval status and turnaround are not stated for any of them.
2. **The city station table has a known status conflict.** The wiki says station VR-03 was switched off on 2024-06-30. The catalog export (2026-10-14) still shows the network as active with no end date. VR-03 readings after that date must be excluded or treated as missing until the Environment Monitoring Unit confirms.
3. **The traffic series has a definition break inside the production window.** Counts changed from per-direction to both-directions combined on 2024-03-18. The catalog has no note about this. There is also no counter-to-station mapping and the timezone of ts_local is not stated.
4. **The prototype window (2004-03-10 to 2005-04-04) has only benchmark sources.** N1 relies on the UCI 360 dataset: one road-level site, single city, with a conflict between "CC BY 4.0" and "research purposes only." Legal must clear this before any use. N3 relies on modelled Open-Meteo data at an unset Valdena location, and on an ARPA Lombardia temperature series whose coverage of the window is not verified.
5. **Two sources are out.** The Chicago link was refused by the host (DOMAIN_NOT_ALLOWLISTED) and its licence is unknown. Patient-level data (N5) is not permitted by policy; only daily district counts may be shared.

## 2. Need coverage

| Need id | Need | Priority | Status | Best source(s) | Gap |
|---|---|---|---|---|---|
| N1 | Hourly air-pollutant concentrations (NO2 or PM2.5) | must | met with conditions | internal.airq.station_readings (production); link.uci_360 (prototype) | Prototype covered only by a single-site benchmark with a research-only licence conflict and -200 sentinels. Production relies on station readings with VR-03 status unresolved and continuity unverified. |
| N2 | Hourly vehicle traffic near monitoring stations | must | met with conditions | internal.traffic.hourly_counts | No counter-to-station mapping. Counting basis changed 2024-03-18 and must be adjusted. Timezone and DST encoding unknown. Production only. |
| N3 | Hourly temperature and humidity | must | met with conditions | api.open_meteo_archive (both windows); link.uci_360 (prototype T and RH); link.lombardia_6eu4_4tja_097de4 (prototype temperature) | Open-Meteo is modelled grid data at an unset Valdena location; full-window coverage unconfirmed (3-day probes only). ARPA Lombardia coverage of the window unverified and non-urban. Prototype humidity exists only in UCI and an unprofiled dataset. |
| N4 | Daily respiratory clinic visits by district | should | met with conditions | internal.clinic.resp_visits_daily | Production only. No respiratory definition, no district code list, access not tested. |
| N5 | Patient-level clinic visit records | could | unmet | none | Clinic data policy allows only aggregate daily district counts. |
| N6 | National yearly context: deaths linked to PM2.5 | could | partially met | link.europa_sdg_11_52_099aa6 | Series ends 2023: no production-window values. Covers prototype only through 2005. Licence not confirmed. |

## 3. Source assessments

### internal.airq.station_readings
- **What it is:** City station readings, hourly NO2 (no2_ugm3) and PM2.5 (pm25_ugm3), keyed by station_id and UTC hour start. Catalog states about 4.2 million rows, coverage from 2023-01-01 with no end date, hourly refresh, last refreshed 2026-10-14. Owner: Environment Monitoring Unit.
- **Verdict:** feasible with conditions. Serves N1 for production only. Does not cover the prototype window.
- **Key flags:**
  - ACC-RESTRICTED (major): auth required, classification internal. Approval status and turnaround not stated.
  - GOV-CATALOG-WIKI-CONFLICT (major): wiki station_network (last edited 2024-07-01) says VR-03 was switched off on 2024-06-30. Catalog still says active.
  - INT-NO-JOIN-KEY (major): no station register. Station locations, types and traffic-counter mapping are undocumented.
- **Conditions:** exclude VR-03 after 2024-06-30 and confirm network status; approve access; supply station register and counter mapping; sample for missing-value encoding, negatives and continuity to 2025-12-31 and reconcile the 4.2M row count. No sample has been taken. Legal to confirm internal use in a clinic warning model; the licence field says only "internal."

### internal.traffic.hourly_counts
- **What it is:** Hourly vehicle counts per road counter (counter_id, hour start in local time, vehicles) near the monitoring stations. Catalog states about 15 million rows, coverage from 2021-01-01, hourly refresh, last refreshed 2026-10-12. Owner: Mobility Office.
- **Verdict:** feasible with conditions. Serves N2 for production only.
- **Key flags:**
  - ACC-RESTRICTED (major): auth required, classification internal. Request goes to the Mobility Office.
  - GOV-CATALOG-WIKI-CONFLICT (major): wiki counter_replacement_2024 (last edited 2024-04-02) says counts are both directions combined from 2024-03-18, and warns not to compare across the change without adjustment. The catalog has no note.
  - INT-NO-JOIN-KEY (major): no counter-to-station mapping, road segment or distance documented.
  - DQ-DST-ARTEFACTS (minor): ts_local is "local time" with no stated timezone. Quality notes say UTC joins need DST-aware conversion.
- **Conditions:** Mobility Office adjusts for or splits the series at 2024-03-18; supplies counter-to-station mapping and direction semantics; confirms timezone, DST handling and zero versus missing hours; approves the request.

### internal.clinic.resp_visits_daily
- **What it is:** Aggregate respiratory visit counts per day and district (visit_date, district, visit_count), about 40,000 rows per catalog, no patient identifiers, daily refresh from 2022-01-01, last refreshed 2026-10-14. Owner: Clinical Analytics. The clinic data policy (wiki clinic_data_policy) permits this as the only clinic source.
- **Verdict:** feasible with conditions. Serves N4 for production only. No prototype coverage. Does not meet N5.
- **Key flags:**
  - ACC-RESTRICTED (major): auth required. Access was not tested.
  - INT-NO-JOIN-KEY (major): no district code list, boundary-change notes or joinability documentation.
  - DQ-UNDOCUMENTED-SCHEMA (major): respiratory diagnosis definition not documented. District is "district of residence" with no code list. Whether counts are by residence or clinic site is unknown.
- **Conditions:** Clinical Analytics approves access and states turnaround, supplies the respiratory definition, district code list and boundary changes, and reconciles the ~40,000 row count against daily by district grain. Data Protection Office to confirm aggregate use; no sign-off record was found.

### api.open_meteo_archive
- **What it is:** Public REST API for gridded hourly historical weather reanalysis, queried by latitude and longitude. Returns temperature_2m (°C) and relative_humidity_2m (%). Licence CC BY 4.0. Owner not stated. Refresh cadence unknown. Metadata last updated not stated. End date open.
- **Verdict:** feasible with conditions. Serves N3 in both windows.
- **Key flags:**
  - LIC-MIXED (major): licence.mixed_sources is true. The upstream Copernicus C3S reanalysis licence was not read.
  - INT-REPRESENTATIVENESS (major): modelled values on a grid cell, not station observations. Probe near Milan (45.46, 9.19) returned grid cell 45.448154, 9.169279, elevation 138 m. Representativeness for Valdena is untested.
  - LIC-ATTRIBUTION (minor): credit "Weather data by Open-Meteo.com."
- **Conditions:** Legal confirms upstream C3S terms and production-use sign-off. Client supplies a justified Valdena location; the Milan probe must not be used as the Valdena assumption. Data engineering confirms full-window coverage for 2004-03-10 to 2004-03-12 and 2024-01-01 to 2025-12-31; only 3-day probes were run. Environment Monitoring Unit validates grid-cell values against local station data before the model relies on them.
- **Register note:** the register default coordinates are 45.44, 10.99. The brief's Lisbon default claim is not supported and is not used.

### link.uci_360
- **What it is:** UCI dataset 360, a single CSV of hourly averaged readings from a road-level chemical multisensor device in an unnamed Italian city. Includes co-located reference analyser values (CO, NMHC, benzene, NOx, NO2), metal-oxide sensor responses, and T, RH and absolute humidity. About 9,357 rows; whole file read. Static one-off dataset. Owner not stated.
- **Verdict:** feasible with conditions. Serves N1 prototype (NO2 present, PM2.5 absent). Also provides T and RH for N3 prototype. Method benchmark only.
- **Key flags:**
  - LIC-NONCOMMERCIAL (blocker, judgement): UCI notes say "exclusively for research purposes; commercial purposes fully excluded." This conflicts with the CC BY 4.0 licence on the page. Treated as resolvable because the use is limited to the prototype benchmark.
  - DQ-SENTINEL-VALUES (major): missing values tagged as -200. Sample shows NMHC(GT) with 8,443 cells at -200, and C6H6(GT) with 366 values at -200 counted as negatives.
  - DQ-METADATA-CONTRADICTION (major): declared has_missing_values "no" and missing_values_symbol null, but notes describe -200 tags.
  - INT-REPRESENTATIVENESS (major): one site, one co-located analyser. Cannot be matched to Valdena.
  - LIC-ATTRIBUTION (minor): cite De Vito et al., Sens. and Act. B, 2008, DOI 10.24432/C59K5F.
- **Date note:** UCI notes say recordings span March 2004 to February 2005. The file runs 2004-03-10 to 2005-04-04. The file range is used.
- **Conditions:** Legal resolves the research-only versus CC BY conflict. Recode -200 to missing in all columns, including C6H6(GT). Use only for the prototype method, not for production or for Valdena district outcomes.

### link.lombardia_6eu4_4tja_097de4
- **What it is:** Dataset "Temperatura fino al 2010" from ARPA Lombardia's idro-nivo-meteorological network, on the Regione Lombardia open-data portal. Hourly air temperature (°C) per sensor, timestamp labelled as interval end (ora solare), value and status flag. Licence CC0 1.0. Creator ARPA Lombardia. Series end 2010-12-31. Refresh unknown. Sensor locations are in a separate register (nf78-nj6b), not profiled.
- **Verdict:** feasible with conditions. Prototype-only benchmark for N3 temperature.
- **Key flags:**
  - COV-GEO-MISMATCH (major): stations are in Lombardy. The client site is not stated to be in Lombardy.
  - INT-REPRESENTATIVENESS (major): network is hydrological, snow and meteorological, not urban. Representativeness for Valdena city-centre temperature unknown.
  - DQ-UNDOCUMENTED-SCHEMA (major): schema documented as free text only. Meaning of "Stato" not documented (only "VA" seen). Field names come from the CSV header and sample, not a data dictionary.
- **Coverage:** the single sensor sampled (id 13) covers 1987–1988 only. Coverage of 2004-03-10 to 2005-04-04 is not verified. FRS-STALE was dismissed: the prototype window is historical by design.
- **Conditions:** profile register nf78-nj6b and the data for the prototype window; client states its region; ARPA or portal supplies the data dictionary for "Stato" and the timestamp convention.
- **Humidity:** this dataset does not cover humidity. Prototype humidity is only in UCI and in a separate unprofiled dataset.

### link.europa_sdg_11_52_099aa6
- **What it is:** Eurostat table sdg_11_52, premature deaths due to PM2.5 exposure, Italy only, annual, in number and rate units. 36 cells across 2005–2023, no missing values in the API response. Metadata last updated 2025-12-09. Licence not found in link metadata. Owner not stated in link metadata.
- **Verdict:** feasible with conditions. National annual context only for N6. No hourly, district, station or traffic data.
- **Key flags:**
  - LIC-UNKNOWN (blocker): no licence in metadata. The Eurostat copyright page redirected to EU Login with no readable text. Resolved under rule 2 because the publisher has a copyright page, so the verdict is conditional rather than not feasible. Legal must confirm.
  - COV-PARTIAL-WINDOW (major): prototype is 24% covered (2005 only). Production is 0% covered; 2023 is the latest year.
  - TIME_GAPS warning: a 2006 gap. Treat as missing, not zero. Use the NR (number) unit unless the rate denominator is documented.
- **Conditions:** Legal confirms terms. Client accepts N6 as labelled national context with the gap. Data engineering handles the 2006 gap and units.

### link.data_open_air_chicago_hour_aggre_d4970b
- **What it is:** Link to a catalog.data.gov page titled "open-air-chicago-hour-aggregations," described by its title as hourly air-quality data from a US city. Contents, fields, period, owner and licence are unknown.
- **Verdict:** not feasible.
- **Key flags:**
  - ACC-UNREACHABLE (blocker): inspect_dataset_link returned DOMAIN_NOT_ALLOWLISTED (config/allowlist.json). Recorded as a finding. No alternative route attempted.
  - LIC-UNKNOWN (blocker): no licence could be read.
  - COV-GEO-MISMATCH (major): US coverage (Chicago), against an Italy geography.
- **Conditions:** none. It is not a candidate for N1 in either window.

## 4. Red-flag register

| source_id | code | severity | evidence | raised by (rule or judgement) |
|---|---|---|---|---|
| internal.airq.station_readings | ACC-RESTRICTED | major | auth required; classification internal; approval status and turnaround not stated | rule |
| internal.airq.station_readings | GOV-CATALOG-WIKI-CONFLICT | major | VR-03 switched off 2024-06-30 per wiki (edited 2024-07-01); catalog still active, end null | judgement |
| internal.airq.station_readings | INT-NO-JOIN-KEY | major | no station register or counter mapping | judgement |
| internal.traffic.hourly_counts | ACC-RESTRICTED | major | auth required; request to Mobility Office | rule |
| internal.traffic.hourly_counts | GOV-CATALOG-WIKI-CONFLICT | major | counting basis changed 2024-03-18; wiki (edited 2024-04-02) warns; catalog silent | judgement |
| internal.traffic.hourly_counts | INT-NO-JOIN-KEY | major | no counter-to-station mapping or distances | judgement |
| internal.traffic.hourly_counts | DQ-DST-ARTEFACTS | minor | ts_local timezone not stated | judgement |
| internal.clinic.resp_visits_daily | ACC-RESTRICTED | major | auth required; access not tested | rule |
| internal.clinic.resp_visits_daily | INT-NO-JOIN-KEY | major | no district code list or boundary changes | judgement |
| internal.clinic.resp_visits_daily | DQ-UNDOCUMENTED-SCHEMA | major | respiratory definition missing; no units or coding notes | judgement |
| api.open_meteo_archive | LIC-MIXED | major | mixed_sources true; upstream C3S licence not read | rule |
| api.open_meteo_archive | INT-REPRESENTATIVENESS | major | grid-cell model values; Valdena location unset | judgement |
| api.open_meteo_archive | LIC-ATTRIBUTION | minor | attribution text required | rule |
| link.uci_360 | LIC-NONCOMMERCIAL | blocker | research-only note conflicts with CC BY 4.0 | judgement |
| link.uci_360 | DQ-SENTINEL-VALUES | major | -200 missing tags; C6H6(GT) negatives | judgement |
| link.uci_360 | DQ-METADATA-CONTRADICTION | major | has_missing_values "no" vs -200 note | rule |
| link.uci_360 | INT-REPRESENTATIVENESS | major | single site, single city | judgement |
| link.uci_360 | LIC-ATTRIBUTION | minor | citation required | rule |
| link.lombardia_6eu4_4tja_097de4 | COV-GEO-MISMATCH | major | Lombardy stations; Valdena not stated in Lombardy | judgement |
| link.lombardia_6eu4_4tja_097de4 | INT-REPRESENTATIVENESS | major | hydro-nivo-meteorological network, not urban | judgement |
| link.lombardia_6eu4_4tja_097de4 | DQ-UNDOCUMENTED-SCHEMA | major | free text only; "Stato" undocumented | judgement |
| link.europa_sdg_11_52_099aa6 | LIC-UNKNOWN | blocker | no licence in metadata; copyright page unreadable | rule |
| link.europa_sdg_11_52_099aa6 | COV-PARTIAL-WINDOW | major | 2005–2023 only; 0% production coverage | rule |
| link.data_open_air_chicago_hour_aggre_d4970b | ACC-UNREACHABLE | blocker | host not allowlisted (DOMAIN_NOT_ALLOWLISTED) | rule |
| link.data_open_air_chicago_hour_aggre_d4970b | LIC-UNKNOWN | blocker | no licence readable | rule |
| link.data_open_air_chicago_hour_aggre_d4970b | COV-GEO-MISMATCH | major | US coverage vs Italy | judgement |

Two blocker-severity flags (LIC-NONCOMMERCIAL on UCI, LIC-UNKNOWN on Eurostat) are resolved as conditions, not as blockers, under the stated rules. Legal must confirm both before use.

## 5. Conditions and owners

| Condition | Source(s) | Who can resolve | Blocking which need |
|---|---|---|---|
| Resolve research-only vs CC BY conflict; limit use to prototype | link.uci_360 | Legal | N1 prototype; N3 prototype (T/RH) |
| Recode -200 to missing, all columns | link.uci_360 | data engineering | N1 prototype; N3 prototype |
| Confirm Valdena location and record assumption in decisions.md | api.open_meteo_archive | client | N3 (both windows) |
| Confirm upstream C3S terms and production-use sign-off | api.open_meteo_archive | Legal | N3 (both windows) |
| Confirm full-window archive coverage (both windows) | api.open_meteo_archive | data engineering | N3 (both windows) |
| Validate grid-cell T and RH against local station data | api.open_meteo_archive | Environment Monitoring Unit | N3 production |
| Profile sensor coverage for prototype window via register nf78-nj6b | link.lombardia_6eu4_4tja_097de4 | data engineering | N3 prototype temperature |
| Confirm meaning of "Stato" and timestamp convention | link.lombardia_6eu4_4tja_097de4 | data engineering; ARPA via portal | N3 prototype temperature |
| State region; use Lombardy series as method benchmark only if outside Lombardy | link.lombardia_6eu4_4tja_097de4 | client | N3 prototype temperature |
| Approve warehouse access and state turnaround | internal.airq.station_readings | Environment Monitoring Unit | N1 production |
| Exclude or treat VR-03 readings after 2024-06-30; confirm network status | internal.airq.station_readings | Environment Monitoring Unit | N1 production |
| Supply station register and station-to-counter mapping | internal.airq.station_readings; internal.traffic.hourly_counts | Environment Monitoring Unit; Mobility Office | N1 production; N2 production |
| Sample for missing-value encoding, negatives, continuity; reconcile 4.2M rows | internal.airq.station_readings | data engineering with Environment Monitoring Unit | N1 production |
| Confirm internal use in a clinic warning model | internal.airq.station_readings | Legal | N1 production |
| Adjust or split series at 2024-03-18 counting-basis change | internal.traffic.hourly_counts | Mobility Office | N2 production |
| Confirm timezone of ts_local, DST and zero vs missing encoding | internal.traffic.hourly_counts | Mobility Office | N2 production |
| Approve warehouse request | internal.traffic.hourly_counts | Mobility Office | N2 production |
| Approve access and state turnaround | internal.clinic.resp_visits_daily | Clinical Analytics | N4 production |
| Supply respiratory definition, district code list, boundary changes, residence vs site | internal.clinic.resp_visits_daily | Clinical Analytics | N4 production |
| Confirm aggregate use under clinic policy | internal.clinic.resp_visits_daily | Data Protection Office | N4 production |
| Reconcile ~40,000 rows against daily by district; report gaps | internal.clinic.resp_visits_daily | Clinical Analytics | N4 production |
| Confirm Eurostat terms | link.europa_sdg_11_52_099aa6 | Legal | N6 (both windows) |
| Accept N6 as annual national context with gaps labelled | link.europa_sdg_11_52_099aa6 | client | N6 (both windows) |
| Treat 2006 gap as missing; use NR unit unless denominator documented | link.europa_sdg_11_52_099aa6 | data engineering | N6 (both windows) |

No condition is open for the Chicago link: it is not feasible and has no route to resolve.

## 6. Recommended next steps

1. **Raise access requests now** to the Environment Monitoring Unit (station readings), the Mobility Office (traffic counts) and Clinical Analytics (clinic counts). Ask each for an approval decision and turnaround date. Access was not granted or tested in this discovery.
2. **Raise a Legal review** covering four items: the UCI research-only conflict, the Open-Meteo upstream C3S terms, the Eurostat terms, and whether internal station data may be used in a clinic warning model.
3. **Decide the Valdena location** for the Open-Meteo point query. Record the justification in decisions.md. Do not use the Milan probe coordinates.
4. **Confirm the station status** with the Environment Monitoring Unit: VR-03 and the network's active state after 2024-06-30. Ask the Mobility Office for the 2024-03-18 adjustment method.
5. **Decide whether the prototype may start** on the UCI benchmark, once Legal has responded and the -200 recode is in place. Decide whether to use Lombardy temperature only if the client's region is outside Lombardy.
6. **Profile first, once the gate is passed:**
   - the station table sample: sentinels, negatives, continuity, VR-03 post-June 2024 values;
   - the traffic sample: the 2024-03-18 break, timezone and DST encoding;
   - the clinic aggregate sample: the district list and row count;
   - the Open-Meteo archive coverage for both full windows.
7. **Do not pursue** the Chicago link or any alternative route to it. Do not seek patient-level data (N5).

## 7. Open questions for the human reviewer

1. What is the Valdena city location (coordinates and justification) for the Open-Meteo query? No source names the city.
2. Has Legal cleared the UCI research-only versus CC BY 4.0 conflict for use as a prototype benchmark?
3. Is the city station network active after 2024-06-30? The wiki says VR-03 was switched off, but the catalog says active. Which record should the warehouse follow?
4. What is the adjustment method for the 2024-03-18 traffic counting-basis change, and does the Mobility Office want the series split or adjusted?
5. Which Italian region is the client in? This determines whether the ARPA Lombardia series is a benchmark only or usable.
6. Does Clinical Analytics count visits by district of residence or by clinic site, and what is the respiratory diagnosis definition?
7. Does the Data Protection Office accept aggregate district counts for a clinic warning model? No sign-off record was found.
8. Is the Eurostat dataset licensed for the client's use? The copyright page was unreadable.
9. Should the client accept annual national PM2.5 context (N6) with no 2024–2025 values?
10. Who is the owner of the UCI and Open-Meteo datasets, and what is their refresh schedule? Neither source states an owner or refresh cadence.

---

## Human review gate

Draft generated by the discovery agents for UC1 on 2026-11-16T13:13:04Z (model claude-haiku-5-5). It is a draft for review, not a decision.

Before any profiling or pipeline work, the reviewer confirms:

- [ ] Each verdict is supported by the evidence cited
- [ ] Every licence was read at its source, and the attribution text is recorded
- [ ] Access requests for the feasible-with-conditions sources are raised with the named owners
- [ ] Consent and purpose limits are understood, and the target population is filtered accordingly

**Blocker flags on sources not rejected (resolve or justify):**

- link.europa_sdg_11_52_099aa6: LIC-UNKNOWN
- link.uci_360: LIC-NONCOMMERCIAL

**Open questions:**

1. What is the Valdena city location (coordinates and justification) for the Open-Meteo point query? No source names the city, and decisions.md was not written in this run.
2. Has Legal cleared the UCI 360 research-only versus CC BY 4.0 conflict for use as a prototype benchmark?
3. Is the city station network active after 2024-06-30? The wiki says VR-03 was switched off; the catalog still says active. Which record should the warehouse follow?
4. What adjustment method applies to the 2024-03-18 traffic counting-basis change, and should the series be adjusted or split at that date?
5. Which Italian region is the client in? This decides whether the ARPA Lombardia temperature series can be used beyond a method benchmark.
6. Does Clinical Analytics count visits by district of residence or by clinic site, and what is the respiratory diagnosis definition?
7. Does the Data Protection Office accept aggregate daily district counts for a clinic warning model? No sign-off record was found.
8. Is the Eurostat sdg_11_52 dataset licensed for the client's use? The copyright page was unreadable and no licence is in the metadata.
9. Should the client accept annual national PM2.5 context (N6) with no 2024–2025 values and a 2006 gap?
10. Who owns the UCI and Open-Meteo datasets, and what is their refresh schedule? Neither source states an owner or cadence.

Reviewer: ____________________   Date: __________   Decision: proceed / proceed with conditions / stop
