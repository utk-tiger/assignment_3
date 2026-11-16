# UC1 Feasibility Memo: Air quality, traffic and poor-air days (Valdena Civic Health Office)

As-of date: 2026-10-15. Source: discovery results generated 2026-11-15 (model output), plus the record summaries. No new tool calls were made for this memo.

## 1. Executive summary

**Verdict: NOT FEASIBLE for the full UC1 scope as documented. The prototype can proceed with conditions. The production build is blocked until the traffic gap (N2) is resolved or the scope changes.**

Facts that drive the verdict:

1. **N2 (hourly traffic near the monitoring stations) is a must need and is unmet.** The only traffic source, `internal.traffic.hourly_counts`, has no documented mapping from counter to monitoring station, road segment or distance. Under rule 7 it is rated not_feasible. No other source covers N2.
2. **The other two must needs have conditional routes.** N1 (air pollutants) has a prototype route (`link.uci_360`, research-only licence) and a production route (`internal.airq.station_readings`, access by request). N3 (temperature and humidity) has `api.open_meteo_archive` for both windows and `link.lombardia_6eu4_4tja_097de4` for prototype temperature only.
3. **The city's own station data has an unresolved status conflict.** The catalog shows the network as active with no end date. The wiki says station VR-03 was switched off on 2024-06-30. Continuity of the other stations through 2025 is unconfirmed.
4. **Clinic data is limited to daily district counts.** `internal.clinic.resp_visits_daily` is the only clinic source the policy permits. It can serve N4 (should) for production only. Patient-level records (N5, could) are not permitted, so N5 is unmet.
5. **Several sources carry blocker-severity flags that the rules treat as resolvable.** These are a research-only licence on the UCI data, an unknown licence on the Eurostat series, and an unreachable host for the Chicago link. The Chicago link is recorded as a finding and is not to be retried.

## 2. Need coverage

| Need ID | Need | Priority | Status | Best source(s) | Gap |
|---|---|---|---|---|---|
| N1 | Hourly air-pollutant concentrations (NO2, PM2.5) | must | met with conditions (prototype and production) | `link.uci_360` (prototype); `internal.airq.station_readings` (production) | Prototype: one road-level site, research-only licence, -200 sentinels. Production: Environment Monitoring Unit approval not yet given; VR-03 switched off 2024-06-30; 2025 continuity unverified. |
| N2 | Hourly vehicle traffic near the monitoring stations | must | **unmet** | `internal.traffic.hourly_counts` (rated not_feasible) | No counter-to-station mapping, so the join cannot be made. Count basis changed on 2024-03-18. Access restricted. Timezone undocumented. |
| N3 | Hourly temperature and humidity | must | met with conditions | `api.open_meteo_archive` (both windows); `link.lombardia_6eu4_4tja_097de4` (prototype, temperature only) | Open-Meteo is modelled reanalysis on a grid cell, not station data. Valdena location is not set. Licence sign-off pending. ARPA covers Lombardy, ends 2010, and the humidity dataset is not profiled. |
| N4 | Daily respiratory clinic visits by district | should | met with conditions (production only) | `internal.clinic.resp_visits_daily` | Diagnosis definition, district code list, Data Protection sign-off and small-cell suppression threshold are all unconfirmed. |
| N5 | Patient-level clinic visit records | could | **unmet** | none | Clinic policy permits only the daily district aggregate. |
| N6 | National yearly context: PM2.5 deaths | could | partially met (prototype only) | `link.europa_sdg_11_52_099aa6` | Covers 2005 only within the prototype window. No 2024–2025 values. Licence unknown. |

## 3. Source assessments

Order: feasible, then with conditions, then not feasible. No source reached a plain "feasible" verdict, so all sources in the first group are "with conditions" and the not-feasible sources follow.

### With conditions

