"""Final evaluation of the whole agent on the 5 stakeholder personas.

For each persona: simulated interview -> requirements rubric (scored by a separate judge model) ->
discovery -> audit -> metric plan -> SQL -> dashboard, timing every stage and recording cost.
Approvals are automatic here (in the app a person approves the brief and the metrics).

Usage (from the project folder):
    python -m eval.eval_end_to_end <persona id>     # one persona (the script runs personas in parallel)
    python -m eval.eval_end_to_end --summary        # combine saved results into eval/results/final/summary.md
"""
import json
import sys
import time

from agent import llm
from agent.audit import audit_markdown
from agent.config import ROOT
from agent.dashboard import build as build_dashboard, to_html
from agent.metrics import plan_markdown
from agent.pipeline import check_in_questions, stage_audit, stage_check_in, stage_discovery, stage_metric_plan, stage_sql
from agent.requirements import RequirementsInterview, brief_markdown
from agent.simulator import answer, personas
from agent.state import ProjectState

OUT = ROOT / "eval" / "results" / "final"
JUDGE_MODEL = "claude-opus-5-5"  # a different, larger model grades the interview, to limit self-grading
RUBRIC = ["found_real_need", "kpis_unambiguous", "useful_questions", "flagged_data_limits", "approvable_as_written"]

JUDGE = """You are grading a business analyst's requirements interview against a rubric. Be strict and fair.
The stakeholder's hidden true need (the analyst never saw this text):
{hidden_need}

Score each criterion from 1 (poor) to 5 (excellent):
- found_real_need: does the brief capture the hidden need, including decision, KPIs, period and breakdowns?
- kpis_unambiguous: could two analysts compute every KPI the same way from its definition?
- useful_questions: were the questions necessary and well chosen (at most 5, none wasted)?
- flagged_data_limits: does the brief honestly state what is assumed or cannot be answered?
- approvable_as_written: would a manager sign off on this brief without changes?
Call submit_scores once."""

SCORE_TOOL = [{"name": "submit_scores", "description": "Submit rubric scores.", "input_schema": {
    "type": "object", "properties": {
        **{k: {"type": "integer", "minimum": 1, "maximum": 5} for k in RUBRIC},
        "comment": {"type": "string", "description": "Two sentences: the main strength and the main gap"}},
    "required": [*RUBRIC, "comment"]}}]


def judge(persona, interview, brief):
    transcript = "\n".join(f"Q{i}: {q['question']}\nA{i}: {q['answer']}" for i, q in enumerate(interview.questions, 1))
    user = f"Opening request: {persona['opening_request']}\n\nInterview:\n{transcript}\n\nFinal brief:\n{json.dumps(brief, indent=1)}"
    _, _, scores, _ = llm.call_tool(JUDGE.format(**persona), [{"role": "user", "content": user}], SCORE_TOOL,
                                     model=JUDGE_MODEL, max_tokens=4000)
    return scores


