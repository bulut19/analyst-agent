"""Stage 6: the dashboard spec and written findings.

The model sees each result table and returns: a headline number (picked from the data, never typed),
chart specs (type, columns, filters) and 3-5 findings. Python then checks the spec against the real
columns, and checks that every number in the findings actually appears in the results ("grounding").
Problems go back to the model once.
"""
import html
import json
import re

import pandas as pd
import plotly.io as pio

from agent import llm
from agent.charts import apply_filter, figure, table
from agent.config import prompt

CHART = {"type": "object", "properties": {
    "result_index": {"type": "integer", "description": "Which result table (0-based)"},
    "type": {"type": "string", "enum": ["line", "bar"]},
    "title": {"type": "string", "description": "The finding, as a short headline (not just the metric name)"},
    "subtitle": {"type": "string", "description": "What is plotted, units and period"},
    "x": {"type": "string"}, "y": {"type": "string"},
    "color": {"type": "string", "description": "Column that splits series, or empty"},
    "filter": {"type": "object", "description": "Optional {column: value or [values]} to select rows"},
    "top_n": {"type": "integer", "description": "Bar charts: show the top N by y, or 0 for all"},
    "y_format": {"type": "string", "enum": ["percent", "points", "currency", "number", "decimal"]},
    "reference_value": {"type": "number", "description": "Optional benchmark line on bar charts (e.g. company average)"},
    "reference_label": {"type": "string"},
    "x_title": {"type": "string", "description": "Axis title for x, e.g. 'Order month' or 'Category'"},
    "y_title": {"type": "string", "description": "Axis title for y with its unit, e.g. 'Return rate (%)', 'Revenue ($)'"},
}, "required": ["result_index", "type", "title", "subtitle", "x", "y", "color", "filter", "top_n", "y_format"]}

TOOLS = [{"name": "submit_dashboard", "description": "Submit the dashboard layout and findings.",
          "input_schema": {"type": "object", "properties": {
              "headline": {"type": "object", "description": "The one number the dashboard leads with", "properties": {
                  "label": {"type": "string"}, "result_index": {"type": "integer"}, "column": {"type": "string"},
                  "filter": {"type": "object", "description": "{column: value} that selects exactly one row"},
                  "format": {"type": "string", "enum": ["percent", "points", "currency", "number", "decimal"]},
                  "context": {"type": "string", "description": "One short line under the number"}},
                  "required": ["label", "result_index", "column", "filter", "format", "context"]},
              "charts": {"type": "array", "items": CHART},
              "findings": {"type": "array", "items": {"type": "string"}},
          }, "required": ["headline", "charts", "findings"]}}]

BOLD = re.compile(r"(?<![\w.])([-+]?\$?\d+(?:,\d{3})*(?:\.\d+)?(?:%| pts| points| percentage points)?)(?![\w])")


def bold_numbers(text: str, html_out: bool = True) -> str:
    """Bold the figures in a finding (amounts, rates, counts), but not years like 2025 or tiny counts."""
    def wrap(m):
        tok = m.group(1)
        bare = tok.replace("$", "").replace(",", "").split()[0].rstrip("%").lstrip("+-")
        try:
            n = float(bare)
        except ValueError:
            return tok
        is_year = 1990 <= n <= 2100 and n.is_integer() and "," not in tok and "%" not in tok and "$" not in tok
        small = n < 10 and n.is_integer() and not any(ch in tok for ch in "%$") and "pts" not in tok and "point" not in tok
        if is_year or small:
            return tok
        return f"<b>{tok}</b>" if html_out else f"**{tok}**"
    return BOLD.sub(wrap, text)


NUMBER = re.compile(r"(?<![\w.])[-+]?\$?\d[\d,]*\.?\d*%?")


