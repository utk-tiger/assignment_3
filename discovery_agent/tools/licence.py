"""Licence and structured-metadata extraction from dataset landing pages."""
from __future__ import annotations

import json
import re


def jsonld_datasets(html: str) -> list[dict]:
    """Return every schema.org Dataset object embedded as JSON-LD in a page.

    Many portals (Kaggle, Zenodo, data.gov, Hugging Face, Dataverse, CKAN sites) embed one.
    It is the most reliable machine-readable description of a dataset when it exists.
    """
    found = []
    for m in re.finditer(r"""(?is)<script[^>]*type=["']application/ld\+json["'][^>]*>(.*?)</script>""", html):
        try:
            data = json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data]) if isinstance(data, dict) else []
        for item in items:
            if isinstance(item, dict) and "Dataset" in str(item.get("@type", "")):
                found.append(item)
    return found


def summarise_jsonld_dataset(d: dict) -> dict:
    """Keep the fields that matter for discovery, clipped for the model."""
    def name_of(v):
        if isinstance(v, list):
            return [name_of(x) for x in v][:5]
        if isinstance(v, dict):
            return v.get("name") or v.get("url") or v.get("@id")
        return v

    def clip(v, n=600):
        v = re.sub(r"<[^>]+>", " ", str(v)) if v is not None else None
        return None if v is None else (" ".join(v.split())[:n])

    dist = d.get("distribution") or []
    dist = dist if isinstance(dist, list) else [dist]
    return {
        "name": d.get("name"), "description": clip(d.get("description")),
        "license": d.get("license"), "creator": name_of(d.get("creator")), "publisher": name_of(d.get("publisher")),
        "datePublished": d.get("datePublished"), "dateModified": d.get("dateModified"),
        "temporalCoverage": d.get("temporalCoverage"), "spatialCoverage": name_of(d.get("spatialCoverage")),
        "isAccessibleForFree": d.get("isAccessibleForFree"), "keywords": clip(d.get("keywords"), 300),
        "variableMeasured": name_of(d.get("variableMeasured")),
        "distribution": [{k: x.get(k) for k in ("contentUrl", "encodingFormat", "fileFormat", "contentSize", "requiresSubscription", "name")
                          if isinstance(x, dict) and x.get(k) is not None} for x in dist[:10]],
    }


# ---------------------------------------------------------------------------
# LEARNER TODO (G1): find the licence of ANY dataset from its landing page
# ---------------------------------------------------------------------------
# Without this, every dataset link ends up LIC-UNKNOWN (a blocker) and verdicts are wrong.
#
# Contract (tests/test_learner_gaps.py::test_g1_* checks it):
#   extract_licence(html: str, jsonld: list[dict] | None = None) -> dict with EXACTLY these keys
#     licence_name : normalised name, one of e.g. "CC BY 4.0", "CC BY-SA 4.0", "CC BY-NC 4.0", "CC BY-NC-SA 4.0",
#                    "CC BY-ND 4.0", "CC0 1.0", "ODbL 1.0", "OGL v3.0", "MIT", "Apache-2.0"; None if not found
#                    or if the page says the licence is unknown/unspecified
#     licence_url  : the licence URL you found, or None
#     snippet      : the text or JSON-LD value you read it from (<= 400 chars), or None
#     found_in     : "json-ld" | "link" | "text" | None
#
# Order of evidence: JSON-LD "license" (string URL, or {"name", "url"}) first; then links to
# creativecommons.org / opendatacommons.org / nationalarchives.gov.uk (OGL) / choosealicense.com;
# then sentences such as "licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license".
# jsonld defaults to jsonld_datasets(html) when None. Never guess: return None values when unsure.
SNIPPET_MAX = 400

# Values a publisher uses to say "there is no licence we can tell you about". They are evidence
# (the page was read and says so), but they are not a licence name.
UNKNOWN_LICENCE_RE = re.compile(
    r"^\s*(unknown|unspecified|not specified|none|n/?a|no licen[cs]e)\s*\.?\s*$", re.I)
# "Other (specified in description)" and "see ..." are not decisive: they point to the page text, so the
# link and sentence searches still run, and the JSON-LD value is kept only as a fallback.

# Hosts whose links are licence evidence (a link elsewhere is only a link).
LICENCE_LINK_RE = re.compile(
    r"(creativecommons\.org/(licenses|publicdomain)/|opendatacommons\.org/licenses/|"
    r"nationalarchives\.gov\.uk/doc/open-government-licence|choosealicense\.com/licenses/|"
    r"spdx\.org/licenses/|opensource\.org/licenses?/)", re.I)

