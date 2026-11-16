# Test case results (rubric Sheet 2): actual outputs

Generated 2026-11-16 by running each check listed in the rubric.

## TC-001
```
$ pytest tests/test_learner_gaps.py -k g1 -q -> 9 passed, 12 deselected in 0.03s
extract_licence(uci_321_repository_page.html) = {"licence_name": "CC BY 4.0", "licence_url": "https://creativecommons.org/licenses/by/4.0/legalcode", "snippet": "This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license.", "found_in": "link"}
```

## TC-002
```
extract_licence(zenodo_record_landing_page.html) = {"licence_name": "CC BY 4.0", "licence_url": "https://creativecommons.org/licenses/by/4.0/legalcode", "snippet": "https://creativecommons.org/licenses/by/4.0/legalcode", "found_in": "json-ld"}
```

## TC-003
```
extract_licence(kaggle_ecommerce_landing_page.html) = {"licence_name": null, "licence_url": null, "snippet": "{\"@type\": \"CreativeWork\", \"name\": \"Unknown\", \"url\": \"\"}", "found_in": "json-ld"}
```

## TC-004
```
licence_name for ODbL URL / choosealicense CC0 URL / {name: 'CC BY-NC-SA 4.0'}: 'ODbL 1.0' | 'CC0 1.0' | 'CC BY-NC-SA 4.0'
```

## TC-005
```
OGL link -> OGL v3.0; CC BY-NC link text -> CC BY-NC 4.0; no terms -> {"licence_name": null, "licence_url": null, "snippet": null, "found_in": null}
```

## TC-006
```
$ pytest tests/test_learner_gaps.py -k g3 -q -> 2 passed, 19 deselected in 0.02s
keys=['dimensions', 'expected_cells', 'geo_codes', 'label', 'missing_cells', 'source', 'status_counts', 'time', 'updated', 'value_count', 'warnings']; dimensions=['freq', 'indic_is', 'ind_type', 'unit', 'geo', 'time']; time=2009..2011; geo_codes=['BE', 'DE', 'IE', 'ES', 'FR', 'NL', 'PT', 'UK']; expected_cells=24, value_count=24, missing_cells=0; warnings=['NON_ISO_GEO_CODES']
```

## TC-007
```
geo_codes=['FR', 'EL']; time.values=['2010', '2011']; value_count=3; missing_cells=1; status_counts={'p': 1}; warnings=['MISSING_CELLS', 'NON_ISO_GEO_CODES']
```

## TC-008
```
$ pytest tests/test_learner_gaps.py -k g4 -q -> 7 passed, 14 deselected in 0.02s
codes=['COV-OUT-OF-WINDOW', 'FRS-STALE']; evidence=['Source covers 1990-01-01..1998-12-31, which does not overlap any target window (prototype window 2004-03-10..2005-04-04: 0% covered).', 'Data ends 1998-12-31, more than 5 years before as_of 2026-10-15 (cutoff 2021-10-15).']
```

## TC-009
```
codes=['COV-PARTIAL-WINDOW']; evidence=['Source covers 2005-01-01..2023-12-31; below the 95% coverage threshold for prototype (24%), production (0%) (prototype window 2004-03-10..2005-04-04: 24% covered; production window 2024-01-01..2025-12-31: 0% covered).']
```

## TC-010
```
codes=['COV-PARTIAL-WINDOW']; evidence=['Source covers 2024-06-01..open-ended (treated as covered up to as_of 2026-10-15); below the 95% coverage threshold for production (79%) (production window 2024-01-01..2025-12-31: 79% covered).']
```

## TC-011
```
full coverage: codes=['FRS-STALE'] (Data ends 2005-04-04, more than 5 years before as_of 2026-10-15 (cutoff 2021-10-15).); static source: []
```

## TC-012
```
monthly for N1 -> ['COV-GRAIN-MISMATCH']; annual for N1 -> ['COV-GRAIN-MISMATCH']; daily for N4 -> []; event for N5 -> []; 15min for N1 -> []; hourly for N99 -> []
```

## TC-013
```
doc says missing, metadata no (UCI 235) -> ['DQ-METADATA-CONTRADICTION']; doc says no missing (UCI 321) -> []; -200 note, metadata no (UCI 360) -> ['DQ-METADATA-CONTRADICTION']; honest declaration -> []
```

## TC-014
```
warnings=[]; flags=['FRS-STALE', 'LIC-UNKNOWN'] (no rule skipped as NOT_IMPLEMENTED)
```

## TC-015
```
$ pytest tests/test_learner_gaps.py -k g5 -q -> 1 passed, 20 deselected in 0.02s
'LEARNER TODO (G5)' present: False; heading: '## Verdict calibration'; numbered/bulleted lines under it: 16 (12 numbered rules)
```

## TC-016
```
$ pytest tests/test_learner_gaps.py -k g6 -q -> 2 passed, 19 deselected in 0.02s
config/allowlist.json domains = ['archive.ics.uci.edu', 'archive-api.open-meteo.com', 'open-meteo.com', 'date.nager.at', 'github.com', 'raw.githubusercontent.com', 'ec.europa.eu', 'www.dati.lombardia.it']; wildcard entries: []; justification per added host: outputs/artifacts/decisions.md, section G6
```