def run(pid):
    p = {x["id"]: x for x in personas()}[pid]
    out = OUT / pid
    out.mkdir(parents=True, exist_ok=True)
    timings, t = {}, time.time()

    interview = RequirementsInterview(p["opening_request"])
    step = interview.next()
    while step["type"] == "question":
        step = interview.answer(answer(p, step["text"], interview.questions))
    timings["interview"] = time.time() - t
    cost_interview = llm.costs.usd
    scores = judge(p, interview, step["brief"])
    judge_cost = llm.costs.usd - cost_interview

    state = ProjectState(f"final-{pid}", brief=step["brief"], request=p["opening_request"], interview=interview.questions)
    def check_in(state):  # the simulated stakeholder answers the agent's check-in questions, if any
        history, answers = list(interview.questions), []
        for q in check_in_questions(state):
            answers.append(answer(p, q, history))
            history.append({"question": q, "answer": answers[-1]})
        stage_check_in(state, answers) if answers else state.set("check_in", [])

    for name, stage in [("discovery", stage_discovery), ("audit", stage_audit), ("metric_plan", stage_metric_plan),
                        ("check_in", check_in), ("sql", stage_sql)]:
        t = time.time()
        stage(state)
        timings[name] = time.time() - t
    t = time.time()
    spec = build_dashboard(state["brief"], state["metric_plan"], state.results)
    timings["dashboard"] = time.time() - t
    state.set("dashboard", spec)

    (out / "interview_and_brief.md").write_text(
        "\n".join(f"**Q{i}:** {q['question']}\n\n**A:** {q['answer']}\n" for i, q in enumerate(interview.questions, 1))
        + "\n---\n\n" + brief_markdown(state["brief"]))
    (out / "check_in.md").write_text("# Check-in before building\n\n" + ("\n".join(
        f"**Q:** {q['question']}\n\n**A:** {q['answer']}\n" for q in state["check_in"]) or "No questions: nothing material to confirm.\n"))
    (out / "audit.md").write_text(audit_markdown(state["audit"]))
    (out / "metric_plan.md").write_text(plan_markdown(state["metric_plan"]))
    (out / "dashboard.html").write_text(to_html(p["opening_request"], state["brief"], state["metric_plan"], spec,
                                                state.results, state["audit"]))
    sql = state["sql"]
    result = {
        "id": pid, "questions": len(interview.questions), "check_ins": len(state["check_in"]),
        "check_in": state["check_in"], "scores": scores,
        "rubric_avg": sum(scores[k] for k in RUBRIC) / len(RUBRIC),
        "metrics": len(sql), "metrics_ok": sum(r["ok"] for r in sql),
        "sql_retries": sum(len(r["attempts"]) - 1 for r in sql),
        "findings_grounded": spec["grounded"], "dashboard_problems": spec["problems"],
        "minutes": sum(timings.values()) / 60, "timings_s": {k: round(v) for k, v in timings.items()},
        "agent_cost_usd": llm.costs.usd - judge_cost, "judge_cost_usd": judge_cost,
    }
    (out / "result.json").write_text(json.dumps(result, indent=1, default=str))
    print(json.dumps({k: result[k] for k in ("id", "rubric_avg", "metrics_ok", "metrics", "minutes", "agent_cost_usd")}))


def summary():
    rows = [json.loads(p.read_text()) for p in sorted(OUT.glob("*/result.json"))]
    n = len(rows)
    md = ["# Final evaluation: 5 stakeholder personas, end to end", "",
          "| Persona | Questions | Check-ins | Rubric (1-5) | Metrics OK | SQL retries | Findings grounded | Minutes | Agent cost |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['id']} | {r['questions']} | {r.get('check_ins', 0)} | {r['rubric_avg']:.1f} | {r['metrics_ok']}/{r['metrics']} | "
                  f"{r['sql_retries']} | {'yes' if r['findings_grounded'] else 'NO'} | {r['minutes']:.1f} | ${r['agent_cost_usd']:.2f} |")
    md += ["", f"**Averages:** rubric {sum(r['rubric_avg'] for r in rows) / n:.1f}/5, "
           f"{sum(r['metrics_ok'] for r in rows)}/{sum(r['metrics'] for r in rows)} metrics OK, "
           f"{sum(r['minutes'] for r in rows) / n:.1f} minutes and ${sum(r['agent_cost_usd'] for r in rows) / n:.2f} per run.", "",
           "## Rubric detail (judge model: " + JUDGE_MODEL + ")", "",
           "| Persona | " + " | ".join(RUBRIC) + " | Comment |", "|---" * (len(RUBRIC) + 2) + "|"]
    for r in rows:
        md.append(f"| {r['id']} | " + " | ".join(str(r["scores"][k]) for k in RUBRIC) + f" | {r['scores']['comment']} |")
    md += ["", "## Check-in questions (asked after the metric plan, before any SQL)", ""]
    for r in rows:
        for q in r.get("check_in", []):
            md.append(f"- **{r['id']}:** {q['question']} *Answer:* {q['answer']}")
    md += ["", "Minutes include the simulated interview. Agent cost excludes the judge model."]
    (OUT / "summary.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    summary() if "--summary" in sys.argv else run(sys.argv[1])