**api.open_meteo_archive** (N3, both windows)
- What it is: gridded hourly historical weather reanalysis served by a public REST API, queried by latitude and longitude. Probes returned hourly temperature and relative humidity for 2004-03-10 to 2004-03-12 and 2024-01-01 to 2024-01-03.
- Verdict: feasible with conditions.
- Key flags: LIC-MIXED (major): output is CC BY 4.0, but the upstream Copernicus C3S licence was not read. INT-REPRESENTATIVENESS (major): modelled values, not station observations; representativeness for the client's stations is untested. LIC-ATTRIBUTION (minor).
- Conditions: Legal confirms upstream terms and gives production sign-off. Set and justify Valdena coordinates. Confirm archive start and end dates for both windows (only the probed dates are confirmed). Record both attributions.
- Note: the record shows no owner, refresh cadence or metadata update date. These are unknown.

**internal.airq.station_readings** (N1, production)
- What it is: hourly NO2 and PM2.5 from the city's own stations, keyed by station and UTC hour. Catalog: about 4.2 million rows, coverage from 2023-01-01, hourly refresh, last refreshed 2026-10-14. Owner: Environment Monitoring Unit. Access is by request via warehouse SQL.
- Verdict: feasible with conditions.
- Key flags: ACC-RESTRICTED (major): approval status and turnaround not stated. GOV-CATALOG-WIKI-CONFLICT (major): catalog says active with no end date; wiki says VR-03 was switched off on 2024-06-30.
- Conditions: approval and turnaround from the unit. Exclude VR-03 after 2024-06-30 and treat it as no data, not zero. Confirm continuity and station count through 2025-12-31. Obtain the station register (needed for any N2 link). Profile for sentinels, negatives and validated status.
- Note: no sample was taken. The prototype window is not covered by this source.

**internal.clinic.resp_visits_daily** (N4, production)
- What it is: daily respiratory visit counts by district (visit_date, district, visit_count). About 40,000 rows per catalog. Catalog says no patient identifiers. Refresh daily from 2022-01-01, last refreshed 2026-10-14. Owner: Clinical Analytics.
- Verdict: feasible with conditions.
- Key flags: ACC-RESTRICTED (major): request to Clinical Analytics; access not tested. DQ-UNDOCUMENTED-SCHEMA (major): no respiratory definition, no district code list, no units or coding-change notes. GOV-PURPOSE-LIMITATION (major): the policy permits this table for this purpose, but no record shows Data Protection sign-off for warning-model use.
- Conditions: access approval. Definition, code list and boundary history. State whether counts are by residence or clinic site. Written Data Protection confirmation and a suppression threshold. Check row count, date gaps and refresh consistency since 2022.

**link.europa_sdg_11_52_099aa6** (N6, prototype and production windows)
- What it is: Eurostat table sdg_11_52, Italy only, PM2.5 premature deaths, annual, in number and rate units. 18 years (2005–2023). Metadata last updated 2025-12-09.
- Verdict: feasible with conditions (annual national context only).
- Key flags: LIC-UNKNOWN (blocker): no licence text found; the copyright page redirected to a login. COV-PARTIAL-WINDOW (major): 2005 only in the prototype window; 0% coverage of 2024–2025. DQ-UNDOCUMENTED-SCHEMA (major): rate denominator (RT) not stated. DQ-METADATA-CONTRADICTION (major): TIME_GAPS warning; 2006 absent.
- Conditions: Legal confirms terms. Confirm the RT denominator. Treat 2006 as missing, not zero. Use only as national context in the prototype.

**link.lombardia_6eu4_4tja_097de4** (N3 temperature, prototype)
- What it is: ARPA Lombardia hourly air temperature, Lombardy sensor network, ends 2010-12-31. Licence CC0 1.0. Sample showed hourly steps, all flagged VA, for one sensor in 1987 (sample only).
- Verdict: feasible with conditions (benchmark only).
- Key flags: COV-GEO-MISMATCH (major): Lombardy, not Valdena; coverage of the client's city unknown. FRS-METADATA-DATE-MISLEADING (minor): modified 2025-05-06 but the series ends 2010.
- Conditions: state the Lombardy assumption. Verify coverage of 2004-03-10 to 2005-04-04 (the 178-sensor figure is unverified). Profile the humidity dataset and station register before claiming N3 humidity. Align timestamps (standard time, interval-end labels). Production use needs Legal sign-off and is not possible because the series ends in 2010.

