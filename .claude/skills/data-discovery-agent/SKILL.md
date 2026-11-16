---
name: data-discovery-agent
description: >
  Reusable skill for Stack AI Rewire, Assignment: AI-Native Data Discovery. Runs the first
  stage of any AI/DS project: locate, catalog and assess the feasibility of internal and
  external data sources for a business problem, before any pipeline is built. Works for
  any use case written to the use-case contract (use_cases/<ID>_*.json + brief + internal
  estate). It sets up and checks the agent, frames the use case, runs planning and scouting,
  suggests external sources for unmet needs (Step 2b), stops at the candidate gate, then
  profiles and rule-checks every accepted source (Step 3), assesses and drafts the feasibility
  memo (Step 4), and evaluates and hands off at the human review gate (Step 5). The human
  decides at every gate; Claude never writes a gate, suggestion or sign-off reason for them.
---

# AI-Native Data Discovery: Assignment Runner (Steps 0–5)

You are Claude, running the first steps of **Stack AI Rewire, Assignment: AI-Native Data
Discovery** in Claude Code, against the learner's copy of this repo. The repo
contains a multi-agent discovery system (`discovery_agent/`): Planner → Scout (internal catalog,
wiki, external register) → **candidate gate, where the human adds dataset links (any URL)** →
Profiler (one per source) → deterministic rules → Risk Assessor → Memo Writer, then a human review gate.

This skill gets a use case ready, checks the tooling, runs **plan + scout**, suggests external
sources for the needs that remain unmet (Step 2b), then profiles the accepted sources, runs the
deterministic rules and the Risk Assessor, drafts the memo, and evaluates the run for hand-off
(Steps 3–5). It assumes the tools and rules are complete (gaps G1–G7 closed); Step 3.1 checks that.

The skill is **use-case agnostic**. UC1 (air quality and traffic) and UC2 (ice-cream sales, weather and holidays) ship with
the repo, but any business problem written to the contract below runs the same way.

## Required input
- `use_cases/<ID>_<slug>.json`: the machine-readable use case (windows, needs, grains, geography).
  Contract: `use_cases/_TEMPLATE_use_case.json`.
- `use_cases/<ID>_<slug>.md`: the business brief: problem, decisions supported, scope, out of scope.
- `internal/<ID>_<client>/catalog_export.json` + `internal/<ID>_<client>/wiki/*.md`: the client's
  internal catalog export and documentation (metadata only, never data values).
- `config/external_sources_register.json`: the external sources the client has agreements for or
  has approved, tagged with the use case id.
- **Dataset links** (any https URL): supplied by the human at the candidate gate, from their own
  search or accepted from the Step 2b suggestions. For UC1 and UC2, README.md section 4 lists links
  whose expected assessment is known.
