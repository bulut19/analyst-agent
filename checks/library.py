"""The data quality check library: deterministic SQL checks, no LLM.

Each check returns a list of findings:
  {check, table, column, rule, rows_affected, key_column, keys (up to MAX_KEYS), sample_keys}

Business rules (keys, required columns, date order) come from data/data_dictionary.json ("_rules").
Joins come from "_joins". Outlier and spelling checks need no rules at all.

Run all checks on a dataset:  python -m checks.library thelook_dirty
"""
import json
import re
import sys
from difflib import SequenceMatcher

from google.cloud import bigquery

from agent.config import ACTIVE_DATASET, MAX_BYTES_BILLED, PROJECT, ROOT
from agent.schema import load_profile

DICTIONARY = json.loads((ROOT / "data" / "data_dictionary.json").read_text())
RULES = DICTIONARY["_rules"]
PK = RULES["primary_keys"]
MAX_KEYS = 1000             # row keys kept per finding (enough to score the evaluation)
OUTLIER_FACTOR = 10         # flag values above 10x the 99th percentile
SPELLING_MAX_DISTINCT = 300  # only compare spellings in columns with this many values or fewer

_bq = None


def bq():
    global _bq
    _bq = _bq or bigquery.Client(project=PROJECT)
    return _bq


def run(sql):
    return list(bq().query(sql, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES_BILLED)).result())


def finding(check, table, column, rule, key_column, keys, rows_affected=None, sql=""):
    keys = list(keys)
    return {"check": check, "table": table, "column": column, "rule": rule,
            "rows_affected": rows_affected if rows_affected is not None else len(keys),
            "key_column": key_column, "keys": keys[:MAX_KEYS], "sample_keys": keys[:10], "sql": " ".join(sql.split())}


def flagged(ds, table, where, check, column, rule):
    """Run a WHERE condition and return a finding listing the primary keys of matching rows (or None)."""
    pk = PK[table]
    sql = f"SELECT {pk} k FROM `{ds}.{table}` WHERE {where} ORDER BY {pk} LIMIT {MAX_KEYS}"
    count = run(f"SELECT COUNT(*) n FROM `{ds}.{table}` WHERE {where}")[0].n
    if not count:
        return None
    return finding(check, table, column, rule, pk, [r.k for r in run(sql)], count, sql)


# --- checks -----------------------------------------------------------------

def duplicate_keys(ds, tables):
    out = []
    for t in tables:
        pk = PK[t]
        sql = f"SELECT {pk} k, COUNT(*) n FROM `{ds}.{t}` GROUP BY 1 HAVING n > 1 ORDER BY 1"
        rows = run(sql)
        if rows:
            out.append(finding("duplicate_key", t, pk, f"{pk} must be unique", pk,
                               [r.k for r in rows], sum(r.n - 1 for r in rows), sql))
    return out


def duplicate_values(ds, tables):
    out = []
    for tc in RULES["unique_columns"]:
        t, c = tc.split(".")
        if t not in tables:
            continue
        pk = PK[t]
        where = f"{c} IN (SELECT {c} FROM `{ds}.{t}` GROUP BY 1 HAVING COUNT(*) > 1)"
        f = flagged(ds, t, where, "duplicate_value", c, f"{c} should be unique per row")
        if f:
            f["distinct_duplicated_values"] = run(
                f"SELECT COUNT(*) n FROM (SELECT {c} FROM `{ds}.{t}` GROUP BY 1 HAVING COUNT(*) > 1)")[0].n
            out.append(f)
    return out


def missing_required(ds, tables):
    out = []
    for tc in RULES["required_columns"]:
        t, c = tc.split(".")
        if t in tables:
            f = flagged(ds, t, f"{c} IS NULL", "missing_required", c, f"{c} must not be empty")
            if f:
                out.append(f)
    return out


def non_positive(ds, tables):
    out = []
    for tc in RULES["positive_columns"]:
        t, c = tc.split(".")
        if t in tables:
            f = flagged(ds, t, f"{c} <= 0", "non_positive", c, f"{c} must be greater than 0")
            if f:
                out.append(f)
    return out


