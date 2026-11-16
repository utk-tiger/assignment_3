"""Step 2b web search through the Tiger AI Gateway (OpenAI-compatible chat completions).

Usage:
    python scripts/web_search.py "<query>"

Environment:
    ANTHROPIC_BASE_URL    gateway base URL (no /v1 suffix; this script adds /v1/chat/completions)
    ANTHROPIC_AUTH_TOKEN  gateway key, sent as a Bearer token (never printed)
    WEB_SEARCH_MODEL      optional, defaults to gemini-3.8-flash

Prints the answer text, then the citation URLs. A result is a lead, not a verified source:
check every URL on its publisher's page before suggesting it.
Standard library only.
"""
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = "gemini-3.8-flash"
TIMEOUT_S = 120


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"Missing environment variable: {name}")
    return value


def collect_citations(response: dict) -> list[dict]:
    """Gather citations from the shapes OpenAI-compatible gateways use, de-duplicated by URL in order.

    Each item: {"url", "title", "claims"}. With Gemini via the gateway, "url" is a Vertex grounding
    redirect and "title" is the cited site's domain; "claims" are the answer spans it supports.
    """
    by_url: dict[str, dict] = {}

    def add(url, title=None, claim=None):
        if not (isinstance(url, str) and url.startswith(("http://", "https://"))):
            return
        item = by_url.setdefault(url, {"url": url, "title": title, "claims": []})
        if claim and claim not in item["claims"]:
            item["claims"].append(claim)

    for c in response.get("citations") or []:  # top-level list of URLs or objects
        add(c) if isinstance(c, str) else add((c or {}).get("url"), (c or {}).get("title"))
    for choice in response.get("choices") or []:
        message = choice.get("message") or {}
        content = message.get("content") or ""
        for ann in message.get("annotations") or []:  # OpenAI-style url_citation annotations
            cit = (ann or {}).get("url_citation") or ann or {}
            start, end = cit.get("start_index"), cit.get("end_index")
            claim = " ".join(content[start:end].split()) if isinstance(start, int) and isinstance(end, int) else None
            add(cit.get("url"), cit.get("title"), claim)
        for c in message.get("citations") or []:
            add(c) if isinstance(c, str) else add((c or {}).get("url"), (c or {}).get("title"))
    return list(by_url.values())


def main() -> None:
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        sys.exit('Usage: python scripts/web_search.py "<query>"')
    query = sys.argv[1].strip()

    base_url = require_env("ANTHROPIC_BASE_URL").rstrip("/")
    token = require_env("ANTHROPIC_AUTH_TOKEN")
    model = os.environ.get("WEB_SEARCH_MODEL", "").strip() or DEFAULT_MODEL

    body = {
        "model": model,
        "messages": [{"role": "user", "content": query}],
        "web_search_options": {},
    }
    request = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as resp:
            response = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        sys.exit(f"Gateway returned HTTP {exc.code} for model {model}: {detail}")
    except urllib.error.URLError as exc:
        sys.exit(f"Could not reach the gateway: {exc.reason}")

    choices = response.get("choices") or []
    answer = ((choices[0].get("message") or {}).get("content") if choices else None) or ""
    print(f"Model: {response.get('model', model)}")
    print(f"Query: {query}\n")
    print(answer.strip() or "(no answer text returned)")

    citations = collect_citations(response)
    print("\nCitations:")
    if citations:
        for i, c in enumerate(citations, 1):
            print(f"  [{i}] {c['title'] or '(no title)'}: {c['url']}")
            for claim in c["claims"][:3]:
                print(f"       supports: {claim[:200]}")
    else:
        print("  (none returned: treat this answer as unverified and do not suggest from it)")


if __name__ == "__main__":
    main()