**link.uci_360** (N1, prototype)
- What it is: single CSV of hourly averaged readings from a road-level multisensor device in an unnamed Italian city, with reference analyser values (CO, NMHC, benzene, NOx, NO2), 2004-03-10 to 2005-04-04. About 9,357 rows. One-off dataset. No traffic or clinic data.
- Verdict: feasible with conditions (prototype only).
- Key flags: LIC-NONCOMMERCIAL (blocker): page says CC BY 4.0; dataset notes say research use only, commercial excluded. DQ-SENTINEL-VALUES (major): -200 missing tags; C6H6 has 366 values that pass a naive filter. DQ-METADATA-CONTRADICTION (major): documentation says missing values exist, but metadata says none. INT-REPRESENTATIVENESS (major): one site, one reference analyser, uncalibrated sensors. COV-GEO-MISMATCH (major): city not named. FRS-STALE (major) was dismissed by rule 5 because the window is historical. LIC-ATTRIBUTION (minor).
- Conditions: Legal review of the licence conflict, required before any use beyond prototyping. Recode -200 to missing, including C6H6. Use as a method benchmark only. Treat the date span conflict (2004-03 to 2005-02 vs 2005-04) and the 9,357 vs 9,358 row count as documentation issues.

### Not feasible

**internal.traffic.hourly_counts** (N2, production)
- What it is: hourly vehicle counts per road counter, owned by the Mobility Office. About 15 million rows, coverage from 2021-01-01, hourly refresh, last refreshed 2026-10-12.
- Verdict: **not feasible** (rule 7).
- Key flags: INT-NO-JOIN-KEY (major): no counter-to-station, segment or coordinate field. GOV-CATALOG-WIKI-CONFLICT (major): on 2024-03-18 counts changed from per-direction to both-directions combined; the catalog does not note this. ACC-RESTRICTED (major): request to the Mobility Office; access not tested.
- What would change the verdict: a validated counter-to-station register with distances. Timezone of the local timestamp is also undocumented and must be clarified.

**link.data_open_air_chicago_hour_aggre_d4970b** (N1, prototype)
- What it is: a catalog.data.gov link titled as hourly air-quality aggregations for Chicago, US. Not reached.
- Verdict: **not feasible**.
- Key flags: ACC-UNREACHABLE (blocker): host not allowlisted (DOMAIN_NOT_ALLOWLISTED). LIC-UNKNOWN (blocker): no licence readable. COV-GEO-MISMATCH (major): US city, use case is Italy.
- Recorded as a finding. Not to be retried through another route. Contents, period, owner and licence are unverified.

## 4. Red-flag register

