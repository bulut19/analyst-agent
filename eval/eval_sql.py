"""SQL accuracy: run the agent on every golden question (clean data) and compare with the verified answers.

Usage (from the project folder):  python -m eval.eval_sql
Numbers match within 0.5% (relative) or 0.0005 (absolute); text answers must match exactly (ignoring case).
Writes eval/results/sql_accuracy.md and .json
"""
import json

from agent import llm
from agent.ask import answer_question
from agent.config import CLEAN_DATASET, ROOT


def matches(expected, got, kind):
    if got is None:
        return False
    if kind == "text":
        return str(got).strip().lower() == str(expected).strip().lower()
    try:
        g, e = float(got), float(expected)
    except (TypeError, ValueError):
        return False
    return abs(g - e) <= max(abs(e) * 0.005, 0.0005)


def main():
    golden = json.loads((ROOT / "eval" / "golden_questions.json").read_text())
    rows = []
    for g in golden:
        r = answer_question(g["question"], CLEAN_DATASET)
        ok = matches(g["answer"], r["value"], g["answer_type"])
        rows.append({**g, "agent_answer": r["value"], "agent_sql": r["sql"], "attempts": r["attempts"], "correct": ok})
        print(f"{g['id']:<3} {'OK  ' if ok else 'MISS'} expected={g['answer']} got={r['value']}")

    by_level = {}
    for r in rows:
        by_level.setdefault(r["difficulty"], []).append(r["correct"])
    total = sum(r["correct"] for r in rows)
    verified = sum(r["verified"] for r in rows)
    md = ["# SQL accuracy", "", f"**{total}/{len(rows)} correct ({total / len(rows):.0%})** on the clean copy. "
          f"{verified}/{len(rows)} reference answers verified by hand.", "",
          "| Difficulty | Correct |", "|---|---|"]
    md += [f"| {k} | {sum(v)}/{len(v)} |" for k, v in by_level.items()]
    md += ["", "| ID | Expected | Agent | Correct | Attempts |", "|---|---|---|---|---|"]
    for r in rows:
        fmt = (lambda v: v) if r["answer_type"] == "text" else (lambda v: f"{float(v):,.4f}" if v is not None else "none")
        md.append(f"| {r['id']} | {fmt(r['answer'])} | {fmt(r['agent_answer'])} | {'yes' if r['correct'] else 'NO'} | {r['attempts']} |")
    md += ["", f"*Cost: {llm.costs}*"]
    out = ROOT / "eval" / "results"
    (out / "sql_accuracy.md").write_text("\n".join(md) + "\n")
    (out / "sql_accuracy.json").write_text(json.dumps(rows, indent=1, default=str))
    print(f"\n{total}/{len(rows)} correct. Cost: {llm.costs}")


if __name__ == "__main__":
    main()
