# Step 0: tooling checks (UC1)

Date: 2026-11-16. Run by the `/data-discovery-agent` skill, Step 0. No LLM calls were made by these checks.

## Environment
- Python 3.12.7, virtual environment `.venv/`, `pip install -r requirements.txt` (anthropic 1.17.0, jsonschema 4.26.0, pytest 9.2.0).
- Gateway variables (values not shown): `ANTHROPIC_BASE_URL` set, `ANTHROPIC_AUTH_TOKEN` set, `ANTHROPIC_MODEL` set. Loaded from the project-local, git-ignored `.env`.
- Model in use for the agents: `claude-haiku-5-5` (the only Claude model listed by the gateway's `/v1/models` for this key; others listed: DeepSeek-V4-Flash, gemini-3.5-flash-lite, gemini-3.8-flash, gpt-5.4-nano, text-embedding-3-large).

## Offline tests (`python -m pytest <file> -q`)
| File | Result |
|---|---|
| tests/test_tools_offline.py | 24 passed |
| tests/test_agent_loop.py | 7 passed |
| tests/test_learner_gaps.py | 20 failed, 1 passed (expected: G1 ×9, G3 ×2, G4 ×7, G5 ×1, G6 `ec.europa.eu` ×1 fail; `test_g6_allowlist_not_wildcarded` passes) |

Full suite: 52 collected, 32 passed, 20 failed (saved in `outputs/artifacts/pytest_before.txt`).

## Tool smoke tests (no LLM)
- `search_internal_catalog {"query": "hourly vehicle traffic near monitoring stations"}` → JSON; top hit `internal.traffic.hourly_counts` (score 9.55), then `internal.airq.station_readings` and wiki page `station_network`.
- `inspect_dataset_link {"url": "https://archive.ics.uci.edu/dataset/360/air+quality"}` → JSON; `link_type=uci_dataset_page`, `source_id=link.uci_360`, page_status 200, files `.../360/air+quality.zip` and `.../360/data.csv`; licence fields null with note "extract_licence is a learner TODO (G1)". First attempt failed with a transient DNS error (`Temporary failure in name resolution`); the retry succeeded.
- `list_external_register {}` → JSON; sources include `policy.open_data_links`, `api.open_meteo_archive` (default_query latitude 38.72, longitude -9.14, i.e. Lisbon, not the client's region: to be decided and logged in decisions.md), Nager.Date, and the vendor feed.
