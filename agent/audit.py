"""Stage 3: the data quality audit. Deterministic checks run first; the LLM then judges and ranks them.

Usage:
    findings = run_checks(mapping)            # SQL checks on the tables the mapping uses
    report = interpret(findings, brief)       # LLM verdicts, severity, cleaning rules
"""
import json

from agent import llm
from agent.config import ACTIVE_DATASET, prompt
from checks.library import PK, run, run_all

ISSUE = {"type": "object", "properties": {
    "finding_id": {"type": "integer"},
    "verdict": {"type": "string", "enum": ["real_issue", "expected", "false_alarm"]},
    "severity": {"type": "string", "enum": ["high", "medium", "low", "none"]},
    "kpis_affected": {"type": "array", "items": {"type": "string"}},
    "explanation": {"type": "string"},
    "proposed_rule": {"type": "string"},
    "needs_decision": {"type": "boolean"},
    "decision_question": {"type": "string", "description": "Question for the stakeholder, or empty"},
}, "required": ["finding_id", "verdict", "severity", "kpis_affected", "explanation", "proposed_rule",
                "needs_decision", "decision_question"]}

TOOLS = [{"name": "submit_audit", "description": "Submit the audit judgments, real issues first by severity.",
          "input_schema": {"type": "object", "properties": {
              "summary": {"type": "string", "description": "Two or three sentences for the stakeholder"},
              "issues": {"type": "array", "items": ISSUE}}, "required": ["summary", "issues"]}}]


def tables_in(mapping: dict) -> list:
    used = {c.split(".")[0] for m in mapping["mappings"] for c in m["columns"]}
    return [t for t in PK if t in used]


def run_checks(mapping=None, dataset=ACTIVE_DATASET) -> list:
    tables = tables_in(mapping) if mapping else None
    findings = run_all(dataset, tables)
    for i, f in enumerate(findings, 1):
        f["finding_id"] = i
    return findings


def _sample_rows(f, dataset):
    """Up to 3 example rows showing the key and the columns involved, so the model can judge."""
    pk = PK[f["table"]]
    cols = [c.strip() for c in f["column"].split(",")]
    select = ", ".join(dict.fromkeys([pk, *cols]))
    keys = ", ".join(str(k) for k in f["sample_keys"][:3] if isinstance(k, int))
    if not keys:
        return []
    rows = run(f"SELECT {select} FROM `{dataset}.{f['table']}` WHERE {pk} IN ({keys}) LIMIT 3")
    return [{k: str(v) for k, v in dict(r).items()} for r in rows]


def _value_range(f, dataset):
    """Min and max of the flagged column across ALL flagged rows, so the model does not guess from samples."""
    col = f["column"]
    if "," in col or not f["keys"] or not all(isinstance(k, int) for k in f["keys"][:5]):
        return {}
    pk, keys = PK[f["table"]], ", ".join(str(k) for k in f["keys"])
    r = run(f"SELECT CAST(MIN({col}) AS STRING) lo, CAST(MAX({col}) AS STRING) hi "
            f"FROM `{dataset}.{f['table']}` WHERE {pk} IN ({keys})")[0]
    return {"flagged_values_min": r.lo, "flagged_values_max": r.hi}


def interpret(findings: list, brief: dict = None, dataset=ACTIVE_DATASET) -> dict:
    compact = []
    for f in findings:
        item = {k: f[k] for k in ("finding_id", "check", "table", "column", "rule", "rows_affected")}
        item["sample_rows"] = _sample_rows(f, dataset)
        item.update(_value_range(f, dataset))
        if "variants" in f:
            item["variants"] = f["variants"]
        compact.append(item)

    context = f"Approved brief:\n{json.dumps(brief, indent=1)}" if brief else \
        "No brief yet: judge severity for typical revenue, customer and returns reporting."
    user = f"{context}\n\nCheck findings:\n{json.dumps(compact, indent=1)}"
    system = prompt("system") + "\n\n" + prompt("audit")
    _, _, report, _ = llm.call_tool(system, [{"role": "user", "content": user}], TOOLS, max_tokens=12000)

    by_id = {f["finding_id"]: f for f in findings}
    for issue in report["issues"]:  # attach the facts the model judged
        f = by_id.get(issue["finding_id"], {})
        issue.update({k: f.get(k) for k in ("check", "table", "column", "rule", "rows_affected")})
    return report


def audit_markdown(report: dict) -> str:
    order = {"high": 0, "medium": 1, "low": 2, "none": 3}
    issues = sorted(report["issues"], key=lambda i: (i["verdict"] != "real_issue", order[i["severity"]]))
    real = [i for i in issues if i["verdict"] == "real_issue"]
    other = [i for i in issues if i["verdict"] != "real_issue"]

    lines = ["# Data Quality Audit", "", report["summary"], "", "## Issues to fix", "",
             "| Severity | Table.column | Rows | What is wrong | Proposed rule |", "|---|---|---|---|---|"]
    lines += [f"| {i['severity']} | `{i['table']}.{i['column']}` | {i['rows_affected']:,} | {i['explanation']} | {i['proposed_rule']} |"
              for i in real]
    decisions = [i for i in real if i["needs_decision"]]
    if decisions:
        lines += ["", "## Decisions needed", ""] + [f"- **{i['table']}.{i['column']}:** {i['decision_question']}" for i in decisions]
    if other:
        lines += ["", "## Flagged but not a problem", "", "| Verdict | Table.column | Rows | Why |", "|---|---|---|---|"]
        lines += [f"| {i['verdict'].replace('_', ' ')} | `{i['table']}.{i['column']}` | {i['rows_affected']:,} | {i['explanation']} |"
                  for i in other]
    return "\n".join(lines) + "\n"
