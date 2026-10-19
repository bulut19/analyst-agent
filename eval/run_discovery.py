"""Run data discovery on the saved test briefs and save the mappings.

Usage (from the project folder):  python -m eval.run_discovery [persona ids...]
"""
import json
import sys

from agent import llm
from agent.config import ROOT
from agent.discovery import discover, mapping_markdown

IN = ROOT / "eval" / "results" / "requirements"
OUT = ROOT / "eval" / "results" / "discovery"

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    wanted = sys.argv[1:]
    for path in sorted(IN.glob("*.json")):
        pid = path.stem
        if wanted and pid not in wanted:
            continue
        brief = json.loads(path.read_text())["brief"]
        mapping = discover(brief)
        (OUT / f"{pid}.json").write_text(json.dumps(mapping, indent=2))
        (OUT / f"{pid}.md").write_text(f"# {pid}\n\n**Business question:** {brief['business_question']}\n\n"
                                       + mapping_markdown(mapping))
        print(f"{pid}: {len(mapping['mappings'])} items mapped, {len(mapping['gaps'])} gaps, "
              f"invalid columns: {mapping['invalid_columns'] or 'none'}")
    print(f"\nCost: {llm.costs}")
