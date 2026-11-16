# Decisions log

## Source suggestions (Step 2b)
One row per suggestion you accepted, rejected or revised, with your reason. Use the page's own wording for the reason.

**UC2 (2026-11-16): none accepted.** All five suggestions were rejected. `outputs/UC2/links.json` stays `[]`, no hosts were added, and no gate file or profiling of links is needed.

Who decided: the learner. The reasons below are recorded word for word as the learner gave them.

| # | Suggestion (publisher, URL) | Need, window | Decision | Reason (verbatim, as given by the learner) |
|---|---|---|---|---|
| 1 | Comune di Bologna, https://opendata.comune.bologna.it/explore/dataset/eventi-bologna-agenda-cultura/ | N5; history, recent | reject | the shop location assumption is Verona (Veneto), not Bologna, and the page could not be read here, so its coverage and licence are unverified. |
| 2 | ARPA – Regione Lombardia (Open Data Lombardia), https://www.dati.lombardia.it/Ambiente/Dati-sensori-meteo/647i-nhxk | N3; history, recent | reject | the page itself says it holds only the current month ("nel mese in corso"), so it covers neither window; Lombardy is also not the assumed location, and Open-Meteo already serves N3. |
| 3 | ARPA Veneto, https://www.arpa.veneto.it/dati-ambientali/dati-storici/meteo-idro-nivo/ultimi_anni | N3; history, recent | reject | right region for a Verona assumption, but when I opened the publisher page on 2026-11-16 it timed out and its host is not allowlisted, so period, licence and access are unverified; Open-Meteo already serves N3. Revisit if the client confirms Verona. |
| 4 | OpenHolidays project, https://www.openholidaysapi.org/en/sources-europe/ | N4; history, recent | reject | the page could not be read; it is described as a school-holiday source, which is not one of our needs, and Italian patron-day coverage is unverified. |
| 5 | GitHub user MatteoHenryChinaski (community repo), https://github.com/MatteoHenryChinaski/Comuni-Italiani-2018-Sql-Json-excel | N4; history, recent | reject | an unofficial 2018 snapshot with no licence stated, and its README warns that patron data may be missing or out of date. |

How the suggestions were found: `scripts/web_search.py` (model `gemini-3.8-flash`), five queries; one (Verona/Veneto events) returned no citations and was dropped. Citations came back as `vertexaisearch.cloud.google.com` grounding redirects; Claude Code read each redirect's `Location` header (no follow, no download) to get the publisher URL. WebFetch was not permitted in the session, so pages #1, #3 and #4 (hosts not allowlisted) were not read; #2 and #5 were read through `inspect_dataset_link` (allowlisted hosts). N2 (product-code mapping) had no external suggestion: it is the client's own mapping.

Inspected through the workflow (at least one accepted extra source): none accepted for UC2. #2 and #5 were inspected with `inspect_dataset_link` before the decision (link_type `landing_page`, CC0 1.0 from json-ld; and `data_file` for the README, no licence).

## G1 and G3: one edge case in each function
- **G1, `extract_licence`**: the edge case, what the code does with it, and how it changes the `licence` field:
- **G3, `jsonstat_summary`**: the edge case, what the code does with it, and how it changes the summary:

## G4–G5: feasible for one need or window, not another
- Source and the rule or calibration decision:
- Feasible for (need, window), and why:
- Not feasible for (need, window), and why:
- Reason for each red flag you dismissed:

## G6: Allowlist changes
Exact hosts only. For each host: what it provides and why a broader domain is not needed.

| Host added | Needed for (source, page) | Why nothing broader | Date |
|---|---|---|---|
| | | | |

Hosts you chose **not** to add, and why:

## G5: Verdict calibration
- What you changed in `prompts/risk_assessor.md`, and the reasoning behind each rule:
- Verdicts that changed after you re-ran `--from-stage assess` (source: before → after, why):

## G7: One agent failure, fixed at its cause
- **Symptom** (what was wrong in the output):
- **Evidence** (trace event or transcript excerpt, with file and line or turn):
- **Root cause** (prompt, tool description, validator, rule, or missing tool):
- **Fix** (file and diff summary):
- **Re-run** (command):
- **Before / after** (measured: e.g. candidates found, flags raised, verdict, tokens, tool calls):
- **Decision this failure could affect:**
- **Related source or test checked:**

## Other decisions
- **2026-11-16, UC2: `scripts/web_search.py` was a missing input.** It did not exist at Step 0. At the learner's request, Claude Code regenerated it from the README prompt ("Suggest sources (Step 2b)"): stdlib only (urllib, json, os, sys), one query argument, POST to `{ANTHROPIC_BASE_URL}/v1/chat/completions`, Bearer token from `ANTHROPIC_AUTH_TOKEN`, `model` from `WEB_SEARCH_MODEL` (default `gemini-3.8-flash`), `web_search_options: {}`. It prints the answer, then citation URLs; it exits with a message naming any missing variable, exits 2 when the response has no citations, and never prints the token or the request. Tested with one query (citations returned) and with the token unset ("Missing environment variable: ANTHROPIC_AUTH_TOKEN"). `python -m pytest tests/ -q`: 52 passed.
