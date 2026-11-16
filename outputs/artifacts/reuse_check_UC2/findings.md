# Reuse check (UC2): findings

*From `session_transcript.md` and the fresh session's files in this folder (2026-11-16); summarised in the README "Submission notes".*

**Result.** A fresh Claude Code session, given only the skill and the README in a clean copy of the repo, completed Steps 0–2b for UC2 and stopped at each STOP:
- needs table;
- dataset-link question;
- missing search script;
- suggestion decisions.

Facts from the run:
- The session ran plan and scout (`run_summary_fresh_session.json`) and reached the same internal and register candidates and the same N2 gap as the main run ("no mapping table exists").
- It regenerated `scripts/web_search.py` from the README prompt (`web_search_regenerated.py`). It ran five searches, kept only cited leads, and made five suggestions.
- All five were rejected, so the result is "none accepted" (`decisions_fresh_session.md`). No profiling, no gate file and no new hosts were needed.
- Session cost: 32 turns over 4 prompts, about $1.37 cumulative.

**Steps that could not be followed as written, and what was missing**
1. **Step 0.3** said `tests/test_learner_gaps.py` is "expected to fail". In a finished repo all 52 tests pass, so the session flagged the step as contradicted. *Changed:* it now says the suite fails until the gaps are closed and passes in full after.
2. **Step 0.2** assumed the gateway variables are exported. The session found them only because the prompt pointed to `./.env`. *Changed:* it now says to load an untracked `.env` inside each command.
3. **Step 0.4** hard-coded the UCI 360 link (a UC1 dataset) as the smoke test. *Changed:* any link from `outputs/<ID>/links.json` or a page on an allowlisted host.
4. **Step 2b, missing input:** `scripts/web_search.py` was not present (by design). The skill correctly stopped and refused to write it unasked. The learner had to paste the README prompt as the request, and the session then generated it.
5. **Step 2b.1–2:**
   - Gemini citations come back as Google grounding redirect URLs, not publisher pages.
   - The session could not read most publisher pages. WebFetch was not permitted, and it treated the pipeline allowlist as applying to its own checks.
   - Three of the five suggestions ended up "not read".
   *Changed:* resolve redirects from the `Location` header, and read publisher metadata with one small GET of the page or its catalogue API (never a data file). The allowlist governs the pipeline agents, not this check.
6. **Location assumption:** the register's weather `default_query` had coordinates, but the skill had no step to check them against the use case's geography. The fresh session asked for the location to be recorded before Step 3. *Changed:* Step 1 now checks register defaults against the geography and records any permitted change in `decisions.md`.
7. **Step 2.4 and 2b.5** named UC1's prescribed links and the Chicago and Eurostat hosts. *Changed:* both are now generic (prescribed links from `links/<ID>_example_links.json`; distractor and G6 hosts described generically, with UC1 as the example).

**Inputs a data scientist would replace for a new project.** All are listed in the skill's "Reusing this skill on a new use case" section:
- `use_cases/<ID>_*.json` and the brief;
- `internal/<ID>_<client>/catalog_export.json` and `wiki/`;
- the register entries in `config/external_sources_register.json`;
- the exact allowlist hosts for the new links (G6);
- the dataset links, with their gate decisions;
- the weather API's latitude and longitude (the only permitted config change).

**Values found hard-coded for UC1 or UC2, and what changed**
- In the skill: the UCI 360 smoke-test URL, the UC1 prescribed-link wording, and the Chicago and Eurostat host notes. All made generic (above).
- In config: the register's Open-Meteo `default_query` defaulted to Lisbon (38.72, -9.14) with 2014 dates and hourly UTC variables. Latitude and longitude were changed to Verona (45.44, 10.99) and logged; the other fields may not be changed. Nager.Date has no default country (its notes mention PT), so `IT` has to come from the probe arguments.
- In the code: none found that changed results. The G1/G3/G4 code reads thresholds from `config/settings.json` and use-case windows and needs from the contract, not from fixtures.
