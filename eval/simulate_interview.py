"""Run the requirements interview against simulated stakeholders and save each transcript + brief.

Usage (from the project folder):
    python -m eval.simulate_interview                  # all personas
    python -m eval.simulate_interview returns finance  # only these personas
"""
import json
import sys

from agent import llm
from agent.config import ROOT
from agent.requirements import RequirementsInterview, brief_markdown
from agent.simulator import answer

OUT = ROOT / "eval" / "results" / "requirements"


def run(p):
    interview = RequirementsInterview(p["opening_request"])
    step = interview.next()
    while step["type"] == "question":
        step = interview.answer(answer(p, step["text"], interview.questions))

    lines = [f"# Interview: {p['id']}", "", f"**Request:** {p['opening_request']}", "",
             f"**Hidden need (what the simulator knew):** {p['hidden_need']}", "", "## Questions asked", ""]
    for i, q in enumerate(interview.questions, 1):
        lines += [f"**Q{i}:** {q['question']}", f"*Why:* {q['why']}", f"**A:** {q['answer']}", ""]
    report = "\n".join(lines) + "\n---\n\n" + brief_markdown(step["brief"])

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{p['id']}.md").write_text(report)
    (OUT / f"{p['id']}.json").write_text(json.dumps(
        {"persona": p, "questions": interview.questions, "brief": step["brief"]}, indent=2))
    print(f"{p['id']}: {len(interview.questions)} questions, {len(step['brief']['kpis'])} KPIs")


if __name__ == "__main__":
    personas = json.loads((ROOT / "eval" / "personas.json").read_text())
    wanted = sys.argv[1:]
    for p in personas:
        if not wanted or p["id"] in wanted:
            run(p)
    print(f"\nCost: {llm.costs}")