| Source ID | Code | Severity | Evidence | Raised by |
|---|---|---|---|---|
| api.open_meteo_archive | LIC-MIXED | major | Upstream C3S licence not read | rule |
| api.open_meteo_archive | LIC-ATTRIBUTION | minor | Upstream attribution not read | rule |
| api.open_meteo_archive | INT-REPRESENTATIVENESS | major | Grid-cell model values; Valdena coordinates not stated | judgement |
| internal.airq.station_readings | ACC-RESTRICTED | major | Auth required; approval and turnaround not stated | rule |
| internal.airq.station_readings | GOV-CATALOG-WIKI-CONFLICT | major | Catalog active vs wiki VR-03 off 2024-06-30 | judgement |
| internal.clinic.resp_visits_daily | ACC-RESTRICTED | major | Access not tested | rule |
| internal.clinic.resp_visits_daily | DQ-UNDOCUMENTED-SCHEMA | major | No diagnosis definition or district code list | judgement |
| internal.clinic.resp_visits_daily | GOV-PURPOSE-LIMITATION | major | No Data Protection sign-off for warning use | judgement |
| internal.traffic.hourly_counts | INT-NO-JOIN-KEY | major | No counter-to-station mapping | judgement |
| internal.traffic.hourly_counts | GOV-CATALOG-WIKI-CONFLICT | major | 2024-03-18 count basis change not in catalog | judgement |
| internal.traffic.hourly_counts | ACC-RESTRICTED | major | Access not tested | rule |
| link.data_open_air_chicago_hour_aggre_d4970b | ACC-UNREACHABLE | blocker | DOMAIN_NOT_ALLOWLISTED | rule |
| link.data_open_air_chicago_hour_aggre_d4970b | LIC-UNKNOWN | blocker | No licence readable | rule |
| link.data_open_air_chicago_hour_aggre_d4970b | COV-GEO-MISMATCH | major | US city, Italy use case | judgement |
| link.europa_sdg_11_52_099aa6 | LIC-UNKNOWN | blocker | No licence text; terms page redirected to login | rule |
| link.europa_sdg_11_52_099aa6 | COV-PARTIAL-WINDOW | major | 2005 only in prototype; no 2024–2025 | rule |
| link.europa_sdg_11_52_099aa6 | DQ-UNDOCUMENTED-SCHEMA | major | RT denominator not stated | judgement |
| link.europa_sdg_11_52_099aa6 | DQ-METADATA-CONTRADICTION | major | TIME_GAPS; 2006 absent | judgement |
| link.lombardia_6eu4_4tja_097de4 | COV-GEO-MISMATCH | major | Lombardy, not Valdena | judgement |
| link.lombardia_6eu4_4tja_097de4 | FRS-METADATA-DATE-MISLEADING | minor | Modified 2025; series ends 2010 | judgement |
| link.uci_360 | LIC-NONCOMMERCIAL | blocker | CC BY 4.0 vs research-only note | judgement |
| link.uci_360 | DQ-SENTINEL-VALUES | major | -200 missing tags; C6H6 issue | judgement |
| link.uci_360 | DQ-METADATA-CONTRADICTION | major | Missing values documented but metadata says none | rule |
| link.uci_360 | INT-REPRESENTATIVENESS | major | Single road site, uncalibrated sensors | judgement |
| link.uci_360 | COV-GEO-MISMATCH | major | City not named | judgement |
| link.uci_360 | FRS-STALE | major | Dismissed by rule 5 (historical window) | rule (dismissed) |
| link.uci_360 | LIC-ATTRIBUTION | minor | Citation required | rule |

## 5. Conditions and owners

| Condition | Source(s) | Who can resolve | Blocking which need |
|---|---|---|---|
| Set and justify Valdena coordinates in decisions.md | api.open_meteo_archive | Environment Monitoring Unit with analytics team | N3 |
| Legal sign-off on upstream C3S terms for production | api.open_meteo_archive | Legal | N3 (production) |
| Check reanalysis representativeness against 2024 station readings | api.open_meteo_archive | Environment Monitoring Unit, analytics team | N3 |
| Approve warehouse request and state turnaround | internal.airq.station_readings | Environment Monitoring Unit | N1 (production) |
| Confirm VR-03 status; exclude after 2024-06-30 | internal.airq.station_readings | Environment Monitoring Unit | N1 (production) |
| Confirm station continuity through 2025 and station count | internal.airq.station_readings | Environment Monitoring Unit | N1 (production) |
| Obtain station register with traffic-counter mapping | internal.airq.station_readings; internal.traffic.hourly_counts | Environment Monitoring Unit; Mobility Office | N2 |
| Approve access request | internal.clinic.resp_visits_daily | Clinical Analytics | N4 |
| Supply diagnosis definition, district code list, boundary history, residence vs site | internal.clinic.resp_visits_daily | Clinical Analytics | N4 |
| Written confirmation of warning-model use; suppression threshold | internal.clinic.resp_visits_daily | Data Protection Office | N4 |
| Validated counter-to-station register with distances; timezone; 2024-03-18 adjustment | internal.traffic.hourly_counts | Mobility Office | N2 (blocking, no route yet) |
| Licence terms readable and confirmed | link.europa_sdg_11_52_099aa6 | Legal | N6 |
| Confirm RT denominator | link.europa_sdg_11_52_099aa6 | analytics team | N6 |
| Legal review of research-only licence conflict | link.uci_360 | Legal | N1 (prototype) |
| Recode -200 to missing across all columns | link.uci_360 | analytics team | N1 (prototype) |
| Verify ARPA coverage for 2004-03 to 2005-04; profile humidity dataset and register | link.lombardia_6eu4_4tja_097de4 | analytics team | N3 humidity (prototype) |
| Chicago link: unreachable; no owner | link.data_open_air_chicago_hour_aggre_d4970b | none (not retried) | none |

