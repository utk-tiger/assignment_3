# data-discovery-agent

## Overview
A reusable skill for the first stage of any AI/DS project: locate, catalog and assess the feasibility of data sources before any pipeline is built. It drives the multi-agent system in `discovery_agent/` for any use case written to the use-case contract (`use_cases/_TEMPLATE_use_case.json`).

## Files in This Skill
- SKILL.md: the assignment runner, Steps 0–5 (0–2b provided; 3–5 profile and rule-check, assess and draft the memo, evaluate and hand off, added from the UC1/UC2 runs).

## How Learners Should Use This
Invoke `/data-discovery-agent` in Claude Code (or paste SKILL.md) and name the use case and steps, for example "Run Steps 0–2b for UC1" or "Run Steps 3–5 for UC1". Claude checks the tooling, frames or validates the use case, runs plan and scout, suggests sources for unmet needs and stops at the candidate gate. After the human's gate decisions it profiles and rule-checks the sources, runs the Risk Assessor and Memo Writer, and evaluates the run, stopping at the human review gate for the sign-off.

## Evidence to Submit
Put `outputs/artifacts/step0_checks.md`, `outputs/<ID>/` (plan, candidates, records, results, memo, trace, transcripts, run summary), `outputs/artifacts/decisions.md` and your updated SKILL.md in your submission.

## Notes for Evaluators
Check that the extended steps reflect what the learner actually did, and that they are use-case agnostic. A good test is to hand the updated skill a third use case and see whether a fresh session can follow it.