# Sentences that state a licence in prose.
LICENCE_SENTENCE_RE = re.compile(
    r"[^.<>]*\b(licen[cs]ed under|released under|available under|distributed under|made available under|"
    r"licen[cs]e\s*:|terms of the)\b[^.<>]*(\.\d[^.<>]*)*", re.I)

_CC_MODS = {"nc": "NC", "sa": "SA", "nd": "ND"}
_CC_LONG = [("noncommercial", "NC"), ("non-commercial", "NC"), ("sharealike", "SA"), ("share-alike", "SA"),
            ("noderivatives", "ND"), ("noderivs", "ND"), ("no-derivatives", "ND")]


def _version(v: str | None, default: str | None = None) -> str | None:
    if not v:
        return default
    return v if "." in v else f"{v}.0"


def _cc(mods: list[str], version: str | None) -> str | None:
    if version is None:
        return None  # a CC licence without a version is not specific enough to name
    order = [m for m in ("NC", "SA", "ND") if m in mods]
    return "CC BY" + "".join(f"-{m}" for m in order) + f" {version}"


def normalise_licence(value: str | None) -> str | None:
    """Map a licence URL, SPDX id or name to a short canonical name. None when not recognised.

    Never guesses: a value that does not clearly name one licence (and version, for CC) returns None.
    """
    if not value or not isinstance(value, str):
        return None
    v = " ".join(value.split())
    low = v.lower()

    # --- URLs --------------------------------------------------------------
    m = re.search(r"creativecommons\.org/licenses/(by(?:-(?:nc|sa|nd))*)/(\d(?:\.\d)?)", low)
    if m:
        return _cc([_CC_MODS[p] for p in m.group(1).split("-")[1:]], _version(m.group(2)))
    m = re.search(r"creativecommons\.org/publicdomain/zero/(\d(?:\.\d)?)", low)
    if m:
        return f"CC0 {_version(m.group(1))}"
    m = re.search(r"opendatacommons\.org/licenses/(odbl|by|pddl)(?:/(\d(?:\.\d)?))?", low)
    if m:
        name = {"odbl": "ODbL", "by": "ODC-By", "pddl": "PDDL"}[m.group(1)]
        return f"{name} {_version(m.group(2), '1.0')}"
    m = re.search(r"nationalarchives\.gov\.uk/doc/open-government-licence/version/(\d)", low)
    if m:
        return f"OGL v{_version(m.group(1))}"
    m = re.search(r"(?:choosealicense\.com/licenses|spdx\.org/licenses|opensource\.org/licenses?)/([a-z0-9.\-]+)", low)
    if m:
        return normalise_licence(m.group(1).strip("/").removesuffix(".html"))

    # --- SPDX-style ids (cc-by-4.0, cc0-1.0, odbl-1.0, mit, apache-2.0) ----
    m = re.fullmatch(r"cc-(by(?:-(?:nc|sa|nd))*)-(\d(?:\.\d)?)", low)
    if m:
        return _cc([_CC_MODS[p] for p in m.group(1).split("-")[1:]], _version(m.group(2)))
    m = re.fullmatch(r"cc0(?:-(\d(?:\.\d)?))?", low)
    if m:
        return f"CC0 {_version(m.group(1), '1.0')}"
    if re.fullmatch(r"odbl(-1\.0)?", low):
        return "ODbL 1.0"
    if low == "mit":
        return "MIT"
    if re.fullmatch(r"apache-2\.0", low):
        return "Apache-2.0"

    # --- Short names inside text: "CC BY-NC-SA 4.0", "CC-BY 4.0", "CC0 1.0" ---
    m = re.search(r"\bcc[\s-]?(by(?:[\s-](?:nc|sa|nd))*)[\s-]?(\d(?:\.\d)?)\b", low)
    if m:
        return _cc([_CC_MODS[p] for p in re.split(r"[\s-]", m.group(1))[1:]], _version(m.group(2)))
    m = re.search(r"\bcc[\s-]?0(?:[\s-]+(\d\.\d))?\b|\bcc[\s-]?zero\b", low)
    if m:
        return f"CC0 {_version(m.groups()[0] if m.groups() else None, '1.0')}"

    # --- Long names: "Creative Commons Attribution-NonCommercial 4.0 International" ---
    m = re.search(r"creative\s+commons\s+attribution([\w\s\-]*?)(\d(?:\.\d)?)", low)
    if m:
        mods = [code for word, code in _CC_LONG if word in m.group(1)]
        return _cc(mods, _version(m.group(2)))
    if re.search(r"creative\s+commons\s+(zero|cc0)|public\s+domain\s+dedication", low):
        m = re.search(r"(\d\.\d)", low)
        return f"CC0 {m.group(1) if m else '1.0'}"
    m = re.search(r"open\s+government\s+licen[cs]e(?:\s+(?:for\s+public\s+sector\s+information\s+)?v(?:ersion)?\.?\s*(\d(?:\.\d)?))?", low)
    if m and m.group(1):
        return f"OGL v{_version(m.group(1))}"
    if re.search(r"open\s+data(base)?\s+licen[cs]e|\bodbl\b", low):
        return "ODbL 1.0"
    if re.search(r"\bmit\s+licen[cs]e\b", low):
        return "MIT"
    if re.search(r"apache\s+licen[cs]e,?\s*(version\s*)?2(\.0)?", low):
        return "Apache-2.0"
    return None