## 6. Recommended next steps

1. **Raise access requests now:** Environment Monitoring Unit (station readings, station register), Clinical Analytics (clinic daily table), Mobility Office (traffic counts and counter register). Ask each for a turnaround date.
2. **Ask Legal for three reviews:** upstream C3S terms for Open-Meteo; the research-only licence on the UCI data (prototype use); the Eurostat terms page.
3. **Ask the Data Protection Office** to confirm in writing that aggregate daily district counts may be used for the warning model, and to set a suppression threshold.
4. **Decide the Valdena location** and record it as an assumption in decisions.md. Do not use the 45.46/9.19 probe point or the register default 45.44/10.99 without a stated reason.
5. **Decide whether N2 stays a must.** Without a counter-to-station register, the production build cannot meet its traffic requirement. Either obtain the register or change the scope.
6. **Gate for prototype profiling:** Legal review of the UCI licence; recode -200 sentinels; confirm Open-Meteo archive dates for 2004-03-10 to 2005-04-04; verify ARPA coverage for that window. Then profile the UCI file as a method benchmark only.
7. **Gate for production profiling:** access approved for station readings and clinic table; VR-03 status confirmed; station continuity through 2025 confirmed; clinic definitions and code list received; Open-Meteo production sign-off.
8. **Do not profile N5 or any patient-level data.** Policy does not permit it.

## 7. Open questions for the human reviewer

1. Which city and coordinates should represent Valdena? No source names it, and the Open-Meteo and representativeness checks depend on this.
2. Can the Mobility Office supply a validated counter-to-station register with distances? If not, is the production scope still viable without N2?
3. Should the UCI research-only licence conflict (rated blocker, but verdict "with conditions") be accepted as a prototype-only gate pending Legal review?
4. Should the Eurostat "LIC-UNKNOWN" blocker, which is also rated resolvable, block use of N6 until Legal confirms the terms?
5. Was VR-03 really switched off on 2024-06-30, and are the other stations still reporting through 2025-12-31?
6. Does the Data Protection Office accept warning-model use of aggregate daily district counts, and what suppression threshold applies?
7. Is N6 (national PM2.5 deaths, annual) still needed, given it has no 2024–2025 values?
8. Is a humidity source needed for the prototype, given the ARPA humidity dataset has not been profiled?
9. Should the Chicago link be dropped from the register, given it is unreachable and off-geography?

---

## Human review gate

Draft generated by the discovery agents for UC1 on 2026-11-15T21:32:34Z (model claude-haiku-5-5). It is a draft for review, not a decision.

Before any profiling or pipeline work, the reviewer confirms:

- [ ] Each verdict is supported by the evidence cited
- [ ] Every licence was read at its source, and the attribution text is recorded
- [ ] Access requests for the feasible-with-conditions sources are raised with the named owners
- [ ] Consent and purpose limits are understood, and the target population is filtered accordingly

**Blocker flags on sources not rejected (resolve or justify):**

- link.europa_sdg_11_52_099aa6: LIC-UNKNOWN
- link.uci_360: LIC-NONCOMMERCIAL

**Open questions:**

1. Which city and coordinates should represent Valdena? No source names it, and the Open-Meteo and representativeness checks depend on this.
2. Can the Mobility Office supply a validated counter-to-station register with distances? If not, is the production scope still viable without N2?
3. Should the UCI research-only licence conflict (rated blocker, but verdict 'with conditions') be accepted as a prototype-only gate pending Legal review?
4. Should the Eurostat LIC-UNKNOWN blocker, which is also rated resolvable, block use of N6 until Legal confirms the terms?
5. Was VR-03 really switched off on 2024-06-30, and are the other stations still reporting through 2025-12-31?
6. Does the Data Protection Office accept warning-model use of aggregate daily district counts, and what small-cell suppression threshold applies?
7. Is N6 (national PM2.5 deaths, annual) still needed, given it has no 2024-2025 values?
8. Is a humidity source needed for the prototype, given the ARPA humidity dataset has not been profiled?
9. Should the Chicago link be dropped from the register, given it is unreachable and off-geography?

Reviewer: ____________________   Date: __________   Decision: proceed / proceed with conditions / stop