def describe(results) -> str:
    """Each result table for the prompt: columns, ranges and rows. Values keep 6 decimals so the model rounds once
    (0.282486 -> 28.2%), not twice (0.2825 -> 28.3%)."""
    parts = []
    for i, r in enumerate(results):
        df = r["df"]
        if df is None:
            parts.append(f"## Result {i}: {r['metric']} (FAILED, no data)")
            continue
        ranges = {c: [df[c].min(), df[c].max()] for c in df.select_dtypes("number").columns}
        shown = df if len(df) <= 300 else df.head(150)
        note = "" if len(shown) == len(df) else f" (first 150 of {len(df)} rows shown)"
        parts.append(f"## Result {i}: {r['metric']} ({len(df)} rows{note})\nColumns: {list(df.columns)}\n"
                     f"Numeric ranges: {json.dumps(ranges, default=str)}\nRows:\n{shown.round(6).to_csv(index=False)}")
    return "\n\n".join(parts)


def headline_value(spec, results):
    h = spec["headline"]
    df = apply_filter(results[h["result_index"]]["df"], h["filter"])
    if h["column"] not in df.columns or len(df) != 1:
        return None
    return df[h["column"]].iloc[0]


def fmt(value, kind):
    if value is None or pd.isna(value):
        return "n/a"
    return {"percent": f"{value:.1%}", "points": f"{value * 100:+.1f} pts", "currency": f"${value:,.0f}",
            "number": f"{value:,.0f}"}.get(kind, f"{value:,.2f}")


def _numbers_in_results(results):
    """Every number in the results, plus fractions as percentages, for the grounding check."""
    vals = []
    for r in results:
        if r["df"] is not None:
            for v in r["df"].select_dtypes("number").to_numpy().ravel():
                if pd.notna(v):
                    vals += [float(v), float(v) * 100]
    return vals


def ungrounded_numbers(findings, results):
    """Numbers in the findings that match nothing in the results (allowing for rounding)."""
    known = _numbers_in_results(results)
    missing = []
    for text in findings:
        for token in NUMBER.findall(text):
            raw = token.replace("$", "").replace(",", "").replace("%", "").strip("+")
            try:
                n = float(raw)
            except ValueError:
                continue
            if abs(n) < 13 and "%" not in token and "$" not in token:
                continue  # small counts like "3 categories" or "12 months"
            if 1990 <= n <= 2100 and float(n).is_integer():
                continue  # years
            decimals = len(raw.split(".")[1]) if "." in raw else 0
            half_unit = 0.5 * 10 ** -decimals + 1e-9  # 28.3% must round from [28.25, 28.35)
            tol = half_unit if "%" in token else max(abs(n) * 0.006, half_unit)
            if not any(abs(n - k) <= tol for k in known):
                missing.append(token)
    return missing


def validate(spec, results) -> list:
    problems = []
    for i, c in enumerate(spec["charts"]):
        if not 0 <= c["result_index"] < len(results) or results[c["result_index"]]["df"] is None:
            problems.append(f"chart {i}: result_index {c['result_index']} has no data")
            continue
        cols = set(results[c["result_index"]]["df"].columns)
        for key in ("x", "y", "color"):
            if c.get(key) and c[key] not in cols:
                problems.append(f"chart {i}: column '{c[key]}' not in result {c['result_index']} {sorted(cols)}")
        for col in (c.get("filter") or {}):
            if col not in cols:
                problems.append(f"chart {i}: filter column '{col}' not in result")
    if headline_value(spec, results) is None:
        problems.append("headline: the filter must select exactly one row and the column must exist")
    bad = ungrounded_numbers(spec["findings"], results)
    if bad:
        problems.append(f"findings cite numbers not found in the results: {bad}. Use only numbers from the tables.")
    return problems


def build(brief: dict, plan: dict, results: list) -> dict:
    system = prompt("system") + "\n\n" + prompt("dashboard")
    user = (f"Brief:\n{json.dumps(brief, indent=1)}\n\nMetric plan time window: {json.dumps(plan['time_window'])}\n"
            f"Decisions confirmed with the stakeholder: {json.dumps(plan.get('decisions_confirmed', []))}\n"
            f"Decisions assumed: {json.dumps(plan['decisions_assumed'])}\n\n# Result tables\n{describe(results)}")
    messages = [{"role": "user", "content": user}]
    response, _, spec, tool_id = llm.call_tool(system, messages, TOOLS, max_tokens=12000)
    problems = validate(spec, results)
    if problems:
        messages += [{"role": "assistant", "content": response.content},
                     {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id, "is_error": True,
                      "content": "Fix these problems and submit again:\n- " + "\n- ".join(problems)}]}]
        _, _, spec, _ = llm.call_tool(system, messages, TOOLS, max_tokens=12000)
        problems = validate(spec, results)
    spec["problems"] = problems  # should be empty; kept for the evaluation
    spec["grounded"] = not ungrounded_numbers(spec["findings"], results)
    return spec


