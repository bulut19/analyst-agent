"""Requirements rubric only: rerun the 5 simulated interviews and grade them with the judge model.
Faster and cheaper than the full end-to-end run, for testing prompt changes.

Usage (from the project folder):  python -m eval.eval_requirements [label]
Writes eval/results/requirements_rubric_<label>.md
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor

from agent import llm
from agent.config import ROOT
from agent.requirements import RequirementsInterview
from agent.simulator import answer, personas
from eval.eval_end_to_end import JUDGE_MODEL, RUBRIC, judge


def one(p):
    iv = RequirementsInterview(p["opening_request"])
    step = iv.next()
    while step["type"] == "question":
        step = iv.answer(answer(p, step["text"], iv.questions))
    return p["id"], len(iv.questions), judge(p, iv, step["brief"]), step["brief"]


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "latest"
    with ThreadPoolExecutor(5) as pool:
        rows = list(pool.map(one, personas()))
    md = [f"# Requirements rubric ({label})", "", "| Persona | Questions | " + " | ".join(RUBRIC) + " | Avg |",
          "|---" * (len(RUBRIC) + 3) + "|"]
    for pid, nq, s, _ in rows:
        avg = sum(s[k] for k in RUBRIC) / len(RUBRIC)
        md.append(f"| {pid} | {nq} | " + " | ".join(str(s[k]) for k in RUBRIC) + f" | {avg:.1f} |")
    overall = sum(sum(s[k] for k in RUBRIC) / len(RUBRIC) for _, _, s, _ in rows) / len(rows)
    md += ["", f"**Average: {overall:.1f}/5** (judge: {JUDGE_MODEL})", "", "## Judge comments", ""]
    md += [f"- **{pid}:** {s['comment']}" for pid, _, s, _ in rows]
    out = ROOT / "eval" / "results" / f"requirements_rubric_{label}.md"
    out.write_text("\n".join(md) + "\n")
    (out.with_suffix(".json")).write_text(json.dumps([{"id": r[0], "scores": r[2], "brief": r[3]} for r in rows], indent=1))
    print("\n".join(md[:9]), f"\nAverage {overall:.2f}. Cost: {llm.costs}")
