"""Bundle finished end-to-end runs into one JSON file each, so the app can replay them instantly (no API calls).

Usage (from the project folder):  python -m eval.export_examples
Writes app/examples/<id>.json from the final evaluation runs (outputs/runs/final-<id>).
"""
import json

from agent.config import ROOT
from eval.recheck_grounding import results_for

OUT = ROOT / "app" / "examples"
EXAMPLES = ["returns", "finance", "repeat_customers"]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for pid in EXAMPLES:
        state, results = results_for(f"final-{pid}")
        bundle = {"id": pid, "request": state["request"], "questions": state["interview"],
                  **{k: state.get(k) for k in ("brief", "mapping", "audit", "metric_plan", "check_in", "sql", "dashboard")},
                  "results": [{"metric": r["metric"], "csv": None if r["df"] is None else r["df"].to_csv(index=False)}
                              for r in results]}
        (OUT / f"{pid}.json").write_text(json.dumps(bundle, default=str))
        print(f"{pid}: {(OUT / f'{pid}.json').stat().st_size / 1e3:.0f} KB")
