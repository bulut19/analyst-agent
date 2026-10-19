"""Stage 4: the metric plan. Exact, approvable definitions for every KPI in the brief."""
import json

from agent import llm
from agent.config import prompt
from agent.schema import load_profile

METRIC = {"type": "object", "properties": {
    "name": {"type": "string"},
    "question_answered": {"type": "string"},
    "formula": {"type": "string", "description": "Numerator, denominator and what counts, in words"},
    "grain": {"type": "string", "description": "One row per ... in the result table"},
    "breakdowns": {"type": "array", "items": {"type": "string"}},
    "filters": {"type": "array", "items": {"type": "string"}},
    "time_logic": {"type": "string", "description": "Exact dates and which date column places a row in a period"},
    "cleaning_rules": {"type": "array", "items": {"type": "string"}},
    "excluded_example": {"type": "string"},
    "chart_hint": {"type": "string", "enum": ["line", "bar", "card", "table"]},
}, "required": ["name", "question_answered", "formula", "grain", "breakdowns", "filters", "time_logic",
                "cleaning_rules", "excluded_example", "chart_hint"]}

CHECK_IN = {"type": "object", "properties": {
    "question": {"type": "string", "description": "Plain-English question for a busy manager"},
    "options": {"type": "array", "items": {"type": "string"}, "description": "2 or 3 short options"},
    "recommended": {"type": "string", "description": "The option the plan uses if the stakeholder has no view"},
    "why_it_matters": {"type": "string", "description": "One sentence: what changes on the dashboard"},
    "metrics_affected": {"type": "array", "items": {"type": "string"}},
}, "required": ["question", "options", "recommended", "why_it_matters", "metrics_affected"]}

TOOLS = [{"name": "submit_metric_plan", "description": "Submit the metric definitions for approval.",
          "input_schema": {"type": "object", "properties": {
              "time_window": {"type": "object", "properties": {
                  "start": {"type": "string", "description": "YYYY-MM-DD, inclusive"},
                  "end": {"type": "string", "description": "YYYY-MM-DD, inclusive"},
                  "explanation": {"type": "string"}}, "required": ["start", "end", "explanation"]},
              "shared_rules": {"type": "array", "items": {"type": "string"}},
              "metrics": {"type": "array", "items": METRIC},
              "decisions_assumed": {"type": "array", "items": {"type": "string"}},
              "check_in": {"type": "array", "maxItems": 2, "description":
                  "At most 2 decisions to ask the stakeholder about before building, only ones that change which "
                  "rows or entities appear, a ranking, or the headline number. Empty if none.", "items": CHECK_IN},
          }, "required": ["time_window", "shared_rules", "metrics", "decisions_assumed", "check_in"]}}]

MAX_CHECK_INS = 2


def data_range():
    created = load_profile()["orders"]["columns"]["created_at"]["range"]
    return created[0][:10], created[1][:10]


def plan_metrics(brief: dict, mapping: dict, audit: dict) -> dict:
    start, end = data_range()
    system = prompt("system") + "\n\n" + prompt("metrics").format(data_start=start, data_end=end)
    real_issues = [{k: i[k] for k in ("table", "column", "severity", "explanation", "proposed_rule",
                                      "needs_decision", "decision_question")}
                   for i in audit["issues"] if i["verdict"] == "real_issue"]
    user = (f"Approved brief:\n{json.dumps(brief, indent=1)}\n\n"
            f"Data mapping:\n{json.dumps({k: mapping[k] for k in ('mappings', 'joins', 'gaps', 'data_notes')}, indent=1)}\n\n"
            f"Audit (real issues and proposed cleaning rules):\n{json.dumps(real_issues, indent=1)}")
    _, _, plan, _ = llm.call_tool(system, [{"role": "user", "content": user}], TOOLS, max_tokens=12000)
    plan["check_in"] = (plan.get("check_in") or [])[:MAX_CHECK_INS]
    plan.setdefault("decisions_confirmed", [])
    return plan


def check_in_text(item: dict) -> str:
    """One check-in as the stakeholder sees it: question, options, recommendation and why it matters."""
    return (f"{item['question']} Options: {'; '.join(item['options'])}. "
            f"I'd suggest: {item['recommended']}, unless you prefer otherwise. ({item['why_it_matters']})")


def revise_plan(brief: dict, plan: dict, answers: list) -> dict:
    """Apply the stakeholder's check-in answers. answers: [{"question", "answer"}] in check-in order."""
    start, end = data_range()
    system = prompt("system") + "\n\n" + prompt("metrics").format(data_start=start, data_end=end)
    current = {k: v for k, v in plan.items() if k not in ("check_in", "decisions_confirmed")}
    qa = "\n".join(f"Q: {a['question']}\nA: {a['answer']}" for a in answers)
    user = (f"Approved brief:\n{json.dumps(brief, indent=1)}\n\nYour current metric plan:\n{json.dumps(current, indent=1)}\n\n"
            f"You checked in with the stakeholder before building:\n{qa}\n\n"
            "Submit the full plan again with their answers applied. Change only what the answers require. If an "
            "answer is unsure or matches your suggestion, keep your suggestion. Do not list these decisions in "
            "decisions_assumed (they are now confirmed), and leave check_in empty.")
    _, _, revised, _ = llm.call_tool(system, [{"role": "user", "content": user}], TOOLS, max_tokens=12000)
    revised["check_in"] = []
    short = [c["question"] for c in plan.get("check_in", [])] or [a["question"] for a in answers]
    revised["decisions_confirmed"] = plan.get("decisions_confirmed", []) + [
        f"{q} Answer: {a['answer']}" for q, a in zip(short, answers)]
    return revised


def plan_markdown(plan: dict) -> str:
    tw = plan["time_window"]
    lines = ["# Metric Plan", "", f"**Time window:** {tw['start']} to {tw['end']}. {tw['explanation']}", ""]
    if plan["shared_rules"]:
        lines += ["**Rules applied to every metric:**", ""] + [f"- {r}" for r in plan["shared_rules"]] + [""]
    for i, m in enumerate(plan["metrics"], 1):
        lines += [f"## {i}. {m['name']}", "", f"*{m['question_answered']}*", "",
                  f"- **Formula:** {m['formula']}", f"- **Grain:** {m['grain']}",
                  f"- **Breakdowns:** {', '.join(m['breakdowns']) or 'none'}",
                  f"- **Filters:** {'; '.join(m['filters']) or 'none'}",
                  f"- **Time logic:** {m['time_logic']}",
                  f"- **Cleaning:** {'; '.join(m['cleaning_rules']) or 'shared rules only'}",
                  f"- **Excluded example:** {m['excluded_example']}", ""]
    if plan.get("decisions_confirmed"):
        lines += ["## Confirmed with the stakeholder", ""] + [f"- {d}" for d in plan["decisions_confirmed"]] + [""]
    lines += ["## Decisions assumed (please confirm)", ""] + [f"- {d}" for d in plan["decisions_assumed"] or ["None"]]
    return "\n".join(lines) + "\n"
