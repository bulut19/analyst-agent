"""Dashboard filters: one row of controls that scope every chart and table at once.

Options are found automatically in the result tables: a month range for any date column, and a
multi-select for each text column with a handful of values (channel, department, category...).
"""
import re

import pandas as pd

YEAR = re.compile(r"(19|20)\d{2}")

MAX_VALUES = 30   # text columns with more values than this are not offered as filters
MAX_FILTERS = 4


def options(results: list, charts: list) -> dict:
    used = [results[c["result_index"]]["df"] for c in charts if results[c["result_index"]]["df"] is not None]
    # Row-type selectors (a chart filter that picks ONE value, e.g. breakdown = "category") are not user filters.
    internal = {k for c in charts for k, v in (c.get("filter") or {}).items() if not isinstance(v, list) or len(v) == 1}
    months, dims, counts = set(), {}, {}
    for df in dict((id(d), d) for d in used).values():
        for col in df.columns:
            s = df[col]
            if pd.api.types.is_datetime64_any_dtype(s):
                months |= set(s.dropna().dt.to_period("M").astype(str))
            elif pd.api.types.is_string_dtype(s) and col not in internal and 2 <= s.nunique() <= MAX_VALUES:
                values = set(s.dropna().astype(str))
                if any(YEAR.search(v) for v in values) or {v.lower() for v in values} <= {"true", "false", "yes", "no"}:
                    continue  # period labels and yes/no flags are not useful filters
                dims.setdefault(col, set()).update(values)
                counts[col] = counts.get(col, 0) + 1
    top = sorted(dims, key=lambda c: (-counts[c], c))[:MAX_FILTERS]
    return {"months": sorted(months), "dims": {c: sorted(dims[c]) for c in top}}


def apply(df: pd.DataFrame, selection: dict) -> pd.DataFrame:
    """selection = {"months": (start, end) as 'YYYY-MM', "dims": {column: [values]}}"""
    if df is None:
        return None
    start, end = selection.get("months") or (None, None)
    for col in df.columns:
        if start and pd.api.types.is_datetime64_any_dtype(df[col]):
            m = df[col].dt.to_period("M").astype(str)
            df = df[(m >= start) & (m <= end)]
    for col, values in (selection.get("dims") or {}).items():
        if col in df.columns and values:
            df = df[df[col].astype(str).isin(values)]
    return df


def for_chart(df: pd.DataFrame, chart: dict, selection: dict) -> dict:
    """The part of the selection that applies to one chart: a dimension filter only applies where that
    column actually varies in the chart (a company-wide line is not hidden by a category filter)."""
    from agent.charts import prepare
    shown = prepare(df, chart)
    dims = {k: v for k, v in (selection.get("dims") or {}).items()
            if v and k in shown.columns and shown[k].nunique() > 1}
    return {"months": selection.get("months"), "dims": dims}