def _clip(text: str | None) -> str | None:
    if text is None:
        return None
    text = " ".join(str(text).split())
    return text[:SNIPPET_MAX] if text else None


def _strip_tags(fragment: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", fragment).split())


def _result(name, url, snippet, found_in) -> dict:
    return {"licence_name": name, "licence_url": url or None, "snippet": _clip(snippet), "found_in": found_in}


def _from_jsonld(jsonld: list[dict]) -> tuple[dict | None, dict | None]:
    """Returns (decisive_result, fallback_result). Decisive: a recognised licence or an explicit 'unknown'."""
    fallback = None
    for d in jsonld:
        lic = d.get("license", d.get("licence"))
        for item in (lic if isinstance(lic, list) else [lic]):
            if item in (None, "", {}):
                continue
            if isinstance(item, dict):
                name, url = item.get("name"), item.get("url") or item.get("@id")
            else:
                name, url = (None, item) if str(item).lower().startswith("http") else (item, None)
            snippet = json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else str(item)
            canonical = normalise_licence(name) or normalise_licence(url)
            if canonical:
                return _result(canonical, url if url and str(url).startswith("http") else None, snippet, "json-ld"), None
            if (name and UNKNOWN_LICENCE_RE.match(str(name))) or (not name and not url):
                # The publisher states the licence is unknown: record what we read, never a name.
                return _result(None, url if url and str(url).startswith("http") else None, snippet, "json-ld"), None
            fallback = fallback or _result(None, url if url and str(url).startswith("http") else None, snippet, "json-ld")
    return None, fallback


def _from_links(html: str) -> dict | None:
    best = None
    for m in re.finditer(r"""(?is)<a\b[^>]*href=["']([^"']+)["'][^>]*>(.*?)</a>""", html):
        href, text = m.group(1), _strip_tags(m.group(2))
        if not LICENCE_LINK_RE.search(href):
            continue
        name = normalise_licence(href) or normalise_licence(text)
        if not name:
            continue
        # Context: the enclosing paragraph-ish text around the link, so the snippet shows the sentence.
        start = max(html.rfind("<p", 0, m.start()), html.rfind("<div", 0, m.start()), m.start() - 600)
        end_p = html.find("</p>", m.end())
        context = _strip_tags(html[start:end_p if 0 < end_p < m.end() + 600 else m.end() + 200])
        hit = _result(name, href, context or text, "link")
        if re.search(r"licen[cs]", context, re.I):
            return hit  # a licence link stated as the dataset's licence wins
        best = best or hit
    return best


def _from_text(html: str) -> dict | None:
    text = _strip_tags(re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html))
    for m in LICENCE_SENTENCE_RE.finditer(text):
        sentence = m.group(0)
        name = normalise_licence(sentence)
        if name:
            url = re.search(r"https?://\S+", sentence)
            return _result(name, url.group(0).rstrip(").,") if url else None, sentence, "text")
    return None


def extract_licence(html: str, jsonld: list[dict] | None = None) -> dict:
    """Licence of a dataset from its landing page. Evidence order: JSON-LD, licence links, licence sentences.

    An explicit "Unknown" in JSON-LD is decisive (licence_name None, found_in "json-ld"): the publisher has
    said it does not know, so a site-wide footer link must not be read as the dataset's licence.
    """
    html = html or ""
    if jsonld is None:
        jsonld = jsonld_datasets(html)
    decisive, fallback = _from_jsonld(jsonld or [])
    if decisive:
        return decisive
    for finder in (_from_links, _from_text):
        hit = finder(html)
        if hit:
            return hit
    return fallback or _result(None, None, None, None)