- **The learner's search script** `scripts/web_search.py` for Step 2b. It is not provided: the learner
  generates it with Claude Code (Assignment Task 3; the prompt is in README.md, section 4, "Suggest
  sources (Step 2b)"). Claude Code's built-in `WebSearch` does not work with the gateway key, so do not
  use it. If the script is missing, fails, or returns no citations, stop at Step 2b and tell the learner
  to generate or fix it. Do not write suggestions without search results.
- `config/allowlist.json`, `config/red_flags.json`, `config/settings.json`: provided. Do not loosen
  the allowlist or the caps to make a run pass.
- Gateway credentials in the environment: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`,
  `ANTHROPIC_MODEL`. Never print, log or commit the token.

## Repo scaffold this skill produces
```
.
├── use_cases/<ID>_*.json, <ID>_*.md         <- provided, or written by you in Step 1 (new use case)
├── internal/<ID>_<client>/                  <- provided, or assembled in Step 1 (new use case)
├── outputs/<ID>/
│   ├── use_case_validation.txt              <- Step 1
│   ├── search_plan.json                     <- Step 2 (Planner)
│   ├── candidates.json                      <- Step 2 (Scout)
│   ├── trace.jsonl, transcripts/            <- Step 2 (evidence of every LLM/tool/HTTP call)
│   ├── run_summary.json                     <- Step 2 (tokens, tool calls, warnings)
│   ├── links.json                           <- Step 2 (copy of the prescribed links) and Step 2b (accepted suggestions appended): the ONE links file
└── outputs/artifacts/step0_checks.md        <- Step 0
```
Steps 3–5 add, in `outputs/<ID>/`: `gate_decisions.json` (written by the human), `candidates_final.json`,
`records/<source_id>.json`, `rule_flags.json`, `risk_assessment.json`, `discovery_results.json`,
`feasibility_memo.md`, `run_history.jsonl`, `signoff.json` (written by the human); and in
`outputs/artifacts/`: `decisions.md`, `review_<ID>.md`, `check_<ID>.json`, `pytest_after.txt`.

---

## Step 0: Set up and check the tooling (no LLM calls)
1. If no environment is active: `python3 -m venv .venv && source .venv/bin/activate`, then
   `pip install -r requirements.txt`.
2. Check that the gateway variables are **set**, without printing their values:
   `python -c "import os;print({k: bool(os.environ.get(k)) for k in ['ANTHROPIC_BASE_URL','ANTHROPIC_AUTH_TOKEN','ANTHROPIC_MODEL']})"`.
   If any is `False`, check for an untracked `.env` in the repo root and load it inside each shell command
   (`set -a; . ./.env; set +a`), never printing it. If they are still missing, stop and tell the learner which one.
   Do not ask them to paste the token.
3. Run the offline tests: `python -m pytest tests/ -q`. `tests/test_tools_offline.py` and
   `tests/test_agent_loop.py` must pass. `tests/test_learner_gaps.py` fails until the learner has implemented
   G1, G3, G4, G5 and G6, and passes in full once they have (52 of 52 in a finished repo). Report which gap tests
   fail, if any; do not implement them here.
4. Smoke-test the tools without the LLM:
   - `python -m discovery_agent tool search_internal_catalog '{"query": "<a need from the brief>"}' --use-case <ID>`
   - `python -m discovery_agent tool inspect_dataset_link '{"url": "<a link from outputs/<ID>/links.json, or any page on an allowlisted host, e.g. https://archive.ics.uci.edu/dataset/360/air+quality>"}' --use-case <ID>`
   - `python -m discovery_agent tool list_external_register '{}' --use-case <ID>`
   Each must return JSON, not a traceback. A `DOMAIN_NOT_ALLOWLISTED` result is the guardrail
   working, not a bug.
5. Write `outputs/artifacts/step0_checks.md`: test results (pass/fail counts per file), the tool
   smoke results (one line each), and the model id in use. Never write the token.

## Step 1: Frame the use case against the contract
**Existing use case** (UC1 or UC2, where `use_cases/<ID>_*.json`
and `internal/<ID>_*/` already exist): check that the files exist, then do item 4 and item 5 below.
Do not rewrite a contract that someone else wrote. If item 4 fails, report the error and ask the
learner before you change any input.

**New use case** (the learner gives you a business problem): write the inputs, do not invent data.
1. Copy `use_cases/_TEMPLATE_use_case.json` to `use_cases/<ID>_<slug>.json` and fill every field:
   - `windows`: one per analysis period, with ISO dates and a purpose. Do not use a single
     open-ended window to dodge coverage checks.
   - `needs`: one row per data need, in business words, with `priority` (must/should/could),
     `min_grain` (one of `minute, 15min, 30min, hourly, daily, weekly, monthly, quarterly, annual,
     event, static`) and the `windows` it applies to. Aim for 5–12 needs. Split compound needs.
   - `as_of`: the date the discovery is valid for. It drives staleness checks.
2. Write `use_cases/<ID>_<slug>.md` with the same sections as the UC1 brief: business problem,
   decisions supported, scope, needs table, where to look, out of scope.
3. Internal estate: if the learner has a real catalog export, convert it to the
   `catalog_export.json` entry shape used in `internal/UC1_valdena_health/` (null where the catalog
   holds nothing, never a guess), and put the documentation pages in `wiki/` with the same front
   matter (`page_id`, `title`, `owner`, `last_edited`). Add the client's approved external sources
   to `config/external_sources_register.json` with the new use-case id and their real
   `agreement_status`. If the learner has no internal estate, stop and ask. Do not fabricate one.
4. Validate: `python -m discovery_agent validate-use-case <ID> | tee outputs/<ID>/use_case_validation.txt`.
   Fix every error it reports in the inputs, not in the validator.
   Then check the register's API defaults for this use case (`list_external_register`): if a `default_query`
   holds coordinates or a country that are not the use case's geography (for example a default city in another
   country), ask the learner for the location. Only `latitude`/`longitude` of the weather API's `default_query`
   may be changed; record the city, the reason and that it is an assumption in `outputs/artifacts/decisions.md`.
5. Show the learner the needs table (id, name, priority, min_grain, windows) and the windows.
   **Pause** (for a human learner in an interactive session; in a non-interactive run, write the table and stop). Wait for them to confirm or change it. The needs list decides what the agents
   search for and what the rules check, so a wrong need here gives wrong verdicts later.

## Step 2: Plan and scout, then stop at the candidate gate
1. Run: `python -m discovery_agent run --use-case <ID> --stop-after scout --no-input`.
   This runs the Planner (search plan per need, including hints on what external data to link) and
   the Scout (catalog, wiki and register search), and writes `search_plan.json`, `candidates.json`, `trace.jsonl` and `transcripts/`.
2. If the run fails, read the last events in `outputs/<ID>/trace.jsonl` and the failing agent's
   transcript before changing anything. Fix the cause (credentials, model id, a prompt, a tool
   bug) and re-run. Do not raise `max_turns` or the HTTP caps as a first response.
3. Review `candidates.json` against the needs, and give the learner a table:
   need id → candidate source ids → `unmet_needs`. Then name, from the trace:
   - needs with no candidate, or only one;
   - internal entries the Scout opened but did not read the wiki backlinks for;
   - internal searches that returned nothing and were not rephrased.
4. Show the learner the `unmet_needs` and the planner's `external_data_hints`. If a need is already met
   by internal or register sources, say so. Then ask: **do you already have dataset links that fill any
   of these needs?** If README.md section 4 or `links/<ID>_example_links.json` lists prescribed links for this
   use case, name them and ask whether the learner will use them. Each link needs need ids and windows. If the
   learner uses them, copy `links/<ID>_example_links.json` to `outputs/<ID>/links.json` once, only if that file
   does not exist yet; with no links, start from `[]`. Never copy over it: it may already hold accepted
   suggestions. A prescribed distractor (a link whose host must never be allowlisted) is one the learner accepts
   on purpose: its refusal is the finding. Claude does not make that decision for the learner. **STOP and wait for the reply.**
   Only then go to Step 2b.

## Step 2b: Suggest external sources (only for needs still unmet)
1. Only after the learner has answered Step 2, item 4. Check that `scripts/web_search.py` exists in the
   learner's repo. If it does not, **STOP**: ask the learner to generate it with Claude Code, using the
   prompt in README.md ("Suggest sources (Step 2b)"), and wait for it. Do not write the script yourself.
   Once it exists, search with it for up to **five** public datasets that could fill the unmet needs:
   `python scripts/web_search.py "<query>"`. Use the planner's `external_data_hints` as starting queries.
   Each result is a lead from a search model, not a verified source. Only a URL with a citation may be
   suggested, and each one still needs checking on its publisher's page. Gemini citations through the gateway
   are Google grounding redirect URLs: resolve each one to its publisher URL from the redirect's `Location`
   header (`curl -sI -m 30 <redirect>`, no body, nothing downloaded) and drop citations that land off-topic.
2. For each suggestion, show the learner: publisher, exact URL (the dataset or record page, not a search
   page), need ids, coverage **as the page states it** (quote the page; write `"not stated"` if the page
   does not say), and what still needs checking (licence, population, access). Do not download data.
   The allowlist governs the pipeline agents, not this check: read the publisher page's metadata yourself
   with one small GET of the HTML page or its catalogue API (`curl -sSL -m 40 <page>`; Socrata
   `/api/views/<id>.json`, Opendatasoft `/api/explore/v2.1/catalog/datasets/<id>`, CKAN `package_show`), never a
   data file. If the page cannot be read, write "not read (<reason>)" and ask the learner to open it.
3. **STOP and wait.** For each suggestion the learner decides `accept`, `reject` or `revise` (with new
   need ids or windows), with a short reason. The learner may also add links they found. Never decide,
   and never write a reason, for the learner. Silence is not acceptance.
4. Record every decision and reason in `outputs/artifacts/decisions.md` under "Source suggestions". Append each
   accepted suggestion to `outputs/<ID>/links.json` (the same file as Step 2), in the shape of
   `links/_TEMPLATE_links.json`, with the learner's reason as `note`. Never overwrite the prescribed links.
   The **learner** writes `outputs/<ID>/gate_decisions.json` (`{"decisions": [{"url", "decision": "accept" or
   "reject", "reason"}]}`), one entry for every link in `links.json`, after inspecting each link themselves.
   If the learner asks you to write it, transcribe only the reasons they have dictated, word for word, and
   say so in `decisions.md`. Never write a reason the learner did not give. The pipeline refuses to profile
   a link without one.
5. For each accepted link, check its host is on `config/allowlist.json`:
   `python -m discovery_agent tool inspect_dataset_link '{"url": "<link>"}' --use-case <ID>`.
   If a host is refused, **STOP**: the learner decides whether to add it, with a G6 justification in
   `outputs/artifacts/decisions.md`. Do not add hosts yourself, and do not try an alternate URL. A distractor's host is refused by design (in UC1, `catalog.data.gov`): record that refusal as a finding. A host the learner approves under G6 is added as an exact host only; re-run the inspection after it is added (in UC1, `ec.europa.eu` for Eurostat).

**Then stop at the candidate gate.** Tell the learner the candidate list and accepted links are ready, and
that `outputs/<ID>/gate_decisions.json` must exist (one `accept`/`reject` with a reason of at least 20 characters
per link in `outputs/<ID>/links.json`, written by the learner) before Step 3. If the use case has no dataset
links (`links.json` is `[]` or absent), no gate file is needed. Continue with Step 3 only after the learner says so.

---

## Step 3: Profile and rule-check
1. **Pre-flight (no LLM).** Run `python -m pytest tests/ -q`; every test must pass (tools G1/G3, rules G4,
   calibration G5, allowlist G6). If `tests/test_learner_gaps.py` fails, stop: profiling with a stubbed tool
   produces `NOT_IMPLEMENTED` records and wrong verdicts. Never edit that test file.
2. **Gate check (no LLM).** If `outputs/<ID>/links.json` holds links, confirm `outputs/<ID>/gate_decisions.json`
   exists and covers every URL exactly. The pipeline enforces it and stops with `Missing …`, `No decision for <url>`
   or `Reason … is too short` before any model call (`run_summary.json` then shows `llm_calls: 0`). Report the
   message; never write or shorten a reason for the learner.
3. **Host check (no LLM).** For every accepted link run
   `python -m discovery_agent tool inspect_dataset_link '{"url": "<link>"}' --use-case <ID>`. Record the
   `link_type` it detects (`uci_dataset_page`, `landing_page` with `jsonld_datasets`, `json_stat` with a `summary`,
   data package, raw file, archive, login wall). A `DOMAIN_NOT_ALLOWLISTED` result means the host needs a G6
   decision by the learner (exact host only, justified in `outputs/artifacts/decisions.md`) or is a deliberate
   refusal to keep. Never add a host yourself, never try another route, never retry a refused link more than twice.
   For a data file it lists, `sample_data_file '{"url": "<file>"}'` shows what the profiler will see in the
   first ≤2 MB; note when the sample cannot reach the target window (for example a file sorted by sensor).
4. **Run the profile stage only:**
   `python -m discovery_agent run --use-case <ID> --from-stage profile --stop-after profile --links-file outputs/<ID>/links.json --no-input`
   (omit `--links-file` when there are no links). Re-profile one source with `--only <source_id>`. Read the
   totals line: `http_refused` must equal the number of deliberately refused links, `tool_errors` should be 0 or
   explained.
5. **Check every `outputs/<ID>/records/<source_id>.json`** before assessing. For each record verify:
   - `provenance`: at least one entry per claim area, each naming a tool call, URL, catalog field or wiki page id.
   - `licence`: `name` plus `evidence`; for a link, the `found_in` of `inspect_dataset_link` (`json-ld`, `link`,
     `text`) or null. A JSON-stat or JSON API response carries no licence: the profiler must read the publisher's
     terms page on an allowed host, and the URL it cites must actually resolve (check the trace `http` line).
     Conflicting statements (a CC link plus "research purposes only" in the notes) must both be recorded.
     Unknown stays null and is listed in `unknowns`, never inferred.
   - `temporal.start/end/grain`: compared with the windows in `use_cases/<ID>_*.json`. An open end is
     "still updating"; a null start means the coverage rule will skip the source, so say where coverage comes from.
     A "last updated"/`Last-Modified` date is not a data date.
   - `declared_metadata` vs `documentation_excerpts` and `quality_notes`: sentinels (-200, 0, '?'), "no missing
     values" claims, unit or definition changes, code changes. Compare the sampler's sentinel counts with the
     values themselves; the sampler can miss a sentinel on a column.
   - `access` (`reachable`, `auth_required`, `classification`) and `spatial.coverage` against the use-case geography.
   - Probe arguments in the trace (`grep '"kind": "http"' outputs/<ID>/trace.jsonl`): API probes must use the
     register's `default_query` (for example the agreed coordinates) or the record must say why not.
6. **Read the rules.** Run `python -m discovery_agent run --use-case <ID> --from-stage assess --stop-after assess --no-input`
   or read `outputs/<ID>/rule_flags.json` after Step 4: `flags` per source with `raised_by: rule:<name>` and
   `warnings`. `warnings` must be empty (a non-empty list means a rule is skipped as not implemented). Check that
   the coverage rule fired as expected for each source and window (`COV-OUT-OF-WINDOW`, `COV-PARTIAL-WINDOW`,
   `FRS-STALE`, `COV-GRAIN-MISMATCH`, `DQ-METADATA-CONTRADICTION`) and note sources it skipped (static grain or
   null start).
7. **Fix the agent, not the record.** If a record is wrong (a missed wiki note, a sentinel read as data, a wrong
   probe location, a licence read from the wrong page), change the prompt, tool description, tool or validator,
   re-run `--from-stage profile --only <source_id>`, and keep the before file for the G7 evidence. Never hand-edit
   `records/`, `candidates.json` or results.

## Step 4: Assess and draft the memo
1. **Calibration in force.** Read the `## Verdict calibration` section of `discovery_agent/prompts/risk_assessor.md`.
   It maps flag severity (`config/red_flags.json`: blocker, major, minor) and the source's role (`must` = core,
   `should`/`could` = context) to a verdict, first matching rule wins: unresolvable blockers (refused host,
   expired agreement, no window overlap, consent gap, policy ban) → `not_feasible`; resolvable licence blockers
   (terms page or client-register approval; non-commercial terms only for a non-commercial prototype, or a
   commercial plan the publisher states exists) → `feasible_with_conditions` with Legal/Procurement as owner;
   per-window judgement; stale data allowed for a historical window; fixable quality issues → conditions; no join
   path → `not_feasible` **only when the documentation explicitly says no mapping exists** (an undocumented mapping
   is a condition); minor flags only → `feasible`.
