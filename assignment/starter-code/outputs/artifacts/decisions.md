# Decisions log

## Source suggestions (Step 2b)
One row per suggestion you accepted, rejected or revised, with your reason. Use the page's own wording for the reason.

| Suggestion (publisher, URL) | Need, window | Decision | Reason |
|---|---|---|---|
| | | | |

Inspected through the workflow (at least one accepted extra source):

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
