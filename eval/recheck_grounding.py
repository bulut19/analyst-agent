"""Re-run the grounding check on saved dashboards (re-runs their saved SQL; no LLM calls).

Usage (from the project folder):  python -m eval.recheck_grounding final-returns final-finance ...
"""
import json
import sys

from agent.dashboard import ungrounded_numbers
from agent.sql import bq
from agent.state import OUTPUTS


def results_for(run_id):
    state = json.loads((OUTPUTS / "runs" / run_id / "state.json").read_text())
    results = [{"metric": r["metric"], "df": bq().query(r["sql"]).result().to_dataframe() if r["ok"] else None}
               for r in state["sql"]]
    return state, results


if __name__ == "__main__":
    for run_id in sys.argv[1:]:
        state, results = results_for(run_id)
        print(run_id, ungrounded_numbers(state["dashboard"]["findings"], results) or "all grounded")