def orphan_keys(ds, tables):
    out = []
    for j in DICTIONARY["_joins"]:
        (t1, c1), (t2, c2) = [s.strip().split(".") for s in j.split("=")]
        if t1 not in tables or t2 not in tables:
            continue
        where = f"{c1} IS NOT NULL AND {c1} NOT IN (SELECT {c2} FROM `{ds}.{t2}` WHERE {c2} IS NOT NULL)"
        f = flagged(ds, t1, where, "orphan_key", c1, f"every {t1}.{c1} must exist in {t2}.{c2}")
        if f:
            out.append(f)
    return out


def date_order(ds, tables):
    out = []
    for t, pairs in RULES["date_order"].items():
        if t not in tables:
            continue
        for early, late in pairs:
            f = flagged(ds, t, f"{late} < {early}", "date_order", f"{early}, {late}", f"{late} must not be before {early}")
            if f:
                out.append(f)
    return out


def future_dates(ds, tables):
    out = []
    profile = load_profile()
    for t in tables:
        for c, info in profile[t]["columns"].items():
            if info["type"] == "TIMESTAMP":
                f = flagged(ds, t, f"{c} > CURRENT_TIMESTAMP()", "future_date", c, f"{c} must not be in the future")
                if f:
                    out.append(f)
    return out


def outliers(ds, tables):
    out = []
    profile = load_profile()
    for t in tables:
        for c, info in profile[t]["columns"].items():
            if info["type"] not in ("INT64", "FLOAT64") or c == "id" or c.endswith("_id"):
                continue
            p99 = run(f"SELECT APPROX_QUANTILES({c}, 100)[OFFSET(99)] p FROM `{ds}.{t}`")[0].p
            if p99 and p99 > 0:
                limit = OUTLIER_FACTOR * p99
                f = flagged(ds, t, f"{c} > {limit}", "outlier", c,
                            f"{c} more than {OUTLIER_FACTOR}x its 99th percentile ({p99:g}), i.e. above {limit:g}")
                if f:
                    out.append(f)
    return out


def _norm(v: str) -> str:
    v = v.strip().lower().replace("&", "and")
    v = re.sub(r"[^a-z0-9]+", " ", v).strip()
    return re.sub(r"s\b", "", v)  # crude singular: "sweaters" -> "sweater"


def inconsistent_spelling(ds, tables):
    """Rare values that are near-copies of a common value: case, spacing, '&' vs 'and', plurals, typos."""
    out = []
    profile = load_profile()
    for t in tables:
        for c, info in profile[t]["columns"].items():
            if info["type"] != "STRING":
                continue
            counts = {r.v: r.n for r in run(
                f"SELECT {c} v, COUNT(*) n FROM `{ds}.{t}` WHERE {c} IS NOT NULL GROUP BY 1")}
            if len(counts) > SPELLING_MAX_DISTINCT:
                continue
            variants = {}
            values = sorted(counts, key=counts.get, reverse=True)
            for i, common in enumerate(values):
                for rare in values[i + 1:]:
                    if counts[rare] > 0.05 * counts[common] or rare in variants:
                        continue  # only rare variants of a much more common value
                    a, b = _norm(common), _norm(rare)
                    if a == b or (min(len(a), len(b)) >= 5 and SequenceMatcher(None, a, b).ratio() >= 0.85):
                        variants[rare] = common
            if variants:
                in_list = ", ".join("'" + v.replace("'", "\\'") + "'" for v in variants)
                f = flagged(ds, t, f"{c} IN ({in_list})", "inconsistent_spelling", c,
                            "rare spellings of a common value: " +
                            "; ".join(f"{v!r} looks like {w!r}" for v, w in variants.items()))
                if f:
                    f["variants"] = variants
                    out.append(f)
    return out


CHECKS = [duplicate_keys, duplicate_values, missing_required, non_positive, orphan_keys,
          date_order, future_dates, outliers, inconsistent_spelling]


def run_all(dataset=ACTIVE_DATASET, tables=None):
    """Run every check on the given tables (default: all four). Returns a list of findings."""
    tables = tables or list(PK)
    ds = dataset if "." in dataset else f"{PROJECT}.{dataset}"
    results = []
    for check in CHECKS:
        results += check(ds, tables)
    return results


if __name__ == "__main__":
    ds = sys.argv[1] if len(sys.argv) > 1 else ACTIVE_DATASET
    for f in run_all(ds):
        print(f"{f['check']:<22} {f['table']}.{f['column']:<28} {f['rows_affected']:>7,} rows  {f['rule'][:80]}")
