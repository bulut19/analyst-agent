"""Run discovery -> audit -> metric plan -> SQL on the saved test briefs (auto-approving each step).

Usage (from the project folder):  python -m eval.run_pipeline [persona ids...]
Saves to eval/results/pipeline/<id>/: metric_plan.md, audit.md, one .sql and .csv per metric, summary.md
"""
import json
import sys
import time

from agent import llm
from agent.audit import audit_markdown
from agent.config import ROOT
from agent.metrics import plan_markdown
from agent.pipeline import stage_audit, stage_metric_plan, stage_sql
from agent.state import ProjectState

BRIEFS = ROOT / "eval" / "results" / "requirements"
MAPPINGS = ROOT / "eval" / "results" / "discovery"
OUT = ROOT / "eval" / "results" / "pipeline"


def slug(text):
    return "".join(c if c.isalnum() else "_" for c in text.lower()).strip("_")[:50]


def run(pid):
    start, cost0 = time.time(), llm.costs.usd
    out = OUT / pid
    (out / "results").mkdir(parents=True, exist_ok=True)
    state = ProjectState(f"eval-{pid}", brief=json.loads((BRIEFS / f"{pid}.json").read_text())["brief"],
                         mapping=json.loads((MAPPINGS / f"{pid}.json").read_text()))
    stage_audit(state)
    (out / "audit.md").write_text(audit_markdown(state["audit"]))
    stage_metric_plan(state)
    (out / "metric_plan.md").write_text(plan_markdown(state["metric_plan"]))
    stage_sql(state, on_result=lambda r: print(f"  {'OK ' if r['ok'] else 'FAIL'} {r['metric']} "
                                                f"({len(r['attempts'])} attempt(s))"))

    lines = [f"# Pipeline run: {pid}", "", "| Metric | Status | Attempts | Rows | MB scanned |", "|---|---|---|---|---|"]
    for i, r in enumerate(state.results, 1):
        name = f"{i:02d}_{slug(r['metric'])}"
        (out / "results" / f"{name}.sql").write_text(r["sql"] + "\n")
        if r["df"] is not None:
            r["df"].to_csv(out / "results" / f"{name}.csv", index=False)
        rows = len(r["df"]) if r["df"] is not None else "-"
        mb = f"{r['mb_scanned']:.1f}" if r["mb_scanned"] is not None else "-"
        lines.append(f"| {r['metric']} | {'OK' if r['ok'] else 'FAILED'} | {len(r['attempts'])} | {rows} | {mb} |")
    failed = [r for r in state.results if not r["ok"]]
    for r in failed:
        lines += ["", f"**{r['metric']} last error:** {r['attempts'][-1]['error']}"]
    lines += ["", f"Time: {time.time() - start:.0f}s. LLM cost: ${llm.costs.usd - cost0:.3f}."]
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print(f"{pid}: {len(state.results) - len(failed)}/{len(state.results)} metrics OK, "
          f"{time.time() - start:.0f}s, ${llm.costs.usd - cost0:.3f}")


if __name__ == "__main__":
    ids = sys.argv[1:] or ["returns", "finance", "marketing"]
    for pid in ids:
        print(pid)
        run(pid)
    print(f"\nTotal cost: {llm.costs}")
