"""Rebuild the dashboard step of saved end-to-end runs (same SQL results, new dashboard spec and HTML).

Usage (from the project folder):  python -m eval.rebuild_dashboards <persona id> [...]
"""
import json
import sys

from agent.dashboard import build, to_html
from agent.state import OUTPUTS, ProjectState
from eval.eval_end_to_end import OUT
from eval.recheck_grounding import results_for

if __name__ == "__main__":
    for pid in sys.argv[1:]:
        _, results = results_for(f"final-{pid}")
        state = ProjectState.load(f"final-{pid}")
        spec = build(state["brief"], state["metric_plan"], results)
        state.set("dashboard", spec)
        (OUT / pid / "dashboard.html").write_text(to_html(state["request"], state["brief"], state["metric_plan"], spec,
                                                           results, state["audit"]))
        res = json.loads((OUT / pid / "result.json").read_text())
        res.update(findings_grounded=spec["grounded"], dashboard_problems=spec["problems"])
        (OUT / pid / "result.json").write_text(json.dumps(res, indent=1, default=str))
        print(pid, "grounded" if spec["grounded"] else "NOT grounded", spec["problems"])
