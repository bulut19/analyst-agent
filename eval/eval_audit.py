"""Evaluate the data quality audit.

1. Recall: run the checks on the dirty copy and count how many of the 40 planted errors are caught.
2. Precision: of the rows flagged on the dirty copy that are NOT also flagged on the clean copy,
   how many are planted errors (anything else is noise the planting did not explain).
3. Judgment: the LLM reviews the clean copy's findings (pre-existing issues in theLook) and the dirty
   copy's findings in the context of the returns brief. Reports are saved for review.

Usage (from the project folder):  python -m eval.eval_audit
"""
import csv
import json
from collections import defaultdict

from agent import llm
from agent.audit import audit_markdown, interpret, run_checks
from agent.config import CLEAN_DATASET, DIRTY_DATASET, ROOT

OUT = ROOT / "eval" / "results" / "audit"
EXPECTED_CHECK = {  # which check should catch each planted error type
    "duplicate_order": "duplicate_key", "missing_user_id": "missing_required",
    "delivered_before_created": "date_order", "outlier_quantity": "outlier",
    "future_order_date": "future_date", "invalid_price": "non_positive",
    "orphan_product": "orphan_key", "inconsistent_category": "inconsistent_spelling",
}


def flagged_rows(findings):
    """{(check, table, column): set of row keys}"""
    return {(f["check"], f["table"], f["column"]): set(f["keys"]) for f in findings}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    answer_key = list(csv.DictReader(open(ROOT / "data" / "answer_key.csv")))

    dirty = run_checks(dataset=DIRTY_DATASET)
    clean = run_checks(dataset=CLEAN_DATASET)
    for name, findings in (("dirty", dirty), ("clean", clean)):
        (OUT / f"checks_{name}.json").write_text(json.dumps(findings, indent=1, default=str))

    # 1. Recall
    caught_by_type = defaultdict(int)
    rows = []
    for e in answer_key:
        key = int(e["row_key"].split("=")[1])
        hits = [f["check"] for f in dirty if f["table"] == e["table"] and key in f["keys"]]
        right_check = EXPECTED_CHECK[e["error_type"]] in hits
        caught_by_type[e["error_type"]] += right_check
        rows.append((e["error_id"], e["error_type"], e["row_key"], ", ".join(sorted(set(hits))) or "MISSED"))
    recall = sum(caught_by_type.values()) / len(answer_key)

    # 2. Precision on rows the planting introduced
    planted = {(e["table"], int(e["row_key"].split("=")[1])) for e in answer_key}
    clean_rows = flagged_rows(clean)
    new_rows = set()
    for (check, table, column), keys in flagged_rows(dirty).items():
        new_rows |= {(table, k) for k in keys - clean_rows.get((check, table, column), set())}
    true_new = new_rows & planted
    precision = len(true_new) / len(new_rows) if new_rows else 1.0

    # 3. LLM judgment
    returns_brief = json.loads((ROOT / "eval/results/requirements/returns.json").read_text())["brief"]
    clean_report = interpret(clean, dataset=CLEAN_DATASET)
    dirty_report = interpret(dirty, brief=returns_brief, dataset=DIRTY_DATASET)
    (OUT / "audit_clean.md").write_text(audit_markdown(clean_report))
    (OUT / "audit_dirty_returns_brief.md").write_text(audit_markdown(dirty_report))
    (OUT / "audit_clean.json").write_text(json.dumps(clean_report, indent=1, default=str))
    (OUT / "audit_dirty_returns_brief.json").write_text(json.dumps(dirty_report, indent=1, default=str))

    clean_high = [i for i in clean_report["issues"] if i["verdict"] == "real_issue" and i["severity"] == "high"]
    dirty_verdicts = {i["finding_id"]: i for i in dirty_report["issues"]}
    planted_findings = [f for f in dirty if any((f["table"], k) in planted for k in f["keys"])]
    planted_called_real = sum(dirty_verdicts.get(f["finding_id"], {}).get("verdict") == "real_issue"
                              for f in planted_findings)

    lines = [
        "# Audit Evaluation", "",
        "| Metric | Result | Target |", "|---|---|---|",
        f"| Recall: planted errors caught by the right check | {sum(caught_by_type.values())}/{len(answer_key)} ({recall:.0%}) | 90%+ |",
        f"| Precision: new flagged rows that are planted errors | {len(true_new)}/{len(new_rows)} ({precision:.0%}) | 80%+ |",
        f"| Findings containing planted errors that the LLM called real issues | {planted_called_real}/{len(planted_findings)} | all |",
        f"| Clean copy: findings | {len(clean)} | |",
        f"| Clean copy: high-severity real issues (should be genuine pre-existing problems) | {len(clean_high)} | review |",
        "", "## Recall by error type", "", "| Error type | Caught |", "|---|---|",
        *[f"| {t} | {caught_by_type[t]}/5 |" for t in EXPECTED_CHECK],
        "", "## Every planted error", "", "| ID | Type | Row | Flagged by |", "|---|---|---|---|",
        *[f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows],
        "", "## Clean copy findings and the LLM's verdicts", "",
        "| Check | Table.column | Rows | Verdict | Severity |", "|---|---|---|---|---|",
        *[f"| {i['check']} | {i['table']}.{i['column']} | {i['rows_affected']:,} | {i['verdict']} | {i['severity']} |"
          for i in clean_report["issues"]],
        "", f"*Cost of the two LLM reviews: {llm.costs}*",
    ]
    (OUT / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:9]))
    print(f"\nCost: {llm.costs}")


if __name__ == "__main__":
    main()
