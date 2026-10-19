"""The stages after the requirements interview, each reading and writing the shared ProjectState.

state["brief"] (approved) -> discovery -> audit -> metric plan -> check-in questions (if any) -> plan
(approved) -> SQL + results
The app calls these one at a time so a person can approve the brief and the metric plan in between.
"""
from agent.audit import interpret, run_checks
from agent.discovery import discover
from agent.metrics import check_in_text, plan_metrics, revise_plan
from agent.sql import write_and_run


def stage_discovery(state):
    return state.set("mapping", discover(state["brief"]))


def stage_audit(state):
    findings = run_checks(state["mapping"])
    report = interpret(findings, state["brief"])
    state["audit_findings"] = [{k: v for k, v in f.items() if k != "keys"} for f in findings]
    return state.set("audit", report)


def stage_metric_plan(state):
    return state.set("metric_plan", plan_metrics(state["brief"], state["mapping"], state["audit"]))


def check_in_questions(state) -> list:
    """The questions the agent wants answered before building (0 to 2), as plain text."""
    return [check_in_text(c) for c in state["metric_plan"].get("check_in", [])]


def stage_check_in(state, answers: list):
    """answers: the stakeholder's replies, in the order of check_in_questions(state)."""
    qa = [{"question": q, "answer": a} for q, a in zip(check_in_questions(state), answers)]
    state["check_in"] = qa
    state["metric_plan_before_check_in"] = state["metric_plan"]
    return state.set("metric_plan", revise_plan(state["brief"], state["metric_plan"], qa))


def stage_sql(state, on_result=None):
    """Write and run SQL for every metric. Results (DataFrames) are kept on the state object, not in JSON."""
    state.results = []
    for metric in state["metric_plan"]["metrics"]:
        result = write_and_run(metric, state["metric_plan"])
        state.results.append(result)
        if on_result:
            on_result(result)
    state["sql"] = [{k: v for k, v in r.items() if k != "df"} | {"rows": None if r["df"] is None else len(r["df"])}
                    for r in state.results]
    return state.save()
