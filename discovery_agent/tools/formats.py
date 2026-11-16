"""Summarisers for self-describing metadata formats the supplementary URLs use.

The tool wrappers (fetch + call) are provided. The pure functions that do the
summarising are LEARNER TODOs (G3). The data-package summary is not graded in this version. They are pure so you can test them offline
against tests/fixtures/ without network or LLM.
"""
from __future__ import annotations

from .base import NotImplementedTool, ToolContext, tool

LARGE_RESOURCE_BYTES = 100_000_000


# ---------------------------------------------------------------------------
# Not graded in this version (former G2). Left as a stub: no graded link uses a data package.
# ---------------------------------------------------------------------------
# Spec: https://specs.frictionlessdata.io/data-package/
# Return a dict with EXACTLY these keys (tests/test_learner_gaps.py checks them):
#   title, version, profile          : str | None, copied from the package
#   declared_licences                : the package's "licenses" list, or None if absent/empty
#   temporal                         : {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"} from package["temporal"], or None
#   resources                        : [{"name", "path", "format", "bytes", "field_count"}] one per resource
#   total_bytes                      : sum of resource bytes (missing bytes count as 0)
#   largest_resource_bytes           : max resource bytes
#   matching_fields                  : fields whose name starts with any prefix in field_filter (all resources,
#                                      de-duplicated by name, max 60): [{"resource", "name", "unit", "source"}]
#                                      where "source" is field["source"]["name"] if present. [] if field_filter is None.
#   upstream_sources                 : sorted distinct field["source"]["name"] values across ALL fields
#   warnings                         : list containing (when they apply)
#                                        "NO_PACKAGE_LICENCE"         no package-level licence declared
#                                        "LARGE_RESOURCE"             any resource > LARGE_RESOURCE_BYTES
#                                        "MULTIPLE_UPSTREAM_SOURCES"  more than one upstream source
def datapackage_summary(package: dict, field_filter: list[str] | None = None) -> dict:
    raise NotImplementedTool("datapackage_summary is not implemented in this version (former G2).")


# ---------------------------------------------------------------------------
# LEARNER TODO (G3): JSON-stat 2.0 dataset -> summary
# ---------------------------------------------------------------------------
# Spec: https://json-stat.org/full/   (Eurostat's dissemination API returns this format)
# Return a dict with EXACTLY these keys:
#   label, updated, source           : copied from the dataset
#   dimensions                       : [{"id", "size", "labels"}] in the order of dataset["id"];
#                                      labels = first 10 "code: label" strings for that dimension
#   time                             : {"first", "last", "values"} for the "time" dimension (codes, sorted), or None
#   geo_codes                        : list of codes in the "geo" dimension, in index order ([] if no geo dimension)
#   expected_cells                   : product of dataset["size"]
#   value_count                      : number of non-null values (dataset["value"] can be a dict OR a list)
#   missing_cells                    : expected_cells - value_count
#   status_counts                    : {status_code: count} from dataset.get("status") (dict or list), {} if absent
#   warnings                         : list containing (when they apply)
#                                        "MISSING_CELLS"       missing_cells > 0
#                                        "NON_ISO_GEO_CODES"   any geo code that is not ISO 3166-1 alpha-2,
#                                                              including Eurostat's "UK" (ISO: GB) and "EL" (ISO: GR)
#                                                              and aggregates such as "EU27_2020"
# Hint: dimension categories look like
#   dataset["dimension"]["geo"]["category"] = {"index": {"UK": 0, "FR": 1}, "label": {"UK": "United Kingdom", ...}}
#   "index" can also be a list of codes.
# ISO 3166-1 alpha-2 country codes (officially assigned). Eurostat's "UK" and "EL", aggregates such as
# "EU27_2020"/"EA20", and user-assigned codes such as "XK" are deliberately absent, so they raise
# NON_ISO_GEO_CODES: they will not join to an ISO-keyed table without a mapping.
ISO_3166_ALPHA2 = frozenset("""
AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ
CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR
GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO
JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR
MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO
RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV
TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW
""".split())


def _category_codes(dim: dict) -> list[str]:
    """Codes of one dimension in index order. "index" may be a list of codes or a {code: position} dict;
    a dimension with a single category may give only "label"."""
    cat = (dim or {}).get("category") or {}
    index = cat.get("index")
    if isinstance(index, list):
        return [str(c) for c in index]
    if isinstance(index, dict):
        return [str(c) for c, _ in sorted(index.items(), key=lambda kv: kv[1])]
    return [str(c) for c in (cat.get("label") or {})]


