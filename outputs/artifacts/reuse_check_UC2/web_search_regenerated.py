"""Web search through the gateway's chat-completions endpoint (Step 2b).

Usage: python scripts/web_search.py "<query>"

Prints the model's answer text, then the citation URLs found in the response.
Results are leads from a search model, not verified sources.
Standard library only. Never prints the token or the request.
"""
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = "gemini-3.8-flash"
TIMEOUT_S = 120


def _require(name):
    value = os.environ.get(name)
    if not value:
        sys.exit(f"Missing environment variable: {name}")
    return value


def _citations(data):
    """Collect citation URLs from the shapes OpenAI-compatible gateways use."""
    urls = []

    def add(u):
        if isinstance(u, str) and u.startswith("http") and u not in urls:
            urls.append(u)

    # Top-level list (Perplexity-style): ["https://...", ...] or [{"url": ...}]
    for c in data.get("citations") or []:
        add(c.get("url") if isinstance(c, dict) else c)
    for c in data.get("search_results") or []:
        if isinstance(c, dict):
            add(c.get("url"))
    # Message annotations (OpenAI web_search_options style)
    for choice in data.get("choices") or []:
        msg = choice.get("message") or {}
        for a in msg.get("annotations") or []:
            if not isinstance(a, dict):
                continue
            uc = a.get("url_citation")
            add(uc.get("url") if isinstance(uc, dict) else a.get("url"))
        for c in msg.get("citations") or []:
            add(c.get("url") if isinstance(c, dict) else c)
    return urls


def main(argv):
    if len(argv) != 2 or not argv[1].strip():
        sys.exit('Usage: python scripts/web_search.py "<query>"')
    query = argv[1]

    base_url = _require("ANTHROPIC_BASE_URL").rstrip("/")
    token = _require("ANTHROPIC_AUTH_TOKEN")
    model = os.environ.get("WEB_SEARCH_MODEL") or DEFAULT_MODEL

    body = {
        "model": model,
        "messages": [{"role": "user", "content": query}],
        "web_search_options": {},
    }
    req = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500].replace(token, "***")
        sys.exit(f"HTTP {e.code} from gateway: {detail}")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach gateway: {e.reason}")
    except json.JSONDecodeError:
        sys.exit("Gateway returned a non-JSON response.")

    choices = data.get("choices") or []
    answer = ((choices[0].get("message") or {}).get("content") if choices else None) or ""
    print(f"model: {model}")
    print("=== answer ===")
    print(answer.strip() or "(no answer text)")
    print("=== citations ===")
    urls = _citations(data)
    if not urls:
        print("(no citation URLs in the response)")
        return 2
    for u in urls:
        print(u)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
