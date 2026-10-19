"""Schema context for the agent: column list, a profile of each column, and business descriptions.

The profile is built once from the clean copy (python -m agent.schema) and cached in
data/schema_profile.json, so every run sees the same context without re-scanning tables.
Business descriptions live in data/data_dictionary.json (written by hand: that is analyst knowledge).
"""
import json

from google.cloud import bigquery

from agent.config import CLEAN_DATASET, MAX_BYTES_BILLED, ROOT

TABLES = ["orders", "order_items", "products", "users"]
PROFILE_PATH = ROOT / "data" / "schema_profile.json"
DICTIONARY_PATH = ROOT / "data" / "data_dictionary.json"
MAX_LISTED_VALUES = 30  # list every value for string columns with this many distinct values or fewer


def _run(bq, sql):
    return list(bq.query(sql, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES_BILLED)).result())


def build_profile(dataset=CLEAN_DATASET) -> dict:
    """Profile every column: type, null %, distinct count, and values or a min/max range."""
    bq = bigquery.Client()
    project, ds = dataset.split(".")
    cols = _run(bq, f"""
        SELECT table_name, column_name, data_type
        FROM `{project}.{ds}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name IN UNNEST({TABLES}) ORDER BY table_name, ordinal_position""")

    profile = {}
    for table in TABLES:
        table_cols = [c for c in cols if c.table_name == table]
        rows = _run(bq, f"SELECT COUNT(*) n FROM `{dataset}.{table}`")[0].n
        profile[table] = {"rows": rows, "columns": {}}
        for c in table_cols:
            name, dtype = c.column_name, c.data_type
            stats = _run(bq, f"""
                SELECT COUNTIF({name} IS NULL) / COUNT(*) AS null_share,
                       COUNT(DISTINCT {name}) AS distinct_values,
                       CAST(MIN({name}) AS STRING) AS min_value,
                       CAST(MAX({name}) AS STRING) AS max_value
                FROM `{dataset}.{table}`""")[0]
            info = {"type": dtype, "null_pct": round(100 * stats.null_share, 1),
                    "distinct": stats.distinct_values}
            if dtype == "STRING" and stats.distinct_values <= MAX_LISTED_VALUES:
                info["values"] = [r.v for r in _run(bq, f"""
                    SELECT {name} v, COUNT(*) n FROM `{dataset}.{table}`
                    WHERE {name} IS NOT NULL GROUP BY 1 ORDER BY 2 DESC""")]
            elif dtype != "STRING":
                info["range"] = [stats.min_value, stats.max_value]
            profile[table]["columns"][name] = info
        print(f"Profiled {table}: {len(table_cols)} columns")

    PROFILE_PATH.write_text(json.dumps(profile, indent=2))
    return profile


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text())


def column_set() -> set:
    """All valid 'table.column' names, for checking the agent's output."""
    return {f"{t}.{c}" for t, info in load_profile().items() for c in info["columns"]}


def schema_text() -> str:
    """The schema as compact text for prompts: tables, columns, descriptions, profiles."""
    profile = load_profile()
    dictionary = json.loads(DICTIONARY_PATH.read_text())
    lines = []
    for table, info in profile.items():
        d = dictionary.get(table, {})
        lines.append(f"\n## {table} ({info['rows']:,} rows): {d.get('description', '')}")
        for col, c in info["columns"].items():
            desc = d.get("columns", {}).get(col, "")
            detail = f"values: {', '.join(map(str, c['values']))}" if "values" in c else \
                f"range: {c['range'][0]} to {c['range'][1]}" if "range" in c else f"{c['distinct']:,} distinct"
            nulls = f", {c['null_pct']}% null" if c["null_pct"] else ""
            lines.append(f"- {col} ({c['type']}{nulls}): {desc} [{detail}]")
    joins = dictionary.get("_joins", [])
    if joins:
        lines.append("\n## Join keys\n" + "\n".join(f"- {j}" for j in joins))
    return "\n".join(lines).strip()


if __name__ == "__main__":
    build_profile()
    print(schema_text())
