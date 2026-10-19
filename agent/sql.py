"""Stage 5: SQL writing and validation.

For each metric: the model writes a query; Python checks it is read-only and only touches our tables,
dry runs it (cost check), runs it with a byte cap, and runs the model's own sanity checks on the result.
Any failure goes back to the model with the error message, up to MAX_RETRIES times.
"""
import json
import re

from google.cloud import bigquery

from agent import llm
from agent.config import ACTIVE_DATASET, MAX_BYTES_BILLED, PROJECT, prompt
from agent.schema import TABLES, schema_text

MAX_RETRIES = 2
MAX_ROWS = 5000

TOOLS = [{"name": "submit_sql", "description": "Submit the query for this metric.",
          "input_schema": {"type": "object", "properties": {
              "sql": {"type": "string"},
              "output_columns": {"type": "array", "items": {"type": "string"}},
              "sanity_checks": {"type": "array", "items": {"type": "object", "properties": {
                  "column": {"type": "string"}, "min": {"type": "number"}, "max": {"type": "number"},
                  "blank_allowed_because": {"type": "string", "description":
                      "Only if blanks are a correct result for some rows, the business reason (e.g. 'unsold "
                      "products have no sales margin'). Leave empty otherwise."}},
                  "required": ["column", "min", "max"]}},
              "notes": {"type": "string", "description": "Anything a reviewer should know about the query"},
          }, "required": ["sql", "output_columns", "sanity_checks", "notes"]}}]

FORBIDDEN = re.compile(r"\b(INSERT|UPDATE|DELETE|MERGE|CREATE|DROP|ALTER|TRUNCATE|GRANT|REVOKE|EXPORT|CALL|EXECUTE)\b", re.I)
TABLE_REF = re.compile(r"`([^`]+)`")

_bq = None


def bq():
    global _bq
    _bq = _bq or bigquery.Client(project=PROJECT)
    return _bq


def check_safety(sql: str, dataset: str) -> str:
    """Return an error message, or '' if the query is a read-only query on allowed tables."""
    body = re.sub(r"--[^\n]*|/\*.*?\*/", " ", sql, flags=re.S).strip()
    if not re.match(r"^(SELECT|WITH)\b", body, re.I):
        return "The query must start with SELECT or WITH."
    if ";" in body.rstrip(";"):
        return "Only one statement is allowed."
    if FORBIDDEN.search(body):
        return f"Forbidden keyword: {FORBIDDEN.search(body).group(0)}. Only SELECT queries are allowed."
    allowed = {f"{dataset}.{t}" for t in TABLES}
    bad = [t for t in TABLE_REF.findall(body) if "." in t and t not in allowed]
    if bad:
        return f"Unknown tables {bad}. Use only: {sorted(allowed)}"
    return ""


def check_results(df, spec) -> str:
    """Deterministic checks on the result table. Returns an error message or ''."""
    if df.empty:
        return ("The query returned no rows. Check the date window, filters and joins. If you have checked and "
                "zero rows is the true answer (for example, no product meets every condition), rewrite the query "
                "to return one summary row that reports the count as 0, so the reader sees the result.")
    missing = [c for c in spec["output_columns"] if c not in df.columns]
    if missing:
        return f"Expected columns missing from the result: {missing}. Got {list(df.columns)}."
    problems = []
    for chk in spec["sanity_checks"]:
        col = chk["column"]
        if col not in df.columns:
            continue
        values = df[col].dropna()
        if values.empty:
            if chk.get("blank_allowed_because"):
                continue  # blanks were expected and explained; the explanation is kept with the query
            problems.append(f"{col} is empty in every row. If that is correct (for example the rows have no sales, "
                            "so a ratio has nothing to divide by), apply the metric definition's rule for that "
                            "case, or set blank_allowed_because for this column with the business reason")
        elif values.min() < chk["min"] or values.max() > chk["max"]:
            problems.append(f"{col} ranges {values.min():g} to {values.max():g}, outside {chk['min']:g} to {chk['max']:g}")
    return "; ".join(problems)


def write_and_run(metric: dict, plan: dict, dataset: str = ACTIVE_DATASET) -> dict:
    """Write, validate and run the SQL for one metric. Returns a result record (with a DataFrame)."""
    tables = ", ".join(f"`{dataset}.{t}`" for t in TABLES)
    system = prompt("system") + "\n\n" + prompt("sql").format(tables=tables, schema=schema_text())
    user = (f"Metric definition:\n{json.dumps(metric, indent=1)}\n\n"
            f"Time window: {json.dumps(plan['time_window'])}\n"
            f"Rules for every metric: {json.dumps(plan['shared_rules'])}")
    messages = [{"role": "user", "content": user}]
    attempts = []

    for attempt in range(MAX_RETRIES + 1):
        response, _, spec, tool_id = llm.call_tool(system, messages, TOOLS, max_tokens=16000)
        sql = spec["sql"].strip().rstrip(";")
        error, df, mb = check_safety(sql, dataset), None, None
        if not error:
            try:
                dry = bq().query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
                mb = dry.total_bytes_processed / 1e6
                job = bq().query(sql, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES_BILLED))
                df = job.result(max_results=MAX_ROWS).to_dataframe()
                error = check_results(df, spec)
            except Exception as e:  # BigQuery errors go back to the model
                error = f"BigQuery error: {str(e)[:1500]}"
        attempts.append({"sql": sql, "error": error})
        if not error:
            return {"metric": metric["name"], "sql": sql, "spec": spec, "df": df, "mb_scanned": mb,
                    "attempts": attempts, "ok": True}
        messages += [{"role": "assistant", "content": response.content},
                     {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id, "is_error": True,
                      "content": f"The query failed validation: {error}\nFix it and submit again."}]}]

    return {"metric": metric["name"], "sql": attempts[-1]["sql"], "spec": spec, "df": None, "mb_scanned": None,
            "attempts": attempts, "ok": False}
