# Step 0 checks (UC2)

Date: 2026-11-16. Environment: fresh `.venv` (Python 3.12.7), `pip install -r requirements.txt`.

## Gateway variables (set / not set; values not shown)
ANTHROPIC_BASE_URL: set · ANTHROPIC_AUTH_TOKEN: set · ANTHROPIC_MODEL: set · WEB_SEARCH_MODEL: set

Model in use: `claude-haiku-5-5` (ANTHROPIC_MODEL). Web search model: `gemini-3.8-flash` (WEB_SEARCH_MODEL).

## Offline tests (`python -m pytest tests/ -q`): 52 passed, 0 failed
| File | Result |
|---|---|
| tests/test_agent_loop.py | 7 passed |
| tests/test_tools_offline.py | 24 passed |
| tests/test_learner_gaps.py | 21 passed (G1, G3, G4, G5, G6 tests all pass; the gaps are already implemented in this copy) |

## Tool smoke tests (no LLM)
- `search_internal_catalog {"query": "daily ice-cream sales by product"}` → JSON, 4 hits (sales.daily_by_product, wiki till_migration_2024, sales.products, wiki product_codes_2024).
- `inspect_dataset_link {"url": "https://archive.ics.uci.edu/dataset/360/air+quality"}` → JSON, link_type `uci_dataset_page`, source_id `link.uci_360`.
- `list_external_register {}` → JSON, 3 UC2 entries: policy.open_data_links, api.open_meteo_archive, api.nager_public_holidays.

## Noted
- `scripts/web_search.py` does not exist yet (needed at Step 2b; the learner generates it, Assignment Task 3).