2. **Run** `python -m discovery_agent run --use-case <ID> --from-stage assess --no-input` (rules + Risk Assessor +
   Memo Writer on the saved records).
3. **Review `outputs/<ID>/risk_assessment.json`** source by source:
   - every rule flag is kept or in `dismissed_rule_flags` with a reason naming the record field (only valid when
     the rule's input was wrong or not applicable, e.g. `FRS-STALE` for a source serving only a historical window);
     `ACC-UNREACHABLE`, `LIC-AGREEMENT-NOT-ACTIVE`, `GOV-CONSENT-GAP`, `GOV-PII` are never dismissed;
   - every `rationale` names the calibration rule that decided it, and every quoted "the documentation states …"
     is actually in the record or wiki (open the page);
   - every `feasible_with_conditions` has conditions with an owner; every `not_feasible` names its blocker;
   - `need_coverage`: each `must` need is `met`/`met_with_conditions` or explains why not; the overall verdict
     follows the rule in the prompt (any unmet must need → `not_feasible`).
4. **Measure calibration changes.** When you change the calibration, re-run `--from-stage assess` on the same
   records (use `--out <scratch dir>` with a copy of `search_plan.json`, `candidates*.json` and `records/` for a
   "before" run so `outputs/<ID>/` is not overwritten) and record source: before → after, and why, in
   `outputs/artifacts/decisions.md` (G5). Expect some run-to-run variation (for example a dismissal applied in one
   run and not the next); report it.
5. **Check the memo** `outputs/<ID>/feasibility_memo.md`: the seven required sections in order (see
   `discovery_agent/prompts/memo_writer.md`), the human review gate block at the end, provenance on every claim,
   no stale statements (for example an "unset location" that `decisions.md` has since fixed), blockers on sources
   not rejected listed under the gate block.
6. **STOP at the human review gate.** Show the learner: overall verdict, need coverage table, verdict per source,
   blockers, and the agent mistakes you found. The learner decides the sign-off.

## Step 5: Evaluate and hand off
1. **Trace checks** on `outputs/<ID>/trace.jsonl` (no LLM):
   - refusals: every `http` line with an error names the host; refused hosts = the deliberate ones only, each
     tried at most twice (`python -m discovery_agent check <ID>` reports `refused_hosts` and `unreachable_links`);
   - no call to a source with an expired agreement or a login wall (`grep` its host);
   - request count under `http.max_requests_per_run` in `config/settings.json` (never raise it);
   - model usage: `llm_calls`, input/output tokens per stage from `outputs/<ID>/run_history.jsonl`;
   - failed submits (`"kind": "submit", "ok": false`) and turns that hit `max_tokens`, as G7 leads.
2. **One agent failure, fixed at its cause (G7).** Pick a real mistake from a transcript (`outputs/<ID>/transcripts/<agent>.json`,
   message index) or trace line. Copy the "before" files to `outputs/artifacts/` first, fix the prompt, tool
   description, tool, rule or validator, run `python -m pytest tests/ -q`, re-run from the affected stage, and
   record in `decisions.md`: symptom, evidence (file + line/turn), root cause, fix (file + diff summary), re-run
   command, measured before/after (verdicts, need coverage, flags, turns, tokens), the project decision it could
   change, and one related source or test re-checked to show the fix does not over-correct.
3. **Human sign-off.** The learner writes `outputs/<ID>/signoff.json` from `outputs/artifacts/_TEMPLATE_signoff.json`
   (verdict `proceed`, `proceed_with_conditions` or `stop`; conditions with `text`, `owner`, `due`; at least one
   agreement or override with a reason; `traced_conclusion` = a `source_id` in `discovery_results.json`, a dotted
   field that exists in its record, and `could_change_if` ≥ 20 characters) and `outputs/artifacts/review_<ID>.md`
   (agreements, overrides with evidence, a verdict per dataset link, the gate decision, one traced conclusion).
   Help by preparing a fact sheet of memo claims against record fields and trace lines; never write their verdict
   or reasons unless they explicitly delegate it, and then say so in both files.
4. **Self-check until clean:** `python -m discovery_agent check <ID> > outputs/artifacts/check_<ID>.json`; it must
   list `"problems": []`. It checks completeness and consistency, not whether the verdicts are right.
5. **Evidence in `outputs/artifacts/`:** `step0_checks.md`, `decisions.md` (Step 2b suggestions, G1/G3 edge
   cases, G4–G5 feasibility case, G5 before/after, G6 hosts and non-hosts, G7, gate decisions, any permitted config
   change), `review_<ID>.md`, `check_<ID>.json`, `pytest_before.txt`, `pytest_after.txt`
   (`python -m pytest tests/ -q | tee outputs/artifacts/pytest_after.txt`), `walkthrough.md`. Keep `outputs/<ID>/`
   with traces and transcripts. Before hand-off, search the repo for the token value (it must appear nowhere but
   the untracked `.env`) and for email-like strings in outputs.
6. **Hand off.** Give the learner: the overall verdict per use case, the open conditions with owners, the agent
   failure fixed, and what remains a human decision.

---

## Rules that hold in every step
- **Metadata first, then a capped sample, never the whole dataset.** Read schemas, descriptions,
  coverage and terms; `sample_data_file` may read the first part of a file. Do not download whole
  datasets or copy personal data into any output.
- **Provenance on every claim.** Every statement about a source names a tool call, URL, catalog
  field or wiki page.
- **Unknown stays unknown.** Never infer a licence, owner, refresh cadence or consent. Use null and
  list it under unknowns.
- **Guardrails are not obstacles.** A refused host, an expired vendor agreement or a restricted
  table is a finding to record, not something to work around.
- **The agents are the product.** When an output is wrong, fix the agent (prompt, tool, rule,
  validator) and re-run. Never hand-edit `candidates.json`, records or results to look right.
- **A suggestion is not a verified source.** Selecting it grants no host access and no permission to
  use the data. Keep the exact-host allowlist.

---

## Reusing this skill on a new use case
Replace only the inputs: `use_cases/<ID>_*.json` and brief, `internal/<ID>_<client>/` (catalog export and wiki),
register entries in `config/external_sources_register.json` (with the new use-case id), the dataset links and
their gate decisions, exact allowlist hosts for those links (G6), and any permitted location defaults (only
latitude/longitude of the weather API's `default_query`, logged in `decisions.md`). Regenerate
`scripts/web_search.py` from the README prompt if it is missing. Steps 0–5 do not change.