## TC-017
```
{"error": "DOMAIN_NOT_ALLOWLISTED", "message": "DOMAIN_NOT_ALLOWLISTED: host 'catalog.data.gov' is not on config/allowlist.json. Do not try another route to it; record the source as unreachable and say which host would need approval."}
Gate: accept (reason on file); catalog.data.gov in allowlist: False; pipeline requests to catalog.data.gov in outputs/UC1/trace.jsonl: 1 (error: None); recorded as a finding in review_UC1.md
```

## TC-018
```
# TC-018 gate decision checks (2026-11-15T20:24Z)

$ python -m pytest tests/test_agent_loop.py -k links -q
.                                                                        [100%]
1 passed, 6 deselected in 0.15s

## (a) no gate_decisions.json
$ python -m discovery_agent run --use-case UC1 --from-stage profile --stop-after profile --links-file outputs/UC1/links.json --no-input
Discovery run UC1 | model=claude-haiku-5-5 | stages profile..profile | out=/home/utk_tiger/stack_ai_rewire/work_3/outputs/UC1
[profile]
  totals: {'llm_calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'cache_read_input_tokens': 0, 'tool_calls': 0, 'tool_errors': 0, 'http_requests': 0, 'http_refused': 0}
Missing /home/utk_tiger/stack_ai_rewire/work_3/outputs/UC1/gate_decisions.json. Record accept or reject, with a reason, for each dataset link before profiling. Format and rules: README section 9, template links/_TEMPLATE_gate_decisions.json.
run_summary.json totals: {'llm_calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'cache_read_input_tokens': 0, 'tool_calls': 0, 'tool_errors': 0, 'http_requests': 0, 'http_refused': 0}

## (b) gate file covering only the UCI link (throwaway fixture, deleted after)
$ python -m discovery_agent run --use-case UC1 --from-stage profile --stop-after profile --links-file outputs/UC1/links.json --no-input
Discovery run UC1 | model=claude-haiku-5-5 | stages profile..profile | out=/home/utk_tiger/stack_ai_rewire/work_3/outputs/UC1
[profile]
  totals: {'llm_calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'cache_read_input_tokens': 0, 'tool_calls': 0, 'tool_errors': 0, 'http_requests': 0, 'http_refused': 0}
No decision for https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sdg_11_52?format=JSON&lang=EN&geo=IT in /home/utk_tiger/stack_ai_rewire/work_3/outputs/UC1/gate_decisions.json. Add accept or reject with a reason.
run_summary.json totals: {'llm_calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'cache_read_input_tokens': 0, 'tool_calls': 0, 'tool_errors': 0, 'http_requests': 0, 'http_refused': 0}

## (c) gate file covering all three links, one reason under 20 chars (throwaway fixture, deleted after)
$ python -m discovery_agent run --use-case UC1 --from-stage profile --stop-after profile --links-file outputs/UC1/links.json --no-input
Discovery run UC1 | model=claude-haiku-5-5 | stages profile..profile | out=/home/utk_tiger/stack_ai_rewire/work_3/outputs/UC1
[profile]
  totals: {'llm_calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'cache_read_input_tokens': 0, 'tool_calls': 0, 'tool_errors': 0, 'http_requests': 0, 'http_refused': 0}
Reason for https://archive.ics.uci.edu/dataset/360/air+quality is too short: give at least 20 characters, in your own words.
run_summary.json totals: {'llm_calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'cache_read_input_tokens': 0, 'tool_calls': 0, 'tool_errors': 0, 'http_requests': 0, 'http_refused': 0}

Fixture gate file removed: yes
```

## TC-019
```
outputs/artifacts/decisions.md 'Source suggestions': S1-S5, each with exact URL, need ids/windows, decision and reason; coverage as stated by the page and citations in outputs/artifacts/step2b_search/verification.md and 01-05_search.txt (all from scripts/web_search.py, gemini-3.8-flash, with citations). S3 revised and accepted -> https://www.dati.lombardia.it/Ambiente/Temperatura-fino-al-2010/6eu4-4tja, inspected with inspect_dataset_link and profiled (outputs/UC1/records/link.lombardia_6eu4_4tja_097de4.json). Gate file: outputs/UC1/gate_decisions.json covers all 4 links.
```

## TC-020
```
before (pytest_before.txt): 20 failed, 32 passed in 0.51s
after (pytest_after.txt): 52 passed in 0.18s
now: 52 passed in 0.16s
tests/test_learner_gaps.py vs provided copy: identical
```

## TC-021
```
check UC1: problems=[], traced=link.uci_360.temporal.end; check UC2: problems=[], traced=internal.sales.products.schema.notes
```

## TC-022
```
outputs/UC1/records/link.europa_sdg_11_52_099aa6.json: licence.name=None, commercial_use='unknown'; unknowns[0]='Licence name, reuse terms and attribution for Eurostat SDG 11.52 data were not found.'; provenance entries=6
```

## TC-023
```
$ pytest tests/test_tools_offline.py -k vendor -q -> 1 passed, 23 deselected in 0.05s
HTTP requests to api.atmosdata.example in outputs/UC1/trace.jsonl: 0; vendor status recorded in outputs/UC1/candidates.json rejected_without_profiling (agreement expired); login walls followed: none (no link resolved to a login page; no credentials anywhere in config or code)
```

## TC-024
```
check UC1/UC2 email findings: none; token value found in tracked files (git grep on HEAD): 0 files; .env is git-ignored
```

## TC-025
```
config/settings.json vs starter copy: identical; outputs/<ID>/ files are produced by pipeline runs (run_history.jsonl) or written from templates (gate_decisions.json, signoff.json); no record or result was hand-edited
```