def _role_dimension(dataset: dict, role: str) -> str | None:
    """The dimension id playing a role ("time", "geo"): from dataset["role"] when given, else by id."""
    ids = dataset.get("role", {}).get(role) if isinstance(dataset.get("role"), dict) else None
    if ids:
        return ids[0]
    return role if role in (dataset.get("dimension") or {}) else None


def jsonstat_summary(dataset: dict) -> dict:
    ids = list(dataset.get("id") or [])
    sizes = list(dataset.get("size") or [])
    dims = dataset.get("dimension") or {}

    dimensions = []
    for pos, dim_id in enumerate(ids):
        dim = dims.get(dim_id) or {}
        codes = _category_codes(dim)
        labels = (dim.get("category") or {}).get("label") or {}
        dimensions.append({
            "id": dim_id,
            "size": sizes[pos] if pos < len(sizes) else len(codes),
            "labels": [f"{c}: {labels.get(c, c)}" for c in codes[:10]],
        })

    time_id = _role_dimension(dataset, "time")
    time_codes = sorted(_category_codes(dims.get(time_id))) if time_id else []
    time = {"first": time_codes[0], "last": time_codes[-1], "values": time_codes} if time_codes else None

    geo_id = _role_dimension(dataset, "geo")
    geo_codes = _category_codes(dims.get(geo_id)) if geo_id else []

    expected = 1
    for s in sizes:
        expected *= int(s)
    if not sizes:
        expected = 0

    # value: dense list (null = missing) or sparse {flat_index: value} dict (absent or null = missing).
    # A missing cell is never read as zero.
    values = dataset.get("value")
    if isinstance(values, dict):
        value_count = sum(1 for v in values.values() if v is not None)
    elif isinstance(values, list):
        value_count = sum(1 for v in values if v is not None)
    else:
        value_count = 0

    # status: {flat_index: code}, a list aligned with value, or one string that applies to every cell.
    status = dataset.get("status")
    status_counts: dict[str, int] = {}
    if isinstance(status, dict):
        flags = list(status.values())
    elif isinstance(status, list):
        flags = status
    elif isinstance(status, str) and status:
        flags = [status] * expected
    else:
        flags = []
    for flag in flags:
        if flag not in (None, ""):
            status_counts[str(flag)] = status_counts.get(str(flag), 0) + 1

    missing = max(expected - value_count, 0)
    warnings = []
    if missing > 0:
        warnings.append("MISSING_CELLS")
    if any(c not in ISO_3166_ALPHA2 for c in geo_codes):
        warnings.append("NON_ISO_GEO_CODES")
    # Extra (beyond the contract's two codes): a year absent from the time dimension is not a missing
    # cell (the category simply does not exist), so MISSING_CELLS cannot see it. Eurostat's sdg_11_52
    # omits 2006 this way. Flag gaps in a run of plain year codes.
    years = [int(c) for c in time_codes if c.isdigit() and len(c) == 4]
    if len(years) == len(time_codes) and len(years) > 1 and years[-1] - years[0] + 1 > len(set(years)):
        warnings.append("TIME_GAPS")

    return {
        "label": dataset.get("label"),
        "updated": dataset.get("updated"),
        "source": dataset.get("source"),
        "dimensions": dimensions,
        "time": time,
        "geo_codes": geo_codes,
        "expected_cells": expected,
        "value_count": value_count,
        "missing_cells": missing,
        "status_counts": status_counts,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# Tool wrappers (provided)
# ---------------------------------------------------------------------------
@tool("summarize_datapackage",
      "Summarise a Frictionless Data Package descriptor (datapackage.json): licence declarations, temporal coverage, "
      "resource sizes, matching fields and their upstream sources. Reads only the descriptor, never the data files.",
      {"url": {"type": "string"},
       "field_filter": {"type": "array", "items": {"type": "string"},
                        "description": "Field-name prefixes to list, e.g. ['AB_', 'CD_load']"}},
      ["url"])
def summarize_datapackage(ctx: ToolContext, args: dict) -> dict:
    package, res = ctx.http.get_json(args["url"], max_bytes=5_000_000, agent=ctx.agent)
    return {"url": args["url"], "last_modified_header": res.headers.get("last-modified"),
            **datapackage_summary(package, args.get("field_filter"))}


@tool("summarize_jsonstat",
      "Summarise a JSON-stat 2.0 dataset (for example from the Eurostat dissemination API): dimensions, time coverage, "
      "geo codes, missing cells and status flags.",
      {"url": {"type": "string"}}, ["url"])
def summarize_jsonstat(ctx: ToolContext, args: dict) -> dict:
    dataset, _ = ctx.http.get_json(args["url"], max_bytes=5_000_000, agent=ctx.agent)
    return {"url": args["url"], **jsonstat_summary(dataset)}