def to_html(title: str, brief: dict, plan: dict, spec: dict, results: list, audit: dict = None,
            headline_results: list = None) -> str:
    """A self-contained HTML dashboard (Plotly from CDN) for sharing and screenshots."""
    e = html.escape
    h = spec["headline"]
    charts_html = []
    for i, c in enumerate(spec["charts"]):
        df = results[c["result_index"]]["df"]
        if df is None:
            continue
        fig_html = pio.to_html(figure(df, c), include_plotlyjs="cdn" if i == 0 else False, full_html=False,
                               config={"displayModeBar": False, "responsive": True})
        tbl = table(df, c).to_html(index=False, classes="data", border=0)
        charts_html.append(f'<section class="card">{fig_html}<details><summary>Table view</summary>{tbl}</details></section>')
    findings = "".join(f"<li>{bold_numbers(e(f))}</li>" for f in spec["findings"])
    decisions = "".join(f"<li>{e(d)}</li>" for d in plan.get("decisions_assumed", []))
    confirmed = "".join(f"<li>{e(d)}</li>" for d in plan.get("decisions_confirmed", []))
    confirmed = f"<p><b>Confirmed with the stakeholder:</b></p><ul>{confirmed}</ul>" if confirmed else ""
    audit_line = f"<p>{e(audit['summary'])}</p>" if audit else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)}</title>
<style>
:root {{ --surface:#fcfcfb; --page:#f9f9f7; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781; --rule:#e1e0d9; }}
body {{ margin:0; background:var(--page); color:var(--ink); font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }}
main {{ max-width:1040px; margin:0 auto; padding:32px 16px 64px; }}
h1 {{ font-size:24px; margin:0 0 4px; }} .q {{ color:var(--ink2); margin:0 0 24px; }}
.top {{ display:grid; grid-template-columns:minmax(220px,1fr) 2fr; gap:16px; margin-bottom:16px; }}
.card {{ background:var(--surface); border:1px solid var(--rule); border-radius:12px; padding:20px; margin-bottom:16px; }}
.hero .label {{ color:var(--ink2); font-size:13px; }} .hero .value {{ font-size:48px; font-weight:600; line-height:1.1; margin:6px 0; }}
.hero .ctx {{ color:var(--ink2); font-size:13px; }} h2 {{ font-size:13px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); margin:0 0 8px; }}
ul {{ margin:0; padding-left:20px; }} li {{ margin:4px 0; }}
details {{ margin-top:8px; }} summary {{ cursor:pointer; color:var(--ink2); font-size:13px; }}
table.data {{ border-collapse:collapse; font-size:13px; margin-top:8px; font-variant-numeric:tabular-nums; }}
table.data th, table.data td {{ border-bottom:1px solid var(--rule); padding:4px 12px 4px 0; text-align:left; }}
.notes {{ color:var(--ink2); font-size:13px; }} @media (max-width:720px) {{ .top {{ grid-template-columns:1fr; }} }}
</style></head><body><main>
<h1>{e(title)}</h1><p class="q">{e(brief['business_question'])}</p>
<div class="top"><section class="card hero"><div class="label">{e(h['label'])}</div>
<div class="value">{e(fmt(headline_value(spec, headline_results or results), h['format']))}</div><div class="ctx">{e(h['context'])}</div></section>
<section class="card"><h2>Findings</h2><ul>{findings}</ul></section></div>
{''.join(charts_html)}
<section class="card notes"><h2>Data notes</h2>{audit_line}<p><b>Period:</b> {e(plan['time_window']['start'])} to {e(plan['time_window']['end'])}.</p>
{confirmed}<p><b>Decisions assumed:</b></p><ul>{decisions}</ul></section>
</main></body></html>"""
