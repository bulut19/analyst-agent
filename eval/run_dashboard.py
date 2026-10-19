"""Build the dashboard (spec, findings, HTML) from the saved pipeline results.

Usage (from the project folder):  python -m eval.run_dashboard [persona ids...] [--rerender]
Saves eval/results/dashboards/<id>.html and <id>.json
"""
import json
import sys

import pandas as pd

from agent import llm
from agent.config import OUTPUTS, ROOT
from agent.dashboard import build, to_html

PIPE = ROOT / "eval" / "results" / "pipeline"
OUT = ROOT / "eval" / "results" / "dashboards"
TITLES = {"returns": "Returns by Category and Brand", "finance": "Revenue and Gross Margin",
          "marketing": "Repeat Customers by Channel"}


def load_results(pid):
    state = json.loads((OUTPUTS / "runs" / f"eval-{pid}" / "state.json").read_text())
    results = []
    csvs = sorted((PIPE / pid / "results").glob("*.csv"))
    for rec, path in zip(state["sql"], csvs):
        df = pd.read_csv(path)
        for c in df.columns:  # restore dates lost in CSV
            if pd.api.types.is_string_dtype(df[c]) and df[c].astype(str).str.match(r"^\d{4}-\d{2}-\d{2}").all():
                df[c] = pd.to_datetime(df[c])
        results.append({"metric": rec["metric"], "df": df})
    return state, results


def run(pid, rerender=False):
    state, results = load_results(pid)
    spec = json.loads((OUT / f"{pid}.json").read_text()) if rerender else build(state["brief"], state["metric_plan"], results)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{pid}.json").write_text(json.dumps(spec, indent=1, default=str))
    (OUT / f"{pid}.html").write_text(to_html(TITLES.get(pid, pid), state["brief"], state["metric_plan"],
                                             spec, results, state.get("audit")))
    print(f"{pid}: {len(spec['charts'])} charts, {len(spec['findings'])} findings, "
          f"grounded={spec['grounded']}, problems={spec['problems'] or 'none'}")


if __name__ == "__main__":
    rerender = "--rerender" in sys.argv  # redraw from the saved spec, no LLM call
    for pid in [a for a in sys.argv[1:] if not a.startswith("--")] or ["returns", "finance", "marketing"]:
        run(pid, rerender)
    print(f"\nCost: {llm.costs}")
